"""Part 3 of 4 of a large module, split out of `memory_store`.

Everything here is re-exported from `memory_store`, so callers import it from there as before.
"""
import re

from ..memory import (
    content, current, last_user, log, name, note, others, recent, remember, remember_other, thread,
    user,
)
from ..memory import decided
from ..memory import company
from ..memory import surname as family_name
from ..memory import guest
from ..memory import plans
from ..memory import facts as extract
from ..knowledge import units
from ..memory import counts as how_many
from ..memory import rates as rates_reader
from ..memory.times import keep as _keep_the_times
from ..memory import recall
from ..memory import told as told_about
from ..memory.when import until_answer
from ..memory import repeat as repeat_the_line


from ..memory.store_lines import (
    NAME_FIX_WORDS, NAME_GIVEN_WORDS, DROP_LISTS, FIGURE_UNITS, FIGURE_TIME, FIGURE_NUMBER,
    FIGURE_QUALIFIER, LOOK_BACK_FIGURE, FIGURE_ANSWER_LEN, ROUTINE_SAY_BACK,
)
from .memory_store_part_01 import (
    CORRECTING, REMIND_QUESTION, _a_detail_does_not_replace_the_job, _a_number,
    _a_trip_booked_named, _about_this_chat, _after_the_yes_no_frame, _apply_correction,
    _behind_a_remembering_frame, _folded, _person_from_pronoun, _pronoun_fits, _statement,
    _this_line_put_something_right, _with_repaired, company, decided, extract, family_name,
    how_many, last_user, note, note_the_hours, others, plans, rates_reader, re, recall, remember,
    remember_other, told_about, CANT_HAVE, CAN_HAVE, CAN_THEY_HAVE, CAN_THEY_HAVE_A_FOOD, EAT_ASK,
    NO_RECORD, OTHER_FACT, PERSON_ADVICE_ASK, THEM, _RELATION, _a_limit_kept_for_them, _asks, _bare,
    _named_person, _other_person_reply, _the_person_still_in_hand, CORRECTS_A_MAKE, name, user,
    A_NAME_AFTER_A_PRONOUN, NAME_FIX, NAME_NOT_A_NAME, NAME_GIVEN, NOT_A_NAME_AFTER_CALLED,
    NOT_A_NEW_VALUE, PAIR_WITHOUT_A_MARKER, _fact_naming, TOO_AS_WELL, _canon_relation,
    _the_limit_the_last_line_gave, MONTHS, current, _a_feeling_about_what_they_said, _repeat_ask,
    thread, until_answer, FIGURE_ASK, FIGURE_FILLER, units, ACTION_AMOUNT, A_MONEY_FIGURE,
    A_PERCENT_FIGURE, ACTION_DURATION, FIGURE_AFTER, after, ANSWER_MODULES, A_RATE_ASK,
    A_RATE_STATED, LISTED_FIGURE, YES_NO_ASK, SAID_AGAIN, SORRY_OPENS_A_CORRECTION, SLOT_WORDS,
    recent, RECALL_POSSESSIVE, RECALL_SLOTS, RECALL_SLOTS_BY_POSSESSIVE, RECALL_WRAPPER,
    _names_the_thing, _says_the_verb, content, guest,
)
from .memory_store_part_02 import (
    _age_said_of_the_only_animal, _age_the_named_pet, _age_they_answered, _fix_a_persons_age,
    _fix_a_pets_age, _fix_a_pets_name, _fix_the_weeks_of_a_pregnancy, _forget_denied,
    _name_the_last_pet, _reads_the_store, _retract_last, _the_back_on_the_plate,
    _their_name_answered,
)


