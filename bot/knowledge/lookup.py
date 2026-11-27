"""Find the knowledge entry a line is about, by meaning rather than by wording.

Every domain module in bot/knowledge/ exposes ENTRIES, a list of Entry built with
entry(). An Entry says what it is about with `key` (single words or short phrases,
optionally a tuple of alternatives) and how to answer with `reply`. The matcher finds
the entry whose key words the line actually contains, so one fact answers every way
of asking for it: "how long do I roast a chicken", "chicken cooking time" and
"2kg chicken, how long?" all reach the same entry.

    entry("roast-chicken", ("chicken", ("roast", "oven", "cook", "time")),
          "About 20 minutes per 500g at 190C (170C fan), plus 20 minutes: ...")

Matching is deliberately strict. Words match loosely (eggs/egg, cooking/cook), a
phrase matches a short run of words, a phrase scores 3 and a single word 2, and a
line needs MIN_SCORE (4) to be answered at all. So two signals are needed, and a line
that only mentions a topic in passing ("my chicken pox") falls through to a module
that can help, or to "I don't know", instead of getting the wrong canned answer.

The one exception is a misspelt key word. People type "chiken" and "radiatior", so a
line word that is no key word at all and is a single slip (one letter wrong, missing,
extra, or swapped with its neighbour) away from exactly one key word is read as that
key word. Three things keep that from turning a real word into a fact: the word must be
one the engine does not already read, in any of its forms ("leaving" is a form of
"leave", so a charging phone does not become a changing leaf), the slip must lead to a
single word family ("radiaters" is one answer, "lips" is not), and a slip never lifts a
line past the entry's avoid list, not even an ambiguous one ("brest" is a whole-bird
question neither way).

The implementation lives in the `lookup_part_NN` parts (in bot/knowledge_parts); this module keeps the header
imports and re-exports every name the parts bind, so `lookup.<name>` is what it was.
"""
import re

