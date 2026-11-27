"""Part 10 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..compose import ruledout
from ..memory import (
    content, current, keywords, last_bot, last_module, last_user, others, recent, stem, thread,
    user, you,
)
from ..memory import condition
from ..memory import spent
from ..memory import guest
from ..memory.taste import read_all as read_tastes
from ..memory import facts as extract
from ..memory import history
from ..memory import named as named_thing
from ..memory import recall
from ..memory import reminded
from ..memory.store_lines import (
    NOT_THE_PLAN, NOT_ON_A_MEDIUM, QUOTE_LEADS, ASKED_LEADS, RESTRICT_OPENS, CALL_LEADS, LENGTH,
    WORD_NUMBERS, UNIT_SECONDS, BUDGET_FITS, BUDGET_MORE, BUDGET_TIGHT, ANY_FIGURE,
)
from ..memory.relations import (
    ABOUT_PERSON_ASK, _called, _continues_an_about_ask, _every_line, _folded, _named_person,
    _person_from_pronoun,
)
from ..modules.memory_tables import (
    ASK_WITHOUT_MY, MEMORY_POINTER, PLAN_MINE, SAID_ASK, TOPIC_ASK, WHAT_I_SAID,
)
from bot.memory.corrected import _asks
from .store_replies_part_01 import (
    ACTIVITY_ASK, ASKED_ALL, FIRST_ASK, MORE_OF_IT, _a_count_ask, _a_length_i_have, _bare,
    OTHER_ASK, REMINDER_MID, ABOUT_A_NAME, ABOUT_PERSON_MORE, REPEAT_ASK, REPEAT_START, REPEAT_TAIL,
    REPEAT_WORDS, WHOLE_ASK, LAST_LINE_ASK,
)
from .store_replies_part_02 import (
    PLACES_ASK, THE_CHAT_ASK, THING_AGAIN, _about_the_bot_here, _an_attribute_they_gave,
    _job_just_said, _said_word, _summary_ask, _which_thing_was_it, SELF_DO_AGAIN, _job_words_seen,
    ATTRIBUTE_KIND, NOT_A_KIND,
)
from .store_replies_part_03 import (
    _dislikes_here, _last_answer, _one_half_of_the_dish, _lines_a_person_moved, _and_list,
)
from .store_replies_part_04 import (
    DISLIKE_ASK, A_PROGRAMME_IS_ON, _a_relation_in, TELLING_ALREADY, _covers,
    _date_written_as_a_date, _named_back, _pronoun_person, _said_everything, _the_person_called,
    _tokens, ANSWER_MODULES,
)
from .store_replies_part_06 import (
    _diet_sentence, _the_ask_beats_the_receipt, _a_name_in_a_pronoun_line, _only_a_pointer,
    _person_clauses,
)
from .store_replies_part_07 import (
    _about_the_children_reply, _vary,
)
from .store_replies_part_08 import (
    _alike, _seen, _only_the_name, _the_name_pattern, _the_same_person, _a_line_about, _only_a_nod,
    _turn_lines, _worth_reporting,
)
from .store_replies_part_09 import (
    HALF_AN_HOUR, LENGTH_FILLER, TIME_LENGTH, _sentences, _halves, LEAD_LABEL, A_HORIZON, BUDGET,
    CLAUSE_SPLIT, STOP_CONDITION, CALL_ASK, CARRY_ON, SEE_SOMEONE, STOP_IT,
)


def _about_this_chat(text, memory=None):
    """Lines that ask about the conversation itself, not about the world."""
    if _about_the_bot_here(memory):
        return False
    if history.asked(text):
        return True
    # A recall ask with nothing named in it ("anything you've learned about me", "what have you
    # picked up about me") is the whole picture asked for in other words. The reader that decides
    # so is the one the store answers with, so the gate and the answers agree: without this the
    # line was neither answered nor skipped, and the next "what did i tell you" quoted it back.
    if recall.ask(text) == "me":
        return True
    # "what was wrong with my boiler again" is a reminder about the boiler, and the store owns
    # it: read as a question about the world it was a fault to diagnose, so the answers lane
    # handed back its flow-temperature card a turn after the person told us about the boiler.
    if reminded.about_a_thing_they_said(text, memory):
        return True
    folded = _folded(text, memory)
    low = MORE_OF_IT.sub(r"\1", _bare(folded))
    # "how many cats", "how many have i got": a count of their own animals is a fact they told
    # the store, not a question about the world. Only a line that ends at the number counts -
    # "how many cats are there in the world" is still a question about the world.
    if _a_count_ask(low) is not None:
        return True
    # The length of a pregnancy the chat was told is the same kind of ask: "how far along is my
    # wife" and "how many weeks am i" are questions about what they said, and the store has the
    # number. The dating card answered them with how a due date is worked out while the store
    # held eight weeks, so the shape is published here as the chat's own business.
    if memory is not None and _a_length_i_have(memory, low):
        return True
    checks = (
        r"\b(?:what|which)\b.*\bmy name\b|\bwho am i\b|\b(?:know|remember) my name\b|"
        r"\bwhat did (?:i|u|you) (?:say|tell me) my name was\b|^my name$|\bwhat my name (?:is|was)\b",
        r"\bwhere do (?:i|we) (?:live|work|come from)\b",
        r"\bwhat did i say my job\b|\bwhat(?:'s| is| was) my job\b|\bwhere do (?:i|we) work\b|"
        r"\bwhat did i say i (?:do|did)\b|\bwhat do i work as\b|\bwhat do i do for (?:a )?living\b",
        # "where was i going with this" is a lost thread, not a place: the place ask is the one
        # that stands on its own. It is the same pattern the store answers it with, read here as
        # well, so a shape added to one is answered by the other: "whereabouts do i live" and
        # "what area do i live in" were in the answer but not in this gate, and fell to the
        # search hedge while the store had the place on file.
        PLACES_ASK.pattern + r"|\bwhere do (?:i|we) work\b",
        # The animal can be singular, plural or possessive: "what's my dog called",
        # "whats my dogs name", "what's my cat's name" are one ask, and people type all three.
        r"\bwhat(?:'s| is| was) my (?:dog|cat|pet)(?:'?s)?\b|"
        r"\bwhat did i say my (?:dog|cat|pet)(?:'?s)?\b|"
        r"\bremember my (?:dog|cat|pet)(?:'?s)?\b|\bwhat do i call my (?:dog|cat|pet)(?:'?s)?\b|"
        r"\bwhat did i call my (?:dog|cat|pet)(?:'?s)?\b|"
        r"\bwhat(?:'s| is| was) my (?:dog|cat|pet)(?:'?s)? called\b|"
        r"\bwhat are my (?:pets|dogs|cats) called\b|\bwhat are my (?:pets|dogs|cats)\b|"
        r"\bwhat did i say my (?:pets|dogs|cats) (?:were|are) called\b|"
        r"\bwhat my (?:dog|cat|pet)(?:'?s)?\b|^my (?:dog|cat|pet)(?:'?s)?$",
        # "what am I allergic to" arrives in many shapes: "what was I allergic to", "what I'm
        # allergic to", "what did I say I was allergic to". They all put "I" beside the ask.
        r"\bwhat (?:am|was) i allergic to\b|\bwhat i (?:am|was) allergic to\b|"
        r"\bwhat did i say i (?:am|was) allergic to\b|"
        r"\bwhat(?:'s| is| was)? my budget\b|\bmy budget again\b|\bwhat did i say my budget was\b|"
        r"^my budget$",
        # How they eat is a fact of theirs like their budget: "what's my diet" is a recall, not
        # a request for ideas. "what should i eat" is left to the answers, which can suggest.
        r"\bmy diet\b|\bwhat do i not eat\b|"
        r"\bwhat (?:do|did) i eat\b(?=\s*[?.!,]|\s*$)|"
        r"\bwhat am i (?:eating|not eating)\b",
        # Every shape of "what were we on?", and every shape of "say that back to me": these
        # are the lines that ask about the conversation, so the store must own them all. One
        # pattern, read in both places, so a shape added to the gate is answered as well.
        THE_CHAT_ASK.pattern,
        r"\bwhat did i (?:just )?(?:ask|want to know)\b"
        r"(?![^.?!]*\babout\b(?!\s+(?:me|it|that|this|them|us)\b))|"
        r"\bwhat did i (?:just )?say\b(?!\s+(?:about|to|when|in|on|wrong)\b)|"
        + ACTIVITY_ASK.pattern + "|" + PLAN_MINE.pattern,
        r"\bwhat have i told you\b|\bwhat do you (?:know|remember) about me\b|"
        r"\bwhat did i (?:tell|say)(?: you)? about me\b|\bwhat do you know about me\b|"
        # A clause that ends the line cannot tell an ask from a statement on its own: "i feel
        # guilty about what i said" and "remind me what i said" end the same way, and the
        # statement was answered with the whole picture ("Not much yet - you haven't told me
        # about yourself"). The reminder wrapper comes off in `_bare`, so the ask is the whole
        # line; anything in front of it is the statement it is a clause of.
        r"^what i (?:told|said)(?: you)?$|^what have i (?:told|said)(?: you)?$",
        r"\bremember what we talked about\b|\bdo you remember (?:what|our|yesterday|me)\b",
        # "what did i say about the cake?", "and what did i tell you about it?": whatever the
        # thing is, the question is about this conversation, not about the world.
        WHAT_I_SAID.pattern + r"|\bwhat was it i said\b|"
        # The same ask in the tense of the telling: "what was i telling you about the deposit",
        # "what have i been saying about the boiler". People use the tense of the telling, not
        # the tense of the reading, and the recap of the chat is not the line they want.
        r"\bwhat (?:was|were) (?:i|we) (?:telling you|mentioning|on about)\b|"
        r"\bwhat have i been (?:saying|telling you)\b|"
        # The same ask with the "did" left out, which is how people say it in a reminder:
        # "remind me what i said about the boiler", "can you remember what i told you...". What
        # follows is the thing or the ask ("about the boiler", "i was saving for"), never a
        # statement about the person ("what i said hurt him"), which is news, not a recall.
        # "we" as well when it names the thing: "remind me what we said about the boiler" is that
        # one recall, and a bare "what we said" is the recap of the whole chat.
        r"\b(?:what|anything) (?:i|we) (?:said|told you|mentioned|asked)"
        r"|\bwhere (?:we|it|this|the (?:chat|conversation)) (?:all )?(?:started|began)\b"
        r"|\bwhich (?:question|thing) (?:did i|i) (?:ask|asked|say|said|start with|started with)\b"
        r"(?=\s*(?:\?|$|again\b|please\b|about\b|i\b|my\b|the\b|that\b|"
        r"to (?:me|you)\b|before\b|earlier\b))|"
        r"\b(?:do|can|could|did) (?:you|u) remember what i\b",
        # "remind me what i do" is the job ask in the words a reminder uses; a bare "what i do"
        # after a statement ("that's what i do") is not an ask at all, so it needs the pointer.
        r"^what i (?:do|did)$|\b(?:remind me|tell me|can you (?:remind me|tell me)) what i (?:do|did)\b|"
        r"\bwhat did i say my age\b|\bhow old am i\b|\bwhat(?:'s| is| was)? my age\b|"
        r"\bmy age again\b|\bhow old did i say\b|"
        # The age in the order a reminder puts it: "do you know how old i am", "remind me how
        # old i am". `_bare` takes the asking frame off, so what is left is "how old i am",
        # and the gate has to know it is the same ask or it never reaches `_age_reply`.
        r"\bhow old i (?:am|was)\b",
        r"\bwhat (?:am i|are we) (?:planning|up to)\b|\bwhat (?:am i|are we) doing\b(?!\s+wrong)\b|"
        r"\bwhat(?:'s| is|s)?\s+(?:coming up|on for (?:me|us))\b|"
        r"\bwhat (?:have|has) (?:i|we) got (?:coming up|on|planned)?\b|"
        r"\bwhat do (?:i|we) have (?:coming up|on|planned)\b|"
        r"\banything (?:planned|coming up)\b|\banything on\b" + NOT_ON_A_MEDIUM +
        r"|\bwhat am i looking forward to\b|"
        # A plan is a fact of theirs like the budget, and people ask for it in the past as often
        # as the present: "what was I planning?", "remind me what I'm saving for", "whats my
        # plan". The reminder wrapper is off already ("what i was planning").
        r"\bwhat (?:was|were) (?:i|we) (?:planning|saving|saving up)\b|"
        r"\bwhat (?:am i|are we|is) (?:saving|saving up)\b|"
        r"\bwhat i (?:was|am) (?:planning|saving)\b|"
        r"\bwhat(?:'s| is| was) my plan\b" + NOT_THE_PLAN + r"|"
        r"\bwhat was (?:the|my) plan\b" + NOT_THE_PLAN + r"|"
        r"\bwhat was i going to do\b(?:\s*then)?\s*[?.!,]*$|"
        r"\bwhere (?:are|were|was|am) (?:we|i) (?:going|off|headed|heading|away)\b|"
        r"\bwhen (?:are|were|was|am) (?:we|i) (?:off|going|away|moving|flying|travelling)\b|"
        r"\b(?:which|what) (?:month|day|week|date) (?:are|am|is) (?:we|i)\b|"
        r"\bremind me where\b",
    )
    if ASKED_ALL.search(low):
        return True
    if any(re.search(pattern, low) for pattern in checks):
        return True
    if TOPIC_ASK.search(low) or ASK_WITHOUT_MY.search(low):
        return True
    # "summarise our chat", "what did we talk about": a recap ask is about the conversation, so
    # it is never quoted back as something the person said, and it is never the thing the chat
    # was on.
    if _summary_ask(low):
        return True
    # "what's the noise again?" names the thing instead of asking "what did I say about it".
    # It is a recall only when the thing is one they really said: the word has to be in one of
    # their last lines, so "what's the time" is still a question about the time.
    named = THING_AGAIN.match(low)
    if named and _said_word(named.group(1), memory):
        return True
    # "and which knee was it": a detail they gave, asked for by the thing it is about. The same
    # ask as "what did i say about my knee", and it was answered by nobody - the gate let it
    # through as a question about the world, so it got the search hedge from the fallback.
    if _which_thing_was_it(low, memory):
        return True
    if _an_attribute_they_gave(low):
        return True
    # "what subject did i say i was revising": only when a line answers it does the gate hold.
    if _an_open_attribute_ask(low, memory):
        return True
    # "and my job?" after "what's my name?" is one more fact recalled, not a new subject: a
    # short line that only names a fact of theirs, and only once the recall is already going.
    if re.search(r"^my (?:job|work|name|budget)$", low) and _recall_in_progress(memory):
        return True
    # Reads of the chat itself keep the words that ask for them: "say that again" needs its
    # "again", so these are matched before the reminder wrapper comes off.
    if FIRST_ASK.search(low) or SAID_ASK.search(low) or _repeat_ask(text, folded):
        return True
    # A money ask in the present tense names a thing the chat may already hold a bill for: "my
    # water is 40 a month" then "how much do i spend on water" was answered "Six to eight
    # glasses a day", because the entry keyed on the word "water" is supported by the line and
    # took the turn from the store that had the figure. Where a bill for that very thing is on
    # record the line is the figure they gave, asked back. Where none is, it is the habit
    # question it sounds like ("how much do i spend on food a month"), and the world's.
    if memory is not None and spent.PRESENT_ASK.search(text or "") and spent.answer(text, memory):
        return True
    # "what do I do?" is only about their job when the line points back at what they told us
    # ("what do I do again?", "what do I do for a living?") or when the recall is already going
    # ("what did I say my name was?" / "and what do I do?"). After a problem
    # ("my washing machine is leaking" / "what do I do?") it is a request for help, and a real
    # answer should take the turn.
    if not re.search(r"\bwhat do i do\b", low) or len(low.split()) > 7:
        return False
    if MEMORY_POINTER.search(folded) or _recall_in_progress(memory):
        return True
    # "i work in a warehouse" then "what do i do" is the job they just told us; the same ask
    # after a problem ("my washing machine is leaking") is a request for help, not a recall.
    return _job_just_said(memory, low)


def _doing_again(text, memory):
    """True when "what do i do again" is about the task on the table, not the person's job."""
    folded = _folded(text or "", memory)
    if not SELF_DO_AGAIN.search(folded):
        return False
    if _recall_in_progress(memory):
        return False
    # The line the person just wrote may be the one that gave the job ("hi, i'm a baker in
    # Cardiff"), which `_job_just_said` does not count because it also carries a name: the job
    # is still what they last told us, so "what do i do again?" is that job.
    job = (user(memory) or {}).get("job")
    line = last_user(memory) or ""
    if job and (str(job).lower() in line.lower() or _job_words_seen(job, line)):
        return False
    return not _job_just_said(memory, "what do i do again")


