"""Part 4 of 5 of the module, split out of `fallback_chain`.

Everything here is re-exported from `fallback_chain`, so callers import it from there as before.
"""

import re
from ..memory import ack, last_user, swap
from ..memory import stuck as stuck_line
from ..understanding import understand
from ..understanding.kinds import ANSWERING_A_QUOTED_ASK, greeting_only, verdicts_a_thing
from ..understanding.topics import THE_PEOPLE
from . import says_it_has_lingered, step_when_low
from .limit import a_limit_on_the_answer
from . import (
    circumstance, draft, finding_out, goodnews, handoff, leaving, loss, morning_after, no_eyes,
    onething, quantity, reaction as answer_reaction, remark, safetyask, trouble, unseen, why, worn,
)
from .badnews import (reads_as_a_closed_door, reads_as_an_award_lost, reads_as_bad_news,
                      reads_as_news_with_a_name, reads_as_pregnancy_bleeding, reads_as_the_leaving,
                      reads_as_a_leaving_already_gone, reads_as_a_pet_condition,
                      reads_as_the_speakers_own_plan, reads_as_sudden_loss, reads_as_a_carer_body,
                      reads_for_a_carer, reads_for_a_pet, reads_as_a_pet_low, reads_like_a_symptom)
from .goodnews import (reads_as_an_occasion, reads_as_a_win_nobody_noticed,
                      reads_as_a_win_a_cost_came_with,
                       reads_as_a_clear_result, reads_as_good_news, reads_as_news_to_come,
                       reads_as_recovery,
                       reads_as_settled, worry_on_the_table)
from .fallback_data import (
    A_DISMISSAL, A_LOVE_FOR_PEOPLE, A_LOVE_FOR_SOMEONE, A_SORRY_ON_ITS_OWN, ABOUT, ABOUT_SELF,
    ABOUT_TALLY, ACK, ACKS, ACK_AFTER_TROUBLE, ACK_WARM, ACTS_FOR_ME, AGREEMENT, ANIMALS,
    A_CHILD_LEAVING, A_CHILD_LEFT, A_COST_SOMEBODY_ASKS, A_DREAD, A_GOOD_TIME,
    A_GOOD_TIME_IN_A_CARE_THREAD, A_LAUGH, A_NEWS_OF_SOMETHING_ELSE, A_NEWS_OF_WEATHER,
    A_REST_OF_A_GOOD_DAY, A_REST_OF_A_HARD_DAY, A_SMALL_DAY, A_SUGGESTED, A_SUGGESTED_BY_SOMEONE,
    A_THING_LOOKS_SAD, A_THING_THEY_REGRET, A_BETRAYAL, A_WANT_IT_OVER, BAD_STRETCH_REPLIES,
    BODY_POOLS, BOUND_FOR, CAME_BACK, CARD_LINES, CARING, CARING_FOR_A_BODY, CHECK_PHRASES,
    CLOSED_DOOR, COMFORT_SAID, CONGRATS, CUT_FOR, DATES_KEEP_SLIPPING, DECLINED_PLAN,
    DECLINED_PLAN_GENTLE, DITHER_DECIDE, STUCK_AFTER_TROUBLE, RUN_OUT_LINES, DITHER_OPEN_LINES,
    DITHER_TWO_WAY_LINES, DOUBLE_BOOKED, EMPTY, EXPERT_WORDS, FLAT, FOUND_IT, GREETING, GRIEF_AFTER,
    GRIEVANCE, HABIT_REPLY, HAND, HEALTH_WORDS, HANDS_BACK, HELP_ALREADY, HOW_ARE_YOU, IDIOM_GLAD,
    IDIOM_SHY, INVITED, INVITED_TO_TALK, KEEPS_FORGETTING, KNOCKED, LANDED_BAD, LATE_BEHIND_LINES,
    LATE_NOW_LINES, LEFT_POOL, LEFT_POOL_GONE, LOCKED_OUT_LINES, LOCKED_OUT_OF_THE_CAR,
    LOST_A_THING, LOST_A_THING_AGAIN, LOW_DAY_REPLIES, LUMP, MILESTONE, MISHAP_BACK, NAMED_NEGATIVE,
    NEGATIVE, NEUTRAL, NEVER_MIND, A_CORRECTION_TAKEN, NEWS_TO_COME, NOT_FIT_ENOUGH, NOT_TOO_OLD,
    NO_DIRECTION_REPLY, ONE_SKILL_RATED, PENDING_DOUBT, PENDING_LANDED, PENDING_WAITING,
    PENDING_WHEN, PET_CONDITION_TROUBLE, PET_LOW_REPLY, PET_TROUBLE, PLAN, PLAN_DONE, PLAN_DONE_ACK,
    PLAN_KNOCKED, POSITIVE, PREGNANCY_BLEEDING, PRESENT, PUNT, QUOTE_LINES, REACTIONS_CARE,
    REACTIONS_SAID, REACTION_REPEAT, RELATIONSHIP_DECISION, RELIEF, RUMINATION_REPLIES,
    SECRETS_KEEP_SLIPPING, SELF_BLAME, SOMEONE_GONE, SOMEONE_LEAVING, SOMEONE_SERIOUSLY_ILL,
    RETURNED_TO_A_THING, RETURNED_TO_IT, RETURNED_TO_IT_FIRST, SORRY_FOR_ASKING, SORRY_ON_ITS_OWN,
    SUDDEN_LOSS, SYMPTOM, SYMPTOM_COLD, TELL_HARD_LINES, THANKS, THANKS_THEN_SAID,
    THE_FIRST_HOUR_AND_A_CHILD, TIGHT_MONEY, TIGHT_MONEY_MORE, TIPS_LINES, ELDER_AID_REPLIES,
    ELDER_CLINIC_REPLIES, ELDER_DOCTOR_REPLIES, ELDER_HELP_REPLIES, UNKNOWN, UNKNOWN_HEALTH,
    UNKNOWN_WORD, VET_WHO, WALKED_INTO_POOL, WIN_IN_A_SILENCE, WIN_AND_A_COST, WORDING_LINES,
)

# The day that went badly and the name that came from somebody: the pools those readings choose
# from. They are in the data file with the rest, and the readings that use them live here.
from .fallback_data import (
    A_BAD_TIME_TOLD, A_DAY_ASKED_PLAIN, A_NAMED_AFTER, A_NAMED_AFTER_THEM, A_NAME_STORY,
    A_NAME_TOLD, A_PLAN_THAT_FELL_THROUGH, A_STATE_NOW, A_STATE_PAST, A_THING_CAME_OUT_WRONG,
)
from .fallback_data import A_WAY_OF_BEING, LEFT_BEHIND, PAUSE_IN_A_SAFETY_THREAD

# What the moved rows take from fallback.py, which is fully defined by the time this
# module is imported, because fallback.py imports it from its own last line.
from .fallback_part_01 import (
    A_BIT_PAST_IT, A_CHILD, A_HELP_WORD, DITHER, DITHER_OPEN, DITHER_YES_NO, HANDS_IT_BACK,
    HEALTH_MODIFIER, HELP_SERVICE, _a_carer_refused, _a_dead_end, _matchable,
    _only_the_stuck_phrase, _plain, _reads_as_dither, _run_out, _weighs_a_choice,
)
from .fallback_part_02 import UNKNOWN, _a_thing_they_started, _names_their_age, _the_line_before
from .fallback_part_03 import (
    CLOSED_DOOR, NAMED_NEGATIVE, NEGATIVE, _a_start_ask, _a_subject_above, _asks_for_help,
    _occasion_pool, _says_only_what_they_said,
)
from .fallback_part_04 import (
    FORGETS_AGAIN, FORGETS_A_CLASH, FORGET_A_DATE, FORGET_A_SECRET, LEAVING_A_PERSON,
    NOT_LEAVING_ANYONE, SYMPTOM_LINGERS, THE_LEAVE_HAS_HAPPENED, _CAUGHT, _ILL, _LUMP,
    _a_cost_somebody_asks, _a_guessed_result, _a_time_in_it, _an_invitation, _an_open_result,
    _no_words, _the_day_described, _the_news_landed, a_fresh_death_and_the_words,
    reads_as_a_narrowing, reads_as_someone_close_is_ill, the_bound_said, the_limits_said,
)
from .fallback_part_05 import (
    FLAT_LINE, HARM_NAMED, A_HURT_MYSELF, _a_declined_plan, _a_knock_into_a_thing,
    _a_knock_on_oneself, _reaction_pool, _someone_else_dropped_it, _the_heavy_pool,
    _the_person_already_said_it, _the_turn_before_was_a_heavy_one, _verdict_pool, a_happening_now,
    the_answer_to_cut,
)
from .fallback_part_06 import (
    A_COMPARISON_OF_STANDING, IDIOM_GLAD, IDIOM_SHY, LOST_QUESTION, NEGATIVE_LINE, NOT_SELF, PLAN,
    reads_as_a_change_of_medicine, PLAN_MEDICINE_REPLY, PLAN_MEDICINE_SLOW,
    PLAN_MEDICINE_SLOW_REPLY, PLAN_IDIOM, PLAN_NOT_YET, _a_mishap, _a_mishap_to_ask_about,
    _a_relationship_ending, _own_feeling, _plan_reported, _a_promise_that_keeps_moving,
    _summons_pool, a_comparison_of_standing,
)
from .fallback_part_07 import (
    FRIGHTENED, _is_presence_check, _the_answers_take_it, unknown_pool,
)
from .fallback_part_08 import (
    HAND_BACK, _asks_how_are_you, _in_a_care_thread, _news_above, _their_contact_number,
)
from .fallback_part_09 import (
    CANNOT_ANYTHING, CANNOT_ANYTHING_ASK, CANNOT_READ_YOURS, CANNOT_SEE_ANYTHING,
    CANNOT_SEE_ANYTHING_LINES, CANNOT_YOUR_OWN, SO_NOTHING_LIVE, WORDING_ASKS, WORDING_ASKS_WHO,
    _a_no_from_the_bot, _a_verdict_on_their_plan, _the_bot_says_it_cannot, _the_live_thing_named,
    _the_person_they_are_stuck_on, _what_no_eyes_already_says,
)
from .fallback_part_10 import (
    TELL_HARD, _hedged_recently, _in_a_pool, _is_a_tips_ask, _reads_as_greeting, _asks_for_words,
    _the_view_asked_for, _thread_is_about_the_body, is_a_hedge,
)
from .fallback_part_11 import (
    QUOTE_ASKS, _a_place_asked_about, _answered_recently, _live, _reads_as_a_question_when_repaired,
    _reads_as_question, asks_for_more,
)
from .fallback_part_12 import (
    _a_tally_of_its_own_day, _about, _help_topic, _self_line, a_continuation_of_the_tight_week,
)
from .fallback_part_13 import (
    _a_day_ahead, _a_good_time, _dreading, _grief_thread, _grievance_thread, _looking_forward,
    _someone_else_minding, _something_funny, _their_own_slip, _wants_it_over,
)
from .fallback_part_14 import (
    THANKS_GOOD_AGAIN, THANKS_NO_BETTER, THANKS_WENT_BADLY, _a_care_thread_to_leave_alone,
    _a_hard_week, _a_loss_recently, _came_back, _in_a_loss_thread, _in_sudden_loss_thread,
    _is_rumination, _am_i_a_nuisance, _sorry_for_asking, _acknowledges_alone, _thanks_then_said,
    _thanks_with_more, _the_last_line_was_a_fault, _the_last_line_was_bad_news,
    a_loss_in_the_thread, reads_as_a_return, _a_chat_behind_it, the_advice,
)
from .fallback_part_15 import (
    _a_bad_line_above, _a_doable, _a_leaning_side, _a_question_about_the_person,
    _a_refusal_to_answer, _action, _after_advice, _after_safety, _my_pick, _named_draft, _taste,
    _thanks_news_went_badly, _the_last_line_was_heavy, _the_stretch_of_time, _thing_done_pool,
    _tips, _trouble, _unknown, _who_for, _words, in_a_safety_thread, reading, the_dislike_ask,
    the_lost_ask_reply, who_settles,
)
from .fallback import (
    ABOUT, ABOUT_SELF, ABOUT_TALLY, ACK, ACKS, ACK_AFTER_TROUBLE, ACK_WARM, ACTS_FOR_ME, AGREEMENT,
    ANIMALS, ANSWERING_A_QUOTED_ASK, A_CHILD_LEAVING, A_CHILD_LEFT, A_COST_SOMEBODY_ASKS,
    A_DISMISSAL, A_DREAD, A_GOOD_TIME, A_GOOD_TIME_IN_A_CARE_THREAD, A_LAUGH, A_SMALL_DAY,
    A_SORRY_ON_ITS_OWN, A_SUGGESTED, A_SUGGESTED_BY_SOMEONE, A_THING_LOOKS_SAD, A_THING_THEY_REGRET,
    A_WANT_IT_OVER, A_WAY_OF_BEING, BAD_STRETCH_REPLIES, BODY_POOLS, BOUND_FOR, CAME_BACK,
    CARD_LINES, CARING, CARING_FOR_A_BODY, CHECK_PHRASES, COMFORT_SAID, CONGRATS, CUT_FOR,
    DATES_KEEP_SLIPPING, DECLINED_PLAN, DECLINED_PLAN_GENTLE, DITHER_DECIDE, DITHER_OPEN_LINES,
    DITHER_TWO_WAY_LINES, DOUBLE_BOOKED, ELDER_AID_REPLIES, ELDER_CLINIC_REPLIES,
    ELDER_DOCTOR_REPLIES, ELDER_HELP_REPLIES, EMBARRASSED, EMPTY, EXPERT_WORDS, FLAT, FOUND_IT,
    GREETING, GRIEF_AFTER, GRIEVANCE, HABIT_REPLY, HAND, HANDS_BACK, HEALTH_WORDS, HELP_ALREADY,
    HOW_ARE_YOU, INVITED, INVITED_TO_TALK, A_GOODNESS_ASKED_OF_ME, A_SKILL_ASKED_OF_ME,
    ASKED_A_RATING, ASKED_IF_GOOD, I_RATE_A_SKILL, KEEPS_FORGETTING, KNOCKED, LANDED_BAD,
    LATE_BEHIND_LINES, LATE_NOW_LINES, LAUGHED_AT, LEFT_BEHIND, LEFT_POOL, LEFT_POOL_GONE,
    LOCKED_OUT_LINES, LOCKED_OUT_OF_THE_CAR, LOST_A_THING, LOST_A_THING_AGAIN, LOW_DAY_REPLIES,
    LUMP, MILESTONE, MISHAP_BACK, NEUTRAL, NEVER_MIND, NEWS_TO_COME, NOT_FIT_ENOUGH,
    A_CORRECTION_TAKEN, NOT_TOO_OLD, NO_DIRECTION_REPLY, ONE_SKILL_RATED, PENDING_DOUBT,
    PENDING_LANDED, PENDING_WAITING, PENDING_WHEN, PET_CONDITION_TROUBLE, PET_TROUBLE, PLAN_DONE,
    PLAN_DONE_ACK, PLAN_KNOCKED, POSITIVE, PREGNANCY_BLEEDING, PRESENT, PUNT, QUOTE_LINES,
    RATES_A_SKILL, REACTIONS_CARE, REACTIONS_SAID, REACTION_REPEAT, RELATIONSHIP_DECISION, RELIEF,
    RUMINATION_REPLIES, RUN_OUT_LINES, SECRETS_KEEP_SLIPPING, SELF_BLAME, SELF_BLAME_ASKS,
    SELF_SUBJECT, SOMEONE_GONE, SOMEONE_LEAVING, SOMEONE_SERIOUSLY_ILL, SORRY_FOR_ASKING,
    SORRY_ON_ITS_OWN, STUCK_AFTER_TROUBLE, SUDDEN_LOSS, SYMPTOM, SYMPTOM_COLD, TELL_HARD_LINES,
    THANKS, THANKS_THEN_SAID, THE_FIRST_HOUR_AND_A_CHILD, TIGHT_MONEY, TIGHT_MONEY_MORE, TIPS_LINES,
    UNKNOWN_HEALTH, UNKNOWN_WORD, VET_WHO, WALKED_INTO_POOL, WIN_IN_A_SILENCE, WORDING_LINES,
    WOULD_HAVE_BEEN, ack, answer_reaction, circumstance, draft, finding_out, goodnews,
    greeting_only, handoff, last_user, leaving, loss, no_eyes, onething, quantity, re,
    reads_as_a_carer_body, reads_as_a_clear_result, reads_as_a_closed_door,
    reads_as_a_leaving_already_gone, reads_as_a_pet_condition, reads_as_a_win_nobody_noticed,
    reads_as_an_award_lost, reads_as_an_occasion, reads_as_bad_news, reads_as_good_news,
    reads_as_news_to_come, reads_as_news_with_a_name, reads_as_pregnancy_bleeding,
    reads_as_recovery, reads_as_settled, reads_as_sudden_loss, reads_as_the_leaving,
    reads_as_the_speakers_own_plan, reads_for_a_carer, reads_for_a_pet, reads_like_a_symptom,
    remark, says_it_has_lingered, step_when_low, stuck_line, swap, trouble, understand, unseen,
    verdicts_a_thing, why, worn, worry_on_the_table,
)
from .fallback_chain_part_01 import (
    ABOUT_THE_BOT_LINES, PLEASURE_GONE_LINES, _act_asked_of_me, _acts_for_me,
    _an_order_it_cannot_do, _body_state, _reads_as_a_bad_stretch, reads_as_a_question_about_the_bot,
    reads_as_no_pleasure,
)
from .fallback_chain_part_02 import (
    _choose, NEAR_MISS_REPLY, _A_CORRECTION, _a_birthday_still_to_come, _a_lateness_report,
    _a_low_day, _a_near_miss, _a_things_state, _asks_the_bot, _loves_people, _mood,
    _only_what_the_line_gives, _options_already_up, _reads, _reads_value, _restated, _routine_pool,
    _somebody_hurt, _takes_something_back, _the_birthday_said_back, _the_clock_pool,
    _the_morning_has_a_clock, _the_time_said, _words, reads_as_a_flat_habit,
)
from .fallback_chain_part_03 import (
    A_CROWD_AHEAD, NOTHING_TO_WEAR_REPLIES, _a_betrayal, _a_care_home_line,
    _a_countdown_in_a_care_thread, _a_problem_stated, _a_thing_got_ahead, _a_thing_they_regret,
    _a_wear_ask_about_a_day, _just_asked_about_the_day, _says_there_is_nothing_to_wear,
    _the_crowd_is_ahead, _the_wear_pool_for_the_line, HAVE_GOT_A_THING, A_HARD_DAY_MOOD,
    _an_emotion, A_BAD_THING_NAMED, A_DAY_SUBJECT, A_DAY_WENT_WRONG, A_HAND_OUT, A_LOOKING_BACK,
    A_SYMPTOM_PHRASE, BAD_DAY_ANYWAY, DAY_PAST, NOT_A_DAY_DONE, NOT_A_DAY_SAID, PAST_DOING,
    SOMEONE_DONE_WRONG, _a_day_of_someone_else, _a_detail_about_what_was_said, _a_thing_happened,
    A_NAMES_TOLD, A_NAME_A_HOUSEHOLD_TAKES, NOT_A_NAME_WORD, AN_ATTEMPT_AT_SOMEONE,
    A_BETRAYAL_FOUND_OUT, A_NAME_IS_NOT_A_DAY,
)


def _answers_the_correction(restated, memory):
    """The pointed-at ask answered from the thread, or None when it has only a punt in it."""
    from . import verdict
    sub = dict(memory)
    sub["compose"] = dict(memory.get("compose") or {})
    sub["understood"] = understand(restated, memory)
    # Never a second hop: a reading of the pointed-at words may itself come back as a correction
    # ("porto not lisbon" carries "not "), and answering that would be the same line again.
    sub["correction_answered"] = True
    # Every pool is filtered, not only this file's own: a verdict path can answer with the
    # search shrug too ("i want to kill myself" / "no i meant how do i tell my wife" lost the
    # drafting offer to "That's beyond what I know well"). The first reply that is not a punt
    # wins, and a punt in one pool never hides a real answer in the next.
    for pool in (verdict.next_step, verdict.reply_for, reply_for):
        reply = pool(restated, sub)
        if reply and not any(punt in reply.lower() for punt in PUNT):
            return reply
    return None


def reply_for(text, memory, verdict=True):
    """One short reply that fits the kind of line, never repeating the last few.

    `verdict=False` is for a caller asking what the composer would say about a line *as a thing*
    rather than as this turn: the memory store asks it that way (`bot/memory/cause.py`,
    `_the_bot_would_only_shrug`) to find out whether the words on their own already have an
    answer, and the verdict pool is the answer to the turn, not to the words. Left in, "im so
    tired" then "thats annoying" made the store think the composer had answered and stand down,
    and the pool's line then lost the turn to chat's - the store's own line about that tiredness
    is the better answer and the one it gave on main (gray-cypress on #5479).
    """
    # A line that names a person of theirs and nothing else is a person to ask about however it is
    # worded, and "what about the little one" is the same line as "and the little one". As a
    # question it reached the search hedge ("I'm not sure about that one, sorry"), which is the
    # wrong answer to a person a friend was just told about. The pattern is anchored to the whole
    # line, so a real question about a person ("what about my sons school") never gets here.
    if verdict and isinstance(memory, dict):
        alone = (ack.a_person_named_alone(_matchable(text), memory)
                 or ack.a_person_pointed_at(_matchable(text), memory))
        if alone:
            return alone
    said = _reply_for(text, memory, verdict=verdict)
    if verdict and said and is_a_hedge(said):
        # "I'd rather not guess. A quick search online will get you a solid answer" is the last
        # thing the bot can say, and a verdict on the plan already on the table is never worse than
        # it. "i want to grow a beard" was answered "Grow a beard — fair enough. What's stopped it
        # happening so far?", and the follow-up "is that daft" got the hedge: the stand-down in
        # `_the_reply_above_judged` keeps the verdict off the bot's own question, which is right
        # while something else can answer the turn and wrong when the hedge is the alternative.
        clean = _matchable(text)
        pool = _a_verdict_on_their_plan(clean, memory, past_a_question=True)
        if pool:
            return _choose(pool, memory, clean)
    if verdict and said:
        # Nothing has been said in this chat yet, and every pool here is written for a conversation
        # in progress, so the line that fits this turn can be about a life the person has not
        # described: "sorry, i got cut off" as the first thing in a chat was answered "Good to
        # hear. What was the best bit?", "back to what we were saying" by "Nice one. How did the
        # rest of it go?", and "carry on" by "Thanks for telling me - I'm here if you want to dig
        # into any of that." The pools are right a turn later, so the reading is not wrong - what
        # is wrong is answering a turn that has not happened. The question is asked in one place
        # (`bot/memory/already.py::nothing_said_yet`), and this is the composer's own answer to it:
        # a line that names no earlier turn, because there is none to name. It takes both facts -
        # this is a chat's first line, and the line brings nothing of its own - because a first
        # line that does bring something ("weve booked a week in cornwall in august") is well met
        # by a pool written for a chat in progress: "Nice one. Is it soon, or have you got a while
        # yet?" The fault is only where there is nothing to react to.
        from . import fallback as composer
        if (composer.nothing_said_yet(memory)
                and composer.brings_nothing_of_its_own(text)
                and composer.assumes_an_earlier_turn(said)):
            return _choose(composer.NOTHING_SAID_YET, memory, _matchable(text))
    return said