def _observe(text, memory):
    from ..memory import not_this as ruled_out_place
    if ruled_out_place.the_place_ruled_out(text, memory):
        # A place they ruled out is not a place they are going: "im going to spain" / "we arent
        # going to portugal" filed Portugal as a second place and answered with its card. The
        # line states nothing to keep, so nothing below it is read.
        return
    understood = memory.get("understood")
    # The kind of week their hours make, kept for the turn after it: "does that get easier",
    # "i never know when to stop" are about the week just described, and the reply is written in
    # bot/memory/hours.py. It is noted here rather than where the reply is written because the
    # hours line is often answered by a knowledge entry ("my rota changes every week") that never
    # reaches bot/memory/ack.py, and the follow-up is the same follow-up either way.
    note_the_hours(text, memory)
    # How many of a thing they have, kept as the number: "i have three brothers" was filed as one
    # brother, so "how many brothers do i have" said the store did not know. Noted here, beside the
    # hours, because the line that says it is often answered by another module.
    how_many.observe(text, memory)
    # A family name is a second name and not the one they are called: "my last name is okafor" was
    # filed as nothing, and "whats my surname" a turn later said the chat had never said one. It is
    # kept here, beside the count, because a line that gives one is often answered by another
    # module, and the file has to be there whichever module takes the turn.
    family_name.observe(text, memory)
    # The paragraph a plan announcement implies is kept for the next line rather than given now:
    # "im getting married in june" wants a warm word and a question, which the composer has, while
    # "what do i do first" wants the plan's own first step. It is kept here, in observe, because
    # each module works on its own copy of memory and only the chosen module's copy is kept: a
    # plan recorded by whichever module happened to answer is lost whenever the composer has the
    # turn (sturdy-poppy, #1848).
    planned = plans.answer(text, memory) if isinstance(text, str) else None
    if planned:
        memory["plan_answer"] = {"text": planned, "user": text}
    kind = understood.get("kind") if isinstance(understood, dict) else None
    if not isinstance(text, str):
        return
    # A remembering frame can carry the telling in the same line: "can you remember my sisters
    # name is amy" asks about the store and gives it a name. The frame states nothing - what
    # follows it is a line the store already knows how to read - so it is read as if it had been
    # said on its own. Left whole, the line filed the sister and not her name, and the reply to it
    # told a person who had just given the name that the store had nothing on her.
    said = _behind_a_remembering_frame(text)
    if said:
        text = said
    if recall.ask(text) or _reads_the_store(text, memory):
        return  # a question about what is already known states nothing new to keep
    if REMIND_QUESTION.search(text):
        return  # so does asking to be reminded, whatever the ask names
    if _asks_about_someone_else(text):
        # A yes/no question about someone else asks what is on record, so the frame itself
        # states nothing: "is he allergic to peanuts" must not file peanuts. A line that asks
        # and then tells ("does my mum eat meat? she is vegetarian") is two lines in one, and
        # the telling is kept: the frame is cut off and the rest is read as the statement it
        # is, or nothing is filed at all when the frame is the whole line.
        rest = _after_the_yes_no_frame(text)
        if not rest:
            return
        text = rest
    if isinstance(text, str) and _statement(text):
        # "do i live in york?" / "am i a baker?" / "am i right?" ask about the person; they state
        # nothing, so nothing is filed from them. Without this the question's own hypothetical
        # becomes the fact ("i live in leeds" then "do i live in york?" left York in the store)
        # and "am i right?" was filed as a name.
        return
    # A chat that weighs two things and picks one keeps the choice: "im thinking of getting a
    # cat" then "actually a dog" is a decision, and "what did i decide to get" is a question
    # about it. Read here because the line is a statement the store's own readers pass over.
    decided.observe(text, memory)
    # "im travelling with my mum": who is going with them is a fact about the chat, and
    # "who is coming with me" three turns later is answered from it (bot/memory/company.py).
    company.observe(text, memory)
    memory.pop("pet_age", None)  # an age taken last turn is not news for this one
    _keep_the_times(text, memory)
    # "i go to the gym twice a week" is a rate of their own doing, filed so a late "how often
    # was that again" is answered from it rather than asked back (bot/memory/rates.py).
    rates_reader.keep(text, memory)
    found = extract.extract(text, question=(kind == "question"))
    if not found:
        # "im an accountant" then "actually an engineer rather than an accountant": the person
        # says the correction on its own, and the subject is the turn before's.
        found = extract.a_correction_without_a_subject(text, last_user(memory))
    if not found.get("name"):
        # "can you remember my name" then "sam": the answer to the bot's own question, which no
        # pattern of the line's own words can read.
        answered = _their_name_answered(text, memory)
        if answered:
            found["name"] = answered
    found = _with_repaired(found, text, memory, kind)
    if not found.get("kids"):
        # "actually there are three of them": the number said back about the people in hand, with
        # no word for the people in the line at all. `kid_count` reads the count in front of the
        # word ("my three kids") and nothing here, because which people it counts is the store's
        # question: the children, when they are what the turn before was about.
        counted = extract.count_of_the_people(text, memory)
        if counted:
            found["kids"] = counted
    if not found.get("budget"):
        # Chat-speak hides the amount: "ive got 60 pounds to spend" is a budget once the folded
        # line reads "i have got 60 pounds to spend", so the folded line is read for the fact.
        folded = _folded(text, memory)
        if folded and folded != " ".join(text.lower().split()):
            budget = extract.extract(folded, question=(kind == "question")).get("budget")
            if budget:
                found["budget"] = budget
    if found.get("budget") and not re.search(r"[\u00a3$\u20ac]", found["budget"]):
        # "ive got £60 to spend": the folded line is plain words, so the sign is read off the
        # line they typed and put back on the amount.
        budget = str(found["budget"])
        sign = _budget_sign(text, budget)
        if sign:
            found["budget"] = sign + budget.lstrip()
    correction = found.pop("correction", None)
    if correction is None:
        # "its Preeya not Priya": a correction with no marker in front of it is only one when the
        # store already holds the value it takes back, which is the store's question, not the
        # reader's.
        correction = _a_correction_without_a_marker(text, memory)
    dropped = found.pop("drop", None)
    retracted = found.pop("retract", None)
    if not found.get("allergies"):
        # "im allergic to peanuts" then "and milk too": the line names one more thing and no
        # fact of its own, so it is the allergy on record with the milk in it. A food word on its
        # own is not enough - nothing is added to an allergy the person never gave.
        more = extract.one_more(text)
        held = (memory.get("user") or {}).get("allergies") or []
        if more and held:
            found["allergies"] = [item for item in more if item not in held]
    # Someone named in this same line comes first: "my mum is allergic to nuts and she doesnt
    # eat meat" is two facts about the mum, not one about the mum and one about nobody.
    named_here = [who for who in (found.get("people") or []) if isinstance(who, str)]
    _remember_dislikes(text, memory, named_here)
    second = _a_second_persons_limit(text, memory)
    if second:
        # Filed with the rest of this line's people, so it is logged and merged like any other: the
        # reader is the only one that knows the limit, because the limit is the line before's.
        found.setdefault("others", []).append(second)
    for entry in found.pop("others", []) or []:
        pronoun = entry.pop("pronoun", None)
        if not entry.get("who"):
            if pronoun and pronoun not in ("she", "he"):
                # "they" is nobody in particular, so the age is not the last person's: "my son is
                # 7" then "theyre 70 next month" is not the son's seventieth birthday, and folding
                # it onto him took the age the plain line gave away. Kept for the "how old are
                # they" ask instead, where the answer is about the same "they".
                age = _a_number(entry.get("age"))
                if age:
                    memory["their_age"] = {"age": age, "turns": entry.get("turns") or ""}
                continue
            who = _person_from_pronoun(text, memory, named_here)
            if pronoun:
                # "she's 78 and doesn't walk far" in a chat about her mum: the age goes on the
                # mum, never on the dad the chat was on before, because the pronoun has to fit.
                fits = extract.SHE if pronoun == "she" else extract.HE
                who = who if _pronoun_fits(who, fits) else ""
            if not who:
                if pronoun in ("she", "he") and isinstance(entry.get("months"), int):
                    # An age in months said with only a pronoun is still the chat's fact: "rough
                    # night, the baby was up 3 times" then "shes 4 months" names nobody the store
                    # can file it on, and dropping it made "how old did i say she was" say she had
                    # never said. Kept against the pronoun, the same way "they" is, so the ask
                    # about her can answer it.
                    entry["pronoun"] = pronoun
                    remember_other(memory, entry, text)
                continue  # a pronoun and nobody to put it on is not a fact about nobody
            entry["who"] = who
        if pronoun and "age" in entry and CORRECTING.search(str(text or "")):
            # "my son is 7 kilos" stores no age; "actually hes 8" then corrects nothing, so
            # it must not become the first age he has. A correction replaces a fact.
            known = next((one for one in others(memory) if one.get("who") == entry["who"]), None)
            if not (known and "age" in known):
                continue
        was = next((dict(one) for one in others(memory)
                    if one.get("who") == entry.get("who")), None)
        remember_other(memory, entry, text)
        _note_a_corrected_fact(memory, text, entry, was)
        _note_a_fact_moved(memory, text, entry, was)
    found = _a_detail_does_not_replace_the_job(found, memory)
    held_name = str((memory.get("user") or {}).get("name") or "")
    for key, value in found.items():
        remember(memory, key, value, text)
    if (found.get("name") and held_name
            and str(found["name"]).lower() != held_name.lower()):
        # A name that arrives when another is already on record is the name put right, whether
        # or not the line carries a correcting word: "im tom" then "i go by tomas" was answered
        # as a first introduction - "Hi Tomas - good to meet you" - one line after meeting Tom,
        # and the old name went without a word. Said as the correction it is, the person hears
        # which name the bot goes with.
        memory["name_fixed"] = {"name": str(found["name"]), "from": held_name,
                                "said": " ".join(str(text or "").lower().split())}
    if found.get("job") and not found.get("job_frame"):
        # A job said plainly ("i'm a chef now") is said back the same way: the frame belongs to
        # the job it was said with, so "i work in a warehouse" then "i'm a chef" is not "in a
        # chef" - the old frame goes with the old job.
        (memory.get("user") or {}).pop("job_frame", None)
    # A name put right moves the name on the one pet it is about, and the "last pet" reader below
    # would otherwise drop that name on whichever pet came last: "i have two cats called milo and
    # tom" then "no hes called max" renamed Tom and then Milo, leaving one cat called Max.
    _fix_a_pets_name(text, memory)
    if "pets" not in found:
        _name_the_last_pet(text, memory)
        _age_the_named_pet(text, memory)
        _age_they_answered(text, memory)
        _age_said_of_the_only_animal(text, memory)
        _fix_a_pets_age(text, memory)
    _fix_a_persons_age(text, memory)
    _fix_the_weeks_of_a_pregnancy(text, memory)
    fixed = _fix_a_persons_name(text, memory)
    if fixed:
        # The correction is the turn's news: the summary has the new name, and the reply says
        # both halves so the person knows the old one is gone.
        memory["name_fixed"] = dict(fixed, said=" ".join(str(text or "").lower().split()))
    if "owns" not in found:
        _fix_the_make_of_a_thing(text, memory)
    _the_name_they_gave_to_the_person_they_mean(text, memory)
    _a_trip_booked_named(text, memory)
    if correction:
        _apply_correction(memory, correction, text)
        _fix_a_pets_name(text, memory)
        return
    if dropped and _drop_value(memory, dropped, text):
        return
    if retracted and _retract_last(memory, text):
        return
    _forget_denied(text, memory)
    _the_back_on_the_plate(text, memory)
    if _about_this_chat(text, memory):
        return
    if told_about.a_callback_the_chat_has(text, memory):
        # "remember when i said my knee hurt" names a thing the conversation is already on, so
        # the line adds no subject: filing it made "remember" a word of the topic, and the turn
        # after it ("its better now") was read against remembering and answered with a revision
        # tip. A callback naming something the chat does not hold ("remember when we talked
        # about lisbon") does say what the conversation is on, so that one is filed as usual.
        return
    # A line that put a value right is the turn's news, not a new subject: the conversation is
    # still on the thing the value belongs to. Noted as a topic, "my dog is called rex" then
    # "his names actually rocky" left the chat on a subject whose only word was "name", and
    # "how old is he" after it was answered with a tip on remembering names instead of with the
    # dog. The record the correction fixed stays the current one, so the next line about the
    # dog is read against the dog.
    if not _this_line_put_something_right(memory, text):
        note(memory, text, kind)