def _an_open_attribute_ask(low, memory):
    """The line that answers "what subject did i say i was revising", or "" when none does.

    A line has to be found for this to hold, so a question about the world keeps its reply. The
    clause after the verb decides the line; the kind's words are the fallback for an ask that
    stops at the verb. The best line wins, so "shift pattern" finds the line that says "shifts".
    """
    part = ATTRIBUTE_KIND.match(low or "")
    if not part:
        return ""
    kind = " ".join(part.group(1).split())
    if not kind or kind.split()[0] in NOT_A_KIND or len(kind.split()) > 3:
        return ""
    after = re.search(r"\b(?:say|said|tell you|told you|mention|mentioned)\b(.*)$", low)
    words = content(after.group(1)) if after else set()
    words = {word for word in (words or content(kind)) if len(word) > 2}
    if not words:
        return ""
    best, score = "", 0
    for turn in _every_line(memory):
        line = turn.get("user") or ""
        if not line or _asks(line):
            continue
        seen = _seen(line)
        found = sum(1 for word in words if _alike(word, seen))
        # The later line wins a tie: it is the one with the name in it, which is what was asked.
        if found and found >= score:
            best, score = line, found
    return _recall_quote(best, memory) if best else ""


def _recall_in_progress(memory):
    """True when the last turn was the bot answering a question about the conversation."""
    if not isinstance(memory, dict):
        return False
    before = " ".join((last_user(memory) or "").lower().split())
    # A question about how the chat went ("what did I ask you first?") tells us nothing about
    # the person's job: "so what do I do?" after it is a request for help, not a job recall.
    if before and (FIRST_ASK.search(before) or SAID_ASK.search(before)
                   or _repeat_ask(before, before)):
        return False
    if last_module(memory) == "memory_store":
        return True
    return bool(before) and _about_this_chat(before)