def _reply_for(text, memory, understood=None, verdict=True):
    """The composer's reply to this turn (`reply_for`), with the reading already made."""
    if understood is None:
        understood = memory.get("understood")
    if not isinstance(understood, dict):
        understood = understand(text, memory)
    state = memory.setdefault("compose", {})
    was_taste = bool(state.get("taste"))
    state["taste"] = False
    kind = understood.get("kind") or "statement"
    words = understood.get("words") or []
    clean = understood.get("clean") or " ".join(text.lower().split())
    # A countdown asked inside a care thread reaches this file's own care continuation first, and
    # that continuation answers any second line with "I'm glad you're talking about it" - which is
    # right for most of them and wrong for "how long till december", where the person is asking how
    # long they have to hold on. The date is the one thing this turn wants said, so it is read here.
    counted = _a_countdown_in_a_care_thread(memory, clean, text, understood)
    if counted:
        return counted
    after = _after_safety(memory, clean, understood)
    if after:
        return after
    # The ask one turn after the condolence: "how do i tell a 4 year old". The child's words are
    # the whole answer, and the readings below take this line first: the hedge sends a bereaved
    # parent to a search engine, the drafter asks them to write the words themselves, and the
    # topic entries answer "a 4 year old" with the screen-time card. Narrow on purpose - the ask
    # shape, a child, and a death in the thread (see bot/compose/childwords.py). The line itself,
    # not `clean`: the reading in memory was made for the previous turn.
    from . import childwords
    if childwords.asks_the_words_for_a_child(text or clean, memory):
        return _choose(childwords.THE_WORDS_FOR_A_CHILD, memory, clean)
    # A talk asked for at a time: "can we talk tonight", "can we chat later", "can you keep me
    # company". There is no diary and no clock here, and the search hedge sent a person who wanted
    # a conversation to a page about nothing. Asked here, before the hedge and before the pools
    # that answer a thing, because the time is all the line holds - a line that names what the talk
    # is about ("can we talk about my boiler") is that thing's answer and the reader stands down.
    from . import talktime
    at_a_time = talktime.answer_for(clean, memory)
    if at_a_time:
        return at_a_time

    # A night of drinking, said the day after. Six pools deeper in this chain were answering it:
    # "i was blind drunk last night" and "i got pissed last night" got the day pools' "Good to
    # hear. What was the best bit?", "i got wasted at the party" the echo, "i was bladdered at the
    # do" the skills line, "im hanging this morning" the task line, and "i was plastered last
    # night" the sober-years pool, which read "plastered" as time off the drink. A cheer at a
    # night a person is not proud of is the reply they cannot use, so the reading is one place and
    # it is here, before all six. A knowledge card still takes the turn, because the composer is
    # last: "i have such a hangover" keeps the water, sleep and food card.
    if morning_after.reads_as_a_morning_after(clean):
        return _choose(morning_after.A_MORNING_AFTER, memory, clean)

    # Somebody the person loves has been hurt and no card covers it. "my son was in an accident"
    # was filed back to them ("Noted: your son was in an accident"), and "my brother got hit by a
    # car" got "Got it. Is there anything you'd like a hand with?" - a line that could have come
    # before any message at all. The person is not handing the bot a fact to keep, they are saying
    # the worst thing in their week, so the reply asks about them.
    hurt = _somebody_hurt(clean, memory, understood)
    if hurt:
        return hurt
    # A safety question about a thing of theirs ("is it safe to keep it on tonight" about the
    # boiler the line before) reached the repeat frame and the search shrug. It is one question
    # with one answer, and it is read here, above the topic pools and below every card that
    # names the thing (bot/compose/safetyask.py, and the size note in `_reply_for`).
    if not _a_care_thread_to_leave_alone(memory):
        safety_ask = safetyask.reply_for(clean, memory)
        if safety_ask:
            return _choose(safety_ask, memory, clean)
    # The person hands the choice straight back and there is nothing on the screen to pick from
    # (see HANDS_BACK). Read here, before the topic pools, because there is no topic: the line is
    # all the person said.
    if HANDS_IT_BACK.match(clean) and not _options_already_up(memory):
        return _choose(HANDS_BACK, memory, clean)
    # A line that only points back at the conversation - "as i was saying", "where was i", "sorry,
    # i got cut off", "so anyway" - names nothing, so the account-of-the-day pool answered it as
    # though it were news ("Sounds alright. Anything good in it?") and the search hedge took
    # "where was i". The person is picking the thread back up, which is the whole content of the
    # line, so it is read here, before the pools that answer a line's subject. The thing named
    # after the phrase ("as i was saying about the car") is asked about, because the person has
    # not said it yet - and neither pool names a turn, so both work as a chat's first reply.
    returned = reads_as_a_return(clean)
    if returned is not None and not _came_back(clean) and not _grief_thread(memory):
        if returned:
            return _choose(RETURNED_TO_A_THING, memory, clean).format(thing=returned)
        if not _a_chat_behind_it(memory):
            return _choose(RETURNED_TO_IT_FIRST, memory, clean)
        return _choose(RETURNED_TO_IT, memory, clean)
    # The bot's own last turn offered to write the message ("tell me who it's for and what you
    # want them to do"), and this line is that detail. Read here, before the topic pools, because
    # the reason inside the message is not a new topic: "saying i cant make saturday cos im
    # skint" was reaching the money pool and the note the bot asked for never arrived. An
    # emergency, a loss or a bleed still wins - a draft of chest pains is not a message.
    drafted = _named_draft(memory, text, words, clean)
    if drafted:
        return drafted
    # An idiom of agreement is the person saying "quite", not asking to be told about anything:
    # "tell me about it" was reaching the search hedge. The reading found the idiom, the pool
    # only phrases it, and it is asked before the flat branch because "you and me both" is flat
    # enough to be read as a shrug at the weather.
    if understood.get("agreement"):
        return _choose(AGREEMENT, memory, clean)
    # A line that says the money has run out is a tight week, not a money question: the reading
    # only says so when nothing is being asked, so "what can i cook till payday" is untouched.
    if understood.get("tight_on_money"):
        # A line that already says what is left ("i have 20 quid till friday") has answered the
        # question the last pool line asks, and asking it back is the bot not listening. The
        # lines that name the week rather than ask about it are the ones left.
        pool = TIGHT_MONEY
        if understood.get("amount_left"):
            pool = tuple(line for line in pool if "what's left" not in line.lower())
        return _choose(pool, memory, clean)
    # The turn after that one, when the person asks the bot to go on instead of answering the
    # question the pool asked: the same week, said again as the ask it needs.
    if a_continuation_of_the_tight_week(memory, clean):
        return _choose(TIGHT_MONEY_MORE, memory, clean)
    # A day of the person's own that went badly is not a fact to file and not a request: the floor
    # answered "i had a low day" with "Thanks for telling me" and "low day today" with "Noted: low
    # day today", which hands the person their own sentence back. Read before the ack and the
    # reaction pools, because the day is the whole of what they said.
    if _a_low_day(clean, understood):
        return _choose(LOW_DAY_REPLIES, memory, clean, seed_text=text)
    # The hand-back ("what about you", "and you", "yourself") is the person passing the
    # question over, and the manners pool is the reply: left to the follow-up readers it is read
    # as a question about the thing on the table, and after the egg answer "what about you" got
    # the egg answer again. It is asked here, before the advice and reaction pools, because it
    # names nothing of its own and there is nothing for them to answer. An opening hand-back has
    # nothing behind it to pass over, so that one is left to the chat module's warmer line.
    if HAND_BACK.match(_self_line(text)) and (memory or {}).get("turns"):
        # Seeded on the line itself so two chats with the same shape do not get the same
        # sentence: the letter sum `_choose` uses by default collides on lines of the same
        # length, which put one wording on most of the hand-backs (sure-umbrella on #6004).
        return _choose(HOW_ARE_YOU, memory, clean, seed_text=text)
    # A report on the advice in the last answer ("i tried that and it helped a bit", "its not
    # helping") is answered with the outcome, not with the stock nod or the flat "could be
    # worse" ack. It sits before that ack and after the safety continuation, and it only fires
    # on a line that is nothing but the report, so it can never take a turn from a subject of
    # the person's own.
    verdict = _verdict_pool(clean, memory) if verdict else None
    if verdict and in_a_safety_thread(memory):
        # A live emergency is not a verdict turn at all: the bot's own continuation of it is.
        verdict = None
    elif verdict and a_happening_now(memory):
        # It is happening as they type: a miscarriage now, a death in the house. Sympathy and a
        # question about how they are today is the wrong turn to take - the careful continuation
        # already there is not to be talked over.
        verdict = None
    elif verdict and a_loss_in_the_thread(memory):
        # A verdict on a death, a diagnosis or a baby lost is a heavier turn, and the light pools
        # ask a fix question that fits a laptop and not a bereavement. Standing the pool down once
        # left the floor under it ("Got it. Is there anything you'd like a hand with?" after "my
        # nan died in march" then "thats a shame"), so the heavier pool takes the turn instead.
        # The answer a module already gave about the loss keeps the turn before this is asked
        # (`bot/modules/arbiter.py`, `_the_verdict_back`), and the composer only fills the floor.
        # The pool is the weight of the news: a death, a queue, a job gone and a hard week are
        # not the same line (`_the_heavy_pool`).
        verdict = _the_heavy_pool(memory)
    # A verdict is not a report on the advice in the last answer: "what a headache" after the
    # tenant line read as "it did not help" and got a second tenant card, and "its a mess" after
    # the oven answer read as asking for the rest of it. Nothing is being reported and nothing
    # more is being asked for, so the report branch stands aside for the verdict.
    tried_reply = None if verdict else _after_advice(memory, clean, words)
    if tried_reply:
        return tried_reply
    # A fifth outcome of that advice, and the one that is not about the person's own try: they did
    # what the answer said and were turned down. "my boss said no" was filed back as "Got it -
    # your boss said no", so the no is answered here rather than by the ack.
    refused = _a_refusal_to_answer(clean, memory, words)
    if refused:
        return _choose(refused, memory, clean, seed_text=the_advice(memory) or clean)
    # The line before the try: they have read the answer and it sounds doable. It sits with the
    # report on the advice for the same reason - both are about the answer and not about a subject
    # of the person's own - and after it, because "i tried that, it was doable" is a report.
    doable = _a_doable(clean, memory)
    if doable:
        return doable
    if verdict:
        # Before the flat pool, the hedge and the taste question: a verdict is the whole line,
        # and "what a hassle" was reaching the search shrug as if it had asked something.
        return _choose(verdict, memory, clean)
    # The same reading, for the reactions another pool would take first: "seriously?" and
    # "no way" after an explanation were answered "Really? Tell me what happened", which asks for
    # news when the person is reacting to the answer they just got. bot/compose/reaction.py says
    # nothing unless the line above was an answer, so a reaction to news keeps this pool.
    answered = answer_reaction.reply_for(clean, memory) if isinstance(memory, dict) else None
    if answered:
        return answered
    reaction = _reaction_pool(clean, memory)
    if reaction is REACTION_REPEAT:
        # "what?" and "huh" are read as the repeat, and the answer above is the one thing that can
        # be said again in fewer words: the answer's own opening clause beats "which bit was
        # unclear?" because it hands something back. Where there is nothing to cut the reading says
        # so itself and asks which part (bot/compose/why.py, `said_again`).
        again = why.said_again(clean, memory) if isinstance(memory, dict) else None
        if again:
            return again
    if reaction and not _a_care_thread_to_leave_alone(memory):
        if _the_person_already_said_it(memory):
            reaction = REACTIONS_SAID.get(reaction, reaction)
        # Before the flat pool and the hedge: a reaction is answered in kind, and it is the same
        # kind of line the flat pool answers, so it has to come first for "ugh" and the rest.
        return _choose(reaction, memory, clean)
    if reaction and _a_care_thread_to_leave_alone(memory) and reaction is not REACTION_REPEAT:
        # A death, a loss or a crisis: the reaction above stands down so the thread stays with the
        # person, and this is what answers instead of the flat pool's shrug.
        return _choose(REACTIONS_CARE, memory, clean)
    # A remark about the day ("bit nippy", "pouring down", "the suns out") is answered with the
    # day, not with the stock nod. It is read after the pools that need the turn before to read it
    # (a verdict, a reaction, a report on the advice), because "lovely day" the turn after good
    # news is about the news and not about the weather, and it stands down in a care thread, a
    # heavy week or an emergency, where the day is not what the person is talking about.
    the_day = _the_day_described(clean)
    if the_day and not in_a_safety_thread(memory) \
            and not _a_care_thread_to_leave_alone(memory) \
            and not _the_turn_before_was_a_heavy_one(memory, clean):
        return _choose(the_day, memory, clean)
    if words and len(words) <= 6 and FLAT_LINE.match(" ".join(words)):
        # Before the hedge, the taste question and the nod: "could be worse" was reaching the
        # search shrug as if it asked something, "same old" carried "same" into the cheery ack,
        # and a bare "ugh" got "I'm listening - say more if it helps" as if nothing was said.
        return _choose(FLAT, memory, clean)

    # A view asked for with nothing named ("whats your honest view?", "honest view?", "your take",
    # "honest answer"): the person is asking the bot to stand behind the answer just given, and a
    # search suggestion there is the bot denying its own paragraph. It is read before every pool
    # that answers a *subject*, because the line names none: "honest answer" one turn after a
    # phone-battery answer was reaching the routine pool's phone habit line ("take the choice out
    # of the moment rather than counting on willpower"), which answers a question the person did
    # not ask. It is also before the taste pools, because "your take" and "what do you reckon"
    # are in both families, and the general taste line ("No strong view on that one, honestly.
    # What's yours?") is the shrug for a question with no answer behind it - said one turn after
    # a full answer, it is a lie.
    view = _the_view_asked_for(clean, memory)
    if view:
        return view
    no_words = _no_words(clean)
    if no_words:
        return _choose(no_words, memory, clean)

    if kind == "thanks" and "?" in text:
        kind = "question"
    # ... but a greeting in front of something to answer is not a hello: "hi, my boiler is
    # leaking" and "hello my cat keeps being sick" want those lines answered, and
    # "hi there - what can I help with?" answers nothing. So the greeting is only claimed when
    # the line is a hello on its own (the same test the reading uses) or when what follows is
    # someone saying what they want ("hi i need help writing a cv"): a hello and an offer is a
    # better reply to that than a neutral "got it", which is all the rest of this file can say.
    # A line that reports something keeps the kind it was given, so the news and trouble
    # replies below still get their turn.
    # "hi, can you help me" is the ask with a hello in front of it. The hello adds nothing to
    # answer and the greeting pool would offer nothing back, so the ask keeps the turn.
    asks_for_help = _asks_for_help(_plain(clean), understood)
    opens_with_hello = kind == "statement" and _reads_as_greeting(words, text) \
        and not _reads_as_question(text, words)
    if opens_with_hello and not asks_for_help \
            and (greeting_only(words) or understood.get("intent") == "request"):
        kind = "greeting"
    if kind == "empty":
        return _choose(EMPTY, memory, clean)
    if kind == "greeting" and not asks_for_help:
        return _choose(GREETING, memory, clean)
    if kind == "thanks":
        # A thank-you with bad news behind it is that news: the kind reader takes the whole line
        # for manners, so this asks first or every "thanks, its still stinging" is thanked back
        # and the thing that has not come right goes unanswered.
        if _thanks_news_went_badly(clean):
            return _choose(THANKS_NO_BETTER, memory, clean)
        # A thank-you with a goodbye on the end is a goodbye: "thanks, i need to go, the kids are
        # up" was answered "Happy to help.", which answers the half that was not the point. The
        # pool is the composer's goodbye, so the wording and the reading stay in one place.
        bye = leaving.pool(clean, words, memory=memory)
        if bye:
            return _choose(bye, memory, clean)
        return _choose(THANKS, memory, clean)
    # A person they love, said plainly: filed back by the store as "Noted: you love your mum."
    # It sits before the hand-off, the repairs and the echo, and after the greeting and thanks
    # branches, which are the lines it cannot be.
    loved = _loves_people(clean)
    if kind != "question" and loved:
        return _choose(A_LOVE_FOR_PEOPLE if loved > 1 else A_LOVE_FOR_SOMEONE,
                       memory, clean)

    # A hand-off ("one more thing", "quick one") has said nothing yet, so there is nothing to
    # answer and nothing to search for: the knowledge base matched the words "one" and "thing"
    # and answered a study question. It sits before the search and the taste branches, which are
    # the ones that would otherwise claim it, and after the safety, thanks and hello branches,
    # which are the lines it cannot be.
    going_on = handoff.reply_for(clean, memory)
    if going_on:
        return going_on

    # The line takes the last answer back and asks again. The pointed-at words are the turn.
    restated = "" if memory.get("correction_answered") else _restated(understood)
    if restated:
        reply = _answers_the_correction(restated, memory)
        if reply:
            return reply

    # A line that only puts a new value where the old one was ("make it four", "make that 10k")
    # is not asking the bot for options, and the store can only correct a value it holds: a habit
    # they described is not one, so these lines were reaching the search hedge from the asks-the-bot
    # branch below ("That's beyond what I know well, sorry"), which answers a correction as if the
    # person had asked a question. The value goes back up with the unit of the line it corrects.
    corrected = ack.value_put_right(clean, memory)
    if corrected:
        return corrected
    wondered = ack._a_condition_they_wonder_about(clean, memory)
    if wondered:
        # "i think i have diabetes" is a question about diabetes, and nothing else answers it:
        # said back as a fact it was "Noted: you think you have diabetes", which is no answer.
        return wondered
    plain = _plain(clean)
    # The same line with its wrong words put right ("me knee is killing me" -> "my knee is
    # killing me"), from the reading. Only ever a second reading: every pool below test the
    # typed line first and consult this one only when nothing matched.
    repaired = understood.get("plain") or clean
    if _is_presence_check(clean):
        # "can you hear me" with nothing else in it is a presence check: a search shrug is
        # the wrong answer, so say something present and leave the floor open.
        return _choose(PRESENT, memory, clean)

    # A plan the person has had to drop ("i cant come", "sorry i cant make it", "gonna have to
    # cancel") is answered as the plan it is, before the trouble question and the stock nod: see
    # `DECLINED_PLAN`. Nothing else in this file reads these lines.
    if _a_declined_plan(plain) and not draft.drafter(memory, clean):
        # Not while the bot has an offer open to write the message: "can you help me write a text
        # to my boss" then "i need to tell her i cant come" is the message, and it was getting
        # this pool instead of the draft ("No trouble at all - these things happen" in place of
        # the note to send). The draft below answers it.
        if _a_hard_week(memory):
            # "my mum is dying" then "i cant come": the plan is dropped in the worst week of
            # their life, so the answer stays in that register instead of being jolly about it.
            return _choose(DECLINED_PLAN_GENTLE, memory, clean)
        if _the_turn_before_was_a_heavy_one(memory, plain):
            # "i had a panic attack" then "i cant come", "im depressed" then "i cant make it":
            # the plan is what the feeling cost them, not a diary clash. The line is left to the
            # readers that answer a feeling, so the panic card and the warm frame keep the turn
            # instead of asking somebody who is struggling whether they want to rearrange it.
            pass
        elif _someone_else_dropped_it(plain):
            # The plumber, the sitter, a friend: nothing to explain and nobody expecting them.
            return _choose(PLAN_KNOCKED, memory, clean)
        else:
            return _choose(DECLINED_PLAN, memory, clean)

    help_topic = _help_topic(clean, understood)
    if help_topic:
        return _choose(help_topic, memory, clean)

    # "Which would you pick?" asks for the bot's own taste, but the thing to pick from is
    # already on the table, so it is answered before the identity pool: "what would you get"
    # was reading as a question about the bot itself ("I'm a chatbot").
    # A trade-off the person has put down and a bare "what would you do" after it: the bot has a
    # side, and saying it beats handing the decision back ("Not mine to decide, sorry") or asking
    # what the options are when they have just named two.
    leaning = _a_leaning_side(plain, memory)
    if leaning:
        return leaning
    mine = _my_pick(plain, memory)
    if mine:
        return mine
    verdict = _a_verdict_on_their_plan(plain, memory)
    if verdict:
        return _choose(verdict, memory, clean)
    # The place on the table, asked about in three words: "is it nice" after "we are going to
    # Cornwall in August". The nod pool read it as agreement and the hedge sent them to a search
    # engine; this says plainly that the bot has not been, and asks what the trip is for.
    place_ask = _a_place_asked_about(plain, memory)
    if place_ask:
        return _choose(place_ask, memory, clean)

    # The same ask as a bare "why", said about the words just used: "why do you say that", "how
    # come you said so", "what makes you say that". It carries nothing of its own for the
    # knowledge base to match, and the pool below owns every line about the bot, so it answered
    # these with a different question's answer - "No grand reason. Someone built a thing that
    # helps with everyday questions without a search engine" - which is why the bot exists, not
    # why it said what it said. The ask reaches the reason code first, and that code stands down
    # when the answer above was the bot describing itself, so the identity answer keeps its turn.
    saying_ask = why.respond_to_a_saying_ask(clean, memory, understood,
                                             body=_thread_is_about_the_body(memory))
    if saying_ask:
        return saying_ask

    about = _about(plain, understood)
    # A question the person is quoting is somebody else's question, and the two bot-about cards
    # below answer with the bot's own day and the bot's own clothes - the wrong person answering.
    # "how should i answer what are you up to" and "what do i say when they ask what are you
    # wearing" are interview and small-talk questions the person wants an answer to give, so the
    # frame stands these two cards down (`understanding.kinds.ANSWERING_A_QUOTED_ASK`) and the
    # knowledge base, which has the interview answer, takes the turn.
    if about in ("self_doing", "clothes") and ANSWERING_A_QUOTED_ASK.search(clean or "") \
            and _the_answers_take_it(clean or ""):
        about = None
    if about == "memory" and _a_tally_of_its_own_day(understood):
        return _choose(ABOUT_TALLY, memory, clean)
    if about == "hand":
        return _choose(HAND, memory, clean)
    if about in ABOUT:
        return _choose(ABOUT[about], memory, clean)
    if about:
        return _choose(ABOUT_SELF[about], memory, clean)

    # A small social slip of their own is a minute to be met warmly, not a verdict on the person.
    # It goes above the self-judgement pool, which read the word "embarrassment" in "im dying of
    # embarrassment" as one, and above the laugh pools' stand-down for a laugh that was at them.
    awkward = _their_own_slip(clean, memory)
    if awkward:
        said = _choose(awkward, memory, clean)
        if said is None:
            # A chat that has already had five of these has emptied the pool it chose, and the
            # other one is a line about the same kind of minute: better that than the stock nod
            # the turn falls to if this returns nothing.
            said = _choose(EMBARRASSED if awkward is LAUGHED_AT else LAUGHED_AT, memory, clean)
        if said:
            return said

    if SELF_SUBJECT.search(clean) and not SELF_BLAME_ASKS.search(clean) \
            and not WORDING_ASKS.search(clean) and not RATES_A_SKILL.search(clean) \
            and not _own_feeling(clean):
        # Before the asking branch: "am i useless" is the same sad question as "im useless", and
        # a search link answers neither. A line that also asks for something the bot can give
        # ("any tips", "what should i eat") keeps its own answer: the ask comes first.
        return _choose(SELF_BLAME, memory, clean)

    # The same question in the spelling the person meant: "any ideaz", "wich one should i pick".
    # A typo that hides the shape of the ask turns a question into a statement, and a statement
    # is answered by the nod or the hedge instead of the way in. The typed line is read first
    # and the repaired one only as a second try, like every other pool in this file.
    asking = kind == "question" or (kind == "statement" and (
        _reads_as_question(text, words)
        or (repaired != clean and _reads_as_a_question_when_repaired(repaired))))
    if asking and _thanks_then_said(clean):
        # "thanks, its back to how it was" is a report of the outcome, and the "how" in it made
        # the understanding read the whole line as a question, so the search hedge answered the one
        # turn the thanks pools below are for. A thanks that really asks keeps `asking`: the tail
        # has to be free of every question word ("thanks, can you do the same for the shed",
        # "thanks, how do i set the timer" both stay questions).
        asking = False
    if asking and _acknowledges_alone(clean):
        # "good to know" is the whole line and there is nothing in it to search for: `know` read
        # as the question word, so the acknowledgement went to the hedge - "I'd rather not guess.
        # A quick search online will get you a solid answer". Nothing is being asked, so the
        # thanks pools below answer it like any other "thanks".
        asking = False

    # A line with a right action gets it whatever its grammar: "i can smell gas" is not small
    # talk, and a statement can be an emergency.
    action = _action(clean, memory)
    if action:
        return action
    # A date that would have been theirs is not a fact to file away and not a question to hedge:
    # "it would have been our anniversary next week" was answered with "Got it, is there anything
    # you'd like a hand with", and "would have been our anniversary today" with the search hedge.
    # It sits here, after the action, because anything with an emergency in it is still that.
    if WOULD_HAVE_BEEN.search(clean):
        return _choose(MILESTONE, memory, clean)

    # A line that says the person is going is a goodbye, and the reason behind it is not a
    # question: "ill let you go, dinner is burning" is not a cooking question, and "anyway i
    # better go, hes crying" is not something to search for. Read here, so both the wording
    # and the arbiter's rule come from bot/compose/leaving.py.
    bye = leaving.pool(clean, words, memory=memory)
    if bye:
        return _choose(bye, memory, clean)
    # A goodbye whose reason is a body in trouble stands out of the body's way, and this module
    # only speaks when nothing answered it: "right, im off to bed, my tooth is agony" had no
    # toothache entry behind it, so the only thing left was to file the line back ("Noted: you're
    # off to bed, your tooth is agony"), which gives the person nothing. Letting them go warmly
    # is the smaller thing to say, and the body is asked about on the next line if they come back.
    if leaving.reads_as_a_leave_with_a_body_in_it(clean, words):
        bye = leaving.pool(clean, words, unwell_blocks=False, memory=memory)
        if bye:
            return _choose(bye, memory, clean)

    # "What should I say to my boss?" is not a search: it wants a shape to say it in. Before
    # the taste and live branches, because asking what to say is never a taste.
    # A slip inside the ask hides its shape: "waht shud i tell her face to face" carries "what
    # should i tell" with two letters missing and went to the search hedge, while the same line
    # spelt right was told how to open. So the line is asked twice - as typed first and as repaired
    # second, the way the question test above it already does - and only a line the reading had to
    # repair is asked twice, so a line that reads as typed is untouched.
    asks_for_words = _asks_for_words(clean, words) or (
        repaired != clean and _asks_for_words(repaired, words))
    if WORDING_ASKS_WHO.search(clean) and any(w in EXPERT_WORDS for w in words):
        asks_for_words = True
    if QUOTE_ASKS.search(clean):
        return _choose(QUOTE_LINES, memory, clean)
    if asks_for_words:
        if TELL_HARD.search(clean):
            return _choose(TELL_HARD_LINES, memory, clean)
        if "card" in words:
            return _choose(CARD_LINES, memory, clean)
        return _choose(WORDING_LINES, memory, clean)
    if _asks_how_are_you(plain, understood.get("plain") or "") \
            or understood.get("asks_how_i_am"):
        # The phrase table above holds the spellings it knows; the reading says the same thing
        # about every spelling of the greeting, so "how you been", "hows everything", "what u
        # saying" and "hows the day going" are answered here instead of reaching the search
        # hedge (`bot/understanding/kinds.py::asks_how_i_am`).
        return _choose(HOW_ARE_YOU, memory, clean)
    # A view asked for with nothing named ("whats your honest view?", "honest view?", "your take",
    # "honest answer"): the person is asking the bot to stand behind the answer just given, and a
    # search suggestion there is the bot denying its own paragraph. It is read before the taste
    # pools because "your take" and "what do you reckon" are in both families, and the general
    # taste line ("No strong view on that one, honestly. What's yours?") is the shrug for a
    # question with no answer behind it - said one turn after a full answer, it is a lie.
    taste = _taste(plain, memory, was_taste, asking, repaired)
    if taste:
        state["taste"] = True
        return taste
    # A phone number is wanted in lines that are not questions ("i need the number for the
    # jobcentre"), so it is read before the live pools, which wait for an ask word. Nothing
    # else here answers one, so it takes no answer away.
    number = _their_contact_number(plain, asking)
    if number:
        return _choose(number, memory, clean)
    # A line that only asks the bot to confirm its own limit is a question about the bot, and
    # the honest answer is the one it would give if they had asked it straight: what it cannot
    # do, and the one place that knows. "so you cant check the weather for me", said one turn
    # after the bot had said it had nothing live, got "I'm listening - say more if it helps",
    # which answers nothing at all; "you cant see my calendar can you" got the search hedge,
    # which sends a person to Google to find out what the bot can do. The live pools already
    # know which thing it is and where to find it, so the line is read as the ask it is.
    if _a_no_from_the_bot(plain):
        cannot = _live(plain, True, memory) or _the_live_thing_named(plain)
        if cannot:
            return _choose(cannot, memory, clean)
        if CANNOT_SEE_ANYTHING.search(plain):
            return _choose(CANNOT_SEE_ANYTHING_LINES, memory, clean)
        if CANNOT_READ_YOURS.search(plain):
            return _choose(_what_no_eyes_already_says(plain) or CANNOT_YOUR_OWN, memory, clean)
        if SO_NOTHING_LIVE.search(plain) or (
                _the_bot_says_it_cannot(plain) and CANNOT_ANYTHING_ASK.search(plain)):
            return _choose(CANNOT_ANYTHING, memory, clean)
    live = _live(plain, asking, memory)
    if live:
        return _choose(live, memory, clean)
    # A search that has just ended ("found them, in my coat pocket") is the good half of the
    # same chat, so it is answered as its own news rather than as a fresh topic.
    if loss.found_what_was_lost(clean) and loss.lost_thing_to_find(last_user(memory) or ""):
        return _choose(FOUND_IT, memory, clean)
    # A thing they are looking for is not an unanswerable question: "where are my keys" and
    # "have you seen my passport" want somewhere to look, so this comes before the honest hedge.
    # Standing outside the front door is not a search: the way back in is the answer, and it
    # comes before every "where to look" pool.
    if loss.locked_out(clean):
        if loss.locked_out_of_the_car(clean):
            return _choose(LOCKED_OUT_OF_THE_CAR, memory, clean)
        return _choose(LOCKED_OUT_LINES, memory, clean)
    if loss.keeps_losing_thing(clean):
        return _choose(LOST_A_THING_AGAIN, memory, clean)
    if loss.lost_thing_to_find(clean):
        return _choose(LOST_A_THING, memory, clean)
    # A verdict on the person's own worth is not a question for the bot, whatever grammar the
    # line arrived in: "my best isnt good enough" was read as a question and got the honest
    # hedge ("a quick search will get you a solid answer"). The same goes for the one lost line
    # that is written as a question ("what am i even doing with my life"). Both pools name the
    # thing and ask one question back, so they beat the hedge here.
    # Not being seen by the people around them is not a fact to file and not a question for the
    # bot: "i feel like nobody cares" was answered with the line said back ("you feel like nobody
    # cares - noted"), which is the loneliest reply there is. The reading is `bot/compose/unseen`
    # so the echo in `bot/memory/ack` can stand down for the same lines.
    if unseen.reads(clean):
        return _choose(unseen.LINES, memory, clean)
    own = _own_feeling(clean) or (
        NO_DIRECTION_REPLY if LOST_QUESTION.search(clean) and not NOT_SELF.search(clean) else None)
    if own:
        return _choose(own, memory, clean)
    # A routine, a habit or a day that keeps getting away: the composer can give a method, so
    # it does, instead of the shrug it gives a question it cannot answer.
    routine = _routine_pool(clean, words, memory)
    if routine:
        return _choose(routine, memory, clean)
    # A rating of one of their own skills is not a verdict on the person and not a bad day: "im
    # rubbish at saving" was filed away by the neutral nod ("Got it. Is there anything you'd like
    # a hand with?") and "im terrible with names" was read as heavy news ("Ugh, that's a lot to
    # carry"). The pools that treat it as self-blame already stand aside for it (RATES_A_SKILL);
    # this is what it gets instead. It sits after the routine and the wording answers, which are
    # more use to the line ("im rubbish at mornings" keeps the morning method), and before the
    # hedge and the gentle pools, which give it nothing.
    if (I_RATE_A_SKILL.search(clean) and not WORDING_ASKS.search(clean)
            and not A_WAY_OF_BEING.search(clean)):
        return _choose(ONE_SKILL_RATED, memory, clean)
    # ...and the same thing asked as a question, which is the shape that got the search hedge: "am
    # i any good at my job" was told a link would sort it out, and "am i a good mum" and "am i good
    # enough" got the nod or the hedge. They sit here rather than with the self-blame pool above
    # because the ask is what the line is: a question that wants a mark nobody can give, and the
    # one useful thing left to say is the question about what happened. A line with an ask of its
    # own ("am i good enough what should i do") keeps its own answer, as the statement version does.
    if not SELF_BLAME_ASKS.search(clean):
        if A_SKILL_ASKED_OF_ME.search(clean) and not A_WAY_OF_BEING.search(clean):
            return _choose(ASKED_A_RATING, memory, clean)
        if A_GOODNESS_ASKED_OF_ME.search(clean):
            return _choose(ASKED_IF_GOOD, memory, clean)

    # A bare "why" asks for the reason behind the answer just given. It has no words of its own
    # to match, so nothing above could take it, and the search hedge throws the last turn away:
    # the reason is not something this bot can see, so it says that and asks what would narrow it
    # (bot/compose/why.py).
    why_follow_up = why.respond(clean, memory, understood,
                                body=_thread_is_about_the_body(memory))
    if why_follow_up:
        return why_follow_up
    # A job asked of the bot itself, in the imperative ("take the rubbish out") or politely
    # ("can you ring the school for me"): neither is a question to search for nor a statement to
    # file away. The limit is the answer, so it comes before the hedge, and each shape of job
    # says what the bot can offer instead.
    asked = _act_asked_of_me(clean)
    if asked:
        return _choose(asked, memory, clean)
    if _acts_for_me(clean, memory):
        return _choose(ACTS_FOR_ME, memory, clean)
    # A job in the world typed as an order rather than as a polite ask: "text my mum", "book the
    # tickets", "set a timer for 10 minutes". Nothing above claims them and the store's nod read
    # as a job done, so the limit comes next, before the hedge.
    ordered = _an_order_it_cannot_do(clean)
    if ordered:
        return _choose(ordered, memory, clean)


    # A lump keeps its own answer even where a specialist is named: the line that names one
    # would be right ("a pharmacist or your GP can answer that today"), and for a lump the GP
    # line says the same thing and says what to do ("ring your GP surgery and say you have
    # found a lump"), where the named line hedges ("not mine to decide, sorry").
    if reads_like_a_symptom(repaired.lower()) and _LUMP.search(repaired):
        return _choose(LUMP, memory, clean)
    settled = " " + re.sub(r"[^a-z0-9']", " ", clean) + " "
    if (reads_like_a_symptom(repaired.lower())
            and not _who_for(clean, settled, settled.replace("'", "").split())
            and not (trouble.reads_as_trouble(clean, words, repaired) == "sore"
                     and not _CAUGHT.search(clean))
            and says_it_has_lingered(repaired, illness=bool(_ILL.search(repaired)))):
        return _choose(SYMPTOM_LINGERS, memory, clean)
    # A body complaint asked as a question is not an unanswerable question when nobody else can
    # be named for it: "what should i do about my bad back" got "I'd rather not guess. A quick
    # search online will get you a solid answer", and the warm line for a back that is bad ("go
    # easy on yourself today, and see someone if it's not shifting") is the friend's answer.
    if (asking and reads_like_a_symptom(repaired.lower())
            and not _who_for(clean, settled, settled.replace("'", "").split())
            and not (trouble.reads_as_trouble(clean, words, repaired) == "sore"
                     and not _CAUGHT.search(clean))):
        return _choose(SYMPTOM_COLD if _ILL.search(repaired) else SYMPTOM, memory, clean)
    # A lateness report is not a question nobody can answer: "im running late for the school pick
    # up" was read as an ask and got the search hedge, and "im running late for work" was read off
    # its verb as a job under way ("im painting my kitchen") and cheered. Both are the same line
    # as "im late for work", so all of them get the one useful reply. A line that asks something
    # on top of it ("im late again, what do i say to my boss") keeps its own answer below.
    if _a_lateness_report(clean, (understood or {}).get("norm_text") or ""):
        pool = (LATE_BEHIND_LINES
                if "behind" in clean or "behind" in ((understood or {}).get("norm_text") or "")
                else LATE_NOW_LINES)
        return _choose(pool, memory, clean)

    # An invitation is somebody asking for company, and nothing about the world answers it: "do
    # you fancy a walk" got the search hedge, "you up for a walk" the neutral nod and "want a
    # brew" the floor. The honest warm line comes before both.
    invited = _an_invitation(clean)
    if invited == "talk":
        return _choose(INVITED_TO_TALK, memory, clean)
    if invited:
        return _choose(INVITED, memory, clean)
    # A line that only narrows the answer above goes back to it. "we fancy a few days away in
    # october" was answered with four destinations, and "somewhere thats not too far" got "Got it.
    # Is there anything you'd like a hand with?"; "cheaper" the same, "under 20 minutes" was said
    # back as "Got it - under 20 minutes", and "not too far" after "we want a day out" got "Thanks
    # for telling me - I'm here if you want to dig into any of that". Nothing in the line names a
    # subject, so it falls past every reader that would give it a topic and lands on the ack: what
    # it does is choose a direction to cut in, and the answer to cut is still on the screen. The
    # axis is read from the line and the reply goes back to "those" with the one question that
    # pins it, which is what a friend says to "somewhere not too far".
    # A line with two limits in it is tried one limit at a time, in the order `the_limits_said` puts
    # them: the bound-carrying part first, then the last said. Only a limit the answer above can be
    # cut on gets the reply, so "under 500 pounds each and not too far" after four destinations that
    # quote no prices is the distance question, not a budget one; and the bound is taken from the
    # part it belongs to, because read off the whole line "under 500 pounds and close" says the
    # person's own words back as the bound.
    limits = the_limits_said(clean) or [(reads_as_a_narrowing(clean), "")]
    for axis, part in limits:
        if not axis or not the_answer_to_cut(memory, axis):
            continue
        bound = the_bound_said(part or clean)
        if bound:
            return _choose(BOUND_FOR[axis], memory, clean).format(bound=bound)
        return _choose(CUT_FOR[axis], memory, clean)

    # Somebody close refusing the thing that would help them, and the person caring for them at the
    # other end of the line: "she refuses a pendant alarm" was answered "Got it. Is there anything
    # you'd like a hand with?", "hes 80 and wont use a stick" with "I'm here if you want to dig into
    # any of that", and "he wont go to the doctors" with the floor. Nothing in the file could read
    # it, and the two things worth saying are what the refusal is usually about and the person whose
    # word carries - neither of which is a fact the bot would be guessing at. It sits here, after
    # the emergencies, the goodbyes and the plans, and before the nod: a crisis, a bereavement or a
    # safety thread keeps its own voice, and the second refusal in a thread gets the detail it
    # brings rather than the same paragraph in other words.
    refused = _a_carer_refused(clean) or _a_carer_refused(repaired)
    if (refused and not _hedged_recently(memory)
            and not (_in_a_loss_thread(memory) or _grief_thread(memory)
                     or in_a_safety_thread(memory))):
        pool = {"aid": ELDER_AID_REPLIES, "clinic": ELDER_CLINIC_REPLIES,
                "doctor": ELDER_DOCTOR_REPLIES, "help": ELDER_HELP_REPLIES}[refused]
        said_before = str((memory.get("turns") or [{}])[-1].get("bot") or "")
        if not _in_a_pool(said_before, (ELDER_AID_REPLIES, ELDER_CLINIC_REPLIES,
                                        ELDER_DOCTOR_REPLIES, ELDER_HELP_REPLIES,)):
            return _choose(pool, memory, clean, clean + " " + _the_line_before(memory))

    # A thing of theirs on their own side, handed over or asked about. The asks are read in
    # `_unknown` below; a line that hands it over ("here's a screenshot", "the link is www...")
    # is not a question at all, so it never reaches there and used to get "Got it. Is there
    # anything you'd like a hand with?" as though the picture had arrived.
    handed = no_eyes.handed_you_something(clean)
    if handed:
        return _choose(handed, memory, clean)

    # "help me fill in this form" asks the bot to do something to a thing on the person's side and
    # is not a question, so it never reached `_unknown` where the same reader answers "can you fill
    # in this form", and it got the search hedge. The limit is the same whoever phrases it.
    # A mark on their own body is not a page on their screen: "can you see if this mole is ok"
    # holds "see" and "this", so the reader below reads it as the text they are looking at and
    # answers "I can't see the page you're looking at - paste the bit you want help with". The
    # pool above already asks the body reader first for the same reason; this is the other way
    # into the same line, so it asks first here too.
    body_lines = no_eyes.look_at_a_body_lines(clean, None, memory)
    if body_lines:
        return _choose(body_lines, memory, clean)
    cannot_see = no_eyes.cannot_see_your_thing(clean)
    if cannot_see:
        return _choose(cannot_see, memory, clean)

    # "Am i bothering you", "am i bugging you", "do you mind me asking", "should i stop asking":
    # the apology for asking turned into a question, and the person wants to hear that they are
    # welcome rather than an answer about anything. It goes above the door below, which sends
    # every unclaimed question to the search hedge - the web was searched for whether the bot
    # minds being asked - and the pool is the one the apology for asking already gets. The mood
    # is not read first: "annoying" in the line would make it a bad mood.
    if _am_i_a_nuisance(clean) and not _grief_thread(memory) and not in_a_safety_thread(memory):
        return _choose(SORRY_FOR_ASKING, memory, clean)

    # Nothing here can answer it: say who can, when the line names that world, and stay
    # honest when it does not. A correction is not that: "no it was my idea not the kids" takes
    # something back, and the hedge sent the person to a search engine to do it ("I don't know
    # enough to answer that honestly"). It is answered where the other corrections are, at the
    # end of the chain (`A_CORRECTION_TAKEN`), so the echo and every reading with something of
    # its own has already had its turn by the time it is reached.
    if asking and not _takes_something_back(clean, memory):
        # A line about how the person is, typed in the shape of an ask, reaches this door and
        # nothing else: "nothing feels worth doing", "nothing is worth it any more", "nothing
        # feels good". Nothing here can look it up and no page knows them, so the hedge ("a quick
        # search online will get you a solid answer") is a shrug at the person it is said to. The
        # gentle pools are what this file says to a low line everywhere else, and the reading that
        # puts the pleasure-gone family together is the same one `_mood` uses, so the two cannot
        # disagree about a line.
        if reads_as_no_pleasure(clean) or (repaired and reads_as_no_pleasure(repaired)):
            return _choose(PLEASURE_GONE_LINES, memory, clean)
        step = step_when_low(clean, memory, COMFORT_SAID)
        if step:
            return step
        # The one ask that is always answerable: whether this program can drive, smell, feel pain.
        # Above the hedge, because there is nothing to look up, and below everything else, because
        # a line about a thing of theirs has already been answered by now.
        if reads_as_a_question_about_the_bot(clean) or reads_as_a_question_about_the_bot(repaired):
            return _choose(ABOUT_THE_BOT_LINES, memory, clean)
        unknown = _unknown(understood, memory, clean)
        # A question about clothes that no clothes row answered still has the rule that decides it
        # and one question to narrow it, which beats sending the person to a search engine with
        # the question they just asked. Only the hedge is replaced: a route to the place that does
        # know ("the dress code is on the invite") is still the better reply when there is one.
        if _a_wear_ask_about_a_day(clean, repaired, text) and is_a_hedge(unknown):
            return _choose(_the_wear_pool_for_the_line(clean, repaired, text), memory, clean)
        return unknown

    # The bot's own last turn offered to write the message, and this line is that detail.
    # Handing it back ("Got it - you're off sick tomorrow") is the one reply the offer rules out,
    # so below the news, the symptoms and the losses (a death is condoled, not drafted) and above
    # the topic entries, which is the half that has to lose the turn.
    drafted = draft.drafter(memory, text, words)
    if drafted:
        return _choose([f'{lead} "{drafted}"' for lead in draft.LEAD_INS], memory, clean)
    if draft.not_the_message(memory, text):
        # The offer is still open: a complaint is not the message, so ask for the words instead of
        # quoting "my boss is a nightmare" back as a text to send.
        return _choose(draft.NOT_YET, memory, clean)

    if _reads(reads_as_pregnancy_bleeding, clean, repaired):
        return _choose(PREGNANCY_BLEEDING, memory, clean)
    if a_fresh_death_and_the_words(clean):
        # The death is the whole line and the ask is the words: the pool for it, before the
        # condolence, which is what the line above would answer this turn with.
        return _choose(THE_FIRST_HOUR_AND_A_CHILD, memory, clean)
    if _reads(reads_as_sudden_loss, clean, repaired):
        return _choose(SUDDEN_LOSS, memory, clean)
    if _reads(reads_as_recovery, clean, repaired, lower=True) and not _in_a_loss_thread(memory):
        return _choose(RELIEF, memory, clean)
    # A test that came back clear is the same news as "the pain has gone": relief said back, not
    # congratulations and not the gentle pool. It has its own reader because the subject is often
    # somebody else ("my mums cancer is in remission"), which `reads_as_recovery` excludes.
    if _reads(reads_as_a_clear_result, clean, repaired, lower=True) and not _in_a_loss_thread(memory):
        return _choose(RELIEF, memory, clean)
    # The same news about someone else, or about the thing that was wrong - "hes ok
    # now", "its gone down now" - but only while a worry is on the table: in a chat
    # about a broken phone these are still an echo of a detail.
    if (reads_as_settled(clean.lower()) and worry_on_the_table(memory)
            and not _in_a_loss_thread(memory)):
        return _choose(RELIEF, memory, clean)
    # Being turned away from work is not bad news to be gentle about and not small talk: the
    # closed-door pool names the door and asks the one question worth asking.
    if _reads(reads_as_a_closed_door, clean, repaired):
        return _choose(CLOSED_DOOR, memory, clean)
    if _came_back(clean) and in_a_safety_thread(memory):
        # "i cut my hand and it wont stop bleeding" then "sorry i went quiet" was answered "No
        # bother at all - go on": a breezy hand-back to somebody who has just been told to keep
        # pressing on a wound. The pause is still a go-ahead, in the voice of the thread it is
        # said in - the same reasoning as the condolence below, and the same `in_a_safety_thread`
        # the rest of this file asks before it answers an emergency with anything lighter.
        return _choose(PAUSE_IN_A_SAFETY_THREAD, memory, clean)
    if _came_back(clean) and not _grief_thread(memory):
        # The thread paused for a minute; the apology is the whole content of the line. After a
        # condolence it is not: "sorry i went quiet" there is the person coming back to the
        # hard thing, and the listening line keeps the floor with them.
        #
        # It comes before the bad news, because the word that made the mood sad is usually part
        # of the apology itself ("sorry, i lost track" has "lost" in it) and the reading only
        # says this when nothing else is in the line: "sorry i missed your message, my mum died"
        # is still the death's.
        return _choose(CAME_BACK, memory, clean)
    # The leaving said about the partner without the "me" ("my wife is leaving and i dont know
    # what to do", "i think my partner wants to leave") is not read as bad news by the gate below,
    # which looks for the words of a loss, so it fell through to the stock nod. It is the same
    # news as being left and it gets the same pool, before anything else reads the line.
    if (_reads(reads_as_the_leaving, clean, repaired)
            and not _reads(reads_as_the_speakers_own_plan, clean, repaired)
            and not _a_things_state(memory, clean)):
        return _choose(
            LEFT_POOL_GONE if reads_as_a_leaving_already_gone(clean) else LEFT_POOL,
            memory, clean)
    # A relationship ending the person is deciding on is not news that happened to them: "im
    # leaving him tonight" is a decision, and "Sorry to hear that" is what you say to the person
    # it happened to. Those lines have their own answer below (RELATIONSHIP_DECISION, then PLAN
    # for a next step), so the sad pool stands down for them and stays for the turn that is
    # about being left. ack's reading keeps LEFT_PLAN whole, because after "im thinking of
    # leaving my husband" the next line is still the middle of a story.
    # A standing situation of theirs, said on its own ("i rent", "im a carer", "im self
    # employed", "im on benefits", "im disabled", "im divorced"): where they are starting from,
    # not a job to chat about, not a small day that went by, not bad news and not a fact to file
    # away. It comes before the mood's own pools for that reason - the small-day pool answered
    # "im disabled" with "Good to hear. What was the best bit?" and the receipt answered "i
    # rent" with "Thanks for telling me", and the sad pool read "im divorced" as news. Only a
    # whole line is a situation, so a line that goes on to say something else ("i rent and the
    # boiler is broken") keeps the reading it has (bot/compose/circumstance.py).
    situation = circumstance.pool(clean)
    if situation:
        return _choose(situation, memory, clean)
    # The figure of speech is not bad news, whatever the sad words in it: "i keep killing myself
    # laughing" is read as a trouble by the sad words alone, and the gentle pool answers it with
    # "ugh, that's a lot to carry" for a person who is laughing. The idiom has its own light line
    # further down, so this stands aside for it.
    # A named condition on someone they look after, a child they are kept from, a court letter
    # or a house that has to go names nobody who can settle it, so the gentle pool is the answer.
    # An award stopped or refused is the other kind of line: where the person whose job settles it
    # can be named ("they stopped my universal credit" -> MoneyHelper, a frozen pension the same),
    # the pointer is concrete and "I'm sorry - that's frustrating" is not, so the award stands
    # aside and the pointer keeps its turn. It is the award alone: a house sold to cover the
    # mortgage names a mortgage and is still not a money-advice question.
    # A home entered is not the gentle pool's line either: "someone broke into our house" is read
    # as bad news and answered "Ugh, that's a lot to carry", and a person who has just been
    # burgled needs the order of the two phone calls first.
    broken_into = remark.break_in_reply_for(clean, words, memory)
    if broken_into:
        return broken_into
    if (_reads(reads_as_bad_news, clean, repaired)
            and not _reads(reads_as_the_speakers_own_plan, clean, repaired)
            and not PLAN_IDIOM.search(clean)
            and not (_reads(reads_as_an_award_lost, clean, repaired)
                     and who_settles(clean, memory))):
        if _a_things_state(memory, clean):
            return _choose(A_THING_LOOKS_SAD, memory, clean)
        if _reads(reads_as_the_leaving, clean, repaired):
            return _choose(
                LEFT_POOL_GONE if reads_as_a_leaving_already_gone(clean) else LEFT_POOL,
                memory, clean)
        # "That's frustrating" is a word for a setback, and half of this list is a person: a dad
        # with parkinsons, a daughter taken into care, a roof that has to go. Those keep the pool
        # without that one line (NAMED_NEGATIVE); a court date and a wage stopped are the other
        # kind and keep the whole pool.
        # The third refusal is not the first one: "my dla got refused again" is a line whose one
        # concrete thing is the repeat, and the gentle pool answers it as if it were new
        # ("Sorry to hear that"), which loses the only part of it a friend would pick up. The
        # repeat pool is below this gate and would have answered it, so the gate stands aside for
        # that shape alone; read here so nothing else between the two can claim the line.
        if remark.reads_as_report(clean, words) == "again":
            again = remark.report_reply_for(clean, words, memory)
            if again:
                return again
        # A heart attack, a cancer, an operation, the hospital: news about someone close has no
        # next step to offer and no "it depends" to weigh, so the gentle pool's "that's
        # frustrating" is too small a word for it. Asked as a question ("my dad had a heart
        # attack, what do i do") it is not this pool's: that line wants the practical answer the
        # rest of the file gives, so the pool is only for the news as news.
        if not asking and _reads(reads_as_someone_close_is_ill, clean, repaired):
            return _choose(SOMEONE_SERIOUSLY_ILL, memory, clean)
        pool = NAMED_NEGATIVE if _reads(reads_as_news_with_a_name, clean, repaired) else NEGATIVE
        return _choose(pool, memory, clean)
    # Somebody they love is leaving: "my daughter is leaving home for uni", "my best friend is
    # moving away", "my neighbour is moving away and i will miss her". It sits here, above the
    # echo and above the gentle pool, because the two things the person can get here both say
    # nothing about the thing that is happening: "Noted: your daughter is leaving home for uni"
    # is the coldest line this file has, and "that sounds rough" is sympathy for a change that
    # may be half proud. It is below the bad-news and separation pools, so a death, an ending or
    # an emergency is still theirs.
    if (not asking
            and not _in_a_loss_thread(memory)
            and _reads(LEAVING_A_PERSON.search, clean, repaired)
            and _reads(LEFT_BEHIND.search, clean, repaired)
            and not _reads(NOT_LEAVING_ANYONE.search, clean, repaired)):
        is_a_child = _reads(A_CHILD.search, clean, repaired)
        has_happened = _reads(THE_LEAVE_HAS_HAPPENED.search, clean, repaired)
        if has_happened:
            pool = A_CHILD_LEFT if is_a_child else SOMEONE_GONE
        else:
            pool = _only_what_the_line_gives(
                A_CHILD_LEAVING if is_a_child else SOMEONE_LEAVING, clean)
        return _choose(pool, memory, clean)
    # A complaint about someone else, or a penalty that landed on them ("my boss had a go at me",
    # "i got a parking ticket") is not small talk: the stock nod answers it with nothing. The
    # gentle pool is the word for it, and it is never said back (ack.COMPLAINT).
    if _reads(ack.COMPLAINT.search, clean, repaired):
        if _a_things_state(memory, clean):
            return _choose(A_THING_LOOKS_SAD, memory, clean)
        return _choose(NEGATIVE, memory, clean)

    # "what am i even doing with my life" is not a question for the bot: it is the person
    # saying they are lost, and the honest hedge ("a quick search will get you a solid answer")
    # is nonsense for it. So it is answered with the direction pool before the hedge, which is
    # the one place it can be, because the line is read as a question.
    # Somebody asking the bot for something that nothing could answer must not get a neutral
    # nod ("got it, is there anything you'd like a hand with?"): it ignores what was asked. Say
    # plainly that this one is beyond what the bot knows, and stay useful.
    # A correction is not an ask to the bot, though the words inside it can look like one: "no it
    # was my idea not the kids" is a statement, and the reading of it as an ask sent it to the
    # search hedge - "I don't know enough to answer that honestly" - for somebody putting the bot
    # right. It is answered at the end of the chain, with the other corrections.
    if (_asks_the_bot(understood) and not _takes_something_back(clean, memory)
            and not _reads_value(_a_good_time, clean, repaired, memory)
            and not _reads(reads_as_a_win_nobody_noticed, clean.lower(), repaired.lower())
            and not _a_good_time(clean, memory)
            # A doubt about what to do is read as a question for the bot, and nothing in the
            # knowledge could answer it, so it took the search hedge - "a quick search online
            # will get you a solid answer" for "no idea what to do next" and "i have no idea what
            # to do". It is not a fact to look up: the open doubt pool below asks the one question
            # that gets at it, and it is reached from here now instead of after the hedge.
            and not (_reads_as_dither(clean, repaired) and _weighs_a_choice(clean))
            and not _a_dead_end(clean) and not _the_person_they_are_stuck_on(clean)
            # "good to know" reads as an ask to `_asks_the_bot` ("good" is an imperative verb by
            # grammar) and there is nothing in it to look up, so it took this door: "I'd rather
            # not guess. A quick search online will get you a solid answer" for somebody saying
            # the answer was useful. It is acknowledged by the thanks pools below, like any other
            # "thanks" - the line asks for nothing and the one thing it must not get is a search.
            and not _acknowledges_alone(clean)):
        # A good time said plainly ("best day ever", "great day today") is not a request, and
        # "I'd rather not guess, do a search" answers it by sending them to Google. Neither is a
        # win with a silence round it: "i got the job and nobody said anything good" has the words
        # of an ask for tips and is a letdown, so the search hedge is the last thing it needs.
        tips = _tips(memory, clean, repaired)
        if tips:
            return tips
        # A request the bot cannot answer still wants the reply its shape asks for: "help me
        # write an email to the council" is a wording request, not a fact question, so it gets
        # the same offer to draft as "can you help me write a text to my boss". One place works
        # out which pool that is (`unknown_pool`), so both doors open on the same lines.
        #
        # "i have no idea what to do" is this block's line said from the other end: it names
        # nothing to look up, and a search engine is the worst reply to somebody asking for a
        # hand. The offer the bare "what should i do" already gets is the reply, so the lost ask
        # is read at the same door - only the shape, because everything with a subject of its own
        # has already answered above. A thread already working through advice keeps it: "the
        # boiler is broken" then "i dont know what to do" is the next step of that advice, and
        # asking what has gone on reads as a bot that was not listening.
        free_time = _the_stretch_of_time(clean, memory)
        if free_time:
            return free_time
        lost = the_lost_ask_reply(memory, clean, repaired)
        if lost:
            return lost
        pool = unknown_pool(clean, words)
        if pool is UNKNOWN_WORD:
            # The same drafting chooser as the pool reader's own door, imported on the call the
            # way `fallback.py` reaches that module: asking who it is for after the person has
            # just said who it is for is the failure this stands down from.
            from .fallback_pools import _drafting_pool
            return _choose(_drafting_pool(clean), memory, clean)
        # A request the bot cannot answer often names the thing that can: "find me a plumber near
        # me" wants somebody local and no list of them is here, so the search hedge, which says a
        # search will sort it out without saying where, is the weakest of the honest replies.
        # The route pool names the one place and the one question, and it stands down on its own
        # for everything it cannot route better than the hedge.
        routed = finding_out.for_the_ask(clean, repaired, understood)
        if routed:
            said = _choose(routed, memory, clean)
            if said:
                return said
        # A question about clothes that no clothes row answered - the occasion is one the tables
        # do not have, or the ask was said the long way round - still has the rule that decides it
        # and one question to narrow it ("a layer you can take off, and shoes you can spend the
        # day in", then whether it is indoors or out). The hedge sends the person to a search
        # engine with the question they just asked, which for clothes is never the best reply
        # here: what decides it is the weather and how long they will be on their feet, and that
        # is true of every occasion, including the one the bot has never heard of.
        if _a_wear_ask_about_a_day(clean, repaired, text):
            return _choose(_the_wear_pool_for_the_line(clean, repaired, text), memory, clean)
        return _choose(UNKNOWN, memory, clean)
    # "Any tricks" is the same plea as "any tips" and the same shape: a statement by grammar
    # ("any tips" has no ? and no wh-word either, and it is answered here through `_asks_the_bot`).
    # The word "tricks" is the one the reading does not treat as asking, so it used to fall through
    # to the flat nod. It sits here, below the safety and bad-news reads, so a plea for tricks in a
    # line about bleeding or a death still gets the emergency rather than "what have you tried".
    if _reads(_is_a_tips_ask, clean, repaired):
        tips = _tips(memory, clean, repaired)
        if tips:
            return tips
        return _choose(TIPS_LINES, memory, clean)
    # A statement of trouble ("my landlord wont fix the damp") is not a question, but the same
    # person can settle it, so name them rather than nodding.
    told = _trouble(memory, repaired, words)
    if told:
        return told

    # "anything else" on two words is a request for more of the answer just given, not a nod:
    # the flat pool here asks "is there anything you'd like a hand with", one line after the
    # bot has just answered the same subject.
    if (asks_for_more(clean, memory) and not _hedged_recently(memory)
            and _answered_recently(memory)):
        return _choose(HELP_ALREADY, memory, clean)
    if _in_sudden_loss_thread(memory):
        # The next line of that chat ("my partner wont talk about it") is still the same loss, so
        # it is answered with room to say more, not with a stock line that fits any message. It
        return _choose(loss.AFTER_REPLIES, memory, clean)
    if len(words) <= 2 and set(words) & ACKS:
        if _a_loss_recently(memory):
            # "mm" and "ok" are how a person answers a condolence, and ACK's first line is
            # "Great — shout if you need anything else": after "the funeral was yesterday" the
            # bot told them great and offered a hand with anything. Answer the nod with room to
            # say more instead.
            return _choose(loss.AFTER_REPLIES, memory, clean)
        if _the_last_line_was_bad_news(memory):
            # "Great — shout if you want anything else" is the nod pool's first line, and after
            # "my mum has cancer" it congratulates the person on the news. A nod to heavy news is
            # them taking it in, so it gets the same room to say more a condolence gets - the
            # pool main already uses for "i lost my job" / "mm".
            return _choose(loss.AFTER_REPLIES, memory, clean)
        if _the_last_line_was_a_fault(memory):
            # "my knee is sore when i run" is everyday trouble, not heavy news: no congratulation,
            # no laugh, and no question, which asks them to start again on a subject still open.
            return _choose(ACK_AFTER_TROUBLE, memory, clean)
        if _the_last_line_was_heavy(memory):
            # One step away from a fault: the bot's own line was a condolence or a sorry ("im
            # really sad" / "mm" was told "Great — shout if you need anything else"). The nod
            # there is the person staying in the room, so it gets room and no cheer.
            return _choose(ACK_WARM, memory, clean)
        return _choose(ACK, memory, clean)
    # A kept-forgetting habit is a task to sort out before it is a loop ("i keep forgetting to
    # water the plants" has a plant in it), so it is read first.
    if not _in_a_loss_thread(memory):
        if FORGETS_A_CLASH.search(plain):
            return _choose(DOUBLE_BOOKED, memory, clean)
        if FORGET_A_DATE.search(plain):
            return _choose(DATES_KEEP_SLIPPING, memory, clean)
        if FORGET_A_SECRET.search(plain):
            return _choose(SECRETS_KEEP_SLIPPING, memory, clean)
    if FORGETS_AGAIN.search(plain) and not _in_a_loss_thread(memory):
        return _choose(KEEPS_FORGETTING, memory, clean)
    if _is_rumination(clean):
        # A line that says the same thing is going round again ("i keep going over it in my head
        # at 2am", "its been on my mind all week") is not a fact to file away: saying it back
        # returns their own sentence with nothing added, and "noted" is an intake form. The loop
        # itself is worth a word, then the one thing it keeps returning to.
        return _choose(RUMINATION_REPLIES, memory, clean)
    mood = _mood(words, clean)
    # A detail added to the complaint we are already on ("its sore when i sit down" after "how
    # long has it been like that?") is the next line of the same complaint, not a new subject.
    # Nothing in the composer could hold that thread, so it was answered with a stock line that
    # could have come before any message at all. It only fires on one of this module's own
    # questions as the last reply, and only for a line that is a detail about it.
    carried = trouble.carried_on(clean, words, memory)
    if carried:
        return _choose(carried, memory, clean)
    # A result they did not get is not a win and it is not a day that went alright, and every
    # pool reads the result without the "almost" in front of it: "i almost got the job" was
    # answered "Good to hear. What was the best bit?", "i almost won" "Nice one. How did the rest
    # of it go?", and "i nearly broke my pb yesterday" "Right. What have you tried so far?" - a
    # repair question about a personal best. The mood reading already refuses a cue behind
    # "nearly" (`nearly` in bot/compose/__init__.py), and the record reading does too, which is
    # why nothing above answers these lines; what was missing was a reply for the near miss
    # itself. It comes before the trouble question, which read "broke my pb" as a fault.
    if _a_near_miss(clean):
        return _choose(NEAR_MISS_REPLY, memory, clean)
    if mood == "neutral" and repaired and repaired != clean:
        # The reading put the line right ("me n my gf r arguin a lot" -> "me and my gf are
        # arguing a lot") but `_mood` reads the words as they were typed. A cue in the repaired
        # line is a cue in what the person said, so the typed line is read first and this is the
        # second try - the same deal the pools below make with `understood["plain"]`. Without it
        # the quick way of typing the same line gets "Got it. Is there anything you'd like a
        # hand with?" where the spelled-out line gets "Sorry to hear that."
        mood = _mood(_words(repaired), repaired)
    # The warm line is for an illness the person names ("i've got a sore throat", "i think ive
    # got the flu"), not for a body part that hurts: "my knee has been aching for a week" is the
    # trouble module's question, and "rest, warm drinks and an early night" is the wrong advice
    # for a knee anyway. trouble.reads_as_trouble tells the two apart, so it decides this one.
    # The cold's own line ("rest, warm drinks") is kept for an illness it fits; a headache at a
    # desk gets the two lines that suit any symptom.
    # A bug the person caught keeps its advice: reads_as_trouble answers "sore" for a cough as
    # well as for a knee, but "i've had a cough for three weeks now" wants "see someone if it is
    # not shifting", and the trouble question would ignore how long they have had it. So it is
    # only a body part that hurts that hands the line over, and a caught bug is not a body part.
    # Before the person's own symptom, because a cat and a horse are looked after in the same
    # words: "my cat has a bad back" is not "take it slow today".
    if mood != "positive" and _reads(reads_for_a_pet, clean.lower(), repaired.lower()):
        if _reads(reads_as_a_pet_low, clean.lower(), repaired.lower()):
            return _choose(PET_LOW_REPLY, memory, clean)
        condition = _reads(reads_as_a_pet_condition, clean.lower(), repaired.lower())
        return _choose(PET_CONDITION_TROUBLE if condition else PET_TROUBLE, memory, clean)
    if mood != "positive" and _reads(reads_as_a_carer_body, clean.lower(), repaired.lower(),
                                     memory=memory):
        return _choose(CARING_FOR_A_BODY, memory, clean)
    if mood != "positive" and _reads(reads_for_a_carer, clean.lower(), repaired.lower(),
                                     memory=memory):
        return _choose(CARING, memory, clean)
    if (mood == "neutral" and _reads(reads_like_a_symptom, clean.lower(),
                                     repaired.lower())
            and not (trouble.reads_as_trouble(clean, words, repaired) == "sore"
                     and not _CAUGHT.search(clean))):
        return _choose(SYMPTOM_COLD if _ILL.search(repaired) else SYMPTOM, memory, clean)
    if _a_relationship_ending(clean):
        # "i'm finally leaving him" is read as good news by the cue and as a next step by the
        # plan, and both cheer: "Lovely to hear. Enjoy it!" and "Nice one. Let me know how it
        # goes." The decision is the line, so it is answered as one.
        return _choose(RELATIONSHIP_DECISION, memory, clean)
    # A good time had by a group or by an event is a chat nobody can add a fact to, so it gets the
    # warm pool rather than the nod. Before the congratulations, which reads oddly for a party
    # they went to ("Good for you! That sounds like it was worth the wait").
    # Something funny is the good half of a chat, so it is answered with a laugh and a question
    # about it. It sits above the echo and the neutral pool, which between them either said the
    # line back without the smile or treated a laugh as something to sympathise with.
    if a_comparison_of_standing(clean) and not _in_a_loss_thread(memory):
        # Somebody holding their own life up against a crowd's gets the comparison answered, not
        # a cheer for the crowd and not the stock nod. In a loss thread it stands aside: "everyone
        # my age has their mum still" is grief, and the condolence is the right reply to it.
        return _choose(A_COMPARISON_OF_STANDING, memory, clean)
    if (mood != "negative" and not a_limit_on_the_answer(clean)
            and _something_funny(clean, memory)):
        return _choose(A_LAUGH, memory, clean)
    # The person measured against other people: "everyone else seems to have it sorted", "all my
    # mates have bought houses", "im 41 and everyone my age seems busy with kids". Every reader
    # above wants something to answer - a plan, a report, a thing that went wrong - and these
    # carry none of it, so on main they reach the pools that answer nothing: the account of the
    # day ("How was it, overall?"), the cheer the word "sorted" alone earns ("Good to hear. What
    # was the best bit?"), the intake form, or the line said back. What a friend answers is the
    # comparison, not the milestone: nobody's week looks like their update, and the scoreboard is
    # not the person's own. It sits above the good-time and day pools because those are what it
    # was falling into, and below every reading with something of its own.
    if not _in_a_care_thread(memory) and _the_crowd_is_ahead(clean):
        return _choose(A_CROWD_AHEAD, memory, clean)
    if mood != "negative" and _reads_value(_a_good_time, clean, repaired, memory):
        if _in_a_care_thread(memory):
            return _choose(A_GOOD_TIME_IN_A_CARE_THREAD, memory, clean)
        return _choose(A_GOOD_TIME, memory, clean)
    if mood != "negative" and _reads(reads_as_a_win_nobody_noticed, clean.lower(),
                                     repaired.lower()):
        # Two things in one line - the win and the silence around it - and congratulating alone
        # answers half of it. Before the congratulations, which it would otherwise get.
        return _choose(WIN_IN_A_SILENCE, memory, clean)
    if mood != "negative" and _reads(reads_as_a_win_a_cost_came_with, clean.lower(),
                                     repaired.lower()):
        # The same two halves the other way round - the win and what it costs ("we finally got the
        # keys and the place is a state", "we came into some money and now everyone wants it").
        # The cheer ("Lovely to hear. Enjoy it!") answers the first half and is deaf to the second,
        # and the good-news reader cannot be the one to stop it, because this file asks it later
        # and the new-thing reader reads a set of keys as a win on its own.
        return _choose(WIN_AND_A_COST, memory, clean)
    occasion = (reads_as_an_occasion(clean.lower())
                or (reads_as_an_occasion(repaired.lower()) if repaired != clean else None))
    if mood != "negative" and occasion:
        # "its my birthday on friday" is good news with a date on it, and the congratulations line
        # ("Brilliant. Really pleased for you.") reads oddly for it - you wish somebody a happy
        # birthday. Before the good-news branch, which is what a birth or an exam result wants,
        # and before the news-to-come line, which welcomes a wedding or a baby as a thing ahead.
        return _choose(_occasion_pool(occasion, clean), memory, clean)
    ahead_pool = _reads_value(_a_day_ahead, clean, repaired)
    if mood != "negative" and ahead_pool is not None:
        # "my holiday is next week" and "my exam is on monday" were nodded back ("Noted: your
        # holiday is next week"), which is the restatement STYLE.md rules out, and a dated
        # appointment was worse than nodded: "im due at the dentist on friday" wears the due-date
        # pattern in bot/compose/goodnews.py, which is there for a baby, and was congratulated -
        # "That's lovely news - and something to look forward to" - as was "im due in court on
        # friday" and "im due for my jab on monday". A line with a date on it and a tense thing in
        # it is a diary entry, so this sits above the news-to-come branch, and it needs one of its
        # own tone words, so a baby due in june is still good news.
        return _choose(ahead_pool, memory, clean)
    if mood != "negative" and _reads(reads_as_news_to_come, clean.lower(), repaired.lower()):
        # Still to come, so the reply looks forward and never asks how it went. A birthday said
        # with a figure ("my mum is 72 and she is 73 next month") is answered with the figure:
        # the pool above looks forward without saying which birthday, which hands the person
        # their own news back with the number taken out.
        birthday = _a_birthday_still_to_come(clean, memory)
        if birthday:
            return _choose(_the_birthday_said_back(birthday), memory, clean)
        return _choose(NEWS_TO_COME, memory, clean)
    if ack.a_limit_on_the_plan(clean):
        # A limit on the plan is answered with what the bot will do with it, whatever mood the
        # rest of the line is in: "she is 8 months pregnant and cant walk far" is not "Brilliant.
        # Thanks for telling me", which hears the pregnancy and drops the walk. Only a line that
        # is nothing but a limit gets this, so a month they have planned keeps its own reply.
        said_back = ack.a_limit_reply(text, memory)
        if said_back:
            return said_back
    if mood == "neutral" and _dreading(clean):
        # "im dreading monday", "not looking forward to the scan", "i cant face the phone call":
        # mild, and the two pools that could answer them are both wrong - the negative pool is for
        # a bad week and the floor says nothing.
        return _choose(A_DREAD, memory, clean)
    if mood == "neutral" and _wants_it_over(clean):
        return _choose(A_WANT_IT_OVER, memory, clean)
    if mood != "negative" and _reads_value(_looking_forward, clean, repaired):
        # A thing still to come said as a want rather than as news - "i cant wait for the
        # weekend", "roll on friday", "counting down to my holiday", "really looking forward to
        # it", "only 3 days till my holiday" - was at the composer's floor ("I'm listening - say
        # more if it helps"), which answers nothing at all, while the news-to-come pool is the
        # pool for a thing ahead and never asks how it went. Placed after the named events, so a
        # wedding, a baby and a holiday still get their own reading, and before the
        # congratulations, which would cheer a weekend as if it had happened.
        return _choose(NEWS_TO_COME, memory, clean)
    if mood == "neutral" and _reads(reads_as_good_news, clean.lower(), repaired.lower()):
        return _choose(_says_only_what_they_said(CONGRATS, clean),
                       memory, clean)  # a baby is not a fact to file away
    # A thing that has arrived - a rescue greyhound, a kitchen going in, a move - is news the
    # congrats pool cannot say anything about ("Good for you!" congratulates a sofa) and the nod
    # says nothing at all. It keeps its own question, about the thing that arrived. After the
    # congratulations, so a new job or a set of keys is still a win.
    arrived = goodnews.new_thing(clean.lower())
    if arrived and mood != "negative":
        return _choose(goodnews.new_thing_replies(arrived), memory, clean)

    # A regret ("we booked the holiday but now i regret it", "i wish i hadnt booked it") is not a
    # doubt to weigh and not a plan reported: the whole message is the regret, and every reading
    # below answers it with something that is not about it - the nod says nothing about it, and
    # the plan offers a first step for a thing they wish they had not started. It goes above them
    # and below the good news and the news of a thing that arrived, which are not regrets.
    # The repaired line is the second try, which is what carries the same regret typed with a
    # dropped apostrophe ("i shudnt have said anything") to the pool the standard spelling reaches.
    regretted = remark.regret_reply_for(clean, words, memory,
                                        understood.get("plain") or "")
    if regretted:
        return regretted
    idiom = PLAN_IDIOM.search(clean)
    if idiom:
        # "im going to die of embarrassment" is a feeling, and the plan ack answers the wrong
        # thing. A light line back, then the person says what happened.
        return _choose(IDIOM_SHY if "excit" not in idiom.group(0) else IDIOM_GLAD, memory, clean)
    if _plan_reported(clean, mood) and not ack.reads_as_a_trip(clean):
        if reads_as_a_change_of_medicine(clean):
            # "im going to skip my medication for a week" is a decision about a prescription, so
            # it is the one plan that is not blessed: the dose waits for the person who wrote it.
            # Above the done-things pool, because a medicine stopped last week is the same advice
            # and the same 111 line.
            whole = (PLAN_MEDICINE_SLOW_REPLY if PLAN_MEDICINE_SLOW.search(clean)
                     else PLAN_MEDICINE_REPLY)
            return _choose(whole, memory, clean)
        if any(phrase in clean for phrase in PLAN_DONE) and not PLAN_NOT_YET.search(clean):
            # The plan has already happened, so there is nothing to be told how it goes.
            return _choose(PLAN_DONE_ACK, memory, clean)
        # "ok ill book her in tomorrow" is a plan, not a fact. A trip or an occasion is not a
        # next step being reported ("i'm going to a wedding in september" has nothing to be told
        # how it goes yet), so it falls through to the store, which answers with the trip itself.
        return _choose(PLAN, memory, clean)
    promise = _a_promise_that_keeps_moving(clean)
    if promise is not None and mood != "positive":
        # A promise that keeps not happening has no impact word and nothing of theirs in the
        # way, so the grievance reader below could not see it and the line got "I'm listening".
        # It is read first: a promise with a word for the wear in it ("he keeps saying he will
        # sort it and it never happens") is still a promise.
        return _choose(promise, memory, clean)
    if mood != "positive" and _someone_else_minding(clean, words, _grievance_thread(memory)):
        if _grief_thread(memory):
            # "my partner wont talk about it" after a death is part of the grief, not a row about
            # somebody's manners: the last thing they need is "annoying".
            return _choose(GRIEF_AFTER, memory, clean)
        return _choose(GRIEVANCE, memory, clean)
    if mood == "neutral" and _sorry_for_asking(clean):
        # "Sorry to bother you" is manners, not a report: the stock line asks them to say more
        # when they have not said anything yet.
        return _choose(SORRY_FOR_ASKING, memory, clean)
    said = _thanks_then_said(clean)
    if _thanks_news_went_badly(clean):
        # Bad news behind a thanks. It used to fall through to the pools below, which read the
        # line as something new and answered the thanks instead: "thanks, its worse today" got
        # the echo and "thanks, still hurting" got "Got it". The outcome is the line, so the
        # pool that owns bad news answers it, and the person is asked the detail a card needs.
        return _choose(THANKS_NO_BETTER, memory, clean)
    if said:
        # A thanks and the outcome after it. The mood is read on the outcome, not on the whole line:
        # "thanks" in front of it hides the words that say which way it went, and "thanks, it's worse
        # today" was answered "Good. Thanks for letting me know."
        said_words = re.findall(r"[a-z']+", said)
        if THANKS_GOOD_AGAIN.search(said) or (
                not THANKS_WENT_BADLY.search(said) and _mood(said_words, said) != "negative"):
            return _choose(THANKS_THEN_SAID, memory, clean)
    if mood == "neutral" and (_thanks_with_more(clean) or _acknowledges_alone(clean)):
        # "That's good to know, thanks" is thanks with extra words, not a statement to file.
        return _choose(THANKS, memory, clean)
    if mood == "neutral" and (DITHER.search(clean) or DITHER.search(repaired or "")) \
            and HELP_SERVICE.search(clean):
        # A doubt pointed at a service you go to for help asks what to do about a body, so it is
        # the advisor's line, not a weighing: "im not sure whether to take him to the vets
        # tonight" wants the vet's number, and "not sure whether to go to a and e" is a person
        # deciding whether a body needs looking at (warm-feather on #1467). A pet's is the vet.
        if "vet" in clean or "vets" in clean or any(
                word in ANIMALS or word.rstrip("s") in ANIMALS for word in words):
            return VET_WHO
        return _choose(UNKNOWN_HEALTH, memory, clean)
    if mood == "neutral":
        # "i dont know what to do about my mum" names the person the doubt is about and nothing
        # else, so the open pool's "the part of it that won't move" points at a thing nobody
        # said. A friend asks about the person, which is the one question the line has already
        # made possible.
        about_a_person = _a_question_about_the_person(clean, memory)
        if about_a_person:
            return about_a_person
    free_time = _the_stretch_of_time(clean, memory)
    if free_time:
        return free_time
    if mood == "neutral" and _reads_as_dither(clean, repaired) and _weighs_a_choice(clean):
        # "im not sure whether to move in with her" is a decision the person has already put
        # down, so the echo ("I'll remember that") and the nod both answer it with nothing a
        # friend would say. It comes after the symptom, good-news and plan readings, which are
        # different kinds of line, and before the echo, which would otherwise file the decision
        # away as a fact. A doubt about health is the one that keeps the advisor: whether to
        # ring the doctor is not a question the bot weighs.
        if ((set(words) & HEALTH_WORDS and not HEALTH_MODIFIER.search(clean))
                or any(phrase in clean for phrase in CHECK_PHRASES)):
            return _choose(UNKNOWN_HEALTH, memory, clean)
        if DITHER_YES_NO.search(clean):
            return _choose(DITHER_DECIDE, memory, clean)
        if DITHER_OPEN.search(clean):
            return _choose(DITHER_OPEN_LINES, memory, clean)
        return _choose(DITHER_TWO_WAY_LINES, memory, clean)
    # A line with no way in - "i dont know what to do", "im stuck", "where do i start", "no idea
    # what to do first" - names nothing at all, so no reading above can use it and none of them
    # should: it reached the echo ("I'm listening - say more if it helps"), the nod ("Got it. Is
    # there anything you'd like a hand with?") or the search hedge, and there is nothing to look
    # up in a line that has not named anything. It sits here, after every reading that can find
    # a subject, so it only ever replaces a reply that answers nothing, and it asks the one
    # question that gets somewhere: about the trouble when the line above named one, and about
    # what is in the way when it named nothing.
    if mood == "neutral" and _run_out(clean) and not _in_a_care_thread(memory):
        return _choose(RUN_OUT_LINES, memory, clean)
    if mood == "neutral" and _only_the_stuck_phrase(clean) and not _in_a_care_thread(memory):
        # Never in a thread that safety, urgent, loss or grief answered: "i keep thinking about
        # ending it" then "i dont know where to start" is a person saying where the start is, and
        # "what have you tried so far" is the last question to ask them. The gentle pool the
        # fallback already had is the right answer there.
        if A_HELP_WORD.search(clean):
            # "i need help but i dont know what with" is an ask for a hand with the with taken
            # out, and the offer is the answer a friend gives: "of course - what are you stuck
            # on". A question about the part that will not move answers a person who has said
            # what they need least.
            return _choose(HAND, memory, clean)
        if _news_above(memory) or _a_subject_above(memory) or _a_bad_line_above(memory):
            return _choose(STUCK_AFTER_TROUBLE, memory, clean)
        # A bare stuck line is `bot/memory/stuck.py`'s: it carries the news above over, and where
        # it can it answers better than a question ("Tell me what has gone on, even roughly, and
        # I will help you work out the first step"). Read with its own regex, this file keeps its
        # answer by falling through, and keeps the forms it does not read - "i dont know how to
        # start" was the search hedge - and the run-out lines above.
        if not (stuck_line.STUCK.match(clean) or _a_start_ask(clean)):
            return _choose(DITHER_OPEN_LINES, memory, clean)
    # A line that is nothing but a number ("20 mins", "45 a month", "its about 5 miles", "forty
    # minutes each way") is half of a sum, and the sum is the reply: 45 a month is 540 a year, 40
    # minutes each way is 6 hours 40 a week. Today such a line is either filed away ("Got it - you
    # have 40 pounds left for food this week") or dropped in a stock line, and both say nothing
    # about the number the person just gave. It comes after every reading above, because a line
    # with a subject of its own ("i have 2000 saved and no idea what to do with it") is not a bare
    # number and keeps its own reply.
    #
    # A problem stated and left there ("i have a problem", "i got a problem", "problem",
    # "something is wrong", "something happened") is the same kind of line: it names nothing the
    # readings above can use, and it reaches the pools below as a thing done with the day or as a
    # fact to file away. Both say nothing about what the person just said - the intake form ("Got
    # it. Is there anything you'd like a hand with?"), the nod, the echo, and "Good to hear. What
    # was the best bit?" for "i have a problem i need help with" because "need" read as a past
    # tense. The offer is the answer a friend gives, and the question in it is the one that moves
    # the conversation on.
    if _a_problem_stated(clean, repaired):
        return _choose(HAND, memory, clean)
    amount = quantity.reply_for(clean, memory)
    if amount:
        return amount
    # A name that came from somebody ("my son is called after me", "hes named after his grandad"):
    # no pool above reads it, and the store's read-back was all these lines got. It is a whole-line
    # shape of its own, so it costs nothing to read here.
    named_after = _named_after_reply(clean, memory)
    if named_after:
        return named_after
    if mood == "neutral":
        # Before the echo and the nod: something hard said about themselves ("i feel like im not
        # doing enough", "i still dont know what i want to do") is not a fact to file away, and
        # saying it back ("noted: you feel like you're not doing enough as a mum") is not an
        # answer to it either. The pool names the thing and asks one question back.
        own = _own_feeling(clean)
        if own:
            return _choose(own, memory, clean)
        # A knock the person gave themselves ("i hit my thumb with a hammer"). It comes before
        # every pool below, because a sore thumb is not a plan, an arrangement or a small thing
        # done, and the receipt it used to get ("Got it. Is there anything you'd like a hand
        # with?") could have come before any message at all.
        if _a_knock_on_oneself(clean):
            return _choose(KNOCKED, memory, clean)
        if _a_knock_into_a_thing(clean):
            return _choose(WALKED_INTO_POOL, memory, clean)
        # A fall or something sharp underfoot, with no card on it ("my baby rolled off the bed",
        # "i stepped on a nail in the garden", "i got glass in my foot"). It sits with the knocks
        # because it is the same thing - something landing on a person - and, like them, it has
        # to come before the echo and the pleasantry, which filed "i got glass in my foot" back
        # as "Noted: you got glass in your foot." and cheered the rest ("Nice one. How did the
        # rest of it go?"). The question is about how bad it is, because what to do next depends
        # on that and the bot cannot see it.
        if _a_mishap(clean, words):
            return _choose(MISHAP_BACK, memory, clean)
        # Someone who can call them in wants a word (understood["summons"]). It comes before the
        # echo: "Noted: your sons teacher wants a word" gives the person nothing to do, and
        # every one of these lines was answered that way.
        summons = understood.get("summons")
        if summons:
            return _choose(_summons_pool(summons, clean), memory, clean)
        # Something they mean to do ("im thinking of going back to college", "i want to start
        # saving") - a plan, not a fault. The reply is about the first step, which is the part
        # people get stuck on (bot/compose/remark.py). It comes before the echo: a plan said
        # back ("Noted: you want to sort out the loft this weekend") names the thing and still
        # leaves them nowhere to start, and gray-cypress measured the echo claiming these
        # lines. It stays after trouble, because a plan that is also a fault is the fault.
        # An activity the person is into ("im into climbing", "ive got into yoga") is a
        # statement about themselves and nothing else, and every one of these lines got the
        # stocking pool. It comes before the plan reader because "im getting into gardening" is
        # both shapes and the reading names the activity, which is the part a friend answers
        # (bot/compose/remark.py). Whose interest it is, and whether the word "into" means an
        # activity rather than a person or a fight, is already decided there.
        taken = remark.interest_reply_for(understood.get("taking_up"), memory)
        if taken:
            return taken
        planned = remark.reply_for(clean, words, memory, understood.get("topics") or ())
        if planned:
            return planned
        # Something the person has arranged ("i booked flights to spain", "i booked a smear
        # test"). It is not a plan - it is done - so it fell through to the nod or to the echo,
        # and neither says anything about it. It comes before _thing_done_scan and the echo,
        # because the arrangement is the news here.
        arranged = remark.arranged_reply_for(clean, words, memory)
        if arranged:
            return arranged
        # A small thing done with the day, with nothing to add to it. It comes after the plan and
        # the arrangement, which say more than the pool can, and before the echo, which would only
        # say the line back.
        pool = _thing_done_pool(clean)
        if mood != "negative" and pool:
            return _choose(pool, memory, clean)
        # A detail about the thing we are on ("we live in a flat on the third floor", "i can put
        # away about 200 a month") is answered with the thing itself, and it comes before the
        # neutral pool, which would only nod: the stock line could have come before any message
        # at all. A report of a next step is a plan, so it keeps its own reply above.
        # A report of something that has happened ("the shop was shut", "the bus was late
        # again", "i started a new job") is not a question and not a plan, so it fell through to
        # the stock line. A friend answers a small setback with the nuisance it is, the same
        # setback again with "again", and something that has started with one question about how
        # it is going. It comes before the echo, because news is not a fact to file away:
        # "Noted: you started a new job on monday." says the line back and says nothing about it.
        reported = remark.report_reply_for(clean, words, memory)
        if reported:
            return reported
        # A habit said flatly ("i always leave things to the last minute", "i never finish
        # anything i start", "i keep interrupting my sister") is how somebody asks for help with
        # it: nobody tells you a pattern about themselves unless they want it to change. It
        # comes before the echo, because the line back - "Noted: you keep interrupting your
        # sister" - is the reply this file itself calls the coldest one, and `chat` stands down
        # on the same test, so the claim and the reply have to be in the same place.
        if not asking and reads_as_a_flat_habit(text, understood):
            return _choose(HABIT_REPLY, memory, clean)
        # A relationship said to be in trouble ("my marriage is on the rocks", "me and my
        # husband barely talk", "my mum and i dont get on") is not a plain fact to take an
        # interest in and not a fault to troubleshoot. It comes before the echo and before the
        # facts about their people, because both of those answer it as if the person had read
        # out a bus timetable: "Noted: things are bad with your wife."
        together = remark.the_two_of_them(clean, memory)
        if together:
            return together
        # A plain fact about one of their people ("my parents live in derby", "my daughter is
        # 4", "my sister is called meg") is what the store files, and the filing said back -
        # "Noted: your parents live in derby." - is the coldest reply in this file. A friend
        # takes an interest in the person in the fact. It comes before the echo for that
        # reason, and the shapes are whole lines, so a worry about the same person ("my mum is
        # 82 and keeps forgetting things") never reaches it.
        of_theirs = remark.their_people_reply_for(clean, words, memory)
        if of_theirs:
            return of_theirs
        # A place secured in something still to come ("i got an audition", "i got tickets for the
        # match"), read above the receipt: the store files the line and says it back ("Noted: you
        # got tickets for the match"), which answers a thing that has not happened yet with the
        # person's own words. It is above the echo and below the people, and the day question
        # below it stands down for the same shape.
        got_ahead = _a_thing_got_ahead(clean)
        if got_ahead:
            return _choose(got_ahead, memory, clean)
        # How one of their people was *with them* is not a fact about that person: "my mum was
        # funny with me" was filed as a trait ("Noted: your mum was funny with you") and "he
        # snapped at me this morning" got a receipt. A friend asks what set them off
        # (bot/compose/remark.py).
        going_on = remark.their_mood_going_on_reply_for(clean, memory)
        if going_on:
            return going_on
        mooded = remark.their_mood_with_you_reply_for(clean, words, memory)
        if mooded:
            return mooded
        # A thing, or a pile of them, wearing them down ("this spreadsheet is killing me", "i
        # have so much marking to do"). Nothing is broken and nobody else is in the line, so it
        # fell all the way to a stock line that could have answered any message at all. It comes
        # before the echo, which for these says the complaint back and adds nothing.
        wear = worn.reads_as_worn(clean, words, repaired)
        if wear:
            return _choose(worn.pool(wear), memory, clean)
        # A stated dislike with nothing under it to object to ("i hate presenting", "i cant stand
        # cats"). It comes before the echo, which for these is the coldest line in the file.
        disliked = the_dislike_ask(clean, memory)
        if disliked:
            return disliked
        said_back = ack.reply(text, memory)
        # A want somebody the person looks after has ("my son wants a tattoo", "my dad wants a
        # scooter at 78"). Whose the wanting is decides the reply: the person is asking on their
        # behalf, so it gets the first step of that want. It stands immediately above the filing
        # because the filing is the whole fault - "Noted: your son wants a tattoo." says the want
        # back and leaves them nowhere to start - and the filing is all it takes: the store's own
        # shaped answers ("So you are thinking about a horse. Who would look after it in the
        # day?") are better than anything this pool can say and keep their turn. A filing with a
        # guessed feeling on it ("Your son is 16 and wants a motorbike. That is a lot to carry on
        # top of how you feel.") counts as a filing - the mood is invented for a line that never
        # said one, and `remark.a_want_said_back` is what decides which of the two it is.
        if remark.a_want_said_back(said_back, clean):
            theirs = remark.dependant_want_reply_for(clean, words, memory)
            if theirs:
                return theirs
        told = _a_day_told_instead_of_the_receipt(said_back, clean, memory)
        if told:
            return told
        if said_back:
            return said_back
    if mood == "neutral":
        # A plain statement that gave the memory store something is answered with the thing
        # itself ("My sister is called Meg" -> "Your sister is called Meg — noted."), which
        # beats a stock line. News and bad news keep their own replies, so a rescue dog is still
        # "That's great news" and an argument about money is still "That sounds rough".
        of_theirs = remark.their_people_reply_for(clean, words, memory)
        if of_theirs:
            return of_theirs
        # A clock time somebody has to be somewhere by ("i need to be at work for 8", "i have a
        # train at 7", "my shift starts at 7"). It comes before the echo, because the store files
        # the time and says it back - "Noted: you have a train at 7." - which is the coldest
        # version of the one thing in the line worth working back from.
        if _the_morning_has_a_clock(clean):
            said = _the_time_said(clean)
            return _choose(_the_clock_pool(said.group(1) if said else ""), memory, clean)
        said_back = ack.reply(text, memory)
        if remark.a_want_said_back(said_back, clean):
            theirs = remark.dependant_want_reply_for(clean, words, memory)
            if theirs:
                return theirs
        told = _a_day_told_instead_of_the_receipt(said_back, clean, memory)
        if told:
            return told
        if said_back:
            return said_back
        # Something of theirs has gone wrong ("my washing machine is leaking", "my knee has been
        # aching for a week"). The trouble itself is the reply: what it is doing, when it
        # started, what they have tried (bot/compose/trouble.py). It comes after the echo,
        # because a line the memory store can say back is more specific still, and it never
        # fires on a question, a plea for tips, or anything about another person - an emergency
        # about a husband or a baby is not a fault to troubleshoot.
        shape = trouble.reads_as_trouble(clean, words, repaired)
        if shape:
            said = _choose(trouble.pool(shape, clean, memory), memory, clean)
            if said:
                return said
    if mood == "negative":
        # The word that made the mood negative is usually the pain word itself ("my back hurts",
        # "my shoulder is killing me"), so an ache was answered with the gentle pool: "That
        # sounds rough. If you want, I can help you think through what to do next" reads as if
        # the bot had misheard a person saying where it hurts. A body part that hurts is the
        # trouble module's question whatever the mood of the line, on the same terms the symptom
        # branch above uses, so a caught bug ("ive had a cough for three weeks now") keeps its
        # advice: the trouble question would ignore how long they have had it. A line that also
        # says the person is crying or frightened is a feeling line, not a fault to troubleshoot
        # ("my eyes are sore from crying all afternoon"): FRIGHTENED is the reading the file
        # already uses for that, so the gentle pool keeps it.
        shape = trouble.reads_as_trouble(clean, words, repaired)
        if shape == "sore" and not _CAUGHT.search(clean) and not FRIGHTENED.search(clean):
            said = _choose(trouble.pool(shape, clean, memory), memory, clean)
            if said:
                return said
    # A result still in the post ("i dont think i passed", "im waiting to hear about the job",
    # "i havent heard back yet") is not a thing to nod at, and the flat "Got it" is what is left
    # otherwise. The one useful thing a friend says is when, because that is the part the person
    # cannot move and can tell you. Placed after the echo and the trouble question and before
    # the neutral pool, so it can only ever replace a nod, and a line that already says when
    # gets the waiting itself instead of being asked again.
    landed = None
    if not (_in_a_loss_thread(memory) or _grief_thread(memory)):
        landed = _the_news_landed(clean)
    if landed == "bad":
        return _choose(LANDED_BAD, memory, clean)
    if landed == "good":
        return _choose(_says_only_what_they_said(CONGRATS, clean), memory, clean)
    if landed == "landed":
        return _choose(PENDING_LANDED, memory, clean)
    # "Anything I should know about the job" carries the same four words as "i should know by
    # friday", and the wait reading below took them: a person about to accept an offer was asked
    # when they would hear back. The ask is read in `toknow.py`, which also hands it to a card the
    # knowledge base holds when there is one. None is "not this ask", "" is this ask with nothing
    # to add - and then the line goes on past the wait, because a question about a thing is not
    # news in the post either way.
    from .toknow import ask_about_what_to_look_out_for as _ask_about

    answered = _ask_about(clean, memory)
    if answered:
        return answered
    if answered is None and _an_open_result(clean):
        if _a_time_in_it(clean):
            pool = PENDING_WAITING
        elif _a_guessed_result(clean):
            pool = PENDING_DOUBT
        else:
            pool = PENDING_WHEN
        return _choose(pool, memory, clean)
    if opens_with_hello and mood == "neutral":
        # Nothing in this file could answer the line, but it still opened with a hello
        # ("hi sorry, my phone was updating", "hey so im thinking of getting a dog"): saying
        # hello back is warmer than the neutral "got it", which is all that is left.
        # Only when the line carries no news of its own, though: a hello in front of bad news
        # ("hi, i think my waters broke", "hi, my waters broke an hour ago") was losing the news
        # to "Hi! What's up?", and the pool below already has the answer for it. The hello adds
        # nothing to a line that says something; it only decides the reply when it is all there
        # is, which `greeting_only` above has already had its turn at.
        return _choose(GREETING, memory, clean)
    if _reads_as_a_bad_stretch(clean):
        return _choose(BAD_STRETCH_REPLIES, memory, clean)
    # The same clothes question said as a statement rather than an ask - "im going to a do at the
    # golf club and i have no idea what to wear" is not read as asking, so it never reached the
    # arm above and the pools below only have a hedge for it, while the rule that decides clothes
    # is the same rule. It sits here, under every reading that could have something to say about
    # what the line is about, because all that is left below is the hedge and the neutral nod.
    if _says_there_is_nothing_to_wear(clean, repaired, text):
        return _choose(NOTHING_TO_WEAR_REPLIES, memory, clean)
    if _a_wear_ask_about_a_day(clean, repaired, text):
        return _choose(_the_wear_pool_for_the_line(clean, repaired, text), memory, clean)
    # A follow-up that names a new thing for the question before it ("and in the freezer too",
    # "what about the shed") is a question about that thing, even when it is said without one: it
    # has an answer somewhere or it has none. When answers has refused it - there is no entry for
    # the freezer - the honest hedge is what fits, because "Thanks for telling me - I'm here if
    # you want to dig into any of that" hears the line as something said about the person and
    # leaves the freezer where it was. Only a neutral line gets here: a follow-up that carries
    # trouble of its own ("and my neck hurts too") is answered above.
    # A correction is not that question: "sorry, i meant next august" takes something back, and
    # the search hedge would answer it as if they had asked about next august (see facts'
    # correction openers, which is where a correction is read).
    if mood == "neutral" and not _A_CORRECTION.match(clean) and swap.rewritten(clean, memory):
        return _choose(UNKNOWN, memory, clean)
    # "my landlord is a joke", "my job is a nightmare", "the buses are a joke round here": a
    # verdict on a thing of theirs is a complaint. The one thing it must not get is the punchline
    # pool ("joke" is in the line) or the note-back that files the verdict as a fact ("Noted: your
    # job is a nightmare."). It sits low, above only the last pools, because a verdict says how
    # the person feels about a thing they named, and a thing with an answer of its own keeps it:
    # "my boiler is a nightmare" is still the plumber's, "my rota is a nightmare" still the rota's.
    if verdicts_a_thing(clean):
        return _choose(NEGATIVE, memory, clean)
    # A body state and nothing else - "im cold", "im starving", "my hands are freezing" - is a
    # line no module has anything to say about, so it reached the neutral nod. It comes last,
    # after every reading above that might have something better: a line that names a fault or
    # a result is not this, and a cold room with the heating broken is still the trouble one.
    state = _body_state(clean)
    if not state:
        # A state typed with a syllable dropped is repaired by the reading ("im starvin",
        # "im nakerd", "im sare"), and the pools only know the word it repairs to. The typed
        # line is asked first, so nothing whose own spelling is a state moves; only a line
        # whose repair is the whole state reaches the pools.
        repaired = understood.get("plain") or ""
        if repaired and repaired != clean:
            state = _body_state(repaired)
    if state:
        return _choose(BODY_POOLS[state], memory, clean)
    # The same thing done, for a line whose mood is not neutral: "hired" and "sorted" are
    # good-news cues, so "hired a van" was read as a win and cheered with "Lovely to hear. Enjoy
    # it!" - a van is borrowed for the afternoon, not a thing to enjoy. Only the cheer is
    # replaced here; a neutral line has already had its turn above, after the plan and the
    # arrangement. A mood word on a thing of theirs is still the thing's, so it keeps the pool
    # below.
    pool = _thing_done_pool(clean)
    if mood != "negative" and pool and not _a_things_state(memory, clean):
        return _choose(pool, memory, clean)
    if mood == "negative" and _a_things_state(memory, clean):
        # The last pool of all: a mood word on a thing is still the thing's, not the person's.
        return _choose(A_THING_LOOKS_SAD, memory, clean)
    # The same doubt as "am i too old", said as a fact about themselves: "i want to start
    # running" / "im 44 and quite unfit" reached the neutral nod, and "Got it. Is there anything
    # you'd like a hand with?" answers the fact instead of the doubt - it is the line that fits
    # any message. The age and the fitness are what people offer as the reason not to start, so
    # they get the doubt answered and the plan kept small. It sits here, above nothing but the
    # neutral pool, so every reading with something of its own has already had its turn - and it
    # keeps out of a body thread, where "im 34 and my knee gives way when i run" is a knee
    # question.
    if (A_BIT_PAST_IT.search(clean) and _a_thing_they_started(memory)
            and not _hedged_recently(memory) and not _thread_is_about_the_body(memory)):
        return _choose(NOT_TOO_OLD if _names_their_age(clean) else NOT_FIT_ENOUGH, memory, clean)
    # (The flat habit is answered above the echo - see `reads_as_a_flat_habit`.)
    # A goodbye with the person's own trouble set against it ("im off but i feel rough", "got to
    # go but i keep waking up") is not a goodbye while something answers the trouble, and this
    # file is the last place that could. Where nothing above had a word for it, all that is left
    # is the intake form ("Got it. Is there anything you'd like a hand with?"), which files a
    # goodbye back as a fact and gives the person nothing; letting them go warmly is the smaller
    # thing to say, and the trouble is asked about on the next line if they come back.
    if leaving.reads_as_a_leave_with_a_trouble_in_it(clean, words):
        bye = leaving.pool(clean, words, trouble_blocks=False, memory=memory)
        if bye:
            return _choose(bye, memory, clean)
    # The last thing before the intake form. A cost somebody else has put on the person - "ive
    # been asked to be a bridesmaid but its 800 quid", "my mate wants 500 quid for the holiday",
    # "my sister wants me to spend 1000 on her wedding" - was answered "Got it. Is there anything
    # you'd like a hand with?" or with the line said back, which is the one thing a person
    # weighing up a bill does not need. The pool is here rather than higher up because every
    # reading with something of its own has already had its turn: it can only replace a reply
    # that answers nothing.
    if _a_cost_somebody_asks(clean):
        return _choose(A_COST_SOMEBODY_ASKS, memory, clean)
    # The last placeholder of all, and the commonest way a person asks for a hand: "i dont know
    # what to do", "i dont know what to do anymore", "i dont know what to do about it". The
    # three lines this file used to answer it with - "Thanks for telling me - I'm here if you
    # want to dig into any of that", "Got it. Is there anything you'd like a hand with?" and
    # "I'm listening - say more if it helps" - fit any message, and each one answers a person
    # asking for direction by handing the turn back. It sits here, above nothing but the mood
    # pool, because a line with a subject has already had its own answer; what is left is the
    # bare ask, and the bare ask has a pool already (BARE_PICK_DO). A thread with advice in it is
    # the exception: "the boiler is broken" then "i dont know what to do" is the next step of
    # that advice, and the reply that carries on with it is already proposed.
    lost = the_lost_ask_reply(memory, clean, repaired)
    if lost:
        return lost
    # A thing that came out wrong, without the thing being named ("it came out grey in the
    # middle"): every card that answers a bake or a roast needs the word for what it was, so a
    # line that only reports the result has nothing to look up, and it fell to the question about
    # the day or to being said back. The one thing a friend asks is what happened.
    if RESULT_WENT_WRONG.search(clean):
        return _choose(A_THING_CAME_OUT_WRONG, memory, clean)
    # What is true of them, said as a fact ("im self employed", "i was on a diet last year"): the
    # cheer above asks about a day nobody described and the intake form offers help with a task
    # nobody mentioned, so the question is about the thing they have just said about themselves.
    if PLAN_THAT_FELL_THROUGH.search(clean):
        return _choose(A_PLAN_THAT_FELL_THROUGH, memory, clean)
    # A state said with good news in it is the news ("im engaged", "im pregnant", "i feel like im
    # pregnant"): "Does that suit you, or would you change it?" is a question for a state somebody
    # might want to shift, and it took the congratulations off all three. The mood the line is
    # already read with is the test, so no word is listed here and a state that is only a state
    # ("im self employed") still gets its question.
    state = None if RESULT_WENT_WRONG.search(clean) or mood == "positive" else _a_state_of_theirs(clean)
    if state:
        return _choose(A_STATE_PAST if state == "then" else A_STATE_NOW, memory, clean)
    # A day the person has just said went badly ("we had a row last night", "were gutted when it
    # happened"): the day pool below is a cheer, and with the cheer taken away these reached the
    # floor. One question about the day is what a friend says, and nothing above wants the line.
    if _a_bad_time_told(clean, memory):
        return _choose(A_BAD_TIME_TOLD, memory, clean)
    # The same shape where the word for the trouble is a loose one ("we had a strange day at
    # work", "it was a grim afternoon"): the cheer is wrong and the floor answers nothing, so the
    # question is asked without a presumption in it.
    if _a_day_asked_without_a_cheer(clean, memory):
        return _choose(A_DAY_ASKED_PLAIN, memory, clean)
    # A line that is only a name ("my kids are called jack and emma", "my mother-in-law is called
    # june"): the cheer below asks about a day nobody described, and the intake form offers help
    # with a task nobody mentioned. The names are said back with one question about the people.
    named = _a_name_told_reply(clean, memory)
    if named:
        return named
    # A small account of the day, said with nothing on the end of it ("work was ok today", "i got
    # my hair cut", "we had a takeaway last night"): every reading above is for a thing with a
    # shape of its own, so these reached the intake form ("Got it. Is there anything you'd like a
    # hand with?"), which offers help with a task nobody mentioned and could have come before any
    # message at all. A friend asks about the day. It is the last reading before that pool, so it
    # can only ever replace a reply that answers nothing.
    # Advice somebody else gave the person is a plan with a name on it, and nothing in it has
    # happened yet: "my mate said i should try that new pizza place" was answered "How was it,
    # overall?" and "i was told to rest" got "Good to hear. What was the best bit?" - day pools
    # asking about a thing still to come. It sits beside the small day, as the last reading
    # before the intake form, so a line with a card of its own keeps it: "my wife wants me to
    # stop drinking" is the relationship answer's and "ive been told to lose weight" is the
    # weight card's. The reading is the understanding engine's own (`suggestion`).
    suggestion = understood.get("suggestion") if isinstance(understood, dict) else None
    if suggestion and not asking:
        who = str(suggestion.get("who") or "")
        if who:
            return _choose(tuple(line.format(who=who) for line in A_SUGGESTED_BY_SOMEONE),
                           memory, clean)
        return _choose(A_SUGGESTED, memory, clean)
    # A thing they did and are judging themselves for. Nothing above has a shape for it - it is
    # not a question, a plan, a symptom or a thing done about the house - so it reached the day
    # pool or the shrug, and "i did something stupid yesterday" was answered "Good to hear. What
    # was the best bit?", "i lied to my friend" "Sounds alright. Anything good in it?" and "i made
    # a mistake at work" "I'm listening - say more if it helps". A cheer at a confession is the
    # one reply a person does not forgive, and the shrug hands back the turn they were already
    # finding hard. The pool asks the only question worth asking.
    if _a_thing_they_regret(clean):
        return _choose(A_THING_THEY_REGRET, memory, clean)
    # The other half of the same reading: a line about what somebody close did to them is not a
    # day of their own that went fine.
    if _a_betrayal(clean):
        return _choose(A_BETRAYAL, memory, clean)
    # Somebody living in a care home ("my mum moved into a home last month", "my nan is in a home
    # too", "i feel guilty about not visiting my dad in the home"). It comes before the small day
    # and the echo, both of which answered these lines with something that could have been said to
    # anyone, and before the neutral pool for the same reason.
    care = _a_care_home_line(understood, memory)
    if care:
        return care
    # A form or a page that threw the person's work away ("my online application didnt save") is a
    # statement about a loss, and every pool below reads a line like that as a small account of the
    # day: a cleared checkout was answered "Sounds alright. Anything good in it?" and a lost
    # application "I'm listening - say more if it helps". The order that gets the work back is
    # known, so it is answered before the day pools - and nothing else takes its place, because
    # this can only answer a line that names a form and says the work went.
    wrecked = finding_out.the_wrecked_form_reply(clean)
    if wrecked:
        said = _choose(wrecked, memory, clean)
        if said:
            return said
    # The day is told over two lines, and every pool above reads one of them. "i had a lovely
    # day" then "we went to the beach" reached the flat pool ("Sounds alright. Anything good in
    # it?"), asking for the good bit of a good day the person was in the middle of describing, and
    # "work was mad today" then "i ended up staying till eight" was congratulated ("Good to hear.
    # What was the best bit?"). Where the turn before already said how the day was, the rest of it
    # is part of that day, so the pool is chosen from the day and not from the line alone.
    # A price the person stated is not a day they had. "my quote was 300", "my new sofa was 800"
    # and "i paid 60 for a haircut" were all read as a flat account of a day and cheered -
    # "Sounds alright. Anything good in it?", "Good to hear. What was the best bit?" - which
    # invents a feeling about a sum of money and asks what was good about a bill. A sum with no
    # second figure beside it is the one thing the bot cannot judge and can honestly say so, so the
    # answer is the one it already gives when somebody asks "is that a lot": the figure said back,
    # and the one other number that would settle it. The knowledge cards have all had their turn
    # above this line - "my boiler service cost 90" still gets the £60 to £120 card - so what is
    # left here is the sum of money with nothing behind it.
    sum_said = _a_sum_with_nothing_beside_it(clean, memory)
    if sum_said:
        return _choose([line.format(said=sum_said) for line in A_SUM_STATED], memory, clean)
    rest = _the_rest_of_the_day(clean, memory, mood)
    if rest is not None:
        return _choose(rest, memory, clean)
    # Something they have only been told about is not a day of theirs, and the day pool below
    # answered every one of these as an afternoon that went fine. It sits immediately before
    # that pool so it can only ever replace a line that would otherwise be congratulated.
    reported = _a_report_from_elsewhere(clean)
    if reported is not None:
        return _choose(reported, memory, clean)
    if mood == "neutral" and _a_small_day(clean, memory) and not _just_asked_about_the_day(memory):
        return _choose(A_SMALL_DAY, memory, clean)
    # The last thing before the neutral pool, and here for the same reason as the pool above: only
    # a reply that answers nothing can be replaced. An apology or a "never mind" names nothing, so
    # every reading with something of its own has already had its turn by now.
    if A_SORRY_ON_ITS_OWN.match((clean or "").strip()):
        return _choose(SORRY_ON_ITS_OWN, memory, clean)
    if A_DISMISSAL.match((clean or "").strip()):
        return _choose(NEVER_MIND, memory, clean)
    # A warm line that carries a detail the person never gave is a guess about their week, so the
    # positive pool is read through the line: "worth the wait" only where they said they waited.
    # A correction nobody here could file: "no it was my idea not the kids" after the bot asked
    # which of the party games the children had picked, "no the quiet is the best bit of it" after
    # an answer about the noise. The store files the corrections it can key ("no he is 7" is
    # "Got it - he is 7") and the echo says the rest back; what is left is a correction of
    # something neither could hold, and it reached the search hedge. The pool takes it and hands
    # the thread back. It sits with the other last readings, so the echo, the small day and every
    # pool with something of its own has already had its turn.
    if _takes_something_back(clean, memory):
        return _choose(A_CORRECTION_TAKEN, memory, clean)
    positive = _says_only_what_they_said(POSITIVE, clean)
    # A plain account of a thing with nothing on the end of it ("the tap has been running all
    # morning", "i think theyre underpaying me", "my shift starts at half 5") reached the intake
    # form, which offers help with a task nobody mentioned. The family of thing it names decides
    # one true thing to say instead. Last, so it can only replace a reply that answers nothing.
    if mood == "neutral":
        one_thing = onething.pool(clean, understood, memory)
        if one_thing:
            return _choose(one_thing, memory, clean)
        # A limit said in words the reading does not file ("nothing with a laugh track though")
        # arrived at the neutral receipt - the filler this shape least deserves, because the person
        # has just narrowed a list and is waiting for the next one. Here, last, so every reading
        # with something of its own keeps its turn.
        from . import limit as limit_line  # noqa: PLC0415 - no cycle at load
        narrowed = limit_line.a_limit_the_reading_missed(clean, memory)
        if narrowed:
            return narrowed
    # A pleasure gone out of everything is a low line and not a dull afternoon, so it does not
    # get the pool that offers a film and a book to cheer the day up: it gets the pool about the
    # flatness itself. Read here, last, so every reading with something of its own keeps its turn
    # ("my medication makes me sleepy" stays the medicine's), and read on the reading rather than
    # on the mood, because the mood is what the line says it is not.
    if reads_as_no_pleasure(clean):
        return _choose(PLEASURE_GONE_LINES, memory, clean)
    return _choose({"positive": positive, "negative": NEGATIVE, "neutral": NEUTRAL}[mood],
                   memory, clean)


