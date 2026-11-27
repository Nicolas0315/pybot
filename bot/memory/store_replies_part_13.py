"""Part 13 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..memory import current, note, recent, remember_other, thread
from ..memory import cause as a_reason
from ..memory import choice as choose
from ..memory import facts as extract
from ..memory import counts as how_many
from ..memory import rates as rates_reader
from ..memory.times import answer as _the_time_they_said
from ..memory import carry as about_the_choice
from ..memory import repair as a_repair
from ..memory import whathurts as a_hurting_part
from ..memory.when import asks_what_today_is
from ..memory.store_lines import (
    HELD_THREAD, GRIEF_WORDS, CLOSE_PLAIN, CLOSE_HEAVY, CHANGE_PLAIN, CHANGE_HEAVY,
    CHECK_NOTHING_SAID, CHECK_A_FEELING, CHECK_A_QUESTION, CHECK_PLAIN,
)
from ..memory.relations import _a_pet_age, _folded, _pet_named, _same_as_last
from ..modules.memory_tables import ELIDED_NOT_SURE
from .store_replies_part_01 import (
    _bare, _the_figure_for_the_size_they_named, _the_limit_they_share,
)
from .store_replies_part_02 import (
    _bare_ask_naming_a_fact, _elided_ask, _remember_asked, _said_another_way, _slot_of, _slot_words,
    _the_bot_name, _the_case_they_just_gave, A_PERSON_IN_TROUBLE, FEELING_ALONE, TREATMENT,
    _is_a_question,
)
from .store_replies_part_04 import (
    _detail_they_left_out,
)
from .store_replies_part_05 import (
    _behind_a_remembering_frame, _the_amount_they_made, _the_part_it_never_said,
    _the_people_that_size_feeds,
)
from .store_replies_part_06 import (
    _other_person_reply, _the_person_still_in_hand, _the_same_fact_about_someone,
)
from .store_replies_part_07 import (
    _a_feeling_about_what_they_said, _remembers_fact,
)
from .store_replies_part_08 import (
    _pet_part_reply,
)
from .store_replies_part_10 import (
    _the_budget_on_the_answer, _the_call_from_the_advice,
)
from .store_replies_part_11 import (
    _the_names_again,
)
from .store_replies_part_12 import (
    _respond, _the_fact_just_asked, INTENSIFIER, CLOSE_SUBJECT,
)


def _the_store_reply(text, memory):
    """A recall ask answered about the fact it means, even with the fact left out.

    "what did I call him?" right after "we have a dog called Biscuit" is about the dog, so the
    ask is turned into the plain one the store already answers for that fact. The fact is taken
    from the one the last thing they said gave, or else from the last recall question; the
    second is a guess, and a guess that misses returns None rather than claim they never said
    something they did.
    """
    if asks_what_today_is(text):
        # "what day is it" asks the calendar, and the store has no part of it: the chat it is said
        # in is not the subject. Without this the ask was filled from the thread - the plan on it
        # ("i'm starting my new job on monday") stood in for the value, and its implied question
        # answered a question about today with the dress code for a first day.
        return None
    behind = _behind_a_remembering_frame(text)
    if behind:
        # A remembering frame is not the line: "can you remember the dentist is on tuesday" is a
        # person handing over the appointment. The store answers the thing behind it, and the
        # frame's own yes-only question ("do you remember that i live in leeds") is answered by
        # _remembers_fact first, which is the one reader that needs the frame in front of it.
        remembered = _remembers_fact(text, memory)
        if remembered:
            return remembered
        answered = _the_store_reply(behind, memory)
        if answered:
            return answered
    followed = _the_followed_check(text, memory)
    if followed:
        # "did you get that?" is a question about the conversation, not about the world: the
        # answer is the thing they said, said back, and never a lookup of the last word in it.
        return followed
    closed = _the_close(text, memory)
    if closed:
        # "i just want to forget it" is not the subject asked about again: it is the person
        # closing it, and the answer is short and warm. Read before anything else, because every
        # reader below would answer the subject they have just been asked to leave.
        return closed
    shared = _the_limit_they_share(text, memory)
    if shared:
        # The limit the turn before stated is this person's as well ("im too", "my son is too"):
        # the reading has filed it on them, and the answer says which limit and whose it is, so
        # the person is not left with "Glad to hear it." after telling the bot about an allergy.
        return shared
    # "i had an interview today" / "how did it go" is a question about the person's own day, and
    # the answer is to ask them: the bot was not there. Read before the knowledge reads, because
    # the topic of the line is the thing they just did - "how did it go" after the interview was
    # answered with how to prepare for one, a line after they said it was over
    # (bot/memory/thread.went).
    how_it_went = thread.went(text, memory)
    if how_it_went:
        return how_it_went
    timed = _the_time_they_said(text, memory)
    if timed:
        # "what time do i get up" is about the time they told us, not about sleep in general.
        return timed
    took = memory.pop("pet_age", None) if isinstance(memory, dict) else None
    if isinstance(took, dict) and isinstance(took.get("age"), int):
        # The bot asked how old their animal was and this line was the answer: say it back.
        return "Noted: " + _pet_named(took) + " is " + _a_pet_age(took) + "."
    call = _the_call_from_the_advice(text, memory)
    if call:
        # "should i keep running?" after an answer that said how to go on with a change: the
        # chat has already settled it, so the store answers with that answer's own limit.
        return call
    given = extract.bot_name(text)
    if given:
        # A name for the bot is theirs to give, and the store keeps it (facts.bot_name files it as
        # `bot_name`), so the next "whats your name" agrees with this line instead of saying it has
        # no name at all. The confirmation is the turn's news; nothing else in the line to answer.
        return pick([given + " it is \u2014 I'll answer to that.",
                     given + " \u2014 noted, I'll answer to it.",
                     "I'll be " + given + " then."], memory)
    settled = choose.the_decision(text, memory)
    if settled:
        # "what did i decide to get" names nothing, so nothing could answer it: the thing is in
        # the line where they changed their mind ("im thinking of getting a cat" / "actually a
        # dog"), and the store is the only part of the bot that keeps that line.
        return settled
    budget = _the_budget_on_the_answer(text, memory)
    if budget:
        # "and i only get 20 minutes" after a lunch answer is the room that answer has, not a new
        # question about 20 minutes. Left to itself the knowledge base answered it as one and the
        # subject left the lunch: the eggs came back as the fastest dinner there is.
        return budget
    made = _the_amount_they_made(text, memory)
    if made:
        # "i only made 200g" after an answer that worked a total out for four: the person is saying
        # they are short, and "5 minutes" was the answers module reading the weight as a question
        # about how long to cook it.
        return made
    fed = _the_people_that_size_feeds(text, memory)
    if fed:
        # "is that enough for 6" while holding the joint: the portion the cooking know-how keeps
        # turns the size in hand into a number of people, which is the question. Left to itself
        # the turn was the same roast paragraph again behind "Same as before".
        return fed
    sized = _the_figure_for_the_size_they_named(text, memory)
    if sized:
        # "how long do i roast a chicken" then "its 2kg" is the size the answer was waiting for:
        # the roast entry works its rate out for the size in the line, and the answer already did
        # the arithmetic for exactly this size ("so a 2kg bird takes roughly 1 hour 40 minutes").
        # The store said "Thanks for telling me - I'm here if you want to dig into any of that",
        # which is an acknowledgement of the one thing in the chat that has a figure in it.
        return sized
    folded = _folded(text, memory)
    low = _bare(folded)
    undeclared = _the_person_still_in_hand(low, memory)
    if undeclared:
        # "can he have cheese" then "what about milk": one more food asked about the same person,
        # with the person left out. The chat has just answered that ask, so the person in hand is
        # the one the question is about - and with no person named, the knowledge entry for milk
        # answered it with the baby feeding schedule.
        one_more = _other_person_reply(memory, low)
        if one_more:
            return one_more
    named_back = _the_bot_name(memory, low)
    if named_back:
        return named_back
    names = _the_names_again(folded, low, memory)
    if names:
        # "what are they called again?" names the pets the store is holding, so the names it kept
        # are the answer.
        return names
    counted = how_many.answer(low, memory)
    if counted:
        # "how many brothers do i have" a turn after "i have three brothers": the number is the
        # answer, and the store holds it. Animals and children are answered by the readers below.
        return counted
    same = _the_same_fact_about_someone(text, memory)
    if same:
        # "and my wife is too" after "im allergic to nuts": the fact comes with them, and it is
        # kept on the person named here because this module is the one answering.
        said, note = same
        if note:
            remember_other(memory, dict(note))
        return said
    # "im scared" right after they told us something coming up is about that thing, so it is
    # said back and answered, not handed a line that would fit any frightening thing.
    about_it = _a_feeling_about_what_they_said(memory, low)
    if about_it:
        return about_it
    kept = _the_fact_just_asked(memory, low)
    if kept:
        # "do you remember it?" right after a recall answer is a question about that fact, not
        # about the bot's memory in general: "whats my name" -> "You're Dave." -> "do you
        # remember it?" is answered by the name, not by "I keep what you tell me here".
        return kept
    slot, guessed = _elided_ask(text, memory, low)
    if slot:
        reply = _respond(_slot_words(slot, memory), memory)
        if not reply or (guessed and ELIDED_NOT_SURE.search(reply)):
            # The fact the guess picked has nothing to say: fall through to the echo below
            # ("You said: \"weve got 2 cats\"") rather than lose the turn to a hedge.
            reply = _respond(text, memory)
            if reply:
                _remember_asked(memory, _slot_of(low))
            return reply
        if _same_as_last(reply, memory):
            # the same sentence twice in a row reads like a machine: say the fact another way.
            return _said_another_way(reply) or reply
        return reply
    taken = _the_case_they_just_gave(text, memory)
    if taken:
        return taken
    named = _bare_ask_naming_a_fact(low, memory)
    if named:
        # "and my job?" names the fact rather than asking for it, so the answer is the same one
        # the plain ask gets. When that answer is a miss there is nothing to say: the line goes
        # to another module rather than to a denial.
        reply = _respond(_slot_words(named, memory), memory)
        if reply and not ELIDED_NOT_SURE.search(reply):
            _remember_asked(memory, named)
            if _same_as_last(reply, memory):
                return _said_another_way(reply) or reply
            return reply
    # "and which knee was it": read before the store's own reply, which answers a line it does
    # not know with the last thing they said ("You said: \"its on the outside of the knee\"").
    part_asked = a_hurting_part.the_part_asked(memory, low)
    if part_asked:
        return part_asked
    reply = _respond(text, memory)
    if not reply:
        # "no i meant the front room" names no fact to move - the thing it swaps is the subject of
        # the ask - so the ask is the one they would have made, and it is answered as the question
        # it is. Only when the store's own correction readers said nothing, so a value is still
        # the store's to put right.
        reply = a_repair.the_thing_they_meant(text, memory)
    if not reply:
        # "but i work long hours" after a question about getting a cat names nothing of its own,
        # so the entries for the cat cannot see it: the choice in hand is carried into the line
        # and asked again, and an answer about something else is refused.
        reply = about_the_choice.the_subject_in_the_condition(text, memory)
    if not reply:
        reply = about_the_choice.the_verdict_in_the_chat(text, memory)
    if not reply:
        # "hows about something cold" after a dessert was offered names no dish, so no entry
        # could reach it: the course the chat is on is carried into the line and the knowledge
        # base is asked the question the person would have made of it.
        reply = about_the_choice.the_quality_in_the_chat(text, memory)
    if not reply:
        # "and no dairy" after a chicken dish takes something out of an answer that never named
        # it, so nothing is left to cut: the dish is carried into the line and the knowledge base
        # is asked again.
        reply = about_the_choice.the_limit_in_the_chat(text, memory)
    if reply:
        _remember_asked(memory, _slot_of(low))
        if _same_as_last(reply, memory):
            # The same sentence twice in a row reads like a machine, whatever the ask was:
            # "how many cats do i have" asked again, or "what pets do i have" and then
            # "how many cats do i have", both land on the same line about the same fact.
            return _said_another_way(reply) or reply
    if not reply:
        # A part of an animal the chat has described is a fact it holds, not a detail the person
        # left out: "hes a labrador, 9 weeks old" then "what breed is he" was asked back, which
        # says the chat was not listening.
        reply = _pet_part_reply(memory, low)
    if not reply:
        # "and which knee was it": the store holds the part and the side it was said with.
        reply = a_hurting_part.the_part_asked(memory, low)
    if not reply:
        # The rate of their own doing, asked back late: "how often was that again" after "i go to
        # the gym twice a week". Read before the detail ask-back, which asks them the question
        # they are asking this store.
        reply = rates_reader.answer(text, memory)
    if not reply:
        reply = _detail_they_left_out(memory, low)
    if not reply:
        # "im knackered" ... "why" ... "the baby": the thing they named is the reason for how
        # they said they were, and the store has plenty to say about a baby and nothing at all
        # about those two words on their own. Read as the sentence it would have been, it is
        # answered - but only after the store's own readers, so a bare thing the store already
        # answers ("the baby" right after "im knackered" is met with a question about it) keeps
        # the line it has.
        reply = a_reason.answer_for(text, memory)
    if not reply:
        reply = _the_part_it_never_said(memory, low)
    return reply


CHANGE_SUBJECT = re.compile(
    r"\b(?:talk|speak|chat) about (?:something|anything) (?:else|different)\b|"
    r"\b(?:change|switch|move) (?:the subject|the topic|to a different|to another|"
    r"onto something else|on to something else)\b|"
    r"\b(?:talk|speak|chat) about another (?:topic|subject|thing)\b|"
    r"\b(?:change|switch) (?:the )?(?:subject|topic)\b|"
    r"\bsomething (?:else|different) (?:for a bit|instead|to talk about)\b")


CARRIES_ON_AFTER = re.compile(
    r"\b(?:it|that|this|all of it|all that)\s+"
    r"(?:(?:in|into|on|onto|for|to|from|with|about|between|among|and|then|when|if|after|before|"
    r"until|till|while|overnight|so|because|as)\b"
    # "at" carries on ("drop it at the door") except in "at all", which is the closing itself:
    # "i dont want to talk about it at all" was answered with an open-question card.
    r"|at\b(?!\s+all\b))")


ASKS_WHETHER_TO = re.compile(r"\b(?:should|shall|can|could|would|do|does|did)\s+i\b|\bi should\b")


ASKS_FOR_HELP = re.compile(r"\b(?:can you help|help me|is it (?:wrong|bad|ok|okay|normal)|"
                           r"what should i|do you think i should|am i wrong)\b")


# The words that say how long a closing holds: "not at all", "at the moment", "for now",
# "right now", "any more". They are part of the closing, not the rest of the sentence, so they are
# taken out before the fence that says the pronoun still has work to do ("leave it for 20
# minutes" keeps its fence because "for 20 minutes" is not one of these).
HOLDS_FOR_NOW = re.compile(
    r"\b(?:at|for)\s+(?:the\s+)?(?:all|moment|minute|time\s+being|now)\b"
    r"|\b(?:right|just)\s+now\b|\bany\s?more\b|\bagain\b|\byet\b")


CLOSE_FILLER = frozenset("""and but so ok okay right then well anyway anyhow also now just
please thanks thank you for a bit moment second though too as if that this at all never mind let
lets we you i me my of on in to the good fine fair enough alright still only really can could
would will shall not oh ah hmm yeah yes no actually wait it its
today tonight now anymore any more again yet later tomorrow moment minute time being""".split())


# The same set without the word for when: what a frame read before the word was allowed.
CLOSE_FILLER_ALWAYS = CLOSE_FILLER - frozenset(
    "today tonight now anymore any more again yet later tomorrow".split())


CHECK_FOLLOWED = re.compile(
    r"^(?:(?:did|do|have|has|were|are)\s+(?:you|u)\s+"
    r"(?:get|got|see|saw|catch|caught|read|hear|heard|note|noted|follow|following"
    r"|have|got|keep|kept|take|taken|remember)"
    r"|(?:you|u)\s+(?:get|got|catch|caught|see|saw|read|hear|heard|follow|following)\b"
    r"|got\s+(?:that|it|this))\s*"
    r"(?:that|it|this|it\s+all|all\s+of\s+that|all\s+of\s+it|all\s+that|everything"
    r"|any\s+of\s+that|any\s+of\s+it|the\s+lot|the\s+whole\s+lot|my\s+message"
    r"|my\s+last\s+message|the\s+message|what\s+i\s+said|what\s+i\s+sent"
    r"|the\s+last\s+bit)?\s*$")


BARE_ACKNOWLEDGEMENT = re.compile(
    r"^(?:(?:so|ok|okay|right|ah|oh|yeah|and|well|great|good|nice|cheers|perfect|loud and clear)"
    r"\s+)*got(?:\s+(?:that|it|this|ya|yas|you))$")


SAID_TO_THE_BOT = re.compile(r"\b(?:you|u|your|yours|urs|yourself)\b")


A_MOOD_LINE = re.compile(
    r"\b(?:sad|sadly|upset|miserable|depressed|low|down|angry|furious|annoyed|gutted|stressed"
    r"|fed up|knackered|exhausted|tired|worn out|lonely|bored|happy|glad|pleased|excited"
    r"|nervous|worried|anxious|scared|frightened|terrified|dreading|overwhelmed|burnt out)\b")


def _reads_as_the_invitation(text, memory):
    """True where the composer reads the line as asking whether the bot saw the thing named.

    Asked of the composer's own reading rather than of a word list, so the store stands down
    exactly where the composer answers and nowhere else. Guarded by `except`, because a reading
    that fails leaves the check in service rather than dropping a line the store did read.
    """
    try:
        from ..compose import fallback
        return bool(fallback.reads_as_if_i_saw(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails leaves the check in service
        return False


SAFETY_MODULES = frozenset(("safety", "urgent"))


def _the_module_behind(memory, said):
    """The module that answered this line, or "" when the turns do not say."""
    low = _plain_line(said)
    for turn in reversed([t for t in (memory.get("turns") or []) if isinstance(t, dict)]):
        if _plain_line(turn.get("user")) == low:
            return str(turn.get("module") or "")
    return ""


def _the_line_before_the_check(memory, line):
    """The last line they said that was not itself a check, or ""."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-6:]
    for turn in reversed(turns):
        said = str(turn.get("user") or "").strip()
        if not said:
            continue
        if CHECK_FOLLOWED.match(_plain_line(said)):
            continue
        if line and _plain_line(said) == line:
            continue
        return said
    return ""


