"""Part 8 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..compose.recall import with_a_tail
from ..memory import (
    content, forms, keywords, last_bot, last_user, name, others, plan_line, plan_sentence, recent,
    thread, user, you,
)
from ..memory.places import _a_place
from ..memory import plans
from ..memory import facts as extract
from ..memory import history
from ..memory.when import the_part_asked
from ..memory.topics import ACKS, GREET, STOPWORDS
from ..understanding.normalize import fix_typo, normalise
from ..understanding.topics import PLACES
from ..memory.store_lines import NO_PLANS_REPLY, TAIL_WINDOW, KEY_SLOT, CONCEPTS, POSSESSIVE
from ..memory.relations import (
    ABOUT_PERSON_ASK, _every_line, _pet_age_reply, _plural_person, _same_name,
)
from ..modules.memory_tables import (
    DAY_ASKS, DAY_IT, DAY_THING, TIME_ASKS, TIME_IT, TIME_THING, WHEN_ASKS, WHEN_PLAN, WHEN_THING,
    WHERE_PLAN,
)
from bot.memory.corrected import _asks, _birthday_words
from .store_replies_part_01 import (
    STOPWORDS, DETAIL_START, ACTIVITY_ASK, ACTIVITY_LOOSE, ACTIVITY_WORDS, ASK_LINE,
)
from .store_replies_part_03 import (
    _the_day_before, _names_something_of_its_own, _a_time_for_the_job_itself,
    _answers_the_end_asked, _asks_the_end, _asks_the_start, _at_the_clock, _says_the_verb,
    _the_answer_about_it_is_on_the_screen, _the_date_behind_that, _the_day_is_the_whole_date,
    _the_day_of, _the_line_that_said, _the_plan_was_just_said_back, _thing_is_a_quality,
    _when_thing,
)
from .store_replies_part_04 import (
    POINTS_BACK_AT_IT, SETTING_OUT, STUDY_PLAN, SAYS_A_TRIP, PET_PART_ASK, WHOSE_BIRTHDAY,
    NOD_WORDS, HELLO_FILLER, CORRECTS, DENIAL, TAGS, PERSON_STANDS, NOT_A_PLACE_IN, SAYS_A_STAY,
    SAYS_A_JOB, SAYS_FOOD, _kind, THING_POINTER, NAME_SAID, NOT_A_NAME,
)
from .store_replies_part_05 import (
    _the_verb_they_asked,
)
from .store_replies_part_06 import (
    _only_a_pointer,
)
from .store_replies_part_07 import (
    _pet_breed_reply, _birthday_in_words, _vary, _the_same_relative,
)


def _the_prep_day(memory, low):
    """The plan and the day the work for it goes on, or None when the store cannot say.

    "when is the best time to prep for it" after "i have a big work thing on friday" is a timing
    ask the store can answer only because it knows the day: the plan said back is what they just
    told it, so the reply has to add the prep day, which is the bit they cannot work out from
    what they said. Without a weekday in the plan there is nothing to add, and the ask is left to
    whoever can answer it: the same words about a passport or a flight have an answer of their
    own, and "You need to renew your passport." is no answer at all.
    """
    if not POINTS_BACK_AT_IT.search(low) or not _a_plan_answers(memory, low):
        return None
    back = POINTS_BACK_AT_IT.search(low)
    if SETTING_OUT.search(low[max(0, back.start() - TAIL_WINDOW):back.start()]):
        return None      # "when is the best time to leave for it" is about setting out
    known = user(memory)
    plans = [p for p in (known.get("plans") or []) if isinstance(p, str) and p.strip()]
    latest = known.get("plan")
    if isinstance(latest, str) and latest.strip() and latest not in plans:
        plans.append(latest)
    for plan in reversed(plans):
        if STUDY_PLAN.search(plan):
            continue     # studying for an exam has an answer of its own
        dated = _the_day_before(plan)
        if not dated:
            continue
        day, before = dated
        said = plan_sentence(plan, plan_line(memory, plan)).rstrip(".")
        return (said + ", so " + before.title() + " is the day for the prep \u2014 keep " + day
                + " itself for the last bits.")
    return None


def _a_plan_answers(memory, low):
    """True when a when or time ask that names nothing of its own is answered by a plan.

    The ask has to be one of the store's own shapes, and the part after its head has to name
    nothing: "when is the best time to prep for it", "when do i start", "what time is my
    appointment". "when is the next full moon" names a moon, so it is about the world and the
    knowledge base keeps it, and so does an ask the plans cannot answer. The hedge for a chat
    with nothing coming up is not a plan either, so a claim is never made on it.
    """
    for pattern in (WHEN_ASKS, WHEN_THING, TIME_ASKS, TIME_THING):
        found = pattern.search(low)
        if not found:
            continue
        if _names_something_of_its_own(low, found.end()):
            return False
        reply = _plans_reply(memory, low)
        return bool(reply) and reply not in NO_PLANS_REPLY
    return False


def _plans_reply(memory, low):
    """What is coming up, in the words they said it in: the one plan, or the newest of several."""
    known = user(memory)
    plans = [p for p in (known.get("plans") or []) if isinstance(p, str) and p.strip()]
    latest = known.get("plan")
    if isinstance(latest, str) and latest.strip() and latest not in plans:
        plans.append(latest)
    worked = _the_date_behind_that(memory, low, plans)
    if worked:
        return worked
    if WHERE_PLAN.search(low) or WHEN_PLAN.search(low):
        # "where are we going again" and "which month are we going" are the trip said back. The
        # newest plan is the one they mean, and the sentence it came from says both parts of it.
        # Said whole it is the same sentence the turn before already gave, word for word, so an ask
        # that names one part gets that part: "Portugal.", "In August."
        if plans:
            # The sentence the plan came from still has the verb in it, which is what says a
            # place is a place: "i'm going to the gym tomorrow" is the gym, and the plan kept
            # without it ("house in june") is no place at all.
            said = plan_line(memory, plans[-1])
            part = the_part_asked(plans[-1], low, said, _a_place)
            if part and content(part) != content(str(last_bot(memory) or "")):
                # Unless it is the answer the bot has just given: the part asked for a second time
                # in the same words is the repeat the "Same answer" framing is for, and the plan
                # itself says something this turn.
                return part
            return plan_sentence(plans[-1], said) + "."
        return None
    clock = TIME_ASKS.search(low)
    if clock:
        # "what time am I meeting sam?" is the plan that names that verb, answered with its hour.
        plan = _the_one_asked([p for p in plans if _says_the_verb(p, clock.group(1))],
                              low[clock.end():])
        if plan:
            return _at_the_clock(plan) or plan_sentence(plan, plan_line(memory, plan)) + "."
        return None
    hour = TIME_THING.search(low)
    if hour:
        plan = _the_one_asked([p for p in plans if _names_the_thing(p, hour.group(1))],
                              low[hour.end():])
        if plan:
            return _at_the_clock(plan) or plan_sentence(plan) + "."
        return None
    pointed_clock = TIME_IT.search(low)
    if pointed_clock:
        # "what time was that again" points at the plan on the table, and the hour it names is the
        # answer. A plan with no hour on it does not answer it: the ask is then about the clock in
        # the room, which the calendar says, so the store stands aside instead of saying their
        # sentence back ("the meeting is at 3" was no answer to "what time was that again").
        if plans:
            return _at_the_clock(plans[-1])
        return None
    day_asked = DAY_ASKS.search(low)
    if day_asked:
        # "what day do i start" is the plan that names that verb, answered with its day: the day is
        # what was asked for, so it is the whole answer ("On Tuesday.").
        plan = _the_one_asked([p for p in plans if _says_the_verb(p, day_asked.group(1))],
                              low[day_asked.end():])
        if plan:
            return _the_day_of(plan) or plan_sentence(plan, plan_line(memory, plan)) + "."
        return None
    day = DAY_THING.search(low)
    if day:
        plan = _the_one_asked([p for p in plans if _names_the_thing(p, day.group(1))],
                              low[day.end():])
        if plan:
            return _the_day_of(plan) or plan_sentence(plan, plan_line(memory, plan)) + "."
        return None
    pointed_day = DAY_IT.search(low)
    if pointed_day:
        # "what day is it on" is the plan's day and not today's: with a plan on the table that
        # names a weekday, the weekday is the whole answer. A plan with no weekday on it does not
        # answer it - "i need to ring the bank tomorrow" then "what day is it on" asks what day
        # today is, and "im going to rome" asks the trip - so nothing is said rather than the
        # person's own sentence handed back, and the calendar and the trip answer are left to
        # answer it as they did before.
        if plans:
            return _the_day_of(plans[-1])
        return None
    when = WHEN_ASKS.search(low)
    if when:
        # The plan that names the verb they asked about answers "when do I start?".
        plan = _the_one_asked([p for p in plans if _says_the_verb(p, when.group(1))],
                              low[when.end():])
        if plan:
            day = _the_day_of(plan)
            if day and _the_day_is_the_whole_date(plan) and _the_plan_was_just_said_back(memory, plan):
                # "i begin my new job on monday" / "sorry i meant tuesday" is answered "Got it -
                # you begin your new job on Tuesday.", and "when do i start" then wants the day:
                # the plan read back is that same sentence twice, a line apart.
                return day
            return plan_sentence(_the_verb_they_asked(plan, low, plan_line(memory, plan)
                                        or _the_line_that_said(memory, plan)),
                                 plan_line(memory, plan)) + "."
        # A half of a line with two things in it keeps no verb ("i start my new job in january and
        # my course in february" keeps "my course in february"), and the ask names the verb the
        # half left out: "when does my course start" is that plan with "start" put back.
        halves = [p for p in plans if _the_verb_they_asked(p, low) != p]
        plan = _the_one_asked(halves, "") if halves else None
        if plan:
            return plan_sentence(_the_verb_they_asked(plan, low, plan_line(memory, plan)
                                        or _the_line_that_said(memory, plan)),
                                 plan_line(memory, plan)) + "."
        # "when do i go on holiday?" asks when the trip is without naming the plan by its verb:
        # the line says it is a trip, so a plan that is one answers it.
        if SAYS_A_TRIP.search(low):
            for plan in reversed(plans):
                if _about_kind("trip", plan, memory, phrase=True):
                    return plan_sentence(plan, plan_line(memory, plan)) + "."
        return None
    thing = _when_thing(low, wide=not plans)
    if thing:
        # The plan that names the thing they asked about answers "when is the wedding?".
        asking = [p for p in plans if _names_the_thing(p, thing, memory)]
        if _asks_the_end(low) or _asks_the_start(low):
            # "when does my job end" is not answered by the day it starts, and "when does my
            # course start" is not answered by the day it finishes. A plan that says the end
            # they asked about (or the start) still answers it.
            asking = [p for p in asking if _answers_the_end_asked(p, low)]
        plan = _the_one_asked(asking, "")
        if plan:
            day = _the_day_of(plan)
            if day and _the_day_is_the_whole_date(plan) and _the_plan_was_just_said_back(memory, plan):
                # The plan said back a line ago ("Got it - your exam is on the 15th.") is the same
                # sentence twice when the ask comes again: the date is what was asked for.
                return day
            return plan_sentence(_the_verb_they_asked(plan, low, plan_line(memory, plan)
                                        or _the_line_that_said(memory, plan)),
                                 plan_line(memory, plan)) + "."
        # The thing is named but nothing they told us is about it: not a plans answer at all.
        return None
    if WHEN_THING.search(low) and re.search(r"\b(?:bank|public)\s+holiday", low):
        # A when ask about a bank holiday names something too vague to be a plan, and nothing
        # they told us is about it. That is a question about the calendar, not about their own
        # plans, so this is not the place to answer it: it fell through to "nothing so far, you
        # haven't mentioned anything coming up". A vaguer "when is the next holiday" can be
        # either, and the nothing-so-far line is a fair answer to it.
        return None
    if _thing_is_a_quality(low):
        return None
    if not plans:
        if _a_time_for_the_job_itself(low):
            # "when is the best time to do it" is about the job in front of them, not about their
            # calendar. With nothing in the store the empty-store line is a wrong-subject answer:
            # it was said to somebody who had just asked about the mould on their courgette
            # leaves ("You haven't told me about anything coming up yet. What's on?"). Whoever
            # can answer the job keeps the turn, and a plan they do have still answers these
            # through the branch above.
            return None
        return pick(list(NO_PLANS_REPLY), memory)
    if _the_answer_about_it_is_on_the_screen(memory, plans[-1], low):
        # The answer this plan's own line was given is what the person is asking for again, and the
        # plan said back is only their own words: stand down so the answer can be framed as the
        # repeat it is.
        return None
    said = [plan_sentence(plan, plan_line(memory, plan)) for plan in plans[-2:]][::-1]
    if len(said) == 1:
        return with_a_tail(said[0] + ".", memory)
    return said[0] + ". And " + said[1][:1].lower() + said[1][1:] + "."


def _the_one_asked(matching, rest):
    """Which of the plans that fit the ask is the one they mean, or "" when none fits.

    Two plans can say the same verb: "im meeting sam at 6 tomorrow" and "im meeting jo at 8 on
    friday" both answer "what time am i meeting". The ask usually goes on to name the thing it
    wants ("meeting **sam**"), so the plan that also names a word of the ask is the one they
    mean, and the newest of those when several do. Only when the ask names nothing after the
    verb is the newest plan that fits the answer, which is what a store can honestly do.
    """
    asked = content(rest) if rest else []
    if asked:
        for plan in reversed(matching):
            if any(_names_the_thing(plan, word) for word in asked):
                return plan
    return matching[-1] if matching else ""


def _names_the_thing(plan, thing, memory=None):
    """True when the plan is about that thing: "wedding" is in "my sister's wedding is next
    june". A plan about something else is not the plan they asked about.

    A thing that is a kind of plan ("the trip", "the holiday") is about the plan by its shape and
    not by its word: nobody writes "trip" on a plan that says "Lisbon in may".

    The plan is kept as content words, which are singular ("the vets at 4.30" keeps "vet"), and
    the ask is the person's own word ("what time is the vets"), so both sides are read for their
    forms: a plural in the ask is the same thing as the singular the store keeps.
    """
    for word in content(plan):
        for key in [thing] + content(thing):
            if key == word or key in forms(word) or word in forms(key):
                return True
    return _about_kind(thing, plan, memory, phrase=True)


def _only_the_name(line, named, who):
    """True when a line says nothing but the name the store already files for the person.

    "my mums name is Ann", "my sister is called Meg": the name is what the store answers with,
    in the words it uses for a name ("Your mum is called Ann"), so the raw line is left out
    rather than quoted back with its "my mums name is" still in it.
    """
    person = set(_the_same_person(who))
    drop = ({"my", "our", "your", "the", "is", "was", "name", "names", "called", "and", "she",
             "he", "her", "his", "they", "their", "them", "also", "s"} | person)
    # A figure is a word of the line too: "my mum is called janet and shes 72" says the name and
    # her age, so the line is not only the name and is still read back whole.
    words = set(re.findall(r"[a-z0-9]+", str(line or "").lower()))
    # The possessive is written without its apostrophe more often than with it ("my mums name"),
    # so the person's word plus an "s" is the person again.
    words = {word[:-1] if word.endswith("s") and word[:-1] in (drop | person) else word
             for word in words}
    return words - drop == {str(named or "").lower()}


def _a_line_about(memory, who):
    """The newest line of theirs that names this person, or None.

    Only used when the store filed no fact and no line against them, so it is the difference
    between "you haven't told me anything about your dad" and the line that said what the dad
    was doing. A line that asks about the person is not a line about them, and neither is the
    ask being answered now.
    """
    for turn in reversed(_every_line(memory)):
        line = str(turn.get("user") or "").strip()
        # An ask is not something they told me: "how old is my dad", "is my sister coming on
        # friday", "should i call my mum" are questions about the person, and saying one back as
        # "you told me how old is your dad" puts words in their mouth and contradicts the
        # "you haven't told me how old your dad is" the line itself got a turn before.
        if (not line or "?" in line or _asks(line)
                or ABOUT_PERSON_ASK.search(line.lower())):
            continue
        if _only_a_pointer(" ".join(line.lower().split()).strip(" ?!.")):
            # "my wife is too" and "she isnt" point at a fact rather than saying one, so neither is
            # something to hand back as what they told me about her.
            continue
        if _the_word_for_them(who).search(line):
            return line
    return None


def _pet_part_reply(memory, low):
    """An age or a breed asked about an animal they have described, or None."""
    if not PET_PART_ASK.search(low):
        return None
    if re.search(r"\bage\b|\bhow old\b", low):
        said = _pet_age_reply(memory, low)
        if said:
            return said
    return _pet_breed_reply(memory, low)


def _birthday_reply(memory):
    """The birthday they gave, in the words they would use for it."""
    known = user(memory)
    date = known.get("birthday")
    words = _birthday_words(date) if date else _birthday_in_words(memory)
    if not words:
        return "You haven't told me your birthday yet."
    # A birthday is a date, and a date is answered the way every other date in the store is
    # ("On 3 May.", "In August." - see `when_answer`): the joining word is not part of the date,
    # so "my birthday is on 3 may" is not answered "Your birthday is 3 May." A birthday given in
    # words rather than as a date ("tomorrow") is not a date, and keeps the sentence form.
    if words.startswith("in "):
        plain = words[:1].upper() + words[1:] + "."
    elif re.match(r"(?:the\s+)?\d", words):
        plain = "On " + words + "."
    else:
        plain = "Your birthday is " + words + "."
    if plain in {turn.get("bot") for turn in memory.get("turns") or []}:
        return _vary(["It's " + words + " — that's what you told me.",
                      "You said " + words + ".",
                      "Still " + words + "."], memory)
    return plain


def _a_persons_birthday_reply(memory, low):
    """The date the store holds for the person the ask names, said back, or None.

    Only a date it holds is answered: a person with no birthday kept leaves the turn to whoever
    can answer it, the same rule as their name and their age. The person is the relation the ask
    names ("my mums birthday"), the name it gives ("toms birthday") or the pronoun ("his
    birthday"), and a pronoun only points at a person it fits.
    """
    asked = WHOSE_BIRTHDAY.search(low)
    if not asked:
        return None
    who = extract.a_person_word(asked.groupdict().get("who") or "")
    pronoun = (asked.groupdict().get("pronoun") or "").lower()
    named = (asked.groupdict().get("name") or "").lower()
    if who in ("birthday", "bday", "dob", "date"):
        return None
    known = None
    if who:
        known = next((entry for entry in others(memory)
                      if _the_same_relative(entry.get("who"), who)), None)
        if known is not None:
            who = str(known.get("who") or who)
    elif named:
        known = next((entry for entry in others(memory)
                      if _same_name(entry.get("name") or "", named)), None)
    elif pronoun:
        # "when is he/she ...": the last person the chat was about whose pronoun fits, which is
        # how the same ask about an age is read. A date kept against the pronoun itself ("his
        # birthday is in may" with nobody named in the chat) is that pronoun's, since it is the
        # only person the store was given.
        fits = extract.SHE if pronoun == "her" else extract.HE
        known = next((entry for entry in reversed(others(memory))
                      if (entry.get("who") or "").lower() in fits), None)
        if known is not None:
            who = str(known.get("who") or "")
            named = str(known.get("name") or "")
        else:
            word = "she" if pronoun == "her" else "he"
            known = next((entry for entry in others(memory)
                          if str(entry.get("pronoun") or "") == word and entry.get("birthday")),
                         None)
    if known is None or not known.get("birthday"):
        return None
    words = _birthday_words(known["birthday"])
    said_name = str(known.get("name") or named or "")
    if said_name and not who:
        # The store keeps a name as it was typed ("my son is called tom"), so the date is said
        # with it as a name reads.
        said_name = said_name[:1].upper() + said_name[1:]
        return _vary([said_name + "'s birthday is " + words + ".",
                      "That's " + words + " for " + said_name + "."], memory)
    if not who:
        return None
    # A relation is the person the store knows them by, so the date is said with them: "Your
    # mum's birthday is the 3rd of May." A word for more than one person takes the apostrophe
    # after it ("your kids' birthday"), the same way the rest of the store pluralises.
    theirs = ("Your " + who + ("'" if _plural_person(who) else "'s") + " birthday is "
              + words + ".")
    return _vary([theirs,
                  "That's " + words + " for your " + who + ".",
                  "Your " + who + ("'" if _plural_person(who) else "'s") + " birthday: "
                  + words + "."], memory)


def _weight_reply(memory):
    """What they weigh, in the unit they gave it in."""
    known = user(memory)
    weight = known.get("weight")
    if not weight:
        return "You haven't told me what you weigh."
    plain = "You weigh " + weight + "."
    if plain in {turn.get("bot") for turn in memory.get("turns") or []}:
        return _vary(["Still " + weight + ".", "You said " + weight + ".",
                      "It's " + weight + " — that's what you told me."], memory)
    return plain


def _height_reply(memory):
    """How tall they are, in the unit they gave it in.

    A height is said the way a person says it - "You're 5 foot 10", "You're 175cm" - and never
    "You weigh ...", which is the sentence the weight answer uses.
    """
    known = user(memory)
    height = str(known.get("height") or "").strip()
    if not height:
        return "You haven't told me how tall you are."
    plain = "You're " + height + "."
    if plain in {turn.get("bot") for turn in memory.get("turns") or []}:
        return _vary(["Still " + height + ".", "You said " + height + ".",
                      "It's " + height + " \u2014 that's what you told me."], memory)
    return plain


def _turn_lines(memory):
    """The user and bot lines of the earlier turns, oldest first."""
    lines = []
    for turn in memory.get("turns") or []:
        if isinstance(turn, dict):
            lines.append((str(turn.get("user") or ""), str(turn.get("bot") or "")))
    return lines


def _only_a_nod(line):
    """True for a line that says nothing but thank you or so: "thanks", "got it", "ok cheers"."""
    found = re.findall(r"[a-z']+", str(line or "").lower())
    if not found or len(found) > 4:
        return False
    return all(word in NOD_WORDS for word in found)


def _just_a_hello(line):
    """True for a line that is only a greeting ("hi", "good morning", "hiya there").

    Only greetings, word by word: "what are you exactly" is a real question that happens to be
    short, and "hi we got a cat" is a cat. A word that is not a greeting, an acknowledgement or
    one of the few fillers that ride along with a hello means the line said something.
    """
    if "?" in line:
        return False
    found = re.findall(r"[a-z']+", line.lower())
    return bool(found) and any(w in GREET for w in found) and all(
        w in GREET or w in ACKS or w in HELLO_FILLER for w in found)


def _worth_reporting(line):
    """True for a line that said something a chat can be said to have opened with.

    A chat that opened with "hi" began with the line after it: handing back "You started with:
    "hi"" tells them nothing they don't already know. The same goes for a line that was about
    the chat itself - "what have we talked about" handed back as "the first thing you said" is
    the bot quoting its own paperwork - so those are skipped too, and only a line that said
    something about their own life is reported.
    """
    return bool(line) and not _just_a_hello(line) and not history.not_a_subject(line)


def _adds_something(said, asked):
    """True when a bot line says more than the line it answers, so it can be quoted as an answer.

    "hes chewing all the furniture" / "Got it - he's chewing all the furniture." is the line said
    back with a nod in front. Handing that to "what did you say about chewing" quotes the person
    to themselves and calls it the bot's answer.
    """
    said_words = {word for word in keywords(said)} - NOD_WORDS
    asked_words = {word for word in keywords(asked)}
    return bool(said_words - asked_words)


def _corrects(line):
    """"sorry, Naples not Rome" replaces an earlier line instead of saying something new."""
    return bool(CORRECTS.search(" ".join((line or "").lower().split())))


def _the_fact_is_kept(key, memory):
    """True when the store holds the fact a recall key names."""
    slot = KEY_SLOT.get(key)
    return bool(slot and user(memory).get(slot))


def _a_denial(reply):
    """True when the reply is the store saying it has nothing about the thing."""
    return bool(reply) and bool(DENIAL.search(reply))


def _names_its_thing(low):
    """True when a "what was i saying about ..." line names the thing it asks about.

    "what were we on about?" and "what was i saying about it?" point at the subject instead of
    naming it, and the chat's own topic is the honest answer to those; only a line that names
    something ("about pasta", "about the boiler") is a lookup by name.
    """
    after = re.search(r"\babout\b\s+(.+)$", low or "")
    if not after:
        return False
    thing = re.sub(r"\b(?:again|before|earlier|please|so far|up to now|until now)\b",
                   "", after.group(1)).strip(" ?!.,")
    if not content(thing) or thing in ("it", "that", "this", "them", "that one"):
        return False
    return True


def _tagged(line):
    """The words a line stands for without saying them: the ask's own word for that thing."""
    low = str(line or "")
    return {concept for concept, pattern in TAGS if pattern.search(low)}


def _the_same_person(who):
    """Every word the chat may use for the person an ask names, its own word first.

    "my mum died in january" then "what did i say about my mother?" is one person asked about
    twice, and reading the ask's word alone said "you haven't told me anything about your mother"
    about a line they had just said. The concept table above already holds the everyday pairs
    (mum/mother, dad/father), so the person is read through it rather than by a list of its own.
    """
    who = str(who or "").strip().lower()
    if not who:
        return []
    concept = CONCEPTS.get(who)
    words = [who]
    if concept:
        words += [word for word, its in CONCEPTS.items() if its == concept and word != who]
    return words


def _the_name_pattern(who):
    """A line that names this person, in any of the words the chat uses for them.

    The word has to stand where a person stands: after "my"/"our" ("my dad"), or where the line
    turns to them ("we went out, dad paid"). "my mum loves dad jokes" is a line about the mum and
    not about the dad, so the word alone is not enough.
    """
    called = "(?:" + "|".join(re.escape(word) for word in _the_same_person(who)) + ")"
    # An in-law is not the parent: "my mother in law is 70" is somebody else, and "my father in
    # law" opens with "my father". The relation tail is what says so, in either spelling.
    not_a_relation = r"(?!\s*-?\s*in\s*-?\s*law)"
    return re.compile(r"\b(?:my|our)\s+" + called + not_a_relation + POSSESSIVE + r"\b|"
                      r"(?:^\s*|[,;]\s*|\b(?:and|but|also|then)\s+)" + called
                      + not_a_relation + POSSESSIVE + r"\b", re.I)


def _the_word_for_them(who):
    """Every word for this person standing where the person stands, anywhere in the line.

    A line about somebody does not have to open with them: "i think mum is allergic to shellfish"
    and "the doctor said dad needs a scan" are about the mum and the dad, and the store said it
    knew nothing about either. The word has to stand where a person stands, which is what keeps
    "dad jokes" out of the dad's lines.
    """
    words = "|".join(re.escape(word) for word in _the_same_person(who))
    return re.compile(r"\b(?:" + words + r")" + POSSESSIVE + r"\s*" + PERSON_STANDS.pattern, re.I)


def _a_stay_in_a_place(text):
    """True when the line says a stretch of time somewhere they are going."""
    for found in SAYS_A_STAY.finditer(text):
        word = found.group("place").lower()
        if word in extract.NOT_PLACES or word in NOT_A_PLACE_IN:
            continue
        return True
    return False


SAYS_THE_KIND = {
    "trip": SAYS_A_TRIP,
    "job": SAYS_A_JOB,
    "food": SAYS_FOOD,
}


def _says_where_they_live(text):
    """True when the line says where they live, in whatever words: "we moved to york last year".

    Read by the store's own places reader rather than by a second pattern here, so the words that
    make a place a home ("i live in a flat in leeds") are the same two readings in both places. A
    stay is not one: "we're staying in york for the weekend" names a visit.
    """
    if not isinstance(text, str) or not text.strip():
        return False
    try:
        found = extract.extract(text)
    except Exception:  # noqa: BLE001 - a line this cannot read names no home
        return False
    return bool(found.get("home"))


def _a_place_they_go(text):
    """The place a line says they are going to, or "": "im going to lisbon in may".

    Only the words that say somebody is travelling count, so where they live is not a trip: "i
    live in leeds" names a place and goes nowhere.
    """
    found = extract.PLACE_LOWER.search(text or "")
    if not found:
        return ""
    word = found.group(1).lower()
    if word in extract.NOT_PLACES or word in extract.PLACE_VERBS:
        return ""
    return word


def _about_kind(thing, text, memory=None, phrase=False):
    """True when `text` is about the kind of thing the ask names ("trip" -> "Lisbon in may").

    A trip is where they are going, in whatever words they used: a line that says they are going
    to a place is a trip though it never says the word. A plan kept as the bare phrase ("Lisbon in
    may") names no verb at all, so it is the trip when the place in it is one of theirs - which is
    why only a plan is read that way, and a line is not. A job is said in its own words ("i start
    at the hospital"), which is what SAYS_A_JOB is for.
    """
    kind = _kind(thing)
    if not kind or not isinstance(text, str) or not text.strip():
        return False
    said = SAYS_THE_KIND.get(kind)
    if kind == "job":
        return bool(said.search(text))
    # Where they live has no word of its own in the line that moves them, so the store's own
    # reading of a home is what decides, exactly as a place they are going decides a trip.
    if kind == "home":
        return _says_where_they_live(text)
    # A trip is the one kind with a second way of being said, so it is the only kind allowed to
    # answer a place: an ask about food must not be given "im going to lisbon in june".
    if kind == "trip" and (SAYS_A_TRIP.search(text) or _a_stay_in_a_place(text)
                            or _a_place_they_go(text)):
        return True
    if said is not None and said.search(text):
        return True
    if not phrase:
        return False
    known = (user(memory).get("places") or []) if isinstance(memory, dict) else []
    low = text.lower()
    return any(str(place).lower() in low for place in known if isinstance(place, str) and place)


def _seen(line):
    """The content words of a line, read the way the ask about it is read.

    The ask arrives in full words ("what did i say about my girlfriend") and the line it asks
    about stays as it was typed ("me and my gf are thinking of getting a cat"), so the line is
    put through the same reading before its words are taken. Otherwise a short spelling never
    reaches the word it stands for, and a two-letter one is not even a content word.
    """
    words = set(content(line))
    plain = normalise(line or "")
    plain = plain.get("norm_text") if isinstance(plain, dict) else ""
    if plain and plain != line:
        words |= set(content(plain))
    return words | _tagged(line)


def _alike(word, seen):
    """One word family is enough: "my allergy" finds "i'm allergic to nuts".

    A word finds its own family (the word with its verb ending on or off, stem, prefix, first
    five letters) and the words that name the same everyday thing, so "what did i say about the
    dog?" finds "we got a puppy" and "what did i say i was saving for?" finds "i want to save".
    """
    want = CONCEPTS.get(word)
    mine = forms(word)
    for other in seen:
        if word == other:
            return True
        if mine & forms(other):
            return True
        if want and want == CONCEPTS.get(other):
            return True
        if len(word) >= 4 and len(other) >= 4 and (word.startswith(other)
                                                  or other.startswith(word)):
            return True
        if len(word) >= 5 and len(other) >= 5 and word[:5] == other[:5]:
            return True
    return False


def _age_reply(memory):
    age = user(memory).get("age")
    # 6 is not an age anyone has ("i am 6 foot 2" is a height), so a number outside the range a
    # person can be is no answer at all, whatever an earlier line stored.
    if not age or not 1 <= age <= 120:
        return pick(["You haven't told me your age yet.", "I don't know it — you haven't said."],
                    memory)
    return pick(["You told me you're " + str(age) + ".", str(age) + " — you said."], memory)


def _content_words(line):
    return {word for word in re.findall(r"[a-z']+", line.lower())
            if len(word) > 3 and word not in STOPWORDS}


def _the_line_before_was_a_plan(memory):
    """True when the last thing they said was a plan of their own.

    "what am i up to?" is about what is coming up when the line before it said something coming
    up, and about the thing in their hands when that line said what they are doing now. The
    store knows which of its plans came from that line, so the ask is read there rather than
    answered by quoting the line back.
    """
    plan = (user(memory) or {}).get("plan")
    if not isinstance(plan, str) or not plan.strip():
        return False
    told = plan_line(memory, plan)
    if not told:
        return False
    return (" ".join(told.lower().split())
            == " ".join(str(last_user(memory) or "").lower().split()))


def _plan_was_corrected(memory):
    """True when the last thing they put right was a value inside the plan itself.

    The key is not always "plan": "we need to leave for the airport at 4" with "sorry, i meant
    5" corrects the line the plan was said in, and the plan is kept as "Leave for the airport
    at 5". What says the correction went into the plan is that the plan now holds the value
    they corrected it to.
    """
    changed = memory.get("correction") if isinstance(memory, dict) else None
    if not isinstance(changed, dict):
        return False
    if changed.get("key") in ("plan", "plans"):
        return True
    value = " ".join(str(changed.get("value") or "").lower().split())
    plan = " ".join(str((user(memory) or {}).get("plan") or "").lower().split())
    return bool(value) and bool(plan) and value in plan


def _about_the_same(line, line_words):
    """A line that carries on about the subject (a detail) and not a statement of its own."""
    return bool(DETAIL_START.search(line)) or bool(_content_words(line) & line_words)


def _activity_line(memory):
    """The last line in which they said what they were making, cooking or planning - a line of
    detail about it ("he is allergic to nuts") keeps the subject, so the plan is further back.
    A statement about something else ends the trail: what they were doing is then the newest
    statement, and if that one has no activity there is nothing to say back."""
    lines = [" ".join(str(turn.get("user") or "").split()) for turn in recent(memory, 4)]
    changed = memory.get("correction") if isinstance(memory, dict) else None
    fixed = " ".join(str(changed.get("said") or "").split()) if isinstance(changed, dict) else ""
    for wanted in (ACTIVITY_WORDS, ACTIVITY_LOOSE):
        for index in range(len(lines) - 1, -1, -1):
            line = lines[index]
            if not line or ASK_LINE.search(line) or ACTIVITY_ASK.search(line):
                continue
            if not wanted.search(line):
                continue
            words = _content_words(line)
            newer = [later for later in lines[index + 1:] if later]
            if any(fixed and later == fixed for later in newer):
                # A correction is the newest word on the thing they were on: they said the plan
                # another way, so the line they said before it is not what they are up to now.
                return ""
            if all(ASK_LINE.search(later) or ACTIVITY_ASK.search(later)
                   or _about_the_same(later, words) for later in newer):
                return line
            return ""
    return ""


def _the_making_line_they_said(memory, back=8):
    """The last line of theirs that says what they are making, without the trail check.

    `_activity_line` stops the trail at the first line about something else, which is right for
    "what was i cooking?" in a chat that has moved on to a dishwasher. "Again" asks for a line
    the person knows they said, so what happened in between is not the subject to answer from:
    "im making a cake for my sons birthday" / "by the way my back is killing me" / "what am i
    making again" is still the cake. Without this the ask fell to a method card, or to "I'm not
    sure about that one" in a chat that says plainly what it is making.
    """
    for turn in reversed(recent(memory, back)):
        line = " ".join(str(turn.get("user") or "").split())
        if not line or ASK_LINE.search(line) or ACTIVITY_ASK.search(line):
            continue
        if ACTIVITY_WORDS.search(line) or ACTIVITY_LOOSE.search(line):
            return line
    return ""


def _recap(line):
    """Their own line said back as a sentence about them: "im making a cake" -> "You're making
    a cake for your son." Only a line that starts with the person and the plan is reworded;
    "i think im just going to have a bath" is quoted as it stands, which reads right."""
    flat = " ".join(str(line or "").split()).strip(" .")
    planned = re.match(r"^(?:im|i'm|i am|ive|i've|were|we're|we are)\s+(\S.*)$", flat, re.I)
    if planned:
        body = "you're " + planned.group(1)
    else:
        wanted = re.match(r"^i\s+(?:want|need|plan)\s+to\s+(\S.*)$", flat, re.I)
        if not wanted:
            return ""
        body = "you want to " + wanted.group(1)
    body = _tidy_words(you(body))
    return body[:1].upper() + body[1:]


def _tidy_words(text):
    """A country or a month keeps its capital: "going to portugal in june" -> "Portugal in
    June". The same tidy the places in the fact store get, so a plan reads like a sentence."""
    ORDINARY = ("a", "an", "the", "my", "your", "our", "his", "her", "their", "this", "that")
    # A name that is also an everyday word needs the sentence to say it is a place: "roast
    # turkey" is dinner and "going to turkey" is a trip, "china plates" are crockery.
    BOTH = frozenset(("turkey", "china", "bath", "hull", "york", "goa"))
    TRAVEL = ("to", "in", "from", "at", "near", "visit", "visiting", "into")

    def keep(match):
        word = match.group(0)
        if word not in extract.COUNTRIES and word not in extract.MONTHS and word not in PLACES:
            return word
        before = text[:match.start()].split()
        if before and before[-1].lower() in ORDINARY:
            return word
        if word in BOTH and not (before and before[-1].lower() in TRAVEL):
            return word
        return word[:1].upper() + word[1:]
    return re.sub(r"[a-z]+", keep, text)


def _a_thing(name):
    """Whether the thing we were on is a phrase a person would say, and not a verb.

    The subject is cut out of the words of the line, so a verb or an adjective reaches it:
    "im getting married in june" gave "the married", "im learning spanish" gave "the spanish".
    A recap that names one of those reads like a machine reading a label back, so the sentence
    is said without the subject instead.
    """
    words = str(name or "").split()
    if not words:
        return False
    head = words[-1].lower().strip(".,;:!?")
    if not head:
        return False
    if head.endswith(("ing", "ed", "ish")):
        return False
    # "and again" left a subject of "again": a filler word is not a thing to be on either.
    return head not in thread.QUALITY and head not in thread.NON_NOUN


def _says_the_thing(said, thing):
    """Whether the line about to be quoted already names the thing the recap would name.

    A recap says the subject once. "We were on the pressure - you asked how you top it up" says
    it twice, once badly, so the line itself is said instead. The test is the words, not the
    speaker: a thing is named again when one of its own words is in the line, in any order.
    """
    named = {w for w in re.findall(r"[a-z']+", str(thing or "").lower()) if w not in THING_POINTER}
    return bool(named) and bool(named & set(re.findall(r"[a-z']+", str(said or "").lower())))


def _a_description(thing):
    """Whether the thing is a description the store gave an article to, not a name.

    "the pressure" was cut out of "my boiler keeps losing pressure": it is a part of the thing we
    were on, and it reads like a label. "Edinburgh", "my sister" and "the boiler" stand on their
    own - a name or what the person called it - so a recap can be on one.
    """
    words = str(thing or "").strip().split()
    if len(words) < 2:
        return False
    return words[0].lower() in ("the", "a", "an")


def _the_last_ask_about_the_bot(memory):
    """The last thing they asked about the bot, as a sentence, when that is all they have said.

    A chat that opens "are you a real person" and then asks what we have talked about has nothing
    of theirs to go back over - but "nothing yet" is not true either, because they asked something.
    The question is said back in their own words ("whether I am a real person") as the one thing
    the chat has covered, which is what a friend would say.
    """
    for text, reading in reversed(list(thread.user_lines(memory))):
        if not (isinstance(reading, dict) and reading.get("about_bot")):
            return None
        asked = thread.restate(text)
        if asked:
            return asked
    return None


def _as_repaired(word):
    """The word as the reader repairs it: the repair is right for a typo and wrong for a name."""
    return fix_typo(str(word or "").lower()) or str(word or "")


def _with_the_name(said, raw):
    """The same line with a name put back as they spelt it.

    The reader's repairs are for typos, and a name is not one: "ann" is repaired to "an" in every
    line, so "my mum is called ann" came back as "your mum is called an".
    """
    names = []
    for match in NAME_SAID.finditer(raw or ""):
        name = match.group(1).strip("'\u2019-")
        if name.lower() in NOT_A_NAME or len(name) < 2 or name in names:
            continue
        names.append(name)
    if not names or not said:
        return said
    words = said.split()
    for name in names:
        spelled = name[:1].upper() + name[1:]
        wanted = {name.lower(), _as_repaired(name)}
        for at, word in enumerate(words):
            core = word.strip(".,!?;:")
            if core.lower() in wanted:
                words[at] = word.replace(core, spelled)
                break
    return " ".join(words)


SAY_BACK_VAGUE_TAIL = frozenset("""haha hehe hahaha lol lmao hmm ah oh eh yeah yep nope ok okay
    aye mate hun x xx xxx""".split())


SAY_BACK_CORRECTION = re.compile(r"^you (?:meant|mean)\b|\bno wait\b|^you said (?:actually|sorry)\b")


SAY_BACK_VAGUE = frozenset("""
    there here it that this them those these one ones thing things stuff
    like loves love hate hates want wants need needs think thinking thought
    going get got getting be been being said say told tell
""".split())


DENIAL_LINE = re.compile(r"^(?:no|nah|nope)\b.{0,40}\b(?:isnt|isn't|wasnt|wasn't|not)\b"
                         r"|\bno (?:wait|actually)\b|\bsorry,? (?:i )?(?:mean|meant)\b"
                         # "actually hes called jake", "sorry, his name is sam": the line says the
                         # right name for somebody the chat already named, so it is a correction
                         # of that line rather than a new fact about a new person.
                         r"|^(?:actually|sorry|no|nope|wait)\b[^?]{0,40}?\b(?:called|named|"
                         r"name is)\b")


A_NEW_PERSON = re.compile(r"\b(?:my|our|your)\s+\w+")


def _reads_as_a_correction(line):
    """True when the line takes something back rather than stating something new."""
    text = " ".join(str(line or "").lower().split())
    if not text:
        return False
    if DENIAL_LINE.search(text) and A_NEW_PERSON.search(text) and not re.search(
            r"\b(?:isnt|isn't|wasnt|wasn't|not)\b", text):
        return bool(extract.extract(line).get("correction"))
    return bool(DENIAL_LINE.search(text)) or bool(extract.extract(line).get("correction"))


def _lines_that_moved(memory):
    """The lines whose fact a later line put again, with a different value.

    "im 34" / "im 35 now" leaves both lines in the log, and the store has the 35. A summary that
    says the 35 and then "you said you are 34" hands back the value they just replaced. The same
    for a correction: "my budget is 400" / "sorry, i meant 500".

    A value the store recorded with a *frame* is a detail of the fact, not a new value for it:
    "im a nurse" / "i work nights" writes the job key ("nights", frame "work"), and the nurse is
    still what they told the bot. Those lines are kept.
    """
    entries = [entry for entry in (memory.get("facts_log") or [])
               if isinstance(entry, dict) and entry.get("key")]
    framed = {(str(entry["key"])[:-len("_frame")], entry.get("turn")) for entry in entries
              if str(entry["key"]).endswith("_frame")}
    moved = set()
    last = {}
    for entry in entries:
        key = str(entry["key"])
        # A list is a thing that grows ("plans", "pets"): a later line adds one, it does not
        # replace the old one, so nothing on those lines has moved.
        if key.endswith("_frame") or isinstance(entry.get("value"), (list, dict)):
            continue
        text = " ".join(str(entry.get("text") or "").lower().split())
        older = last.get(key)
        if older and older != text:
            if _reads_as_a_correction(entry.get("text")) or (key, entry.get("turn")) not in framed:
                moved.add(older)
        last[key] = text
    return moved


# The facts the summary above says for itself. A key named here is not said back as the line it
# came in on, because the summary already says it better - so a key here with no branch in
# `_summary_reply` is a fact that reaches no reply at all. `tests/test_a_fact_reaches_the_recap.py`
# walks this set and asks the recap for each, which is the check that keeps the two in step.
SUMMARY_KEYS = frozenset(("name", "age", "job", "city", "shift", "workplace", "from", "pets",
                          "kids", "tastes", "allergies", "diet", "condition", "budget",
                          "plan", "plans"))


def _the_summary_already_says(memory, flat):
    """True when every fact the line gave is one the summary says, at the value it holds."""
    known = user(memory)
    keys = set()
    for entry in memory.get("facts_log") or []:
        if not isinstance(entry, dict) or not entry.get("key"):
            continue
        if " ".join(str(entry.get("text") or "").lower().split()) != flat:
            continue
        key = entry["key"]
        then, now = entry.get("value"), known.get(key)
        if isinstance(now, (list, dict)) or isinstance(then, (list, dict)):
            continue
        if then is None or now is None or str(then).lower() != str(now).lower():
            return False
        keys.add(key)
    return bool(keys) and keys <= SUMMARY_KEYS


def _safety_lines(memory):
    """The lines the bot answered with care: a crisis.

    "what do you know about me" is the last ask to answer with an inventory in a chat like that:
    "you said you keep thinking about ending it" turns the worst thing they said into a bullet
    in a list of things kept on file. A death in the family is not that: people do want it
    remembered, and main already said it back.
    """
    out = set()
    for turn in memory.get("turns") or []:
        if not isinstance(turn, dict):
            continue
        if turn.get("module") not in ("safety",):
            continue
        out.add(" ".join(str(turn.get("user") or "").lower().split()))
    return out


CHANGE_WORD = re.compile(r"\b(?:now|new|again|instead|anymore|any more|no longer|these days|"
                         r"moved to|switched to|changed to)\b", re.I)


NEGATIVE_LINE = re.compile(r"\b(?:i|we)\s*(?:dont|don't|do not|didnt|didn't|did not|cant|can't|"
                            r"cannot|never|havent|haven't|have not|am not|im not|i'm not|wasnt|"
                            r"wasn't|was not|wont|won't|will not)\b", re.I)


AN_ATTITUDE = re.compile(r"\b(?:i|we)\s*(?:dont|don't|do not|didnt|didn't|did not)\s+"
                          r"(?:really\s+|actually\s+)?(?:like|love|enjoy|want|fancy|prefer|hate|"
                          r"eat|drink|need|mind|watch|read|believe|trust|care)\b", re.I)


def _shape(line):
    """The frame a line about the person is written in: "im", "i have", "i dont"."""
    words = str(line or "").split()
    if not words:
        return ""
    if words[0] in ("im", "i'm", "ive", "i've", "iam"):
        return words[0]
    if len(words) > 1 and words[0] == "i" and words[1] in (
            "am", "have", "got", "dont", "do", "cant", "cannot", "was", "were", "live", "work"):
        return " ".join(words[:2])
    return words[0]
