"""Answers everyday requests from the knowledge base (bot/knowledge).

This is the one module that turns a line into a knowledge answer. It reads the shared
reading in memory["understood"] rather than its own keywords, asks the maths domain for a
computed answer when the line is a calculation, then asks bot.knowledge.lookup for the
entry the line is really about. It stays out of the way (returns None) when nothing fits
well: a wrong answer is worse than letting another module, or an honest "I don't know",
take the turn.

The implementation lives in the `answers_part_NN` parts (in bot/module_parts); this module keeps the header
imports and re-exports every name the parts bind, so `answers.<name>` is what it was.
"""
import copy
import difflib
import re
import string

from .. import memory as mem
from ..compose import NEGATORS, goodnews, lead, pick, with_name
from ..compose import fit as shapes
from ..compose.repair import amends_to
from ..compose import trouble as trouble_reading
from ..knowledge import (by_topic, cooking, dishes, entertainment, entries as all_entries,
                         freshness, home, meat_in_a_card, pets, shopping, topics, work)
from ..knowledge.lookup import (EXPLAIN_FILLER, EXPLAIN_LEADS, about_the_chat,
                                about_the_topic, find, leans_on_a_subject,
                                names_its_own_subject, names_nothing_of_its_own)
from ..knowledge.lookup import entry as lookup_entry
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import (ack, deadline, healing, named, narrow as length, onset, prefer, repeat,
                      taste, when)
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import hope as a_wish, matters
from ..memory import topics as memory_topics  # not `topics`: this module has a `topics()` of its own
from ..knowledge.maths import solve
from ..understanding.kinds import ANSWERING_A_QUOTED_ASK, SUMMONS_WHO
from ..memory import a_year_of_birth
from ..memory import baking, doing_it, trips
from ..memory import repeat
from ..memory import outfit
from ..memory import (followup_reading, keywords, recall, remember_answer, resize,
                     same_as_before, the_ask_about_the_thing_it_points_at)
from ..memory import stuck as stuck_line
from ..memory import again as same_again  # the short of an answer already on the screen
from ..memory.again import NOTHING_MORE  # said of an answer with nothing further in it
from ..memory.again import AGAIN_HELP, DETAIL_AGAIN, SAME_ADVICE  # the lead-ins on a repeat
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory import repeat
from ..memory import topics as said_topic
from ..memory.topics import AMOUNT, ASK_ONLY, already_said, pairing, stem
from ..understanding import kinds
from ..memory.ack import VAGUE
from ..memory.topics import current as the_topic, is_follow_up
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import repeat, tried, more, returned
from ..memory import returns as went_back
from ..memory import limit
from ..memory import whereabout
from ..memory import price as a_price
from ..memory import (a_detail_of_the_thing_we_hold, answers_about_another_creature,
                      followup_reading, keywords, remember_answer, resize, same_as_before, swap,
                      the_animal_the_subject_is, the_thing_a_detail_belongs_to)
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory import repeat
from ..memory.narrow import (CAUSE, RATE, SIGNALS, asks_a_part, flat, kind_of as asked_kind,
                             narrow, the_outcome_asked, the_part_asked, words_of)
from ..understanding import understand