from ..knowledge_parts.lookup_part_01 import (  # noqa: F401
    _DREAM, string, SLIPS, lexicon, COMMON_WORDS, TIME_WORDS, GRAMMAR_ONLY, names_a_thing, WORD,
    ASKING_MODALS, ASKING_SUBJECTS, _asking_with, MIN_SCORE, MODAL_PHRASES, FEELING_WORDS,
    ASK_ABOUT, ORIGIN_ASK, NOT_A_NOSE, TOOTH_OUT, TOOTH_OR_GUM, WORD_WEIGHT, PHRASE_WEIGHT,
    _SAVING_VERB, _SAVING_FOR_A_TRIP, _AFFORD_THE_TRIP, saving_for_a_trip, PRESENT_ASK, IMPROVE,
    HOW_OFTEN_WORDS, the_line, said_text, guard_passes, asks_how_often, SANDING_JOB, a_sanding_job,
    SAID_LEADS, said, _WRAPPED, _NOT_A_SUBJECT, _NOT_A_THING, ASK_FRAME_IDS, AS_A_KIND,
    MIN_TYPO_LENGTH, RING_AS_A_CALL, ENDINGS, MIN_FORM, Entry, PLACES_AFTER_BACK, BACK_OF_THE_HOUSE,
    THE_BACK_ITSELF, APPLIANCE_NAMES, the_appliance_swallows_the_name, the_back_is_a_body_part,
    _avoid_words, PEOPLE_MALE, PEOPLE_FEMALE, about_them, WHERE_PHRASES, PRICE_COMPARED, asks_where,
    WHERE_PART_WORDS, asks_where_a_shop_answers, THE_FAULT, _BOUNDED, _BOUNDED_KEEP, _bounded,
    the_fault, FOOD_SUBJECT, HAS_GONE, GONE_INTENSIFIER, GONE_STATE, STOPPED_WORKING,
    a_thing_has_stopped, the_thing_has_gone, FOOD_NAMED, SMELL_VERBS, _BAD_IS_A_STATE,
    OFF_SAID_OF_FOOD, A_GOOD_SMELL, BEFORE_OFF, OFF_STATE_ASKS, JOB_GUARD, _BORROWING_IN_THE_LINE,
)
from ..knowledge_parts.lookup_part_02 import (  # noqa: F401
    food_has_gone_off, _OFF_A_PERSON, a_price_not_a_loan, _FLAT_YOU_LIVE_IN,
    _THE_HEAT_OF_AN_ARGUMENT, not_the_heat_of_an_argument, _ORDER_OF_STEPS,
    the_ask_is_the_order_of_steps, not_the_ask_about_the_order, not_the_flat_you_live_in,
    _A_BAKE_OR_A_PAN, _CAME_OUT_FLAT, _THE_GROUND_UNDERFOOT, not_the_flat_of_something_made,
    _YEAR_OLD_FIGURE, _A_THING_SAID_IS, _A_THING_JUST_BEFORE, _A_THING_POINTED_AT, _PEOPLE_AGED,
    the_years_are_a_things, _CHILD_WORDS, _CHILD_PHRASES, _A_YEARS_OLD, _the_age_is_a_childs,
    _key_says_years_old, _CHILDS_AGE_ROWS, _KEEPING_AN_EYE, not_keeping_an_eye_on_it,
    SHORT_OF_SLEEP, NOT_TIRED_AFTER_ALL, A_DEVICE_THAT_SLEEPS, _A_PERSON_WHO_SLEEPS, _SLEEPY_MARKS,
    _the_device_is_the_one_falling_asleep, the_body_is_short_of_sleep, not_a_sleepy_body, all_of,
    _the_whole_line, entry, KINDS_WORDS, KINDS_SHAPE, KINDS_FOLLOW_UP_WORDS, KINDS_ASKS_ME,
    KINDS_ASKS_WITH_A_VERB, KINDS_SAYS_HOW_IT_IS, KINDS_NAMED_A_USE, asks_the_kinds, kinds_entries,
    _CONTRACTION, IRREGULAR_PLURALS, _CURLY, _CURLY_ANY, _doubles_for_an_ending, _is_consonant,
    _FORMS_CACHE, _FORMS_CACHE_KEEP, NOT_THE_STEM, NOT_A_WORD_WITH_AN_S, NOT_THE_STEM_WITH_E,
    NOT_A_BASE, NOT_THE_DOUBLED_STEM, _add, _CHAT_PHRASES, _CHAT_TAIL, _ABOUT_THE_CHAT,
    about_the_chat, _FUNCTION_WORDS, _cvc, tokens, _THROAT, _BRIDGES, _BRIDGE, _PUNCTUATION,
    _past_a_handoff, CARER_FRAME, AN_ILLNESS, _past_the_carer, DEAD_AS_VERY_AFTER,
    _without_a_dead_that_only_means_very, _MARKS, COOKING_AS_A_NAME,
)
from ..knowledge_parts.lookup_part_03 import (  # noqa: F401
    _forms, _work_out_forms, _bare_is_the_word, _without_a_cooking_that_is_a_name, CHILD_BY_PLACE,
    CHILD_PLACE_WORDS, CHILD_SIZE_WORDS, CHILD_AFTER_A_SIZE, EVERYDAY_CHILD, A_CHILD_WORD_BY_ITSELF,
    A_CHILD_GETTING_OLDER, A_TEEN, NOT_A_CHILD_SAID, TWO_OF_US, _with_the_animal_in_hand,
    _THE_PRONOUNS, _the_animal_rules_out_that_card, _with_the_child_by_place, _one_edit, _stem,
    _COMMON, _STEMS, _engine_reads, PLURAL_ONLY_PHRASES, _WANTED_CACHE, _ARTICLE_WORDS,
    _ARTICLE_FORMS, _WHERE, _LINE_FORMS, _PHRASE_SPANS, _WANTING, _ASK_ABOUT_SOMEONE, _SAID_BETWEEN,
    _ONE_SPELLING, _ONE_SPELLING_EITHER_WAY, _short, _long, WANT_FILLER, ASK_PEOPLE, DENY_SAID_OF,
    DENIERS, STATES_AFTER, DENY_BETWEEN, _FRAME_MASK, ASK_FRAME, WHEN_WORDS, A_LENGTH_WORD,
    A_STAND_IN, FRAME_ENDS, FRAME_PRONOUNS, ASK_PHRASE_WORDS, _ASK_PHRASE_MASK, REPORT_LEADS,
    REPORT_PERSON, REPORT_FILLER, HAPPENING_AGAIN, EXPLAIN_LEADS, EXPLAIN_FILLER,
    ASKS_FOR_THE_HANDS, A_HAND_OR_EYE_DOES_IT, ASKS_WHAT_IT_SAYS, OWN_THING_ON_THEIR_SIDE,
    THEIR_OWN_HANDS_THINGS, GOES_IN, COUNTED_INTO_A_THING, HOW_MANY_DAYS, KEEPS_OR_STORES,
    _KEEPING_VERB, _RESULT_VERB, _SPOILING, _ING_NOUNS, _KEEPING_KEY, _LIFE_KEY, _RECURRING,
    _RECURRING_ANYWAY, _RECURRING_WITH, _SUBJECT_POINTS, NOT_THE_ADJECTIVE, _A_PERSON,
    _NOT_A_THING_HAD, _FILLER, FEELING_ABOUT, FEELING_ENDS, FEELING_NAMES_NOTHING, FEELING_DOMAINS,
    FEELING_FAULT_WORDS, FEELING_SPEAKER, FEARED_THINGS, _WHERE_I_PUT, _WHERE_TO_KEEP,
    _KEPT_SOMEWHERE, _HOLDS_MONEY, _THE_THING_JUDGED, _POINTS_AT_IT, _A_PLACE_ON_THEM, _NOT_GONE,
    _SUBJECT_LEAD, _POSSESSIVE, _OF_THE_RULE_OUT, _THE_DEGREE_WORDS, _THE_HEAT_OF_THE_DAY,
    _THE_WH_WORDS, _ASK_FRAME, _PLACES_PEOPLE_LIVE_IN, _COLD_WORDS, _BETWEEN_A_PLACE_AND_ITS_COLD,
    _HOW_A_PERSON_IS_COLD, _SAYS_OF_THEMSELVES, _DEFINITION_ASK, _DEFINITION_TAIL,
    _DEFINITION_POINTERS, _DEFINITION_TROUBLE, _DEFINITION_EMPTY, _DEFINING_VERBS, _BE_VERBS,
    _DEFINITION_ARTICLES, _BEFORE_THE_THING, NAME_ALONE_DOMAINS, NOT_A_NAME_ALONE,
    A_STATE_AS_A_NAME_END, A_STATE_IN_THE_PHRASE, POINTS_BACK, FOLLOW_ON_WORDS, ASK_FRAME_WORDS,
    SUBSTITUTE_WORDS, RETURNED_AFTER, GENERAL_BODY, _CUT_BESIDE, _STILL_GOOD_ASHERS, _KEEPING_WORDS,
    _A_KEEP_AND_A_LENGTH, COLOUR_WORDS,
)
from ..knowledge_parts.lookup_part_04 import (  # noqa: F401
    _typo_forms, _wanted, _MIN_BARE_WORDS, BARE_WEIGHT, _wanted_bare, _phrase_span_bare, _shape,
    _SHAPE_CACHE, _line_forms, _where, _phrase_span, _A_BREATH, _ASK_FRAME_FORMS, _ask_frame_forms,
    _phrase_span_between, _the_same_words, _PHRASE_OTHER_SPELLINGS, _OTHER_SPELLINGS_KEEP,
    _work_out_the_same_words, _phrase_span_work, _phrase_span_spelling, _phrase_found, _PART_FORMS,
    _PART_FORMS_KEEP, _part_forms, _part_matches, _part_match, _part_score, _own_words,
    _misspelt_avoid, WANTING, WANT_KNOWING, ASK_PERSON_PRONOUNS, ASK_PERSON_POSSESSIVES,
    _about_someone_else, _said_about_someone, _ask_about_someone_only, _the_subject_it_avoids,
    _the_ask_said, _wanting, _only_the_want, _key_on_the_want, _denier_inside, _denied,
    A_SAYS_NOTHING, _only_the_frame, _TAKE_OFF, _says_removal, FRAME_WORDS, _FRAME_PRONOUN_FORMS,
    _frame_pronoun_forms, _the_subjects_own_clause, _a_clause_about_the_thing, _frame_starts,
    _FRAME_STARTS, _frame_masked, _key_names, _unframed, _without_ask_phrase, _said_again,
    _bare_report, _asks_to_explain, _only_as_a_kind,
)
from ..knowledge_parts.lookup_part_05 import (  # noqa: F401
    _says_a_shape, PACK_DATE, DAY_WORDS, _under_their_own_hands, A_HOUSE_WARMING_UP, A_WEATHER_ASK,
    A_WHAT_TO_WEAR, KEPT_FOODS, KEEPING_WORDS, not_a_count_for_the_box_or_the_dish,
    a_food_is_being_kept, CONTAINERS, only_a_container, A_HOURS_ASK, DISH_ASK, _KEEPING_ROWS,
    _keeping_row, _gerund, _later_words, _keeps_failing_at, _keeps_failing, _the_whole_subject,
    MACHINE_SOUNDS, _rarity, _TAIL_ASK_WORDS, _the_tail_asks_about, _rank, _CACHE, _CACHE_KEEP,
    _key_words, _KEY_FORMS, _key_forms, _two_positions, _word_index, _INDEX, _reaching,
    _domain_rarity, _vocabulary, _y_word_stems, _a_word_itself, _read_the_adjective,
    _read_a_thing_had, _read_typos, _without_possessive, FEELING_ABOUT_A_THING, _names_a_fault,
    _speaker_is_feeling, _names_a_feared_thing, _feeling_occasion, _the_kept_rows,
    _the_thing_the_chat_is_on, _without_the_place, _a_thing_that_has_not_gone,
    _what_is_wrong_with_them, _without_the_ruled_out, _the_degrees_are_a_temperature,
    _answers_a_qualification, _the_person_says_they_are_cold, _the_place_the_line_says_is_cold,
    _answers_the_cold_of_a_person, _answers_the_cold_of_a_place, _the_card_for_the_place_first,
    _the_ask_reading, _the_ask_on_its_own,
)
from ..knowledge_parts.lookup_part_06 import (  # noqa: F401
    score, _the_thing_asked_about, _words_of, _asks_what_it_is_for, _SUBJECT_AT_MOST, _a_number,
    _the_thing_in, _the_reply_defines, _the_key_names_the_thing, _the_name_card, _the_name_alone,
    _declared_for, _defines, _named_things, PLAN_WORDS, _plans_it, _names_one,
    _only_asking_about_it, names_nothing_of_its_own, _ROWS_CACHE, _ROWS_KEEP, ASK_NAME_CAP,
    ASK_PLAIN_CAP, _the_names_in_the_ask, _the_ask_in_order, _two_clauses, _rows_key, _line_rows,
    _scanned_rows, _the_longest_run, _row_order, PLAIN_MARGIN, _plainer, _the_subjects_own_row,
    _offers_a_substitute, BODY_WORDS, SPECIFIC_PARTS, PART_INSIDE, _inside, _a_cut_of_meat,
    _body_parts, _key_body_parts, _a_part_the_line_does_not_have, _another_part, _KEEPING_ANSWER,
    _asks_if_it_is_still_good, _a_keeping_row, _a_keeping_key, A_COLOUR_USED, ASKING_FIRST,
)
from ..knowledge_parts.lookup_part_07 import (  # noqa: F401
    _the_subject_the_line_leans_on, _a_price_judged_is_not_answered_here, _a_range_for_the_thing,
    find, _the_best_entry, leans_on_a_subject, A_COLOUR_ASKED, COLOUR_ASKED_WORDS, WEARING,
    OCCASION, A_DRESS_CODE_AFTER, _a_dress_code, AFTER_A_COLOUR_STANDS, WORN_AFTER_A_COLOUR,
    _the_colour_is_the_whole_ask, a_colour_is_worn, _the_words_without_a_colour, _BARE_IN_A_KEY,
    _the_key_words, THE_SAME_OCCASION, _the_occasion_family, _the_occasion_words,
    _the_card_for_the_occasion_asked, _the_answer_the_colour_dragged_in, _best, HOUSEHOLD_WORDS,
    _household_reading, _other_reading, CONTEXT_WORDS, SPECIFIC, _says_a_key_word, _touches,
    _parts_across, key_words, about, WEIGHT_UNITS, a_weight, PERSON_PRONOUNS, _refers_to_the_person,
    SPEAKER_ONLY, HANDLING_WORDS, _says_how_the_speaker_handles_it, _following_on, _WEAR_ASK,
    asks_what_to_wear, _topic_domains, _in_topic, about_the_topic, MISSING_WORDS, _is_a_person,
    _says_what_is_missing, _reaches, names_its_own_subject, _wrapped_subject, _the_ask_it_wraps,
    COMMON_WORD, names_one_thing, _the_subject_alone,
)
from ..knowledge_parts.lookup_part_08 import (  # noqa: F401
    _said_as_a_report, GONE_OFF_SIGNS, says_it_has_gone_off, said_in_this_line,
)
