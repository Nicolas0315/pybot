"""Rows of fallback, kept in their own file so fallback.py stays under the publisher's 1 MiB limit.

Nothing here is new: every name below was written in fallback.py and moved out unchanged, verbatim
and in the same order, when that file went over the limit. It is imported from the last line
of fallback.py, so the two still read as one module.

The implementation lives in the `fallback_chain_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `fallback_chain.<name>` is what it was.
"""

import random
import re
import string
from ..memory import ack, facts, history, last_bot, last_user, reject, repeat, swap
from ..memory import stuck as stuck_line
from ..understanding import understand
from ..understanding import kinds as understanding_kinds
from ..understanding.body import GOING_BOTH_WAYS
from ..understanding.kinds import ANSWERING_A_QUOTED_ASK, greeting_only, verdicts_a_thing
from ..understanding.topics import THE_PEOPLE
from . import DOUBT, DOUBTED, NEARLY, says_it_has_lingered, step_when_low, turned, turns_round
from .limit import NOTHING_THAT_LIMITS, a_limit_on_the_answer
from . import (badnews, circumstance, draft, finding_out, goodnews, handoff, harm, leaving, loss,
               morning_after, no_eyes, onething, pick, prices, quantity,
               reaction as answer_reaction, remark, safetyask, trouble, unseen, why, worn)
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
from .fallback_data import (A_CARE_HOME, A_CARE_HOME_BRING, A_CARE_HOME_GUILT, A_CARE_HOME_MOVED,
                            A_CARE_HOME_VISITING, A_DISMISSAL, A_LOVE_FOR_PEOPLE,
                            A_LOVE_FOR_SOMEONE, A_SORRY_ON_ITS_OWN, ABOUT, ABOUT_SELF, ABOUT_TALLY,
                            ABOUT_WORDS, ACK, ACKS, ACK_AFTER_TROUBLE, ACK_WARM, ACTS_FOR_ME,
                            AGREEMENT, AIM_HEADS, ANIMALS, A_BIRTHDAY_STILL_TO_COME,
                            A_CHILD_LEAVING, A_CHILD_LEFT, A_COST_SOMEBODY_ASKS, A_DREAD,
                            A_GOOD_TIME, A_GOOD_TIME_IN_A_CARE_THREAD, A_LAUGH,
                            A_MOOD_WITH_A_CATCH, A_NEWS_OF_SOMETHING_ELSE, A_NEWS_OF_WEATHER,
                            A_REST_OF_A_GOOD_DAY, A_REST_OF_A_HARD_DAY, A_SMALL_DAY, A_SUGGESTED,
                            A_SUGGESTED_BY_SOMEONE, A_THING_LOOKS_SAD, A_THING_THEY_REGRET,
                            A_BETRAYAL, A_WANT_IT_OVER, BAD_STRETCH, BAD_STRETCH_REPLIES,
                            BARE_PICK_WEAR_COLD, BARE_PICK_WEAR_HOT, BARE_PICK_WEAR_WET,
                            BEHIND_ON_MONEY, BODY_ALSO, BODY_LEAD, BODY_PART_QUALIFIER,
                            BODY_PART_TAIL, BODY_POOLS, BODY_SITUATION, BODY_STATES, BODY_TAIL,
                            BOUND_FOR, CAME_BACK, CARD_LINES, CARING, CARING_FOR_A_BODY,
                            CHECK_PHRASES, CLOSED_DOOR, COMFORT_SAID, CONGRATS, CROWD, CUT_FOR,
                            DATES_KEEP_SLIPPING, DECLINED_PLAN, DECLINED_PLAN_GENTLE,
                            DISH_DETERMINER, DISH_PARTICIPLE, DITHER_DECIDE, STUCK_AFTER_TROUBLE,
                            RUN_OUT_LINES, DITHER_OPEN_LINES, DITHER_TWO_WAY_LINES, DONE_NOT_THIS,
                            DONE_VERB, DOUBLE_BOOKED, EMPTY, EXPERT_WORDS, FLAT, FOUND_IT,
                            FRAME_WORDS, GREETING, GRIEF_AFTER, GRIEVANCE, HABIT_ACT, HABIT_REPLY,
                            HAND, HEALTH_WORDS, HANDS_BACK, HELP_ALREADY, HOUSE_VERB, HOW_ARE_YOU,
                            IDIOM_GLAD, IDIOM_SHY, IMPERATIVE, INVITED, INVITED_TO_TALK, JUNK_CUES,
                            KEEPS_FORGETTING, KNOCKED, LANDED_BAD, LATE_BEHIND_LINES,
                            LATE_NOW_LINES, LEFT_POOL, LEFT_POOL_GONE, LOCKED_OUT_LINES,
                            LOCKED_OUT_OF_THE_CAR, LOST_A_THING, LOST_A_THING_AGAIN,
                            LOW_DAY_REPLIES, LUMP, MILESTONE, MISHAP_BACK, MY_WORKINGS,
                            NAMED_NEGATIVE, NEGATIVE, NEGATIVE_CUES, NEGATORS, NOTHING_AT_ALL,
                            CONTRAST, NEUTRAL, NEVER_MIND, A_CORRECTION_TAKEN, NEWS_TO_COME,
                            NOT_FIT_ENOUGH, NOT_TOO_OLD, NO_DIRECTION_REPLY, ONE_SKILL_RATED,
                            PAST_STATE_CUES, PENDING_DOUBT, PENDING_LANDED, PENDING_WAITING,
                            PENDING_WHEN, PERSON_WORDS, PET_CONDITION_TROUBLE, PET_LOW_REPLY,
                            PET_TROUBLE, PLAN, PLAN_DONE, PLAN_DONE_ACK, PLAN_KNOCKED, POSITIVE,
                            POSITIVE_CUES, A_WAIT_ENDING, SOMETHING_CAME_APART, PREGNANCY_BLEEDING,
                            PRESENT, PUNT, QUOTE_LINES, REACTIONS_CARE, REACTIONS_SAID,
                            REACTION_REPEAT, RELATIONSHIP_DECISION, RELIEF, ROUTINE, ROUTINE_NOT,
                            ROUTINE_PHRASES, ROUTINE_WORDS, RUMINATION_REPLIES,
                            SECRETS_KEEP_SLIPPING, SELF_BLAME, SOMEBODY_HURT, SOMEONE_GONE,
                            SOMEONE_LEAVING, SOMEONE_SERIOUSLY_ILL, RETURNED_TO_A_THING,
                            RETURNED_TO_IT, RETURNED_TO_IT_FIRST, SORRY_FOR_ASKING,
                            SORRY_ON_ITS_OWN, STATE_CUES, STRETCH_OF_TIME, SUDDEN_LOSS, SYMPTOM,
                            SYMPTOM_COLD, TELL_HARD_LINES, THANKS, THANKS_THEN_SAID,
                            THE_FIRST_HOUR_AND_A_CHILD, TIGHT_MONEY, TIGHT_MONEY_MORE, TIPS_LINES,
                            TOO_MUCH, TOO_MUCH_PHRASES, ELDER_AID_REPLIES, ELDER_CLINIC_REPLIES,
                            ELDER_DOCTOR_REPLIES, ELDER_HELP_REPLIES, UNKNOWN, UNKNOWN_HEALTH,
                            UNKNOWN_MONEY, UNKNOWN_WORD, VERDICT_ANNOY, VERDICT_HEAVY,
                            VERDICT_LUCK, VERDICT_NUMB, VERDICT_ROUGH, VERDICT_SHAME, VET_WHO,
                            WALKED_INTO_POOL, WIN_IN_A_SILENCE, WIN_AND_A_COST, WORDING_LINES,
                            YOU_SUBJECTS, _DAY_WORDS, _NO_DAY_OF_THEIR_OWN, _START_ASK,
                            _THING_DONE_LINES, _WAS)