def _a_day_told_instead_of_the_receipt(said_back, clean, memory):
    """The question about the day, where the echo is only a receipt of it.

    "i saw my sister at the weekend" is the store filing the visit, and the filing said back -
    "Noted: you saw your sister at the weekend." - is the coldest reply in this file and says
    nothing about the visit. A pool's own line ("Your sister is called Meg - noted.") is not a
    receipt and keeps its turn, and neither does a hire, a win or a thing bought reach here.
    """
    if not said_back or not ack.reads_as_a_receipt(said_back):
        return None
    # The receipt this file gets for a line that is only a name is the coldest of them ("Noted:
    # your kids are called jack and emma."), and a line the name reader has a pool for is not a
    # receipt and never reaches here. The names are said back and asked about instead.
    named = _a_name_told_reply(clean, memory)
    if named:
        return named
    # The detail of a day the person has already said went badly ("sorry, bad day" then "sorry,
    # it was the meeting"): the receipt is colder than the cheer it replaced, and the question
    # about the day is the reply a friend gives. The words for a bad day are not in this line,
    # so the line before it is the test.
    if _a_small_day_shape(clean) and _a_detail_of_a_bad_day(memory, clean):
        return _choose(A_BAD_TIME_TOLD, memory, clean)
    # A confession filed by the store is the coldest of the receipts: "i lied to my friend" came
    # back as "Noted: you lied to your friend." The pool asks what happened instead.
    if _a_thing_they_regret(clean):
        return _choose(A_THING_THEY_REGRET, memory, clean)
    if _a_betrayal(clean):
        return _choose(A_BETRAYAL, memory, clean)
    # "my nan is in a home too shes 88" was filed as a fact and said back, and the store is the one
    # claiming that turn: the pool answers it instead, as it does above.
    care = _a_care_home_line((memory or {}).get("understood"), memory)
    if care:
        return care
    if HAVE_GOT_A_THING.search(clean or ""):
        return None
    if _just_asked_about_the_day(memory):
        return None
    # The same three readings, in the order the day pools above are asked, because the echo this
    # replaces is also the reply a day that went wrong somewhere gets: "the mums got together on
    # sunday and it kicked off" is a row, and the cheer that stood here congratulated them on it.
    # A cheer is the wrong reply to a day like that whether it comes from the chain or from this
    # hook, so the hook asks the same questions the chain does and not only the flat one.
    if _a_bad_time_told(clean, memory):
        return _choose(A_BAD_TIME_TOLD, memory, clean)
    if _a_day_asked_without_a_cheer(clean, memory):
        return _choose(A_DAY_ASKED_PLAIN, memory, clean)
    if not _a_small_day(clean, memory):
        return None
    # A form that ate the work is a loss and not a day, and it reaches this hook as well as the
    # chain: the store's receipt is what the composer would otherwise stand behind. The order that
    # gets the work back is known, so it takes the receipt's place.
    wrecked = finding_out.the_wrecked_form_reply(clean)
    if wrecked:
        said = _choose(wrecked, memory, clean)
        if said:
            return said
    # The receipt is only a receipt: where the turn before already said how the day went, the
    # question about the day is the wrong read of the second half of it (see
    # `_the_rest_of_the_day`).
    rest = _the_rest_of_the_day(clean, memory)
    if rest:
        return _choose(rest, memory, clean)
    return _choose(A_SMALL_DAY, memory, clean)