def _a_dislike_told(text, memory):
    """The answer just given with the food the guest hates taken out, or None."""
    if not isinstance(text, str) or DISLIKE_ASK.search(text):
        return None
    if _about_this_chat(text, memory):
        return None
    tastes = read_tastes(text)
    if len(tastes) > 1:
        # "i dont like fish but i love prawns" is two tastes, and the promise about one of them
        # throws away the other half ("Fair enough - no fish in anything I suggest" for a person
        # who has just said they love prawns). A line of more than one taste is the taste
        # module's, which says both back.
        return None
    found = _dislikes_here(text)
    if any(_one_half_of_the_dish(food, taste) for food, _ in found for taste in tastes):
        # A dish said with both its halves is one thing, not its first word: "fish and chips"
        # is not fish and "mac and cheese" is not cheese, and promising to leave "fish" out of
        # everything for someone who eats fish is worse than saying the line back. The taste
        # module keeps the dish whole.
        return None
    foods = [food for food, kind in found if kind in ("user", "other")]
    alone = []
    if not foods and _last_answer(memory):
        # A bare "no mushrooms" answers the suggestion the bot has just made, and nothing in the
        # line has a verb for `found` to read. It is only a dislike when there is a suggestion
        # for it to be about: "no milk" on its own is as likely to be about the fridge.
        alone = guest.turned_down_alone(text)
        foods = alone
    if not foods:
        return None
    previous = _last_answer(memory)
    if previous:
        revised = guest.revise(previous, foods)
        if revised:
            return revised
        # The answer on the table does not name the food, so this is a steer on that answer and
        # not a fresh dislike: "what can i cook with mince" then "i dont want a lasagne" is
        # `ruled_out`'s line, which says the answer still stands. Promising to leave lasagne out
        # of everything is an answer to a question nobody asked, and it takes the turn from the
        # module built for the shape. The hook is the one the arbiter already asks for it.
        try:
            if ruledout.takes_as_it_comes(text, memory):
                return None
        except Exception:  # noqa: BLE001 - a hook that raises claims nothing
            pass
    a_pair = len(foods) > 1
    own = [guest.plain(food, a_pair) for food, kind in found if kind == "user"]
    own = own or [guest.plain(food) for food in alone]
    own = [food for food in own if food]
    if own:
        return guest.left_out(own)
    return None