# The day that went badly and the name that came from somebody: the pools those readings choose
# from. They are in the data file with the rest, and the readings that use them live here.
from .fallback_data import (
    A_BAD_TIME_TOLD, A_DAY_ASKED_PLAIN, A_NAMED_AFTER, A_NAMED_AFTER_THEM, A_NAME_STORY,
    A_NAME_TOLD, A_PLAN_THAT_FELL_THROUGH, A_STATE_NOW, A_STATE_PAST, A_THING_CAME_OUT_WRONG,
)
from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    ABSENCE,
    A_BOOKING_AHEAD,
    A_BOOKING_AHEAD_DATED,
    A_WAY_OF_BEING,
    BARE_PICK_LOST,
    DITHER_SUBJECT,
    HABIT_PROBLEM_ACT,
    HEAVY_NEWS,
    HURT_EVENT,
    LEFT_BEHIND,
    NAMED_BODIES,
    NOT_WHAT_I_SAID,
    NUMBER_PLACES,
    ONLINE_ASK,
    PASSED_OUT,
    PASSING_OUT_A_THING,
    PAUSE_IN_A_SAFETY_THREAD,
    PRIVACY_ASK,
    PRIVACY_SHAPES,
    THE_DAY,
    WORDING_SOMEONE,
    _LANDED,
)

