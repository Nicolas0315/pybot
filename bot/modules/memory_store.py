"""The memory store at work: remember what the user says, and answer questions about it.

PRIORITY 7000 (README routing bands: memory recall that must lead). It observes every line and
keeps the shared keys in bot/memory/; it only proposes a reply when the user asks about the
conversation itself ("what did I say my job was?", "what were we talking about?"), so it passes
on every ordinary question.

One exception, in the same spirit: when the person hands a choice back ("you pick", "your
call"), the answer is one of the options the bot itself offered a turn ago, so the store reads
the bot's own last reply for them (bot/memory/choice.py).

The implementation lives in the `memory_store_part_NN` parts (in bot/module_parts); this module keeps the header
imports and re-exports every name the parts bind, so `memory_store.<name>` is what it was.
"""
import copy
import random
import re

from ..compose import pick
from ..memory import (content, current, forget, forms, is_follow_up, keywords, last_bot,
                      last_module, last_user, log, name, note, others, plan_line, plan_sentence,
                      recent, remember, remember_answer, remember_other, resumed, return_target,
                      stem, thread, user, you)
from ..memory import ack
from ..memory import change as a_change
from ..memory import cause as a_reason
from ..memory import another as second_half
from ..memory import choice as choose
from ..memory import condition
from ..memory import decided
from ..memory import company
from ..memory import spent
from ..memory import surname as family_name
from ..memory.filler import without_the_end_shrug
from ..memory import guest
from ..memory import plans
from ..memory.taste import read_all as read_tastes
from ..memory import facts as extract
from ..knowledge import cooking
from ..knowledge import units
from ..knowledge.maths import solve
from ..memory import counts as how_many
from ..memory import rates as rates_reader
from ..memory.times import keep as _keep_the_times
from ..memory.times import answer as _the_time_they_said
from ..memory.times import is_a_time_ask as _a_plain_time_ask
from ..memory import history
from ..memory import narrow
from ..memory import hours as hours_after
from ..memory import named as named_thing
from ..memory import recall
from ..memory import reminded
from ..memory import carry as about_the_choice
from ..memory import resize
from ..memory import reject as turned_down
from ..memory import repair as a_repair
from ..memory import told as told_about
from ..memory import whathurts as a_hurting_part
from ..memory.when import until_answer, when_answer
from ..memory import topics as _topics
from ..memory.repeat import HEDGE as _HEDGE
from ..memory import repeat as repeat_the_line
from ..memory.topics import subject as topic_subject
from ..memory.thread import about as _about_the_chat
from ..understanding import breeds, understand