def _a_diet_told(text, memory, low):
    """"she doesnt eat meat" said about someone: "Your mum doesn't eat meat."

    The fact is already kept against that person by the time this runs (observe comes first), so
    a friend says it back with their name in it instead of "Noted! What would be most useful to
    talk about?", which tells the person nothing about whether it was taken in. The user's own
    diet is not here: that is a line about them, and the echo handles it.
    """
    if not isinstance(text, str) or "?" in text:
        return None
    if _the_ask_beats_the_receipt(text, memory):
        # The line ends on a question the cards can answer, so the fact is only what that question
        # is about: filing it is the whole job, and the receipt is a line nobody asked to have said
        # back. "my sister is veggie ... what can i cook" gets the dinner card, not "Your sister is
        # veggie."
        return None
    if _about_this_chat(text, memory) or OTHER_ASK.search(low) or REMINDER_MID.search(low):
        return None
    found = extract.extract(text)
    if found.get("diet") or found.get("no_meat") or found.get("allergies"):
        return None
    named = [who for who in (found.get("people") or []) if isinstance(who, str)]
    for entry in found.get("others") or []:
        diet = entry.get("diet")
        if not diet:
            continue
        who = entry.get("who") or _person_from_pronoun(text, memory, named)
        return _diet_sentence(who, diet)
    return None


def _a_known_person(memory, who):
    """What the chat holds about one person: the facts filed against them and the lines said.

    The two are kept apart because they answer differently: a fact goes into the sentence about
    the person, and a line is something they said, said back in their own words. A line that is
    itself an ask about them ("what did i say about my sister") is not something they told me
    about her, so it is skipped: otherwise the follow-up "what else did i say" quotes the ask.
    A line that carries on in "she"/"he"/"they" belongs to the person named just before it, so
    "my sister is called meg" then "she doesnt eat meat" is two lines about the sister.
    """
    family = _the_same_person(who)
    entry = {}
    for known in others(memory):
        if str(known.get("who") or "").lower() not in family:
            continue
        # The facts for one person arrive in several entries ("my son is 7", then "my son is
        # allergic to nuts"), so they are read together: the age from one and the allergy from
        # the other are the same son.
        for key, value in known.items():
            if key == "who":
                continue
            if isinstance(value, list) and isinstance(entry.get(key), list):
                entry[key] += [item for item in value if item not in entry[key]]
            else:
                entry[key] = value
    # "my mum" is the usual way of naming her, and a line that opens with the word ("mum is
    # allergic to shellfish") is about the same person. The word has to open the line: "dad jokes"
    # in the middle of a line about something else is not their dad.
    pattern = _the_name_pattern(who)
    # A line that carries on in a pronoun is about the person named just before it, so
    # "my sister is called meg" then "she doesnt eat meat" is two lines about the sister.
    carried = re.compile(r"^\s*(?:and\s+|also\s+)?(?:she|he|they|her|him|them|his|hers|their)"
                         r"(?:'s|'re|s|re)?\b", re.I)
    lines = []
    # A line whose fact a later line gave again with a different value is not something to say
    # back: "my sister is 12" / "sorry shes 14" would answer "Your sister is 14. You also said
    # my sister is 12", handing back the value they just corrected. The store holds the 14, so
    # the old line is left out and the fact speaks for itself.
    moved = _lines_a_person_moved(memory)
    current = ""
    for turn in _every_line(memory):
        line = str(turn.get("user") or "")
        if not line:
            continue
        named_here = _a_relation_in(line)
        if named_here:
            current = named_here
        if _asks(line) or _about_this_chat(line) or ABOUT_PERSON_ASK.search(line.lower()):
            continue
        if ((pattern.search(line) and not A_PROGRAMME_IS_ON.search(line))
                or (current in family and carried.match(line))):
            flat = " ".join(line.lower().split()).strip(" ?!.")
            if flat in moved:
                continue
            if _only_a_pointer(flat):
                # "she isnt" is the fact taken back and "my wife is too" is the fact given to her,
                # not something to say back about the person: quoting one would answer "what do
                # you know about my wife" with "you told me your wife isnt".
                continue
            lines.append(line)
            # "his names tom" after "my husband" is his name, and a name is said properly:
            # "your husband" and a bare "his names tom and hes a teacher" is a line of theirs
            # read back with nothing added, which is what a search result does.
            given = _a_name_in_a_pronoun_line(line)
            if given and not entry.get("name"):
                entry["name"] = given
                lines = []
    # A line that gives the name already filed for them says nothing the store cannot say
    # better: "my mums name is Ann" is answered "Your mum is called Ann", not read back as
    # "You told me your mums name is Ann".
    if entry.get("name"):
        lines = [one for one in lines if not _only_the_name(one, entry["name"], who)]
    return entry, lines


