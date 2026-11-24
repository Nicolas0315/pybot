"""Part 14 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import copy
import re

from ..compose import fallback, pick
from ..compose import loss as loss_reading
from ..compose import repair
from ..compose.repair import DEEDS_WITH_A_CARD, amends_to, deed_of, owns_the_deed
from ..compose import reading as reading_reply
from ..compose import occasionplan
from ..memory import PERSON_TROUBLE as SOMEONE_TROUBLE
from ..memory import about, person_named, trouble

from ..memory import ack
from ..memory.topics import in_a_safety_thread as _safety_thread

from ..memory import again as _same_again  # the answer under a repeat's lead-in
from ..memory import limits, portions
from ..memory import facts, repeat, tried, more
from ..knowledge import lookup
from .chat_part_02 import (
    AT_IT,
)
from .chat_part_03 import (
    _a_limit, _line_as_read, _their_own_call, REGRET_DEED,
)
from .chat_part_05 import (
    _about_bot,
)
from .chat_part_06 import (
    LOSS, _body_is_a_feeling, END_OF_ROPE, SYMPTOM,
)
from .chat_part_07 import (
    SOMEBODY_ELSE, _a_bare_acknowledgement, _the_heavy_line,
)
from .chat_part_09 import (
    ASKS_FOR_WORDS, A_ROW, A_ROW_CLOSE, ROW_ASK, ROW_CONTACT, ROW_CONTACT_ASK, ROW_ENDING, ROW_HOW,
    WANTS_AN_APOLOGY, _ASKS_AFTER, _a_repair_is_open, _checks_the_fact, _names_the_person,
    _the_base_answers_the_row, _the_base_has_an_answer, _the_deed_before, FEAR, LIMIT,
    MAYBE_SOMEONE, SERIOUS_DIAGNOSIS, SOMEONE_AGAIN, SOMEONE_AGES_IT, SOMEONE_ASK,
    SOMEONE_IS_IT_NORMAL, SOMEONE_MORE, SOMEONE_NEXT, SOMEONE_NEXT_STEP, SOMEONE_NORMAL,
    SOMEONE_NORMAL_ANY, SOMEONE_REPLY, SOMEONE_TROUBLE_ANY, YOUNG, _a_thing_cannot, _after_a_plan,
)
from .chat_part_10 import (
    _frequency_is_the_turn, _better_answer_exists, _grieving, _still_about_me,
)
from .chat_part_11 import (
    BACK_FROM_CARE, DOCTOR_SAID, GOT_RESULTS, HAD_A_THING_DONE, LONG_AGO, NIGHT, NOT_A_DIAGNOSIS,
    PART_FINE, PUT_ON, RESTED, REST_WORD, RESULT_CLEAR, TAKEN_OUT, WAS_IN_CARE, WENT_TO_CARE,
    _A_DRESSING, _a_thing_of_care, _ends_plural, _names_a_person, _the_visit_was_this_week,
    _wearer_is_themselves,
)
from .chat_part_12 import (
    _say,
)


def _a_follow_up_about_their_person(clean, memory):
    """A short ask after a person's trouble is answered about that person, not the topic in hand.

    "my dad keeps saying the same story" then "is that a sign of anything" names nothing of its
    own, so the specialist rule read the story in the chat and handed the turn to the story
    entry, which wrote a story about the word "anything". The person's trouble is the subject
    and this module already has the answer for the short asks after it; claim only those, and
    only when the line is not the turn that first reported it.
    """
    if not isinstance(memory, dict) or len(clean.split()) > 9:
        return False
    record = about(memory)
    if not record:
        return False
    said = " ".join(str(record.get("said") or "").lower().split())
    if not said or said == clean:
        return False
    try:
        return _about_someone(clean, memory) is not None
    except Exception:  # noqa: BLE001 - a reading that raises claims nothing
        return False


# A row with someone close is told far more often than it is asked about, and it is not a mood to
# name back at them. "i argued with my best friend" was answered with the search hedge ("I don't
# know enough to answer that honestly. A search should sort you out quickly"), which reads as if
# not a word of it had been heard: there is nothing to search for in it, and the person wants a
# hand with the person, not a link.
def TAKES_AS_IT_COMES(text, memory=None):
    """The lines this module read whole and no entry has any business answering.

    A row is told, not looked up, and the turns after it are the same conversation one step on.
    Both carry a noun an entry matches: "i had a really silly argument with my sister" was
    answered with a list of things to agree before a family party, "she slammed the door" with a
    door closer, and "should i give her some space" with a couple's boundary script. Nothing in
    an entry knows a row has just happened, so the arbiter asks here.

    A check of the fact the bot just gave is here for the same reason. "is that right" after "how
    long does chicken keep in the fridge" names nothing, so the specialist rule read the
    conversation's topic on it and the entry answered the check by reading its own answer out
    again. The person is asking whether the bot stands behind that answer, so the turn is this
    module's (`thread.checking_a_fact` says which lines are a check).

    A sentence of their own that landed badly is here for the same reason: "i said something
    stupid at dinner" names a dinner and "i said the wrong thing to my sister" a sister, but the
    subject is where or to whom it was said, not what the line is about (`_said_wrong`,
    `_said_unkindly`). So is a verdict the person has already reached on their own life
    (`_their_own_call`) and a feeling said through the body (`_body_is_a_feeling`): in both the
    fact in the line is only what the turn is about, and an entry that answers the fact argues
    with the person.

    One definition, deliberately. This hook had grown a second and a third copy further down the
    file and the last one wins, so the claims in the others never ran: "i argued with my best
    friend" went back to a search hedge and "i feel sick to my stomach with guilt" to the stomach
    entry. A claim belongs here, after the guard that keeps an emergency off it.

    A line that only rules something out ("no horror" after a film, "no treats" after the lead)
    is claimed on the same terms as the rest: it names no subject of its own, so every topic entry
    about the word after "no" is a guess at a subject the person has just taken away. See
    `_a_limit`.
    """
    if _checks_the_fact(text, memory):
        return True
    # A plan ask for a birthday the store already holds: the day and the age are the person's own
    # news, and an entry knows neither, so a card that plans a plain Saturday cannot have the
    # turn. Said only on the lines the plan is written for (bot/compose/occasionplan.py).
    if occasionplan.takes_as_it_comes(text, memory):
        return True
    # A line that asks what the thing on the screen costs names nothing of its own, so the
    # specialist rule read the conversation's topic on it and the entry priced its own subject:
    # after "should i get it serviced" ("a gas boiler service is usually 60 to 120 pounds"),
    # "how much is that usually" was answered with the price of a new boiler. The figure the
    # person is asking about is the one in that answer, so the turn is this module's
    # (`repeat.asks_what_that_costs`).
    try:
        if repeat.asks_what_that_costs(text, memory):
            return True
    except Exception:  # noqa: BLE001 - a reading that raises is a line this module does not claim
        pass
    clean = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    if _a_follow_up_about_their_person(clean, memory):
        return True
    if _frequency_is_the_turn(clean, memory):
        return True
    if LOSS.search(clean) or _safety_thread(memory):
        return False
    # The effort that is not landing is read whole here: "im going round in circles" is a trip the
    # store answers ("Circles - nice. When are you going?"), and the person is telling the bot
    # where they are stuck rather than asking about the word.
    if AT_IT.match(clean):
        return True
    # A limit on what somebody can do - "she cant walk far", "two adults, one is in a wheelchair",
    # "my dad cant walk far so we need somewhere flat" - is a fact about the plan, and it used to
    # be read as a report about the person's health, echoed back word for word, or met with "keep
    # going" (bot/memory/limits.py). Read whole here too, so the specialist rule cannot hand the
    # turn to the entry keyed on the walking word or the place word in it.
    try:
        if limits.reply(text, memory) is not None:
            return True
    except Exception:  # noqa: BLE001 - a reading that raises is a line this module does not claim
        pass
    # A doubt that names its own figure ("is 3500 too much", "is 1.5 bar a lot") names no subject
    # of its own either, so the specialist rule read the conversation's topic on it and the entry
    # answered by saying its whole answer again ("Same as before: ...") instead of judging the
    # figure. The claim is the same reading that produces the reply, so it is only made on a line
    # this module can answer, and only on one whose figure is in the line: a bare "is that enough"
    # may be about a figure the person gave, which the memory store reads already.
    try:
        if reading_reply.judges_a_figure(text, memory):
            return True
    except Exception:  # noqa: BLE001 - a reading that raises is a line this module does not claim
        pass
    line = _line_as_read(text)
    # A line that asks about the bot itself: "what do you do when im not here" five turns into a
    # tomato chat was answered with the tomato card. Nothing on the line is a subject of the
    # world - the thing in front of them is - so the card matched only the topic the chat is on,
    # and the specialist rule lifted it over this module's own answer. `_about_bot` is the same
    # table `_respond` answers from, and it is narrow: "do you cook a chicken with the lid on"
    # names a chicken and is left to the kitchen (`_self_only`).
    # The name the person gave the bot is left out: it is not a question about the bot's nature
    # but a fact about this chat, and the line that asks for it is answered with their name and
    # nothing else ("You call me Pip.") rather than with the pool's "What can I do for you?".
    try:
        named = str(((memory or {}).get("user") or {}).get("bot_name") or "").strip()
        if not (named and facts.BOT_NAME_ASK.search(line)) and _about_bot(
                line, (memory or {}).get("understood") if isinstance(memory, dict) else None,
                memory):
            return True
    except Exception:  # noqa: BLE001 - a reading that raises is a line this module does not claim
        pass
    if _body_is_a_feeling(line):
        return True  # a feeling said through the body is not the body
    if _a_limit(text, memory):
        return True  # a line that only rules something out names no subject of its own
    if _their_own_call(line):
        return True  # the verdict they have already reached on their own life
    if amends_to(clean):
        # How to make it up to somebody is a question about what to do, and no entry has it: the
        # cooking one answered "how do i make it up to my mum" with a tray bake.
        return True
    if _a_repair_is_open(memory) and THEY_ARE_NOT_TALKING.search(clean):
        # The silence that follows the apology belongs to the repair, and the words "wont talk to
        # me" also name a small child who is late speaking.
        return True
    if (ASKS_FOR_THE_WORDS.search(clean) and _after_a_repair(memory)
            and _the_deed_before(memory) != SAID_WRONG_DEED):
        # The words of the apology were asked for, and the pool of the deed has them: a row keyed
        # on the person in the line answers with what to ask them instead.
        return True
    if _said_wrong(clean) or _said_unkindly(clean):
        # ...unless a row already has this deed's answer: what they did is the row's subject and
        # the row says the next step better than the composer's short repair does.
        return not _an_entry_answers_the_deed(clean, memory)
    said = A_ROW.search(clean)
    if (said and A_ROW_CLOSE.search(clean)
            and not ROW_ASK.match(clean) and not clean.rstrip().endswith("?")
            and not _ASKS_AFTER.search(clean[said.end():])
            and len(clean.split()) <= 18):
        return True  # the row itself, on the turn it is said
    row = memory.get("row") if isinstance(memory, dict) else None
    if not isinstance(row, dict) or not row.get("them") or len(clean.split()) > 14:
        return False
    if _the_base_answers_the_row(clean, memory):
        return False  # the entry about this very row has the answer, and `_a_row_next` stands down too
    how = bool(ROW_HOW.search(clean))
    if how and row.get("handed_over"):
        # The base answered the row itself, so its own script is what comes back here; a claim on
        # the turn only framed that script as a repeat ("Same as before: ...").
        return False
    if (how and (WANTS_AN_APOLOGY.search(clean) or ASKS_FOR_WORDS.search(clean))
            and _the_base_has_an_answer(clean, copy.deepcopy(memory)) is not None):
        # The knowledge base has the words written out and this module answers with a sentence
        # about them, so the turn is the base's - the same test `_a_row_next` makes.
        return False
    if not (ROW_ENDING.search(clean) or how
            or (ROW_CONTACT.search(clean) and ROW_CONTACT_ASK.search(clean)
                and _names_the_person(clean, row))):
        return False
    waited = len(memory.get("turns") or []) - int(row.get("turn") or 0)
    return 0 < waited <= 3


def _after_a_repair(memory):
    """True when the line before this one was a sentence of theirs that landed badly.

    The repair is answered on the turn it is said, so the follow-up ("what do i do", "how do i
    fix it") is the next step of the same repair rather than a fresh report about the person it
    was said to. Without this the store's trouble record from that line answered "what do i
    do" with a note to take to the GP about their mum.
    """
    if not isinstance(memory, dict):
        return False
    told = [turn.get("user") for turn in (memory.get("turns") or [])[-1:] if isinstance(turn, dict)]
    said = " ".join(str(told[0] if told else "").lower().split())
    # "how do i make it up to my mum" names no deed and is the same repair asked as a question,
    # so the turn after it ("what do i say") is the words rather than a fresh subject.
    return bool(said) and bool(_said_wrong(said) or _said_unkindly(said) or amends_to(said))


def _about_someone(clean, memory):
    """The reply for a line about a person they love that reports something not right, or None."""
    if _safety_thread(memory):
        # Mid-emergency the person is the one on the floor, not a symptom to be worked up: after
        # "my husband fell off a ladder" the next line "he is confused" is the head injury going
        # on, and a GP/dementia card answers a question nobody asked (quality watch, foo-08). The
        # safety thread's own continuation has the line.
        return None
    if loss_reading.reads_as_loss(clean) or _grieving(memory, clean):
        return None  # a house in grief is not the place for a careful question about a partner
    # The last thing they said was a sentence of their own that landed badly, so "what do i
    # do" is the next step of repairing it, not a card about the person they said it to: the
    # repair has somebody to make it up to, and their health is not what is in question.
    if _after_a_repair(memory) and not SOMEONE_TROUBLE_ANY.search(clean):
        return None
    record = about(memory) if isinstance(memory, dict) else None
    read = memory.get("understood") if isinstance(memory, dict) else None
    # The trouble the last line reported is the one this short ask leans on even when that line
    # was answered by the knowledge base and no record was kept: "my mums getting forgetful" got
    # the memory card and no note, so "is it just her age" - the same question, worn down to its
    # worry - had nothing behind it and got the search hedge. The reading lives in the store, so
    # the same line reads the same way whoever answered it.
    if not record and SOMEONE_AGES_IT.search(clean):
        above = (read or {}).get("leans_on")
        said = str((above or {}).get("text") if isinstance(above, dict) else above or "")
        kept = trouble(said) if said else None
        if kept in SOMEONE_NORMAL:
            return SOMEONE_NORMAL[kept]
    if record and len(clean.split()) <= 9:
        kept = record.get("trouble")
        asks_normal = SOMEONE_IS_IT_NORMAL.search(clean)
        # A baby's night is not an adult's: the method a grown-up uses (no caffeine, out of bed
        # after twenty minutes) is nonsense said about an eight-month-old, and "what should I look
        # out for" is better answered by the knowledge base, which has the baby's own night in it.
        # "Is that normal" is safe for both: sleep going in patches is the same sentence for a
        # baby and for a nan.
        young_night = kept == "sleep" and not asks_normal \
            and YOUNG.search(str(record.get("said") or ""))
        if kept in SOMEONE_NEXT and (asks_normal or SOMEONE_NEXT_STEP.search(clean)) \
                and not young_night:
            pool = (SOMEONE_NORMAL[kept],) if asks_normal else (SOMEONE_NEXT[kept],)
            who = record.get("who") or "them"
            return pool[0].format(who=who)
        if SOMEONE_AGES_IT.search(clean):
            # "is that just old age" about a worry the kinds do not name ("stopped going out",
            # "isnt herself") still gets the honest answer rather than the search hedge, which
            # reads as if not a word of it had been heard.
            return SOMEONE_NORMAL_ANY
    # A second example has to be a *second* one: on the turn the trouble is first told, the words
    # in it ("he had a fall") are not an "again", so the reply is the plan, not the note-taking.
    mine_now = len((memory or {}).get("turns") or [])
    first_said = record.get("trouble_turn", -1) if record else -1
    if record and first_said < mine_now and len(clean.split()) <= 12:
        kept = record.get("trouble")
        pattern = dict(SOMEONE_TROUBLE).get(kept)
        more = (pattern is not None and pattern.search(clean)) or (
            SOMEONE_MORE.search(clean) and len(clean.split()) <= 8)
        if kept in SOMEONE_AGAIN and more:
            return SOMEONE_AGAIN[kept]
    if (LIMIT.search(clean) or ack.a_limit_on_the_plan(clean)) and _after_a_plan(memory, clean):
        return None  # a limit given after a plan is a fact about the plan
    if _said_wrong(clean) or _said_unkindly(clean):
        # A sentence that landed badly is the conversation, not a symptom of the person named in
        # it: "my sister said the wrong thing to me" is not a report about the sister's memory.
        return None
    if not MAYBE_SOMEONE.search(clean):
        return None
    if LOSS.search(clean) or END_OF_ROPE.search(clean):
        return None
    who = (record or {}).get("who")
    if not who:
        who = person_named(clean, memory)
    if not who:
        return None
    young = YOUNG.search(clean)
    if FEAR.search(clean):
        return None  # a fear about something is theirs to talk through, not a report of it
    # The kind is the store's reading, not a second table here, so the reply and the note kept in
    # memory["person"]["trouble"] can never disagree about what the line showed.
    # A date of ours going by is a complaint about the partner, not a memory sign: the composer's
    # grievance pool has that line ("Annoying. Tell me how it has gone so far..."), and answering
    # it here sent "my husband keeps forgetting our anniversary" to a GP for a dementia workup.
    if fallback.a_date_of_ours_forgotten(clean):
        return None
    kind = trouble(clean)
    if kind == "hospital" and SERIOUS_DIAGNOSIS.search(clean):
        return pick(SOMEONE_REPLY["diagnosed"], memory).format(who=who)
    if kind in SOMEONE_REPLY and not (SYMPTOM.search(clean) and kind == "ill") \
            and not (kind in ("low", "sleep") and young):
        # Their body is the other modules' turn, and safety's first; a two-year-old not talking
        # much is not a withdrawn adult.
        return pick(SOMEONE_REPLY[kind], memory).format(who=who)
    if isinstance(read, dict) and read.get("kind") == "question":
        # A question that names no trouble has its own answer somewhere. One that does is still
        # a report ("she keeps forgetting where things are in the kitchen" is read as a "where"
        # question by the understanding engine), so the kinds above are tried first.
        return None
    if SOMEONE_TROUBLE_ANY.search(clean) and not _a_thing_cannot(clean) \
            and not _still_about_me(clean) \
            and not _better_answer_exists(clean, memory):
        return pick(SOMEONE_ASK, memory).format(who=who)
    return None


def _own_medical_news(flat, memory, clean=""):
    """Their own visit, scan, result or diagnosis, answered about that thing, or None.

    The line has to be the person's own: "my mum came out of hospital" is `_about_someone`'s
    line, and a line that reads as distress is left to the modules that answer distress.
    Nothing is said that a doctor did not - the reply names what they were told and what to do
    with it, and never a diagnosis, a dose or a prognosis of the bot's own.
    """
    if _reads_as_distress(clean or flat):
        return None
    # "they said my knee is fine but i should rest it" comes before the somebody-else check: the
    # "they" in it is the people at the hospital, and the body part is the person's own.
    match = PART_FINE.search(flat)
    if match:
        part = " ".join(str(match.group("part") or "").split())
        # The word after "my" has to be a body part: "they said my son is fine" is about the son,
        # and the reply about a knee that came back fine is about the wrong body.
        if (part and len(part.split()) <= 2 and part.lower() not in facts.NOT_A_PRONOUN_NAME
                and not _names_a_person(part)):
            # Resting is only the advice when the thing is one resting helps, or when the line
            # itself says so.
            pool = "med_part_fine" if (REST_WORD.search(flat)
                                       or part.split()[-1].lower() in RESTED) \
                else "med_part_fine_result"
            return _say(pool, memory, **_a_thing_of_care(part, article=False))
    # "they put a cast on my arm" is the person's own arm, and the "they" is the people at the
    # hospital: it comes before the somebody-else check, and only when the thing put on is theirs.
    match = PUT_ON.search(flat)
    if match and not LONG_AGO.search(flat) and _wearer_is_themselves(flat, match):
        thing = match.group("thing")
        # A dressing covers a wound for a day or two and comes off again; a cast, a boot or a sling
        # is on for weeks and holds a bone still. One pool for both says "for a few weeks" about a
        # bandage, which is the wrong length of time for the thing they were given.
        pool = "med_dressing" if _A_DRESSING.search(thing) else "med_wearing"
        return _say(pool, memory, **_a_thing_of_care(thing))
    if SOMEBODY_ELSE.search(flat):
        return None
    match = RESULT_CLEAR.search(flat)
    if match:
        thing = match.group("thing")
        plural = _ends_plural(thing)
        return _say("med_clear_plural" if plural else "med_clear", memory,
                    **_a_thing_of_care(thing, article=not plural))
    match = DOCTOR_SAID.search(flat)
    if match:
        dx = " ".join(str(match.group("dx") or "").split()).strip(" .,;!")
        if dx and dx.lower() not in NOT_A_DIAGNOSIS and len(dx.split()) <= 3:
            return _say("med_diagnosis", memory, **_a_thing_of_care(dx, article=False))
    # A visit at night is the same news with the evening gone, and "that is never a fun morning"
    # is the wrong thing to say about it, so the time of the telling picks the pool.
    visit = "med_visit_night" if NIGHT.search(flat) else "med_visit"
    match = BACK_FROM_CARE.search(flat)
    if match:
        return _say(visit, memory, **_a_thing_of_care(match.group("place")))
    match = WENT_TO_CARE.search(flat)
    if match and _the_visit_was_this_week(flat):
        return _say(visit, memory, **_a_thing_of_care(match.group("place")))
    match = WAS_IN_CARE.search(flat)
    if match and _the_visit_was_this_week(flat):
        return _say(visit, memory, **_a_thing_of_care(match.group("place")))
    match = TAKEN_OUT.search(flat)
    if match and not LONG_AGO.search(flat):
        return _say("med_out", memory, **_a_thing_of_care(match.group("thing")))
    # The results are not the test: "i got my scan results back" is news about the wait being
    # over, and it comes before the visit that produced them.
    match = GOT_RESULTS.search(flat)
    if match:
        return _say("med_results", memory, **_a_thing_of_care(match.group("thing") or "results"))
    match = HAD_A_THING_DONE.search(flat)
    if match and not LONG_AGO.search(flat):
        return _say(visit, memory, **_a_thing_of_care(match.group("thing")))
    return None


def claims_instead(text, memory):
    """The arbiter's `CLAIMS_INSTEAD`: this line's next step is this module's answer.

    "i tried that and it didn't work" after a how-to is a report on the advice, and the composer
    claims those lines as it comes, so its own line - how to say the attempt went - is what the
    person got even when this module had the next step in the thread ("a plumber, with the plunger
    and the trap already ruled out"). Said here rather than in the arbiter because only the module
    that has the answer can say whether it has one: `tried.pool_for` is the same reading that
    produces the reply below, so a line it reads as a plain report that the answer did not work is
    the line, and nothing else is claimed.

    No is the safe answer, and it is also the common one: with no pool, or a report that carries
    its own verdict ("that helped a bit", "it made it worse"), the composer's outcome line keeps
    the turn.
    """
    clean = " ".join(str(text or "").lower().split())
    # A bare "ok" or "cool" after something hard is this module's line, and the nudge module says
    # it answers every bare continuation as it comes - which signed a death off with "That's all
    # from me, and there is no hurry". The reading is the same one that picks the reply, so the
    # claim is as narrow as the reply it stands for: it is only made on a line that says nothing
    # but "I heard that" in a thread that is hard.
    if _a_bare_acknowledgement(clean) and _the_heavy_line(memory):
        return True
    # A line that asks how many the answer in hand feeds, or a count of people said on the turn
    # after the reply asked for one, is the answer's own sum, and the topic entries have a card
    # about party food that answers a different question: "how much potato salad for a party" /
    # "how many does that feed" got the party-food card. The claim is the same reading that picks
    # the reply, so it is only made where this module has the answer.
    if (portions.an_ask(clean, memory) or portions.a_count_to_fill(clean, memory)
            or portions.a_bare_count_to_fill(clean, memory)):
        return True
    try:
        if tried.pool_for(clean, memory):
            return True
    except Exception:  # noqa: BLE001 - a reading that fails claims nothing
        pass
    # The silence after the apology is the turn the repair was making: "she wont talk to me" names
    # no deed, so the row for a child who is late speaking claimed it and answered with the ages
    # children start talking at. The claim is as narrow as the reply: the same repair has to be
    # open in the turns just said.
    if _a_repair_is_open(memory) and THEY_ARE_NOT_TALKING.search(clean):
        return True
    # A regret about something done to somebody is the guilt family's line, and the composer
    # claims every regret as it comes (`bot/compose/fallback.py:takes_as_it_comes` asks
    # `remark.regret_reply_for`). That pool asks the hindsight question - "what would you change?"
    # - which is right for a choice and wrong for a wrong to own: "i regret telling her" is a
    # confession, and the guilt line is the answer to it. `REGRET_DEED` is the reading that puts
    # the line in the guilt pool, so the claim is as narrow as the reply it stands for.
    return bool(REGRET_DEED.search(clean))


CLAIMS_INSTEAD = claims_instead


# --- something they said that they wish they had not said --------------------
# "i said the wrong thing to my sister" was answered with the trouble of the person named - the
# memory pool of the someone-unwell reader ("that is worth mentioning to a GP ... what you have
# noticed about your sister") - and "i said something stupid at dinner" was answered with a
# dinner recipe. In both, the person is telling you about a sentence of their own that landed
# badly; the person named is who it was said to, not who is unwell, and the meal is when it
# happened. What a friend answers is the regret and the next step: say it soon, say which bit,
# and leave the explaining out.
# The one deed here where the thing that landed badly was a sentence, so the pool above is the
# right one for it. Every other deed gets the one below.
SAID_WRONG_DEED = "said the wrong thing"


SAID_WRONG = re.compile(
    # "i always say the wrong thing to my mum" is the same regret as "i said the wrong thing to
    # my mum", said as the pattern it is.
    r"\bi (?:(?:keep|always|still|just|also|often|usually|sometimes|constantly)\s+){0,2}"
    r"(?:said|say|told|tell)\s+(?:the wrong thing|something\s+(?:stupid|awful|daft|silly|"
    r"dumb|mean|horrible|wrong|embarrassing|terrible)|it badly|that badly)\b|"
    r"\bi (?:put|putting|put my)\b[^.]{0,12}\bfoot in it\b|"
    # A raised voice is only this when the target is the person writing: "i snapped a photo at
    # the wedding" is a camera, and "i shouted at my son last night" already has a card of its
    # own that names the repair ("say sorry plainly, name what happened"), which is more use
    # than anything this pool can say. What is left is being cross with yourself out loud.
    r"\bi (?:really |kind of |sort of )?(?:snapped|shouted|yelled|swore)\s+(?:at|to|with)\s+"
    r"(?:myself|yourself|ourselves)\b|"
    r"\bi (?:was|been|were) (?:rude|horrible|mean|cruel|sharp|short|unfair|awful|dreadful|"
    r"terrible|nasty|unkind) (?:to|with)\b(?! be\b)|"
    # "i was off with my sister" is short-tempered with her; "i was off to bed early" is not a
    # regret at all, and "off" on its own read the second one as the first.
    r"\bi (?:was|been|were) off with\b|"
    r"\bi (?:upset|offended|insulted|embarrassed|hurt)\s+(?:my|his|her|their|our)\s+"
    r"(?:mum|mom|mam|mother|dad|father|son|daughter|child|kid|baby|partner|husband|wife|"
    r"sister|brother|nan|nana|gran|granny|grandma|grandad|grandpa|aunt|uncle|cousin|friend|"
    r"flatmate|neighbour|neighbor|boss|colleague|team)\b|"
    r"\bi (?:hurt|upset|offended) (?:her|him|them|someone|somebody)(?:'s)? feelings\b|"
    # "i told her her cooking was awful": they are telling you what they said to someone, and
    # the adjective is their own verdict, not a thing they are sorry to have heard.
    r"\bi (?:said|told)\b[^.]{0,40}\b(?:was|were|is) (?:awful|horrible|stupid|mean|rude|"
    r"unkind|dreadful|terrible|nasty|rubbish|disgusting|pathetic)\b")


# A deed that is a strain, a bug or a mood is not this: "i hurt my back" is the body, "i snapped
# my phone in half" is a broken thing, and "i said nothing for an hour" is not a regret. The
# regex asks for the words people use about a sentence that landed badly, and these keep the
# physical readings out.
SAID_WRONG_NOT = re.compile(
    r"\bi (?:hurt|upset|pulled|broke|twisted|strained|cut|burnt|burned) my\b|"
    r"\bi snapped my\b|\bi said (?:nothing|no|yes|okay|ok|bye|hello|hi)\b")


# The repair pool is a conversation with the person the sentence was said to, so it needs one
# that is still there to have it. Three lines were taking it with nobody to repair anything with:
#
#   "i said the wrong thing at the interview and didnt get the job" - the interview is over and
#   the job is gone: "go back and say which bit was wrong" sends them nowhere, and what there is
#   to answer is the loss. Main's answer for it (the disappointment, then one line of feedback)
#   is the better one, so this stands the pool down rather than writing a second one.
#   "i was horrible to myself today", "i snapped at myself" - the person is the target, so
#   "let them be annoyed first" puts a second person in a line that has none. Those take the
#   being-cross-with-yourself pool instead (SAID_WRONG_AT_THEMSELVES, below).
#   "i was horrible to my dog" - a dog does not read an explanation as an excuse.
SAID_WRONG_LOST = re.compile(
    r"\b(?:didnt|didn't|did not|never)\s+(?:get|got|win|won|pass|passed|make|made)\b|"
    r"\b(?:got|been) (?:fired|sacked|dumped|rejected|turned down)\b|"
    r"\bi (?:lost|lose|failed)\b|"
    r"\b(?:she|he|they|we)\s+(?:left|walked out|split|broke up|stopped talking|moved out)\b|"
    r"\b(?:wont|won't|wouldnt|wouldn't) (?:talk|speak) to me\b|"
    r"\bthere'?s no fixing\b|\bit'?s too late\b|\bno longer (?:speaks?|talks?|friends?)\b")


# What a note to a pet gets is not this: no explanation, no apology, no letting them be annoyed.
SAID_WRONG_TO_AN_ANIMAL = re.compile(
    r"\b(?:to|with|at)\s+(?:my|our|the|a)\s+(?:dog|cat|puppy|kitten|horse|pony|rabbit|"
    r"hamster|guinea pig|budgie|parrot|pet|fish|bird|chickens?|sheep|cow|goat|lamb)\b")


# A professional is told, not apologised to: "i said the wrong thing to my doctor about my
# symptoms" is a briefing they made a mess of, and the repair pool's "naming the exact thing you
# regret shows you heard it" invents somebody who was hurt by it.
SAID_WRONG_TO_A_PROFESSIONAL = re.compile(
    r"\b(?:to|at|with)\s+(?:my|our|the)\s+(?:doctor|gp|nurse|consultant|surgeon|midwife|"
    r"health visitor|dentist|orthodontist|physio(?:therapist)?|pharmacist|optician|vet|"
    r"solicitor|accountant|bank|landlord|letting agent)\b[^.?!]*\babout\b")


# Somebody being hard on themselves in the words of a regret: the target is them, so the repair
# pool's "let them be annoyed first" invents a person to go and apologise to. Same pool as
# "im so annoyed with myself", which is the same thing said the other way round.
SAID_WRONG_AT_THEMSELVES = re.compile(
    r"\b(?:to|with|at)\s+(?:myself|yourself|ourselves)\b|"
    r"\bi (?:feel|felt|look|sound|am|'m) (?:like )?(?:such )?(?:an? )?"
    r"(?:idiot|fool|mug|failure|fraud|moron|mess|disgrace)\b")


SAID_WRONG_NEXT = (
    "Pick the moment rather than the words: not mid-argument and not as they walk out. Ask for "
    "two minutes, say the one sentence, and let them answer it.",
    "Say it once and then let them talk. The explaining is what turns a repair back into the row.",
    "Don't ask them to tell you it's fine. Say what you got wrong, then let them be annoyed or "
    "not - that part is theirs.",
    "Ask what they heard. If it is not what you meant, that is the next sentence, and it is worth "
    "saying rather than arguing.",
    "Let what you do next carry it: the few days after matter more than the apology itself.",
)


# The follow-up to a repair: asking what to do, not asking what was said.
# The follow-up that asks for the sentence rather than the next step: "what do i actually say to
# her". It has its own pool because the answer is the words, and DEED_NEXT's advice would be a
# step down from them.
# The asks that lean on the turn before them are the repair reading's own (bot/compose/repair.py),
# because the knowledge base reads the same repair to stand the wrong card down.
ASKS_FOR_THE_WORDS = repair.ASKS_FOR_THE_WORDS


ASKS_WHAT_TO_DO = repair.ASKS_WHAT_TO_DO


SAID_WRONG_REPLIES = (
    "Say it sooner than feels comfortable, and name the sentence itself rather than hinting at "
    "it: people forgive a plain \"that came out badly, I didn't mean it\" far more easily than a "
    "vague apology for everything.",
    "Keep it to what you said and that you got it wrong. The explaining is the part that makes "
    "it land as an excuse, so leave it for later, or out.",
    "Own the one sentence, not everything around it: naming the exact thing you regret shows you "
    "heard it, and a general apology mostly sounds like you want it over with.",
    "Most people want to know you noticed, not that you are sorry in general, so go back and say "
    "which bit was wrong. It costs you a minute and it is usually the whole repair.",
    "It is fixable, and the fix is a sentence rather than a gesture. Say the one thing you got "
    "wrong, plainly, and stop there - they can be annoyed while you leave the details alone.",
)


# A deed of their own that was not a sentence: a birthday let pass, a promise broken, a night
# out that was cancelled at the last minute, money that was not told about. The reading is
# `bot/compose/repair.py` (`deed_of`); the pool is separate because there is nothing to quote
# back. "i forgot my mums birthday" was answered with a party to plan and "i lied to my wife
# about the money" with how to split the bills - both are the other person's question, and the
# one this person asked is what to do now. The moves are the same three a repair always has -
# own it plainly, name the one thing rather than the whole story, and do something - and the
# words differ only because the deed was an act rather than a sentence.
DEED_REPLIES = (
    "Own it before they have to bring it up, and keep it to one sentence: what you did, that "
    "you are sorry, and what you will do instead. The explaining can come later, or not at all.",
    "Say the plain version first - name what you did, say you are sorry, and add no reason "
    "unless they ask for one - then do the small thing you can actually do this week.",
    "The apology is the small part; the change is the rest. Name what you did once, then let the "
    "next few weeks show it rather than repeating it every time you speak.",
    "Put it right sooner than feels comfortable, and name the one thing rather than a list of "
    "everything you feel bad about. People forgive a specific \"I got that wrong\" far more "
    "easily than a general apology for a whole week.",
    "Say what you did, then stop. Adding why is the part that sounds like an excuse, and they "
    "can be annoyed for a bit without you talking them out of it.",
)


# A deed that was a thing not done - the call not made, the visit not paid, the present not
# bought - takes the same repair with a different first move: there is nothing to own that they
# have not noticed already, so the answer is the doing of it now.
LEFT_IT_TOO_LONG_REPLIES = (
    "Do it today, before you explain anything: the call, the visit, the present that is late "
    "arriving. Then say the one line - \"I left it too long and I'm sorry\" - because a reason "
    "offered first sounds like the reason you did not.",
    "Ring rather than message, and lead with them rather than with your week: they have been "
    "waiting, and what they want to hear is that you know it. Put the next one in your phone "
    "before you hang up.",
    "Name the gap once, plainly, and then be there: \"It's been too long and that's on me.\" A "
    "visit or a call booked this week says the rest, and asking them to reassure you costs them "
    "the thing you owe them.",
    "Pick the smallest real thing that ends the gap today - a call on the walk home, a note, a "
    "date in the diary with the day fixed - and do that rather than plan a bigger gesture later.",
)


# A date that was missed has its own words, because the day is the thing and the make-up is the
# answer: "i forgot my mums birthday" is not helped by advice for a promise or a lie.
FORGOT_DATE_REPLIES = (
    "Own it today, and take the sting out of it by naming the day: \"I got the date wrong and "
    "I'm sorry - it isn't that it doesn't matter.\" Then book the thing, because a make-up that "
    "happens this week beats a bigger sorry that stays a plan.",
    "Say it before they have to ask, and don't hide behind the date: \"I knew it was coming and I "
    "still let it pass, and I'm sorry.\" Then do the specific thing - a dinner, a card, a visit - "
    "rather than waiting to be forgiven.",
    "Ring rather than text, and keep it to the one thing: you missed the day, you are sorry, and "
    "here is what you are doing about it. A late card that arrives is worth more than an apology "
    "that asks them to tell you it is fine.",
)


# "what do i actually say to her" after a deed: the words of the apology rather than what to do
# next, which DEED_NEXT answers. The pool is the sentence itself because that is the whole ask.
DEED_WORDS = (
    "Name it in one line and stop: \"I let you down over this and I'm sorry - that was my doing.\" "
    "Then the one thing you are doing about it, because a sentence with a next step in it is heard "
    "as meant rather than as sorry-sounding.",
    "Say what you did, that it was yours, and leave why out of the first sentence: \"I got that "
    "wrong and I'm sorry.\" If they ask why, answer it then; before that it arrives as a defence.",
    "Start with the thing they are owed rather than how bad you feel: \"You had every right to be "
    "annoyed with me, and I'm sorry.\" Then ask what would help, and do that one thing.",
    "Keep it short and specific: what you did, that you are sorry, and the change they can see in "
    "the next few weeks. \"I'm sorry - I won't do that again\" is worth more when you name which "
    "\"that\" was.",
)


FORGOT_DATE_WORDS = (
    "\"I missed your birthday and I'm sorry - I'm not going to pretend I was saving it up.\" Say "
    "that on the phone rather than in a message, then ask when they are free this week, so the "
    "next thing after the apology is a date in the diary.",
    "\"I got the day wrong and I've felt rotten about it all week.\" Naming the day is what makes "
    "it land as an oversight rather than as not caring, and it is the one thing they are waiting "
    "to hear.",
    "Lead with the sorry and then the plan: \"I'm sorry I let it go by - I've booked a table for "
    "Friday, if you're free.\" The booking is the apology; asking them to reassure you is not.",
)


# "how do i make it up to my mum": no deed is named, so what they want is the thing that would put
# it right rather than the words. Two of these lines were answered with a tray bake, because
# "make" and "up to" are also how a dish is sized for a table.
AMENDS_REPLIES = (
    "Pick the one thing they would actually notice and do it this week: the visit, the lift they "
    "always ask for, the money paid back, the afternoon spent with the child. Amends is a verb - "
    "what they are owed is the thing made good, not a longer apology.",
    "Say sorry for your part of it in one sentence, then ask them: \"what would help?\" once, and "
    "do that rather than what you would have chosen. Most people want the thing put right, and the "
    "ones who want to say their piece get to say it.",
    "Do it in their language rather than yours: if they tidy and cook, turn up and help with that "
    "rather than buying something. Then keep it up for a few weeks, because the change after the "
    "apology is the part that reads as meant.",
    "Start with the smallest real thing you can finish today - the call you have put off, the "
    "message that says you know you owe them - then tell them what you are doing about the rest "
    "rather than asking them to trust the intention.",
)


FORGOT_DATE_NEXT = (
    "Ring them today rather than waiting for a better moment, and keep it to the three things: you "
    "missed the day, you are sorry, and here is what you are doing about it. Then put the next one "
    "in your phone with a week's warning on it, because the second miss is the one that hurts.",
    "A card and a date beat a longer apology: book something they would like for this week and "
    "tell them the day rather than asking them to choose it. What they are owed now is the thing "
    "made up, not the explaining.",
    "Get the next one right in public: say the sorry once, then let the dinner or the visit do the "
    "rest. Bringing it up again a month later makes them do the forgiving twice.",
)


# The turn after one of those, when the ask is "what do i do": the first move has been said, so
# the second one is the answer. Handing back the first pool is the repeat the pool above is
# written to avoid.
def _the_deed_pool(deed):
    """The pool for the deed, because a missed day and a call that was never made differ."""
    if deed == "forgot a date":
        return FORGOT_DATE_REPLIES
    if deed == "left it too long":
        return LEFT_IT_TOO_LONG_REPLIES
    return DEED_REPLIES


def _the_words_pool(deed):
    """The words asked for after a deed: a missed day has its own sentence to say."""
    return FORGOT_DATE_WORDS if deed == "forgot a date" else DEED_WORDS


# "she wont talk to me" the day after the apology is the same repair. The line names no deed, so
# it was read as a new subject and a child who is late to speak answered it.
THEY_ARE_NOT_TALKING = re.compile(
    r"\b(?:he|she|they)(?:s|'s|re| is| are|'re)?\s+(?:not|isn'?t|aren'?t|still not|hasnt|"
    r"has not|"
    r"wont|won'?t)\s+(?:speak|speaking|talk|talking|reply|replying|replied|answer|answering|"
    r"answered|call(?:ed|ing)?"
    r"text(?:ed|ing)|messag(?:ed|ing)|been in touch)\b|"
    r"\b(?:he|she|they)(?:s|'s|re| is| are|'re)?\s+(?:giving me the silent|ignoring me|"
    r"blanking me|gone quiet on me)\b")


NOT_TALKING_AFTER_A_REPAIR = (
    "Give them the day, then send one message with no question in it: what you did, that you are "
    "sorry, and that you will be there when they are ready. Asking them to say it is fine is the "
    "part that keeps it going.",
    "Their silence is the answer for now, so do not fill it. Keep the ordinary things going - the "
    "call at the usual time, the lift you promised - and let that, rather than a second apology, "
    "be the thing that says you meant it.",
    "Try once the way they cannot ignore - the phone rather than a text, in person if you can - "
    "then wait. Say the sentence, ask nothing of them, and leave the next move with them: two "
    "apologies in a week sound like you want something back.",
)


DEED_NEXT = (
    "Do it today rather than waiting for a good moment, and in person or on the phone rather than "
    "a text: name the one thing you did, then ask what would help.",
    "Ask what they want from you now and do that rather than what you would choose. People usually "
    "want the thing made good, not a longer apology.",
    "Pick the smallest real thing you can put right this week - the dinner you book, the money you "
    "pay back, the call you make - and do it before you explain anything.",
    "Go back to them rather than round it: say the one sentence you owe them, then leave the next "
    "move with them instead of asking to be told it is fine.",
)


# The other end of it: somebody said something unkind to them. The same reader found this line
# too - "my sister said the wrong thing to me" got the unwell-relative card, quoting "wrong
# thing" as something wrong with the sister. What is said is what the line is about, so the
# adjective after a speech verb is read as the content of a sentence, not as a symptom.
SAID_UNKINDLY = re.compile(
    r"\b(?:said|says|saying|told|tells|shouted|yelled|snapped|swore|swears|texted|messaged)\b"
    r"[^.]{0,30}\b(?P<word>wrong thing|stupid|awful|daft|silly|dumb|mean|horrible|unkind|rude|"
    r"dreadful|terrible|nasty|hurtful|disrespectful)\b")


# The word has to be the content of what was said, and a word the person says they feel is not
# content: "i shouted at my kids and i feel awful" read "awful" as something said *to* them, so a
# regret about their own shouting was answered "Tell me what was said and we can work out whether
# it is worth taking up with them" - and the repair answer, which is the one the line wants, never
# got the turn. The feeling has to be a clause of its own, so "she told me i was stupid" (reported
# speech, the word is hers) and "my mum said i am lazy and stupid" (the word is still the content
# of what was said) keep their reading; what is dropped is only "... and i feel <word>".
FEELING_CLAUSE = re.compile(
    r"(?:^|[.;!?]|\band|\bbut|\bso|\bbecause|,)\s*(?:i|we)\s+"
    r"(?:(?:just|really|also|still|honestly|actually|then)\s+)?(?:feel|felt)\s+"
    r"(?:so |very |really |quite |pretty |a bit |kind of |like |such )?$")


# Whether it was family decides only the words: "especially from family" is a claim about the
# person, and a boss in a meeting is not that. Nothing else in the reply changes.
SAID_UNKINDLY_REPLIES = (
    "That stings, and it is worse from someone whose opinion you cannot just shrug off. Tell me "
    "what was said and we can work out whether it is worth taking up with them.",
    "Words like that lodge: give it a night before you answer it, and if it is still there "
    "tomorrow, say plainly which bit hurt - people often have no idea.",
    "It is fair to be hurt by that. Say the sentence back to me and we can work out what they "
    "probably meant by it.",
)


SAID_UNKINDLY_FAMILY = (
    "That stings more from family. Tell me what was said and we can work out whether it is "
    "worth taking up with them.",
    "Words like that lodge, especially from family: give it a night before you answer it, and if "
    "it is still there tomorrow, say plainly which bit hurt - people often have no idea.",
    "It is fair to be hurt by that, and harder from someone close. Say the sentence back to me "
    "and we can work out what they probably meant by it.",
)


FAMILY_NAMED = re.compile(
    r"\b(?:mum|mom|mam|mother|dad|father|son|daughter|child|kid|baby|partner|husband|wife|"
    r"sister|brother|nan|nana|gran|granny|grandma|grandad|grandpa|aunt|uncle|cousin|in-laws?|"
    r"family)\b")


def _an_entry_answers_the_deed(clean, memory):
    """True when a card of its own answers this deed, so the turn is that card's.

    "i shouted at them again tonight" has a card naming the deed and the next step, and the
    composer's short repair is a step down from it. Only the deeds that had such a card on main
    are let through (`DEEDS_WITH_A_CARD`): for the rest, what answered the line was written for
    the person it happened to, which is the whole reason the composer took the turn.
    """
    if deed_of(clean) not in DEEDS_WITH_A_CARD:
        return False
    read = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(read, dict):
        return False
    try:
        return lookup.find(read) is not None
    except Exception:  # noqa: BLE001 - a lookup that raises is not a reason to lose the turn
        return False


def _said_wrong(clean):
    # A deed of their own that was not a sentence - a birthday let pass, a promise broken, money
    # not told about - is the same turn: the person named is who it was done to, and what is
    # wanted is what to do now rather than a card about them (bot/compose/repair.py).
    if owns_the_deed(clean):
        return True
    if not SAID_WRONG.search(clean) or SAID_WRONG_NOT.search(clean):
        return False
    # A repair needs somebody still there to have it: the outcome is already settled
    # ("didnt get the job"), there was never a person on the other end ("to my dog"), or the
    # person was being told something rather than hurt by it ("to my doctor about my symptoms"
    # is a briefing that went wrong). Those keep whatever answer main gave them.
    return not (SAID_WRONG_LOST.search(clean) or SAID_WRONG_TO_AN_ANIMAL.search(clean)
                or SAID_WRONG_TO_A_PROFESSIONAL.search(clean))


# The subject of the sentence decides which way round it is: "my boss said something horrible
# in the meeting" is something said to them, and "i told her her cooking was awful" is something
# they said. The speaker's own deed is never the sympathy line.
# "i keep saying the wrong thing" is the speaker's own deed as much as "i said the wrong thing"
# is, and without the words in between it was read as something said to them.
I_SAID = re.compile(
    r"\bi (?:(?:keep|keeps|always|still|just|also|then|really|often|usually|sometimes|"
    r"constantly|forever|never)\s+){0,2}(?:said|say|saying|told|tell|telling|admit|admitted)\b")


CLAUSE_BOUNDARY = re.compile(r"[.;!?,]|\band\b|\bbut\b|\bso\b|\bbecause\b|\bthen\b|\bwhich\b")


def _own_deed(clean, start):
    """True when the speech verb at `start` has the person themself as its speaker."""
    opening = clean[max((b.end() for b in CLAUSE_BOUNDARY.finditer(clean[:start])), default=0):start]
    return bool(FIRST_PERSON_DEED.match(opening) or not opening.strip())


FIRST_PERSON_DEED = re.compile(r"^\s*(?:and\s+|but\s+|so\s+|then\s+|because\s+)?(?:i|we)\b")


def _said_unkindly(clean):
    if _said_wrong(clean) or I_SAID.search(clean):
        return False
    for matched in SAID_UNKINDLY.finditer(clean):
        # A word in the person's own feeling clause, about a deed of their own, is a state and not
        # something said to them: "... i shouted at my kids and i feel awful". A harsh word
        # somebody else said keeps its reading even when the person adds how they feel about it.
        if FEELING_CLAUSE.search(clean[:matched.start("word")]) \
                and _own_deed(clean, matched.start()):
            continue
        return True
    return False


def _a_part_of_the_answer_they_have(clean, memory):
    """The sentence of the answer already on the screen that answers this ask, or None.

    A follow-up that asks for a part of what they were just told - "how much do they cost" after
    the driving answer had already said "Lessons run 25 to 40 pounds an hour" - names no entry of
    its own, so the carry led back to the entry that had answered and the line got the search
    hedge with the answer two lines up. `bot/memory/narrow.py` reads the property the line asks
    for (money, time, heat, amount, distance, order) off a paragraph, and it returns None rather
    than guess, so a line whose part cannot be found safely is left to the fallback as before.
    """
    last = ""
    previous = ""
    for turn in reversed(memory.get("turns") or ()):
        if isinstance(turn, dict):
            if not last and turn.get("bot"):
                last = str(turn["bot"])
            if turn.get("user"):
                previous = " ".join(str(turn["user"]).lower().split())
                break
    if not last.strip():
        return None
    # The same question asked a second time is not a follow-up: the answer they want has already
    # been given, and a figure out of the same paragraph is the neighbouring fact the bare-ask
    # tests refuse ("how many lessons will i need" again is not a question about the price). A
    # plain repeat is the composer's to settle.
    asked = " ".join(str(clean or "").lower().split())
    if asked and previous and (asked == previous or asked in previous):
        return None
    # A why line is not a part of the answer they already have: the part it asks for is the cause,
    # and a card keeps the cause in a sentence of its own at the end ("... The reason is moist air
    # getting in every time the door opens."). Narrowed like a figure ask, "why does it do that"
    # was handed the opening of the card - the steps, not the reason - with the one sentence that
    # answers it left behind. `bot/compose/why` reads what a cause sentence is and this is that
    # same reading, so a why line is answered out of the answer on the screen.
    cause = _same_again.the_cause_said_again(last, memory)
    if cause:
        return cause
    # A line that asks for a period ("how much sugar should i have a day") is not asking for the
    # single serving the answer already gave ("a can ... has 35g"): the answer never says what a
    # day is, so a part of it is not that answer.
    from ..memory.narrow import NO_SET_TIME, narrow
    from ..memory.topics import _the_rates_in
    asked_rates = _the_rates_in(clean)
    if asked_rates and not (asked_rates & _the_rates_in(last)):
        return None
    try:
        part = narrow(last, clean)
    except Exception:  # noqa: BLE001 - a part that cannot be cut leaves the line as it was
        return None
    if not isinstance(part, str) or not part.strip():
        return None
    # The whole answer handed back is the answer said twice, which is not an answer to a line that
    # asked for one of its parts.
    if " ".join(part.lower().split()) == " ".join(last.lower().split()):
        return None
    # A part with no figure in it is a fragment of the answer rather than the thing asked for.
    # The one exception is narrow's own "no set time" line: it is a complete answer to a length
    # ask, and it often says the time in words ("half an hour before bed") rather than digits.
    if not re.search(r"\d", part) and not part.startswith(NO_SET_TIME):
        return None
    # The rate is part of the figure. A cut that drops "a year" turns a running cost into a
    # price: "and how much does one cost" after a dog's "budget about £1,500 to £2,000 a year"
    # was handed "£1,500 to £2,000.", which is the yearly cost of keeping a dog and not what one
    # costs. If the answer's rate is not in the part, the part is not safe to hand back. A
    # rate the part keeps ("25 to 40 pounds an hour") is the answer and stays.
    last_rates = _the_rates_in(last)
    if last_rates and not (_the_rates_in(part) & last_rates):
        return None
    return part.strip()


def _the_newest_line_started_the_topic(memory):
    """True when the last line said is the one the newest topic began on.

    A topic record remembers the turn it started on (`memory["topics"][-1]["turn"]`, and the
    list holds the topic the last line touched last), so a follow-up that adds to a topic begun
    earlier carries it without starting one: "should i talk to the school" is the school-start
    topic still, six turns after it was said. Nothing about the words tells those apart - a
    follow-up names as much as any line - so the record is what says it.
    """
    records = memory.get("topics")
    turns = memory.get("turns")
    if not isinstance(records, list) or not records or not isinstance(turns, list):
        return False
    record = records[-1]
    if not isinstance(record, dict):
        return False
    return record.get("turn") == len(turns) - 1


# The sentence of an answer already given that says whether the thing is safe, or what to do
# about it: "is it safe to drive" after "my exhaust is blowing" is answered by "It is not an
# emergency, but fumes can get into the cabin, so keep a window open". The card holds the verdict
# and `narrow` does not read it, because a verdict is not a figure - so the sentence is found by
# the words a verdict uses.
A_VERDICT = re.compile(
    r"\b(?:not an emergency|no emergency|safe to|unsafe|dangerous|harmless|"
    r"(?:fine|ok|okay|all right|alright) (?:to|for|if|on|with)|"
    r"nothing to worry about|no need to worry|don't worry|"
    r"will not (?:hurt|harm|damage)|won't (?:hurt|harm|damage)|"
    r"avoid |stop (?:using|driving|running|eating|taking)|turn (?:it|that) off|"
    r"get (?:it|that|them) (?:looked at|checked|seen)|"
    r"call (?:a|the|your|an|999|111)\b)", re.I)


# Words that are in every line and name nothing: the description of a thing cannot be found by
# one of these being shared with the line before it.
A_VERDICT_FILLER = frozenset((
    "about", "after", "again", "been", "before", "being", "does", "doing", "have", "just",
    "like", "much", "only", "really", "should", "still", "than", "that", "their", "them",
    "then", "there", "these", "they", "thing", "this", "those", "want", "what", "when",
    "where", "which", "while", "will", "with", "would", "your", "from", "into", "cant",
    "don't", "dont", "isn't", "it's", "thats", "whats", "keep", "keeps", "good", "well",
    "make", "made", "know", "think", "sure", "nothing", "something", "anything", "little",
    "scary", "things", "other", "else", "another", "least", "much", "many", "more", "most",
))


# A sentence that tells the person to do something, rather than saying what the thing is.
A_DOES_SOMETHING = re.compile(
    r"^\W*(?:pull|wipe|stand|puff|put|keep|use|try|fill|check|clean|open|leave|run|fit|ring|"
    r"call|ask|take|turn|stop|brush|paint|replace|screw|tighten|blot|sprinkle|switch|set|apply|"
    r"cover|wrap|store|throw|bin|soak|rinse|dry|add|mix|stir|heat|cook|bake|boil|ventilate|"
    r"measure|test|look|buy|get|go|hold|sit|wait|drink|eat|sleep|walk|book|insulate|seal|"
    r"scrape|sand|prime|swap|change|drop|pour|lift|hang|tie|lock|close|shake|dust|run|"
    r"do|don't|don|never|always|say|tell|ask|write|sign|send|give|make|find|learn|start|begin|"
    r"decide|choose|pick|plan|arrange|avoid|refuse|accept|agree|join|save|budget)\b", re.I)


# A sentence that says what the thing usually is, or whether it matters: the description of a
# state rather than the fix for it.
A_STATE_WORD = re.compile(
    r"\b(?:usually|normally|often|rarely|seldom|is not|isn't|are not|aren't|never|fine|"
    r"harmless|ordinary|common|uncommon|safe|unsafe|risk|problem|matters?|worr(?:y|ies|ying)|"
    r"ok|okay|worth|needs?|means?|sign of|a sign|because|due to|caused by|comes from)\b",
    re.I)


# A card telling the person a risk is not there - "it will not chase you", "a wasp will not sting
# unless it is trapped" - which is what a "will it sting me" asks for, long before the first aid.
A_REASSURES = re.compile(
    r"\b(?:won'?t|will not|doesn'?t|does not|don'?t|do not|shall not|need not|"
    r"not going to)\s+(?:\w+\s+){0,3}?"
    r"(?:hurt|harm|damage|sting|bite|chase|bother|attack|spread|kill|poison|burn|"
    r"catch|come back|come to any harm)\b"
    r"|\bnothing to (?:fear|worry about|be afraid of)\b|\bno need to\b", re.I)


# A second thing named beside the one on the table: the noun after a preposition carries an
# article, which is what tells it from the predicate of a yes/no ("is it a puncture").
A_NEW_CONDITION = re.compile(
    r"\b(?:with|without|on|onto|after|before|during|in|at|from|into|under|beside|instead of|"
    r"for|as)\s+"
    r"(?:a|an|the|my|your|his|her|their|our|this|that|these|those)\s+[a-z]", re.I)


# A line asking whether a thing is somewhere - on a service, in a shop, at a place - which is a
# question about the place and not about the thing itself.
A_ASKS_WHERE = re.compile(
    r"^\W*(?:is|are|was|were|will|would|can|could|do|does|did)\s+"
    r"(?:it|that|this|they|those|these|there)\s+(?:on|in|at|from|near)\b", re.I)


# The closing line of a card: when to get help. It answers "should i go to hospital", not whether
# the thing on the table is safe or what to do about it.
A_WHEN_TO_GET_HELP = re.compile(
    r"\b(?:see (?:a|your|the|an) (?:gp|doctor|nurse|pharmacist|dentist)|call (?:999|111)\b|"
    r"a&e|accident and emergency|get (?:it|that|them) (?:looked at|checked|seen)|"
    r"go to (?:hospital|the hospital)|ring (?:999|111)|same day|straight away)\b", re.I)


# A price, however it is asked: "is that expensive", "is it worth it", "should i pay it".
ASKS_A_PRICE = re.compile(
    r"\b(?:expensive|pricey|costly|cheap|cheaper|afford|costs?|prices?|pay|paid|worth)\b", re.I)


# The bot saying it has already answered: no sentence of a line like that is new.
A_REPEAT_FRAME = re.compile(
    r"\b(?:in what i said above|same answer|same as before|no more than that"
    r"|already (?:said|told)|that is everything i have)\b", re.I)


# A question about the state of the thing in hand: "is it blocked", "is it dying", "is that normal".
A_STATE_ASK = re.compile(
    r"^\W*(?:is|are|was|were|does|do|did|will|can|could)\s+"
    r"(?:it|that|this|they|those|these|the|my|a|an)\b", re.I)


# A figure asked for, which is `narrow`'s to read and never a verdict.
ASKS_A_FIGURE = re.compile(
    r"\bhow (?:much|many|long|far|big|often|high|deep|hot|old)\b|\bwhat (?:time|temp|"
    r"temperature|price|size|date|year|gas mark|colour|color)\b|\bwhich (?:year|date)\b|\bwhen\b",
    re.I)


def _a_topic_still_in_this_exchange(topic, memory):
    """True when the topic was set in the last few lines, so the chat is still in it.

    A reply that is the newest topic's answer word for word can be walked past into the topic
    before it, but only into one the person is still in. "my son is starting secondary school" /
    ... / "hes quite anxious anyway" / "should i talk to the school" / "when should i do that" is
    one exchange and the answer the ask wants is the anxious line's. A subject left several
    turns ago is not brought back that way: "my passport runs out in june" / "were going to
    spain in august" / ... / "what does that cost" got the Spain card on a passport question
    when the walk was allowed to go that far back.
    """
    records = memory.get("topics") if isinstance(memory, dict) else None
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(records, list) or not isinstance(turns, list):
        return False
    for record in reversed(records):
        if not isinstance(record, dict):
            continue
        if " ".join(str(record.get("text") or "").lower().split()) != topic:
            continue
        began = record.get("turn")
        if not isinstance(began, int):
            return False
        return len(turns) - began <= 3
    return False


# A line about ending it, or about being at the end of what they can take. This is only ever a
# veto - nothing is answered from these words - so it is deliberately broad on the saying and
# never on a single common word: "no point" is here only with what it is no point in.
DISTRESS = re.compile(
    r"\b(?:had\s+enough\s+of\s+(?:living|life|it\s+all|everything|being\s+here)|"
    r"enough\s+of\s+living|end\s+it\s+all|end\s+my\s+life|kill\s+myself|killing\s+myself|"
    r"not\s+worth\s+living|worth\s+living|want\s+to\s+die|wanna\s+die|"
    r"no\s+reason\s+to\s+(?:live|go\s+on|carry\s+on)|nothing\s+to\s+live\s+for|"
    r"no\s+point\s+in\s+(?:anything|going\s+on|carrying\s+on|living)|"
    r"no\s+point\s+(?:going\s+on|carrying\s+on|living)|"
    r"better\s+off\s+dead|better\s+off\s+without\s+me|tired\s+of\s+living|"
    r"can'?t\s+go\s+on|don'?t\s+want\s+to\s+be\s+here|dont\s+want\s+to\s+be\s+here|"
    r"hurt\s+myself|self[\s-]?harm|suicid\w*|take\s+my\s+own\s+life|"
    r"don'?t\s+want\s+to\s+wake\s+up|dont\s+want\s+to\s+wake\s+up)\b", re.I)


def _reads_as_distress(line):
    """Whether a line is about ending it, or about being at the end of what they can take."""
    return bool(DISTRESS.search(" " + " ".join(str(line or "").lower().split()) + " "))
