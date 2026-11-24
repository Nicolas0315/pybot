"""Part 17 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import copy

from ..compose import greet_with
from ..memory import hope, matters, obstacle, plan as plan_steps
from ..memory.when import asks_what_today_is
from ..memory import size as another_size
from ..memory.cause import NO_REASON as _NO_REASON
from ..compose import verdict as verdict_reply
from ..memory import current

from ..memory import ack, current
from ..memory.topics import in_a_safety_thread as _safety_thread
from ..memory.topics import names_nothing

from ..memory import again as _same_again  # the answer under a repeat's lead-in
from ..memory import repeat
from .chat_part_05 import (
    _tokens,
)
from .chat_part_12 import (
    _reply,
)
from .chat_part_13 import (
    _normalised_line, _repaired_line,
)
from .chat_part_14 import (
    _a_part_of_the_answer_they_have, _a_topic_still_in_this_exchange, _reads_as_distress,
    _the_newest_line_started_the_topic,
)
from .chat_part_15 import (
    A_REPEAT_LEAD, _the_same_answer_again, _a_mood_pool_line, _about_the_topic,
    _asks_what_they_said, _bare_ask, _names_its_own_thing, _nothing_was_heard, _said_before,
    _says_nothing_about_the_ask, _says_the_kind, _the_verdict_in,
)
from .chat_part_16 import (
    _respond,
)


def respond(text, memory):
    if asks_what_today_is(text):
        # "what day is it" asks the calendar, and a chat about a bad week is not the subject: the
        # sentence about how to bring it up answered it, because a bare question was read as one
        # more thing said in the thread. The date is the answer, whatever else was said.
        return None
    # "what next" and "and then" after an answer that gives its steps in order (`bot/memory/
    # plan.py`). Without it this module's own readers hand the first step back for every ask, then
    # the whole card again ("From just now: turn the water off..., take the handle off..."), which
    # is the fault the lane's chat found. Read here as well as in `bot/modules/steps.py`, which is
    # the module this normally goes to: either can be the candidate the arbiter keeps for the line,
    # and both are handed the same step.
    step = plan_steps.carry_on(text, memory) if isinstance(memory, dict) else None
    if step is not None:
        return step
    # A line that is nothing but a stated dislike of the thing the last answer leaned on is the
    # objection to that answer, and the answer to it is the step of it that does not need the
    # thing (`bot/memory/obstacle.py`). It is checked here as well as in `greeting` because this
    # module answers first: "i want to lose weight" / "i cant stand the gym" came back as the
    # whole diet paragraph again from here, so the narrower reply never got the turn. A line with
    # an introduction waiting on it is left alone; the greeting owns that turn.
    if not (isinstance(memory, dict) and memory.get("greet")):
        answer = obstacle.answer_for(text, memory)
        if answer is not None:
            return answer
    # A limit on the plan in hand narrows the answer, so it is not an aside to hand back. "my mum
    # is coming to stay for a week" then "shes 78 and cant do stairs" handed back the same card
    # word for word, and the turn after it again ("Same answer: ..."), with the stairs unused.
    # Read here because this module answers before the pools do, and only when a plan of a kind
    # the frames are written for is on the table: a limit in a chat about a diet or a dripping tap
    # keeps the reply it has.
    if not (isinstance(memory, dict) and memory.get("greet")):
        narrowed = ack.a_limit_for_the_plan(text, memory)
        if narrowed is not None:
            return narrowed
    theirs = matters.what_they_say(text, memory)
    if theirs:
        # "she says she's fine" after the falls answer is her asking for no fuss, and the turn
        # wants the one thing that works around that. Said back it was the receipt ("Got it -
        # she's fine."), and the person was left with the same worry and nothing to do.
        return theirs
    hoped = hope.answer_for(text, memory)
    if hoped:
        # A hopeful aside after the advice ("fingers crossed", "with luck", "hope it works") is
        # the person going off to do the thing, not a question about it. Read as a lookup it
        # reached whatever its own words fit - "fingers crossed" got the entry on fingers going
        # white in the cold - and read as a report it was filed away ("Got it - hope it works").
        # It is the small talk's turn, and the whole of the reply is the wish said back.
        return hoped
    resized = another_size.answer_for(text, memory)
    if resized:
        # "what about a bigger one" straight after a time answer ("20 minutes per 500g") is that
        # rule asked for their own bird. The follow-up names no food and no figure, so every
        # reader refused it and the person was told the bot did not know enough to answer
        # honestly - one turn after an answer that had the whole of it.
        return resized
    reply = _respond(text, memory)
    # "and does that fix the pressure too" after the step: the answers entry hands back a slice of
    # its own paragraph, word for word, and says nothing about the question. The step is in the
    # answer a turn ago, so what the person is owed is whether doing it is the fix and how they
    # will know - the composer owns that reading and its wording (bot/compose/verdict.py).
    # Only when this module has nothing of its own: "my phone battery drains fast" then "will that
    # fix it" is a step that is right and a question about it, and the answer it already gives
    # ("That is the right first move, and what comes back from it decides the next step") is
    # better than any line about watching one - read first, it took that turn and let a repair
    # card in behind it.
    if reply is None or _the_same_answer_again(reply, memory, text):
        fixed = verdict_reply.the_fix_asked(text, memory)
        if fixed:
            reply = fixed
    # The same paragraph twice, word for word. "i had a panic attack" then "i cant come": the
    # decline stands the feeling's claim down, and what is left on the table is the card the
    # person was just given, so the second turn repeated the first one whole. No answer to a new
    # line is the answer to the old one, so this module stands aside and lets the module that
    # reads the line in the light of the last one take the turn ("You can't come. That explains
    # it - no wonder it sits on you."). Only a whole answer, word for word: the pieces of a card
    # are reused on purpose, and only here is the repeat the whole of what the person gets.
    if (reply is not None and _the_same_answer_again(reply, memory, text)
            and not (repeat.asks_to_put_it_right(text) and A_REPEAT_LEAD.match(reply))):
        # A line asking to put the thing right ("can i save it") is answered from the answer on
        # the screen, and that answer's own reader frames it under a lead. The lead is not a
        # module handing back a card on a new subject: it is the one answer this line has, so
        # clearing it left only the search shrug (the burnt pan had bicarbonate in the line above).
        reply = None
    # The hello for a line that introduced someone and then said something else: the answer is
    # what they get, with "Hi Jess — " in front of it. Cleared here whether or not this module
    # wrote the answer, so a greeting cannot arrive on a later turn.
    greeted = memory.pop("greet", None) if isinstance(memory, dict) else None
    if greeted:
        if reply is None:
            # Nothing in this module could answer what came after the introduction, and the
            # fallback's hello back ("Hey! What's on your mind?") answers neither half: the
            # welcome, which says the name, is the better reply and it is what this line got
            # before the introduction was let through.
            return _reply("meet", memory, greeted)
        reply = greet_with(greeted, reply)
    if reply is not None:
        return reply
    # Nothing matched the words as they were typed: read the line the normalised way and try
    # again, so a typo in a greeting, a thank-you or a goodbye ("hii", "thnaks", "byeee")
    # still lands. Only a line that found no reply at all can change here, so this can add a
    # reply and never take one away.
    # The spelling first, in the person's own words: "i dont kno" comes back as "i dont know"
    # and not as "i do not know", where the expansion's "not" reads as a decline.
    typed = " ".join(text.lower().split())
    for retry in (_repaired_line(memory), _normalised_line(memory)):
        if retry is None or retry.strip() == typed:
            continue
        # Only a short line is re-read this way: the rewording is there for a typo in "hii" or
        # "thnaks", and on a longer line it can invent a reading ("thanks. i think i'll ask them
        # for feedback" comes back as "i think i will ..." and reads as a plan).
        if len(_tokens(retry)) > 8:
            continue
        # The retry text has the slips undone already, so it is read as written: the reading
        # holds `plain`, which is the line as typed with its misspellings put right, and
        # putting it over a retry undoes that repair (`as_said=False`, see below).
        reply = _respond(retry, memory, as_said=False)
        if reply is not None:
            return reply
    # Nothing found the line even as it was meant to be read: a question with no subject in it
    # ("how long does it take?") is about the thing on the table, so it is read once more with
    # that thing's words in front of it.
    return _follow_up_reading(text, memory)


def _follow_up_reading(text, memory):
    """A follow-up read again with the topic it follows, when the line on its own found nothing.

    The words a knowledge entry is keyed on are often in the earlier line rather than in the
    ask: "how many lessons will i need" after "im learning to drive" names no subject, so the
    line as typed reached no entry and the bot hedged, while the same question with the topic
    written out - "im learning to drive how many lessons will i need" - is answered. Nothing is
    read this way until the line has failed on its own, mid-emergency the topic starts again
    from the line itself, and the sentence just given is never said twice.
    """
    if _safety_thread(memory) or _reads_as_distress(text):
        return None
    # A yes/no about a thing they have just been told about is answered by the verdict the card
    # they were given already holds: "my exhaust is blowing" / "is it safe to drive" was the
    # search hedge over a paragraph that says "It is not an emergency, but fumes can get into the
    # cabin, so keep a window open". The carry further down reaches the same entry and comes back
    # framed as a repeat, which is no answer to the ask at all. Read before the length gate: a
    # yes/no that names the thing is a bare ask however long the rest of it is ("will it sting me
    # if i ignore it" was nine words, so it fell past this function to a card about a sting
    # already in you).
    verdict = _the_verdict_in(text, memory)
    if verdict:
        return verdict
    if not _bare_ask(text):
        return None
    # A length ask whose answer has no set length is answered by saying so, not by finding a
    # second card about the same subject: "i cant sleep" / "how long will it take" read the
    # sleep answer again, which answered nothing. narrow's own "no set time" line is a whole
    # answer to the ask, and it is already the answer this module has in hand.
    from ..memory.narrow import NO_SET_TIME
    part = _a_part_of_the_answer_they_have(text, memory)
    if part and part.startswith(NO_SET_TIME):
        return part
    if isinstance(memory.get("understood"), dict) and memory["understood"].get("about_bot_kind"):
        # A question about the bot names no subject of its own, so it looks like the plainest
        # follow-up ("who am i talking to"), and carrying the last turn into it answered that
        # ask with the presentation card when the chat before it was about work. The bot is
        # the subject; nothing of the last topic goes in front of it.
        return None
    if isinstance(memory.get("understood"), dict) and memory["understood"].get("someone_new"):
        # "my knee clicks when i climb stairs" / "should i text him back": the ask names a
        # person no line has introduced, so it is a question about them, not a bare ask about
        # the knee. Carried into the knee entry it answered with the knee card again, and the
        # person asking what to do about somebody got their own knee read back.
        return None
    from ..memory.topics import context as _topic_context
    from ..memory.topics import a_stay_with_the_place as _a_stay_with_the_place
    from ..memory.topics import asks_how_long_to_stay as _asks_how_long_to_stay
    from ..memory.topics import the_city_of as _the_city_of
    clean = " ".join(text.lower().replace("\u2019", "'").split())
    # The subject is not always the line just said: "what breed is good with kids" is a
    # follow-up itself, and the dog is in the line before it. Newest first, and a line that
    # names nothing of its own ("how much is that?") is no subject to carry.
    topics_said = [" ".join(str(line or "").lower().split())
                   for line in reversed(_topic_context(memory, 3))]
    # The no-reason line is not always kept as a topic: "im not sure why" is read as a question,
    # so the topic list can drop it and the ask after it carries the feeling anyway. The turns
    # themselves are the reliable record of it.
    recent_said = [" ".join(str(turn.get("user") or "").lower().split())
                   for turn in (memory.get("turns") or [])[-3:] if isinstance(turn, dict)]
    # A line that said there was no reason is not the subject of the question after it. The
    # state it was joined to is not a topic either: "im feeling down today" / "i dont know why" /
    # "how do i feel better" read with the mood in front of it reached the condolence card, and
    # "can i do anything about it" came back as the repeat. An ask is its own line, answered the
    # way it would be without the feeling turn before it - which is what plain-tent's
    # request_changes named: the no-reason turn must not claim the ask after it.
    if (isinstance(memory.get("understood"), dict)
            and memory["understood"].get("kind") == "question"
            and any(_NO_REASON.match(line) for line in (*topics_said, *recent_said))):
        return None
    if topics_said and _nothing_was_heard(memory, topics_said[0]):
        # "i went 2 hours without a drink today" was heard as nothing at all - the module that
        # answered it was the fallback, so nothing was taken from it - and "should i be
        # worried" then read with it in front of it reached the weekly alcohol limits and told
        # somebody who had gone two hours without a drink how many units a week they may have.
        # The ask's own words finding a neighbour is not the topic's fact, and a topic nobody
        # heard is not a topic to carry anything into.
        return None
    if any(_reads_as_distress(topic) for topic in topics_said):
        # "ive had enough of living" then "what can i do about it" was carried into the anger
        # pool and answered "say it out loud to whoever caused it, once you've cooled off".
        # Nothing is carried off a line like that: the widened reading is off, and the turn is
        # whatever the line alone finds (main's hedge, and the safety module's if it reads it).
        return None
    # The line just said is in the turns as well, and read with itself in front it is the same
    # line twice ("my boiler is losing pressure my boiler is losing pressure"), which is not a
    # follow-up at all: it is a line of its own. So a topic that is the line itself is never
    # carried, and a first turn has nothing to be carried from.
    # A line that names a thing of its own is not asking about the topic: "wheres my phone" and
    # "where is the remote" stay lines of their own (see `_names_its_own_thing`).
    readings = []
    for topic in topics_said:
        if not topic or topic == clean or names_nothing(topic):
            continue
        if _names_its_own_thing(text, topic):
            continue
        stay = _a_stay_with_the_place(clean, topic)
        if stay is not None:
            readings.append((topic, stay))
        elif _asks_how_long_to_stay(clean) and _the_city_of(topic):
            # The chat is on a city and the line asks how long. When the stay reading above found
            # nothing, the topic's words in front of the line only reach the city's own entry,
            # whose length is a holiday's: "i live in edinburgh" then "how many days" is a
            # person who lives there, and "how many days should i rest my ankle" is an ankle.
            continue
        else:
            readings.append((topic, topic + " " + clean))
    if not readings:
        return None
    from ..modules import answers as _answers
    from ..understanding import understand as _understand
    # The newest topic is the one a follow-up is carried into. An older one is only reached by
    # an ask that names nothing of its own ("how long does it take", "what can i do"): once the
    # newest topic's answer is the one already on the screen, the ask is that question again,
    # and the topic before it is a different subject. Without this the search walked back to an
    # unanswered line two turns ago and answered the person's own subject from it - "how do i
    # stop courgettes going soggy" / "should i scarify the lawn" / "when should i scarify the
    # lawn" got "Sow courgettes from late April indoors", which is the wrong plant and the
    # worst kind of answer.
    # ...and only when the newest topic named nothing of its own either. "we are getting a
    # puppy" / "i want to lose a stone" / "how long will it take" walked past the stone - the
    # newest line, and the subject of the ask - to the puppy two turns back, and answered a
    # question about a diet with the puppy's walking rule. A topic that named something is the
    # subject the ask belongs to even when the ask names nothing itself, so the walk stops there.
    # ...unless the newest line only leaned on a topic an earlier line started, which is not a
    # subject of its own however much it names. "my son is starting secondary school" / ... /
    # "hes quite anxious anyway" / "should i talk to the school" / "when should i do that": the
    # school line is a follow-up that added to the first topic, so the thing the ask is about is
    # the one before it, and stopping at the school line left the turn with nothing but the
    # opening paragraph again. A line that does start a subject ("i want to lose a stone") is
    # still where the walk stops.
    carries_past_the_newest = names_nothing(clean) and (
        not topics_said or names_nothing(topics_said[0])
        or not _the_newest_line_started_the_topic(memory))
    # The topic's words in front of the ask, and nothing else: the topic on its own is the
    # previous turn's question again, and answering that a second time is not a follow-up.
    for index, (topic, reading) in enumerate(readings):
        if index and not carries_past_the_newest:
            return None
        if reading == clean:
            continue
        # The reading is a line of its own, so it is understood as one. The knowledge base reads
        # the subject off `memory["understood"]` when it is there, and that is the *previous*
        # line: with it left in place "im learning to drive how many lessons will i need" is
        # judged to have a subject of its own and the driving entry never looked at.
        # A copy that is deep enough that nothing this reading writes can reach the real
        # memory: the topic, the plan and the understood line are nested, and a shallow copy
        # left the widened reading's subject behind for the *next* turn, which then answered a
        # salad follow-up with the kitchen-cleaning entry.
        reading_memory = copy.deepcopy(memory)
        reading_memory["understood"] = _understand(reading, reading_memory)
        # The words of the earlier turn are in front of this one, so a pool here must not treat
        # them as words the person just typed (see `_joke` and `_joined_read`).
        reading_memory["joined_read"] = True
        # The knowledge base first: what a follow-up wants is the fact the topic's words
        # reach, not this module's plan line for somebody who has just mentioned a plan.
        said = _answers.respond(reading, reading_memory)
        if not said or _said_before(said, memory):
            if memory.get("entry_answer") or memory.get("entry_answers"):
                # A knowledge entry answered the topic, so the follow-up belongs to that entry
                # and its subject. Asked of this module instead, the synthesised line is read
                # as a line somebody typed, and the pools it picks from are chosen for a
                # trouble already recorded: "should i ring him" after "we fell out over money"
                # got the note-taking line for an elderly person's falls, because "fell out"
                # was taken as a second fall.
                # The entry has answered already, but this line may be a different part of it:
                # "how much do they cost" after the driving answer gave the price in its second
                # sentence, and the carry led back to the same entry, so the price went unread
                # and the person got the search hedge while it sat two lines up.
                part = _a_part_of_the_answer_they_have(clean, memory)
                if part:
                    return part
                continue
            said = _respond(reading, reading_memory)
            current = memory.get("understood") if isinstance(memory, dict) else None
            if (said and isinstance(current, dict) and current.get("kind") == "question"
                    and _a_mood_pool_line(said)):
                # The topic was how the person feels, and this line asks for help or how to do
                # something: the mood pool's line answers neither, so the ask keeps its own
                # answer (the one it would have had without the topic in front of it).
                said = None
            if said and _says_nothing_about_the_ask(said):
                # "Worth doing. Where are you with it so far?" is what this module says to a
                # plan nobody asked about. Read with the topic in front of it, a question about
                # the place ("is it a good place to live") looks like that plan, and the person
                # asked something - so it is no answer to hand back.
                said = None
        if not said:
            continue
        # A reply framed as a repeat is the answer already on the screen: the topic in front of
        # the line led the widened reading back to the entry that answered the topic, and
        # bot/memory/again wrapped the paragraph it had already given. "how do i clean my boots"
        # after "how do i cook rice" came back as "Same answer, and it covers this: Rinse it
        # until the water runs clear...", which is no answer to the second line at all.
        if _said_before(said, memory) or _said_before(_same_again.unframed(said) or said, memory):
            # The entry that answers this topic has already been given in full, so the line is
            # the same question again: it gets the shrug, never the neighbouring fact from an
            # older topic, which is what "how much do they cost" and its neighbour answer were.
            # A part of the answer already given is not the neighbouring fact, so that is tried
            # before the shrug.
            part = _a_part_of_the_answer_they_have(clean, memory)
            if part:
                return part
            # The paragraph that came back is the newest topic's own, and the topic before it
            # is still the exchange the person is in: that one is read next rather than the
            # shrug, because it is the line that has the answer ("when should i do that" after
            # the school line). Only a topic still in this exchange, never an older subject.
            if index == 0 and topics_said[1:2] and _a_topic_still_in_this_exchange(
                    topics_said[1], memory):
                continue
            return None
        if not _says_the_kind(clean, said):
            # A price asked and a duration given is a confident wrong answer, which is worse
            # than the hedge it replaced.
            return None
        if _asks_what_they_said(said, memory):
            # "Mornings that heavy are worth listening to. How long has it been like that?" was
            # the answer to "what should i do" after "ive been like this since about march":
            # a question asked back at somebody who has just answered it. Asking a second time
            # is worse than the hedge it replaced.
            continue
        if not _about_the_topic(reading, reading_memory, topic):
            # The widened line reaches some entry, but not one about anything the topic said:
            # "should i ring him" after "we fell out over money" reached a bowel-tracking entry
            # through "night" and "tablet", and told somebody whose brother is not speaking to
            # them to note a rush to the loo. An entry that shares no word with the topic is
            # the ask's own words finding a neighbour, not the topic's fact.
            continue
        return said
    return None


from ..memory import again as _never_twice  # noqa: F401, E402 - applied once the module is defined


# Whatever this module answers, the last thing that happens to it is the earlier-turn
# check (bot/memory/again.replied): `answers` alone served a card again on 59 deck turns.
respond = _never_twice.replied(respond)