def _about_a_person_reply(memory, low, text=""):
    """Everything held about someone they mentioned: "what do you know about my sister?".

    "what have i told you about my mum" had a reply and "what do you know about my mum" had
    none, so the same ask in the other words fell to the search hedge while the store sat on the
    answer. The person is read first, then the facts filed against them (name, age, allergies,
    what they eat) and the last line said about them: the store says the person back in its own
    words instead of quoting a line, which is what a friend would do. A "what else" ask gets the
    honest "that's everything" once the whole person has been described, never the same sentence
    again.
    """
    if not isinstance(low, str):
        return None
    # "what do you know about ada" is the same ask when Ada is a name the chat was given for
    # someone: the name is filed with the person, and people ask by the name they were told.
    called = _the_person_called(memory, low)
    match = (ABOUT_PERSON_ASK.search(low) or _continues_an_about_ask(memory, low)
             or (ABOUT_A_NAME.search(low) if called else None))
    if not match:
        return None
    who = _named_person(low, memory) or called
    if not who:
        # "what do you know about her" asks about the person the chat was just on: the pronoun
        # is read the way every other line in the store reads it, so the follow-up reaches the
        # facts the named ask reaches.
        who = _pronoun_person(text or low, memory)
    if not who:
        # "what do you know about my kids" names no one relation, so every branch above found
        # nobody: the children are filed as several people under one word, and the whole of them
        # is the answer.
        children = _about_the_children_reply(memory, low)
        if children:
            return children
        return None
    entry, lines = _a_known_person(memory, who)
    named = _called(entry.get("name")) if entry.get("name") else ""
    clauses = _person_clauses(who, entry)
    birthday = str(entry.get("birthday") or "").strip()
    if birthday and not clauses and not lines:
        # A date filed against a person is a fact about them like an age is, and a birthday can
        # be all the store holds: the reader had only the line they said it in, which - once a
        # correction had moved the date - was the line that carried the one they took back.
        return _vary(["Your " + who + "'s birthday is " + _date_written_as_a_date(birthday) + ".",
                      "You told me your " + who + "'s birthday is "
                      + _date_written_as_a_date(birthday) + "."], memory)
    if not clauses and named and not lines:
        # The only thing the chat holds about them is the name they gave for them a line
        # before ("my husband" then "his names tom").
        return _vary(["Your " + who + " is called " + named + ".",
                      "Your " + who + " is " + named + "."], memory)
    if not clauses and not lines:
        # A line the chat has about them is something to say, even when no fact was filed from
        # it: "my mum is 72 and dad is 74" files the mum's age and not the dad's, so "what do you
        # know about my dad" cannot say "you haven't told me anything" about a line they just
        # said. The line that names them is said back in their words.
        named_line = _a_line_about(memory, who)
        if named_line:
            return ("You told me " + _named_back(who, you(named_line)).strip().rstrip(".") + "."
                    if not ABOUT_PERSON_MORE.search(str(text or ""))
                    else "That's all I have: " + _named_back(who, you(named_line))
                    .strip().rstrip(".") + ".")
        # The person is known to the chat only by name ("my sister is coming on friday"), or
        # not at all: there is nothing to say back, so the store says so instead of hedging. The
        # second ask in a row is answered as a second ask, not with the same line in other words.
        if ABOUT_PERSON_MORE.search(str(text or "")):
            return "You haven't told me anything about your " + who + " yet."
        return _vary(["You haven't told me anything about your " + who + " yet.",
                      "Nothing on your " + who + " so far \u2014 tell me and I'll keep it."],
                     memory)
    subject = "Your " + who + ((" " + named) if named and clauses else "")
    facts = ""
    if clauses:
        if len(clauses) == 1:
            facts = subject + " " + clauses[0]
        else:
            rest = [clause[3:] if clauses[0].startswith("is ") and clause.startswith("is ")
                    else clause for clause in clauses[1:]]
            facts = subject + " " + clauses[0] + " and " + _and_list(rest)
    said = ""
    if lines:
        line = you(lines[-1]).strip().rstrip(".")
        # "she doesnt eat meat" is about the person they named a line earlier, so the reply names
        # them: "You told me your sister doesnt eat meat" says who, where a bare "she" does not.
        line = _named_back(who, line)
        if named:
            # The name they gave is written the way a name is written: "Meg" inside the line.
            line = re.sub(r"\b" + re.escape(named) + r"\b", named, line, flags=re.I)
        said = line
    # One line already carrying the facts is the whole answer: "your mum is 72 and lives in
    # york" says the age, and "Your mum is 72. You told me your mum is 72 and lives in york"
    # says it twice. The facts lead only when they add something the line left out.
    if said and (not facts or _covers(said, clauses)):
        # A line that was itself a telling comes back without the store's frame: "You told me you
        # told me about your mum" says the telling twice, and the echo already carries who told
        # whom. Same rule as `told._quote`.
        if TELLING_ALREADY.match(said):
            answer = said[0].upper() + said[1:] + "."
        else:
            answer = _vary(["You told me " + said, "You said " + said], memory) + "."
    elif facts and said and _tokens(said) <= _tokens(facts):
        # The facts already say everything the line says: the line adds nothing to it.
        answer = facts + "."
    elif facts and said:
        answer = facts + ". You also said " + said + "."
    else:
        answer = (facts or "") + "."
    if ABOUT_PERSON_MORE.search(str(text or "")) and (
            _said_everything(answer, memory)
            or re.search(r"\b(?:everything you've told me|all I've got) (?:about|on) your "
                         + re.escape(who), last_bot(memory) or "", re.I)):
        return _vary(["That's everything you've told me about your " + who + ".",
                      "That's still all I've got on your " + who + "."], memory)
    if _said_everything(answer, memory):
        # The same ask twice says the same sentence twice, which is the one thing a store that
        # hands a fact back may not do: the second time it is shorter, and still true.
        body = (facts or said or answer).strip().rstrip(".")
        return "Still: " + body[0].lower() + body[1:] + "."
    return answer


def _repeat_ask(text, low, memory=None):
    """True when the line asks to hear the bot's last reply again, not about its content."""
    if WHOLE_ASK.match(str(low or "").strip()):
        # A whole-answer ask is the store's only when there is a whole answer behind it. With
        # nothing but a hello or a nod above it the store has nothing to hand over, and claiming
        # the line took "hi" / "in full" and "thanks" / "the lot" off the ordinary reply and
        # answered "Nothing from me on that yet. What were you asking about?" back at a person
        # who had asked for nothing.
        return True if memory is None else _a_whole_answer_to_hand_back(memory, text)
    if not REPEAT_ASK.search(low) or not REPEAT_START.match(low):
        return False
    # The words are read off the folded line, not the raw one: "what did you say earlier in this
    # chat" is the ask without the wrapper, and reading the raw line put "chat" among its content
    # words - so the ask was not a repeat ask, and the line was handed the shrug instead of the
    # answer it asked to hear again.
    return set(keywords(REPEAT_TAIL.sub(" ", low))) <= REPEAT_WORDS


def _a_whole_answer_to_hand_back(memory, text=""):
    """True when the chat's last answer is one this store can hand over whole.

    The same reading `_repeat_reply` makes - the last line the bot said that answered something,
    a take-back passed over - so the claim and the reply are about the same turn.
    """
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    said = [turn for turn in turns if str(turn.get("bot") or "").strip()]
    if not said:
        return False
    if named_thing.takes_back(said[-1].get("user")):
        said = [turn for turn in said[:-1]
                if not named_thing.takes_back(turn.get("user"))] or said
    about = _hearing_again(said, str(text or ""))
    return about is not None and about.get("module") in ANSWER_MODULES


def _carries_something(turn):
    """True when a bot turn has something in it to hear again.

    "Glad that helped.", "Sounds good.", "Alright then — good luck with it." are nods. Asked
    "say that again" after one of them, repeating the nod is repeating nothing: the thing the
    person wants back is the answer the nod followed.
    """
    reply = str(turn.get("bot") or "").strip()
    if not reply:
        return False
    if _about_this_chat(str(turn.get("user") or "")):
        # The bot's own paperwork: "You started with: "we got a puppy"" is the store quoting the
        # chat back, not something the person asked to hear again. Asked "what did you say
        # earlier" a turn after a recall, handing that line back told them their own first line
        # twice in a row.
        return False
    return turn.get("module") in ANSWER_MODULES or len(reply.split()) >= 8


def _hearing_again(said, line):
    """The bot turn a repeat ask is about: the last line, or the last one with content in it.

    "thanks" / "Glad that helped." / "say that again" is a person asking for the answer they
    thanked the bot for, so the nod is passed over. A line that asks about the last thing said
    ("what did you just say", "pardon") is about the nod itself.

    A nod is not a question, so nothing the bot said back to one is the answer to hear again,
    whichever module said it: after a "thanks" the reply in hand was the nod's, not the answer's,
    and a repeat ask that lifted a figure out of it lifted the figure out of the wrong text.
    """
    if LAST_LINE_ASK.search(str(line or "")):
        return said[-1]
    live = [turn for turn in said if not _only_a_nod(turn.get("user"))]
    if live and len(live) < len(said):
        said = live
    answered = [turn for turn in said if not _about_this_chat(str(turn.get("user") or ""))]
    if answered and len(answered) < len(said):
        # A turn that was itself a question about the chat is the bot's paperwork, not an answer
        # to hear again: "what did i say at the start of this chat" then "what did you say
        # earlier" handed back "You started with: "we got a puppy last week"" a second time.
        said = answered
    if not thread.thin(str(said[-1].get("user") or "")):
        # The bot was answering a line of its own, so its last reply is the thing to hear again.
        return said[-1]
    # After a "thanks" or an "ok" the reply is a nod. The answer they want back is the one the
    # nod followed, and that is the last turn an answer came from.
    answering = [turn for turn in said if turn.get("module") in ANSWER_MODULES]
    if answering:
        return answering[-1]
    carrying = [turn for turn in said if _carries_something(turn)]
    if carrying:
        return carrying[-1]
    # Only a greeting or a nod to hand back, with the ask having nothing to be about: the caller
    # answers the line as it would have without the ask.
    return None