def _a_check_choice(options, memory, salt):
    """Pick from a pool without saying the same line twice in a row."""
    turns = memory.get("turns") or []
    recent = " ".join(str(t.get("bot") or "") for t in turns[-4:] if isinstance(t, dict))
    fresh = [option for option in options if option[:30] not in recent] or list(options)
    return fresh[(len(turns) + salt) % len(fresh)]


def _a_check_came_before(memory, line):
    """True when the last thing they said was itself a check ("did you get that" twice).

    The sentence was read back to the first one, so reading it back again is the machine repeating
    itself. The check being answered now is not counted, whatever the turns hold.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-6:]
    said_before = [_plain_line(str(turn.get("user") or "")) for turn in turns]
    if (said_before and line and said_before[-1] == line
            and not str(turns[-1].get("bot") or "").strip()):
        # The turn being answered is already recorded, with no reply yet: the line before it is the
        # one that counts. A last turn that has a reply is a line already answered, even when it
        # reads the same as this one - two checks in a row are two checks.
        said_before = said_before[:-1]
    for said in reversed(said_before):
        if not said:
            continue
        return bool(CHECK_FOLLOWED.match(said))
    return False


def _the_followed_check(text, memory):
    """The answer to "did you get that?": the thing they said, said back, or an honest no.

    A check is answered from what the store kept, never with a lookup of the last word in it. The
    line above is read back only when it is theirs to read back: a feeling is answered warmly
    without it, and a line with no fact stays out because "you are so sad" is not something a
    friend says.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return None
    as_said = _folded(text, memory)
    low = _plain_line(as_said)
    if _reads_as_the_invitation(low, memory):
        # "did you see it" after they named the match is a conversation about the match, and the
        # composer answers it (bot/compose/fallback.py, `reads_as_if_i_saw`). Reading their own
        # evening back - "Yes — you watched the final together" - is a true sentence and no reply
        # to somebody who wants to tell you what happened in it. The store answers the other
        # checks on the conversation ("did you get that", "did you see my message") unchanged.
        return None
    if not CHECK_FOLLOWED.match(low):
        return None
    if BARE_ACKNOWLEDGEMENT.match(low) and "?" not in str(text):
        # "got it" is a nod: "understood". Answering it by reading their own line back turns a
        # handshake into a receipt.
        return None
    previous = _the_line_before_the_check(memory, low)
    if previous and _the_module_behind(memory, previous) in SAFETY_MODULES:
        # An emergency is not read back. "Yes, that's what I have: your chest hurts and you can not
        # breathe" is weaker at that moment than the nudge to ring 999 that the safety lane wrote,
        # and reading a symptom back reads as filing it. Nothing is claimed, so the safety pool
        # keeps the turn.
        return None
    # The seed carries the turn count as well as the line, so two chats that check the same way
    # do not open with the same sentence.
    salt = len(low) + 3 * len([t for t in (memory.get("turns") or []) if isinstance(t, dict)])
    if previous:
        if (FEELING_ALONE.match(previous.lower().rstrip("!.,"))
                or A_MOOD_LINE.search(previous.lower())
                or A_PERSON_IN_TROUBLE.search(previous)
                or TREATMENT.search(previous)
                or any(word in previous.lower() for word in GRIEF_WORDS)):
            return _a_check_choice(CHECK_A_FEELING, memory, salt)
        if _is_a_question(previous):
            return _a_check_choice(CHECK_A_QUESTION, memory, salt)
        if SAID_TO_THE_BOT.search(_plain_line(previous)):
            # The line they want read back was addressed to the bot ("i sent you a message", "i
            # wrote to you"): the check is that it arrived, and read back as a fact it comes out
            # as "Yes - you sent you a message".
            return _a_check_choice(CHECK_A_FEELING, memory, salt)
        said = thread.restate(previous)
        if said and len(said.split()) >= 3:
            # A check is answered with the thing they said, unless this is the second check in a
            # row: then the sentence was read back a moment ago, and saying it again is the
            # machine. Whether the bot's line happens to contain that sentence is not the test -
            # "Your budget is 500, then - I'll stick to that" contains it, and after "did you get
            # that" the budget is exactly what the person wants to hear named again. What matters
            # is whether the read-back has already been given to a check.
            checked_before = _a_check_came_before(memory, low)
            if not checked_before:
                return _a_check_choice(CHECK_PLAIN, memory, salt).format(said=said)
            # The bot said this very sentence a moment ago ("Noted: your sons birthday is in
            # june"), so a check twice in a row must not read it back twice: that is the machine
            # talking. A bot line that merely names part of it ("Moving to Leeds. Exciting") is
            # not the same sentence, and reading the line back is what the person is asking for.
            return _a_check_choice(CHECK_A_FEELING, memory, salt)
        # They did say something, it is just not a thing to say back ("hello"): saying there is
        # no line from them would be false.
        return _a_check_choice(CHECK_A_FEELING, memory, salt)
    record = current(memory)
    kept = str((record or {}).get("text") or "") if isinstance(record, dict) else ""
    if kept and not _is_a_question(kept):
        # With nothing to read back, the subject the chat is on is still true and is what they
        # were asking about: "yes - your boiler is broken" answers the question they asked.
        said = thread.restate(kept)
        if said and len(said.split()) >= 2:
            return _a_check_choice(CHECK_PLAIN, memory, salt).format(said=said)
    return _a_check_choice(CHECK_NOTHING_SAID, memory, salt)


