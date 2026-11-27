"""They ask for what to do next, and the bot has just said it.

The commonest follow-up there is: the bot answers "my washing machine is leaking" with the steps
to take, and the next line is "what do I do?" or "and now?" - or the bot answers "i've got about
400 pounds for a used bike" with what to check, and the next line is "what should I look for?".
Both got a search hedge ("I'm not sure about that one, sorry - I'd rather not guess"), which
reads as if the answer had never been given.

This finds that turn: a question with no thing of its own (every word in it is an ask word), the
answer the bot gave a turn or two ago, and nothing said in between that moved the subject on.
Then the reply is that answer again in short form, not a hedge.

The rule is narrow on purpose:
* the line must name nothing, so "what should i cook tonight" and "how long will it take" never
  come here - they have an answer of their own;
* the bot's own hedges are skipped, never handed back ("I'm not sure about that one" is not an
  answer to repeat);
* only the turns just before this one count, and the answer has to be about the thing the chat
  is still on;
* the answer comes back in its short form, so the long version is never read out twice.

The implementation lives in the `repeat_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `repeat.<name>` is what it was.
"""
import re

from ..compose import pick
from ..compose.whole import a_whole_cut
from ..understanding import understand
from . import counts, facts, history, limits, narrow, recall, topics

from .repeat_part_01 import (  # noqa: F401
    ASK, ASK_VERB, DOINGS, WHOLE_OF_IT, _doings, FILLER, TIME, SELF, QUESTION, RESET_LEAD,
    without_a_reset, LOSS_WORDS, AT_A_LOSS, ANSWER_MODULES, A_STORE_ANSWER, HEDGE, LEADS, BARE_ASK,
    BARE_ASK_NEEDS_A_QUESTION, SAY_AGAIN_LEADS, TRIED_LEADS, NEXT_STEP_EMERGENCY, NEXT_STEP,
    MOVE_ASK, PUT_RIGHT, PUT_RIGHT_ASK, PUT_RIGHT_WORDS, AND_NOW, PUT_RIGHT_LEADS, USE_WITH,
    NEXT_ASK, NEXT_LEADS, ALSO_LEADS, MOVE_LEADS, STEP_SAYS_FIRST, LEAD_SAYS_FIRST, NOW_LEADS,
    LOST_LEADS, BE_FORM, POINTING_AT, AGREEING, AGREEMENT_TAIL, AGREES_ON_ITS_OWN,
    AGREES_IN_A_PHRASE, CHANGE_ASK, CHANGE_LEADS, MORE_LEADS, MOVE_VERBS, STEP_WORDS,
    STEP_WITH_ITS_METHOD, CUT_WORDS, SHORT_STEP, NEEDS_COMPLEMENT, QUALIFIER, LEADING_PHRASE,
    AN_ARTICLE, LEADING_PHRASE_MAX, _the_first_instruction_in_a_long_piece,
    _a_verb_after_a_leading_phrase, OPENERS, DANGLING, PIECE_END, NOT_A_STEP, A_MENU, SENTENCE,
    LEAD_SPLIT, QUOTE_PAIRS, MOST, LEAD_IN, LOOK_BACK, LOOK_BACK_FOR_LESS, ASKS, ASKING_THEM,
    REFER_BACK, ABOUT_THE_BOT, WORDS_WANTED, ECHO_FRAME, STALL, only_said_it_back, _an_echo,
    _names_no_topic, _only_echoes_between, JUST_A_NOD, HELP_SHAPE, HELP_ASK_QUESTION_FIRST,
    NAMED_AFTER_IT, NOT_A_THING, _names_a_thing_of_its_own, CONDITION_CLAUSE, NOT_A_MOVE,
    STEP_VERBS, ORDER, asks_to_put_it_right, a_step_of_the_same_answer, _recent_answers,
    _the_answer_about_what_we_are_on, _short, FIRST_THING, _WEIGHS_ONE_AGAINST, _AFTER_A_NOUN,
    _SUBJECT_OPEN, _EXPLANATION_WORDS, _explains, _a_step_comes_after, _opens_an_instruction,
    _HANGS, _NEGATES, _SO_COMES_THE_STEP, _SO_THE_STEP_FOLLOWS, _SO_DOES_NOT_ASK_SOMETHING_OF_THEM,
    _opening_move,
)
from .repeat_part_02 import (  # noqa: F401
    _A_JUDGEMENT, _a_conditional_move, asks_for_more, a_hand_back, _handed_back_last, _another_part,
    _said_in_a_turn, _says_what_to_do, CLAIMS_IT_WAS_SAID, _said_in_the_chat,
    _claims_what_it_never_said, _handed_back, _FRAME_HEADS, _frame_heads, framed, handed_back,
    _already_repeated, _handed_back_already, LESS, LESS_WORDS, LESS_LEADS, OWN_LEAD, OWN_LEAD_WORDS,
    _a_lead_of_its_own, KEEP_CLAUSE, FIGURES, DIGIT, _kept_clause, HOW_TO, BREVITY_WORDS,
    asks_for_less, KEEPING, ALREADY_SHORT, NO_SHORTER_STILL, NOTHING_TO_CUT, JUST_THIS, WELCOMES,
    _recent_lines, SENTENCE_END, _sentences, _most_condensed, SHORT_ENOUGH, CLAUSE_SPLIT,
    CUT_MID_SENTENCE, _short_enough, _ended, _unbalanced, _the_quotation, _closing_the_quote,
    _read_up_to_the_colon, _keeps, shorter_for, A_LENGTH_ASK, A_BARE_TIME, _a_bare_time,
    LENGTH_BACK, A_PRICE_ASK, POINTING_BACK, PRICE_WORDS, _names_no_thing_of_its_own,
    _the_price_the_answer_gave, asks_what_that_costs, _the_price_in_hand, _a_length_already_handed,
    _a_what_to_do_answer, _a_city_guide_is_the_answer_in_front, _AN_ENTRY_IS_LOOKING,
    _an_entry_answers_it, _words, _a_bare_ask,
)
from .repeat_part_03 import (  # noqa: F401
    _a_help_ask, asks_for_the_move, names_nothing, _a_lead_and_a_step, A_COUNT_OF_MORE_THAN_ONE,
    _the_lead_for, _content, _trouble, TROUBLE, OWNED, SOMEONE_ELSES_LIMIT, _a_thing_of_its_own,
    ACK_OPENS, ACK_AND_REST, after_an_ack, CLOSES_THE_TURN, BROODING, _a_feeling, _the_doing,
    _the_advice, _next_step, _later_part, _opens_a_doing, _the_untried, TRIED, NOT_TRIED,
    QUESTION_MORE, _tried, _says_they_agree, _the_thing_they_named, _agreed, DONE, IRREGULAR_PAST,
    NO_LONGER_TO_DO, _the_stems, _the_act, STANDS_IN, OBJECT_END, _the_object, _the_steps_done,
    _the_answer_gives, _a_step_done, _the_step_just_given, REJOINDER, recent_answers, said_recently,
    _A_STALL, ASKING_TO_START, START_ASK, STARTING_WHAT, STARTING_BACK, STARTING_AT, STARTING_OUT,
    STARTING_INTO, _starting_out_names_a_thing, says_where_to_start, MORE_ASK, IDEAS_ASK,
    IDEAS_ONLY, a_more_ask, WORDING, HOW_IT, _places_to_cut, _inside_a_bracket, LIST_LEAD,
    NOT_A_TAIL, NOT_A_DOING, A_QUESTION, DECLARATIVE, QUESTIONS_THAT_ARE_NOT_STEPS, WHAT_IT_IS,
    ATTEMPT, FIGURE_ASKS, FIGURE_WORDS, FIGURE_SAYING, STILL_SAFE, SAID_SAFE, DO_I_NEED_TO, A_MOVE,
    WHERE_TO_START, PART_ASKS, PART_STAND_INS, NOT_ALONE, PART_OPENS, A_MOVE_WORDS, WHETHER_ASKS,
    METHOD_ASKS, NOT_A_METHOD, A_QUALITY, STILL_ASKS, NOT_A_SUBJECT, GAVE_ASKS, ASK_FRAME, A_FIGURE,
    PAY_FAMILY, A_PAY_WORD, A_PAY_VERB_AT_THE_END, A_TAKE_HOME, A_IM_ON_A_FIGURE, A_PAY_JUDGEMENT,
    PAY_WHEN_WORDS, A_MEASURE_WORD, A_DOING_WORD, FIGURE_NOUNS, GOAL_NOUNS, A_GOAL_LINE,
    A_RATE_LINE,
)
from .repeat_part_04 import (  # noqa: F401
    asks_for_the_same_work, _nothing_but_acknowledgements, _about_the_same_thing,
    _the_chat_is_still_on, _a_question, _a_move, _a_move_in, _the_time_an_earlier_answer_gave,
    answer_for, the_next_move, agreement_with_the_answer, carried_on, _a_list_item, _pieces,
    _the_tail_asks_a_question, _the_colon_tail_kept, _opens_on_a_verb, _the_steps, _the_next_step,
    _the_first_step, _a_new_work, asks_which_part, _leads_for, _a_lead_for, the_move,
    _they_say_they_tried, _the_keys_of,
)
from .repeat_part_05 import (  # noqa: F401
    same_subject, the_figure_asked, answers_nothing, the_advice_was_to_get_seen, the_part_asked,
    WHERE_TO_LOOK, WHERE_TO_LOOK_DEFAULT, WHERE_TO_LOOK_WORDS, _whether_to, _a_stem,
    _where_the_rest_is, what_it_knows, GAVE_LOOK_BACK, A_WERE_ASKS, the_plain_line, A_RATE_OF_TIME,
    A_SCHEDULED_AFTER, A_HAS_THE_LENGTH, NOT_A_FIGURE_ASK, A_PLAN_ASK, A_THE_PLAN_ASK,
    A_THING_NAMED_AFTER_THE_CUE, A_BARE_AMOUNT_ASK, A_BARE_DURATION_ASK, A_HOW_LONG_ITS_BEEN,
    _OWNS_THE_THING, how_long_its_been, A_LINE_THAT_ASKS, A_CORRECTION, A_MARKER_AT_THE_END,
    _a_line_that_corrects, A_NUMBER_WORD, JOINERS, FIGURE_TAIL, A_ONE_MORE, A_GAIN, A_GROUP_WORD,
    A_LOSS, _A_AGE, A_LIST_OF_AGES, _a_list_of_ages, _something_gone, COUNT_ASK, PERIOD_WORD,
    A_RATE_IN_THE_FIGURE, THE_SAME_NUMBER, A_PLURAL_ONLY_NOUN, _the_ask_gave_that_figure,
    _a_count_of_one_with_a_plural, _the_thing_counted, _figures_in, _MONEY_PAID_FOR,
    _AN_AMOUNT_WANTED, _money_paid_for_a_thing, _one_figure, _a_bare_count, _the_same_word,
    _the_corrected, A_TOLD_BACK, NOT_A_THING_ASKED, _the_length_they_mean,
)
from .repeat_part_06 import (  # noqa: F401
    _the_figure_of_a_goal, _the_figure_counts_the_thing, A_NARROWING_ONLY, A_NARROWING_WORDS,
    a_narrowing_and_its_line, _the_turn_that_names_it, the_figure_they_gave, A_FIGURE_WORD,
    _the_store_keeps_this_figure, A_RECALL_CUE, A_POINTS_BACK_HARD, _the_figure_beside_the_thing,
    _every_figure_the_ask_names, asked_back, carries_the_figure, CHANGED_IT, _the_same_words,
    _shortened, _the_answer_again, the_same_question_again,
)