from ..memory.store_lines import (  # the pools, moved out whole: see bot/memory/store_lines.py
    PRIORITY,
    ANSWERS,
    RECALL_HINTS,
    SELF,
    NOT_THE_PLAN,
    NOT_ON_A_MEDIUM,
    REPEAT_ADVERB,
    LIMITS,
    DENIAL_SAY,
    CORRECTED_SAY,
    RETRACT_SAY,
    NOT_RETRACTED,
    _FACT_SLOT,
    PET_AGE_FIX_WORDS,
    OTHER_SAID,
    OTHER_KIND_SAY,
    AGE_FIX_WORDS,
    NAME_FIX_WORDS,
    NAME_GIVEN_WORDS,
    UNIT_FAMILY,
    FACT_FAMILY,
    NOT_A_UNIT,
    AMOUNT_WORD,
    SPELLING_APART,
    CORRECTION_SAY_DROP,
    DROP_LISTS,
    CORRECTION_SAY,
    CORRECTION_SAY_PAIR,
    PET_RENAMED_SAY,
    BARE_ECHO_ONLY,
    CORRECTION_BACK,
    AT_TIME_VALUE,
    KIN_ASK,
    IN_LAW_AFTER_TEXT,
    PRONOUN_FITS,
    CHILD_RELATIONS,
    _ABOUT_WHO,
    CHILD,
    CHILD_OF,
    FAMILY_GROUP,
    FOOD_PHRASES,
    ADVICE_MODULES,
    SLOT_KEY,
    BARE_SLOTS,
    WHERE_ASK,
    KIN,
    BAD_NEWS,
    _UNIT_SAID,
    _AMOUNTS,
    _AMOUNT_WORDS,
    _COUNT_WORD,
    _CONVERT,
    _WEEKLY,
    FIGURE_UNITS,
    FIGURE_TIME,
    FIGURE_NUMBER,
    FIGURE_QUALIFIER,
    LOOK_BACK_FIGURE,
    FIGURE_ANSWER_LEN,
    COUNT_WORD,
    PLACE_NOT,
    TURNED,
    PART_HELD,
    PART_KEYS,
    KEPT_THINGS,
    NAMED_BY,
    RESTATED_KEYS,
    SWAPPABLE,
    _TENS_WORDS,
    CORRECTED_AGAIN,
    CORRECTED_AGAIN_WHO,
    CORRECTED_WHICH_PERSON,
    CAT_NAMES,
    DOG_NAMES,
    SMALL_NAMES,
    NAME_ADVICE,
    RESUME,
    NO_PLANS_REPLY,
    WEEK,
    TAIL_WINDOW,
    PLURAL_PEOPLE,
    DIET_RULES_OUT,
    DENIAL_WORDS,
    DENIAL_STEMS,
    CHILD_RELATIONS,
    GROUP_OF,
    RELATION_ALIKE,
    MONTH_ORDER,
    HAVE_ANY_WORDS,
    HER_WORD,
    DIET_FOOD,
    PERSON_GROUP,
    PLURAL_PEOPLE,
    OWNED_BY_THE_VERB,
    PREGNANT_OWN_SAY,
    PREGNANT_SAY,
    PREGNANT_WEEKS_SAY,
    LIMIT_SAY,
    FEEDING_SAY,
    STATE_WAS_SAY,
    PET_WORDS,
    PRONOUN_PEOPLE,
    SAME_FACT_THEIR_OWN,
    CONDITION_RULES_OUT,
    CONDITION_KEEPS_DOWN,
    CAR_CAPS,
    NUMBER_WORDS,
    _SUBJECT_KEYS,
    PLURAL_PETS,
    COUNT_WORDS,
    A_SHORT_ANSWER,
    KEY_SLOT,
    CONCEPTS,
    POSSESSIVE,
    QUOTE_LEADS,
    ASKED_LEADS,
    NOTHING_STARTED,
    POINTS_BACK_NOTHING,
    POINTING_WORD_NOTHING,
    WHAT_I_SAID_NOTHING,
    RESTRICT_OPENS,
    CALL_LEADS,
    LENGTH,
    WORD_NUMBERS,
    UNIT_SECONDS,
    BUDGET_FITS,
    BUDGET_MORE,
    BUDGET_TIGHT,
    ANY_FIGURE,
    HELD_THREAD,
    GRIEF_WORDS,
    CLOSE_PLAIN,
    CLOSE_HEAVY,
    CHANGE_PLAIN,
    CHANGE_HEAVY,
    CHECK_NOTHING_SAID,
    CHECK_A_FEELING,
    CHECK_A_QUESTION,
    CHECK_PLAIN,
    CLOCK_SAID,
    ROUTINE_SUBJECT,
    ROUTINE_SAY_BACK,
)
from ..memory.enough import enough_reply

