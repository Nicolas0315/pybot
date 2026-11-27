"""What kind of line this is: the broad kind, the finer intent, and what it asks for.

`kind` keeps the four values other lanes already read (empty, greeting, thanks, question,
statement). `intent` and `asks` say more, and every richer answer is a new key, so a module
written against `kind` keeps working.

The classification is driven by small word sets, checked in order from the most specific
reading to the most general, so adding a word to one set improves every line that uses it.

The implementation lives in the `kinds_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `kinds.<name>` is what it was.
"""
import re

from . import lexicon
from .normalize import (KIN, UP_TO_LEADS, background_clause, background_positions,
                        opens_without_subject, strip_leaders)

from .kinds_part_01 import (  # noqa: F401
    NEGATIONS, PRONOUNS, SUBJECT_NEGATIONS, GREETINGS, FAREWELLS, THANKS, QUESTION_WORDS,
    THANKS_ASK_NOUNS, THANKS_ASK_PREPS, THANKS_ASK_WORDS, GIVEN_ADVICE, QUESTION_STARTS,
    YESNO_STARTS, AFFIRM, DENY, ACK, LAUGH, POLITE, RECOMMEND, TIPS, TIPS_WANTED, TIPS_ABOUT,
    TIPS_SUBJECT, TIPS_AMOUNT, HELP_ASK, HELP_ASK_SUBJECT, HELP_ASK_TAIL_CLAUSE, HELP_ASK_NOT,
    HELP_ASK_OWN_SUBJECT, _asks_for_help, VERDICT_ASK, QUESTION_WORD, _asks_a_verdict, LIMIT_SHAPES,
    LIMIT_SOFT_BEFORE, LIMIT_SOFT_AFTER, LIMIT_ROOM, LIMIT_REFUSAL, LIMIT_A_FACT, LIMIT_NOT_A_START,
    PAST_ENDS, A_THING_NOT_A_CLAIM, CLAIM_ENDS, CLAIM_STEMS, _claim_forms, names_a_claim,
    LIMIT_NOT_A_THING, RULED_OUT, RULED_OUT_ENDS, RULED_OUT_NO_THING, _A_CLASS_OF_THING,
    _a_class_of_thing, RULED_OUT_CORRECTION, _ruled_out_of, _limit_of, RECOMMEND_PHRASES, OPINION,
    CHOICE, OPPOSITE_PAIRS, SCALE_ASK, two_ends_of_one_scale, REFUSED_PAIR, _turns_the_pair_down,
    COMPARE, REQUEST, STEPS, STEPS_WORD, WRITE, A_COMPARISON, SELF_ONLY_CUES, CONFUSED_SELF_ONLY,
    LABEL_ON_A_PERSON, THING_OR_PERSON_CUES, OWN_PERIOD_NOUNS, OWN_PERIOD_FILLER, OWN_PERIOD_HEADS,
    OWN_PERIOD_STOPS, NOT_THE_SPEAKERS_DAY, OWN_PERIOD_REACH, PERIOD_CUES, A_PERIOD, A_MONTH_PERIOD,
    A_MONEY_SUBJECT, A_LIMIT_ABOUT_PEOPLE, LAUGHED_OFF_AFTER, _laughed_off, SAD_PLAIN_CUES,
    SELF_ONLY_STATE, BODY_STATE_CUES, IDIOM_STATES, HEART_DEGREES, HEART_IN_A_STATE, BROKEN_HEARTED,
    A_BROKEN_HEART, BROKE_A_HEART, EMOTION_WORDS, ALWAYS_SELF_ONLY, SAID_AS_A_NEGATION,
    NOT_A_MOOD_THERE, GOOD_EMOTION_NAMES, NEGATIVE, POSITIVE, TERMS_OF_ADDRESS, ADDRESSED_LINES,
    OK_WORDS,
)
from .kinds_part_02 import (  # noqa: F401
    SAYS_HOW_THEY_ARE, STATING_VERB, SPEAKER, NEWS, ABOUT_BOT, ABOUT_BOT_END, ROBOT_WORDS,
    GENDER_WORDS, TASTE_VERBS, _a_person_they_like, LEARNED_ON, _a_thing_they_own, ASSISTANT_NAMES,
    PRODUCT_ASK_WORDS, PRODUCT_ASK_TAIL, SELF_WORDS, SELF_ASK, SELF_FILLER, NOT_AFTER_THE_BOT,
    NOT_BEFORE_THE_BOT, NOT_AUX, CLAUSE_OPENERS, CAPABILITY, CAPABILITY_FILLER, CAPABILITY_CARRIER,
    CORRECTION, GOING_ON_WHEN, DOING_FILLER, BEEN_WHEN, BEEN_SAID, SPENT_TIME, STILL_COMING,
    SMALL_TALK, ASK_KEYS, SHORT_REPLIES, AGREEMENT_IDIOMS, agreement_of, EVENT_WORDS, MATH_WORDS,
    DEFINITION, ASKS_ABOUT_A_PERSON, BARE_DEFINITION, NOT_A_DEFINITION_HEAD, _has_any,
    SMALL_TALK_WORDS, ADDRESS_WORDS, SMALL_TALK_LEFTOVER, small_talk_only, CUE_FOLLOW,
    PHRASE_OPENERS, CLAUSE_VERBS, CLAUSE_HELPERS, STATE_NOUNS, STATE_TAIL, SPEAKER_TAIL, ING_THINGS,
    ING_TAKES_NO_OBJECT, _a_verb_holds_it, _state_before, _verb_after, _clause_follows,
    BODY_SUBJECT, _a_body_part_before, STATE_JOINERS, OBJECT_MARKERS, TIME_MARKERS, TAIL_STOPS,
    _state_cue, VERB_ONLY_STATE, COPULA_BEFORE, _a_copula_before, ABILITY_AT, EPISODE_NOUNS,
    _names_an_episode, STATE_AS_FEELING, FEELING_NOT_MOOD, FEELING_FILLER, FEELING_COPULA,
    FEELING_CUES_BEFORE, a_broken_heart_shape, NOT_THEIR_OWN, A_PERSON_ELSE,
    A_PERSON_IS_THE_SUBJECT, A_POSSESSED_HEART, _somebody_elses_heart, HAVE_A_BROKEN_HEART,
    _a_broken_heart_is_theirs, HEDGED_LOW, HEDGED_DOUBT, HEDGED_OK, HEDGED_WRAPPER, _a_hedged_low,
    _copula_just_before, WORK_ON_ME, ACT_ON_FILLER, PARTS_OF_ME, ACT_ON_LEAD, _works_on_the_speaker,
    _skeleton, _SOUND_CUES, _sound_cues, feeling_by_sound, FEELING_SOUND_FRAME, SOUND_FOLLOWS,
    _a_feeling_can_end_here, _a_period_of_their_own, ACTS_ON_THE_SPEAKER, LAUGH_AT_THE_END,
    A_BODY_SUBJECT, _acts_on_the_speaker, GETTING_WORSE, NO_BETTER, BETTER_OFF, GOOD_WORD_MISSING,
    GOOD_WORD_COMPARED,
)
from .kinds_part_03 import (  # noqa: F401
    cue_about_person, _speaker_before, _takes_an_object, _object_after, _state_of_a_person,
    _said_of_the_speaker, _state_as_feeling, _feeling_said_as_a_sound, GOOD_WORD_BY_COMPARISON,
    REFERRING, POINTED_AT, _capability_question, ME_ASKS, ME_TAIL, ME_LEAD,
    _asks_how_the_bot_sees_me, WHO_TALKING, WHO_A_THING, WHO_TAIL, _asks_who_this_is,
    WHERE_BOT_TAIL, _asks_where_the_bot_is, ANSWERING_A_QUOTED_ASK, WHILE_ASK, KEEPING_ASK,
    STOP_ASK, STOP_ASK_FILLER, a_stop_ask, STATE_WORDS, PERSON_NOUNS, OTHER_PEOPLE, MOOD_NOUNS,
    PERSON_SUBJECT, BEFORE_STATE, PERSON_PREPOSITIONS, CONJUNCTIONS, BETWEEN_STATE_AND_NOUN,
    TIME_FILLERS, MOOD_TAIL, MOOD_TAIL_WORDS, MOOD_TAIL_TAKEN, _without_mood_tail,
    _last_subject_pos, _last_subject, PARTICLE_STATES, COPULA_STATES, NOUN_STATES, SUPPLY_WORDS,
    SUPPLY_PREPOSITIONS, OWN_RESERVES, DEGREE, DETERMINERS, MOTION_WORDS, TIME_AFTER_A_PARTICLE,
    _particle_is_a_place, _a_direction, MANIPULATE, COPULA, _copula_before, _noun_reading,
    _thing_turned_down, NUMBER_WORDS, EVENT_NOUNS, _is_person, _names_a_thing, RELATIVE_SUBJECTS,
    _names_somebody_else, _whose_state, BE_FORMS, ECHO_CARRIERS, _echoed_state, _carried_over,
    _state_owner, _about_a_supply, shortage_of, BOT_LIFE, BOT_LIFE_FILLER, BOT_LIFE_ASK,
    ITSELF_LONG, ITSELF_LIFE, _how_long_itself, ITSELF_WHEN, ITSELF_WHEN_TAIL, _when_itself,
)
from .kinds_part_04 import (  # noqa: F401
    BOT_DOINGS, BOT_COUNTED, COUNT_OPENERS, BOT_HAVE, BOT_CHATS, BOT_DOERS, COUNT_FILLERS,
    _counts_its_own_doings, _a_count_of_chats, _the_doer_is_the_bot, _asks_about_its_experience,
    EXPERIENCE_ASK, EXPERIENCE_WORDS, THEIR_PROBLEM, KIN, A_YOUR_KIN, A_YOUR_OWN_THING,
    A_HOW_MANY_OF_THE_BOTS_OWN, A_WHAT_ITS_LIKE, _asks_about_its_own_life, JOIN_OPENERS,
    A_PERSON_AFTER_A_POSSESSIVE, LEARNING_WORDS, A_HAVING, CHILD_NOUNS, POSSESSIVE_WORDS,
    MAKER_WORDS, _the_bots_own_not, _I_SAID_IT, _recalls_their_own_line, _self_ask,
    _asks_if_the_bot_is_a_product, _starts_with, BEFORE_COURTESY, without_filler, COURTESY_THING,
    _a_thing_named_after_the_courtesy, _after_thanks, the_line_after_a_courtesy, NEEDS_ANSWER,
    STILL_WRONG, FOUND, SLIPPED_FROM, FALL, FELL_WORDS, _a_fall, GREETING_TAIL, INTRODUCES,
    _after_greeting, after_greeting, FAREWELL_TAIL, _SAID_ON_ITS_OWN, _THANKS_WORDS, _NIGHT_WISHES,
    _WISH_WORDS, _after_farewell, farewell_only, greeting_only, NAMING_WORDS, _says_what_they_are,
    _a_name, HELP_WAS_GOOD, BEFORE_HELP_WAS_GOOD, AFTER_HELP_WAS_GOOD, AFTER_HELP_WAS_GOOD_SAID_OUT,
    _says_the_help_was_good, _thanks_only, THANKS_ABOUT, BETTER, SAYS_ABOUT_YOU, PRAISING,
    PRAISING_VERB, PRAISE_SAID, TURNED_ROUND, STEP_VERBS, STEP_ANY_OBJECT, STEP_WRONG, SIGNING_OFF,
    _a_clause_of_its_own, _a_step_done, _the_step_went_wrong, _a_fall_that_is_not_one,
    _praises_the_thing, AGREE_TAIL, AGREE_AFTER_NOT, NOT_FILLER, THANKS_NOISE, ADDRESSED, _agrees,
    _ends_with_thanks, OPENING_FRAME, OPENING_WORDS, OPENING_MAX, TALK_ASK_VERBS, TALK_TAIL_WORDS,
    TALK_ASK_OPENERS, TALK_OPENING, TALK_HEAD, TALK_TAIL, _talk_opening, talk_frame,
)
from .kinds_part_05 import (  # noqa: F401
    _about_bot_kind, opening_line, _short_reply, COMMIT_OPEN, COMMIT_TRY, COMMIT_SUBJECT,
    COMMIT_ALONE, COMMIT_ALONE_TAIL, HEDGED_COMMIT, HEDGED_ALONE, COMMIT_NO_HARM, HEDGE_LEAD_ONE,
    HEDGE_LEAD_TWO, NO_HARM_SUBJECT, COMMIT_STOP, _cant_for_cannot, _agrees_to_try, ASK_THE_ROOM,
    ASK_THE_ROOM_ANY, ASK_THE_ROOM_WANTS, ASK_THE_ROOM_VERB, _asks_the_room, TAIL_ASKS,
    TAIL_ASK_FILLER, SETUP_MOST_WORDS, SETUP_NOTHING, SETUP_CONNECTIVES, FRAME_NOT_A_SETUP,
    A_FRAME_IN_FRONT, _says_nothing_but_the_floor, TIPS_FRAME, QUESTION_NOUNS, ASKING_VERBS,
    ASK_ABOUT, ASK_FRAMES, PAST_ASK, ALREADY_ASKED, ASK_MODALS, ASK_AUX, ASK_TARGET,
    HAND_OVER_VERBS, HAND_OVER_TO, HAND_OVER_MINE, HAND_OVER_LEADS, HAND_OVER_MODALS,
    HAND_OVER_SUBJECTS, _hands_a_question_to_the_speaker, _asks_a_question_coming, _asks_for_tips,
    YOU_WORDS, ASK_VERBS, ASK_FOLLOW, _asks_the_bot, ANY_ANSWER_WANTED, ANY_ANSWER_LINKS,
    ANY_ALREADY_ASKS, after_any_link, _asks_after_any, _names_a_person, ASK_FOR_A_NAME, COMPARATIVE,
    DESCRIBES, AFTER_COMPARATIVE, A_PERSON_AFTER, A_PERSON_NAMED, OWNS_A_PERSON, COMPARISON,
    ASKS_IT_BACK, FILLER_BEFORE, FILLER_AFTER, BOUT, _ask_words, _asks_it_back, GREETING_ASK_WORDS,
    GREETING_ASK_SUBJECT, GREETING_ASK_STATE, GREETING_ASK_ABOUT_SOMETHING,
    GREETING_ASK_SECOND_PERSON, GREETING_WHAT_SAYING, asks_how_i_am, TAG_RIGHT_NOT, TAG_ENDINGS,
    TAG_PLAN, TAG_TIME_NUMBER, TAG_CHECKABLE, _tag_tells_a_plan, _tag_checks_a_fact, BOT_DAY_WORDS,
    BOT_DAY_SHAPES, _asks_about_the_bot_day, ASKS_IF_ANYTHING, SPENDS_ITS_TIME,
    _asks_how_it_spends_its_time, ABOUT_AT_A_TIME, FREE_OR_BUSY, FIRST_PERSON, MANNERS_WORDS,
    _asks_whether_the_bot_is_about, MANNERS_OPENERS, WHEN_IN_THE_ASK, SAYS_WHAT_ARE_YOU,
    KEEPS_BUSY_SHAPE, the_manners_question, NEW_ASK_WORDS, NEW_FRAME, NEW_ASK_AHEAD,
    _asks_what_is_new_with_the_bot, _asks_what_the_bot_is_doing, _asks_what_the_bot_has_been_doing,
)
from .kinds_part_06 import (  # noqa: F401
    emotion_of, _about_bot, _asks_at_the_end, the_setup, _opens_question, _asks_for_confirmation,
    _wants_a_recommendation, GRATITUDE_OBJECT, GRATITUDE_JOINERS, GRATITUDE_ASK_AGAIN, TIP_WORDS,
    COURTESY_WORD, _the_thing_a_thank_you_is_for, _asks, A_DATE_FIGURE, _a_bare_definition,
    _ask_labels, NOUN_REQUEST_MAX, PLACE_WORD, NOUN_REQUEST_SELF, VERBISH, BARE_VERBS, VERB_FORMS,
    _third_person, VERB_THIRD, PAST_AUX, _verb_form, noun_phrase_request, INTEREST_HEAD,
    INTEREST_NOT, INTEREST_TAIL, STARTED_OUT, BACK_INTO, taking_up, WH_CONTINUES, NOT_A_SUBJECT,
    SUBJECT_OF_ITS_OWN, _bare_subject, _continues_the_sentence, NEGATORS, NEGATION_SKIP,
    DENY_BETWEEN, DENY_BEFORE, denied, _a_state_of_the_speaker, SUMMONS_WHO, SUMMONS_WHO_PHRASES,
    SUMMONS_SEE, SUMMONS_WRITTEN, LETTER_RECEIVED, LETTER_ASKED_FOR, LETTER_SOMEONE_ELSES,
    LETTER_ITSELF, SUMMONS_RANG, SUMMONS_CALL_DONE, SUMMONS_SAID, SUMMONS_WANTS, SUMMONS_VERB,
    SUMMONS_NOT, _asks_for_it_rather_than_got_it, _a_letter_someone_else_got, summons_of,
    _said_to_somebody, STOMACH_WORDS, BODY_STATE_WORDS, _a_body_not_a_mood, BACK_AT, BACK_JOIN,
    BACK_ASKING, BACK_NOT_A_SUBJECT, BACK_AFTER, _asks_what_was_meant, MEANT_APPLIED_TO, _asks_back,
    says_how_they_are, VERDICT_NOUNS, COPULAS, VERDICT_FILLER, VERDICT_ADJECTIVES, PRONOUN_SUBJECT,
    ASKING_SUBJECT, NOT_A_THING, a_bad_verdict, verdicts_a_thing, _polarity, _thanks_still_asks,
)
from .kinds_part_07 import (  # noqa: F401
    PICKING, TO_A_VERB, SAYS_WHAT_IT_IS, OPENS_A_FRAME, PICKING_QUALITY, _only_the_ask, classify,
    ROUTINE_SHAPE, ROUTINE_IS_A_FAULT, ROUTINE_IN_THE_PAST, _ROUTINE_SUBJECT, SHIFT_LATE,
    SHIFT_EARLY, SHIFT_NIGHT, shift_worked, A_REPORTED_VERB, A_SUGGESTED_CLAUSE, A_TOLD_TO,
    A_NOT_A_SUGGESTION, A_SAID_BY, A_SAID_BY_ANYONE, _a_suggestion_from_someone, is_a_routine,
    CARE_HOME_PLACE, CARE_HOME_NOT, CARE_HOME_KIN, CARE_HOME_MOVED, CARE_HOME_VISIT,
    CARE_HOME_GUILT, CARE_HOME_BRING_ASKS, CARE_HOME_BRING_WORD, CARE_HOME_BRING_WHO,
    a_home_carried_forward, a_care_home, _MONEY_NOUN, _A_PRICE_ASK, _A_POST_HOLDER,
    _A_HOW_MUCH_I_SPENT, _A_MY_OWN_FIGURE, _MONEY, _UNITS, _UNITS_BOUGHT, _A_AN_AMOUNT_OF_A_THING,
    _A_A_CONVERSION, _A_HOW_MUCH_OF_A_UNIT, _A_THE_CLOCK, _A_HOW_MUCH_IT_HOLDS, _A_HOW_MUCH_ENOUGH,
    _A_HOW_MUCH_IS_IN, _A_HOW_MUCH_A_FEELING, _A_ARITHMETIC, _A_HAS_A_NUMBER, _A_A_DIFFERENCE,
    _A_DID_YOU_SEE, _A_BARE_RECORD, _A_PAST_YEAR, _A_HISTORY_ITSELF, _A_HOW_A_THING_MEASURES,
    _A_A_TRAFFIC_LIGHT, _A_A_PLAN_ABOUT_THE_WEATHER, _A_WEATHER_HERE, _A_HOW_OLD_IS_THE_WORLD,
    _MONEY_ASKED, _MONEY_FOR, _A_PLACE_THAT_KEEPS_HOURS, _A_LINE_THAT_NAMES_A_PLACE,
    _NOT_A_FITTING_THAT_OPENS, _A_DAY_WORD, _NOT_OPEN_TO_SOMEBODY, _HOURS, _WEATHER, _NEWS,
    _AVAILABILITY, _TIMETABLE, _A_SERVICE, _A_DAY_OR_TIME, _AServiceOnADay, _A_SERVICE_STATE,
    _SERVICE_ON_A_DAY, _RATE, _EVENT, _A_FRESHENING, _CHANGING, _A_HOW_IT_WORKS, _A_MY_OWN_PLAN,
    _A_AN_OCCASION_OF_THEIR_OWN, _A_SAYS_NOW, _A_HOW_MANY, _A_COUNT, _A_RECORD, _A_DEFINITION,
)
from .kinds_part_08 import (  # noqa: F401
    _A_WORKING, _A_HISTORY, _A_MEASURE, _A_MADE_OF, _A_METHOD, _A_WORD_MEANS, _SETTLED,
    _SEALED_ASKS, _ASKS_WITH_A_QUESTION_WORD, _ASKS_MID_LINE, _ASKS_AFTER_A_COMMA,
    _ASKS_AFTER_A_COMMA_WORD, _ASKS_WITH_AN_AUXILIARY, _A_REPORTS_THE_ASK, _a_line_asks, _as_typed,
    _carried_on, _text, _BARE_LIVE_LEAD, _A_BARE_LIVE, _A_REPORTS, _A_BARE_ASK, _A_BARE_LIVE_WORDS,
    _A_FOLLOW_UP_WORDS, _A_BARE_TAIL, _A_DETERMINER, over_time,
)