def _the_rest_of_the_day(clean, memory, mood="neutral"):
    """The pool for the rest of a day the turn before was about, or None.

    The line has to be an account of the day on its own, which is the same reading the flat pool
    takes: a subject with something asked about it, a plan or a question has had its own reply
    higher up and never reaches here. Then the turn before decides which day it is part of - a
    good one, so the reply adds to it instead of asking for its best bit, or a hard one, so the
    reply carries it instead of congratulating the person on it.
    """
    if not isinstance(memory, dict) or mood == "negative":
        return None
    if not _a_small_day(clean, memory):
        return None
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return None
    was = _matchable(str(turns[-1].get("user") or ""))
    if not was:
        return None
    if _a_good_time(was) or _in_a_pool(str(turns[-1].get("bot") or ""),
                                      (A_GOOD_TIME, A_GOOD_TIME_IN_A_CARE_THREAD)):
        return A_REST_OF_A_GOOD_DAY
    if _in_a_pool(str(turns[-1].get("bot") or ""), (LOW_DAY_REPLIES,)):
        return A_REST_OF_A_HARD_DAY
    if _an_emotion(was) in A_HARD_DAY_MOOD:
        return A_REST_OF_A_HARD_DAY
    return None


def _a_small_day(clean, memory=None):
    """True for a short, flat account of a day of the person's own that went neither way.

    The shape first, then what the line feels like: a day that went well has its own warm pool, and
    a day that went badly is met rather than congratulated. This can only replace the intake form,
    because everything with a reading of its own has already had its turn above.
    """
    if not _a_small_day_shape(clean):
        return False
    text = " ".join(str(clean or "").lower().split())
    # Advice somebody else gave them is not a day they have had: "my mate said i should try that
    # new pizza place" has no "how did it go" in it to ask about.
    read = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(read, dict) and read.get("suggestion"):
        return False
    # A day that went well is the good-time pool's, which says something warm about it: "i had a
    # really good sleep", "we had a lovely lunch". This reading is for the flat line, where
    # nothing in it is good or bad.
    if _a_good_time(clean, memory):
        return False
    # A line that opens on "it"/"that"/"this" and a form of "be" is a detail added to what the
    # person has already said, not an account of a day of their own: "i think i sprained my ankle"
    # then "it was yesterday" was answered "Good to hear. What was the best bit?", and "it was in
    # march" after a miscarriage, "it was lifting the shopping" after a back going and "it was on
    # monday" after a cat was put down went the same way. The pleasantry is a small-day reading -
    # something happened and it was fine - and a clause with no doing of its own in it is the
    # wrong thing to read that way.
    if _a_detail_about_what_was_said(text, memory):
        return False
    # ... and neither is a line that goes back over what the person already said.
    if A_LOOKING_BACK.match(text):
        return False
    # A bad feeling in the line is the whole of it: "were gutted when it happened" and "ngl ive
    # bin knackered all week" were both asked how the day went, and "Nice one. How did the rest
    # of it go?" is the one reply a person who has just said they are gutted cannot use. The
    # reading is the one the rest of the bot uses, so a word the mood pools know ("worst", "hate")
    # counts here without being listed again.
    if ((memory or {}).get("understood") or {}).get("polarity") == -1:
        return False
    # A place secured in something still to come, only where the pool above will answer it: a
    # viewing that has already happened keeps the day question rather than losing it to a receipt.
    if _a_thing_got_ahead(text):
        return False
    # A child's name and age is a fact about them, not a day that happened: "and my sons called
    # tom, hes 9" was read as a day of someone else's and answered with the pleasantry that fits
    # any message ("Nice one. How did the rest of it go?"), where the same two facts put as "my
    # daughters name is mia and shes 6" got "Mia, 6. What is she like just now?".
    if remark.THEIR_NAME_AGE.match(text) or remark.THEIR_NAME.match(text):
        return False
    if _a_day_of_someone_else(text):
        return False
    # "i have a problem", "something is wrong": a problem is not a day, and a cheerful question
    # about it is the last thing to say back to somebody who has just said they have one.
    if _a_problem_stated(text):
        return False
    if not DAY_PAST.search(text) and not _a_thing_happened(text):
        return False
    if not (A_DAY_SUBJECT.search(text) and PAST_DOING.search(text)):
        return False
    # A day marker, or a line short enough to be one thing ("i got my hair cut"). The long shape
    # without a marker is a story, and a story has a reading of its own above.
    if not DAY_PAST.search(text) and len(text.split()) > 10:
        return False
    if NOT_A_DAY_DONE.search(text) or NOT_A_DAY_SAID.search(text):
        return False
    # A confession is not a day that happened to someone: "i lied to my friend" is filed by the
    # store like any other line and came back as a receipt, which the hook above turns into the
    # day pool's "Sounds alright. Anything good in it?".
    if _a_thing_they_regret(text):
        return False
    # A colour or a swelling is a symptom, not an account of a day, and the pool below is a warm
    # question about a day that went fine: "i had a red patch on my arm yesterday" was answered
    # "Good to hear. What was the best bit?" because "had" is a past doing and "red" was the only
    # other thing read. Written as the shape a symptom takes - two words that belong together - so
    # "i got a red dress in the sale" is still the day it sounds like.
    if A_SYMPTOM_PHRASE.search(text):
        return False
    if (NEGATIVE_LINE.search(text) or HARM_NAMED.search(text)
            or A_HURT_MYSELF.search(text)):
        return False
    # A crash or a burglary said flat is the same shape as a haircut: "we got burgled last night"
    # is a subject, a past tense and a day marker. What tells them apart is the thing itself, so
    # it is read before the pool is reached rather than left to the mood, which reads a burglary
    # as neutral.
    if A_DAY_WENT_WRONG.search(text) or remark.done_to_me(text):
        return False
    # A mishap is the careful reading's line even though nothing in the sentence is a word for
    # harm: "i got glass in my foot" and "my husband rolled off the bed" were both asked how the
    # rest of it went, and a cheerful question about a day is the one reply nobody wants after one
    # of those. Read off the whole line, so a mishap in a longer account of the day still counts,
    # and by shape rather than by body word, because "i got my hair cut" names a cut and is a day.
    # A fall that is over ("last summer", "nearly", "but hes ok") keeps the day question - it is
    # the story of a day and asking its best bit is what a friend does.
    if _a_mishap_to_ask_about(text):
        return False
    # Somebody doing them wrong - being called names, teased, picked on, left out - is the same
    # shape and the same fault: a parent told "good to hear" after their child was called names
    # has been congratulated on it.
    if SOMEONE_DONE_WRONG.search(text):
        return False
    # "i was in hospital yesterday", "i had a fall": a day with something wrong in it is the
    # trouble and feeling pools' line, and they come before this one anyway.
    if A_BAD_THING_NAMED.search(text) or A_HAND_OUT.search(text):
        return False

    # The day already went badly on the turn before: the cheer is for a day the person has said
    # nothing about, and "sorry, it was the meeting" after the bot's own sympathy is the detail
    # of that bad day, not a new one to ask about. A line that says when it happened is a day of
    # its own - "i did get out for a walk yesterday" after a grim week is the walk, not more of
    # the week - so the cheer is the question about it.
    if _the_day_was_already_bad(memory) and not DAY_PAST.search(text):
        return False
    # "i was in hospital yesterday", "we had a strange day at work": the day went wrong somewhere,
    # and the cheer is for a day that went neither way. This list only ever subtracts - the reply
    # is whatever answers next, which is the question `_a_day_asked_without_a_cheer` asks.
    # A change of medicine has an answer of its own two hooks below, and it is not a day that went
    # fine: "my meds have changed" was asked "Nice one. How did the rest of it go?". Read with the
    # same three patterns that pool uses, and with its stand-down for a symptom in the line, so the
    # dose and symptom cards keep their turns.
    if (onething.A_MEDS.search(text) and onething.A_MEDS_CHANGE.search(text)
            and onething.A_MEDS_MINE.match(text)
            and not onething.A_MEDS_SYMPTOM.search(text)):
        return False
    return not BAD_DAY_ANYWAY.search(text)