from ..module_parts.answers_part_01 import (  # noqa: F401
    PRIORITY, GENERIC_KEEPING, ANSWERS, REFERRING, ABOUT_YOU, _the_new_part, _BARE_VERDICT,
    _without_the_verdict, _CARD_OPENINGS, _card_openings, _without_a_lead, _opening,
    _most_of_it_said, _said_before, AGAIN, WORD, NOT_A_DETAIL, BACK_POINTS, ASK_VERB,
    DETERMINER_BEFORE_DETAIL, DETERMINERS, STOP_BEFORE_A_PART, SENTENCE, PRAISE_WORD, NOTHING_WORD,
    SUBJECT_WORD, FILLER_WORD, A_QUALITY_WORD, A_PLACE_IN_IT, A_JOINING_WORD, A_PLEA_FOR_TIPS,
    NOT_IN_A_NAME, _in_short, _same_as_the_last_answer, PICKED, _the_same_answer_in_other_words,
    _flat, A_SENTENCE_BREAK, A_CLAUSE_FINE, A_CLAUSE_BREAK, A_OPENS_A_CLAUSE, A_SAYS_NOTHING,
    A_SAYS_SOMETHING, _says_something, _the_part_in_the_answer, _names_it, SAID_ABOVE,
    NOTHING_SEPARATE, ASKS_ABOUT_HOW_IT_TURNED_OUT, _a_part_named_in_the_line,
    _short_form_of_the_last, _answer_said, BARE, _carries, _the_sentence_asked, NO_FIGURE, STEP_END,
    SPOKEN, TIMEISH, NO_STEP, _JOINED_ON, _first_step, _asks_of_another_subject, _ask_verb,
    _the_outcome_owed, _said_before_now, A_CORRECTION_WORD, _a_fact_about_the_person,
    _a_restatement_of_the_answer, _all_of_it_in_the_answer, CLAUSE_OPENER, CLAUSE_SUBJECT,
    NUMBER_OR_OWNER, _the_clause_s_verb, MODIFIER_WORDS, _named_whole, FIRST_PERSON,
    _their_own_state, _named_in, similar, _entry_words, _what_they_typed, A_SMALL_OPENER,
    _small_letter, _with_detail, _a_yes_no_ask,
)
from ..module_parts.answers_part_02 import (  # noqa: F401
    MORE_ASK, _asks_for_more, _the_answer_on_screen, _already_said, _the_same_sentences,
    WHO_IS_THE_BOT, _asks_who_the_bot_is, LENGTH_WORDS, _A_LENGTH, _A_DURATION, _DEFINES_THE_UNIT,
    _answers_a_length, _the_article, PROPERTY, _about_subject, SOMETHING_FOR, SOMETHING_FOR_PEOPLE,
    SOMETHING_FOR_FILLER, SOMETHING_FOR_TAIL, _OCCASION_WORDS, SOMETHING_FOR_STATE,
    SOMETHING_FOR_GIVEN_TO, _keyed_on_the_person, _something_for, PLAN_RECALL, _keeps_a_plan,
    RECALL, WHEN_AM_I, ASKS_MEMORY, _with_subject_tail, _subject_tails, CHOOSING, CHOOSING_PRONOUN,
    PREPOSITION_OF, _prep, _verbs, _verb, HOLDING_A_NUMBER, WHEN_WORDS, _bare_subject, MODAL,
    MODALS, MONTH, TIME_WORD, _the_month, TRIP_TOPICS, _a_trip, FINITE, _a_clause, _only_a_size_of,
    QUALIFIER_OPEN, QUALIFIER_MAX_WORDS, _choice_words, _qualifier_rewrites, REFUSE_OPEN,
    REFUSE_CHOICE, REFUSE_WISH, REFUSAL_ACK, WEAK_ACKS, CHOICE_NOUNS, SAID_POLITELY,
    _a_lack_not_a_refusal, _refused, _ASKS_AFTER_A_TASTE, _says_it_leaves_it_out, LACK_OPEN,
    _about_a_lack, _key_words, OWN_THING_AT, OWN_THING_SCAN, POSSESSIVE, PERSON_WORDS,
    _names_a_thing, _own_thing, _thing_named_in, _new_thing, _the_run_said, _head_thing, DESCRIBING,
    _the_same_kind_of_thing, DETAIL_OF, ASK_OF, OBJECT_PRONOUN, DO_VERBS, REPORT_WORDS, ASK_WORDS,
    SAID_OF_THE_THING, _off_the_topic,
)
from ..module_parts.answers_part_03 import (  # noqa: F401
    _hands_back_the_refusal, _from_another_domain, _names_a_topic_word, BARE_GENERIC, ASKING,
    SPEECH, TIME_WORDS, _topic_words, _lent_words, _same_word, _writes_its_own_reply, ASKING_VERBS,
    _leans_on, _is_about, PLACE_WORDS, SUM_TABLE, FEELINGS, PROPERTY_WORDS, _only_a_property,
    PROPERTY_WORD_THAT_NAMES_A_THING, _a_property_word_names_a_thing, MONEY_ASK, _a_money_question,
    _remember_answer, _last_answer, _asks_part, YES_NO_ABOUT_A_THING, ASKING_FRESH, OPTION_TIMING,
    DIGIT_OR_SPAN, DEPENDENT_SENTENCE, ABOUT_THE_ANSWER, WHO_TO_CALL, A_TRADE, CONDITIONS_THE_LINE,
    OPENING_CONNECTIVE, SAYS_TO_GET_SOMEBODY, SOMEONE_TO_GET, STOCK_ACKNOWLEDGEMENT, ACK_MODULES,
    MOST_ACKS, MOST_WORDS_OF_AN_ACK, _a_stock_acknowledgement, CLAUSE_BREAK, LONG_SENTENCE_WORDS,
    _the_clause_that_says_who, WHO_ASK_WORDS, CHOICE_ASK, CHOICE_CONTEXT, A_SPEC, CHOICE_TAIL,
    CHOICE_CUT, CHOICE_SHORTEST, _the_clause_that_picks, CHOICE_FIGURE, CHOICE_LIST_HEAD,
    CHOICE_ITEM, CHOICE_LEAD_VERB, CHOICE_CONDITION, CHOICE_COST, CHOICE_PRICE_OPENS,
    CHOICE_PRICE_ONLY, _a_list_of_things, _the_thing_that_picks, CHOICE_NOT_A_THING,
    _a_price_and_nothing_else, _the_composer_has_options, _AN_ALTERNATIVE, _NOT_AN_OPTION,
    _the_option_that_decides, _the_answer_to_a_choice_behind, _the_one_to_pick, _DISH_TIME,
    _WORD_NUMBER, _A_WHOLE_TIME, _A_BARE_TIME, _A_LABELLED_TIME, _RATE, _TIME_TAIL, _HOW_LONG_ONLY,
    _one_total, _the_dish_time, CORRECTION_FRAME, A_BARE_FIGURE, A_UNIT, UNIT_WORDS,
    _the_unit_last_said, _the_figure_they_meant,
)
from ..module_parts.answers_part_04 import (  # noqa: F401
    _the_sentence_about, _the_person_to_call, SIZE_REPLACED, _the_amount_they_named_again,
    MACHINE_ASKING, _the_machine_follow_up, WHEN_OF_THE_DAY, PROPORTION, MEASURE, _AMOUNT_BEFORE,
    _PROPORTION_PHRASE, _amount_for_the_name, CLAUSE_SEAM, KIND_SAID, JOINING_WORD,
    _sentence_naming_the_part, COUNTS_THE_CAUSES, NAMES_NO_CAUSE, _names_no_cause, _cause_part,
    _reason_again, ASKS_A_MEASURE, A_MEASURE, A_LEAD_TIME, ASKS_A_SPAN, WHEN_IS_A_CONDITION,
    A_WARNING, _asked_figure, _the_figure, _sentence_with, _part_not_repeated, GENERIC_ASK,
    WHERE_WORDS, NOT_NEW, _names_a_property, BARE_ASK, _with_bare_subject, _the_things_to_try,
    _with_the_thing, _care_holds, _named_by, _the_answer_was_about_the_subject,
    ADDING_TO_THE_SUBJECT, A_MEASURE_OF_THE_SUBJECT, GENERIC, _HOURS_AND_MINUTES, _minutes_in,
    _a_figure_apart, _only_a_figure, FIGURE, _figures, _NAME_WORDS, _NAME_DOMAINS, FEW_ENTRIES,
    WHEN_NOT_A_THING, _name_words, _filler, _left_out, SAY_IT, _ASKING_ONLY,
    OPENS_WITH_AN_AUXILIARY, NAMING, HANDOVER_FILLER, CHOICE_KINDS, THING_AFTER, AFTER_A_PLACE,
    NO_THING_NAMED, _AUXILIARY, ASKS_A_QUANTITY, DESCRIBES_ONE, KEEPS,
)
from ..module_parts.answers_part_05 import (  # noqa: F401
    _figure_missing, _figures_changed, _same_answer, _asked_again, _times_the_answer_was_said,
    _nothing_more_said_again, _reaches_another_subject, _keyed_on_the_line, _shares_a_word,
    FIGURE_ASKS, _answers_the_figure, _asks_how_to_say_it, _in_the_subjects_field, _own_thing_words,
    _agrees_with_its_own_field, _the_field_on_the_screen, _last_turn_answered_from_the_field,
    _says_a_subject_phrase, _names_the_entry, DEFINITION_WORD_AT, _a_definition_of_the_entry,
    _says_the_ask_whole, _a_why_line_that_names, _a_choice_with_one_thing_left_out,
    _ADJECTIVE_ENDINGS, _describes_the_thing, _said_in_the_talk, _already_in_the_talk,
    _names_its_own_thing, _the_topic_rules_it_out, _from_rewrite, _NOT_THE_FRIDGE, STORING,
    _asks_storing, _keeping_thing, _the_plan_keeps, _in_this_conversation, _in_bare_context,
    _reply_of, A_FIGURE, NUMBER_IN_TEXT, _figures_of, _new_figure, _adds_a_figure, A_PUT_RIGHT,
    _a_figure_put_right, _without_the_figures, _the_entry_asked_again,
    _the_part_a_longer_variant_adds, _payload, _the_sentence_owed, STAND_IN_WORDS, STAND_IN_PHRASES,
    STAND_IN_TARGET, _wants_a_stand_in, _a_swap_row, PRICE_LIMIT, PRICE_NOT_OVER, PRICE_BARE,
    PRICE_OVER, PRICE_WORDS, CHEAPER, LIMIT_SHAPE, LIMIT_ONLY, INTEREST_ALIASES, _price_limit,
    GIFT_WORD, _only_a_limit, _a_gift_entry, _a_gift_just_answered, _asks_what_to_give,
    _the_interests,
)
from ..module_parts.answers_part_06 import (  # noqa: F401
    _the_sentence_naming, _repeat_short, _the_detail_named, _the_part_named, _only_a_quality_name,
    _covered, _a_question_about_another_thing, _the_detail_said_again, _detail_lead_in,
    _the_part_said_again, _part_asked, _the_entry_reply, _the_present_with_a_price, _HOW_TO_SHAPES,
    HOW_TO, MONEY_SAID, PRICE_FILLER, PRICE_VERBS, _asks_a_price, _names_what_it_wants_priced,
    SAME_WHERE, LEAD_PREPOSITION, MOST_SAME, DETERMINER, NOT_A_THING, ONLY_THE_ASK, CLAUSE_START,
    SAME_PLAIN, _same_where_they_asked, _mid_sentence, ROOMS, NAMED_PLACES, _holds_where_they_asked,
    _the_method_in, _room_they_asked_about, _a_place_of_the_same_kind, _a_place_they_asked,
    _key_terms, _written_for, _more_than_the_thing, _about_the_rest_of_the_question,
    KEEPING_FROM_THE_ANSWER, _keeping_in_the_answer_before, KEEPING_CLAUSE, KEEPS_A_FIGURE, DEGREES,
    COOKED_THING, _cooked_thing, COOK_VERB, KEEPS_ANSWER, KEEPS_ASK,
)
from ..module_parts.answers_part_07 import (  # noqa: F401
    _choosing, _about_the_talk, _names_the_thing_apart_from_the_talk, _the_plan_for,
    PRONOUN_OBJECTS, REHEAT_ASK, REHEAT_REPLY, _names_another_food, KEEPING_WORD, _the_food_named,
    _the_plan_answers_this, _the_plan_said_again, _filling_in_an_emergency, _usable, _next_usable,
    _without_names, REWORD_ASKS, CHECK_ASKS, TONE_WORDS, TONING_WORDS, JOINING_WORDS,
    TONE_DESCRIPTORS, _only_the_tone, DEMANDS, _reword_ask, _tone_of, _softened, CONTINUED,
    _last_rewrite, HARD_TO_SAY, _hard_to_say, _rewritten, THEIR_EAT, COOK_WORD, SAID_WORD, EAT_VERB,
    DIET_WORDS, NOT_THE_THING, _asks_about_a_food, _someones_else_diet, _a_guest_restriction,
    MEAT_FREE, _names_someone_else, WRITE_OBJECT, _a_writing_job, A_TASTE_OF_THEIRS,
    _asks_about_their_taste, _about_them_alone, COMPLAINT, HEALTH_DOMAINS, _HEALTH, _health_entries,
    _names_a_typed_word, DETAIL_LINE, CIRCUMSTANCE, _circumstances, DETAIL_FRAMES, _detail_frame,
    _a_figure_the_answer_has, _a_detail_answered, _a_dish_was_offered, observe, LENGTH_SAID,
    _asks_only_the_length, TAKES_AS_IT_COMES,
)
from ..module_parts.answers_part_08 import (  # noqa: F401
    _a_limit_on_the_plan, THEIR_OWN_ASK, _a_bare_thanks, _a_judgement_of_the_figure_on_the_table,
    _AN_ANSWER, _the_bot_has_something_to_go_over, _the_line_asks_what_this_one_meant, _TURN_ONLY,
    _of_its_own, _keep_the_answer, _the_sentence_it_names, _fitted_to_what_they_eat,
    _DISH_NAME_IN_TEXT, _the_dish_by_name, _the_same_answer_again, _a_city_card_asks_which_first,
    _the_answer_in_front, TAKEN_BACK_OPENER, LEAD_ASK, LEAD_ROWS, LEAD_VERB, LEAD_ANY, _a_lead_time,
    _the_thing_has_got_better, A_CASE_ASK, A_CASE_STOP, _a_case_of_the_answer_in_hand,
    _A_CLAUSE_OF_THE_ANSWER, _A_SHORT_ANSWER, _the_line_already_has_its_answer, _A_HOW_LONG,
    _A_REPAIR, _names_a_repair, _the_entry_names, _the_plan_said, _PART_OF,
    _the_part_is_what_answers, _PART_OF_WORDS, _ATTACHED_TO_THE_LAST_TURN, _the_report_is_answered,
    A_DEGREE, _the_fact_is_what_is_answered, _the_entry_key_words, _the_practice_is_answered,
    _A_YES_NO_ASK, MOAN_STOP, MOAN_VERB_WORDS, _A_PERIOD, BARE_SAY_NO, _turns_on_this_line,
    _without_lead_in, A_CALL_ASK, _the_line_again, _FRAME, _MINE, _SLOT_KEYS, _STORED_VALUE,
    _HOW_TO, _COPULA, _stated_with_copula, _nothing_but_the_slot, _COOKING_DOMAIN,
    _the_food_they_do_not_eat, _store_keeps_the_line, _OVEN_CHECK_WORDS, _OVEN_WORDS,
    _PROPERTY_WORDS, _says_line, PICK_FRAME, _a_pick_is_asked, _the_line_as_said,
)
from ..module_parts.answers_part_09 import (  # noqa: F401
    _written_ask_with_an_answer, _with_subject, _amount_asked, _the_answer_from_thing, _in_context,
    _keeping_entry, _offer, _keeping_reader, _a_cooking_ask_after_a_keeping_answer,
    _a_complaint_answered, _the_figure_the_thing_we_are_on_holds, _a_length_ask_with_no_figure,
    OFFICE_WHO, OFFICE_ASKING, _only_the_office, _a_food_named_of_its_own,
    _keeping_about_the_food_there, _the_answer_on_the_table, _already_on_the_screen, _READ_AGAIN,
    _VERSE_FORM_WORD, _the_verse_said_again, _REPEAT_OPENS, _A_BARE_MEASURE, _the_sentence_around,
    _the_sentence_with_a_figure, SAID_OUT_LOUD, A_PERSON, SAYING_IT_TO, YOUR_PERSON, _TWO_SENTENCES,
    _puts_it_to_someone, _the_ask_is_for_words, _respond,
)
from ..module_parts.answers_part_10 import (  # noqa: F401
    respond, _the_question_with_the_place_on_it, _answer, _a_measure_about_the_subject,
    _the_part_of_the_thing_they_named, _ask_a_line_of_its_own, _the_ask_behind_a_moan,
    _ask_a_rewritten_line, _never_twice, paragraph,
)
from ..module_parts.answers_part_11 import (  # noqa: F401
    claims_instead, CLAIMS_INSTEAD,
)
