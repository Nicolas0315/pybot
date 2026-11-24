"""A bare yes/no question about the thing the bot just explained, answered from that answer.

"I think my knee clicks going up the stairs" gets the harmless-or-not answer. Then "is that
bad" arrives, and the bot says "Alright then — good luck with it.": the person asked whether
what it just told them matters, and the reply hands them the door. "is that normal" is worse
still, because it gets "I'm not sure about that one — a search", which disowns the very thing
the bot explained two seconds ago.

The answer is already in the bot's own last line, so this reads it. Three shapes come out of
that reading, and each has its own pool:

- the reply called the thing ordinary ("usually harmless", "that is normal") -> say no, and say
  what would change the answer;
- the reply said to get someone in, with no condition on it -> say yes;
- the reply gave a job to do and a "if it carries on, get someone in" after it -> say it is a
  job rather than a danger, and point at the condition.

Nothing is invented about the subject: every line says what the previous answer already said,
and what would change it. It stands aside for anything that is not bare ("is my knee normal"
names its own subject and belongs to the knowledge base), for a previous turn that was not a
knowledge answer (a safety line's referral is not a verdict to re-read, and "should i be
worried" after one must not be told "no"), for a previous turn with no verdict in it, and for
its own answers, so a person asking twice does not get the same sentence twice.

The implementation lives in the `verdict_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `verdict.<name>` is what it was.
"""
import re

from ..memory import again as again_reply
from ..understanding.normalize import normalise
from . import A_STEP_ASK, pick, why
from ..memory import healing