def _a_name_told(clean):
    """The names and the person, when the line is only a name: ("Jack and Emma", "kids", True).

    The third part is whether the names are more than one, because "Jack and Emma" is they and
    "June" is she or he: the pronoun comes from the person word the same way the name reader
    does it, so nothing here guesses.
    """
    said = " ".join(str(clean or "").lower().split()).strip(" .!,")
    if not said or "?" in said:
        return None
    match = A_NAMES_TOLD.search(said)
    person = match.group("person") if match else ""
    if not match:
        match = A_NAME_A_HOUSEHOLD_TAKES.search(said)
        if not match:
            return None
    names = [word.strip() for word in re.split(r"\s*(?:,|and)\s*", match.group("names"))]
    # The list stops at the first word that names nobody, so a sentence after the names
    # ("janet and she lives in leeds") leaves the name and not the sentence: the reply is about
    # the people, and their address is theirs to tell. "my son is called after me" is no name at
    # all and leaves nothing, while "the smiths" is a name with "the" in it.
    kept = []
    for word in names:
        if not word or set(word.split()) <= NOT_A_NAME_WORD:
            break
        kept.append(word)
    names = kept
    if not names:
        return None
    if len(names) == 1:
        spoken = names[0].title()
    else:
        spoken = ", ".join(word.title() for word in names[:-1]) + " and " + names[-1].title()
    # A name on a thing is not a person to ask about: "my car is called betsy" says nothing about
    # anybody, and "What are they like?" is not a question about a car. So the person word has to
    # be one the bot already reads as a person (the list the rest of this file uses, which carries
    # a dog and a cat but not a car), or one of the hyphenated kin words the list does not carry
    # ("mother-in-law", "step-dad"); otherwise the reply is about the name itself.
    if person and person not in THE_PEOPLE and "-" not in person:
        person = ""
    return spoken, person, len(names) > 1