from ..module_parts.memory_store_part_01 import (  # noqa: F401
    _enough_reply, _PET_WORD, _animal_family, _canon_relation, _folded, _named_person,
    _person_from_pronoun, _pronoun_fits, ASK_WITHOUT_MY, DAY_IT, DAY_THING, HOW_MANY_OF_MINE,
    PLAN_MINE, TIME_ASKS, TIME_IT, TIME_THING, TOPIC_ASK, WHERE_PLAN, REMIND_QUESTION, NOT_A_FACT,
    _their_own_line_ask, NOT_FROM_THE_REPAIR, _with_repaired, NOT_A_NAME_BEFORE, THE_PLACE_IS_NAMED,
    _the_places_are_written_as_names, note_the_hours, _a_detail_does_not_replace_the_job,
    ASK_OPENERS, _without_the_shrug_at_the_end, after, AGES_IN_WORDS, _the_ages_of_the_children,
    _the_count_was_the_line_before, _the_pets_on_record, _note_a_pet_that_is_new,
    _a_trip_booked_named, _this_line_put_something_right, _on_record_before, NAMED_FACT_ASK,
    ASK_ABOUT_THEM, PERSON_ADVICE_ASK, CORRECTS_A_NAME, CORRECTS_A_NAME_POSSESSIVE, AGE_IN_WORDS,
    PET_NAME_AGE, PET_LEAD_IN, PET_AGE_ANSWER, AMOUNT, ANY_NUMBER, ASK_START, AT_TIME,
    A_DAY_BEFORE_A_MONTH, A_DAY_SAID_LONG, A_UNIT_SAID, BARE_HOUR, BARE_NEW_COUNT, CORRECTABLE,
    COUNT_SAID, CURRENCY, DATE_DAY, DATE_PHRASE, DAY_WORD, MADE_OF_A_VALUE, MONTHS, MONTH_ALT,
    MONTH_WORD, MONTH_WORDS, NAMING_VERB, NOT_A_FACT_OF_THEIRS, NO_SUBJECT_OF_ITS_OWN,
    NUMBER_DIGITS, NUMBER_VALUE, NUMBER_WORD, OTHER_BARE_NUMBER, RELATIVE_MONTH,
    STILL_THE_SAME_PERSON, _a_bare_hour, _a_birthday_for_somebody, _a_birthday_on_the_last_line,
    _a_count, _a_day_in_the_kind, _a_day_written_the_way_the_store_writes_it, _a_name_for_a_person,
    _a_name_the_store_keeps, _a_new_name_was_said, _a_relative_line, _a_relative_month,
    _a_spelling_of, _a_word_of_a_name, _an_amount_on_the_measure, _apply_correction, _asks,
    _birthday_words, _carries, _clock_key, _correct_a_persons_name, _correct_birthday,
    _correct_clock, _correct_count, _correct_date, _correct_fact, _correct_number, _correct_other,
    _correct_plan, _correct_the_count_on_the_table, _correct_their_birthday, _correct_when,
    _count_said, _date_in_plan, _date_said, _date_word, _date_word_case, _denies_and_names,
    _drop_wrong, _fact_naming, _keep_unit, _kind_of_value, _letters_apart, _make_corrects, _many,
    _measured_the_same, _names_a_half_of_the_day, _number_belongs_to_that_age, _number_in,
    _plan_saying, _plan_the_line_named, _plan_told_line, _stated_families, _stated_last,
    _stated_plan, _swap_in, _the_line_is_about_that_birthday, _the_person_the_plan_is_about,
    _the_plan_before, _the_plan_on_the_table, _the_topic_with_the_new_clock, _the_unit,
    _what_took_its_place, _without_the_naming_verb, A_HAVE_QUESTION, _a_bare_limit_ask,
    ACTIVITY_ASK, ANSWER_MODULES, BARE_WHAT_I_DO, CANT_HAVE, CAN_HAVE, CAN_THEY_HAVE,
    CAN_THEY_HAVE_A_FOOD, CHECK_FOLLOWED, EAT_ASK, FIRST_ASK, NO_RECORD, OTHER_FACT,
    POINTS_BACK_AT_IT, THEM, WHOLE_ASK, YES_NO_ASK, _RELATION, _a_feeling_about_what_they_said,
    _a_limit_kept_for_them, _a_number, _a_state_that_was, _a_thing, _a_whole_answer_to_hand_back,
    _about_the_bot_here, _about_this_chat, _activity_line, _after_the_yes_no_frame,
    _asks_about_someone, _bare, _behind_a_remembering_frame, _can_close, _diet_reply, _halves,
    _how_far_along, _kind, _longest, _name_they_answered, _names_its_thing, _names_minutes,
    _names_the_thing, _other_person_reply, _plain_line, _plans_reply, _reads_as_the_invitation,
    _repeat_ask, _says_something, _says_the_verb, _sentences, _someone_else_named, _statement,
    _the_animal_of_the_pick, _the_back_this_turn, _the_budget_on_the_answer,
    _the_call_from_the_advice, _the_job_was_just_said, _the_limit_the_last_line_gave,
    _the_limit_they_share, _the_person_still_in_hand, _the_prep_day, STATES_A_LIMIT,
    _the_same_fact_about_someone, _the_store_reply, _told_phrase, _vary, ack, company, content,
    current, decided, enough_reply, extract, family_name, forget, guest, how_many, last_user, name,
    note, others, pick, plans, rates_reader, re, recall, recent, remember, remember_other, reminded,
    stem, thread, told_about, units, until_answer, user, when_answer, REPEAT_WORDS, asks_again,
    AGE_FIX, CORRECTING, WEEKS_FIX, PREGNANCY_SAID_AGAIN, NAME_FIX, NAME_NOT_A_NAME,
    A_NAME_AFTER_A_PRONOUN, A_NAME_WITH_ITS_VERB, ANOTHER_ANIMAL, CORRECTS_A_MAKE, NAME_GIVEN,
    NOT_A_NAME_AFTER_CALLED, NUMBER, PAIR_WITHOUT_A_MARKER, NOT_A_NEW_VALUE, TOO_AS_WELL,
    OTHER_NOUNS, FIGURE_ASK, FIGURE_FILLER, FIGURE_AFTER, ACTION_DURATION, ACTION_AMOUNT,
    A_MONEY_FIGURE, A_PERCENT_FIGURE, LISTED_FIGURE, A_RATE_ASK, A_RATE_STATED, SAID_AGAIN,
    SORRY_OPENS_A_CORRECTION, RECALL_WRAPPER, RECALL_SLOTS, RECALL_POSSESSIVE,
    RECALL_SLOTS_BY_POSSESSIVE, SLOT_WORDS, WORK_ON_IT, FACT_WORDS, _concept, _words, _word,
    _country,
)
from ..module_parts.memory_store_part_02 import (  # noqa: F401
    _forget_denied, _the_back_on_the_plate, _the_one_they_are_back_on, _off_their_list,
    _the_diet_they_are_back_on, _the_last_line, _losses_taking, _last_stated, _retract_last,
    _reads_the_store, _the_plan_they_took_back, _the_clock_in_their_line,
    _an_ask_about_someone_else, _the_take_back_about_someone, _the_part_that_hurts_asked,
    _name_the_last_pet, _the_animals_named, _the_name_it_had, _names_a_pet_here, _the_figure_said,
    _without_a_lead_in, _put_a_pets_age, _age_the_named_pet, _fix_a_pets_age,
    _age_said_of_the_only_animal, _age_they_answered, _their_name_answered, _fix_a_persons_age,
    _fix_the_weeks_of_a_pregnancy, _fix_a_pets_name, _pets_of, _a_pet_new_this_line,
    _another_animal_is_named, _two_of_the_animal_are_kept, _the_turn_before_said,
)
from ..module_parts.memory_store_part_03 import (  # noqa: F401
    _observe, _their_fact_ask, _fix_the_make_of_a_thing, _fix_a_persons_name,
    _the_name_they_gave_to_the_person_they_mean, _a_person, _a_correction_without_a_marker,
    _a_person_called, _stated_value, _a_second_persons_limit, _drop_value, _plan_names,
    _drop_from_plan, _names_this, _budget_sign, _a_feeling_about_their_own_news, takes_as_it_comes,
    _the_ask_about_how_it_went, _a_count_from_the_date, FIGURE_MONEY, _the_unit_asked, _the_clause,
    _the_money_figures, _the_figures_in, _the_figure_the_answer_names, _a_figure_of_those_units,
    _the_time_they_put_right, _asks_to_hear_it_again, _asks_about_someone_else,
    _note_a_corrected_fact, _note_a_fact_moved, SHE_OR_HE, _a_word_for_the_slot,
    _the_ask_behind_the_recall, _about_the_verb, _remember_dislikes,
)
from ..module_parts.memory_store_part_04 import (  # noqa: F401
    _a_kept_fact_read, observe, _the_store_readings, respond, TAKES_AS_IT_COMES, _a_fact_word,
    _a_callback_that_names_its_thing, _points_back_at_nothing, _a_recall_about_nothing,
    A_RECALL_IN_ANOTHER_SHAPE, RECALL_NAMES_NOTHING, _names_nothing_in_a_recall,
    _a_recall_frame_about_nothing, _an_ask_about_nothing, _the_last_ask_about_the_bot, _fits,
    _asks_whether_we_followed, _the_group_size_ask,
)
