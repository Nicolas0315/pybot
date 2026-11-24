"""Facts about the user, pulled out of what they say. The conversation lane owns this file.

`extract(text)` returns only the facts a line clearly states, e.g.
{"name": "Jess", "job": "nurse", "city": "Leeds", "allergies": ["nuts"]}.
Callers merge the result into memory["user"] with bot.memory.remember(), which keeps an
ordered log so the bot can answer "what did I say my name was?" and "which city did I say
first?". Nothing here replies; it is data extraction only.

The implementation lives in the `facts_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `facts.<name>` is what it was.
"""
import re

from ..understanding import breeds, lexicon, normalize
from ..understanding.kinds import EMOTION_WORDS, VERB_FORMS
from ..understanding.topics import STRONG, PHRASES, WORD_NUMBERS, CONDITIONS

from .named import the_name_in
from . import taste
from .filler import TAIL_OFF

from .facts_part_01 import (  # noqa: F401
    NOT_NAMES, NAME_TAIL_MIN, NAMES_THAT_LOOK_LIKE_STATES, NOT_NAMES_EXTRA, NOT_A_NAME_FEELING,
    NOT_A_NAME_LAUGH, CONDITIONS_OF_THE_MIND, _health_words, NOT_A_NAME_ILLNESS, NOT_A_NAME_TRAIT,
    NOT_A_NAME_DESCRIBING, NOT_A_NAME_CONDITION, NOT_A_NAME_STATE, NAME_FILLER, NAME_FILLER_PHRASES,
    NAME_FOLLOWERS, NAME_PLACE_WORDS, PLACE_JOIN, NAME_SAYS_ABOUT_ME, NAME_ASIDES,
    NAME_ANSWER_HEDGES, without_the_hedges, NAME_MIDDLE, ANNOUNCED_NAME_PATTERNS, GOES_BY_NAME,
    CLAUSE_SPLIT, GUESSED_NAME_PATTERNS, GO_BY_WAYS, MONTHS, DAYS, COUNTRIES, NOT_POSITIONS,
    NOT_PLACES, PLACE_AFTER, PLACE_LOWER, NOT_A_FACT, ASK_WORDS, AFTER_THEN, HOME_IN, DWELLING,
    HOME_DWELL, HOME_PLACE, HOME_STOP, FROM_PLACE, FROM_MORE, FROM_GROWN, GROWN_NOT_PLACE,
    GROWN_ARTICLE, GROWN_NEAR, PLACE_MIDDLE, PLACE_NAME_FIRST, PLACE_LOWER_NAMED, _an_everyday_word,
    COUNTRY_CAPS, COUNTRY_ARTICLE, PLACE_VERBS, HOME_LOOSE, SHORT_LIST, DENIAL_WORDS, DENIAL_OF,
    DIET_PLANS, DIET_PLAN_WORD, DIET_OFF, CLAUSE_EDGE, NOT_HAVE, NOT_HAVE_LONGER, HAVE_NONE,
    A_COMPOUND_AFTER, WITHOUT_ANIMAL, NOT_JUST, TAKEN_BACK_BEFORE, BARE_NO, NO_THEN_A_THING,
    GIVEN_AWAY, NO_PETS, EVERYTHING, DIED, ANIMAL_DEATH, LOSS_ALL, PET_PRONOUN, PLURAL_PRONOUN,
    HEDGE, ALLERGY, CONTRAST, CANNOT_EAT, X_ALLERGY, NOT_AN_ALLERGEN, VEGETARIAN, NO_MEAT, DRINK,
    NO_DRINK, GAVE_UP_DRINK, GAVE_UP_DRINK_THING, NOT_DRINKING, NO_DRINK_THING, MEAT, ANIMALS,
    FREE_FROM, DIET_FREE_WORDS, OTHER_DIET, THEIR_BACK, A_CORRECTION, A_NEGATOR_IN_BETWEEN,
    ALLERGEN_PLURALS, ONE_MORE_FOODS, ONE_MORE_HEAD, ONE_MORE_TAIL, NOT_THEIRS, A_WISH,
    NOT_THEIRS_AFTER, THEIRS_WORD, COMING_HOME, ON_ITS_WAY_BETWEEN, CONDITION, DIET_NAMES,
    DIET_WORDS, SOBER_WORDS, DIET_NAMED, DIET_UNDERWAY, DIET_BARE, DIET_DOING, DIET_WHAT,
    DIET_WHAT_TWO, DIET_QUIT, EATING_VERB, QUIT_AS_DOING, DIET_BACK, DIET_STOP_A_WAY_OF_EATING,
    NO_EAT_QUALIFIER, PETS, NOT_A_COUNT_GAP, AGE_GAP_WORD, PET_COUNT, PET_COUNT_WORDS, NAME_WORD,
    NOT_A_NAME, ANOTHER_ANIMAL, ALSO_HAVE, NOT_THEIR_DETERMINER, PET_TITLE, PET_VERB_NAME,
    PET_PRONOUN_NAME, NOT_THE_VERB_NAME, NOT_A_PRONOUN_NAME, PET_NAME, NAME_AFTER_TITLE, _name_at,
    PET_IS_NAME, PET_POSSESSIVE_NAME, PET_APPOSITIVE, PET_BEFORE_FACT, NOT_A_NAME_MIDDLE,
    PET_ANIMALS, ANIMAL_KINDS, another_animal, NOT_A_PET_NAME, PET_NAME_ONLY, PET_NAME_ONLY_LOWER,
    A_COMMENT_ON_THE_NAME, PET_NAME_ASKED, USER_NAME_ASKED, NOT_A_NAME_THING, JOB_WORDS,
    NUMBER_WORDS, NAME_ANSWER_ANNOUNCED, NAME_ANSWER_ANNOUNCED_LAST, NAMES_OFFERED, NAME_PICK_ASK,
    BUDGET, SPEND_BUDGET, _INTENT, _WHAT_THEY_MEAN_TO_DO, _A_CAP, _MONEY_AGAIN, INTENDED_SPEND,
    THE_THING_MAY_COST, ALL_I_CAN_DO, SPEND_FOR, MONEY_AMOUNT, ONLY_HAVE, SPEND_BUDGET_NOW,
    MONEY_FIGURE, STRETCH_BUDGET, INCOME_PERIOD, INCOME_QUALIFIER, INCOME_RATE, INCOME, INCOME_BARE,
    INCOME_A_YEAR, BARE_BUDGET_LEAD, BARE_BUDGET, CEILING_BUDGET, BUDGET_THOUGHT, BUDGET_ASKED,
    VAGUE_BUDGET, MONEY, AGE_UNIT, AGE, HEIGHT_FEET, HEIGHT_BARE, INCH_WORDS, HEIGHT_CM,
    _NUMBER_IN_WORDS, _A_UNIT_WORD, _A_TEEN_WORD, _A_TEN_WORD, AGE_IN_WORDS, BEFORE_A_FIGURE,
    AFTER_A_FIGURE, NOT_YEARS_AFTER,
)
from .facts_part_02 import (  # noqa: F401
    _fact_value, _coming_home, _only_wanted, _not_theirs, _a_wish_for, _the_food_named,
    _a_way_of_eating_said_with_a_verb, _with_title, _names_something_else, vague_budget,
    _the_numbers_in_words, _how_tall, BIRTHDAY, BIRTHDAY_PRONOUN, A_DATE_CLAUSE_ENDS,
    _the_date_clause, _a_birthday_date, WEIGH_UNITS, _weight_unit, WEIGH, WEIGH_IM, WEIGH_MY,
    COMPOUND_AFTER, COMPOUND_THAT_IS_THEIRS, MY_AGE, _STEP_OF, _GRAND_OF, _BUILT_KIN, RELATIONS,
    SPOKEN_RELATION, PEOPLE_WORD, NOT_A_UNIT, ROLE_PEOPLE, KIN, ALONE_PERSON, PERSON_MODIFIER,
    MODIFIER_BEFORE, IN_LAW, IN_LAW_WORD, an_in_law, IN_LAW_AFTER, KIN_WORDS, _RELATION_WORDS,
    _A_PERSON, _A_WORD_FOR_A_PERSON, TITLE, TITLE_WORDS, TITLE_GENDER, _NAME, RELATION_NAME,
    RELATION_HAVE_NAME, RELATION_POSSESSIVE_NAME, _NOT_A_PERSON_NAME, RELATION_NAMED_AGE,
    RELATION_POSSESSIVE_AGE, RELATION_AGE, THE_PLACE_AGE, BABY_AGE, MONTH_OLD_BABY,
    RELATION_BARE_NAME, RELATION_PAIR_NAMES, GROUP_NAMED_NAMES, GROUP_NAMED_AGES, RELATION_WHOS_AGE,
    CHAINED_RELATION_AGE, CHAINED_PERSON, a_chained_person, AGE_TO_COME_TAIL, HOW_THEY_FEEL,
    _AN_AGE_IN_WORDS, PRONOUN_AGE, a_stated_number, a_person_word, _the_person, _SHE_SAID, _HE_SAID,
    _kin_pronoun, SHE, HE, _sided, _UNPOINTED, A_LIMIT, COMMITS_TO, MONEY_LIMIT,
    _own_body_is_the_trouble, a_limit_on_the_plan, PLAN, PARTICLES, INFINITIVE_FRAME, PERSON_OPEN,
    PREPOSITIONS, POINTING, MONTH_NAMES, DAY_AND_MONTH, CORRECTION_WHY, TAKES_BACK_THE_VALUE,
    MOVED_VERB, MOVED_TO, CLOCK_SAID, A_DATE_VALUE, AFTER_THE_VALUE, _A_SAID_NAME, _the_same_name,
    CORRECTION_STALL, NOT_A_VALUE_START, CORRECTION_HEDGE,
)
from .facts_part_03 import (  # noqa: F401
    ARTICLES, _FAREWELL, _GOT_A, _GOT_TO, FUTURE, PAST, PAST_VERBS, PAST_ARRANGED, PAST_STATES,
    INTENTION_AFTER, PAST_DEED, a_deed, OWN, SECOND_PERSON, NEGATED, DETERMINERS, ASKED_BEFORE,
    ASKING, CORRECTION, CORRECTION_PAIR, CORRECTION_MAKE, CORRECTION_SAID, CORRECTION_MOVED,
    CLOCK_VALUE, CLOCK_IN_PLAN, a_clock_time, the_clock_in, a_moved_time, _a_day_taken_back,
    _a_moved_time, CORRECTION_NUMBER_PAIR, CHANGED_TO, CHANGED_BARE, CHANGED_NOW, CORRECTION_A_DATE,
    A_DAY_TAKEN_BACK, A_DAY_I_MEANT, A_TIME_INSTEAD, MOVED_BY_ITS_OWN_VERB, TRIP_DATE_MOVED,
    NOT_A_DAY, CORRECTION_NOT, RETRACT, CORRECTION_NOT_TO, CORRECTION_NOT_PAIR, DENIAL_OF_A_VALUE,
    A_NAME_IS_TAKEN_BACK, a_name_is_taken_back, NAME_TAKEN_BACK, the_name_they_take_back,
    CORRECTION_TAKEBACK, CORRECTION_LEAD, A_MARKER_ON_THE_END, CORRECTION_FRAME, CORRECTION_BARE,
    CORRECTION_HEDGED, CLOCK_PREFERENCE, CORRECTION_CLOCK, CLOCK_PREFERRED, AMOUNT_CORRECTION,
    AMOUNT_CORRECTION_BARE, AMOUNT_WISH, CORRECTION_MARK, CORRECT_FROM_MARK, CORRECTION_BARE_NO,
    CORRECTION_SHAPE, CLAUSE_OPENERS, COPULA_SPLIT, NOT_A_VALUE, POINTING_AT, _MONTH_ALT,
    DATE_VALUE, _DAY_NUMBER, CORRECTION_DATE, _GOING_VERB, _GOING_SAID, _GOING_DATE,
    CORRECTION_DATE_GOING, CORRECTION_GOING_MOVED, CORRECTION_TAIL_WORDS, CORRECTION_TAIL,
    _a_tail_hangs_off, CORRECTION_TRIP_FRAME, a_value, NO_THEN_A_THING_NAMED, JOB_AFTER, JOB_BECOME,
    JOB_WAS, WAS_NOT_A_JOB, JOB_WORK, JOB_FRAME, JOB_APPOSITIVE, POSSESSION,
    CORRECTION_OPENER_WORDS, JOB_GOT_AT, JOB_GOT_FRAME, JOB_GOT_NOT_A_PLACE, JOB_GOT_POSSESSIVE,
    JOB_GOT_AN_EMPLOYER, a_place_that_employs, JOB_AS_A, JOB_OWN_VOICE, JOB_MINE, JOB_WANTED,
    JUDGEMENT_NOUNS, JOB_STOP, SELF_JUDGEMENT, ROLE_YOU_CAN_FAIL,
)
from .facts_part_04 import (  # noqa: F401
    _the_drink_they_do_not_take, SELF_JUDGEMENT_ROLE_ONLY, SELF_AS_A_ROLE, NOT_A_JUDGEMENT_AFTER,
    SELF_JUDGEMENT_SAID, SELF_JUDGEMENT_ABOUT_A_NOUN, JUDGEMENT_TAIL, is_a_judgement, TAKE_BACK,
    TAKE_BACK_SPLIT, QUALIFYING, take_back_cut, qualified_by, _the_role, JOB_DANGLING, JOB_TAIL,
    JOB_TAIL_PLACE, CHANGED_WORK, WORK_NOW, WORK_DETAIL, WORK_DETAIL_FILLER, is_a_place_of_work,
    is_a_work_detail, work_weight, _finish, THE_MOMENT, without_the_moment, TONE_TAIL, INFINITIVE,
    NOT_AN_END, MAY_AS_A_MONTH, DAY_OF_A_MONTH, _can_end, no_tone, _date_change, ORDINAL_DAY,
    A_DATE_WORD, MOVED_PLACE_TO, MOVED_PLACE_PASSIVE, NOT_A_PLACE_NAME, a_date_put_right,
    the_date_put_right, a_trip_date_put_right, _a_date, _tidy, _tidy_a_titled_name,
    A_LEAD_PREPOSITION, A_LEAD_IDIOM, _the_value_alone, _tidy_apart, INTRO_WORDS, NAME_FRAMES,
    _lowercase_name_fits, _filler_or_intro, _squeezed, _SQUEEZED_INTROS, VERB_ISH, TAIL_DETERMINERS,
    _tail_has_a_verb, SAYS_SOMETHING_VERBS, SAYS_SOMETHING_ELSE, _followers_fit, _without_asides,
    _a_state_word, STATE_DEGREES, _a_degree_of_a_state, _a_letter_too_many, _sounds_like_a_state,
    _a_word_that_is_a_state, LOOKS_WORDS, _a_word_not_a_name, COMPARED, _the_state_compared,
    _with_its_y_back, _a_letter_off_each_run, _a_state_written_as_a_comparison_or_a_double,
    SAYS_A_NAME, _a_judgement_on_themselves, _first_tail, JUDGEMENT_AFTER, _is_a_judgement_phrase,
    _only_discourse_before, _the_correction_named_a_thing, ROLE_ENDING, TAKES_ONE_BACK, I_DRIVE,
    NOT_A_CAR, MEASURED, CAR_ASKED, CAR_NAMED, _CAR_NAMES, _the_car_name_in, CAR_IN_THE_PAST,
    _car_named_in_passing,
)
from .facts_part_05 import (  # noqa: F401
    grown_up_in_a_place, _grown_up_in_a_place, a_moved_place, place_value, _car, ADJECTIVE_NAMING,
    _reads_as_a_plural, NOT_A_PLACE_WORD, _place_name, _born_place, FROM_A_MOVE,
    A_MOVE_FROM_THEN_TO, _the_person_moved, _from_place, A_HOME_BEFORE, _places, _QUANTITY_WORDS,
    ALLERGY_STOP, OTHER_NOUNS, CLAUSE_BREAK, QUESTION_OPEN, CLAUSE_JOIN, stated_not_asked,
    PRONOUN_SUBJECT, SUBJECT, A_ME_WITH_SOMEONE, _the_person_is_in_it, BARE_RELATION,
    NOT_A_PERSON_WORD, BETWEEN_PERSON_AND_FACT, NOT_A_BARE_PERSON_AHEAD, A_PRONOUN_NOT_A_NAME,
    _a_person_word, FILLER_TAIL, FILLER_TAIL_PHRASES, _trim_filler, QUESTION_START, NOT_A_FOOD,
    A_GENERIC_FOOD, _trim_time_tail, NOT_A_FOOD_IN_IT, _a_modifier_before_a_generic_noun,
    _only_stop_words, _allergy_items, ONE_MORE_DETERMINERS, NOT_AN_ADDITION, one_more, SHARE_LEAD,
    I_SHARE_IT, I_SHARE_IT_SHORT, SOMEONE_SHARES_IT_VERB_FIRST, SOMEONE_SHARES_IT,
    SOMEONE_SHARES_IT_PRONOUN, LAST_PERSON, the_limit_they_share, denied_before, _clause, _around,
    _own_named, _own_in_denial, ONE_TAKEN, DIY_OF_ALL, ONE_OF_THEM, given_away_one, _pointed_at,
    not_had, _have_none, taken_back_before, their_back, ALL_OF_THEM, _one_of_several, _merge_pets,
    _the_one_they_have, _only_pet, _names_a_relative, _may_be_an_animal,
)
from .facts_part_06 import (  # noqa: F401
    AGE_MONTHS_TAIL, AGE_TAIL, _month_age_after, AGE_TO_COME, OTHER_CALLED, OTHER_NAME_IS,
    OTHER_NAMED_BARE, OTHER_BIRTHDAY, OTHER_NAMED_BEFORE_VERB, _the_word_then_a_verb,
    OTHER_NAMED_CAPITAL, OTHER_NAME_POSSESSIVE, OTHER_NAMED_MIDLINE, NOT_A_NAME_MIDLINE,
    NOT_A_NAME_THERE, NOT_NAME_ENDING, NAMES_THAT_END_LIKE_A_VERB, a_titled_name,
    _the_name_without_a_possessive, KID_COUNT, KID_COUNT_AND, KID_NUMBERS, KID_NUMBER_WORDS,
    FIGURE_WORDS, FIGURE_PAIR, FIGURE_WORD, figures_as_digits, KID_AGES, KID_AGES_AFTER_A_COMMA,
    ONES_BY_ONE, AGES_ONLY_WORD, the_ones_are_given_one_at_a_time, ages_said_one_by_one,
    KID_ELSEWHERE, KID_ASKING, KID_NONE, KID_NONE_NOT_AFTER_ALL, COUNT_OF_THEM,
    COUNT_OF_THEM_ELSEWHERE, CHILDREN_WORDS, count_of_the_people,
    _the_group_in_hand_is_the_children, KIDS, KID_GROUP, KID_ONE_BY_ONE, A_COUNTED_GROUP,
    KID_AGES_ARE, KID_GROUP_AGES_ARE, KID_COUNT_AGES, KID_ADULTS_AGES, KID_AGES_NOT, KID_NAME_AGES,
    KID_NAME_AGE, FIGURE_AFTER, NOT_A_NAME_HEDGE, _kids_named_with_ages, _the_same_person,
    _STATE_WHO, OTHER_STATE, PREGNANCY_STATES, OTHER_LIMIT, OWN_STATE, OWN_PREGNANCY_WEEKS_MAX,
    _own_states, _other_states, YEAR_OLD, OWN_AGE_BEFORE_IT, YEAR_OLD_ANIMAL, THING_AGED,
    A_PERSON_AGED, NAMED_THING_AGED, THING_AGED_QUALIFIED, PERSON_ELSEWHERE, PEOPLE_AGED,
    AFTER_YEAR_OLD, AFTER_YEAR_OLD_OKAY, CHILD_AGE_UNDER, LIST_BEFORE_IT, A_LIST_OF_AGES,
    GROUP_NAMED, THING_NAMED_BACK, PEOPLE_NAMED_ANYWHERE, SUBJECT_REACH, _A_THING_SAID_IS,
    _A_THING_POINTED_AT, _the_years_are_a_things, _children_by_year_old, _ages_held, _keep_the_ages,
    _relation_before, BARE_NAME, NOT_A_BARE_NAME, names_offered, NOT_DIET, DIET_STOP,
    foods_ruled_out, DIET_GROUP, OTHER_NO_DRINK, _somebody, OTHER_CONDITION, CONDITION_AS_A_WORD,
    JOB_PHRASE, OTHER_JOB,
)
from .facts_part_07 import (  # noqa: F401
    _a_name_for_the_pet, subject, _the_person_without_a_relation, losses, _may_be_a_name,
    _looks_like_a_name, _name_after_a_title, _a_relations_name, pet_appositive, a_name_picked,
    bare_name, OTHER_JOB_AS, OTHER_JOB_NAMED, _the_job_phrase, _names_before_a_fact, pet_name_only,
    _count_before, MOST_NAMES, _names_after, OTHER_PET, OWNER_OF, LIVES_ELSEWHERE, OTHER_PEOPLE,
    OWNER_OF_PLAIN, OWN_ANIMAL, OURS_ANOTHER, KIN_OWNER, _not_their_animal, _someone_elses,
    FOOD_BEFORE, FOOD_AFTER, NAME_BEFORE, PET_COMPOUND, AFTER_ANIMAL, AFTER_A_PET, THEIR_ANIMAL,
    SOMEONE_ELSE_HAS, A_RELATION_OWNED, OWNED, OWNED_VALUE, OWNED_STOP, OWNED_MAKES, OWNED_MODELS,
    OWNED_KIND, OWNED_NOT_A_MODEL, OPENS_AN_ASK, TELLS_ABOUT, _a_question, _owns, _the_thing_of,
    _the_model, _spell_the_model, _a_name_given_by_the_verb, GROWN_UP, _the_same_animal,
    _with_the_breed, _pets, PET_AGE_TAIL, _pet_age_tail, PET_AGE, PET_AGE_BARE, _pet_age,
    ADDRESSING, is_addressing, _names_it_aside, NOT_A_NAME_EITHER, DESCRIBING_ENDS,
    DESCRIBING_WORDS, ED_NAMES, NOT_A_NAME_WORD, COMMON_WORDS, NOT_A_NAME_ENDINGS, NEGATED_VERB,
    is_a_contraction, _not_a_name,
)
from .facts_part_08 import (  # noqa: F401
    reads_as_a_name, _name, _name_from, _was_names_a_role, _the_clause_before, _opens_a_subject,
    pet_counts, _describes_them, _bare_name, a_name_could_be, _object_words, _object_plan,
    _plan_verb, _a_plan_has_a_thing, PLAN_CLAUSE_BREAK, PLAN_CLAUSE_OPENER, _asks_about_the_plan,
    _plan_text, COPULA, STATE_FILLER, STATE_PARTICLE, STATE_MORE, STATE_WORDS, OFF_ABSENCE,
    OFF_AHEAD, _how_they_are, THING_COPULA, AHEAD_OF_THE_THING, THING_TODAY, _how_their_things_are,
    APPOINTMENT_CLOCK, APPOINTMENT_DAY, APPOINTMENT_PAST, APPOINTMENT_OWN_SUBJECT, TAKE_BACK_WORDS,
    APPOINTMENT_NOT_A_THING, APPOINTMENT_PAST_VERB, APPOINTMENT_A_VERB, APPOINTMENT_A_DATE_VERB,
    APPOINTMENT_NOT_A_VERB, APPOINTMENT_CORRECTION, DAY_REMARK_WORDS, DAY_REMARK_GLUE,
    _the_day_described, A_DAY_SAID_FIRST, _A_COUNT_NOT_A_CLOCK, _the_thing_said_after_the_day,
    _appointment, OBLIGATION, RECURRENCE, A_CLOCKED_EVENT, _coming_up, _dated_plan, CLAUSE_SUBJECT,
    WHEN_OR_WHERE, A_SHARED_VERB, CORRECTION_LEAD_RE, OPENER_WORDS, OPENER_PUNCTUATION,
    _the_opener_end, without_the_correction_opener, is_a_correction_opener, _said_after_the_subject,
    _the_verb_for, _with_the_verb_lent, _dated_plans, THE_THING_HAS_A_DAY, JOINED_PERSON,
    SUBJECT_JOIN, _with_the_person_joined_to_the_subject, SELF_INTRO, OTHER_START, NOT_A_PART,
    CONTINUATION_SPLIT, PERSON_SUBJECT, ANY_SUBJECT,
)
from .facts_part_09 import (  # noqa: F401
    _relation_facts, _job_as_a, _job_and_city, kid_ages, kid_count, _other_ages, _people, WISHING,
    CONTINUATION_VERB, CONTINUATION_KEYS, SAME_PERSON_CLAUSE, SAME_PERSON_SPLIT,
    _the_relation_named, _same_thing, _is_only_the_take_back, BOT_NAME, BOT_NAME_ASKED,
    BOT_NAME_TAG, BOT_NAME_TITLE, BOT_NAME_STOP, BOT_NAME_ASK, bot_name, CORRECTION_OPENER,
    SUBJECT_OPENERS, REPORTED, _reported_clause, _paid_by_a_period, _a_years_pay,
    SAYS_WHAT_THEY_ARE, THEIR_NAME, THEIR_PLAN, _one_entry_per_person, _union, _the_pronoun,
    RELATION_SAID, _the_person_the_pronoun_is,
)
from .facts_part_10 import (  # noqa: F401
    denials, _allergies, _other_no_drink, _other_diets, _other_conditions, _other_jobs,
    NAME_THEN_THE_VERB, _a_name_opening_the_clause, _the_name_in_front, _a_person, _same_person,
    NAME_AND_A_FIGURE, NOT_A_NAME_FIGURE, _a_name_and_a_figure, BODY_PARTS, BODY_PART, BODY_HURTS,
    BODY_LATERAL, BODY_PLACE, SOMEONE_ELSE, A_PART_HANDED_OVER, MY_OWN_PART, THE_PART_HURTS,
    THE_PERSON_SAYS, A_PLACE_ON_IT, _tied_to_them, _theirs, the_part_it_hurts, _extract,
)
from .facts_part_11 import (  # noqa: F401
    _the_marker_in_front, reread, _continued_parts, _a_clause_about_the_same_person,
    _self_intro_parts, a_correction_without_a_subject, extract, about_themselves,
)