# A name that came from somebody is not a name at all: "my son is called after me", "hes named
# after his grandad", "i was named after my nan". The name reader rightly stands down ("after you"
# is not a name), so these reached the store's read-back - "Noted: your son is called after you."
# - which is the coldest reply in this file and says nothing about the person the name came from.
# The shape is the words themselves, so nothing else in the file has to know about it.
NAMED_AFTER = re.compile(
    r"\b(?:called|named)\s+(?:(?:him|her|them|it|me|us)\s+)?after\s+(?P<who>me|us|you|i|"
    r"(?:my|his|her|their|our)\s+[a-z-]+)\b")


A_POSSESSIVE_OF_MINE = frozenset(("my", "our"))


def _named_after_reply(clean, memory):
    """The reply to a name that came from somebody, or None."""
    said = " ".join(str(clean or "").lower().split())
    found = NAMED_AFTER.search(said)
    if not found:
        return None
    who = found.group("who")
    if who in ("me", "us", "you", "i"):
        return _choose(A_NAMED_AFTER_THEM, memory, clean) or None
    words = who.split()
    # "my nan" is the person being spoken to's nan, so the reply says "your nan"; "his grandad" is
    # already how they would say it and is left alone.
    if words[0] in A_POSSESSIVE_OF_MINE:
        who = "your " + words[1]
    lines = [remark.fill_person(line.replace("{who}", who), words[-1])
             for line in A_NAMED_AFTER]
    return _choose(lines, memory, clean) or None