def _first_reply(memory):
    """The first line the person sent, the way a friend would recall how the chat began."""
    lines = _turn_lines(memory)
    if not lines or not lines[0][0]:
        return _vary(["You haven't said anything yet, so this is the start.",
                      "We're just beginning — you go first."], memory)
    said = [line for line, _ in lines if _worth_reporting(line)]
    if not said:
        return _vary(["We've only just started — nothing of yours to look back on yet.",
                      "Only hellos so far: your first proper line is still to come.",
                      "Nothing of yours to report back yet — you've only said hello."], memory)
    first = said[0]
    options = ["You started with: \"" + _trim(first) + "\"",
               "Your first line was: \"" + _trim(first) + "\"",
               "That's how we opened: \"" + _trim(first) + "\""]
    if len(said) <= 1:
        options.append("This chat opened with: \"" + _trim(first) + "\" — not much else yet.")
    return _vary(options, memory)


def _recall_quote(line, memory=None, asked=False):
    """"You said: \"...\": their own words, trimmed, so the answer is the thing itself.

    A question is quoted as the question it was: they still said it, so it is what the chat has
    been about, but "You said" would turn a question into a statement.
    """
    said = "\"" + _trim(line, 120) + "\""
    if asked:
        return ASKED_LEADS[(len(recent(memory, 8)) if memory else 0) % len(ASKED_LEADS)] + said
    if memory is None:
        return QUOTE_LEADS[0] + said
    # The same question twice should not read as the same sentence twice.
    asked = sum(1 for turn in recent(memory, 8)
                if re.search(r"\bwhat (?:did|have) i\b", (turn.get("user") or ""), re.I))
    return QUOTE_LEADS[asked % len(QUOTE_LEADS)] + said


def _says_something(part):
    """True when a part of an answer says more than how long it takes.

    "20 minutes, give or take" was handed back as the answer to "i have 20 minutes": it is the
    answer's own aside, and on its own it tells the person nothing they did not just say.
    """
    left = TIME_LENGTH.sub(" ", " ".join(str(part or "").split()))
    left = HALF_AN_HOUR.sub(" ", left)
    words = [word for word in re.findall(r"[a-z']+", left.lower())
             if word not in LENGTH_FILLER and len(word) > 1]
    return len(words) >= 2


def _seconds(said):
    """A length of time in seconds ("20 minutes", "half an hour", "a couple of days"), or None."""
    text = " ".join(str(said or "").split())
    if not text:
        return None
    half = HALF_AN_HOUR.search(text)
    found = TIME_LENGTH.search(text)
    if half and (not found or half.start() < found.start()):
        return 1800
    if not found:
        return None
    count = found.group("count").lower()
    if count.startswith("a couple"):
        number = 2
    elif count.startswith("a few"):
        number = 3
    elif count.isdigit():
        number = int(count)
    else:
        number = WORD_NUMBERS.get(count)
    unit = found.group("unit").lower().rstrip("s")
    if not number or unit not in UNIT_SECONDS:
        return None
    return number * UNIT_SECONDS[unit]


def _names_minutes(said):
    """True when the wording names minutes rather than hours: "45 minutes", "twenty-minute"."""
    return any(match.group("unit").lower().startswith("min")
               for match in TIME_LENGTH.finditer(" ".join(str(said or "").split())))


def _longest(said, bare=False):
    """The longest length of time named in a sentence, in seconds, or None.

    The longest and not the first: a move that says "one minute of jogging, two of walking, for 20
    minutes" wants 20 minutes of room, not one, or a budget of 20 minutes would be told the answer
    does not fit it.
    """
    text = " ".join(str(said or "").split())
    if not text:
        return None
    half = HALF_AN_HOUR.search(text)
    if half:
        text = text[:half.start()] + " 30 minutes " + text[half.end():]
    found = [match.group(0) for match in TIME_LENGTH.finditer(text)]
    lengths = [n for n in (_seconds(part) for part in found) if n]
    if bare or any(second <= 3600 for second in lengths):
        # "tuna pasta in 15, macaroni cheese in 25" says its minutes without the word: beside a
        # figure that does name minutes, a bare number after "in" is a length too, and without it
        # a list of quarter-hour meals was read as taking forty-five minutes.
        for bare in re.finditer(r"\bin\s+(\d{1,2})\b", text, re.I):
            minutes = int(bare.group(1))
            if 0 < minutes <= 90:
                lengths.append(minutes * 60)
    return max(lengths) if lengths else None


A_LENGTH_AS_THE_SUBJECT = re.compile(
    r"^(?:(?:so|and|but|well|ok|okay)\s+)?"
    r"(?:(?P<length>" + LENGTH + r")\s*(?:left\b|,|\bis\b|\bwas\b|\bfeels\b|\bsounds\b)"
    r"|that\s+wants\s+(?:longer|more)\s+than\s+" + LENGTH + r"\b"
    r"|it\s+takes\s+longer\s+than\s+" + LENGTH + r"\b)", re.I)


def _a_remark_about_a_length(answer):
    """Whether the reply only remarks on a length, giving none to a thing it names.

    True only when every sentence of it that names a length has that length as its subject. A reply
    that puts a length on a thing - "roast it for 20 minutes a kilo" - is an answer, whatever else
    it says, so one such sentence is enough to make it one.
    """
    remarked = False
    for sentence in _sentences(answer):
        if _longest(sentence) is None:
            continue
        if not A_LENGTH_AS_THE_SUBJECT.search(" ".join(sentence.split())):
            return False
        remarked = True
    return remarked


def _moves(answer):
    """The moves of an answer in the order given: the move, its length, and its sentence number."""
    names = _names_minutes(answer)
    out = []
    for at, sentence in enumerate(_sentences(answer)):
        for part in _halves(sentence):
            if not _says_something(part):
                continue
            out.append((part, _longest(part, bare=names), at))
    return out


