"""Normalisation: turn the way people type into ordinary words, once, for every module.

The understanding lane owns this file. `normalise(text)` cleans one line:

- chat-speak and shorthand ("u", "pls", "idk", "cn u", "wats") become ordinary words;
- apostrophes people leave out ("cant", "ive", "whats") are filled back in;
- contractions are expanded ("don't" -> "do not"), so a module can match the verb;
- obvious typos are corrected with one edit against the common-word lexicon, but only when
  the correction is unambiguous: a wrong fix is worse than no fix;
- letters people stretch ("sooo", "pleeease") are collapsed;
- run-on lines are split into clauses at discourse markers ("anyway", "so", "but"), and the
  clause that carries the ask is marked as the focus.

It returns a dict; nothing here reads `memory`, so it is safe to call on any line.

The implementation lives in the `normalize_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `normalize.<name>` is what it was.
"""
import itertools
import re
import unicodedata

from . import lexicon

from .normalize_part_01 import (  # noqa: F401
    _MEASURE, WORD, SAID_OUT, CHAT_KEPT_AS_TYPED, CHAT_AS_ONE_WORD, RAW_WORD, URGENT_WORDS,
    _ANY_WORD, CLIPPED_FAMILY, _doubles_its_last_letter, VOWEL_SET, VOWEL_SET_OR_Y,
    _drops_a_final_e, _keeps_its_e_before_ing, _ing_form, _inflections, _BASE, BASE, LEXICON,
    COMMON_RANK, ME_FOR_MY_CLOSES, THING_WORDS_BY_LENGTH, THING_WORDS, learn_thing_words, PHRASES,
    BREAKS, PRONOUN_BASES, ASK_WORDS, WANT_WORDS, WH_WORDS, AUX_WORDS, BE_WORDS, SUBJECT_WORDS,
    HOW_DEGREE, NO_ASK_AFTER, ASK_NOUNS, REPORTING, COPULAS, NOMINAL_BEFORE_COPULA, DETERMINERS,
    RELATIVE, RELATIVE_ASKS, FREQUENT, AEIOU, VOWELS, _double_variants,
    _a_doubled_letter_typed_once, _three_of_a_letter, _doubled_letter_words, _ie_variants,
    S_CLUSTERS, _missing_vowel, _extra_vowel, _A_WORDS, _a_said_for_an_ending, _dropped_letter,
    _an_ing_said_as_n, _a_leading_h, E_KEPT_WORDS, _e_kept_before_ing, _swapped_pair,
    _two_letters_the_wrong_way_round, NO_SWAP_TO, _A_WORD_THE_BOT_WRITES, _words_the_bot_writes,
    _a_word_the_bot_writes, _bones, _longest_consonant_run, URGENT_BONES,
    _an_emergency_word_left_out, NAME_FRAMES, CHAT_NAMES, NAME_ROLL, NAME_CALLS, _dropped_g,
    STOPPED_TH_STEMS, _stopped_th, SHION_WORDS, F_TYPED_FOR_TH, A_THING_TYPED_AS_A_LITTLE_WORD,
    A_THING_GOES_AFTER, _short_double, _one_letter_apart, CORE_VERBS, AFTER_A_VERB, BEFORE_A_VERB,
    _one_letter_wrong, _a_word_the_reading_knows, _known_word, _stems_of, _a_thing_a_letter_short,
    _a_core_verb_typed_wrong, _its_vowels_typed_wrong,
)
from .normalize_part_02 import (  # noqa: F401
    _shun_variant, _said_with_an_f, _said_with_an_f_anywhere, _near_a_part, PART_REACH, A_SIDE,
    ABOUT_THE_FORM, FINDING_A_TEAM, _a_game_named_another_way, _parts_that_hurt, CAUSES_A_STATE,
    OBJECT_PRONOUN, PHRASE_MEASURES, TIMES_A_STATE, AFTER_A_TIME, _a_letter_typed_twice,
    INTRODUCING_A_PERSON, INTRODUCING_AFTER, _an_introduction, STATES_OF_A_PERSON,
    _a_letter_wrong_in_a_state, _a_letter_apart, _a_consonant_left_out_of_an_ing_word,
    the_feeling_two_letters_are_gone_from, _two_letters_out, _feeling_without_its_ending,
    _a_vowel_left_out_of_a_state, _one_vowel_less, reads_as_a_sound, spelled, _unsays_the_word,
    _a_word_of_the_bots, OPENERS, WH_OPENERS, _slip, fix_opener, _plain_word, _four_spells_for,
    _collapse, _apostrophe, DIGIT_WORDS, BEFORE_WORD, BEFORE_VERB, FOR_A, FOR_OBJECT, FOR_MEAL,
    BE_VERBS, TOO_A, TOO_AFTER, TO_AFTER, A_NEGATION_BEFORE, TOO_A_GRADED, OPERATORS, COUNTS,
    COUNT_UNITS, COMPOUND_HEADS, COMPOUND_TAILS, NOT_COUNTED_AFTER, NOT_A_COMPOUND_HEAD,
    NOT_A_COMPOUND_TAIL, _counts_a_compound, A_LABEL_BEFORE, NUMBERS_BEFORE, _counts_a_thing,
    REPEAT_ONCE, REPEAT_ONCE_SUBJECTS, _once_only, AUX_OPENS, DROPPED_SUBJECT_AUX, _SUBJECTS,
    _PREDICATE_ONLY, _A_STATE_OF_THE_PERSON, _SUBJECTLESS_AUX, _STATE_FILLER, _STATE_TAIL,
    _SUBJECTLESS_ONLY, _HAVE_NEGATIONS, _HAVE_PARTICIPLES, _HAVE_THING, _HAVE_ASKING,
    _AFTER_PARTICIPLE, _opener_is, CAUSE_A_SUBJECT_FOLLOWS, CAUSE_A_CLAUSE_VERB,
)
from .normalize_part_03 import (  # noqa: F401
    opens_without_subject, subject_missing, CAUSE_BEFORE_A_NOUN, CAUSE_BEFORE_A_VERB,
    CAUSE_A_DEMONSTRATIVE, _cause_in_place_is_the_verb, ONE_WORD_FOODS, _one_word_food,
    JOINED_WORDS, _joined_words, _z_for_s, _ache_for_aike, SPLIT_CONTRACTION, SPLIT_NOT, NOT_WORDS,
    _a_contraction_typed_with_a_space, UP_TOO_ASKS, HEART_MEASURES, HEART_FEELINGS,
    HEART_SAID_AS_A_FEELING, SAID_AS_A_FEELING, SAID_IT, _the_ask_said_plainer, _A_CLOSING_WORD,
    _A_HEAD_IN_THE_IDIOM, _A_CLIPPED_HEAD, _me_for_my_pass, _phrase_pass, PUNCT_BREAK, SENTENCE_END,
    TOKEN, THOUSANDS, THOUSANDS_SAID_WITH_A_SPACE, CURRENCY_SIGNS, CURRENCY_SIGN, CURRENCY_FACTOR,
    _the_figure, _a_sign_is_a_word, NOT_A_THING, AFTER_A_THING, BEFORE_A_THING,
    BEFORE_A_PREPOSITION, NOT_A_THING_ENDING, LONG_ENOUGH_TO_BE_A_VERB, ING_THINGS, DOING_NOT_THING,
    _is_doing_something, KIN, NOT_A_THING_AFTER, TIME_WORDS, PLACE_WORDS, NOT_A_THING_PAIR,
    OWNING_VERBS, ASKS_WHOSE, possessive_me, SUN_WORDS, OWNING_A_PERSON, SON_VERBS,
    a_son_not_the_sun, LOOSE_FOR_LOSE, THE_LOSING, BEFORE_THE_LOSING, A_PART_THE_PAIN_IS_IN,
    A_GLASS_OR_A_PAN, A_PART_A_PERSON_OWNS, A_PAIN_WORD, A_KEEPING_A_THING,
    THE_HEART_SAID_THE_OTHER_WAY, A_CHOKE_SAID_THE_OTHER_WAY, A_THING_WORN, A_STATE_YOU_CAN_FEEL,
    A_COPULA, BEFORE_A_JOB, A_JOB, A_TIME_TO_LEAVE, _a_slip_that_is_a_word, loose_is_lose,
    DIGIT_AS_WORD, MOTION_BEFORE, DEMONSTRATIVE, A_PERIOD_FOLLOWS, A_WORD_CAN_FOLLOW, KNOW_SUBJECT,
    NOT_BEFORE_KNOW, A_VERB_CAN_FOLLOW, BE_FORMS, HAVE_FORMS, MODAL_FORMS, LEFT_OFF_CONTRACTION,
    CONTRACTION_NEXT, PLURAL_SUBJECTS, THIRD_PERSON, PERSON_WORDS, PERSON_PREPS, HOW_FOLLOWS,
    BEEN_WORDS, BEEN_SUBJECT, THING_POSSESSIVES, IN_NOUNS, BIN_CONTAINERS,
)
from .normalize_part_04 import (  # noqa: F401
    respell_urgent, _family_put_back, _a_name_slot, _a_thing_where_a_thing_goes, _missing_e,
    _where_a_state_stands, _ends_a_state, _opens_a_state, _a_measure_spelt_wrong, _measures_a_state,
    _near_a_feeling, _the_state_is_the_whole_frame, fix_typo, _token, _the_thing_has_been,
    _is_person, _plain_chat, _spells_a_helper, _is_be, IRREGULAR_PARTICIPLES, _is_participle,
    KIN_SINGULAR, KIN_HAS, KIN_IS, KIN_FILLERS, CAN_FOLLOW_A_VERB, _a_gerund_reads_as_a_verb,
    _kin_needs_a_helper, FAMILY_SHRT, SHRT_THINGS, POSSESSIVES, _family_short, PERIOD_COUNTS,
    CLIPPED_UNITS, CLIPPED_THINGS, THING_AFTER, THING_JOIN, THING_PLACE_AFTER, THING_DETERMINER,
    THING_PLACE_WORDS, THING_SUBJECT, A_COUNT, _counts_a_period, _is_a_count, A_PARTS_OF_A_PERIOD,
    HR_IS_THE_DEPARTMENT_AFTER, _hr_is_the_department, _says_one, NOT_BEFORE_A_NOUN,
    _is_a_thing_here, _clipped_thing, _is_before_a_noun, _is_said_of_a_person, _is_possessive,
    A_FEELING_CAN_BE_FOLLOWED, BEFORE_A_FEELING, _sounds_like_a_feeling, AINT_FORMS, HAS_SUBJECT,
    AINT_PLURAL, MISSING_E_AFTER, PAST_AS_PARTICIPLE, HV_SUBJECTS, HV_HELPERS, FIRST_PERSON_BE,
    AMOUNT_BEFORE_A_STATE, BE_BEFORE_A_STATE, THIRD_PERSON_BE, BARE_TO, DETERMINER_IN_FRONT,
    POSSESSIVE_IN_FRONT, AFTER_A_STATE, A_STATE_THEN_A_TIME,
)
from .normalize_part_05 import (  # noqa: F401
    reads_as_a_feeling, repaired_tokens, _digit_word, _lookahead, _WERE_STATE, _WERE_ARE,
    _WERE_DOING, _AFTER_A_DOING, _WERE_PLACE, _WERE_IN_THE_PAST, _AFTER_A_LEAD_IN_SUBJECT,
    _WERE_LEAD_IN, _A_QUESTION_VERB, _were_for_another_word, _a_doing, UP_TO_SPELLINGS,
    WHAT_ARE_YOU_SPELLINGS, WHAT_ARE_YOU_AFTER, LETTER_C_IS_SEE, UP_TO_LEADS, UP_TO_TAGS,
    GLUED_LEFT, GLUED_RIGHT, GLUED_COLLAPSE, GLUED_DO, GLUED_AFTER_A_DO, _a_doubtful_split, I_GLUED,
    A_PRONOUN_GLUED, A_PRONOUN_STATE, _PLACES_SAID_WHOLE, _a_place_said_whole,
    _a_pronoun_said_together, _a_state_typed_onto_im, _glued_words, MRS_IS_THE_WIFE,
    _the_mrs_is_the_wife, _SUBJECT_SAID, _chat_words_said_out, HELLO_SAID_SHORT, HELLO_TAIL,
    _a_hello_said_short, _glued_said_apart, RUN_ON_OPENERS, RUN_ON_SELF, RUN_ON_MINE, RUN_ON_WORDS,
    RUN_ON_PEOPLE, RUN_ON_SELF_LONGEST, RUN_ON_SHORTEST, RUN_ON_LAST_PIECES, _said_run_on,
    _a_run_and_what_surrounds_it, _typed_without_spaces, APOSTROPHE_TAILS, APOSTROPHE_BASES,
    APOSTROPHE_NOT, _the_said_apart_forms, _the_ways_a_word_is_typed_apart, SAID_APART_FORMS,
    SAID_APART, A_LETTER_AFTER, _said_apart, said_apart, SOLFEGE, MI_IS_ME_AFTER, MI_IS_ME_BEFORE,
    MI_IS_A_NAME_AFTER, MI_BACK_VERBS, ILL_GOES_ON, ONE_OF_A_KIND, ONE_PART_AFTER,
    _one_of_the_parts, VEGGIES_AFTER, WEARS_AFTER, SUM_THE_NOUN, SUM_STAYS_AFTER, _sum_word,
    YOU_ARE_AFTER, _join_chat_digits, _SPACED_RUN, _said_apart_as_one_word, _SPACED_PIECE,
    _said_apart_as_one,
)
from .normalize_part_06 import (  # noqa: F401
    _repair_openers, _only_leaders_before, _ill_is_i_will_going, _an_ill_that_is_i_will,
    _left_off_contraction, _wers_word, _positional_word, DOCS_VISIT, DOCS_PAPER, DOCS_SCREEN,
    DOCS_ON, _docs_on_a_screen, MEAL_WORDS, FOOD_SLOT_LEAD, NOT_A_MEAL_TYPO, TIME_AFTER_MEAL,
    _near_a_meal, _a_meal_word_misspelt, _docs_doctor, ONE_RELATION, HAS_FORMS, ONE_RELATION_VERBS,
    SORE_IN_FRONT, SORE_FILLERS, SORE_PARTS, a_sor_bit_is_sore, _one_relation_says, _ask_start,
    WH_QUANTIFIERS, NOT_IN_A_QUESTION_PHRASE, AFTER_AN_INVERTED_AUX,
    _a_word_between_the_ask_and_its_aux, _inverted_ask, _reported, _split_ask, CLAUSE_OPENERS,
    _opens_clause, HAS_AFTER, HAS_SUBJECTS, _says_has, _clauses, LEADERS, LIKE_STARTS_A_CLAUSE,
    _a_leading_like_is_a_filler, EXCLAIMED_AFTER_A_QUESTION, EXCLAMATION_OPENS, EXCLAMATION_PHRASE,
    _EXCLAMATION_SUBJECTS, without_a_leading_exclamation, _an_exclamation_in_front,
    _an_exclamation_is_not_a_thing, strip_leaders, _LEADER_WORD, without_leaders, _PLACE_STOP,
    _PLACE_LEADS, _WH_QUESTIONS, _clause_stop, background_clause, REASON_STARTS, reason_positions,
    background_positions, _the_measure_clause, _asking,
)
from .normalize_part_07 import (  # noqa: F401
    _focus, LETTERS, _unaccent, _INTENSIFIER, WH_INTENSIFIER, WH_INTENSIFIER_LINE, WH_ANY,
    intensifier_positions, _TYPED_SURPRISE, _the_surprise_typed, _without_the_intensifier, _A_CLIP,
    _a_clip_kept_only_with_its_cue, _fix_auxiliaries, TAG_WORDS, TAG_PLEASE, TAG_THANKS,
    TAG_QUESTION_LEADS, TAG_GUARD_BEFORE, CHANGE_OF_SUBJECT, _change_of_subject_off,
    _without_a_tag_at_the_end, SPELLING_ASK, SPELLING_ENDINGS, _spellings_of_one_word, NAMED_LETTER,
    _names_a_letter_beside_a_slip, _A_SHORT_WORD_IS_NAMED_BEFORE, _A_SHORT_WORD_IS_NAMED_AFTER,
    _a_short_word_named, _asks_the_spelling, DAY_NAMED, OWNER_WITHOUT_THE_DAY, TAIL_OF_A_DAY,
    CAN_NOT, _can_not_as_one_word, _the_day_left_out, A_NUMBER_OF_SOMEONES_DAY, NOT_MY_OWN_DAY,
    _a_day_named_as_not_mine, _KEEPING_PLACES, _KEPT_THINGS, _DAY_WORDS, _KEPT_ALREADY,
    _SMALL_NUMBERS, _NUMBER_SHAPE, _a_number, _kept_for, _only_doubles_a_letter, normalise,
    SICK_AS_FEELING, _FEELING_WORD, FEELING_BEFORE_SICK, _the_feeling_word,
    without_the_figure_of_speech, SUGAR_LEVEL, SUGAR_AFTER_ROSE, SUGAR_PRICE, SUGAR_PRICE_SHAPE,
    SUGAR_FIRST_PERSON, BAD_SAYING, BAD_WORD, PART_THAT_IS_BAD, THE_ODD_PLURALS,
    _the_part_that_is_bad, _the_part_that_hurts, _the_sugar_that_is_blood, glued_words,
)