def _a_name_told_reply(clean, memory):
    """The reply to a line that is only a name, said back and asked about, or None."""
    told = _a_name_told(clean)
    if not told:
        return None
    spoken, person, plural = told
    if not person:
        return _choose([line.replace("{names}", spoken) for line in A_NAME_STORY],
                       memory, clean) or None
    # "kids" is the plural stand-in for the pronoun: fill_person gives they/them/their for a word
    # that is not one person, which is what two names need.
    lines = [remark.fill_person(line.replace("{names}", spoken), "kids" if plural else person)
             for line in A_NAME_TOLD]
    return _choose(lines, memory, clean) or None


# A state is not a day either. "im self employed" and "i was on a diet last year" opened with
# the person as the subject and a past tense in them, and were asked how the rest of it went ("Good
# to hear. What was the best bit?"); there is no rest of it, they were saying what is true of them.
# An "-ed" word that describes rather than does ("employed", "married", "retired") is the same
# kind of word as "tired", and "was" on its own says what was the case.
STATE_NOT_A_DOING = re.compile(
    r"\b(?:self[- ]?employed|unemployed|retired|married|divorced|engaged|separated|pregnant|"
    r"based|interested|tired|exhausted|worried|bothered|pleased|delighted|annoyed|scared|"
    r"frightened|settled|sorted|done|on a diet|on benefits|in debt|in credit|on the dole|"
    r"a vegetarian|a vegan|on medication|on tablets)\b")


BARE_STATE = re.compile(r"\b(?:was|were|been|is|are|am|im|i'm|its|it's)\b")


# Which way to ask about it: "i was on a diet last year" is a thing to look back on, "im self
# employed" is a thing still going.
STATE_THEN = re.compile(
    r"\b(?:last (?:year|summer|winter|spring|autumn|month)|years ago|used to|back then|"
    r"when i was|in the past)\b")


# The copula a state that has ended is said with: "i was married for 20 years", "we were skint
# that winter". "been" is left out on purpose - "ive been self employed for 3 years" is a state
# still going.
STATE_IN_THE_PAST = re.compile(r"\b(?:was|were)\b")


# A plan that did not happen, said as a thing that was meant to be: "i was meant to be on holiday
# this week", "it was meant to be a loaf of bread". The cheer that followed it ("Sounds alright.
# Anything good in it?") asked about a day nobody had described, and a loaf that came out wrong is
# the same news as one that came out grey.
# The marker is "supposed to" and "meant to" themselves, so the verb after it is any verb:
# "i was supposed to call the bank", "we were supposed to go away", "i was supposed to finish it
# today" are the same shape as "i was supposed to be on holiday", and all four were cheered.
PLAN_THAT_FELL_THROUGH = re.compile(
    r"\b(?:was|were|is|are|had|have)\s+(?:meant|supposed)\s+to\s+[a-z]+")


def _a_state_of_theirs(text):
    """\"now\", \"then\" or None: what is true of the person rather than what they did.

    A line here has the person as its subject and a word of state in it (\"self employed\",
    \"on a diet\", \"married\") and no past doing of its own, so there is no day to ask about.
    The day marker is what makes a line an account again: \"work was ok today\" is a day had.
    """
    text = " ".join(str(text or "").lower().split())
    if not text or not A_DAY_SUBJECT.search(text):
        return None
    if not STATE_NOT_A_DOING.search(text):
        return None
    rest = BARE_STATE.sub(" ", STATE_NOT_A_DOING.sub(" ", text))
    if DAY_PAST.search(text) or PAST_DOING.search(rest):
        return None
    # "i was married for 20 years" is a state that has ended, and the marker list below only knows
    # the usual time words, so the copula itself says which way to ask: was/were is a state to look
    # back on, is/am/are one still going.
    if STATE_THEN.search(text) or STATE_IN_THE_PAST.search(text):
        return "then"
    return "now"


# A thing that came out wrong is the report of a day that went badly: "it came out grey in the
# middle" was told "How was it, overall?", which is the one thing a person who has just said the
# bake went wrong cannot use. The shape is the result rather than the doing, so it is read on its
# own and the pools for a thing gone wrong are above this one.
RESULT_WENT_WRONG = re.compile(
    r"\b(?:came out|comes out|turned out|turns out|came back|comes back|ended up|went|goes)\s+"
    r"(?:a bit\s+|a little\s+|all\s+|really\s+|quite\s+|so\s+)?\s*"
    r"(?:grey|gray|dry|soggy|burnt|burned|raw|tough|dense|rubbery|pale|lumpy|stodgy|stale|"
    r"bland|wrong|ruined|awful|horrible|terrible|overdone|undercooked|flat|sour|bitter|"
    r"curdled|split|seized)\b")


# The bot's own last line met the day with sympathy, name in front or not ("Hi Eve — sorry to
# hear that. A walk and someone to talk to usually help more than sitting with it.").
BOT_WAS_SORRY = re.compile(
    r"\b(?:sorry|that sounds (?:rough|awful|horrible|hard|heavy|tough)|that is (?:rough|awful|"
    r"hard|heavy|tough)|that's (?:rough|awful|horrible|hard|heavy|tough)|rough one|hard one)\b",
    re.I)


# The words for a day said badly when the day itself is the subject: "sorry, bad day", "rough one
# today", "a rubbish day", "strange day at work", "long day". BAD_DAY_ANYWAY below can afford
# words like "waited" and "late for" because it only ever takes a cheer away; this one decides
# whether the *next* short line belongs to a day already on the table, so it keeps to the words
# that are about the day rather than about one irritating thing in it.
A_DAY_SAID_BADLY = re.compile(
    r"\b(?:bad day|bad one|rough day|rough one|rubbish day|rubbish|awful day|horrible day|"
    r"terrible day|hard day|hard one|long day|tough day|tough one|strange day|grim|draining|"
    # A row that started: "the mums got together on sunday and it kicked off" has the shape of an
    # account of a day and no word in it that says what it was. "it kicked off" and not
    # "kicked off", because that is also how a match or a party starts.
    r"it kicked off|"
    r"wiped out|hectic|full on|knackered|exhausted|shattered|gutted|a row|an argument)\b")


# A day nobody called bad, said only by the way the person did something in it: "i ate badly all
# week", "i drank too much last night", "i skipped the gym all week". None of those names a bad
# day, so the cheer below answered a week they had just told you went wrong with "Good to hear.
# What was the best bit?" - the one reply that cannot be given - and the words that say it are the
# way the doing went, not a word for the day. Two shapes, kept apart because they are not the same
# risk: the excess words are never good news about a doing of the person's own, and "skipped" is
# only a slip where the line also says how long it went on ("i skipped breakfast" is a morning,
# "i gave up sugar yesterday" is an achievement and keeps its own reply above).
A_DOING_GONE_BADLY = re.compile(
    r"\b(?:badly|too\s+much|too\s+many|too\s+often|not\s+enough|nothing\s+but|binged|"
    r"overdid\s+it|junk|crap|rubbish)\b")


A_THING_SKIPPED = re.compile(
    r"\bskipped\b(?:\s+\w+){0,4}\s+(?:all\s+(?:week|month|weekend)|this\s+week|last\s+week|"
    r"lately|every\s+(?:day|morning|week)|again)\b")


# A meal skipped is a day with a hole in it rather than a slip, and the ones that answer it name
# the hole: "i skipped lunch again" is already met with "That's a day with a hole in the middle of
# it. Is it no time to stop, or nothing in?" - warmer and more specific than the pool this
# change reaches, so a skipped meal is left to it and the span above only reads a doing.
A_MEAL_SKIPPED = re.compile(
    r"\bskipped\b(?:\s+\w+){0,2}\s+(?:a\s+|any\s+|my\s+|the\s+)?"
    r"(?:breakfast|lunch|lunches|dinner|dinners|tea|supper|meals?|food)\b")


def _a_day_said_badly(text):
    """True when the person's own line reads as a day that went badly."""
    said = " ".join(str(text or "").lower().split()).strip(" .!,")
    if not said or "?" in said or len(said.split()) > 12:
        return False
    return bool(A_DAY_SAID_BADLY.search(said))