def _up_to_the_move(answer, part):
    """The answer from its first sentence to the one `part` was cut from, and no further.

    A move of an answer is not the whole of it: the sentence before it says what to do with it
    ("bring a pan of water to a bare simmer ... slide the egg in from a cup", then "3 minutes
    gives a soft yolk"). Handing back the move alone answered a question about how with a number,
    and handing back everything after it put a second recipe in the reply.
    """
    want = " ".join(str(part or "").split())
    sentences = _sentences(answer)
    for at, sentence in enumerate(sentences):
        for half in _halves(sentence):
            if " ".join(half.split()) == want:
                if not at:
                    # The move is in the answer's first sentence, where everything that comes
                    # before it is already in it: "tuna pasta in 15, macaroni cheese in 25" needs
                    # no lead-in, and taking the whole sentence would put the forty-five minute
                    # traybake in a reply that says half an hour covers it.
                    return want
                return " ".join(sentences[:at + 1]).strip()
    return None


def _the_move_that_fits(moves, room):
    """The move whose own length is the largest that fits, and the long move it is a step of.

    The largest that fits, not the shortest: somebody with 20 minutes wants the twenty-minute way
    of doing it, not the two-minute half of a paragraph that is about something else. The second
    value is the length of the move that takes longer than the room when that move is in a
    sentence *before* the one that fits, and the fit is therefore a step of it: "rest it for 15
    minutes before carving" comes after "a 2kg bird takes roughly 1 hour 40", so it is a step of
    that bird. Two ways of the same thing ("aim for about 150 minutes a week - five half-hours, or
    three twenty-minute sessions") are in one sentence, so the twenty-minute way there is a way to
    do it and not a step of the longer one.
    """
    best, best_sentence, best_seconds = None, None, -1
    over, over_sentence = None, None
    for part, took, sentence in moves:
        if took is None:
            continue
        if took > room:
            if over is None:
                over, over_sentence = took, sentence
            continue
        if took > best_seconds:
            best, best_sentence, best_seconds = part, sentence, took
    step = over if (best is not None and over is not None and over_sentence < best_sentence) else None
    return best, step


def _left_out(moves, room):
    """True when the answer has a move of its own that takes longer than the room."""
    return any(took is not None and took > room for _part, took, _at in moves)


def _the_lead(answer):
    """The first thing an answer says, for a budget too small for any move of it.

    The lead and not the quickest move: an answer that lists what can be cooked "in 15" and "in
    25" has one move with a length on it - the forty-five minute one - and handing that back to
    somebody with five minutes answers a question they did not ask.
    """
    for sentence in _sentences(answer):
        part = LEAD_LABEL.sub("", sentence.strip(" .;,"))
        if _says_something(part):
            return part
    return None


A_RATE_OF = re.compile(
    r"\b(?P<length>\d[\d,.]*|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|"
    r"twenty|thirty|forty|forty[- ]five|fifty|sixty|ninety|half\s+an|an?)\s*"
    r"(?P<unit>minutes?|mins?|hours?|hrs?)\s+(?:a|per|each)\s+(?:day|week)\b", re.I)


def _a_rate_of_the_same_length(answer, room):
    """True when the answer names this same length as a regular allowance ("20 minutes a day").

    A length said as a rate is what the person's day holds, and the answer is already about it:
    what the allowance means is the sentence that says so, not the answer's first move.
    """
    for found in A_RATE_OF.finditer(str(answer or "")):
        if _seconds(found.group("length") + " " + found.group("unit")) == room:
            return True
    return False


def _the_budget_on_the_answer(text, memory):
    """The answer above, cut to the part of it that fits the time they say they have, or None.

    Narrow on purpose: the line has to be the person saying how much time there is, nothing else
    ("only for work", "i was only 5 minutes" say no length at all), it must not be a question, and
    the answer it follows has to carry a length of its own - there is nothing to fit a budget to
    otherwise. A budget too small for any of the answer still gets its quickest move, because the
    answer is the answer: it only takes longer than they have.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return None
    said = " ".join(text.split())
    if not said or "?" in said or len(said.split()) > 11:
        return None
    found = BUDGET.match(said)
    if not found:
        return None
    tail = said[found.end():].strip(" .!,;")
    if len(tail.split()) > 4:
        # "i only get 20 minutes to get to the station" is a question about the journey, not the
        # room the answer above has.
        return None
    if re.match(r"^of\b", tail, re.I):
        # "i have 2 hours of meetings today" is two hours of meetings, not two hours to cook: the
        # length belongs to the thing after it, and the answer above has all the room it had. A
        # length said "before work" or "to myself" is still room ("20 minutes before work" is the
        # time there is), so the gate is on the "of" and not on a tail at all.
        return None
    room = _seconds(found.group("length"))
    if room is None:
        return None
    longer = None
    for answer in _recent_answers(memory):
        if _a_rate_of_the_same_length(answer, room):
            # The answer already talks about this length as a regular allowance - "Twenty minutes
            # a day gets you a simple song in two or three months" - so the length is answered and
            # the reply is that sentence, which the composer hands back. Claimed as a budget the
            # whole answer came back again, first sentence and all: "i want to learn guitar" then
            # "i only get 20 minutes a day" was the guitar answer twice. A length the answer gives
            # its own steps in ("fry it hot for 5 minutes", "3 minutes gives a soft yolk") is not
            # this, and neither is a rate for a different length ("150 minutes a week").
            return None
        if room < 86400 and A_HORIZON.search(answer):
            # "ice it for 20 minutes at a time ... for the first two days" is a day's regime read to
            # a 20-minute budget: the length in it is a step, not what the answer costs, and "20
            # minutes is more than enough for all of that" is not true of a two-day answer. The
            # answer stands as it was given - passing the line on put another module in charge of
            # it, which said "Same as before: <the whole answer>" and told them nothing new.
            lead = _the_lead(answer)
            if lead:
                return pick(BUDGET_TIGHT, memory).format(
                    budget=_theirs(found.group("length"), mid=True), part=_tidy(lead))
            continue
        if _a_remark_about_a_length(answer):
            # A remark about a length is not an answer with a length in it, so there is nothing
            # here for the budget to fit inside: look further back for the answer it is about.
            continue
        longest = _longest(answer)
        if longest is None:
            # A turn with no length in it is not the answer this budget is about: a reply of the
            # store's own ("Fair enough - no salad in anything I suggest"), or a detail turn in
            # between, must not hide the answer two turns up that the budget is really for.
            continue
        moves = _moves(answer)
        part, over = _the_move_that_fits(moves, room)
        if over is not None:
            # The answer's long move is behind the one that fits, so the fitting move is a step of
            # it and not a way to do the whole thing: "how long do i roast a chicken" with 20
            # minutes found "rest it for 15 minutes before carving" and said 20 minutes covered a
            # bird that takes 1 hour 40. A step is never the answer to a budget that the answer
            # itself does not fit, so the answer's lead says it in the tight shape instead.
            lead = _the_lead(answer)
            if lead:
                return pick(BUDGET_TIGHT, memory).format(
                    budget=_theirs(found.group("length"), mid=True), part=_tidy(lead))
        if part:
            # Which shape it takes is decided by whether the budget leaves anything out: a budget
            # bigger than every move in the answer is not a limit, and saying "two hours is enough
            # for that" beside a list of quarter-hour meals made the clock the point of the reply.
            if _left_out(moves, room):
                shorter = _up_to_the_move(answer, part)
                if shorter and len(shorter.split()) <= 90 and _says_something(shorter):
                    # A move is handed back with everything the answer said before it: "3 minutes
                    # gives a soft yolk" on its own answered a question about how with a number,
                    # and the pan, the vinegar and the whirlpool were in the sentence before it.
                    part = shorter
                shape = BUDGET_FITS
            else:
                # A budget bigger than every move of the answer is not a limit on anything, so the
                # answer must not come back whole: "i want to learn guitar" then "i have 30
                # minutes a day" was the guitar card again, word for word, with one line added,
                # and "how do i cook a steak" then "i have an hour" was the steak card again. The
                # person is saying time is not the thing in the way, so the answer's lead (what to
                # do first) is quoted, not all of it.
                # An answer whose only number is the one in the move keeps the whole of itself: the
                # egg's "3 minutes gives a soft yolk" is the how the person asked for, and the pan
                # work in front of it is one sentence. An answer with several numbers has no single
                # one to keep, and quoting it back reads as the previous reply twice.
                kept = None
                if len(ANY_FIGURE.findall(answer)) == 1:
                    shorter = _up_to_the_move(answer, part)
                    if shorter and len(shorter.split()) <= 45 and _says_something(shorter):
                        kept = shorter
                if kept:
                    part = kept
                else:
                    lead = _the_lead(answer)
                    if lead and len(lead.split()) <= 90 and _says_something(lead):
                        part = lead
                shape = BUDGET_MORE
            return pick(shape, memory).format(budget=_theirs(found.group("length")),
                                              part=_tidy(part))
        if longer is None:
            longer = answer
    if longer is None:
        return None
    part = _the_lead(longer)
    if not part:
        return None
    return pick(BUDGET_TIGHT, memory).format(budget=_theirs(found.group("length"), mid=True),
                                             part=_tidy(part))


def _theirs(length, mid=False):
    """The length as they said it, with a capital and no full stop: "20 minutes"."""
    text = " ".join(str(length or "").split()).strip(" .;,")
    if not text:
        return text
    if mid and not text[1:2].isupper():
        return text[:1].lower() + text[1:]
    return text[:1].upper() + text[1:]


def _tidy(part):
    """A move of an answer as the first thing a reply says: capital, no trailing full stop.

    A question mark goes too: the budget shapes put a full stop and a sentence after this, so an
    answer that ended on a question read "does that feel like enough for what you have in mind?.
    That wants longer than 20 minutes" (witty-string, #6254). The pools that end on a question are
    every pool the composer has, so this is the store's join to fix and not one module's wording.
    """
    text = " ".join(str(part or "").split()).strip(" .;,?!")
    if not text:
        return text
    return text[:1].upper() + text[1:]


def _clauses(reply):
    """The clauses of an answer, longest-lived punctuation split, in the order given."""
    text = " ".join(str(reply or "").split())
    return [part.strip(" .;") for part in CLAUSE_SPLIT.split(text) if part.strip(" .;")]


def _the_limit(reply):
    """The answer's own restriction - "cut the distance and the speed for a week or two"."""
    for part in _clauses(reply):
        low = part.lower()
        if len(part.split()) > 24:
            continue
        if any(low == word or low.startswith(word + " ") for word in RESTRICT_OPENS):
            return part
    return None