def _their_fact_ask(text, memory=None):
    """True for a line that only asks back a fact kept about someone else."""
    if not isinstance(text, str):
        return False
    low = _bare(_folded(text, memory))
    if PERSON_ADVICE_ASK.match(low) and not (CAN_THEY_HAVE.search(low)
                                             and _a_limit_kept_for_them(low, memory)):
        # "can he have cheese" opens like an advice ask and is not one: the person is asking
        # whether one food is all right for somebody with a limit the store already holds, and
        # the limit is the answer. A line with no limit kept for them is advice and is left alone.
        return False
    undeclared = _the_person_still_in_hand(low, memory)
    if not (undeclared or OTHER_FACT.search(low) or EAT_ASK.search(low)
            or CANT_HAVE.search(low) or CAN_HAVE.search(low) or CAN_THEY_HAVE.search(low)):
        return False
    # A line that tells the fact is not asking for it: "my son doesnt eat meat" and "my sister
    # is vegan" are the cooking entry's lines, and the store answering them with the fact said
    # back ("Your son doesn't eat meat.") is an echo where the dinner should be. Only an ask is
    # the store's, with or without the question mark.
    if not (undeclared or _asks(low) or "?" in text or _asks_about_someone_else(text)):
        # "does my mum eat meat she is vegetarian" is an ask and a telling in one breath, and most
        # people type it with no question mark: the auxiliary at the front and the person after it
        # are what make it an ask (`_asks_about_someone_else` reads exactly that shape).
        return False
    # Someone else is in the line: a pronoun, or a relation of theirs ("my mum"). A possessive in
    # front of another noun ("my mums car") is the car, so the word has to be the person.
    if not (undeclared or THEM.search(low) or _named_person(low)
            or re.search(r"\bmy\s+(?:" + _RELATION + r")\b(?!'s|s\b)(?!s\b)", low)):
        return False
    if CAN_THEY_HAVE_A_FOOD.search(low) and not _a_limit_kept_for_them(low, memory):
        # "can she have cheese" is answered from a limit the store holds for that person. With
        # nothing kept but their name, the store has no fact to answer with, and saying so about
        # a person the chat only named once is not worth the turn; with only an allergy kept, the
        # foods that contain the thing are the cooking entries' reading, not the store's.
        return False
    said = _other_person_reply(memory, low)
    if not said:
        return False
    # A miss is not a denial: when the store holds nothing about that person, the honest "you
    # haven't told me" is worse than the answer the knowledge base has. "is my son allergic to
    # nuts? he had a rash" was claimed only to be told nothing was on record, while the entry
    # about a nut-free kitchen had a real answer for it.
    if NO_RECORD.search(said):
        return False
    return True


def _fix_the_make_of_a_thing(text, memory):
    """A correction that names only the make goes on the last thing the store was told about.

    "my car is a ford fiesta" and then "sorry, its a focus" is one car with its make put right,
    and a store that keeps the fiesta answers the next ask with a car they have just corrected.
    """
    line = " ".join(str(text or "").strip().split())
    if not line or line.endswith("?") or len(line.split()) > 6:
        return
    match = CORRECTS_A_MAKE.search(line.lower())
    if not match:
        return
    held = user(memory).get("owns")
    if not isinstance(held, dict) or not held:
        return
    # Which thing the correction is about is decided by what the make is a make of, not by the
    # order things were said: after "my car is a ford fiesta" and "my phone is a pixel", "sorry
    # it's a focus" is the car, and putting it on the phone invents a phone nobody has. A make
    # that fits more than one thing ("sorry, it's a bosch") goes on the one mentioned last.
    fits = {}
    for thing in held:
        name = extract._the_model(match.group("value"), thing)
        if name:
            fits[thing] = name
    if not fits:
        return
    last_said = []
    for entry in log(memory):
        if entry.get("key") == "owns":
            last_said.extend(entry.get("value") or {})
    thing = next((one for one in reversed(last_said) if one in fits), next(iter(fits), ""))
    name = fits.get(thing, "")
    if not name or name == held.get(thing):
        return
    remember(memory, "owns", {thing: name}, text)


def _fix_a_persons_name(text, memory):
    """Put a corrected name on the person the pronoun points at.

    "my sister is called meg" then "actually she's called maggie" left the store saying Meg, so
    the ask after it answered with the name the person had just put right. The line names no
    relation, so who it is about comes from the pronoun, and the name it replaces has to be one
    the store already has: a correction replaces a fact, it is not the first one said.
    """
    low = " ".join(str(text or "").lower().split())
    if not low or len(low.split()) > NAME_FIX_WORDS or not CORRECTING.search(low):
        return None
    match = NAME_FIX.search(low)
    bare = None
    if not match:
        # A bare rename: "no sorry, she is rosie". Both halves are needed - the correcting word
        # in the line, which the check above has already asked for, and a word that is not a
        # word everybody uses.
        bare = A_NAME_AFTER_A_PRONOUN.search(low)
        if not bare:
            return None
        word = bare.group("name").strip("'\u2019")
        if (word in extract.COMMON_WORDS or word in extract.JOB_WORDS
                or word in extract.KIN or extract._not_a_name(word, strict_ly=False)):
            return None
        match = bare
    said = match.group("name").strip("'\u2019")
    if not said or said in NAME_NOT_A_NAME or extract._not_a_name(said, strict_ly=False):
        return None
    name = extract._tidy(extract._finish(said) or "")
    if not name:
        return None
    # "her name is maggie" points the same way "she's called maggie" does, and the pronoun has to
    # be the one `_person_from_pronoun` reads, so the possessive is turned into it here.
    about = re.sub(r"\bhis\b(\s+name)", r"he\1", low)
    about = re.sub(r"\bher\b(\s+name)", r"she\1", about)
    who = _person_from_pronoun(about, memory)
    if not who and bare:
        # "my daughter is called amy" then "no sorry, he is jake": a bare "he is jake" names no
        # relation, so the pronoun is all the line gives, and a "he" about a daughter is not a
        # correction of her but the person starting on somebody else. Renaming her Jake is a
        # wrong fact, worse than the store keeping Amy. The possessive shape below keeps the
        # fallback, because "sorry, her name is tomas" says which fact is being put right.
        return None
    if not who:
        # "my brother is called tom" then "sorry, her name is tomas": the pronoun they picked is
        # the one they type, and with one person named in the chat the correction is about that
        # person - reading the "her" literally left the store on the wrong name and the next ask
        # said the name they had just put right.
        named = [entry for entry in others(memory) if entry.get("name")]
        if len(named) != 1:
            return None
        who = str(named[0].get("who") or "")
    for known in others(memory):
        if known.get("who") == who and known.get("name"):
            before = str(known.get("name") or "")
            if bare and before.lower() == extract._tidy(name).lower():
                # The word is the name already on record, so there is nothing to put right.
                return None
            known["name"] = extract._tidy(name)
            known.pop("turns", None)
            log(memory).append({"key": "other", "value": dict(known),
                                "turn": len(memory.get("turns") or []), "text": text})
            return {"who": who, "name": str(known["name"]), "from": before}
    return None


