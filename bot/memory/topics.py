"""What the conversation is about: the current topic and the topics before it.

The conversation lane owns this. bot/modules/memory_store.py writes it in observe(), so every
lane can read it:

- memory["topic"]: {"turn", "text", "words"} for what the user is talking about now. "text" is
  the user's own line, so a follow-up can be understood in context; "words" are its content
  words, for matching.
- memory["topics"]: every topic so far, oldest first, so "back to the laptop" and "which city
  did I say first" can be answered.
- memory["return_to"]: set when the user clearly goes back to an earlier topic.

Helpers for answer modules (import bot.memory as memory):
- memory.current(memory) -> the topic record or None
- memory.expand(text, memory) -> the line, plus the topic in brackets when it is a follow-up
- memory.is_follow_up(text, memory) -> True for "how long will it take?", "and if I stuff it?"

The implementation lives in the `topics_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `topics.<name>` is what it was.
"""
import re

from ..understanding import lexicon
from ..understanding.kinds import NEGATIVE, POSITIVE
from .filler import without_the_shrug
from . import quotes as quoted

from .topics_part_01 import (  # noqa: F401
    WORD, STOPWORDS, ACKS, GREET, REFERRING, ORDERING, ABOUT_ANOTHER, PART_OF_THE_ONE,
    CONTINUATION_START, MEASURE_WORDS, PROPERTY, KIND_ASK, SWITCHERS, RETURN_LEAD, CASUAL_LEAD,
    CASUAL_OPEN, CASUAL_VERB, RETURN_TIME, RETURN_ASKS, words, stem, keywords, NOT_DOING, ENDINGS,
    forms, content, is_ack, is_small_talk, _a_place_the_line_moves, _asks_about_the_bot,
    _the_record_they_came_back_to, _back_to, AIM_FRAME, A_DEADLINE, ASPECT_OF_IT,
    ASPECT_IS_A_PRONOUN, OWN_THING, _names_a_place_of_its_own, JOINS_THE_THING, ABOUT_THE_PERSON,
    PRONOUN_PERSON, MEASURE, _a_part_of_the_record, _switches, _LEADS_IN, CORRECTION_NOISE,
    DETAIL_WORDS, A_THING_ON_ITS_WAY, NAMES_THE_THING, FRESH_NAMES, MY_THING_IS, SHORTHAND,
    RECENT_TURNS, FRESH_WORDS, WHEN_OR_AMOUNT, NAMED_THING, CONSTRAINT_IS, ON_A_BUDGET, WHO,
    WHO_SAID, WHO_SAID_THIRD, A_BARE_PRONOUN_SUBJECT, A_QUESTION_THEY_ASK, about, PERSON_TROUBLE,
    YOUNG_PERSON, FELL_OUT, FALLS_FINE, A_JOB_AT, SOMETHING_WRONG, CHANGE, A_WORRY_AFTER,
    A_CHILDS_PERSON, A_GROWN_AGE, REPEATED_SAID, _after_an_emergency, CORRECTION_LINE,
    INSIDE_A_SAFETY_THREAD, in_a_safety_thread, WH_WORD_WITHOUT_ITS_APOSTROPHE, HELPER_ASKS,
    ING_VERBS, VERB_PHRASE_AFTER, MODALS, the_thing_asked_again, the_thing_went_back_to,
    _the_answer_on_the_return, resumed, current, _forms, alike, find, LEAD_ACKS, _this_line,
    context, MEASURED, PROCEED, ASK_ONLY, _LEAD_QUESTION, _RELATION, _FRAME_ASK, _WITHOUT_CLAUSE,
    _VERBS, _WISH, _ACTION, _PHRASAL, _PHRASAL_RE, _gerund, _VERB_WORDS, _WISH_RE, _LEAD,
    _CORRECTION_LEAD, _TIME_WORDS, _CONSIDERING, _BUYING_A_STATE, _A_FIGURE, _HANDOFF_THROAT,
    _DATE_OCCASIONS, _DATE_FILLER, _MAKING_A_THING, _PEOPLE, _the_people, _ROOM_LIMIT, _HOME_SPACES,
    DURATION_ASK, DURATION_WORDS, ACTION, PERSON_LEAD, ACTION_AFTER, ONE_ATTRIBUTE, ATTRIBUTE_WORDS,
    NOT_A_THING, A_STATE, DETAIL, ASK_PART, PRICE_ASK, ASKS_FOR_ADVICE, CAUSE_OF_THE_COMPLAINT,
    REFERRING_WORDS, DUMMY_IT, ASK_MORE, STAND_IN, ABOUT_THE_CHAT, ASK_CUE, ELIDED_ASK, SAME_ASK,
    COUNTING, THE_TAIL, LONG_IT_TAKES, TOPIC_OPENS_WITH, STAY_ASK, STAY_ONLY, TRIP_FRAME,
    LIVES_THERE, POINTING_WORD, A_BARE_MEASURE,
)
from .topics_part_02 import (  # noqa: F401
    _what_they_are_not_doing, _the_aim_without_its_deadline, _asks_which_kind,
    _asks_an_aspect_of_the_thing, _names_a_thing_of_its_own, _only_adds_a_person_to_the_thing,
    _another_area, _leans_back, _leads_a_question, opens_by_switching, _without_switchers,
    _only_details, _the_plan_a_correction_renames, _is_a_quantity, _is_a_when_or_how_often,
    _only_names_the_constraint, _adds_a_detail, person, _named_inside_a_question, person_named,
    trouble, _keep_person, _after_a_correction, _the_apostrophe_back, return_target,
    _a_question_after_the_thing, _the_thing, _asks, asks_after, _resume, is_follow_up, expand,
    _MAX_SUBJECT, _strip_considering, _only_a_handoff, _a_word_of_a_date, _only_a_date,
    _the_thing_after_a_date, gist, _room_limit, _thing_of, _about_record, _names_nothing, subject,
    topic_text, MAX_ACTION, _the_action_word, action, written_out, _named_a_thing,
    _the_thing_on_the_table, attribute_of_the_thing, key_subject, _the_part_a_complaint_is_about,
    _the_cause_words, _key_subject, _said, _entry,
)
from .topics_part_03 import (  # noqa: F401
    _reaches_another_thing, _a_detail_of_what_we_are_on, _subject_words_to_carry,
    _where_the_topic_lands, an_entry_for, _the_last_question, how_much_of_the_thing_in_hand,
    elided_ask, names_nothing, _content_words, _the_topic_phrase, _a_length_of_the_job, the_city_of,
    the_country_of, asks_how_long_to_stay, going_there, a_stay_with_the_place,
    _the_ways_of_saying_it, A_VERDICT, _the_last_answer, _the_topics_on_the_chat,
    _the_thing_a_measure_is_of, _with_the_word_before, _how_they_feel, _keyed_to,
    _a_measure_of_the_topic, ADVICE_ONLY, _the_ask_with_its_doing, the_advice_ask_with_its_doing,
    _the_answer_covers_it, ABOUT_A_BARE_THING, _with_the_article, A_FREQUENCY,
    _only_said_as_a_frequency, PROPERTY_ASK, _asks_a_property_and_nothing_else,
    _elided_situated_cache, _an_elided_ask_situated, ABOUT_NAMED, _ABOUT_TAIL_PRONOUN,
    ABOUT_MOST_WORDS, DEFINITE_OPEN, ANSWER_OPENING, _the_same_answer_again, follows_on, keeps_away,
    _kept_away_from, _names_it, _key_words_of, _names_it_as_written, _asked_only,
    _the_step_they_report, CONSTRAINT, CONSTRAINT_FILLER, adds_only_a_constraint,
    _constrains_the_ask, SENTENCE, JOINED_ON, NUMBER, TIME, AMOUNT, AMOUNT_ANSWER, RATE,
    RATE_BY_WEIGHT, OWN_SIZE, PLUS_MINUTES, WEIGHT_IN_GRAMS, TIME_SPAN, DURATION, SPAN_ADJECTIVE,
    LENGTH_ASK, THRESHOLD_SPAN, CLAUSE, ASIDE, SHIELD, _clauses_of, WARNING_SPAN, FREQUENCY,
    NOT_A_QUANTITY,
)
from .topics_part_04 import (  # noqa: F401
    HYPOTHETICAL, ANSWER_KEPT, remember_answer, entry_answer, ACKED_IN_BETWEEN, answer_in_hand,
    newest_answer, REPEAT, REPEAT_LEADS, _carries, ACK, WARM_ACK, ACK_COURTESY, A_CLOSE,
    CLOSE_FILLER, _only_a_close, SHORT_TURN, only_acknowledges, LOOK_BACK, _hands_the_subject_back,
    FIGURE, POINTS_AT_THE_ANSWER, _the_opening_of, said_again, _said_later_than,
    _the_turn_we_lean_on, _the_turn_that_answered, _ASKING_VERBS, _answer_about, answer_about,
    _the_trip_of_theirs, the_place_they_are_on, about_a_place_they_left_behind, ASKS_A_FREQUENCY,
    ADVICE_ASK, ADVICE_NAMES_A_THING, PAIRING, PAIRING_OWN, pairing, IMPERATIVE, SENDS_YOU_ON, WHEN,
    _doing_word, _opening_instruction, RED_FLAG, ASKS_THEM_BACK, _says_it_again, A_CEILING_ASK,
    A_CEILING_WORD, _A_RATE, _the_rates_in, _a_rate_that_fits, _a_comma_that_ends_a_clause,
    _pick_amount, said_on_its_own, AFTERWARDS, TOTAL, _time_of, OPTION, _option_range, QUOTE_MARK,
    _quoted, OPTION_ANY, TIME_ONLY, _only_a_marker, _duration_clauses, _only_a_cadence,
    A_WEATHER_WINDOW, _a_window_in_the_weather, _not_a_length, _duration_clause, _shorten, PERIODS,
    PERIOD_ASK, PERIOD_LEAD, _asked_period, FIGURED, _in_period, _step_they_asked_for,
    _time_in_words, time_for_amount,
)
from .topics_part_05 import (  # noqa: F401
    the_thing_the_subject_brings, _a_sky_ask, _doing_part, _pick_sentence, _the_sentence_it_answers,
    _the_option_for_the_topic, _pick_duration, _already_for_this_size, _in_grams,
    _names_another_thing, sized_reply, _sized_reply, _times_asked, _rate_said, _phrase, has_time,
    _worked_out_for_this_line, _ASKS_WHAT_I_AM, asks_only, _earlier_subject_sentence,
    _repeats_the_question, already_said, STEP_ASK_WORDS, _names_something_new, REQUEST_A_THING,
    A_THING, _named_a_fresh_thing, MOVED_KEEP, _the_thing_the_chat_moved_to, left_for_a_blank,
    POINTS_BACK, A_QUESTION, _a_question, BARE_ASK, BARE_WORDS, bare_question,
    ASKS_ABOUT_THEMSELVES, _still_the_topic, carried_topic, _only_the_topics_own_words, NEXT_SLOT,
    ASK_SLOT, ASK_WORDS, next_slot_reading, TWO_PETS_ASK, PET_WORD, PET_ONE, PET_ARRIVING,
    PET_EXISTING, _introduction_covered, introduction_question, WEATHER_WORDS, MONTH_NAMES,
    WEATHER_NOISE, NOW_AND_HERE, WEATHER_ASKS, the_weather_ask, the_place_and_month,
)
from .topics_part_06 import (  # noqa: F401
    _names_another_subject, _points_at_the_record, carry_the_ask, _carry_the_words, widen,
    same_as_before, leans_on_topic, PERIOD_ONLY, SEASONS, _the_period_in,
    _a_period_and_nothing_else, the_period_they_ask_about, _the_answer_was_about_the_weather,
    _the_place_the_chat_is_on, _with_the_period, MEAL_NAMES, MEAL_ONLY, OPENS_A_FOLLOW_UP,
    _the_meal_in, _a_meal_and_nothing_else, the_meal_they_ask_about, meal_follow_up, _with_the_meal,
    the_weather_of_the_trip, A_TRIP_TAKEN, _the_trip_said, _the_lines_said, THING_ITSELF,
    IT_IS_PART_OF_THE_PHRASE, BABY_OF, WHAT_IT_COSTS, WORTH_DECIDING, PLACEHOLDER_PRONOUN,
    A_NEW_ONE, a_placeholder_pronoun, the_ask_about_the_thing_it_points_at, POINTING_WORDS,
    WITHOUT_A_DETERMINER, _the_thing_with_a_determiner, SOMETHING_IS_BROKEN, THEIR_OWN,
    NOT_THEIR_OWN, _SMALL, _what_they_called_theirs, NAMES_THE_RUNNING, _the_entry_answers_the_ask,
    _the_entry_is_about_the_thing,
)
from .topics_part_07 import (  # noqa: F401
    _note, the_pronoun_written_as_what_it_stands_for, the_thing_it_is,
    _the_things_the_pronoun_stands_for, WHAT_IT_IS_LIKE, WHAT_STANDS_IN, STANDS_IN, MONEY, YES_NO,
    PROGNOSIS, the_prognosis_the_line_asks, HOW_LONG_KEY, _keyed_on_how_long,
    _the_thing_as_a_question_names_it, the_property_of_the_thing, LIKE_LOOKUPS, LIMIT_ASK,
    THE_LIMIT_ITSELF, THE_LIMIT, the_limit_of_the_thing, _the_limit_written_out, _a_doing_word,
    _fills_from_the_things, _fills, HE_OR_SHE_OPENS, ASKS_HOW_EARLY_THERE, A_FLIGHT_IN_THE_TOPIC,
    THE_AIRPORT, the_airport_there_is, the_animal_the_subject_is, CHILD_CARE, _the_kind_of_animal,
    answers_about_another_creature, _called, _the_pet_the_turns_before_named,
    a_detail_of_the_thing_we_hold, _the_kind_the_line_leaves_out, the_thing_a_detail_belongs_to,
    the_pet_the_line_before_named, KEEP_IT_UP, STAYING_WITH_IT, AN_ACTIVITY, _carrying_on,
    LIMIT_LINE, _what_the_turn_took_away, _widened, _the_length_of_the_aim,
)
from .topics_part_08 import (  # noqa: F401
    GATHERING_WORDS, TOO_SOON_TO_COOK, FOR_SOMEBODY, PUTTING_ON, _a_gathering_read_as_the_food,
    _the_whole_topic, ASK_SHAPE_WORDS, _the_answer_is_about_what_the_line_names,
    _already_answered_here, _how_much_of_the_thing_the_entry_uses, _the_things_the_chat_named,
    followup_reading, WORDS_THIS_TURN, TURN_TOPIC, note, _the_reply_to_the_turn_before,
    _the_step_back_is_undone, _the_words_before_the_turn, _the_records, _the_words_this_turn,
    _a_step_back, _the_detail_steps_back, the_step_back_takes_its_words_back,
)