def _the_condition(reply):
    """The answer's own stop condition - "see a physio if the pain is sharp" - or None."""
    for part in _clauses(reply):
        low = part.lower()
        if len(part.split()) > 26:
            continue
        if STOP_CONDITION.match(low) and " if " in low:
            return part
    for part in _clauses(reply):
        low = part.lower()
        if re.search(r"\b(?:means stop|stop driving|do not drive|don't drive)\b", low):
            return part
    return None


def _recent_answers(memory, back=3):
    """The answers the chat has had, newest first, as far back as "the advice above" reaches.

    Read from the history every lane writes (`turns`), not from the answer record one lane keeps
    under its own key: that record is that lane's business, and a reader that depends on it goes
    quiet the moment that lane changes it. A turn of the store's own ("Noted: ...") is not an
    answer with advice in it, and the gates below turn it down anyway."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return []
    said = []
    for turn in turns[-back - 1:][::-1]:
        if not isinstance(turn, dict):
            continue
        reply = turn.get("bot")
        if isinstance(reply, str) and reply.strip():
            said.append(reply.strip())
        if len(said) >= back:
            break
    return said


def _shares_a_word(low, said):
    """True when the line names something the answer it would quote also talks about.

    `should i keep running` and the running-knee answer share "run"; `should i keep the
    appointment` and that answer share nothing but "keep" and "the". Stems, so the tense does not
    have to match, and the chat's filler words are not evidence of anything.
    """
    def words(text):
        return {stem(word) for word in keywords(str(text).lower())}
    return bool(words(low) & words(said))


def _the_call_from_the_advice(text, memory):
    """The decision a follow-up asks, answered with the limit the last answer already gave.

    Only a decision about going on with the thing in the air, only when the answer above put a
    limit on it ("cut the distance...", "keep to ten minutes"), and only inside a chat with a
    topic. Everything else is left to the module that knows the line.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return None
    low = _bare(_folded(text, memory))
    if not low or len(low.split()) > 9 or " you " in " " + low + " ":
        return None
    if not CALL_ASK.match(low) or not CARRY_ON.search(low):
        return None
    if SEE_SOMEONE.search(low):
        # "should i see someone about it or wait" is answered by the "when to see a physio" part
        # of the answer above, which the entry that gave it can hand back in full.
        return None
    # The answer that had the limit in it: the newest one that is about the same thing as the
    # line and carries both halves of the advice. A detail turn in between ("only on the outside
    # of the knee", answered with what that pain is) must not hide the advice two turns up.
    limit = condition = None
    for said in _recent_answers(memory):
        if not _shares_a_word(low, said):
            # The line has to be about the thing the answer was about. Without this, one answer
            # with a limit in it answered every decision the chat made for the next three turns:
            # after the running-knee answer, "should i keep the appointment" and "can i still
            # drive there" both came back as "cut the distance and the speed for a week or two".
            continue
        found, if_half = _the_limit(said), _the_condition(said)
        if found and if_half:
            limit, condition = found, if_half
            break
    if not limit or not condition:
        return None
    rest_or_go = re.search(r"\b(?:keep|keep going|carry on|continue|still|go on)\b", low)
    if STOP_IT.search(low) and rest_or_go:
        # "should i rest it or keep going" is a choice between two things, and the advice above
        # argued for one of them in its own words: the entry that knows the sore knee answers
        # that line better than half of it does, so it is left alone.
        return None
    if STOP_IT.search(low):
        # "should i stop running?" - the advice said how to go on with a change, so the answer is
        # the change rather than stopping, in the answer's own words.
        return ("Not all the way: " + limit[0].lower() + limit[1:] + ". And "
                + condition[0].lower() + condition[1:] + ".")
    return pick(CALL_LEADS, memory).format(limit=limit[0].lower() + limit[1:],
                                           condition=condition[0].lower() + condition[1:])


def _trim(text, limit=90):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"