# What the moved rows take from fallback.py, which is fully defined by the time this
# module is imported, because fallback.py imports it from its own last line.
from .fallback_part_01 import (
    A_BIT_PAST_IT, A_CHILD, A_HELP_WORD, DITHER, DITHER_OPEN, DITHER_YES_NO, EMERGENCY_CALL,
    HANDS_IT_BACK, HEALTH_MODIFIER, HELP_SERVICE, POLICE_CALL, _a_carer_refused, _a_dead_end,
    _matchable, _only_the_stuck_phrase, _plain, _reads_as_dither, _run_out, _weighs_a_choice,
)
from .fallback_part_02 import (
    UNKNOWN, _a_thing_they_started, _money_decision, _names_their_age, _the_line_before,
    reads_as_if_i_saw,
)
from .fallback_part_03 import (
    CLOSED_DOOR, NAMED_NEGATIVE, NEGATIVE, _a_start_ask, _a_subject_above, _asks_for_help,
    _occasion_pool, _says_only_what_they_said, WEATHER_COLD, WEATHER_HOT, WEATHER_WET,
)
from .fallback_part_04 import (
    FORGETS_AGAIN, FORGETS_A_CLASH, FORGET_A_DATE, FORGET_A_SECRET, LEAVING_A_PERSON,
    NOT_LEAVING_ANYONE, SYMPTOM_LINGERS, THE_LEAVE_HAS_HAPPENED, _CAUGHT, _ILL, _LUMP,
    _a_cost_somebody_asks, _a_guessed_result, _a_plan_on_the_table, _a_time_in_it, _an_invitation,
    _an_open_result, _no_words, _the_day_described, _the_line_cancels, _the_news_landed,
    a_fresh_death_and_the_words, reads_as_a_narrowing, reads_as_someone_close_is_ill,
    the_bound_said, the_limits_said,
)
from .fallback_part_05 import (
    FLAT_LINE, HARM_ANYWHERE, HARM_NAMED, HARM_ON_ME, A_HURT_MYSELF, LATE_ASKS, LATE_NOT_A_TIME,
    LATE_NOT_IT, LATE_NOW, _a_declined_plan, _a_knock_into_a_thing, _a_knock_on_oneself,
    _a_verdict_line, _reaction_pool, _someone_else_dropped_it, _the_heavy_pool,
    _the_person_already_said_it, _the_turn_before_was_a_heavy_one, _verdict_pool, a_happening_now,
    the_answer_to_cut,
)
from .fallback_part_06 import (
    A_COMPARISON_OF_STANDING, IDIOM_GLAD, IDIOM_SHY, LOST_QUESTION, NEGATIVE_LINE, NOT_SELF, PLAN,
    reads_as_a_change_of_medicine, PLAN_MEDICINE_REPLY, PLAN_MEDICINE_SLOW,
    PLAN_MEDICINE_SLOW_REPLY, PLAN_IDIOM, PLAN_NOT_YET, _a_mishap, _a_mishap_to_ask_about,
    _a_relationship_ending, _own_feeling, _plan_reported, _a_promise_that_keeps_moving,
    _summons_pool, _thing_done_scan, a_comparison_of_standing,
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
    DATE_AHEAD, _a_day_ahead, _a_good_time, _dreading, _grief_thread, _grievance_thread,
    _looking_forward, _someone_else_minding, _something_funny, _their_own_slip, _wants_it_over,
)
from .fallback_part_14 import (
    BODY_PART, THANKS_GOOD_AGAIN, THANKS_NO_BETTER, THANKS_WENT_BADLY,
    _a_care_thread_to_leave_alone, _a_hard_week, _a_loss_recently, _a_mood_word, _came_back,
    _in_a_loss_thread, _in_an_aim, _in_sudden_loss_thread, _is_rumination, _opens_a_question,
    _reads_as_illness, _am_i_a_nuisance, _sorry_for_asking, _acknowledges_alone, _thanks_then_said,
    _thanks_with_more, _the_last_line_was_a_fault, _the_last_line_was_bad_news,
    a_loss_in_the_thread, reads_as_a_report, reads_as_a_return, _a_chat_behind_it, the_advice,
)
from .fallback_part_15 import (
    FOOD_TOPICS, OWN_THING, _a_bad_line_above, _a_doable, _a_leaning_side,
    _a_question_about_the_person, _a_refusal_to_answer, _action, _after_advice, _after_safety,
    _my_pick, _named_draft, _taste, _thanks_news_went_badly, _the_last_line_was_heavy,
    _the_stretch_of_time, _thing_done_pool, _tips, _trouble, _unknown, _who_for, _words,
    in_a_safety_thread, reading, the_dislike_ask, the_lost_ask_reply, who_settles,
)
from .fallback import (
    ABOUT, ABOUT_SELF, ABOUT_TALLY, ABOUT_WORDS, ACK, ACKS, ACK_AFTER_TROUBLE, ACK_WARM,
    ACTS_FOR_ME, AGREEMENT, AIM_HEADS, ANIMALS, ANSWERING_A_QUOTED_ASK, A_BIRTHDAY_STILL_TO_COME,
    A_CHILD_LEAVING, A_CHILD_LEFT, A_COST_SOMEBODY_ASKS, A_DISMISSAL, A_DREAD, A_GOOD_TIME,
    A_GOOD_TIME_IN_A_CARE_THREAD, A_LAUGH, A_MOOD_WITH_A_CATCH, A_SMALL_DAY, A_SORRY_ON_ITS_OWN,
    A_SUGGESTED, A_SUGGESTED_BY_SOMEONE, A_THING_LOOKS_SAD, A_THING_THEY_REGRET, A_WANT_IT_OVER,
    A_WAY_OF_BEING, BAD_STRETCH, BAD_STRETCH_REPLIES, BEHIND_ON_MONEY, BODY_ALSO, BODY_LEAD,
    BODY_PART_QUALIFIER, BODY_PART_TAIL, BODY_POOLS, BODY_SITUATION, BODY_STATES, BODY_TAIL,
    BOUND_FOR, CAME_BACK, CARD_LINES, CARING, CARING_FOR_A_BODY, CHECK_PHRASES, COMFORT_SAID,
    CONGRATS, CROWD, CUT_FOR, DATES_KEEP_SLIPPING, DECLINED_PLAN, DECLINED_PLAN_GENTLE,
    DISH_DETERMINER, DISH_PARTICIPLE, DITHER_DECIDE, DITHER_OPEN_LINES, DITHER_TWO_WAY_LINES,
    DONE_NOT_THIS, DONE_VERB, DOUBLE_BOOKED, DOUBT, DOUBTED, ELDER_AID_REPLIES,
    ELDER_CLINIC_REPLIES, ELDER_DOCTOR_REPLIES, ELDER_HELP_REPLIES, EMBARRASSED, EMPTY,
    EXPERT_WORDS, FLAT, FOUND_IT, FRAME_WORDS, GOING_BOTH_WAYS, GREETING, GRIEF_AFTER, GRIEVANCE,
    HABIT_ACT, HABIT_PROBLEM_ACT, HABIT_REPLY, HAND, HANDS_BACK, HEALTH_WORDS, HELP_ALREADY,
    HOUSE_VERB, HOW_ARE_YOU, HURT_EVENT, IMPERATIVE, INVITED, INVITED_TO_TALK,
    A_GOODNESS_ASKED_OF_ME, A_SKILL_ASKED_OF_ME, ASKED_A_RATING, ASKED_IF_GOOD, I_RATE_A_SKILL,
    JUNK_CUES, KEEPS_FORGETTING, KNOCKED, LANDED_BAD, LATE_BEHIND_LINES, LATE_NOW_LINES, LAUGHED_AT,
    LEFT_BEHIND, LEFT_POOL, LEFT_POOL_GONE, LOCKED_OUT_LINES, LOCKED_OUT_OF_THE_CAR, LOST_A_THING,
    LOST_A_THING_AGAIN, LOW_DAY_REPLIES, LUMP, MILESTONE, MISHAP_BACK, NEARLY, NEGATIVE_CUES,
    NEGATORS, NEUTRAL, NEVER_MIND, NEWS_TO_COME, NOT_FIT_ENOUGH, A_CORRECTION_TAKEN, NOT_TOO_OLD,
    NO_DIRECTION_REPLY, ONE_SKILL_RATED, PAST_STATE_CUES, PENDING_DOUBT, PENDING_LANDED,
    PENDING_WAITING, PENDING_WHEN, PERSON_WORDS, PET_CONDITION_TROUBLE, PET_TROUBLE, PLAN_DONE,
    PLAN_DONE_ACK, PLAN_KNOCKED, POSITIVE, POSITIVE_CUES, PREGNANCY_BLEEDING, PRESENT, PUNT,
    QUOTE_LINES, RATES_A_SKILL, REACTIONS_CARE, REACTIONS_SAID, REACTION_REPEAT,
    RELATIONSHIP_DECISION, RELIEF, ROUTINE, ROUTINE_NOT, ROUTINE_PHRASES, ROUTINE_WORDS,
    RUMINATION_REPLIES, RUN_OUT_LINES, SECRETS_KEEP_SLIPPING, SELF_BLAME, SELF_BLAME_ASKS,
    SELF_SUBJECT, SOMEBODY_HURT, SOMEONE_GONE, SOMEONE_LEAVING, SOMEONE_SERIOUSLY_ILL,
    SORRY_FOR_ASKING, SORRY_ON_ITS_OWN, STATE_CUES, STRETCH_OF_TIME, STUCK_AFTER_TROUBLE,
    SUDDEN_LOSS, SYMPTOM, SYMPTOM_COLD, TELL_HARD_LINES, THANKS, THANKS_THEN_SAID,
    THE_FIRST_HOUR_AND_A_CHILD, TIGHT_MONEY, TIGHT_MONEY_MORE, TIPS_LINES, TOO_MUCH,
    TOO_MUCH_PHRASES, UNKNOWN_HEALTH, UNKNOWN_MONEY, UNKNOWN_WORD, VET_WHO, WALKED_INTO_POOL,
    WIN_IN_A_SILENCE, WORDING_LINES, WOULD_HAVE_BEEN, YOU_SUBJECTS, _DAY_WORDS,
    _NO_DAY_OF_THEIR_OWN, _START_ASK, _THING_DONE_LINES, _WAS, ack, answer_reaction, circumstance,
    draft, facts, finding_out, goodnews, greeting_only, handoff, last_bot, last_user, leaving, loss,
    no_eyes, onething, quantity, random, re, reads_as_a_carer_body, reads_as_a_clear_result,
    reads_as_a_closed_door, reads_as_a_leaving_already_gone, reads_as_a_pet_condition,
    reads_as_a_win_nobody_noticed, reads_as_an_award_lost, reads_as_an_occasion, reads_as_bad_news,
    reads_as_good_news, reads_as_news_to_come, reads_as_news_with_a_name,
    reads_as_pregnancy_bleeding, reads_as_recovery, reads_as_settled, reads_as_sudden_loss,
    reads_as_the_leaving, reads_as_the_speakers_own_plan, reads_for_a_carer, reads_for_a_pet,
    reads_like_a_symptom, remark, says_it_has_lingered, step_when_low, stuck_line, swap, trouble,
    turns_round, understand, unseen, verdicts_a_thing, why, worn, worry_on_the_table,
)

