"""Part 16 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import badnews, doubted, fallback, negated, pick, says_it_has_lingered, step_when_low
from ..compose.badnews import reads_like_a_symptom
from ..compose.goodnews import a_detail_of_the_news, asks_for_news
from ..understanding.kinds import ADDRESSED, THANKS_NOISE
from ..compose import reaction as answer_reaction
from ..compose.repair import amends_to, deed_of, with_the_feeling_named
from ..compose import reading as reading_reply
from ..compose import verdict as verdict_reply
from ..compose import doubt as doubt_reply
from ..compose import occasionplan
from ..memory import about, about as about_the_person

from ..memory import remedy
from ..memory import stuck as stuck_line
from ..memory import thread
from ..memory.topics import in_a_safety_thread as _safety_thread

from ..memory import carried_on as step_after
from ..memory import passing_the_time
from ..memory import the_years
from ..memory import warmth as talked_to
from ..memory import limits, portions
from ..memory import hours as hours_after, limit, meant, pile, repeat, tried, more, returned
from ..understanding import lexicon
from .chat_part_01 import (
    ACK_WORDS, HELP_ONLY, LAUGH_WORDS, SAYS_TOO_MUCH, THANKS_FILLER, _news_before, _only_a_refusal,
)
from .chat_part_02 import (
    _the_ask_after_a_job_that_went,
)
from .chat_part_03 import (
    ANY_WORLD_NEWS_ON, BODY_BEFORE_AN_EVENT, COLD_NAMED, COLD_SORE, COLD_SORE_FEELING, COLD_SYMPTOM,
    COMPLAINT_ONLY, DOUBT_FRAME, FOND_REPLIES, GOOD_NEWS_SAID, ILL_SELF, KIND_REPLIES, KIND_TO_ME,
    MISS_ME, MISS_YOU_REPLIES, NOT_GLAD_WORDS, NOT_LANDED, POSITIVE, SICK_DEED, STILL_ON_THEM,
    _a_limit, _fond_of_the_bot, _praised_the_answer, _their_own_call,
)
from .chat_part_04 import (
    LONG_SPAN, REPLIES, VENTED, _the_same_cold_again,
)
from .chat_part_05 import (
    ASK_WHETHER_TO_SPEAK, FEELING_SAID, NOT_PROUD, PROUD_OF_ANOTHER, PROUD_OF_MYSELF, SAY_SOMETHING,
    _about_bot, _context_follow_up, _judged, _name, _opinion, _the_steps_again, _tokens,
)
from .chat_part_06 import (
    ANSWERS_HOW_ARE_YOU, HEDGED_LOW_LINE, HEDGED_OK_LINE, HOW_THEY_ARE_LINE, MEANT_LEADS, NOT_GOOD,
    THANKS_FOR, _a_hedge_answering_the_question, _a_plain_good_answer, _a_thank_you_taken_off,
    _bare_feeling, _body_is_a_feeling, _bye_kind, _denies_a_good_word, _ending_bye, _is_bye,
    _is_greeting, _is_howareyou, _is_thanks, _just_met, _mid_chat, _plan_clause,
    _without_the_at_all, _without_the_nod,
)
from .chat_part_07 import (
    AT_MYSELF, AT_MYSELF_REPLIES, A_VERDICT_ASKED, GOING_ON_LONG, KEEPS_HOW_THEY_ARE, KICK_MYSELF,
    MOOD_KINDS, STATE_WHEN, _a_bare_acknowledgement, _a_low_word, _as_said, _idk_kind,
    _the_heavy_line, _the_weight_said,
)
from .chat_part_08 import (
    NOT_A_NOD, _a_doubt_about_being_taken_on, _a_feeling_riding_on_the_thread, _a_judgement_asked,
    _against_me, _asked_how_it_went, _feel_like, _going_on, _reaction, _the_age_in_a_work_thread,
    _the_nod,
)
from .chat_part_09 import (
    SOMEONE_BRING_SOMEONE, SOMEONE_IS_IT_NORMAL, SOMEONE_NEXT_STEP, SOMEONE_NORMAL,
    _a_repair_is_open, _a_row, _a_row_ending, _a_row_next, _the_deed_before, _worry_someone,
)
from .chat_part_10 import (
    FEDUP_GERUND_SAFE, FEDUP_LEAD, FEDUP_REPLIES, FED_UP_WHOLE_OF_IT, OTHER_PERSON,
    _about_the_person, _early_start, _intent, _judgement, _my_night, _not_coping, _other_feeling,
    _says_nothing_much, _stuck,
)
from .chat_part_11 import (
    FED_UP_ABOUT_THE_BOT, FED_UP_DENIED, FED_UP_WITH_A_PERSON, _fed_up_with, _fedup_phrase,
    _question_coming, _someone_reply,
)
from .chat_part_12 import (
    _a_death_just_said, _about_the_night_out, _after_a_lost_thread, _after_lonely, _answers_knows,
    _conversation, _feeling, _nothing_helps, _reply, _say,
)
from .chat_part_13 import (
    _chat_scatter, _joke, _says_dont_know, _short_talk, _standing, _their_thing, _without_the_might,
)
from .chat_part_14 import (
    AMENDS_REPLIES, ASKS_FOR_THE_WORDS, ASKS_WHAT_TO_DO, DEED_NEXT, FAMILY_NAMED,
    NOT_TALKING_AFTER_A_REPAIR, SAID_UNKINDLY_FAMILY, SAID_UNKINDLY_REPLIES, SAID_WRONG,
    SAID_WRONG_AT_THEMSELVES, SAID_WRONG_DEED, SAID_WRONG_NEXT, SAID_WRONG_REPLIES,
    THEY_ARE_NOT_TALKING, _about_someone, _after_a_repair, _said_unkindly, _said_wrong,
    _the_deed_pool, _the_words_pool,
)
from .chat_part_15 import (
    THINKS_REPLIES, _laughing_at, _laughing_still, _news, _somebody_thinks_i_should, _work_grumble,
)


def _thinks_pool(who):
    """The replies for that line, with the person it came from named in them."""
    if who not in ("everyone", "everybody", "people") and not who.startswith("my "):
        who = "your " + who
    return [line.format(who=who, who_cap=who[0].upper() + who[1:]) for line in THINKS_REPLIES]


# Praise of a thing, second-hand, is not advice about the person's life: "everyone says the thai
# place is good", "my sister says i'd like that show", "everyone's raving about that new series",
# "my mates say the new gym is good". The person is not reporting a fact about themselves, a
# trouble or a plan: they have heard something is worth a go, and they are saying so. Every one of
# those was answered by a stock line that fits any message - "Lovely. What made it as good as
# that?" (which assumes they had been), "Thanks for telling me", "I'm listening - say more if it
# helps" - the lines STYLE.md names as failures. There is nothing to know about that place or that
# series and the bot must not pretend otherwise, so the reply takes the recommendation seriously
# and asks what was said about it, which is the thing a friend does next. The thing itself is never
# named in the reply: it can be anything, so a phrase built out of it reads broken English for half
# of them.
A_REPORT_A_THING = re.compile(
    r"\b(?:(?:my|our|the)\s+[a-z]+|everyone'?s?|everybody'?s?|people|someone|somebody|"
    r"a\s+(?:friend|mate|colleague|bloke|girl)(?:\s+of\s+(?:mine|ours))?|friends?)\s+"
    r"(?:says?|said|keeps?\s+saying|was\s+saying|told\s+me|tells\s+me|swears?\s+by|"
    r"swore\s+by|raves?\s+about|"
    r"raving\s+about|went\s+on\s+about|goes\s+on\s+about|wont\s+shut\s+up\s+about|"
    r"won't\s+shut\s+up\s+about|keeps?\s+going\s+on\s+about|put\s+me\s+onto)\b"
    r"(?P<rest>[^?]{2,90})", re.I)


# The same praise with nobody named to carry it: "i heard the thai place is good", "apparently the
# new bakery is lovely", "word is the new gym is great", "i was told the market is worth a visit".
# These were answered as news about the person ("Good for you! That's really lovely news.") or with
# the stock thanks, which fit any message and answer none of it.
A_HEARD_A_THING = re.compile(
    r"\b(?:i\s+heard|i'?ve\s+heard|i\s+was\s+told|i'?ve\s+been\s+told|apparently|"
    r"word\s+is|heard|they\s+say|rumour\s+is|rumor\s+is)\b(?P<rest>[^?]{2,90})", re.I)


# Where the verb itself is the praise, the clause after it needs no "is good" to go with it:
# "my cousin swears by that magnesium", "everyone's raving about that new series".
A_PRAISING_VERB = re.compile(
    r"\b(?:swears?\s+by|swore\s+by|raves?\s+about|raving\s+about|went\s+on\s+about|"
    r"goes\s+on\s+about|keeps?\s+going\s+on\s+about|wont\s+shut\s+up\s+about|"
    r"won't\s+shut\s+up\s+about|put\s+me\s+onto|(?:heard|says?|said|tell\w*\s+me)\s+"
    r"(?:good|great|brilliant|amazing)\s+things\s+about)\b", re.I)


# "does everyone say it is good" is their own question about the world, not a recommendation
# they have been given, and the ask has its own answers.
A_ASKED_NOT_TOLD = re.compile(
    r"^\s*(?:does|do|did|is|are|was|were|has|have|had|would|will|can|could|should|who|why|"
    r"any(?:one|body))\b", re.I)


# "is good", "was great", "is supposed to be brilliant" - the thing being praised. The words after
# the praise are what a person says about a place or a series, and they are what tells a
# recommendation apart from a report about the person themselves.
A_PRAISE_OF_A_THING = re.compile(
    r"\b(?:is|are|was|were|seems|sounds)\s+(?:really\s+|so\s+|apparently\s+|meant\s+to\s+"
    r"be\s+|supposed\s+to\s+be\s+)?(?:good|great|amazing|brilliant|excellent|lovely|"
    r"fantastic|unreal|incredible|the\s+best|worth\s+it|worth\s+a\s+(?:go|look|visit))\b"
    r"|\b(?:you'?d|you\s+would|you'?ll|you\s+will|id|i'?d|i\s+would)\s+(?:really\s+|"
    r"absolutely\s+)?(?:like|love|enjoy)\b"
    r"|\b(?:is|are)\s+(?:meant|supposed)\s+to\s+be\b", re.I)


# A recommendation is not a question, an order to the person, or a health matter. The first is
# their own ask ("does everyone say it is good"), the second is somebody telling them what to do
# ("my mate says i should see a doctor", which has its own answer), and the third is a line the
# health cards must keep.
A_RECOMMENDATION_IS_NOT = re.compile(
    r"\b(?:should|ought|need\s+to|have\s+to|must|make\s+sure|better\s+off|stop|give\s+up|"
    r"doctor|gp|nurse|hospital|999|111|tablet|tablets|medicine|medication|pill|pills|dose|"
    r"antibiotics|checked|check\s+it|scan|test|tested|operation|surgery|injur\w*|symptom\w*|"
    r"bleeding|pain|hurt|sore|fever|rash|pregnant|pregnancy|contagious|infection)\b", re.I)


SECONDHAND_PRAISE_REPLIES = (
    "Worth a look, then. What did they say was so good about it?",
    "Word of mouth is the best kind of recommendation. Is it your sort of thing?",
    "That is one to keep in mind. What made it stick with you?",
    "Praise from someone you know counts for more than a review. What is the draw?",
    "Second-hand or not, that is a good sign. What did they like most about it?",
)


def _somebody_recommended_a_thing(clean):
    """Whether the line is somebody praising a thing the person might try, or None."""
    text = " ".join(str(clean or "").lower().replace("\u2019", "'").split())
    if not text or "?" in text or len(text.split()) > 24:
        return None
    found = A_REPORT_A_THING.search(text) or A_HEARD_A_THING.search(text)
    if not found:
        return None
    rest = " ".join(found.group("rest").split()).strip(" .,!")
    if not rest or len(rest.split()) > 12:
        return None
    if A_ASKED_NOT_TOLD.search(text):
        return None
    if not A_PRAISING_VERB.search(text) and not A_PRAISE_OF_A_THING.search(rest):
        return None
    # "my mate told me to try the 5:2 diet" is somebody telling the person what to do, and that
    # shape has its own answer in the composer; it is not praise of a thing.
    if re.search(r"\b(?:told|tells?)\s+me\s+to\b", text):
        return None
    # "says i'm good with the kids" is praise of the person, not of a thing to go and see
    if re.search(r"\bi(?:'m|\s+am)\b", rest):
        return None
    if A_RECOMMENDATION_IS_NOT.search(rest):
        return None
    return rest


def _respond(text, memory, as_said=True):

    # A plan for a birthday the person already put on file: "my sister turns 30 on saturday" then
    # "i want to plan something". The store holds the day and the age, and this is the only line
    # that reads them: what came back instead was a question ("What's the first step from where
    # you are?") or a plan for a plain Saturday. Read first here, under the greetings and the
    # introduction this function is called after, so the line that introduced somebody still gets
    # its hello.
    planned = occasionplan.reply_for(text, memory)
    if planned is not None:
        return planned

    clean = " ".join(text.lower().replace("’", "'").split())
    # "sick with worry" is a figure of speech, and the only illness in it is the word "sick":
    # answered as a bug it told a person frightened about an exam to rest with warm drinks ("Ugh,
    # the first day of it is the worst"). Read as the feeling it stands for, the rest of this file
    # answers the line the person actually said - "worried about my exam" - and a bug named in the
    # same line ("sick with the flu") is not a feeling, so it keeps its illness.
    clean = badnews.without_the_figure_of_speech(clean)
    # Read before every reading below: a modal in front of a feeling is the feeling, not a plan.
    clean = _without_the_might(clean)
    tokens = _tokens(text)
    if not tokens:
        return None
    # A bare question about how their own thing went - "was it nice", "was it hard", "was it
    # rough" - is a verb and a word this file knows as an acknowledgement, so every pool below
    # reads it as a nod or as a mood of the person's and answers it with a sign-off ("Alright
    # then - good luck with it.") or with advice for the wrong thing ("was it rough" one line
    # after a scan got the pool for a non-stop week). Nothing in here can know how their morning
    # went and the composer's readers can ask it back (bot/compose/how_it_went.py,
    # bot/compose/their_day.py), so the line is left to them. Only the past-tense question with
    # nothing else in it is stood down: "is it scary" about a film and "was it worth it" are
    # questions about the world and keep the answers they have.
    if _asked_how_it_went(clean):
        return None
    still_in = tried.in_care_pool(clean, memory)
    if still_in:
        # A bare "still there" after "my mum is in hospital" is about their mum, and no reader
        # below knows that. The presence line answered about this bot ("Still here. What's up?"),
        # the greeting handed "still the same" the one for a machine that will not budge, and
        # "still in hospital" was asked what happens when they try it again. Nothing in that chat
        # has failed a fix; a person they love is still in, so the next thing said is about them
        # (`bot/memory/tried.py:in_care_pool`). Read before every reading below, and it stands
        # down on every line that is not a bare report on the person (see the reading).
        return pick(still_in, memory)
    news_detail = a_detail_of_the_news(clean, memory)
    if news_detail and not _a_death_just_said(memory):
        # A detail added to news this module has just cheered is the news again, not a question
        # about the subject: "first time" after "i passed my driving test" was answered with the
        # forty-five hours of lessons card, and "2-0" after "we won on saturday" with "That's 2".
        # Read here, under the care fences and above every reading that would take the detail for
        # a question of its own, and only where the cheer was this module's own.
        said_detail = " ".join(clean.split())
        return _say("more_of_the_news" if news_detail == "attempt" else
                    "more_of_the_news_arrival" if news_detail == "arrival" else
                    "more_of_the_news_score", memory,
                    X=said_detail[:1].upper() + said_detail[1:])
    if SOMEONE_BRING_SOMEONE.search(clean):
        record = about_the_person(memory) if isinstance(memory, dict) else None
        if record and record.get("trouble") == "hospital":
            # In a hospital thread, "what should i bring him" is a question about the bag, not the
            # next step of the ward trouble. The step reading below matches a bare "bring" and
            # answered it with "ask the ward what the plan is", while the hospital-bag answer was
            # already in the list behind this one.
            #
            # Only the pronoun shape stands down. A named person ("what should i bring my son")
            # is already the bag in this module's own table, and standing down for it took that
            # away: the gift row does not answer the doubled name, so the turn fell to the search
            # hedge. "What should i bring my dad" and the rest of the named shapes stay on the
            # bag either way; the step reading is the one that needs the fence.
            return None
    doubt = _a_doubt_about_being_taken_on(clean, memory)
    if doubt:
        # "will anyone take me on" after a job loss is a fear and not a question about the world:
        # it was answered with the search hedge, which answers nothing.
        return doubt
    aged = _the_age_in_a_work_thread(clean, memory)
    if aged:
        # Their age, said while the job is gone, is the worry about the age and not the reason for
        # it: answering it as a reason ("so that is the part behind it") puts the age behind the
        # redundancy. Read before every reading below, all of which treat the line as news to
        # acknowledge.
        return aged
    # A sentence of their own that landed badly, said before anything else is read: the words in
    # it name the person it was said to or the meal it was said over, and both would otherwise
    # send the turn to a card about that subject.
    # "what do i do" after a repair is the second step of it, and the first step has just been
    # said: handing the same sentence back is a repeat, and the hedge ("I don't know enough to
    # answer that honestly") disowns the answer given a turn ago. A repair has an order to it, so
    # the follow-up is the next thing to do rather than the thing already done.
    if amends_to(clean):
        return pick(AMENDS_REPLIES, memory, clean)
    if _a_repair_is_open(memory) and THEY_ARE_NOT_TALKING.search(clean):
        # "she wont talk to me" after the apology is the same repair and not a new subject: the row
        # for a child who is slow to talk answered it with the ages children start speaking at.
        return pick(NOT_TALKING_AFTER_A_REPAIR, memory, clean)
    if _after_a_repair(memory) and ASKS_FOR_THE_WORDS.search(clean):
        # "what do i actually say to her" is the sentence itself, and the pool for the deed already
        # has the words in it: what came back instead was the script for comforting somebody who
        # has just told you bad news, which asks the person to say "that sounds really hard" about
        # their own doing.
        deed = _the_deed_before(memory)
        if deed != SAID_WRONG_DEED:
            # An amends ask names no deed, and the sentence it owes is the same one: the pool for
            # the words reads the same for a call that was not made and for "how do i make it up".
            return pick(_the_words_pool(deed), memory, clean)
    if _after_a_repair(memory) and ASKS_WHAT_TO_DO.search(clean):
        # A repair of something done rather than said has no sentence to go back and name, so the
        # next step is the one the pool of the deed was written for.
        if _the_deed_before(memory) == SAID_WRONG_DEED:
            return pick(SAID_WRONG_NEXT, memory, clean)
        return pick(DEED_NEXT, memory, clean)
    if _said_wrong(clean):
        # The target is the person writing: nothing was said to anybody else, so this is
        # being hard on yourself in the words of a regret, not a repair.
        if SAID_WRONG_AT_THEMSELVES.search(clean):
            return pick(AT_MYSELF_REPLIES, memory, clean)
        # The pool follows the deed: what they said is answered with what to say back, and what
        # they did with what to do about it.
        deed = deed_of(clean)
        if deed and deed != SAID_WRONG_DEED and not SAID_WRONG.search(clean):
            # A confession that led with the feeling ("i feel sick that i lied to her") gets the
            # name of it in front of the card, so the answer does not arrive as though nobody had
            # just said how they felt.
            return with_the_feeling_named(pick(_the_deed_pool(deed), memory, clean), clean)
        return pick(SAID_WRONG_REPLIES, memory, clean)
    if _said_unkindly(clean):
        pool = SAID_UNKINDLY_FAMILY if FAMILY_NAMED.search(clean) else SAID_UNKINDLY_REPLIES
        return pick(pool, memory, clean)
    # A line aimed at the bot rather than at the day: warmth ("i love you", "i like you",
    # "youre my favourite") and the line that says the answer missed ("youre not helping",
    # "youre wrong"). Both used to land in the acknowledgement pool, which shrugged at them -
    # "i love you" got "Fair enough." - so they are read whole and answered in kind
    # (bot/memory/warmth.py). Read before the compliment branch below, which would otherwise
    # take "i like you" as praise of the last answer.
    addressed = talked_to.reply(text, memory)
    if addressed:
        return addressed
    # Where the person is right now, when the line is only that: "im on the bus", "waiting for the
    # bus", "im having a lazy day", "im still in bed". The line names a place or a mood and asks
    # nothing, so it used to be declined, filed as a fact about them and left at a shrug - "im on
    # the bus" / "Sorry to hear that." The reply is short and about the moment
    # (bot/memory/passing_the_time.py). Whole-line shapes only, so a request with a vehicle or a
    # place in it ("what can i do on the bus") stays with the module that answers it.
    company = passing_the_time.reply(text, memory)
    if company:
        return company
    # Getting older comes up as ordinary chat, and there was nothing to answer it with: "i feel
    # old" met the shrug, "im past it" was echoed back, and "im getting old" was answered as a
    # length of time ("Nice. How long do you reckon it'll take?"). Read whole, before the small
    # news and before the timers (bot/memory/the_years.py).
    years_turn = the_years.reply(text, memory)
    if years_turn:
        return years_turn
    # A limit on what somebody can do - "she cant walk far", "two adults, one is in a wheelchair",
    # "my dad cant walk far so we need somewhere flat" - is a fact about the plan, and it used to
    # be read as a report about the person's health ("How long has that been going on with your
    # mum?"), echoed back word for word ("Got it - two adults, one is in a wheelchair."), or met
    # with "keep going" (bot/memory/limits.py). Read whole, before anything that answers a request.
    a_limit = limits.reply(text, memory)
    if a_limit:
        return a_limit
    # "not great thanks" is a mood with a courtesy word on the end, and the feeling is the line:
    # read whole it was a thank-you, and the bot told somebody who had just said they were not
    # great "good luck with it". Only a short line whose remaining words name a mood is read
    # this way, so a thank-you on its own and one on the end of a question are unchanged.
    thanks_off = _a_thank_you_taken_off(clean, memory)
    if thanks_off and _a_plain_good_answer(thanks_off, memory):
        # "how are you" / "great thanks" is how they are, not a result: read on, the one bare good
        # word reached the news reader and the bot said "That's great news! Make the most of it."
        # to somebody who had just told it how they were. The positive pool answers it, which is
        # where a bare "fine" and "good" land already.
        return _reply("positive", memory, _name(memory))
    if thanks_off:
        clean = thanks_off
        text = thanks_off
        tokens = _tokens(clean)
    # "no thanks at all", "not at all" and "no thanks at all then" say the no more firmly, and
    # "at all" is that firmness rather than a word of the line: "all" is in the thanks filler but
    # "at" is not, so a bare "no thanks at all" failed the short-line test, `chat` said nothing,
    # and the greeting answered "Got it. Is there anything you'd like a hand with?" where "no
    # thanks" on its own gets "Fair enough." No reading below looks for the word "at".
    tokens = _without_the_at_all(tokens)
    # Straight after a reply about lost contact, "what can i do about it" is asking for the step,
    # and the answer has to be about getting back in touch (see _after_lonely below).
    step = _after_lonely(clean, memory)
    if step:
        return step
    # And straight after the lost-thread question, a line that names nothing of its own is the
    # rest of the thing they could not follow (see _after_a_lost_thread).
    picked_up = _after_a_lost_thread(clean, memory.get("understood"), memory)
    if picked_up:
        return picked_up
    still_at_it = _laughing_still(clean, memory)
    if still_at_it:
        return still_at_it
    laughing = _laughing_at(clean, memory)
    if laughing:
        # A person laughing at something is answered before the body and the feelings below: "im
        # crying laughing at this video" is the word "crying" in a line that is not grief, and
        # every one of these was answered either as a feeling or with a stock line that fits any
        # message (see `_laughing_at`).
        return _reply(laughing, memory, _name(memory), clean)
    # "nothing helps" said straight after they told us how they are is not a request for the
    # same advice again: it says the advice did not reach it, and that is what the reply answers.
    nothing = _nothing_helps(clean, memory)
    if nothing:
        return nothing
    # A line that only rules something out is answered inside the last answer: "my dog pulls on
    # the lead" / "no treats" was answered with the treat again, because "treats" is a food word
    # and the dish entries took the turn. It is read before the illness and feeling readers too:
    # "no pills" after a sore back is a limit on the painkillers in the answer, not a symptom.
    held = _a_limit(text, memory)
    if held:
        return held
    # The verdict they have already reached on their own life is the thing to answer, and the
    # fact in front of it is only what it is about. Read before the feeling readers below, since
    # the words of the fact are what they would take ("i live alone" is not a lonely line when
    # the rest of the line says "and love it").
    own_call = _their_own_call(clean)
    if own_call:
        return _reply("own_call", memory, _name(memory), clean)
    # Being ill is not a mood to be talked through: the sad pool's "a walk and someone to talk to
    # usually help" is the wrong advice for a cold, and it was the answer to "im coming down with
    # a cold" because "down" is a sad word.
    # A feeling said through the body is not the body: the pools for a stomach ("plain toast",
    # "a bug passing through") answer a person naming guilt with advice for an illness nobody has.
    # Read before the illness branch and before the "still on them" readers, because "when i think
    # about it" is not someone they are missing either.
    body_feeling = _body_is_a_feeling(clean)
    if body_feeling:
        return _reply(body_feeling, memory, _name(memory))
    read = memory.get("understood") if isinstance(memory, dict) else None
    asks = isinstance(read, dict) and read.get("kind") == "question"
    symptom = COLD_SYMPTOM.search(clean)
    # The cold pool is the right one when the line names a throat, a cough or a running nose -
    # the parts honey and lemon is honest for - and the plain illness pool for everything else.
    cold = bool(symptom or COLD_NAMED.search(clean))
    # A part of the body the line names ("i have a migraine", "my throat hurts") picks the pool
    # over both: the cold's lines answer the wrong illness for a head, a stomach or a fever. The
    # reading is the shared one (bot/understanding/body.py), so this only chooses words.
    part = read.get("body") if isinstance(read, dict) else None
    # The line that is only the complaint is the person's own illness too, with the "i have"
    # cut off the front: "cough", "flu", "sore throat and a cough".
    bare = bool(COMPLAINT_ONLY.match(clean)) and not asks
    if (ILL_SELF.search(clean) or (symptom and not asks) or part or bare) \
            and not SICK_DEED.search(clean) and not BODY_BEFORE_AN_EVENT.search(clean):
        # a cold sore is the knowledge base's answer, not a cold to be talked through - unless a
        # cold is said in the same line ("i have a cold and a cold sore"), which is still a cold
        if (COLD_SORE.search(clean) and not COLD_SYMPTOM.search(clean)
                and not COLD_SORE_FEELING.search(clean)):
            if not COLD_NAMED.search(COLD_SORE.sub(" ", clean)):
                return None
        # "i feel sick that i lied to her" is guilt about a deed, not a bug: the illness pool
        # would tell someone ashamed of themselves to sleep it off.
        if part and "ill_" + part in REPLIES:
            return _reply("ill_" + part, memory, _name(memory), text)
        if cold and _the_same_cold_again(clean, memory):
            return None
        # The first day of a cold is comfort and an early night; one that has lasted is a
        # different question ("ive got a cough that wont go away"), and the cold pool is the
        # right one only when the line names a throat, a cough or a running nose.
        if says_it_has_lingered(clean, illness=True):
            return _reply("ill_lasting", memory, _name(memory), text)
        return _reply("cold" if cold else "ill", memory, _name(memory), text)
    if reads_like_a_symptom(clean) and says_it_has_lingered(clean) \
            and not SICK_DEED.search(clean):
        # "ive been feeling dizzy for a week should i worry" is a question about a body that has
        # been going on, and the worry pool answers the mood while dropping the body ("say the
        # worst case out loud"). This module has nothing to add to the answer for a thing that
        # has lingered, so it says nothing and the composer's own line for it is the reply.
        return None
    # An apology for the way the chat is going is answered with what the chat is holding, before
    # the readers below take the word in it ("keep" in "sorry i keep jumping about") for a habit
    # to fix. It answers only when the store can name two things, so no turn that used to get an
    # answer loses one here.
    scattered = _chat_scatter(clean, memory)
    if scattered:
        return scattered
    understood = memory.get("understood") if isinstance(memory, dict) else None
    # The reading is of the line as it was typed, and `plain` is that line with its misspellings
    # put right - so it can only stand in for the words of the line it was read from. A retry is
    # a different string (the normalised one), and reading it through the typed line's `plain`
    # puts the slips back: "i dont really know why" is not the not-coping line on the words as
    # typed, and it was its retry "i do not really know why" that did read as one, until
    # `_as_said` replaced the repair with the line it was meant to repair.
    said = _as_said(clean, understood) if as_said else clean
    # While an emergency is still the thread, the careful continuation is what the person
    # needs, and it only gets the turn when nothing else speaks. A cheerful hello or a
    # "you there?" does not take it; a real answer about how they feel still does.
    live_emergency = _safety_thread(memory)
    if isinstance(understood, dict) and understood.get("presence"):
        if live_emergency:
            return None
        # "still there" one turn after an answer is the thing again, not someone checking the bot
        # is present: "i have a headache" then "still there" was answered "Still here. What's
        # up?" and the headache went out of the chat. The store reads that line as the report it
        # is, so the presence pool keeps out of it.
        from ..memory import tried as not_moved
        if not_moved.still_going_on(text, memory):
            return None
        # Someone checking the bot is still there wants it to carry on, not to reset: the
        # presence pool says "go on" where the "here" pool asks what is up.
        return _say("presence", memory)
    if isinstance(understood, dict) and understood.get("intent") == "opening":
        return _reply("opening", memory, _name(memory))
    if (isinstance(understood, dict) and understood.get("asks_back") and len(tokens) <= 12
            and not live_emergency):
        # "not bad, and you?", "im fine thanks, yourself": the line answers how they are and
        # asks the bot the same thing in one breath. The reading called it news about them, so
        # the reply said neither how the bot was nor took the question - "Thanks for telling me
        # - I'm here if you want to dig into any of that". See kinds._asks_back.
        # Both readings of a low are used: the engine's sign ("not great, and you?") and the
        # module's own low words ("im shattered thanks, you?", "im fed up, and you"), because a
        # word like "shattered" is a low the engine scores 0 for.
        polarity = understood.get("polarity")
        low = (isinstance(polarity, int) and polarity < 0) or bool(_a_low_word(clean))
        return _reply("back_low" if low else "back", memory, _name(memory))
    met, plan = _just_met(memory)
    if met:
        said = _plan_clause(plan)
        if said:
            # A plan said as a whole clause ("you're getting married in june") needs the dash, or
            # the welcome reads "you're getting married in june sounds like a good one".
            join = " — that" if said.lower().startswith("you") else ""
            return "Hi " + met + " — good to meet you, and " + said + join + \
                   " sounds like a good one. What do you need a hand with?"
        # An introduction in front of something to answer is not a hello: "hi im jess, i cant
        # sleep" and "hi im dan, is it going to rain" were answered with the welcome alone
        # ("Nice to meet you, Dan. What can I help with?"), which answers neither half. The
        # reading already tells the two apart (`kind` is "greeting" only when the hello is the
        # whole line), so the welcome keeps the turn only then; otherwise the rest of the line
        # is answered and the hello rides on the answer (`greet_with`, in `respond` below).
        kind = understood.get("kind") if isinstance(understood, dict) else None
        if kind in (None, "greeting", "empty"):
            return _reply("meet", memory, met)
        memory["greet"] = met
    if len(tokens) <= 6 and _says_nothing_much(tokens, clean):
        return _reply("notmuch", memory, _name(memory))
    # The reading works out laughter itself, from the spellings people type rather than from the
    # word list here: "hahaha", "ha ha ha", "hahahaha" and a bare "ha" are the same laugh as
    # "haha", and each of them used to read as a statement ("Got it. Is there anything you'd like
    # a hand with?"). Only a line that is nothing but the laugh and its fillers takes the turn,
    # though: the reading calls any line with a laugh word in it a laugh, and "lol i forgot my
    # keys" is a lost-keys question with a laugh in front of it, not a laugh. The spellings come
    # from the reading's own lexicon, so "hahahaha" and "hehehe" count and "he" does not.
    laughed = (isinstance(understood, dict) and understood.get("intent") == "laugh"
               and 0 < len(tokens) <= 8
               and all(lexicon.is_a_laugh(t) or t in ACK_WORDS or t in THANKS_FILLER
                       for t in tokens))
    # A surplus of something is a line with a subject, not a nod: "i have too much mint" and
    # "i have too much chill" are five words that are all acknowledgement words in this file -
    # "mint" and "chill" are here because they also mean "im fine" - so the plain ack pool
    # answered a cooking question with "Fair enough." Whatever follows "too much of" is a thing
    # the person has, so the quantifier takes the line out of the pools.
    chatty = laughed or (len(tokens) <= 8
                         and not SAYS_TOO_MUCH.search(clean)
                         and all(t in ACK_WORDS or t in LAUGH_WORDS or t in THANKS_FILLER
                                 for t in tokens))
    if _is_bye(tokens) or _ending_bye(clean, memory):
        return _reply(_bye_kind(tokens), memory, _name(memory))
    # A thank you said to a name ("thanks love", "thanks pet", "thanks sunshine") is still a
    # thank you, and so is one with a sound in front of it ("oh thanks"). Neither the name nor
    # the sound is part of what the line says, but the word lists above have no entry for
    # either, so "thanks love" failed this test and fell through to the pool for a declined
    # offer: "Fair enough." The words that are not part of the line come from the shared
    # reading, so the module and the reading agree on which ones they are.
    bare = [token for token in tokens
            if token not in ADDRESSED and token not in THANKS_NOISE]
    # A hedged answer to "how are you" before the thank-you branch, because the manners on the end
    # of it ("been better thanks", "so so thanks") are what made the thanks pool answer the state:
    # "been better thanks" got "You're welcome - glad that helped" and "so so thanks" got "No
    # problem at all." The whole line has to be the hedge, so "could be worse than the last one"
    # and "getting there with the forms" keep whatever they were.
    if _a_hedge_answering_the_question(memory):
        if HEDGED_LOW_LINE.match(clean):
            return _reply("hedged_low", memory, _name(memory))
        if HEDGED_OK_LINE.match(clean):
            return _reply("hedged_ok", memory, _name(memory))
    if _is_thanks(bare) or _is_thanks(tokens) or _is_thanks(_without_the_nod(tokens)):
        if ANSWERS_HOW_ARE_YOU.match(clean) and not THANKS_FOR.search(clean):
            # Answered here rather than left to fall through: past this branch the line is read as
            # news, and "yeah im good thanks" after "how are you" got "Alright then — good luck
            # with it." about a plan it never named.
            return _reply("positive", memory, _name(memory))
        return _reply("thanks", memory, _name(memory))
    moved = limit.move_after_a_limit(clean, memory)
    if moved:
        # "whats the first thing to change" right after a limit reply is the first step the limit
        # left, not a new search: the answer that holds it is no longer the turn on the screen.
        return moved
    limited = limit.reply_for(clean, memory)
    if limited:
        # "i ran out of oven cleaner", "ive got a cat": a limit on the answer just given is read
        # from that answer's own steps, not by asking the knowledge base again with the limit on
        # the end of the question (`bot/memory/limit.py`).
        return limited
    piled = pile.reply_for(clean, memory)
    if piled:
        # "ive got too many", "weve got plenty", "ive got about thirty": the size of what the
        # person is holding is not a day that happened, and the account-of-the-day pool answered
        # every one of them with a warm question about a day nobody had. A pile is cut down to a
        # shortlist instead (`bot/memory/pile.py`), and the line that follows names the thing.
        return piled
    total = portions.the_total_for(clean, memory)
    if total:
        # The reply before this one asked how many were coming so it could do the sums; this is
        # the count, and the total is worked out of the figure the answer gave.
        return total
    portion = portions.reply_for(clean, memory)
    if portion:
        # "how much pasta for 4 people" / "how many does that serve": the answer on the screen
        # already says who it is for, so the line is read out of that answer rather than asked of
        # the knowledge base again (`bot/memory/portions.py`).
        return portion
    came_back = returned.pool_for(clean, memory)
    if came_back:
        # "top it up and it came back after a week": the answer has not held, and it already names
        # the step for that point, so that sentence is the reply rather than an echo
        # (`bot/memory/returned.py`). It is a short form of the answer handed back, so the store
        # counts it as said: the same sentence must not come round a third time (`repeat.py`).
        repeat.handed_back(memory, returned.the_whole_of_it(clean, memory) or came_back)
        return came_back
    not_worked = tried.pool_for(clean, memory)
    if not_worked:
        # "i tried that and it didn't work", "still blocked": the last answer had its go, so the
        # next step is who does it for a living, or what the thing is doing now. Never the same
        # instructions again (`bot/memory/tried.py`).
        return pick(not_worked, memory)
    attempt = remedy.reply_for(clean, memory)
    if attempt:
        # "my back hurts" / "i tried a hot bath": the answer had its go and the thing they tried is
        # said back as a question about whether it helped, not "Good to hear. What was the best
        # bit?" (`bot/memory/remedy.py`).
        return attempt
    acted = tried.acted_pool(clean, memory)
    if acted:
        # "what should i say to her" / "i already told her that": the advice was used, so ask
        # how it went instead of falling to "Got it. Is there anything you'd like a hand with?".
        return pick(acted, memory)
    next_step = step_after.reply_for(clean, memory)
    if next_step:
        # "how do i get red wine out of a cream carpet" / "it happened last night and i blotted
        # it": they have said which step of the answer they are on, so the next bit of that same
        # answer is what a friend gives back, not "Thanks for telling me - I'm here if you want
        # to dig into any of that" (`bot/memory/carried_on.py`).
        return next_step
    verdict = _about_the_night_out(clean, tokens, memory)
    if verdict:
        return verdict
    # "does that get easier", "i never know when to stop": the line before this one was about the
    # hours they work, and the answer is about that week rather than a search hedge (the reading
    # lives in bot/memory/hours.py, the wording in bot/memory/ack.py's pools).
    the_hours = hours_after.answer_for(clean, memory)
    if the_hours:
        return the_hours
    conversation = _conversation(clean, tokens, memory)
    if conversation:
        return conversation
    grumble = _work_grumble(clean, tokens, memory)
    if grumble:
        return grumble
    if KICK_MYSELF.search(clean):
        return pick(AT_MYSELF_REPLIES, memory, clean)
    if _is_greeting(tokens):
        return _reply("greeting", memory, _name(memory))
    if _is_howareyou(tokens):
        return _reply("howareyou", memory, _name(memory))
    joke = _joke(clean, tokens, memory)
    if joke:
        return joke
    other = _other_feeling(clean, memory)
    # Someone else being fed up ("my husband is fed up with the commute") is about them, so it
    # is their reply; this branch is only for the person writing.
    # "fed up" on its own is in the phrase too: the bare line names nothing, so it belongs in
    # the branch that answers "nothing named" with the venting pool, not in the annoyed pool's
    # "Walk it off for ten minutes before you reply to anyone", which is advice for a quarrel.
    # `said` is the line with the reading's spelling repairs put in, so a slip typed at speed
    # still reaches these matchers: "im fed up wiv my job" and "im fed up of my jobb" are the
    # lines this branch exists for, and `clean` has not been repaired.
    fedup_at = re.search(
        r"\b(done with|fed up|browned off|peeved|sick of|tired of|had enough|"
        r"had it with)\b", said)
    named = OTHER_PERSON.search(said)
    # "my mum is sick of me" is not the user being fed up, so the person named before the
    # phrase keeps the line out of the user's own annoyed reply.
    # A denial that goes on to say how they are is a correction, not a denial: "im not tired of
    # it, im just bored" names the feeling in the second half, so the line belongs to that
    # feeling and not to the pool that asks what is really behind it.
    corrected = (FED_UP_DENIED.search(said)
                 and _bare_feeling(STATE_WHEN.sub(" ", FED_UP_DENIED.sub(" ", said))))
    if (not other and fedup_at and not corrected
            and not FED_UP_ABOUT_THE_BOT.search(said[:fedup_at.start()])
            and not FED_UP_WITH_A_PERSON.search(said)
            and not (named and named.start() < fedup_at.start())):
        if FED_UP_DENIED.search(said):
            # A denied one is not a fed-up line, and skipping the branch is not enough: the line
            # then falls through to the word inside it, so "im not sick of it" was read as an
            # illness and told to see a doctor, and "i never said i was fed up" was asked how
            # long it had been going on. The denial is the line, so it gets the pool for one.
            return _reply("not_feeling", memory, _name(memory))
        if AT_MYSELF.search(clean):
            # "im fed up with myself" is the same line as "im so annoyed with myself", and it used
            # to be answered here before the feeling block below could read it, so the one line
            # the change is about ("walk it off before you reply to anyone") still landed.
            return pick(AT_MYSELF_REPLIES, memory, clean)
        # Fed up with one thing is annoyance; fed up with everything is low mood, and the
        # annoyed pool's "walk it off" is the wrong reply to that.
        if _not_coping(clean):
            # A fed-up phrase with the object taken out - "ive had enough of living", "i dont
            # want to go on" - is the not-coping disclosure and not a row with somebody. The
            # annoyance pool's "walk it off for ten minutes before you reply to anyone" was
            # the answer, which is the worst line in the bot for what was said.
            return _reply("not_coping", memory, _name(memory))
        # Fed up with everything, or with their life or with living, is low mood, and "what
        # would have to change?" is the wrong question to ask about it. `im tired of living`
        # and `im fed up of my life` used to reach the annoyed pool here.
        if FED_UP_WHOLE_OF_IT.search(said):
            # The low-mood pool for a whole life, not the plain sad one: "im fed up of my life" and
            # "im tired of trying" are the disclosure the not-coping pool is written for, and the
            # sad pool's "a walk and someone to talk to" is advice for a bad day. `im tired of
            # living` and `im tired of being alive` are the same words, so `alive` is in the
            # pattern too and neither reaches the question about the thing named.
            return _reply("not_coping", memory, _name(memory))
        # The thing they are tired of is named in the line, and it is the line: "im fed up of my
        # job" was answered "Annoying. Walk it off for ten minutes before you reply to anyone",
        # which is advice for a row with somebody. Asking about the thing is the reply the
        # same pool already gives for another person ("he is fed up with the commute"), so the
        # line the person wrote gets it too, in their own words.
        _the_weight_said(memory, "annoyed")
        tired_of = _fed_up_with(said)
        if tired_of:
            # "being ill" does not go in a shape that puts the thing straight after "of" or "with",
            # so those templates are taken out of the running for a gerund ("fed up of being ill"
            # asked "being fed up with being ill wears a person down more than a late night does",
            # and "tired of being ill is its own kind of tired" says it twice).
            if tired_of.startswith("being ") or tired_of.startswith("having "):
                options = list(FEDUP_GERUND_SAFE)
            else:
                options = list(FEDUP_REPLIES)
            lead = FEDUP_LEAD.get(_fedup_phrase(said, fedup_at.start()), "Being tired of")
            return pick([option.format(thing=tired_of, obj="you", lead=lead)
                         for option in options], memory, seed_text=text)
        # "im so fed up" names nothing, but there is nobody to cool off at either: the venting
        # pool is the one that asks how long it has been going on.
        return pick(REPLIES["venting"], memory, seed_text=text)
    if MISS_ME.search(clean):
        return pick(MISS_YOU_REPLIES, memory, seed_text=text)
    if STILL_ON_THEM.search(clean):
        return _reply("missing", memory, _name(memory))
    if _fond_of_the_bot(clean):
        return pick(FOND_REPLIES, memory, seed_text=text)
    if (KIND_TO_ME.search(clean) or _praised_the_answer(clean)) and not DOUBT_FRAME.search(clean):
        return pick(KIND_REPLIES, memory, seed_text=text)
    # The same reason as `_news` above: a judgement word that arrived with a slip in it is the
    # judgement word the pools are written for, so the line is read as it was meant.
    judgement = _judgement(_as_said(clean, understood), tokens)
    if judgement:
        # The new pool is picked off the line itself: "i feel like a bad dad" and "i feel like a
        # fraud" are different things to say to yourself, and one line back to both reads as a
        # script. The pools that were already here keep their pick.
        seed = clean if judgement in ("own_harsh", "own_described") else ""
        return _reply(judgement, memory, _name(memory), seed=seed)
    reaction = _reaction(clean, tokens, memory)
    if reaction:
        # The line is the seed, so "oh no" and "thats grim" in two chats do not come back as the
        # same sentence just because both were the second turn of their conversation.
        # An agreement is the one case where the line says nothing of its own - "me too" and
        # "same here" are the same words whatever they agree with - so the thing agreed with is
        # half the seed, or every chat that agrees comes back with one sentence.
        seed = clean if not reaction.startswith("agree") else clean + "|" + _news_before(memory)
        return _reply(reaction, memory, _name(memory), seed)
    if VENTED.search(clean):
        return _reply("venting", memory, _name(memory))
    # A line asking for the news is not the news: "got any good news" and "what's the good news"
    # were congratulated for asking, and the hedge that is left when they are not news is no answer
    # to small talk either. The ask gets the nod a friend gives it, and the branch below keeps
    # every line that reports news (bot/compose/goodnews.py, `asks_for_news`).
    if asks_for_news(clean) and not (
            ANY_WORLD_NEWS_ON.search(clean)
            and not fallback.LIVE_NOT_WORLDS.search(clean)):
        return _reply("no_news", memory)
    if GOOD_NEWS_SAID.search(clean):
        # The words "good news" are not the news: "i feel nothing after good news" and "we got
        # good news and i feel flat" name the news and say it did not land, and the happy pool
        # ("Good! That's a nice thing to hear.") answers a person who has just said the opposite.
        if NOT_LANDED.search(clean) or any(
                negated(clean, word) for word in NOT_GLAD_WORDS):
            # "im not happy about the good news" is the same line: the good feeling is named and
            # denied in front of the words "good news", which is what `negated` reads.
            return _reply("good_news_not_landed", memory, _name(memory), seed=clean)
        return _reply("happy", memory, _name(memory))
    about = _about_bot(clean, memory.get("understood") if isinstance(memory, dict) else None,
                       memory)
    if about:
        return pick(about, memory)
    if isinstance(memory, dict) and isinstance(memory.get("understood"), dict) \
            and memory["understood"].get("about_bot_kind"):
        # The reading worked out that the whole line asks about the bot ("who is this", "who am
        # i talking to"), and this module's own table has no pattern for that shape. The pool
        # that answers who the bot is lives in the composer, so the turn goes there rather than
        # falling through to the knowledge readers, where "talking" and the work of the last
        # turn reached the presentation entry and answered "who am i talking to" with slides.
        return None
    opinion = _opinion(clean, tokens, memory)
    if opinion:
        return opinion
    worry_someone = _worry_someone(said, memory)
    if worry_someone == "pass":
        return None
    if worry_someone:
        return pick(worry_someone, memory)
    early = _early_start(clean, memory)
    if early:
        return pick(early, memory)
    row = _a_row(clean, memory)
    if row:
        return row
    row_next = _a_row_next(clean, memory)
    if row_next:
        return row_next
    row_ending = _a_row_ending(clean, memory)
    if row_ending:
        return row_ending
    # Called here rather than at the point of use: it also writes down which trouble the line
    # shows (`memory["person"]["trouble"]`), and the short ask two turns later leans on that note
    # even when this turn's reply came from the knowledge base ("she keeps forgetting where
    # things are in the kitchen" is answered by an entry, and "what should i look out for" then
    # had nothing to lean on).
    someone = _about_someone(clean, memory)
    follow_up = _context_follow_up(clean, memory)
    # "Should i be worried" and "is that normal" about somebody the thread has already named a
    # trouble for is answered by that trouble's own line, not by the pool for a worry in general:
    # the pool asks the person what would settle it, which is the question they just asked, while
    # the line says which signs are the ones to act on and what the GP can check. Only those asks,
    # and only the "is it ordinary" lines, so every other follow-up keeps its turn.
    if someone and someone in set(SOMEONE_NORMAL.values()) and (
            SOMEONE_IS_IT_NORMAL.search(clean) or SOMEONE_NEXT_STEP.search(clean)):
        return someone
    if follow_up:
        return follow_up
    if other and len(tokens) <= 16:
        # A line that is news with a name in it is answered by the news pool, not by a feeling
        # word that happens to sit inside it. "my son was sent down for two years" read "down" as
        # the son's low mood and "my son" as the person, and answered a prison sentence with
        # "That's a lot for him to carry. Small things done together often help more than words."
        # The reading is the one in `compose/badnews.py`, so the turn goes where that reading
        # already points instead of to a table about somebody else's feelings.
        if not badnews.reads_as_news_with_a_name(clean):
            return _someone_reply(memory, *other, said=said)
    standing = _standing(clean, memory)
    if standing:
        return standing
    bare = _bare_feeling(STATE_WHEN.sub(" ", clean))
    read_as = understood if as_said else None
    feeling = _feeling(clean, read_as, bare=bare)
    if not feeling and KEEPS_HOW_THEY_ARE.search(clean) and not _answers_knows(text, memory):
        # "i keep crying" is how the person is, not a habit to troubleshoot ("i keep losing my
        # keys" is). The knowledge base is asked first because a line it answers has a better
        # reply of its own: "i keep crying at work" wants the crying-at-work entry.
        feeling = _feeling(clean, read_as, bare=bare, kept=True)
    if feeling in MOOD_KINDS and _going_on(clean):
        # "i feel anxious all the time" is the one sentence the anxious pool cannot answer: it
        # presumes an event coming up. The persistence is what there is to answer. Which pool
        # says it depends on how much the line said: a line that gives the length or the
        # frequency has earned the weeks-of-it answer, and one that only says it keeps
        # happening ("i keep crying") gets the pool that does not put a length in its mouth.
        feeling = "ongoing" if GOING_ON_LONG.search(clean) else "recurring"
    # A long line that says how the person feels is still a feeling line ("my nan is 84 and
    # just moved into a care home, i feel guilty"), so the length guard only applies to a
    # question, where something else is being asked for.
    asks = isinstance(understood, dict) and understood.get("kind") == "question"
    if feeling == "carrying":
        # A card that answers a load line says more than a pool does, so it keeps the turn; on
        # every other load line the not-coping pool is the right one, because its "Is there
        # anyone around you who knows it's like this?" is the question this person needs and a
        # mood's advice ("a walk and someone to talk to") is not.
        feeling = None if _answers_knows(text, memory) else "not_coping"
    if feeling in MOOD_KINDS and A_VERDICT_ASKED.search(clean):
        # "would i be mad to sell" asks for a verdict on a choice, so the word is the judgement
        # and not a mood: the decision pool is the reply, and the annoyed pool's "walk it off
        # before you reply to anyone" is advice for a quarrel nobody had.
        feeling = None
    if feeling in MOOD_KINDS and _answers_knows(text, memory):
        # A named condition is a card's line, not a pool's: "i feel depressed" wants the signs and
        # the next step, and the sad pool's "a walk and someone to talk to" is written for a
        # passing low. The knowledge base decides - it is asked on the words the person used, and
        # an entry that answers the line has more to say than any mood pool does.
        feeling = None
    if feeling == "rough_day" and asks and _answers_knows(text, memory):
        # "im hungover what should i do" names a state and then asks what to do with it: the
        # entry that answers it (water and sleep, a pint before bed) says more than the pool,
        # which is written for the line that names the state and stops there.
        feeling = None
    # "i feel like im not doing enough" has no feeling word in it, so the reply comes from the
    # comparison the person drew rather than from FEELINGS (see _feel_like). A comparison the
    # patterns can name (too little done, too much landed on them, nobody on their side) is more
    # specific than a word like "down" that a line can contain by accident, so it goes first;
    # the plain "i feel like ..." reply waits until no named feeling has claimed the line.
    like = _feel_like(clean)
    if like and _a_feeling_riding_on_the_thread(clean, memory):
        # A feeling tacked onto the turn before ("my boss had a go at me" / "i just feel like i
        # cant win") is about what they have just said, so the answer that met that subject a
        # turn back fits the pair better than naming the mood back at them.
        like = None
    if like and like != "feel_like":
        return _reply(like, memory, _name(memory), clean)
    if someone and asks and len(tokens) <= 22:
        # A short question about the trouble already on the table is that trouble's question,
        # not the asker's own mood. "my mum keeps forgetting things" then "should i be worried"
        # was answered from the worry pool ("Worry like that is usually mostly 'what if'") the
        # moment the knowledge base stopped covering that ask: the person had asked whether the
        # thing they had just described was worth worrying about, and nothing of the mother
        # survived into the reply. `_about_someone` answers exactly this shape, so it gets the
        # turn before a pool written for the asker's nerves.
        return someone
    if feeling and (bare or _about_the_person(understood)) and (
            chatty or len(tokens) <= 12 or not asks):
        if feeling in ("ongoing", "recurring"):
            # The person's own words choose: "i feel anxious all the time" and "i feel angry all
            # the time" are not the same sentence said twice.
            _the_weight_said(memory, feeling)
            # Said a second turn running, the advice itself is the problem: the GP was the answer
            # to the last line already, so help with the notes it asked for instead of saying it
            # again. `mood_advice` holds the turn index the advice was given on, which is this
            # one now, so the third line of the same kind keeps helping rather than repeating.
            turns = memory.get("turns")
            turn_no = len(turns) if isinstance(turns, list) else 0
            if memory.get("mood_advice") == turn_no - 1:
                memory["mood_advice"] = turn_no
                return pick(list(REPLIES["recurring_next"]), memory, clean)
            memory["mood_advice"] = turn_no
            return pick(list(REPLIES[feeling]), memory, clean)
        if feeling == "annoyed" and AT_MYSELF.search(clean):
            # Annoyed with themselves, not with anybody else: the pool above answers a quarrel,
            # and this one answers a person who is being hard on themselves. The line is the
            # seed so two chats do not open with the same sentence.
            return pick(AT_MYSELF_REPLIES, memory, clean)
        if feeling == "happy" and NOT_PROUD.search(clean):
            # "im not proud of what i did" is regret, and the happy pool would congratulate them.
            feeling = "guilty"
        elif (feeling == "happy" and PROUD_OF_MYSELF.search(clean)
              and not PROUD_OF_ANOTHER.search(clean)):
            # Pleased with themselves, not pleased about news: there is nothing coming up to ask
            # about, and the person is the one who did it.
            feeling = "proud"
        if feeling == "happy" and DOUBT_FRAME.search(clean) and _praised_the_answer(clean):
            # "i dont really think thats great" praises the last answer only to take it back, and
            # the happy word in it is not the person's feeling: the doubt is about the answer. The
            # warm close is refused above for the same reason, and without this the line fell
            # straight into the happy pool ("Good! That's a nice thing to hear."), which is the
            # warm close said louder. Kept to a line that is praising the answer, so a real good
            # feeling said with a doubt in it - "i cant believe how well that went" - is untouched.
            feeling = None
        if feeling == "confused" and isinstance(memory, dict):
            # The bot may have already answered the thing they are stuck on: "im confused" straight
            # after an explanation wants that line again in plainer words, which the repeat reader
            # (bot/memory/meant.py) does and a question about which bit cannot. Only a real hand-back
            # counts, so "nothing of mine to go back over yet" - the shrug this pool exists to
            # replace - is left to the pool.
            plainer = meant.answer_for(clean, memory)
            if plainer and plainer.lower().startswith(MEANT_LEADS):
                return plainer
        if feeling in ("happy", "anxious", "proud"):
            # The line chooses, so two different happy lines do not both get the same sentence on
            # their first turn of two different conversations.
            return _reply(feeling, memory, _name(memory), clean)
        # The pools whose lines are about the thing the person named take the line as the seed,
        # so two different weeks that drag are not answered with one sentence. `long_stretch` is
        # the same case: "this week is dragging" and "school holidays are too long" are two
        # different complaints and used to both get the pool's third line.
        return _reply(feeling, memory, _name(memory),
                      clean if feeling in ("not_coping", "bad_day", "tears",
                                           "long_stretch") else "")
    if like:
        return _reply(like, memory, _name(memory), clean)
    against = _against_me(clean)
    if against:
        return _reply(against, memory, _name(memory), clean)
    stuck = _stuck(clean, memory)
    if stuck and len(tokens) <= 16:
        # "could i be depressed, i cant be bothered with anything" is a condition named and then
        # a symptom of it: the knowledge base answers that line with the signs and the next step,
        # and the pool's "pick the smallest thing" answers only the second half.
        if not (stuck == "effort" and _answers_knows(text, memory)):
            kind = "stuck_" + stuck if "stuck_" + stuck in REPLIES else "stuck"
            if kind in ("stuck_eating", "stuck_sleep", "stuck") and LONG_SPAN.search(clean):
                # A run of days is a different turn from a bad appetite: the pool that says
                # "call someone today" is the one for it.
                for days in ("stuck_%s_days" % stuck, "stuck_sleep_days"):
                    if days in REPLIES:
                        kind = days
                        break
            return _reply(kind, memory, _name(memory))
    if _my_night(clean) and len(tokens) <= 18:
        # The line chooses, so "i keep waking up at 3" and "i was awake half the night" do not
        # get the same sentence on their first turn.
        return pick(list(REPLIES["stuck_sleep"]), memory, clean)
    someone = _about_someone(clean, memory)
    if someone and len(tokens) <= 22:
        return someone
    # Someone who says they do not know what to do, once something hard is already on the table
    # ("my wife left me" -> "i dont know what to do"), is asking for the next step rather than for
    # a shrug. The vaguer pools below answer it with "Sometimes it's everything at once. It can
    # stay unnamed.", and the fallback nods ("is there anything you'd like a hand with?"), which
    # is the one thing the person has just said they cannot do. bot/memory/stuck.py reads the line
    # before this one and names the first thing there is to do for that kind of news.
    #
    # It sits after `_about_someone`, not before it: "my mum has dementia" then "what do i do" is
    # answered there with the written note for the GP, which is the better answer, and a generic
    # pool of next steps must not take that turn off it.
    news = _news(clean, tokens, memory)
    if news:
        return news
    if _question_coming(understood):
        # The same pool main uses for the plainest of these ("quick question", "i have a
        # question"): a line that invites and opens in one breath, rather than the invitation
        # on its own.
        return _reply("opening", memory, _name(memory))
    thing = _their_thing(clean, tokens, memory, understood)
    if thing:
        return thing
    if SAY_SOMETHING.search(re.sub(r"\s+(?:though|tho)$", "", clean)) \
            and not ASK_WHETHER_TO_SPEAK.search(clean):
        return _reply("say_something", memory, _name(memory))
    if _says_dont_know(clean, tokens):
        return _reply(_idk_kind(memory), memory, _name(memory))
    # "and?", "go on", "tell me more" on the back of a knowledge answer is a request to carry on
    # with that answer, not a new line about the day: read as an intent it got "Alright then -
    # good luck with it", which closes a conversation the person was still in.
    carried_on = more.reply_for(text, memory) if isinstance(memory, dict) else None
    if carried_on:
        return carried_on
    plan = _intent(clean, tokens, memory)
    if plan:
        if plan in ("next_up", "next_rest", "next_act"):
            # Two different lines should not get the same short sentence, so the person's own
            # words choose: "im going to bed early" and "im going to work now" are not the same
            # thing said twice.
            return pick(list(REPLIES[plan]), memory, clean)
        return _reply(plan, memory, _name(memory))
    # A bare "is that bad" / "what should i do" about the thing just explained is answered from
    # that explanation, not with "good luck with it" or a search hedge: the verdict, the first
    # step and the condition are all already in the bot's own line.
    # The reading the person is looking at ("the gauge says 0.5" after the boiler answer) is
    # checked against the range the bot's own line stated, because the echo only says the number
    # back: whether it is the number is the whole of the question.
    reading = reading_reply.reply_for(clean, memory)
    if reading:
        return reading
    # A doubt nobody ruled on ("is that bad", "is that ok", "is that enough") is still a
    # question, and an acknowledgement is not an answer to one.
    #
    # One doubt is not about the thing at all: a question on top of an answer that opened with a
    # call to get something seen ("get it checked", "see your GP", "ring 111") is asking whether
    # the call was fussing, and it was not. The composer's own line for a doubt over an
    # instruction answers that one as a scale it cannot put on the thing ("Hard to put a scale on
    # it. Doing the thing above is what makes the difference"), which leaves the person who asked
    # "is that ok" about a referral still unsure whether to go. So the narrower reading is asked
    # first, from `bot/compose/doubt.py`, and the composer keeps every other doubt. Asked here, in
    # front of the verdict, on purpose: below it the line is already answered and this reading
    # never runs.
    doubted = doubt_reply.reply_for(clean, memory) if isinstance(memory, dict) else None
    if doubted:
        return doubted
    verdict = verdict_reply.reply_for(clean, memory) or verdict_reply.next_step(clean, memory)
    if verdict and verdict not in verdict_reply.QUESTION_BACK_LINES:
        return verdict
    # The next step, asked for in as many words after a comfort line, is the thing to give: the
    # verdict helper had no advice to take it from because the last reply carried none. Handing
    # the bot's own question back is what is left when nothing behind it can be handed on, and a
    # rough day does have a first step - so the step is tried first and the question back is what
    # happens when even that has nothing. The comfort set is the fallback's as well as this
    # module's: "work was awful today" is answered by the fallback's rough-day line, and the step
    # after it is still this module's turn.
    step = step_when_low(clean, memory, FEELING_SAID | fallback.COMFORT_SAID)
    if step:
        return step
    if verdict:
        return verdict
    # "is that alright" after the bot has said no to a thing is about that no, not a line to
    # agree with: the ack pool answered it with "Sounds good.", which is the bot talking itself
    # out of its own answer. The verdict holds, with the reason it gave.
    held = thread.checking_the_verdict(clean, memory) if isinstance(memory, dict) else None
    if held:
        return held
    # "is that right" after a fact the bot gave is about that fact: the ack pool answered it with
    # "Alright then - good luck with it.", which leaves a person who was unsure still unsure.
    checked = thread.checking_a_fact(clean, memory) if isinstance(memory, dict) else None
    if checked:
        return checked
    judged = _judged(clean, memory)
    if judged:
        return judged
    # "help", "help me": the whole line is a request for help and nothing else, so it is answered
    # as one before the acknowledgement pools below take it for a nod.
    if "help" in tokens and all(t in HELP_ONLY for t in tokens):
        # ...unless the thread is carrying something heavy, where the nod-after-news line ("No
        # rush. That can just sit there for now.") is what a person wants and a question about
        # what they are stuck on is one more thing to answer.
        nod, nod_seed = _the_nod(memory)
        if nod == "ack":
            return _reply("help_ask", memory, _name(memory), clean)
    # The two-word ask for a next step - "now what", "what now" - after a job that has just ended.
    # It falls past every pool below, because they are written for the longer ways of saying it
    # ("i dont know what to do", "where do i start"), and it landed on "There is nothing in this
    # to look up. Tell me what has to happen next": the same hard news, answered as a shrug. The
    # job's own first step is the answer, and it is the pool the longer ask already reaches.
    job_step = _the_ask_after_a_job_that_went(clean, memory) if not live_emergency else None
    if job_step:
        return job_step
    # A line that asks for the next step after something hard ("i dont know what to do") is read
    # here, before the short-line pools, because "Sometimes it's everything at once" is the shrug
    # it is asking past. The reader that answers it out of the answer already on the screen goes
    # first: after "my boyfriend dumped me" the reply to look at is that answer's own first step
    # ("One thing to do first: Tell two people today"), and the neutral pool in its place throws
    # the specific advice away for the generic one.
    steps = stuck_line.pool(clean, memory) if not live_emergency else None
    if steps:
        again_steps = repeat.answer_for(text, memory) if isinstance(memory, dict) else None
        if again_steps:
            return again_steps
        return pick(list(steps), memory, clean)
    # An ask that points back at something they said is never a courtesy line: "sorry, how long
    # did i tell you the headaches been going on" was read as an apology about a rant, because
    # "sorry ... going on" is what SORRY_TALK looks for, and answered "No need to apologise" when
    # the four days they gave at the top of the chat was the whole answer. The reader that has
    # the figure sits in front of the short-line pools for the same reason the step reader does:
    # the line is a question about the chat, not a remark about the week.
    if isinstance(memory, dict) and repeat.A_TOLD_BACK.search(clean):
        told = repeat.the_figure_they_gave(text, memory)
        if told:
            return told
    short = _short_talk(clean, tokens, memory)
    if short:
        # The load pool is all advice, so the line picks among it: two people worn out by two
        # different weeks should not be handed the same sentence, and the same line always gets
        # the same one. The other short-line pools keep their turn-based choice.
        if short == "again_what":
            # A bare "again" is two things: after an answer it is the answer again, and
            # anywhere else it is the news that it happened once more, which neither assumes
            # the worst nor shrugs.
            steps = _the_steps_again(memory)
            if steps:
                return steps
        return _reply(short, memory, _name(memory), clean if short == "overloaded" else "")
    # A question that names nothing ("what do i do?", "and now?", "what should i look for?")
    # asks for the thing just said: answer it again in short form rather than hedge.
    again = repeat.answer_for(text, memory) if isinstance(memory, dict) else None
    if again:
        return again
    # "what do you mean?" on its own points at the line just given: the bot meant the first thing
    # it said (or the question it asked), and a search hedge reads as if it had said nothing.
    what = meant.answer_for(clean, memory)
    if what:
        return what
    heavy = _the_heavy_line(memory) if _a_bare_acknowledgement(clean) else ""
    if heavy:
        # "i lost my job" / "cool" was answered "Glad to hear it." and / "ok" was signed off with
        # "good luck with it". The turn after something hard is not the place for either, so a
        # line that only takes it in gets the nod-after-news pool main already has, seeded on the
        # line the news was in so two different threads do not get the same sentence.
        return _reply("nod_after_news", memory, _name(memory), heavy)
    if _a_plain_good_answer(clean, memory):
        # "fine", "good", "not bad" on their own answer how they are the same way "im fine"
        # does; this sits where the ack pool is reached, so a plan or a decline keeps its reply.
        return _reply("positive", memory, _name(memory))
    if HOW_THEY_ARE_LINE.match(clean) and not _denies_a_good_word(tokens):
        # "im doing alright" and "im doing well" say how somebody is exactly the way "im
        # alright" and "im well" do, and neither was chatty enough for the pool that answers
        # them: "im doing alright" was read as a plan ("Get stuck in. What's the first bit?")
        # and "im doing well" got the stock "I'm listening - say more if it helps". The frame is
        # the verb people put in front of the good word and the measure words that come with it,
        # so "im doing the washing" is still the washing and "im doing badly" is still bad.
        return _reply("positive", memory, _name(memory))
    if re.search(r"\bnot (?:too |half )?bad\b", clean) and len(tokens) <= 8:
        # "not bad actually" is the same answer as "not bad": things are all right. Only the
        # short-line test kept it out of the ack pool and left it to the fallback's "Noted!".
        nod, nod_seed = _the_nod(memory)
        return _reply(nod, memory, _name(memory), nod_seed)
    # The reading already worked out that the line is the person agreeing to what the bot just
    # suggested ("will give it a go", "gonna try that", "ok give it a go"). The subject is
    # dropped, so the word lists above do not see it as chatty, and it fell through to the
    # composer's "I don't know enough to answer that" shrug.
    if (isinstance(understood, dict) and understood.get("agrees_to_try")
            and len(tokens) <= 10):
        return _reply("try_ack", memory, _name(memory), clean)
    # A judgement asked before anything has been said to judge: "is that ok", "is that fine",
    # "will that help", "is that enough", "is that serious". Three or four words whose whole
    # content is the verdict, one line into a fresh chat, so there is no thing on the screen for
    # the answer to be about. The ack pool read the judgement word as the whole line and answered
    # "Fair enough.", a shrug that agrees with nothing, and the composer's hedge answered "is that
    # serious" and "is that dangerous" with a search. What a friend does is ask what it is - and
    # the judgement word says which thing to ask for. Only in a fresh chat: after an answer the
    # verdict is about that answer, and the readers just above have it.
    if not _mid_chat(memory):
        asked = _a_judgement_asked(clean)
        if asked:
            return _reply(asked, memory, _name(memory), clean)
    # A line that asks whether the thing just said is bad, normal, serious or safe is a question,
    # not an acknowledgement. The ack pool answered it ("is that bad" got "Sounds good.", which
    # agrees the fault is nothing to worry about) because the whole line is ack words. The verdict
    # composer reads it from the bot's own last answer; when that answer was a shrug it has to say
    # so, and a shrug of its own is still better than agreeing the thing is fine.
    if (isinstance(understood, dict) and understood.get("asks_a_verdict")
            and verdict_reply.answers_the_ask(understood.get("clean") or text, memory)):
        # ...and only when there is something behind it to answer from. After a condolence or a
        # mood the last line is not an answer about a thing, the composer can only shrug, and a
        # search hedge to someone whose dad has just died is worse than the line this pool gives.
        return None
    # Somebody else has an opinion about what the person should do with their own life: "my
    # sister thinks i should get a lodger", "my family thinks i should sell the house". Both were
    # answered by the composer's floor - "I'm listening - say more if it helps." and "Got it. Is
    # there anything you'd like a hand with?" - which are the stock lines STYLE.md names as
    # failures: they fit any message and answer none of this one. The person has not reported a
    # fact, a trouble or a plan they made; they have reported a suggestion, and the reply says
    # whose decision it is and that no is allowed. It sits here, after every reading with
    # something of its own, so a suggestion the knowledge base can answer keeps its own reply.
    # Leaving a partner is the one suggestion with a pool of its own in the composer, and it
    # answers the shape better than this one can: "my sister reckons i should leave him" got
    # "That is a big thing to do. How are you doing with it?" before this reading existed, and it
    # is the right reply - the weight of the decision, not whose call it is.
    thinks = _somebody_thinks_i_should(clean)
    if thinks and not fallback._a_relationship_ending(clean):
        return pick(_thinks_pool(thinks[0]), memory, seed_text=text)
    # Somebody praising a thing the person might try ("everyone says the thai place is good",
    # "my sister says i'd like that show") is the other half of that shape: not what to do with
    # their life, but something worth a look, and there is nothing in it for the knowledge base to
    # answer. It sits here for the same reason - every reading with something of its own goes
    # first, so a line the cards can answer keeps its card.
    recommended = _somebody_recommended_a_thing(clean)
    if recommended:
        return pick(SECONDHAND_PRAISE_REPLIES, memory, seed_text=text)
    if not chatty or live_emergency:
        # A statement that picks up a detail of the answer just given ("and i honestly cant get
        # back off", after the advice on waking at four) has its answer in that answer already.
        # It got the fallback's "Thanks for telling me - I'm here if you want to dig into any of
        # that", a stock line that would fit any message; the part of the answer that speaks to
        # the detail is a reply.
        if not live_emergency and isinstance(memory, dict):
            carried = repeat.carried_on(text, memory)
            if carried:
                return carried
        return None
    if isinstance(understood, dict) and understood.get("agreement"):
        # An idiom of agreement ("i know right", "you and me both", "tell me about it") is the
        # person saying "quite", and this module's only pool for a short line like that was the
        # flat nod: "i know right" got "Alright then - good luck with it.", which signs off a
        # conversation that is still going. The composer's own agreement pool carries the
        # agreement back and leaves the floor open, so the turn goes to it.
        return None
    if isinstance(understood, dict) and understood.get("about_bot_kind"):
        # "do you love me", "are you my friend", "what do you think of me": the reading worked out
        # that the line asks what the bot makes of the person, so the composer's own answer to it
        # should have the turn. "love" is an ack word, so the chatty path answered a question with
        # "Fair enough." - a shrug that reads as agreeing with them.
        return None
    if laughed or any(t in LAUGH_WORDS for t in tokens):
        return _reply("laugh", memory, _name(memory))
    if "worries" in tokens or "problem" in tokens:
        nod, nod_seed = _the_nod(memory)
        return _reply(nod, memory, _name(memory), nod_seed)
    if _only_a_refusal(clean, tokens):
        return _reply("no", memory, _name(memory))
    if any(t in {"idk", "dunno"} for t in tokens) or (
            "not" in tokens and "sure" in tokens) or ("dont" in tokens and "know" in tokens):
        return _reply(_idk_kind(memory), memory, _name(memory))
    # The same answer to "how are you" the other way round: "im not good thanks", "not great
    # thanks", "not brilliant thanks". `_is_thanks` does not fire on it ("not" is not a thanks
    # filler) and no pool above reads the state, so the line fell through to the ack pool and
    # a person saying they were not good got "Alright then - good luck with it.". It sits here,
    # after every reading that does better than the flat-day pool, so "im not doing great
    # thanks" keeps the heavy-feeling line it already earned.
    if NOT_GOOD.match(clean):
        # A short line that denies a good word is a low day whether or not it ends in a
        # thank-you: "im not good" was getting the news the word denies ("Good to know."),
        # because with no thanks on it the line fell through to the plain-good branch below.
        return _reply("bad_day", memory, _name(memory))
    self_positive = any(t in {"i", "im"} for t in tokens) and not _denies_a_good_word(
        tokens) and all(
        t in POSITIVE or t in {"i", "im", "am", "so", "very", "really", "doing", "today",
                               "feeling", "feel", "too", "not", "bad", "ok", "okay"} for t in tokens)
    if self_positive:
        return _reply("positive", memory, _name(memory))
    # A line that is nothing but a reaction to the answer above is not a nod at it: "wow" after
    # an explanation was met with "Alright then — good luck with it.", which signs off on a
    # conversation the person was opening, and "really?" with "Sounds good.", which leaves
    # somebody who doubts the answer still doubting it. The composer reads that case
    # (bot/compose/reaction.py), and it says nothing at all unless the line above was an answer
    # rather than a plan or the bot's own question.
    answered = answer_reaction.reply_for(clean, memory) if isinstance(memory, dict) else None
    if answered:
        return answered
    # A nod after heavy news is how a person takes it in ("mm", "ok", "yeah", "right"), and this
    # pool's "Alright then — good luck with it." is a closing line for a chat about a dripping
    # tap: said at a funeral it reads as the bot signing off from the death. `_the_nod` reads the
    # turn before it and answers with room to say more instead of a goodbye.
    nod, nod_seed = _the_nod(memory)
    # The ack pool is the last thing in this module, so it answered every line nothing above it
    # claimed - including lines with a subject of their own. "it was great", "it was nice" and
    # "it was alright" are three words with an acknowledgement word in them, so they were read as
    # the nod and got "Fair enough.", which is a shrug at an offer and reads as agreement with a
    # person who has just said how something went. A line that says what something was is not a
    # nod, so it is left for the composer, which has the warm pool for a good time had by
    # something ("That sounds like a good time - what was the best of it?").
    # The composer is asked, rather than guessed at: it is the module that owns the pool for a
    # good time had by something ("it was great fun", "it was such a nice day"), and a line it
    # will answer must not be taken by this pool's shrug. A verdict it does not claim ("it was a
    # good idea", "it was fine") keeps the nod it has always had.
    if NOT_A_NOD.match(clean) and fallback._a_good_time(clean, memory):
        return None
    return _reply(nod, memory, _name(memory), nod_seed)