def _plain_line(text):
    """The line in plain lower-case words, with the punctuation taken off.

    The folded form is not used here: the understanding engine puts the referent in place of a
    pronoun, so "i don't want to talk about it" comes back naming the thing they have just asked
    to leave alone.
    """
    low = " ".join(str(text or "").lower().split())
    return " ".join(re.sub(r"[^a-z0-9' ]+", " ", low).split())


# A closing names its subject as often as it says "it": "i dont want to talk about work", "i'd
# rather not talk about him", "i dont want to talk about the row". The frames above spell the
# pronoun out, so a named subject fell through them and an ask about how to make conversation took
# the turn. The subject has to be the end of the line and short, and the words inside it may not be
# the ones that turn a closing into a plan ("i dont want to talk about work BUT i have to, so
# where do i start" is not a closing), so the frame is read here rather than inside CLOSE_SUBJECT.
DECLINE_A_SUBJECT = re.compile(
    r"\bi\s+(?:do\s+not|don'?t|dont)\s+(?:" + INTENSIFIER + r"\s+)?"
    r"(?:want|wanna|need)\s+(?:" + INTENSIFIER + r"\s+)?to\s+"
    r"(?:talk|speak|think|hear)\s+about\s+(?P<subject>.+)$|"
    r"\bi(?:'?d|\s+would)\s+(?:" + INTENSIFIER + r"\s+)?rather\s+not\s+"
    r"(?:talk|speak)\s+about\s+(?P<rather>.+)$|"
    r"\b(?:let'?s|lets|can\s+we|could\s+we)\s+not\s+(?:talk|speak)\s+about\s+"
    r"(?P<let>.+)$")