def _the_name_they_gave_to_the_person_they_mean(text, memory):
    """Put a name given with a pronoun on the person the store already holds.

    "my son is called jack" then "hes called jake" left the store saying Jack while the reply said
    "He's called jake, good to know": the person is told it landed and it did not, so the next
    "what is my son called" answers with the name they have just given. Who it is about comes from
    the pronoun.

    A name the store already holds is replaced. A person it holds and never named gets the name as
    their first one - "im taking my daughter to london" then "her name is maggie" - because the
    reply already promises to remember it, and only when exactly one unnamed person fits the
    pronoun.

    A bare name after the word that opens a correction ("no, jake") is not this reader's: that is
    a correction of a name said wrong, and `_correct_a_persons_name` owns it.
    """
    low = " ".join(str(text or "").lower().split())
    if not low or len(low.split()) > NAME_GIVEN_WORDS or "?" in low:
        # "hes called jake" on its own is a name for the person already meant, but the same words
        # inside a longer line introduce somebody ("my nephew? hes called tom"), and that is a
        # fact about the nephew that the relation readers handle.
        return None
    match = NAME_GIVEN.search(low)
    if not match:
        return None
    raw = str(match.group("name") or match.group("name2") or "")
    name = raw.strip(" .,!")
    if not name or not extract._may_be_a_name(name) or name.lower() in NOT_A_NAME_AFTER_CALLED:
        return None
    if low[match.end():].strip(" .,!;:"):
        # Words after the name mean the line is not only the name: "hes called in sick today".
        return None
    who = _person_from_pronoun(low, memory)
    if not who:
        return None
    for known in others(memory):
        if known.get("who") != who or not known.get("name"):
            continue
        if str(known.get("name")).lower() == name:
            return None
        known["name"] = extract._tidy(name)
        known.pop("turns", None)
        log(memory).append({"key": "other", "value": dict(known),
                            "turn": len(memory.get("turns") or []), "text": text})
        return known
    # A first name for a person the chat was told about and never named: "im taking my daughter to
    # london for her birthday" then "her name is maggie". The reader above only replaces a name the
    # store already holds, so the reply said "Her name is maggie - I'll remember that" and filed
    # nothing, and eight turns later the same chat answered "You haven't told me your daughter's
    # name." One person on record has to be the one the pronoun points at, unnamed, and no second
    # unnamed person may fit it: with two daughters in the chat "her name is maggie" does not say
    # which of them, and a guess is worse than the honest "you haven't told me".
    if extract.PETS.search(low):
        # The line names an animal, so the name is that animal's: "her name is biscuit" after "we've
        # got a cat" belongs to the cat, and `_name_the_last_pet` has it.
        return None
    if re.search(r"\b(?:she|her)\b", low):
        fits = extract.SHE
    elif re.search(r"\b(?:he|his)\b", low):
        fits = extract.HE
    else:
        fits = None  # "theyre called" says no gender, so any unnamed person is a candidate
    unnamed = [str(one.get("who")) for one in others(memory)
               if one.get("who") and not one.get("name")]
    # A person the chat named only by their relation ("my daughter") is in the list of people and
    # has no entry of its own until a fact is filed about them, so the word itself is a candidate.
    kept = {str(one.get("who") or "") for one in others(memory)}
    unnamed += [str(word).lower() for word in (user(memory).get("people") or ())
                if isinstance(word, str) and str(word).lower() not in kept]
    unnamed = [word for word in dict.fromkeys(unnamed) if not fits or _pronoun_fits(word, fits)]
    if len(unnamed) != 1:
        return None
    for known in others(memory):
        if str(known.get("who") or "") == unnamed[0] and not known.get("name"):
            known["name"] = extract._tidy(name)
            known.pop("turns", None)
            log(memory).append({"key": "other", "value": dict(known),
                                "turn": len(memory.get("turns") or []), "text": text})
            return known
    remember_other(memory, {"who": unnamed[0], "name": extract._tidy(name)}, text)
    return {"who": unnamed[0], "name": extract._tidy(name)}


def _a_person(value):
    """True when the corrected value names a person ("sorry, i meant my wife").

    A person put right is answered better by the sentence that says whose the fact was, so the
    short echo stays out of the way and the turn is left to it.
    """
    words = {word.rstrip("s") for word in re.findall(r"[a-z']+", str(value or "").lower())}
    return any(relation.rstrip("s") in words for relation in extract.RELATIONS)


def _a_correction_without_a_marker(text, memory):
    """The {to, from} of a pair correction said with no "no"/"sorry" in front, or None.

    Only a value the store already holds can be taken back this way, so the line has to name an
    older fact in the half it corrects: "its Preeya not Priya" after "my name is Priya" is a
    rename, and "its raining not sunny" is a sentence about the weather that leaves the store
    alone.
    """
    said = str(text or "")
    if len(said.split()) > 6:
        return None
    for shape in PAIR_WITHOUT_A_MARKER:
        found = shape.match(said)
        if not found:
            continue
        right, wrong = extract._tidy(found.group("to")), extract._tidy(found.group("wrong"))
        if not right or not wrong or right.lower() == wrong.lower():
            continue
        if right.lower() in NOT_A_NEW_VALUE or wrong.lower() in NOT_A_NEW_VALUE:
            continue
        if not _fact_naming(memory, wrong) and not _a_person_called(memory, wrong):
            continue  # nothing on record says that, so this is not a correction of it
        return {"to": right, "from": wrong}
    return None


def _a_person_called(memory, name):
    """Whether the store holds a person under that name.

    "my sister is called anna" then "its hannah not anna" names both values with no "no" in
    front, and the name it takes back is one the store keeps for a person rather than in a fact
    of the user's own - so the pair reader has to look in both places before it says the line
    corrects nothing.
    """
    low = " ".join(str(name or "").lower().split())
    if not low:
        return False
    for entry in others(memory):
        if not isinstance(entry, dict):
            continue
        if str(entry.get("name") or "").strip().lower() == low:
            return True
        if any(str(old).strip().lower() == low for old in (entry.get("was") or [])):
            return True
    return False


def _stated_value(memory, key):
    """The value of `key` the line before this one stated, or None.

    A correction replaces what was just said, so the old value is the one on that line: "im
    allergic to peanuts" then "make that tree nuts" takes back peanuts, and not a food named
    three turns earlier.
    """
    said = " ".join(str(last_user(memory) or "").lower().split())
    entries = memory.get("facts_log")
    if not said or not isinstance(entries, list):
        return None
    for entry in reversed(entries):
        if not isinstance(entry, dict):
            continue
        if " ".join(str(entry.get("text") or "").lower().split()) != said:
            return None
        if entry.get("key") == key:
            return entry.get("value")
    return None