from .verdict_part_01 import (  # noqa: F401
    _reads_as_good_news, _a_thing_stopped, BARE, HOW_MANY_PEOPLE, DENIES, HARMLESS, SAYS_NORMAL,
    REASSURE, CARE, CONDITIONAL, CONDITIONAL_AFTER, HARD_NEWS_LINES, HARD_NEWS, SYMPATHY,
    COMPARATIVE, URGENT_TIME, A_SYMPTOM_WORD, A_PERSON_THEY_KNOW, A_RELATION_TROUBLE,
    PERSON_ORDINARY, PERSON_CALL, NO_LINES, BOTH_LINES, DO_LINES, FIX_ASKED_LINES,
    FIX_ASKED_NOW_LINES, A_WAIT_IN_THE_STEP, _ASKS_ABOUT_A_STEP, _ASKS_FOR_THE_STEP, _A_FIX_WORD,
    NOT_A_STEP_TO_WATCH, NOT_A_STEP_TO_WATCH_WORDS, CONDITION_LINES, GRIEF_FLOOR_LINES,
    MET_CONDITION_LINES, WHEN_ASK, WORRYING_ASK, WHEN_LINES, WHEN_CALL_LINES, NEEDS_A_CALL,
    _LIST_JOIN, _the_list_before_the_call, CALLS_FOR, IS_A_NUMBER, _NOT_A_SIGN_WORD,
    _the_sign_words, _the_person_for, A_PLAN, A_HOW_TO_ASK, A_DECISION_ASK, SAID_YES, METHOD_DOUBT,
    A_CHECK_ASK, A_THINKING_ABOUT, METHOD_OK_LINES, CHECK_WORKS_LINES, CHECK_ONCE_LINES,
    A_LENGTH_IN_THE_ANSWER, CHECK_WATCH_LINES, _BODY_PARTS, _SYMPTOM_WORDS, _A_BODY_WORD,
    _about_a_body, CHECK_JOB_LINES, ASKS_FINE, ASKS_WRONG, CHOICE_OK_LINES, NOTHING_WARNED_LINES,
    MONEY_TROUBLE_LINES, MONEY_NOUN_WORDS, MONEY_NOT_MET, NOT_MONEY_PAY, A_BODY_IN_THE_LINE,
    _A_NUMBER, MET_LINES, FIGURE_LINES, A_FIGURE_ASK, MONEY_LINES, MONEY_WORD, A_FIGURE,
    A_COMPARISON, JUST_AGE, AGE_LINES, _a_figure_owed, BODY_WORD, SOMEONE_ELSE,
)
from .verdict_part_02 import (  # noqa: F401
    FEELING_FAMILY, FEELING_DOUBT_LINES, ASKS_NORMAL, ASKS_OK, OK_LINES, ORDINARY_NORMAL,
    CARE_NORMAL, CARE_NORMAL_UNKNOWABLE, CARE_NOW, CARE_NOW_NORMAL, DO_NORMAL, CONDITION_NORMAL,
    NOTHING_WARNED_NORMAL, YES_LINES, A_THING_THEY_OWN, A_BODY_WORD, THING_ORDINARY, THING_CALL,
    BACKSTOP_LINES, PEOPLE_CARE, FLOOR_LINES, NEUTRAL_ASK_LINES, A_PLAN_DOUBT_LINES, SOON_LINES,
    HELPED_LINES, WORRIED_ASK, HELPED, YES_SAID_LINES, THROW_AWAY, NOT_TOLD_TO, ONE_OPTION, TESTING,
    THROW_AWAY_LINES, TEST_LINES, STATED_NO, NO_STATED_LINES, ENOUGH_ASK, STATED_ENOUGH,
    ENOUGH_STATED_LINES, STOP_DOING, DANGER, NEGATED, AGAIN, _FILLER, _LEAD_FILLER, _FILL, STEP,
    SPEAK_VERBS, SPEAK_UP, EMERGENCY_CALL, SEE, HOW_TO, DOING_WITH_NO_OBJECT, KNOWING_DOING,
    TIPS_AGAIN, ONE_THING_ADVERB, _ONE_THING_ADVERB, A_HOW_ASK, ONE_THING, AFTER, SPLIT, THEN_OPEN,
    REFER, NAMES_A_CLINICIAN, DECLARATIVE_REFERRAL, WHEN, HANGING, IMPERATIVES, LIST_STEP_LINES,
    STEP_LINES, STEP_DETAIL_LINES, FIRST_ITSELF, STEP_ALREADY_FIRST_LINES, SUBJECT_OPEN,
    EXPLANATION_WORDS, _is_an_explanation, STEP_ONE_LINES, STEP_KEPT_LINES, ALSO_LINES, ASKS_THEM,
    ONE_TURN_LINES, ONE_TURN_PLAIN_LINES, ALL_OF_IT_LINES, QUESTION_BACK_LINES, ASKED_FIRST_LINES,
    OFFER_TAKEN_LINES, SEE_NOW_LINES, SEE_ANYWAY_LINES, SEE_STATED_LINES, NOTHING_LINES,
    SEE_NONE_LINES, POOLS, OWN_LINES, _own_pattern,
)
from .verdict_part_03 import (  # noqa: F401
    _a_job_somewhere, _they_named_the_sign_themselves, _a_doubt_about_money, _is_a_comparison,
    OWN_PATTERN, _ACK_PATTERN, ECHO_WORDS, takes_a_fact_back, _say, _a_report_line, _flat, READABLE,
    UNREADABLE, COMPOSED, RULED_BY_THE_COMPOSER, rules_on_the_doubt, RUN, _WORD, _AFTER_A_NOUN,
    opens_on_a_job, PUNT_START, PUNT_OFFER, PUNT_CHAT, _a_punt, _skip_the_derived,
    _the_news_just_before, ECHO_FILLER, _words, _is_an_echo, RECAP_FILLER, _is_a_recap,
    _last_line_that_named_a_call, URGENT_CALL, EMERGENCY_ORDER, EMERGENCY_CALL_OPEN,
    _last_person_line, _the_worst_thing_they_said, _as_written, _a_thing_they_own,
    _a_person_they_know, _the_line_behind, _the_plan_they_brought, A_CHECK_ON_A_PLAN_LINES,
    A_CHECK_ON_A_PLAN, CONSIDERING, _considering, _the_last_line_was_mine, _last_module, OWN_DOING,
    CAN_HURT, NAMES_A_TRADE, A_KEEP_OR_STOP, THE_PLAN_CAN_HURT_LINES, _the_plan_can_hurt,
    _the_answer_already_warned, _about_the_person, _own_doing, _a_plan_or_a_choice, _good_news,
    OVER_VERB, STILL_GOING, _an_event_that_is_over, _nothing_to_be_long_about, _first,
    _a_throw_away, SIGN, ASKING_HOW_TO_TELL, _the_person_line, _said_no,
)
from .verdict_part_04 import (  # noqa: F401
    the_fix_asked, carries_the_answer, _last_reply, _a_call_for_now, _the_call_sentence,
    _said_enough, _the_person_gave_the_sign, LATER_CONDITION, TRADE, _care_for_now, _sentence_at,
    _not_fenced, NEGATED_BEFORE, _said_without_a_not, _first_positive, A_FREQUENCY_SAID,
    A_FREQUENCY_ASKED, TIME_NOW, CONDITION_CLAUSE, _cut_condition, _first_sentence_end,
    _told_to_act, GO_FROM, _a_plain_go, _opening, FENCED_IN_SENTENCE, THING_WORDS, _the_thing,
    _referral_about_the_thing, _echoes_the_person, _kept_step, _only_a_verdict,
    _the_line_just_given, _the_answer_before_that, _word_runs, _says_it_again,
    _already_asked_for_a_step, _the_referral_sentence, _the_line_is_the_threshold,
    _most_of_the_line, A_STATEMENT, TARGET_SHAPE, _listed, TRIM, TRIM_INSTRUMENT, CONTRAST,
    STEP_WORDS, LONG_STEP_WORDS, STEP_LONG, COPULA, DETAIL_STATEMENT, CONDITIONAL_OPEN,
    ABOUT_THE_TALK, _cut_on, NEGATIVE_OPEN, HELPS, HEAD_REFUSES, DESCRIBES, _shorten, CONTINUES,
    ORDER_CONTINUES, FRAME_AND, _cut_at_a_join, _first_clause, QUESTION_FRAME, OFFER_QUESTION,
    _an_offer_is_waiting, _INVITATION, THE_PLEA, AN_OFFER, _after_a_comfort_line, _A_DASH,
    _AN_OPENER, _the_question_asked, _ends_on_a_question, _is_a_question,
)
from .verdict_part_05 import (  # noqa: F401
    _the_call_and_its_reason, _a_plan_doubt, _behind_a_description, _unconditional_care,
    _the_fence_is_met, _a_frequency_already_said, _condition_after_care, _referral, _step, _steps,
    _doing_word, _action_count, _no_hanging_end, CONDITION_VERBS, CONDITION_HANGING, REFER_VERB,
    RESTATED, RELATIVE, _described_clause, _in_a_described_clause, _a_described_condition,
    _an_if_that_is_a_condition, LOOK_AND_SEE, _a_judgement_fence, _after_the_if, _when,
    JUDGED_REFERRAL, STATES_A_REFERRAL, NAMES_NOTHING, STATED_LONGEST, _stated_before_the_judgement,
    _stated_referral, DOING, _danger, _a_how_to, _round_robin, _says_what_it_is, LONG_SPAN,
    HEDGE_SPAN, _the_line_it_answered, _past_the_timescale, _subject_words, _the_span_further_up,
    FENCE_FILLER, _stems, _the_fence_is_their_own_line, LOSS_WORDS, MOOD, _a_mood, _about_a_death,
    _the_last_person_lines,
)
from .verdict_part_06 import (  # noqa: F401
    ADVICE_OK_LINES, ASKED_FOR_A_CALL, _a_job_to_do, _the_advice_itself, A_REFUSAL,
    _an_ask_for_a_call, _a_fix_with_no_warning, DIRECTED_LINES, OWED_LINES, OWED,
    _somebody_owes_them, _a_reading_of_the_feeling, _care_pool, _the_knowledge_has_this,
    a_check_on_the_reply, _an_amount_asked, _the_last_thing_said_is_a_nod, _a_check_on_the_method,
    A_DOUBT_ABOUT_THE_THING, reply_for, HANDED_BACK_LINES, _A_RANGE_OF_ITS_OWN, _A_REFERRAL_OUT,
    _A_STOP, _the_referral_it_closed_on, _the_range_it_gave, _STEP_OPENERS,
    _an_instruction_and_nothing_else, ASKED_THEM_LINES, A_WORRY_IN_THE_LINE, _AN_OFFER,
    _the_floor_asked_them_something, _a_feeling_of_their_own,
)
from .verdict_part_07 import (  # noqa: F401
    answers_the_ask, HAND_OVER_WORDS, _the_other_thing_in_the_answer, _step_sentence,
    _up_to_a_break, _an_instruction_sentence, _the_answer_under_a_frame, FRONT_LEAD, FRONT_THIS,
    FRONT_WHEN, FRONT_SUBJECT_WORDS, _the_front_names_what_is_in_hand, next_step,
)