def _the_last_exchange(memory):
    """The last turn that has a reply on it, or None.

    The turn being composed is already on the record with an empty bot line by the time this file
    reads it, so `turns[-1]` is the line being answered and not the exchange before it. Every
    reading of "the line before this one" in this file has to look for the last turn that has a
    bot line, or it reads the wrong turn - which is how the bad-day guard came out false on the
    very row it was written for ("sorry, bad day" then "sorry, it was the meeting").
    """
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    for turn in reversed(turns):
        if str(turn.get("bot") or "").strip():
            return turn
    return None


def _the_day_was_already_bad(memory):
    """True when the bot's own last line already met a bad day.

    "sorry, bad day" / "sorry, it was the meeting": the second line names what went wrong in the
    day the bot has just answered with sympathy, and the cheer that follows it ("Good to hear.
    What was the best bit?") reads as not having heard the first line at all. The bot's own last
    reply is the test, so a day that has already gone badly is only read as one while it is still
    on the table; a chat the bot has moved on from is left to the rest of the chain.
    """
    seen = _the_last_exchange(memory)
    if seen is None:
        return False
    last = str(seen.get("bot") or "")
    # A plan that fell through and a flat day read with no presumption in it are the same thing:
    # the bot has just said something is a shame, so the line after it is the rest of that story and
    # not a new day to cheer. "it was supposed to be sunny" then "we had the picnic in the front
    # room" was told "Nice one. How did the rest of it go?" on top of the bot's own "Ah no. What
    # stopped it?", which is the cheer contradicting the line above it.
    if _in_a_pool(last, (LOW_DAY_REPLIES, NEGATIVE, A_BAD_TIME_TOLD, A_THING_CAME_OUT_WRONG,
                         A_PLAN_THAT_FELL_THROUGH, A_DAY_ASKED_PLAIN)):
        return True
    if BOT_WAS_SORRY.search(last[:80]):
        return True
    # The pools that answer a bad day live in other modules and bring prose of their own ("Rough
    # one. A shower, something warm to eat and an early night usually resets it."), so no list of
    # their openers kept here would cover them - the first reading of this guard missed exactly
    # that line, and the row it was written for still went to the cheer. What the bot heard is on
    # the record too, so the test is the person's own line before it: a day this file would read
    # as one gone badly, and the short line after it is the detail of that day, not a new day.
    return _a_day_said_badly(seen.get("user"))


def _a_detail_of_a_bad_day(memory, text=None):
    """True when this line is the detail of a day the person has already said went badly.

    Narrower than `_the_day_was_already_bad` on purpose: the bot says something sympathetic after
    a great many lines, and the cheer for a haircut after a boiler is a new day, not a detail of
    the old one. What makes it a detail is the person's own line before it - a day read as one
    gone badly - and the short shape of this one.
    """
    seen = _the_last_exchange(memory)
    if seen is None:
        return False
    # A line that says when it happened is a day of its own. "i did get out for a walk yesterday"
    # after a grim week was read as more of the grim week and answered "How are you doing with
    # it?", where the question about the walk is what a friend asks; the exception is the short
    # clause that adds the day to what was already said ("it was yesterday"), which is the detail
    # this reading is for in the first place.
    if text and DAY_PAST.search(str(text).lower()):
        return bool(_a_detail_about_what_was_said(text, memory))
    return _a_day_said_badly(seen.get("user"))


# A thing that is going on, a thing somebody else settled and a wish are all the same shape as an
# account of a day - a subject, a past doing, a word ending in -ed - and none of them is a day that
# is over. On main the pleasantry went to all three: "i am being followed by my shadow" and "my
# leave got approved" got "How was it, overall?", "i wish i was on that beach" and "i wish it was
# friday" got "Nice one. How did the rest of it go?", and "if only i was there" got "How was it,
# overall?".
#
# The present passive is the shape that says a thing is happening now ("i am being followed", "the
# kids are being horrible"); "i got followed home" is still a day. A decision is a thing somebody
# else settled ("the invoice was approved at work", "my shift was confirmed") is a report of a
# thing, not a day spent; the ones that are the person's own good news have already been answered by
# the news reader above. A wish is about what is not the case, and nothing after it is read.
A_BEING_DONE_NOW = re.compile(
    r"\b(?:i|we|he|she|they|it|you|the|my|our|his|her|their|\w+s)\s+"
    r"(?:am|is|are|was|were|been)\s+being\b|\b(?:i'm|im|we're|they're|he's|she's|it's)\s+being\b",
    re.I)


A_DECISION_NOT_A_DAY = re.compile(r"\b(?:approved|granted|confirmed)\b", re.I)


A_WISH = re.compile(r"\b(?:i|we)\s+(?:really\s+|just\s+|so\s+|do\s+)?wish\b|\bif only\b", re.I)


# What to say to a sum of money with no second figure beside it. A friend does not call a price
# good or bad on its own - they ask what the other quote was - and that is also the only thing the
# bot can honestly say from here.
A_SUM_STATED = (
    "{said} on its own tells me nothing about whether it is high or low. What were you paying "
    "before, or what has someone else been quoted for the same thing?",
    "Put {said} beside the other figure for the same job - what you were paying before, or what a "
    "friend was quoted - and then it means something. What have you got to compare it with?",
)


# The words that make a sum of money a price rather than an amount of something. Fenced on the
# nouns a price is said with, because the verb alone is too wide: "it was 60" is a price with a
# haircut in front of it and a measurement without one.
PRICE_NOUNS = frozenset((
    "paid", "pay", "pays", "paying", "cost", "costs", "costing", "charged", "charge",
    "charging", "quote", "quoted", "quoting", "price", "priced", "fee", "fees", "bill",
    "bills", "invoice", "deposit", "fare", "fares", "spent", "spend", "spending", "wants",
    "wanting", "asking",
))


# The words a line can be made of and still name nothing: "it was 60" is a figure with no thing in
# front of it, and a sum with no thing in front of it is a measurement or a number in the middle of
# some other story, not a price. "my new sofa was 800" names the thing, and it is a price.
NO_THING_SAID = frozenset((
    "i", "me", "my", "we", "us", "our", "it", "its", "it's", "that", "thats", "that's",
    "this", "they", "them", "their", "he", "she", "his", "her", "was", "were", "is",
    "are", "be", "been", "a", "an", "the", "and", "but", "so", "then", "now", "just",
    "only", "about", "around", "at", "for", "of", "to", "in", "on", "with", "from",
    "much", "many", "um", "err", "well", "really",
))


# Money that came to the person is not a price they are asking to have judged. "my bonus was 500",
# "my refund was 60", "my pay went up by 200", "they paid me 200" - a friend is glad about that or
# asks about it, and does not say the figure means nothing on its own. The fence is the direction,
# not the sum: the same verb with the money going out ("i paid 200 for it") is still a price.
MONEY_IN_NOUNS = frozenset((
    "bonus", "bonuses", "refund", "refunds", "rebate", "rebates", "payout", "payouts", "pay",
    "wages", "salary", "earnings", "income", "pension", "pensions", "winnings", "commission",
    "dividend", "dividends", "raise", "rise", "backpay", "arrears",
))


MONEY_IN_SHAPES = re.compile(
    r"\b(?:paid|pay|pays|paying|gave|give|gives|giving|refunded|reimbursed|repaid)\s+"
    r"(?:me|us)\b"
    r"|\b(?:i|we)\s+(?:was|were|am|are|got|get|have|had)\s+(?:paid|given|refunded|"
    r"reimbursed|awarded)\b"
    r"|\b(?:i|we)\s+(?:earned|earn|made|make|won|win|sold)\b[^.]{0,24}?\bfor\b"
    r"|\b(?:sold|selling)\b[^.]{0,24}?\bfor\b\s*[\u00a3$\u20ac]?\d"
    r"|\b(?:got|get|gets|getting)\s+[\u00a3$\u20ac]?\d+\s+(?:for|from|back)\b"
    r"|\b(?:pay|wages|salary|income|pension)\s+(?:went|goes|has gone|rose|increased|is up)\b",
    re.I,
)


def _money_came_to_them(text, words):
    """True for a sum the person was given, paid, earned or refunded rather than asked to judge."""
    if words & MONEY_IN_NOUNS:
        return True
    return bool(MONEY_IN_SHAPES.search(text))


def _a_sum_with_nothing_beside_it(clean, memory=None):
    """The figure, said back the way they wrote it, for a sum of money stated with no question.

    Three ways for a line to say the figure is money: a currency mark, a price word ("paid", "the
    quote came to", "the fee"), or a price verb with a thing in front of it ("my new sofa was
    800"). The third is the one that needs care, because the same verb says a measurement: "it was
    60" names nothing, so it is not a price and the reading stands down. An amount with none of the
    three is somebody else's money - "my nan left me 500" is a bequest, and asking what they were
    paying before would be the wrong question about it - so that stands down too.

    The direction is fenced first: money that came to the person ("my bonus was 500", "they paid me
    200", "my pay went up by 200") is not a price, and a friend answers a bonus or a refund as the
    good news it is. Only money going out is a sum with nothing to judge it by.

    The figure itself is read by the same code a doubt is read by (`reading._their_figure`), so a
    year, an age and a distance are passed over here for the same reasons they are passed over
    there. No range is looked for in the answer just given: everything with a card behind it has
    already answered the turn above, so a sum that reaches this line is one the bot knows nothing
    about.
    """
    from . import reading  # noqa: PLC0415 - the reader imports back into this module's band

    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text:
        return None
    words = set(re.findall(r"[a-z']+", text))
    if _money_came_to_them(text, words):
        return None
    marked = bool(re.search(r"[\u00a3$\u20ac]", text))
    named = bool(words - NO_THING_SAID)
    if not (marked or (words & PRICE_NOUNS) or (named and reading.A_PRICE_VERB.search(text))):
        return None
    found = reading._their_figure({"turns": [{"user": text}]})
    if not found:
        return None
    _value, _unit, said, money = found
    if not money or not said:
        return None
    return said


# A report of something the person has only heard, seen or read is a thing that has not happened
# to them: "i saw on the news theres a big storm coming", "i heard theres a storm on the way", "i
# read that the council is closing the library". The day pools asked all three how it went, and
# one of them cheered a storm warning. Two parts make the shape, and both are needed. The verb is
# one of the ways a claim reaches a person, and its object is a clause rather than a thing: what
# follows is "that", "theres", "there is" or a source ("on the news", "in the paper", "on the
# radio"). That is what keeps "i saw a film last night" and "i read the whole book" out - those
# are things done, with an object, and they are the day pool's own lines.
A_ASKING_WORD = re.compile(
    r"^(?:did|do|does|have|has|had|are|is|was|were|can|could|would|will|should|shall|"
    r"what|whats|how|why|when|where|who|which|any)\b", re.I)


A_REPORTED_NOT_LIVED = re.compile(
    r"\b(?:i|we)\s+(?:saw|seen|heard|read|watched)\s+"
    r"(?:that\b|there(?:'s|s| is| are)\b|on\s+the\s+\w+|in\s+the\s+\w+|"
    r"the\s+\w+|"
    r"somebody\b|someone\b|they\b)|"
    r"\b(?:on|in)\s+the\s+(?:news|paper|radio|telly|local news)\b|"
    r"\bthey\s+say\b|\bive\s+been\s+told\b|"
    # The same claim, passed on by one person: "my mate says theres a storm coming". A
    # suggestion ("my mum said i should go") is a different reading and has already been
    # answered above, so what is left here is the claim with a clause after it.
    r"\b(?:says|said|told\s+me)\s+(?:that\b|there(?:'s|s| is| are)\b)", re.I)


# The half of it that can be acted on here is the weather, because a wind is the one thing in a
# warning that finds what is already loose. The words are the outdoor ones: a "storm in a teacup"
# and a "flood of forms" are not weather, so the noun has to be a plain one.
# The everything-else pool is written for a change, a closure or a charge - the reports that come
# as "what it covers, from when" - so a line is only sent to it when it is about one of those. A
# report of something new ("my sister told me theres a new cafe") has no dates in it to look up,
# and it keeps whatever the reading above already gave it.
A_NEWS_IS_A_CHANGE = re.compile(
    r"\b(?:clos(?:e|es|ed|ing|ure)|cancel\w*|chang(?:e|es|ed|ing)|charg(?:e|es|ed|ing)|"
    r"rules?|ban(?:s|ned|ning)?|cuts?|ris(?:e|es|ing)|increas(?:e|es|ed|ing)|delay\w*|"
    r"roadworks?|strikes?|walkout|fees?|prices?|tax(?:es)?|fines?|shut|"
    r"new\s+(?:rules|charges|prices|fares)|from\s+(?:monday|next\s+week|january|april))\b",
    re.I)


A_NEWS_IS_WEATHER = re.compile(
    r"\b(?:storm|storms|gale|gales|wind|winds|windy|rain|snow|ice|sleet|flood|floods|"
    r"freeze|freezing|frost|heatwave|thunder|lightning|hurricane|tornado|weather)\b", re.I)


def _a_report_from_elsewhere(clean):
    """The pool for a thing the person has only been told about, or None.

    Read where the day pool would answer, so a line with a reading of its own never reaches it.
    The weather half and the everything-else half are different jobs - the local forecast and the
    loose things outside, against the body that said it and the dates one line down - so they are
    two pools and the weather words choose.
    """
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text:
        return None
    # The source words are enough to read a report by ("heard it on the news"), so a line that
    # opens on a question word is told apart first: "did you see the storm on the news" asks the
    # bot something and is answered by the reading for the bot itself, not by a pool about the
    # weather.
    if A_ASKING_WORD.match(text):
        return None
    if not A_REPORTED_NOT_LIVED.search(text):
        return None
    if A_NEWS_IS_WEATHER.search(text):
        return A_NEWS_OF_WEATHER
    if A_NEWS_IS_A_CHANGE.search(text):
        return A_NEWS_OF_SOMETHING_ELSE
    return None


def _a_small_day_shape(clean):
    """True for the shape of a short, flat account of a day of the person's own.

    The shape only: a subject, a past doing, short enough to be one thing, and none of the things
    that already have a reading above (a name, a state, a result that came out wrong, a plan that
    fell through, a confession, a symptom, a mishap, a thing that went wrong). What the line
    feels like is read by `_a_small_day`, so the same shape can be answered warmly when it went
    well and met when it went badly.
    """
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text:
        return False
    if len(text.split()) > 14:
        return False
    # Something going on now is not a day that is over; see `A_BEING_DONE_NOW`.
    if A_BEING_DONE_NOW.search(text):
        return False
    # A thing somebody else decided is not a day somebody spent; see `A_DECISION_NOT_A_DAY`.
    if A_DECISION_NOT_A_DAY.search(text):
        return False
    # A wish is not a day somebody had either; see `A_WISH`.
    if A_WISH.search(text):
        return False
    # A report of an attempt at somebody is the follow-up to a trouble ("i asked him nicely
    # twice"), not a day out, and it is read here so both readings of this shape leave it alone.
    if AN_ATTEMPT_AT_SOMEONE.search(text):
        return False
    # Finding out that somebody close has lied, cheated or hidden money is not a flat day of the
    # person's own: "i found out hes been lying" was answered "How was it, overall?" and "i found
    # out shes been hiding money" "Sounds alright. Anything good in it?" - the one reply nobody
    # forgives, and the same for "turns out hes been texting his ex". The news is the wrongdoing,
    # so it goes to the pools that meet bad news.
    if A_BETRAYAL_FOUND_OUT.search(text):
        return False
    if _a_day_of_someone_else(text):
        return False
    if not DAY_PAST.search(text) and not _a_thing_happened(text):
        return False
    if not (A_DAY_SUBJECT.search(text) and PAST_DOING.search(text)):
        return False
    # A day marker, or a line short enough to be one thing ("i got my hair cut"). The long shape
    # without a marker is a story, and a story has a reading of its own above.
    if not DAY_PAST.search(text) and len(text.split()) > 10:
        return False
    if NOT_A_DAY_DONE.search(text) or NOT_A_DAY_SAID.search(text):
        return False
    # A confession is not a day that happened to someone: "i lied to my friend" is filed by the
    # store like any other line and came back as a receipt, which the hook in `_reply_for` turns
    # into the day pool's "Sounds alright. Anything good in it?".
    if _a_thing_they_regret(text):
        return False
    # A colour or a swelling is a symptom, not an account of a day, and the pool below is a warm
    # question about a day that went fine: "i had a red patch on my arm yesterday" was answered
    # "Good to hear. What was the best bit?" because "had" was a past doing and "red" was the only
    # other thing read. Written as the shape a symptom takes - two words that belong together - so
    # "i got a red dress in the sale" is still the day it sounds like.
    if A_SYMPTOM_PHRASE.search(text):
        return False
    # "i was in hospital yesterday", "i had a fall": a day with something wrong in it is the
    # trouble and feeling pools' line, and they come before this one anyway.
    if NEGATIVE_LINE.search(text) or HARM_NAMED.search(text):
        return False
    # A crash or a burglary said flat is the same shape as a haircut: "we got burgled last night"
    # is a subject, a past tense and a day marker. What tells them apart is the thing itself, so
    # it is read before the pool is reached rather than left to the mood, which reads a burglary
    # as neutral.
    if A_DAY_WENT_WRONG.search(text):
        return False
    # A mishap is the careful reading's line even though nothing in the sentence is a word for
    # harm: "i got glass in my foot" and "my husband rolled off the bed" were both asked how the
    # rest of it went, and a cheerful question about a day is the one reply nobody wants after one
    # of those. Read off the whole line, so a mishap in a longer account of the day still counts,
    # and by shape rather than by body word, because "i got my hair cut" names a cut and is a day.
    # A fall that is over ("last summer", "nearly", "but hes ok") keeps the day question - it is
    # the story of a day and asking its best bit is what a friend does.
    if _a_mishap_to_ask_about(text):
        return False
    # "i was in hospital yesterday", "i had a fall": a day with something wrong in it is the
    # trouble and feeling pools' line, and they come before this one anyway.
    if A_BAD_THING_NAMED.search(text) or A_HAND_OUT.search(text):
        return False
    # A name is not an afternoon's work, a state is not a doing, and a result that came out wrong
    # or a plan that fell through is the same news as a thing gone wrong: each has a pool of its
    # own above, and the cheer is a question about a day.
    if A_NAME_IS_NOT_A_DAY.search(text):
        return False
    # A thing they have only been told about is not a day they had, and every day pool here -
    # the cheer, the flat question, the one that meets a bad day - asks about a day. "i saw on
    # the news theres a big storm coming" was answered "Good to hear. What was the best bit?"
    # because "saw" is a past doing and the storm is the only other thing read; the reading just
    # above `_a_small_day` has the reply for it, and this is what keeps the day pools off it when
    # the mood is not neutral.
    #
    # It has to be the whole reading, not the cue alone: `the \w+` is in A_REPORTED_NOT_LIVED to
    # carry "i saw the storm on the news" (the news as the body that said it), and on its own it
    # also reads "the final", "the match", "the kids" and "the doctor" as a source - so a real day
    # of theirs was stood down and fell to the receipt ("we watched the final together" ->
    # "Got it. Is there anything you'd like a hand with?"). The reading is the thing that decides,
    # because it is the thing that knows a change or the weather is on the other end of the line.
    if _a_report_from_elsewhere(text) is not None:
        return False
    if _a_state_of_theirs(text):
        return False
    if RESULT_WENT_WRONG.search(text) or PLAN_THAT_FELL_THROUGH.search(text):
        return False
    return True


def _a_bad_time_told(clean, memory=None):
    """The day pool's own shape, read as a day that went badly: "we had a row last night",
    "we had a strange day at work", "ngl ive bin knackered all week", "were gutted when it
    happened".

    With the cheer taken away from a bad feeling these were left to the floor ("I'm listening -
    say more if it helps"), which is the line a person gets when nothing in what they said was
    heard - and the floor is right under this one, so a small pool here is the whole of the help
    available: one question about the day they have just told you about. The test is the reading
    the rest of the bot already makes, in either of the two ways it makes it: the mood of the
    whole line, or the words this file already keeps for a day gone wrong.
    """
    if not _a_small_day_shape(clean):
        return False
    text = " ".join(str(clean or "").lower().split())
    # A harm, a crash or a burglary is the trouble pools' line, and they come before this one.
    if NEGATIVE_LINE.search(text) or HARM_NAMED.search(text) or A_DAY_WENT_WRONG.search(text):
        return False
    if ((memory or {}).get("understood") or {}).get("polarity") == -1:
        return True
    # The detail of a day the person has already said went badly: "sorry, bad day" then "sorry,
    # it was the meeting". The words below are for a day named in this line, and the meeting is
    # not one, so without this the detail of a bad day fell to the store's read-back or the floor
    # - a colder reply than the cheer it replaced.
    if _a_detail_of_a_bad_day(memory, text):
        return True
    # A doing of the person's own where only the way it went says so ("i ate badly all week",
    # "i drank too much last night", "i skipped the gym all week"): the line names no bad day, so
    # the words below miss it and the cheer asked what the best bit of it was. It is the same day
    # gone wrong, said through the doing, and the pool it reaches is the one that asks about it.
    if A_DOING_GONE_BADLY.search(text) or (A_THING_SKIPPED.search(text)
                                          and not A_MEAL_SKIPPED.search(text)):
        return True
    # The words are A_DAY_SAID_BADLY and not the wider BAD_DAY_ANYWAY list. That list is only
    # ever subtractive - it takes a cheer away and leaves the line to whatever answers next - so
    # it can afford "waited", "late for" and "two hours"; here the words decide what the bot
    # says, and "i watched a film for two hours" was told "That is a nuisance" for a film.
    return bool(A_DAY_SAID_BADLY.search(text))


def _a_day_asked_without_a_cheer(clean, memory=None):
    """True for the day pool's shape where a word in the line says the day went wrong somewhere.

    Two lists, two jobs. A_DAY_SAID_BADLY is narrow because its words choose the sympathetic pool
    (`_a_bad_time_told`). BAD_DAY_ANYWAY is deliberately wide, because it only ever took the cheer
    away and left the line to whatever answers next - and on today's main what answers next is the
    floor ("I'm listening - say more if it helps"), which is worse than the cheer it replaced:
    "we had a strange day at work" went from "Good to hear. What was the best bit?" to the floor.
    So the wide list gets a question with no presumption in it either way, which is true of a
    strange day at work and of a fish that got gutted ("gutted" is in the list for the row it
    usually appears in).
    """
    if not _a_small_day_shape(clean):
        return False
    text = " ".join(str(clean or "").lower().split())
    # A harm, a crash or a burglary is the trouble pools' line, and they come before this one.
    if NEGATIVE_LINE.search(text) or HARM_NAMED.search(text) or A_DAY_WENT_WRONG.search(text):
        return False
    # A bad day already has the sympathetic pool, and a day the bot has just asked about does not
    # want the same question twice.
    if _a_bad_time_told(clean, memory):
        return False
    if _just_asked_about_the_day(memory):
        return False
    return bool(BAD_DAY_ANYWAY.search(text))