def _a_second_persons_limit(text, memory):
    """The limit the line before gave, carried onto the person this line names.

    Only the limit is carried, and only when the line before stated one: "my son is too" after a
    line about the weather carries nothing, and the person is filed with the words the store
    already uses for an allergy and for a diet.
    """
    low = " ".join(str(text or "").lower().split())
    match = TOO_AS_WELL.match(low)
    if not match:
        return None
    who = _canon_relation(extract.a_person_word(match.group("who")))
    if who not in extract._A_WORD_FOR_A_PERSON:
        return None  # "my budget is too" is not a person with an allergy
    theirs = _the_limit_the_last_line_gave(memory)
    if not theirs:
        return None
    giving = {"who": who}
    allergies = theirs.get("allergies")
    if isinstance(allergies, (list, tuple)):
        foods = [str(one) for one in allergies if str(one).strip()]
        if foods:
            giving["allergies"] = foods
    diet = theirs.get("diet")
    if isinstance(diet, str) and diet.strip():
        giving["diet"] = diet
    if len(giving) < 2:
        return None
    return giving


def _drop_value(memory, value, text=""):
    """'Sorry, not peanuts' takes that one back: it comes off the list of things they named.

    The list is the fact the line before it stated, and only a value on it can go, so a "not"
    about anything else ("no, not today") leaves memory alone. Nothing is put in its place, so
    the note of the turn says the value went instead of a new one arriving.
    """
    known = user(memory)
    low = " ".join(str(value or "").lower().split())
    if not low:
        return None
    for key in DROP_LISTS:
        held = known.get(key)
        if not isinstance(held, list):
            continue
        left = [v for v in held if isinstance(v, str) and not _names_this(v, low)]
        if len(left) == len(held):
            continue
        known[key] = left
        memory["correction"] = {"key": key, "value": str(value), "dropped": True,
                                "said": " ".join(str(text or "").lower().split())}
        return memory["correction"]
    return _drop_from_plan(memory, value, text)


def _plan_names(plan, low):
    """Does the plan say this value? A plan is kept as the sentence it arrived in, so the thing
    taken back is a word inside it ("Lisbon" in "Lisbon in may") and not an item on a list."""
    words = re.findall(r"[a-z0-9']+", str(plan or "").lower())
    for word in words:
        if word == low or (low.endswith("s") and word == low[:-1]) \
                or (word.endswith("s") and low == word[:-1]):
            return True
    return False


def _drop_from_plan(memory, value, text=""):
    """'Sorry, not Lisbon' after 'im going to Lisbon in May' takes the trip back with the place.

    A value taken back can be a word inside a plan rather than an item on a list, and a plan has
    no key of its own: it is the sentence the person said. Only a plan that names the value goes,
    so "sorry, not tuesday" leaves the trip to Lisbon alone, and the place goes with it - a store
    that still answers "you're going to lisbon in may" is telling them the thing they just took
    back. A city they also stated on its own ("i live in lisbon") stays: it is a fact about where
    they live, not the plan they dropped.
    """
    known = user(memory)
    low = " ".join(str(value or "").lower().split())
    if not low:
        return None
    # A month or a day inside a plan says when it happens, not what it is: "my exam is in june" /
    # "sorry, not june" took the exam with it, so the next "when is my exam" had nothing to answer
    # from. A date they want moved is a correction ("actually june not may"), and that path already
    # rewrites the plan; a take-back of a date leaves the plan where it was.
    if low in MONTHS or low in extract.DAYS:
        return None
    plans = known.get("plans")
    held = [plan for plan in (plans if isinstance(plans, list) else []) if isinstance(plan, str)]
    current = known.get("plan")
    if isinstance(current, str) and current not in held:
        held.append(current)
    left = [plan for plan in held if not _plan_names(plan, low)]
    if len(left) == len(held):
        return None
    if left:
        known["plans"] = left[-6:]
        known["plan"] = left[-1]
    else:
        known.pop("plans", None)
        known.pop("plan", None)
    city = known.get("city")
    home = isinstance(city, str) and _plan_names(city, low)
    places = known.get("places")
    if isinstance(places, list) and not home:
        left_places = [place for place in places
                       if not (isinstance(place, str) and _plan_names(place, low))]
        if len(left_places) != len(places):
            if left_places:
                known["places"] = left_places
            else:
                known.pop("places", None)
    known["plan_dropped"] = low
    memory["correction"] = {"key": "plan", "value": str(value), "dropped": True,
                            "said": " ".join(str(text or "").lower().split())}
    return memory["correction"]


def _names_this(held, low):
    """Does the value the person named name the thing on the list? Only the word itself and its
    singular or plural: "peanut" is "peanuts", and "nuts" is not something else that went."""
    held = " ".join(str(held).lower().split())
    if held == low:
        return True
    for a, b in ((held, low), (low, held)):
        if b.endswith("s") and a == b[:-1]:
            return True
    return False


def _budget_sign(text, budget):
    """The currency sign before the same amount in the line they typed, or ""."""
    number = re.sub(r"[^\d.,]", "", str(budget or ""))
    if not number:
        return ""
    for match in re.finditer(r"([\u00a3$\u20ac])\s?([\d][\d,.]*)", str(text or "")):
        if re.sub(r"[^\d.,]", "", match.group(2)) == number:
            return match.group(1)
    return ""


def _a_feeling_about_their_own_news(text, memory):
    """This line is a feeling about the thing they just said, and the store answers it.

    A bare "im scared" is read by the small-talk topics as small talk, so a candidate from there
    would take the turn; this says the store read the line whole and names what it is about. It is
    one of the lines the arbiter's single hook asks about, not a hook of its own: a second
    `TAKES_AS_IT_COMES` in this module would shadow the first one and take the store's recall and
    `when` asks out of service.
    """
    try:
        return _a_feeling_about_what_they_said(memory, _bare(_folded(text, memory))) is not None
    except Exception:  # noqa: BLE001 - a reading that fails just leaves the line to the others
        return False


# An ask to hear the last answer again is the store's line and no other module's, whatever else
# proposed on it. "how long should i rest a sprained ankle" / "how long did you say" is a person
# asking for the length they just read; the answers module read the ask as a fresh question and
# proposed a different ankle entry, which the specialist rule handed over, so the repeat was
# answered with other numbers than the ones on the screen (two or three days, two to six weeks,
# where the answer above it said one to two and four to six). The arbiter asks this before the
# never-repeat rule and the specialist fit (README.md, "Interface"), and this says yes only on a
# line `_repeat_ask` read whole: "how long did you say to cook it" and "what did you just say"
# are the store's, while "how long do i rest a sprained ankle" keeps its entry.
def takes_as_it_comes(text, memory=None):
    """True when the line is an ask for the bot's own last answer, so the store answers it."""
    if not isinstance(memory, dict):
        return False
    return _repeat_ask(text, _folded(text, memory), memory)


def _the_ask_about_how_it_went(text, memory):
    """This line asks how the thing they told us about went, and only they can say.

    "i had an interview today" / "how did it go" is a question about the person's own day: the
    knowledge base read the word "interview" and answered how to prepare for one, one line after
    they said it was over, and the specialist rule handed it the turn. The ask names no subject
    of its own on a line that does not, so the store says it read this line whole
    (bot/memory/thread.went).
    """
    try:
        return thread.went(text, memory) is not None
    except Exception:  # noqa: BLE001 - a reading that fails leaves the line to the others
        return False