# The words that turn the subject into the rest of a sentence: a plan, a reason or a second ask.
NOT_A_SUBJECT = frozenset("""but and so because cos with without to about for then if when while
    though although or yet also plus as since unless until before after once""".split())


def _a_subject_to_leave_alone(low):
    """True when the line is a closing that names its subject rather than saying "it"."""
    for found in DECLINE_A_SUBJECT.finditer(low):
        subject = (found.group("subject") or found.group("rather")
                   or found.group("let") or "").strip()
        words = subject.split()
        if not words or len(words) > 4:
            continue
        if len(words) > 1 and words[0] in ("it", "that", "this"):
            # "can we not talk about it today" is the pronoun frame with a word after it, and the
            # frame above decides that one: a heavy subject answered by the grief reader with an
            # offer of something ordinary is better than this line, so it is not taken here.
            continue
        if any(word in NOT_A_SUBJECT for word in words):
            continue
        # What is left in front of the frame is filler or nothing, exactly as in the frames above:
        # "i told you already, i dont want to talk about work" opens with a claim about the chat,
        # and that line is bot/memory/told.py's to answer - it knows what to do with the claim.
        before = low[:found.start()].split()
        if not all(word in CLOSE_FILLER for word in before):
            continue
        return True
    return False


def _closes_the_subject(text):
    """True when the whole line asks to leave the thing in the air alone."""
    low = _plain_line(text)
    if not low or len(low.split()) > 12:
        return False
    if re.match(r"(?:what|how|why|when|where|who|which)\b", low):
        # "how do i forget it" is an ask about the thing, not a request to leave it: only a line
        # whose whole content is the closing is taken. "can we talk about something else" passes,
        # because the close or the change of subject has to match for anything to be claimed.
        return False
    if ASKS_WHETHER_TO.search(low) or ASKS_FOR_HELP.search(low):
        return False
    if CARRIES_ON_AFTER.search(HOLDS_FOR_NOW.sub(" ", low)):
        # "drop it in the pan" and "i want to leave it in the oven for 20 minutes" are about the
        # thing, not about leaving it alone: the pronoun has work to do in the rest of the line.
        return False
    if _closes_by_a_frame(low):
        return True
    return _a_subject_to_leave_alone(low)