from .fallback_chain_part_01 import (  # noqa: F401
    FEEL_COPULA, _body_state, _a_part_in_a_state, _a_part_is_cold, _state_from, _the_state,
    HABIT_STATED, HABIT_NOT, HABIT_MIND_IT, _habit_is_a_problem, NOT_ABOUT_THEM,
    _a_claim_about_a_thing, ACT_OPENER, ACT_THING, ADDRESSED, BOOKING_THING, A_MESSAGE_OR_A_FORM,
    KEEP_ME_POSTED, ACT_FOR_ME, REMIND_ME, ACT_REPORT_TAIL, ACT_CHOICE, ACT_OWN_STEP, ACT_SETTING,
    POLITE_ASK, ACTS_IN_A_DIARY, ACTS_ON_A_PHONE, ACTS_AN_ERRAND, HANDS_IT_OVER_HERE,
    NOT_A_THING_TO_GET, CAN_DO_ITSELF, ACTS_ON_A_PHONE_LINES, ACTS_AN_ERRAND_LINES,
    ACTS_IN_A_DIARY_LINES, ACTS_ON_A_CLOCK_LINES, ACTS_ON_A_DOCUMENT_LINES, ORDER_OPENER,
    ORDER_A_MESSAGE, ORDER_A_BUY, ORDER_A_RECORD, ORDER_A_CLOCK, ORDER_A_DOCUMENT, ORDER_A_REPORT,
    ORDER_NOT_A_JOB, _an_order_it_cannot_do, _act_asked_of_me, _the_store_has_the_recall,
    _acts_for_me, _reads_as_a_bad_stretch, _cue_negated, _a_state_in_the_past,
    _the_win_is_someone_elses, THINGS_THAT_STOP, THINGS_THAT_STOP_AFTER_UP, THE_WORDS_BETWEEN,
    PLEASURE_WORD, NOTHING_AND_A_PLEASURE, A_COMPARISON, NOTHING_NEGATED, PLEASURE_GONE_OUT,
    FEELING_NOTHING, PLEASURE_ABOUT_ONE_THING, reads_as_no_pleasure, ABOUT_THE_BOT_LINES,
    ABOUT_THE_BOT, reads_as_a_question_about_the_bot, PLEASURE_GONE_LINES, _a_thing_stopping_after,
    _A_HURT_DONE, _A_BODY_WORD, _A_HARM_HAD, _A_ILLNESS_WORD, _A_HARM_ILL, _A_HARM_ILL_NOT,
    _A_HARM_IDIOM, _A_HARM_KNOCK, _A_OUT_OF_SOCKET, _A_IN_AGONY, _A_PART_WENT, _A_SOMEONE,
    _A_HURT_BY_SOMEONE, _A_HURT_BY_SOMEONE_NOT, _A_PART_OUT, _A_PROGNOSIS, _A_PROGNOSIS_THAT_IS_NOT,
)
from .fallback_chain_part_02 import (  # noqa: F401
    reads_as_a_flat_habit, _flat_habit_stated, _a_harm_said, _A_BREAK_THAT_IS_GOOD, _BREAK_WORDS,
    _mood, _no_such_thing_before, _mixed_seed, SAYS_A_FEELING, A_FEELING_IN_THE_LINE,
    _only_what_the_line_gives, _choose, _a_birthday_still_to_come, _the_birthday_said_back,
    _ROUTINE_NOT_SHAPE, _UNDERTAKING, _somebody_elses_day_in_thread, A_LIST_ON_THE_TABLE,
    _the_person_named_a_list, _routine_pool, _asks_the_bot, _words, _reads, ASK_SHAPE, FRAME_PREFIX,
    _restated, OWN_THING, A_MOOD, NEAR_MISS, NEAR_MISS_REPLY, _a_near_miss, _a_things_state,
    _A_CORRECTION, TAKING_SOMETHING_BACK, SAYS_A_THING, THE_THING_ITSELF, ASKS_AFTER_THE_OPENER,
    THE_OPENER, _a_chat_to_correct, _takes_something_back, _a_lateness_report, HURT_SOMEBODY,
    HURT_BUT_FINE, HURT_FIGURE, HURT_ON_THE_SPEAKER, HURT_DEATH, _somebody_hurt, LOW_DAY,
    LOW_DAY_MINE, LOW_DAY_NOT_MINE, _a_low_day, LOVE_ONE, LOVE_GROUP, LOVE_PERSON, LOVE_OPENER,
    LOVE_TAIL, LOVES_SOMEONE, LOVES_A_GROUP, LOVES_PEOPLE, LOVE_START, _loves_people,
    _loves_someone, A_CLOCK, A_TIME_SAID, CLOCK_THE_DEPARTURE, CLOCK_SHAPE, A_LENGTH,
    CLOCK_NOT_THIS, CLOCK_ASKED, CLOCK_ABOUT_THE_JOB, CLOCK_SOMEONE_ELSE, AT_THE_CLOCK,
    _the_clock_pool, _the_time_said, _the_morning_has_a_clock, OPTION_ON_THE_TABLE,
    _options_already_up, _reads_value, COUNTDOWN_ASK, COUNTDOWN_TO, COUNTDOWN_AFTER_CARE, COUNTED,
)
from .fallback_chain_part_03 import (  # noqa: F401
    _a_countdown_in_a_care_thread, A_REGRET_DOING, NOT_A_REGRET, SNAPPED_A_PHOTO, A_MISTAKE,
    THE_JOB_NAMED, NOT_A_JOB_BUT_A_PERSON, WHO_DID_IT, A_WRONG_PLAIN, A_WRONG_SAID, A_WRONG_AIMED,
    A_WRONG_ABOUT_A_THING, FOUND_IT_OUT, FOUND_OUT, _a_betrayal, _a_thing_they_regret, DAY_PAST,
    A_DAY_SUBJECT, PAST_DOING, A_SYMPTOM_PHRASE, NOT_A_DAY_DONE, _a_care_home_line,
    HAVE_GOT_A_THING, A_CROWD, A_MILESTONE, NOT_A_CROWD_AHEAD, CROWD_ORDER, A_CROWD_AHEAD,
    _the_crowd_is_ahead, A_HARD_DAY_MOOD, _an_emotion, _just_asked_about_the_day,
    _A_NEGATIVE_AUXILIARY, NOT_A_DAY_SAID, _A_TELLING_OF_WRONG, A_BETRAYAL_FOUND_OUT, _AN_ASKING,
    _AN_ATTEMPT_COUNT, AN_ATTEMPT_AT_SOMEONE, SOMEONE_ELSE_NAMED, A_CHILDHOOD_MEMORY,
    THEIR_OWN_DOING, A_VISIT, _a_day_of_someone_else, A_BARE_MODIFIER, _a_thing_happened,
    A_THING_GOT_AHEAD, GOT_AHEAD_GONE, A_MONTH, GOT_AHEAD_NOT_A_DATE, _a_thing_got_ahead,
    PROBLEM_STATED, SOMETHING_UP, _a_problem_stated, WEAR_ASK, WEAR_WHEN_NOTHING_ANSWERS,
    NOTHING_TO_WEAR, NOTHING_TO_WEAR_REPLIES, _says_there_is_nothing_to_wear,
    _a_wear_ask_about_a_day, HOT_FIGURE, WEATHER_SUN, COLD_FIGURE, _the_wear_pool_for_the_line,
    A_BAD_THING_NAMED, A_HAND_OUT, A_DAY_WENT_WRONG, _A_SYMPATHY, _A_BODY_UNWELL, _A_DETAIL_OPENING,
    A_LOOKING_BACK, _a_detail_about_what_was_said, SOMEONE_DONE_WRONG, BAD_DAY_ANYWAY, FOOD_TOPICS,
    _a_dish_name, _repaired_of, A_NAME_IS_NOT_A_DAY, A_NAMES_TOLD, A_NAME_A_HOUSEHOLD_TAKES,
    NOT_A_NAME_WORD,
)
from .fallback_chain_part_04 import (  # noqa: F401
    _answers_the_correction, reply_for, _reply_for, _a_day_told_instead_of_the_receipt,
    _the_rest_of_the_day, _a_small_day, _a_name_told, NAMED_AFTER, A_POSSESSIVE_OF_MINE,
    _named_after_reply, _a_name_told_reply, STATE_NOT_A_DOING, BARE_STATE, STATE_THEN,
    STATE_IN_THE_PAST, PLAN_THAT_FELL_THROUGH, _a_state_of_theirs, RESULT_WENT_WRONG, BOT_WAS_SORRY,
    A_DAY_SAID_BADLY, A_DOING_GONE_BADLY, A_THING_SKIPPED, A_MEAL_SKIPPED, _a_day_said_badly,
    _the_last_exchange, _the_day_was_already_bad, _a_detail_of_a_bad_day, A_BEING_DONE_NOW,
    A_DECISION_NOT_A_DAY, A_WISH, A_SUM_STATED, PRICE_NOUNS, NO_THING_SAID, MONEY_IN_NOUNS,
    MONEY_IN_SHAPES, _money_came_to_them, _a_sum_with_nothing_beside_it, A_ASKING_WORD,
    A_REPORTED_NOT_LIVED, A_NEWS_IS_A_CHANGE, A_NEWS_IS_WEATHER, _a_report_from_elsewhere,
    _a_small_day_shape, _a_bad_time_told, _a_day_asked_without_a_cheer,
)
from .fallback_chain_part_05 import (  # noqa: F401
    _a_report_with_no_pronoun, takes_as_it_comes, TAKES_AS_IT_COMES,
)