def _a_count_from_the_date(text, memory):
    """Whether the ask is a count from a date already on file: "how many weeks till that".

    The date is in a line they said, so the answer is arithmetic on it and this store's line; a
    knowledge entry for the thing named in the ask ("the driving test") answers what that thing
    is, which is a different question.
    """
    try:
        return bool(until_answer(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        return False


# A line that asks for a figure and nothing else: "how many weeks", "how long", "how much
# longer", "how far". `repeat.the_figure_asked` hands back the whole sentence the figure is in,
# which is the sentence the person has just read: the answer here is the figure itself.
# "how often" and "how soon" are not asks for a length: "how often should i do them" after a back
# answer was handed "Two to six weeks.", and "and how often" after a washing-machine answer was
# handed "About two hours." Both are the length of something else, said on a line that asked how
# frequently. Only the asks that want a figure of a unit are read here.
# An amount of money is the family a bare "how much" asks for; the time families are the default
# for "how long" and for "how many" with no unit named.
FIGURE_MONEY = ("money",)


def _the_unit_asked(line):
    """The unit families this line asks a figure in, or None when it names a thing of its own."""
    found = FIGURE_ASK.match(" ".join(str(line or "").lower().split()))
    if not found:
        return None
    units = []
    for word in re.findall(r"[a-z']+", found.group("rest")):
        if word in FIGURE_FILLER:
            continue
        family = None
        for name, words in FIGURE_UNITS.items():
            if word in words:
                family = name
                break
        if family is None:
            return None  # a thing, not a unit: the thing has an answer of its own
        if family not in units:
            units.append(family)
    per_week = re.match(
        r"^\W*(?:a|an|per|each)\s+(?:%s)\b" % "|".join(
            re.escape(word) for word in sorted(
                {word for family in FIGURE_TIME for word in FIGURE_UNITS[family]}, key=len,
                reverse=True)),
        found.group("rest") or "", re.I)
    if per_week and found.group("asked").lower() == "much" and set(units) <= set(FIGURE_TIME):
        # "how much a month" is a rate of money and not a length: the period is what the amount is
        # per, so "three to six months" - the length of the buffer the answer names - is not what
        # was asked. Only the article makes it a rate: "how long a month" is not a line, and a
        # line with a thing of its own in it ("how much a month do i need") never gets here.
        return FIGURE_MONEY
    if not units and found.group("asked").lower() == "much":
        # An amount with no unit named is money, and a bare "how much" is a price rather than a
        # length. After "should i get a new phone or fix mine" / "its cracked", the answer on the
        # screen said "Repair it if the phone is under four years old ... £50 to £120 at a local
        # shop", and "how much" was handed "Under four years." - the default families here are
        # the time ones, so a price question picked out a time figure. Only a bare "how much" is
        # money: "how much water" names its unit and keeps it.
        return FIGURE_MONEY
    if not units and found.group("asked").lower() == "many":
        # "how many was it" names no unit at all, so it asks for a count and not for a length.
        # The default family here is a length, and the count ask was handed the last answer's
        # figure: eight turns after "theres going to be 8 of us", "how many was it" answered
        # "4 to 5 hours." A bare "how long" is still a length and keeps the default.
        return None
    return tuple(units) or FIGURE_TIME


def _the_clause(said, start, end):
    """The clause of `said` a figure sits in, between the punctuation either side of it."""
    left = max(said.rfind(mark, 0, start) for mark in ".;:")
    rights = [at for at in (said.find(mark, end) for mark in ".;:") if at >= 0]
    return said[left + 1:min(rights) if rights else len(said)]


def _the_money_figures(said):
    """Every amount of money the answer states, in order, as (words, definite)."""
    # The amount as it was said, without the punctuation that ended it: the caller puts the full
    # stop on, and "£60 to £120," came back as "£60 to £120,.".
    out = []
    for found in A_MONEY_FIGURE.finditer(said):
        if ACTION_AMOUNT.search(_the_clause(said, found.start(), found.end())):
            # The clause says when or if it happens, so the money is the size of a step and not
            # the amount the person asked about.
            continue
        out.append((found.group(0).strip().rstrip(",;:"), True))
    if out:
        return out
    for found in A_PERCENT_FIGURE.finditer(said):
        if ACTION_AMOUNT.search(_the_clause(said, found.start(), found.end())):
            continue
        out.append((found.group(0).strip().rstrip(",;:"), True))
    return out


def _the_figures_in(said, units):
    """Every figure of these units the answer states, in order, as (words, definite)."""
    if "money" in units:
        return _the_money_figures(said)
    words = sorted({word for unit in units for word in FIGURE_UNITS[unit]}, key=len, reverse=True)
    unit = r"(?-i:%s)" % "|".join(re.escape(word) for word in words)
    pattern = re.compile(
        r"(?<![\d,])\b(?P<qual>%s\s+)?(?P<num>%s)(?:\s*(?:-|to|or)\s*(?P<more>%s))?\s*"
        r"(?P<unit>%s)\b(?P<extra>\s+\d{1,3})?(?P<after>[^.;:!?,]*)" % (
            FIGURE_QUALIFIER, FIGURE_NUMBER, FIGURE_NUMBER, unit), re.I)
    out = []
    for found in pattern.finditer(said):
        after = found.group("after").strip().lower()
        next_word = (re.findall(r"[a-z']+", after) or [""])[0]
        unit_word = found.group("unit").lower()
        one = not unit_word.endswith("s") and unit_word not in ("km", "kg", "lb", "lbs")
        if one and next_word and next_word not in FIGURE_AFTER \
                and next_word not in {word for family in units for word in FIGURE_UNITS[family]}:
            # "the 5 to 6 minute egg": a singular unit with a word after it is an adjective, not
            # the noun of a figure, and a card that says it is not answering "how many minutes".
            continue
        # The figure alone, not the rest of the sentence it is the subject of: "eight to ten weeks
        # is a realistic build" is handed back as "Eight to ten weeks."
        pieces = [found.group("qual") or "", found.group("num"),
                  (("to " + found.group("more")) if found.group("more") else ""),
                  found.group("unit"), found.group("extra") or ""]
        said_figure = " ".join(piece.strip() for piece in pieces if piece.strip())
        # A rate is not a figure the person can plan by: "three runs a week" and "20 minutes
        # three times a week" belong to the plan, not to the ask about the length of it.
        if re.match(r"(?:a|an|per)\s+", after) or next_word == "per":
            continue
        if ACTION_DURATION.search(_the_clause(said, found.start(), found.end())):
            # A length of the doing, not of the thing: "for the first two days", "20 minutes at a
            # time". The clause says so, and the number is not the one that was asked for.
            continue
        definite = found.group("num").lower() not in ("a", "an")
        if not definite:
            continue
        out.append((said_figure, definite))
    return out


def _the_figure_the_answer_names(text, memory):
    """The figure the answer on the screen named, on a line that asks only for a figure, else None.

    "how many weeks" after "Each week add a minute to the jog ... in about eight weeks you will run
    20 minutes" names no thing, so no entry is reached and the entry the topic does reach answers
    the *unit* instead: the warm-up card, "Five to ten minutes." Nobody asked that. The figure is
    in the answer already on the screen, and `bot/memory/repeat.py` has read the line all along -
    but its reply was only ever asked for under the composer's last-resort module, and an entry
    that answers the wrong card wins the turn first.

    The store is where the answer already said belongs, so the reading is claimed here. It is the
    figure said back and not the sentence it is in, because the sentence is one the person has
    just read.

    Narrow on purpose: the line asks for one kind of figure and names nothing else, the answer is
    a knowledge answer from a turn or two back, the figure is definite and of the kind asked for,
    the unit is the noun of it, a rate ("three runs a week") is not a figure, and a length the
    answer gives for doing something ("for the first two days", "20 minutes at a time") is a
    duration of the action, not the length of the thing the person asked about.
    """
    if not isinstance(memory, dict) or not isinstance(text, str):
        return None
    units = _the_unit_asked(text)
    if not units:
        return None
    # A figure the person gave about their own life is theirs, not the answer's. "my back has
    # been bad for a week now" then "how long have i had it now" was handed "Six weeks." - the
    # follow-up figure at the end of the back answer - and the week they had just said was in the
    # chat all along. The same line after "i started running two weeks ago" was "20 minutes.", the
    # length of the run-walk in the answer. Only where the person's own figure is there to give:
    # with nothing of their own, the answer on the screen is still the best thing the store knows.
    theirs = repeat_the_line.the_figure_they_gave(text, memory)
    if theirs:
        return theirs
    # An amount per month is not a length in months: an answer that states rates is a table of
    # them, and the saving answer is the one that belongs on the line.
    rate_ask = bool(A_RATE_ASK.match(" ".join(text.lower().split())))
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    for back, turn in enumerate(reversed(turns[-LOOK_BACK_FIGURE:]), 1):
        if turn.get("module") not in ANSWER_MODULES:
            continue
        said = " ".join(str(turn.get("bot") or "").split())
        if not said or len(said) < FIGURE_ANSWER_LEN or said.rstrip().endswith("?"):
            continue
        if rate_ask and A_RATE_STATED.search(said):
            continue
        if LISTED_FIGURE.search(said):
            # A list of figures on one unit ("6 minutes for a runny yolk, 7 for jammy, 9 to 10 for
            # hard boiled") is the answer the person needs, and picking one of its numbers is not:
            # "how long do i boil an egg" / "and how long?" came back as "6 minutes." where the
            # answer had already said the whole range.
            continue
        found = _the_figures_in(said, units)
        if not found:
            if _a_figure_of_those_units(said, units):
                # The answer does state a figure of the kind asked and this reader cannot hand
                # back exactly one of them, so the store says nothing rather than reading an
                # older answer: the figure the person wants is the one on the newest answer, and
                # a number out of an answer two turns back is about something else.
                #
                # "im saving for a car" / "i need about 4000" / "i put away 300 a month" /
                # "so how long" was answered "About 3 years." - the 40 months of the table two
                # turns back - while the answer just above it said "£4,000 at £300 a month is 14
                # months". The scan "a month" out of "300 a month is 14 months" as an
                # indefinite figure and moved past the 14, so nothing was read off the newest
                # answer and the reader fell through to the one behind it. The module that works
                # the figure out (`bot/modules/saving_followup.py`) answers this line with the
                # 14 months.
                return None
            continue
        stated = {(figure.lower()) for figure, _ in found}
        if len(stated) > 1:
            # Two figures of the same kind: the answer is not one figure, and the one behind it
            # is about an older thing, so there is nothing to hand back here.
            return None
        figure = found[0][0]
        return figure[:1].upper() + figure[1:] + "."
    return None


def _a_figure_of_those_units(said, units):
    """True when the answer states a number with a unit of one of these families after it.

    The loose reading, used only to tell "this answer says a length and I cannot read which"
    from "this answer says no length at all": the second may hand the line to an older answer,
    the first may not.
    """
    if "money" in units:
        # Money is its own family and has no entry in FIGURE_UNITS: an amount is written with a sign
        # or with a word for it, so the loose reading is the two money patterns themselves.
        return bool(A_MONEY_FIGURE.search(said) or A_PERCENT_FIGURE.search(said))
    words = sorted({word for unit in units for word in FIGURE_UNITS[unit]}, key=len, reverse=True)
    if not words:
        return False
    unit = r"(?-i:%s)" % "|".join(re.escape(word) for word in words)
    pattern = re.compile(
        r"(?<![\d,])(?:%s|%s)\s*(?:-|to|or)?\s*%s\b" % (FIGURE_NUMBER, r"\d[\d,.]*", unit),
        re.I)
    return bool(pattern.search(said))


def _the_time_they_put_right(memory):
    """The reply to a line that does nothing but move a routine time, or None.

    "i get up at 6" then "i meant seven" is one word put right, and the store has always kept it
    (`times.keep`). But the reply to that line came from the composer's shrug ("I'm
    listening - say more if it helps.") or, after "make it 7", from the search hedge: the bot had
    just moved the time and said nothing about it. So the time is said back in the words the store
    holds it in, and the one it replaced is named, because a correction is what the line is:
    "Got it - you're up at 7, not 6."
    """
    fixed = memory.get("fixed_time")
    if not isinstance(fixed, dict):
        return None
    # The time is moved while the line is being read, so its turn is this one: `turns` holds the
    # turns before it. Any other turn is another line, and this reply is not about that line.
    if int(fixed.get("turn") or -1) != len(memory.get("turns") or []):
        return None
    at = " ".join(str(fixed.get("at") or "").split())
    if not at:
        return None
    what = " ".join(str(fixed.get("what") or "").split())
    said_back = (ROUTINE_SAY_BACK.get(what) or "You {what} at {at}.").format(at=at, what=what)
    said_back = said_back.rstrip(" .")
    was = " ".join(str(fixed.get("from") or "").split())
    if was and was != at:
        said_back += ", not " + was
    return "Got it - " + said_back[0].lower() + said_back[1:] + "."


def _asks_to_hear_it_again(text, memory):
    """True for the one turn where the same words are the answer: "what did you say earlier".

    STYLE.md's rule is about answering twice, not about being asked twice: a person who asks to
    hear the last answer again is handed it, and framing that as "Same answer, and it covers
    this:" says the words were volunteered again rather than asked for.
    """
    try:
        return _repeat_ask(text, _folded(text, memory))
    except Exception:  # noqa: BLE001 - an unreadable line keeps the floor under the reply
        return False


def _asks_about_someone_else(text):
    """True for a yes/no question about a person ("is he allergic to peanuts").

    The question mark is not asked for. Most people type an ask about their son on a phone
    without one, and "is he allergic to peanuts" filed peanuts on the son while the same line
    with a "?" did not - the fault this guard exists for, in the one shape where a wrong stored
    fact matters most. What makes the line an ask is the auxiliary at the front and a person
    after it: "is my son", "does he", "can they" never open a statement. A word that is not a
    person ("is it expensive", "is the boiler new") keeps the question mark it needs, because
    those openings are also how a statement about the weather goes.
    """
    line = " ".join(str(text or "").split())
    return bool(YES_NO_ASK.match(line))


def _note_a_corrected_fact(memory, text, entry, was):
    """Remember that this turn put a fact about someone right, so the reply can say which one.

    "my son is 7" then "sorry, i meant my son is 8" is a correction, and the store took it - it
    had 7 and now has 8 - but nobody said so: the line was answered with "Thanks for telling me -
    I'm here if you want to dig into any of that", which is the reply for news and tells the
    person the correction did not land. Worse, "sorry, i meant my son is 8" carries the word
    "sorry" and a relation, so it reached the row on how to word an apology and got advice about
    apologising to him. A correction is answered with the fact, so this one is.
    """
    if not isinstance(was, dict) or not isinstance(entry, dict):
        return
    said = " ".join(str(text or "").lower().split())
    if not (SAID_AGAIN.search(said) or SORRY_OPENS_A_CORRECTION.search(said)):
        return
    for kind, value in entry.items():
        if kind in ("who", "pronoun", "turns") or value in ("", None):
            continue
        before = was.get(kind)
        if before in ("", None) or before == value:
            continue
        memory["fact_fixed"] = {"who": str(entry.get("who") or ""), "kind": kind,
                                "value": value, "was": before,
                                "said": " ".join(str(text or "").lower().split())}
        return


def _note_a_fact_moved(memory, text, entry, was):
    """Remember a correction that moves a fact from one person to another.

    "my son is 9", then "sorry i meant my daughter is 9": the store filed the age on the
    daughter, but the son kept his, so the chat ended up with two nine year olds and no word
    said about it. The line also carries the word "sorry" and a relation, so it reached the row
    on how to word an apology and the person who had just put a fact right was told to name what
    they had done wrong. A correction that names another person takes the fact off the first one,
    and the reply says which person it now belongs to.

    Only the shape a correction is said in ("i meant", "sorry") counts, and only when a
    different person already holds the same value: "my daughter is 9 too" is news about a second
    child, not a correction, and it files both.
    """
    if not isinstance(entry, dict):
        return
    said = " ".join(str(text or "").lower().split())
    if not (SAID_AGAIN.search(said) or SORRY_OPENS_A_CORRECTION.search(said)):
        return
    who = str(entry.get("who") or "").strip()
    if not who:
        return
    # The person has to be named by this line: "sorry i meant my daughter is a nurse" is read for
    # the daughter, and the store also holds the nurse the son had, which is the fact being moved
    # away from and not the one moving - taken as the mover it sent the job the wrong way.
    if not re.search(r"\b" + re.escape(who) + r"\b", said):
        return
    for kind, value in entry.items():
        if kind in ("who", "pronoun", "turns") or value in ("", None):
            continue
        if isinstance(value, (list, dict)):
            continue
        if isinstance(was, dict) and was.get(kind) not in ("", None) and was.get(kind) != value:
            continue  # the same person's own fact being put right: `fact_fixed` has that one
        hold = [one for one in others(memory)
                if isinstance(one, dict) and one.get("who") and one.get("who") != who
                and one.get(kind) == value]
        if not hold:
            continue
        other = hold[0]
        memory["fact_moved"] = {"who": who, "was_who": str(other.get("who")), "kind": kind,
                                "value": value, "said": said}
        # The claim the arbiter asks for (`TAKES_AS_IT_COMES`) is put on the chat's own memory,
        # because each module is handed a copy of it: a mark made in the store's copy would be
        # thrown away. This turn is the store's answer even when an entry reads the word "sorry"
        # in the line, and the apology card took the turn off "sorry i meant my daughter is a
        # nurse" while the store's line said which child the nurse was.
        memory["moved_to_who"] = said
        # The first line said the fact about the wrong person, so it comes off that one: leaving
        # it made "how old is my son" answer nine when the person had already said the nine was
        # their daughter's.
        other.pop(kind, None)
        return


# The pronoun a slot is asked about, as the person the direct ask names: "her age" is "how old is
# she" and "their age" is "how old are they".
SHE_OR_HE = {"his": ("he", "is"), "her": ("she", "is"), "their": ("they", "are"),
             "my": ("i", "am"), "our": ("we", "are")}


def _a_word_for_the_slot(memory, attribute):
    """Whether a line of theirs in this chat holds a word for this slot."""
    pattern = SLOT_WORDS.get(str(attribute or "").lower())
    if not pattern:
        return False
    return any(pattern.search(str(turn.get("user") or "")) for turn in recent(memory, 8))


def _the_ask_behind_the_recall(low):
    """The direct ask and the slot a recall ask is about, or None.

    Only a slot the person could have given in words is read this way, and only with a possessive
    in front of it ("his name", "my budget"): "what did i say about the cake" and "what did i say
    was wrong with it" are not asks about a slot, and they keep their own readers.
    """
    if not isinstance(low, str):
        return None
    wrapped = RECALL_WRAPPER.match(low)
    if not wrapped:
        return None
    rest = re.sub(r"\s+(?:was|is|were|are)\s*$", "", wrapped.group("rest").strip())
    said = wrapped.group("word").lower().replace("  ", " ")
    slot = next(((word, name) for pattern, word, name in RECALL_SLOTS
                 if pattern.search(rest)), None)
    if not slot:
        return None
    word, attribute = slot
    possessive = RECALL_POSSESSIVE.match(rest)
    if said.startswith("how old"):
        # "how old did i say she was": the frame asks the age itself, so the person is the whole
        # of what is left, and it has to be a pronoun the store can point at.
        person = rest.strip().lower()
        if person not in SHE_OR_HE:
            return None
        who, verb = SHE_OR_HE[person]
        return "how old " + verb + (" i" if who == "i" else " " + who), "age", person
    if not possessive:
        return None
    person = possessive.group("poss").lower()
    # The ask is rebuilt from the words the person used, with the verb taken out and the question
    # word that slot is asked with: "what did i say my dog was called" is "what is my dog called"
    # (not "what is my name"), and "what did i say her birthday was" is "when is her birthday".
    plain = " ".join(re.sub(r"\b(?:was|is|were|are)\b", " ", rest).split())
    if not plain:
        return None
    word = "when is " if attribute == "birthday" else "what is "
    slot_word = RECALL_SLOTS_BY_POSSESSIVE.match(plain)
    # The miss line names the slot only when the ask was the slot on its own ("his name", "her
    # birthday"): with a noun in between ("my dog called") the thing is the dog, and what it is
    # called is a read the store's own readers answer.
    only_slot = slot_word.group("attribute") if slot_word else None
    return word + plain, only_slot or (attribute or "answer"), person


def _about_the_verb(plans, low, found):
    """The plan a when or what-time ask is about: the one that says its verb, and its name too.

    Two plans can say the same verb - "meeting sam at 6 tomorrow" and "meeting jo at 8 on friday"
    both say "meeting" - and the verb on its own answers "what time am I meeting sam" with jo's
    hour, which is an answer about somebody the person did not ask about. The words the ask puts
    after the verb are what tell the two plans apart, so a plan that names one of them wins.
    When no plan names them the verb-only reading still stands: "when do I start" names nobody,
    and "what time do I start work" keeps its answer even though the plan says "job".
    """
    named = content(low[found.end():])
    if named:
        for plan in reversed(plans):
            if _says_the_verb(plan, found.group(1)) and any(
                    _names_the_thing(plan, word) for word in named):
                return plan
    for plan in reversed(plans):
        if _says_the_verb(plan, found.group(1)):
            return plan
    return None


def _remember_dislikes(text, memory, named_here=()):
    """Keep a food someone else will not eat against that person: "she hates mushrooms"."""
    if not isinstance(text, str):
        return
    for food, at in guest.found(text):
        kind, who = extract.subject(text, at)
        if kind == "user":
            food = guest.plain(food)
            if food:
                remember(memory, "dislikes", [food], text)
            continue
        if kind != "other":
            continue
        who = who or _person_from_pronoun(text, memory, named_here)
        remember_other(memory, {"who": who, "dislikes": [food]}, text)