def _closes_by_a_frame(low):
    """True when one of the frames above covers the line and nothing else in it carries on."""
    for pattern in (CLOSE_SUBJECT, CHANGE_SUBJECT):
        for found in pattern.finditer(low):
            rest = (low[:found.start()] + " " + low[found.end():]).split()
            if all(word in CLOSE_FILLER for word in rest):
                return True
    return False


def _a_plain_frame_closes(low):
    """True when the frames read the line with no help from this reader's newer allowances."""
    for pattern in (CLOSE_SUBJECT, CHANGE_SUBJECT):
        for found in pattern.finditer(low):
            if re.search(INTENSIFIER, found.group(0)):
                continue
            rest = (low[:found.start()] + " " + low[found.end():]).split()
            if all(word in CLOSE_FILLER_ALWAYS for word in rest):
                return True
    return False


def _held_thread(memory):
    """True when a safety answer, rather than a topic, is the thing the chat is carrying."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-3:]
    for turn in turns:
        if turn.get("module") == "safety":
            return True
        said = str(turn.get("bot") or "").lower()
        if any(word in said for word in HELD_THREAD):
            return True
    return False


def _gentle_subject(memory):
    """True when what was closed is heavy: a loss, an illness, a stay in hospital."""
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-4:]
    for turn in turns:
        if turn.get("module") in ("loss", "grief"):
            return True
        if any(word in str(turn.get("bot") or "").lower() for word in GRIEF_WORDS):
            return True
        if any(word in str(turn.get("user") or "").lower() for word in GRIEF_WORDS):
            return True
    return False


def _can_close(text, memory):
    """Whether the store is the one to answer this closing line.

    Only inside a chat with something in the air (there is nothing to close otherwise) and never
    over a thread the safety module is holding.
    """
    if not _closes_the_subject(text):
        return False
    if not current(memory) and not recent(memory, 2):
        return False
    if _held_thread(memory):
        return False
    if _gentle_subject(memory) and not _a_plain_frame_closes(_plain_line(text)):
        # A loss or a stay in hospital is answered better by the grief reader, which offers
        # something ordinary to talk about instead ("tell me about something ordinary instead if
        # that's easier today"). A closing the plain frames already read stays with it; the ones
        # this reader newly recognises - the word in the middle, the named subject, the word for
        # when - are the store's only on an ordinary subject.
        return False
    return True


def _the_close(text, memory):
    """The answer to a person who has asked to leave the subject: a short yes, and no advice."""
    if not isinstance(text, str) or not isinstance(memory, dict):
        return None
    if not _can_close(text, memory):
        return None
    low = _plain_line(text)
    gentle = _gentle_subject(memory)
    if CHANGE_SUBJECT.search(low):
        return pick(CHANGE_HEAVY if gentle else CHANGE_PLAIN, memory, low)
    return pick(CLOSE_HEAVY if gentle else CLOSE_PLAIN, memory, low)
