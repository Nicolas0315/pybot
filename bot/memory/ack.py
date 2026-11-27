"""Say back the thing they just told you, in their own words.

A person who says "my sister is called Meg" or "we're flying to Rome on Monday" is handing you
something. A friend answers with the thing itself - "Meg, got it" or "Rome on Monday, nice" -
not one stock line for every line ("Noted!") and not a question at the end every time either.
The store is what makes the echo possible; the person's own words are what make it fit.

bot/modules/memory_store.py asks this after its recall answers, and only for a line that is
telling the bot something. Every rule here is a guard against taking a turn that is not that:

* only a statement - never a question, a request, a greeting, a thanks or a "yes"
  (bot/understanding's kind, in memory["understood"]);
* only when the line gave the store a fact (bot/memory/facts.extract found one), or when it adds
  a detail to the thing we are already on ("i work from home" after a question about naps), so
  small talk the bot merely heard is never echoed back;
* never a greeting or a self-introduction, because the chat module answers "Nice to meet you,
  Tom" better than an echo can;
* never a line with a feeling, a loss or good news in it: those belong to the modules that
  answer them, and "your dad died in March - noted" would be awful. The caller passes only
  lines whose mood is neutral, and bot/compose/loss.py and bot/compose/badnews.py are asked
  here as well, so a kind reply always wins over an echo;
* never a body that hurts, a fit or a wound ("your dog choked on a bone - noted" says nothing
  about the dog), and never a birthday nobody reached ("your mum would have been 70 - noted");
* the echo is short: the first clause or two of what they said, cut at a word, so the reply
  matches the line instead of repeating it.

The frames vary through bot.compose.pick, so the bot does not say "noted" three times running.

The implementation lives in the `ack_part_NN` parts (next to this file); this module keeps the header
imports and re-exports every name the parts bind, so `ack.<name>` is what it was.
"""
import re

from ..compose import loss, negated, pick, trouble
from ..compose.badnews import reads_as_bad_news, reads_for_a_pet, reads_like_a_symptom
from ..compose.goodnews import reads_as_good_news, reads_as_settled, worry_on_the_table
from ..understanding import understand as understanding
from ..understanding.kinds import SHIFT_EARLY, SHIFT_LATE, VERBISH
from ..understanding.topics import NUMBER_WORDS
from ..understanding.normalize import (LEFT_OFF_CONTRACTION, LEADERS,
                                       opens_without_subject,
                                       without_a_leading_exclamation)
from . import last_user, there_is_a_chat
from . import opening
from . import you as say_it_back
from . import facts, hours as hours_after, named, narrow, not_a_trip, taste, topics
from . import stuck as stuck_line
from .facts import DAYS, MONTHS, a_limit_on_the_plan
from .relations import _person_from_pronoun, _pronoun_fits
from .store_lines import CHILD, PERSON_GROUP

from .ack_part_01 import (  # noqa: F401
    FACTS, EXPLAIN_TAIL, HAVE_THING, NOT_A_THING, AN_AIM, A_FEELING_ABOUT_IT, SOMEONE_GOOD,
    SOMEONE_TAIL, SOMEONE_COMING, NOT_A_VISIT, VISIT_TAIL, SOMEONE_MILESTONE,
    SOMEONE_MILESTONE_TAIL, A_SECOND_PERSON, A_BIRTHDAY_TOLD, A_PLAN_VERB, A_DATE_TOLD, _a_relation,
    _the_pronoun, _the_ages_held, _people_in_chat, a_person_named_alone, _the_question_about,
    A_POINTED_AT, a_person_pointed_at, _how_many_people, _the_people_pointed_at, _an_age_held,
    _the_person_pointed_at, a_second_person, A_PERSON_ALONE, WHICH_ONE, A_GROUP_ALONE, A_POSITION,
    A_POSITION_MAYBE_A_THING, A_POSITION_LINES, A_PERSON_ALONE_LINES, A_KNOWN_AGE_LINES,
    A_TWO_ALONE_LINES, A_GROUP_ALONE_LINES, FRAMES, STILL_TO_DO, NOT_ONE_THING,
    THE_LIMIT_GOES_FIRST, _A_PLAN_WAS_GIVEN, _the_last_reply_gave_a_plan, _a_limit_on_the_plan,
    DAY_SOON, DAY_BEEN_AND_GONE, A_DOING, A_FIGURE, A_DOING_TURNED_DOWN, DAY_JUST_A_STATE, DAY_FAR,
    A_DAY_ASKED, NOT_A_DAY_TO_LOOK_FORWARD_TO, SOON_TAIL, FAR_TAIL, SORRY_TAIL, _a_day_coming,
    _SAID_BACK, _SENTENCE, _SPACED_DASH, reads_as_a_receipt, _one_frame, WORK_FRAMES, WORK_PLACE,
    HABIT_TAIL, GOING_TAIL, TRIP_TAIL, OCCASION_TAIL, PET_TAIL_ONE, PET_TAIL_MANY,
    OCCASION_FLAT_TAIL, DIARY_WORDS, DIARY_THING, DIARY_TIME, DIARY_TAIL, DIARY_TIME_TAIL,
    MEETING_TAIL, MEETING_TIME_TAIL, COMING_TO_STAY, VISIT_TAIL_ONE, VISIT_TAIL_MANY, PLURAL_KIN,
    A_COMING_WORD, _more_than_one_coming, OCCASIONS, SHOWER, PLACES_WITH_THE,
)
from .ack_part_02 import (  # noqa: F401
    THING_BEFORE, PAST_PLAN, TRIP_VERB, DESTINATION, ARRIVE_VERB, DESTINATION_ARRIVAL, NOT_A_TRIP,
    DATE_AHEAD, DREADED_OCCASION, HOW_LONG_ALREADY, reads_as_a_trip, HABIT, GOING, OBLIGED, FEELING,
    GOING_BAD, BUDGET_FRAMES, PERIOD, A_SPAN_OF_TIME, FOR_A_THING, BUYING, MONEY, SPENDING_FRAMES,
    FOOD_FRAMES, DRINK_FRAMES, CONDITION_FOOD, CONDITION_FRAMES, OTHER_LIMIT_FRAMES, LIMIT_FRAMES,
    A_STAY_PLAN, A_TRIP_PLAN, A_STAY_PERSON, _the_plan_in_hand, _LIMIT_ONLY, _OPENS_WITH_AN_ASK,
    LIKES_FRAMES, A_LIKE_OF_ONE_THING, A_LIKE_ECHO, A_LIKE_WITH_TWO_HALVES, A_PERSON_LIKED,
    _only_a_liking, a_liked_thing, _AN_ABILITY, PLAN_TURNS, WANTS_IT, _a_plan_on_the_table,
    SAID_BACK_WORDS, LIMIT_AFTER_THE_LINE, UP_CLOSED, LEFT_CLOSED, SEPARATION, HEAVY_TURNS,
    _NOT_A_BODY_PART, _BULLIED, HURTS_A_PERSON, A_NAME_WAS_VIOLENT, reads_as_cruelty, HEAVY_FRAMES,
    STILL_FRAMES, LEAD_IN, WANTS_ANSWER, GREETING, DEATH_WORDS, ON_NIGHTS, EARLY_RISE, LATE_FINISH,
    LONG_SHIFT, SHIFTS_ALL_OVER, WORK_FROM_HOME, NIGHT_TAIL, EARLY_TAIL, LATE_TAIL, LONG_TAIL,
    SPREAD_TAIL, HOME_TAIL, AN_ASK, reads_as_an_ask, NOT_THE_HOURS, WHEN_DETAIL, WHEN_TODAY,
    WHEN_TOMORROW, WHEN_DAYS, COUNTED, COUNT, _shape_of, WHEN_TODAY_TAIL, WHEN_TOMORROW_TAIL,
    WHEN_DAYS_TAIL, WHEN_ROOMY_TAIL, TIME_WORD, CLOCK_DETAIL, CLOCK_AT, CLOCK_MORNING_TAIL,
    CLOCK_AFTER_TAIL, CLOCK_EVENT, CLOCK_FLAT, CLOCK_FLAT_TAIL, CLOCK_WORDS, _clock_shape,
)
from .ack_part_03 import (  # noqa: F401
    STEP_OPENS, _tells_them_what_to_do, WOULD_HAVE_BEEN, BODY, BODY_STATE_WORDS, BODY_STATE_PHRASES,
    BODY_STATE_TAIL, _a_bare_state, BLEED, SELF_INTRO, MEET_GREET, SUBJECT, STOP, WORD, POLITE,
    TAIL_OFF, without_filler, STATE, TROUBLE, _EMPTY, _FEELING_WORDS, A_FEELING, GOOD_MOOD, A_EVENT,
    A_CLEAR, A_RESULT, A_MOVED, has_news, COMPLAINT, _NOT_A_DETAIL, _SAID_YES_NO, _ANSWER_OPENER,
    _ASKS_MIDWAY, _ASKED_FOR, DIGIT, _FAULT, _NOT_A_DETAIL_SUBJECT, FRAGMENT, WITH_SLASH,
    DURATION_UNITS, TWO_TO, TWO_PLACE, TWO_VERB, SPEAK, ITS_OWNS_AFTER, SHORT, YES_AFTER, CLAUSES,
    MOST, _repaired, CORRECTED_WITH_UNIT, CORRECTED_ALONE, VALUE_UNIT_WORDS, VALUE_UNIT_GLUED,
    A_MEASURE, WHOLE_FREQUENCY, _the_values_measures, _the_units_measure, _the_unit_is_said_twice,
    PUT_RIGHT_LEAD, PUT_RIGHT_TAIL, _without_a_frame, _without_a_not, _the_bare_value,
    _without_a_unit_already_in_the_value, _the_line_before, GIVEN_AWAY, GIVEN_ANIMAL, NOT_THEIRS,
    GIVEN_AWAY_REPLIES, _the_animal_given_away, pet_given_away, OFFERS_A_CHAT, CHAT_OFFER_REPLY,
    _offers_a_chat, A_DATE_ALONE, A_MONTH_ALONE, A_WEEKDAY, A_DATE_ON_A_PLAN, A_DAY_ON_A_PLAN,
    A_WORRIED_ABOUT_IT, A_DATE_ON_A_HARD_PLAN, A_DAY_ON_A_HARD_PLAN, A_MILESTONE,
    _the_plan_a_date_belongs_to, _a_date_on_the_thing_in_hand, _after_the_hello, REMARK_BACK,
    REMARK_EXPENSE, REMARK_STILL_TO_COME, REMARK_ALREADY_PAID, REMARK_LONG, REMARK_BETTER,
    REMARK_HARD, REMARK_WORK, REMARK_GONE, GROWING, REMARK_REPLIES, REMARK_PRICE_AHEAD,
    REMARK_TWO_SIDED, REMARK_JUDGES_THE_PRICE, REMARK_FIGURE, REMARK_FIGURE_REPLIES, REMARK_KINDS,
    _a_hand_back,
)
from .ack_part_04 import (  # noqa: F401
    _a_price_still_to_come, _a_result_is_on_the_table, _HOLE, _NOT_WORDS, _ending_of, _pick_ending,
    PERSON_WORDS, A_REASON_MARKER, NO_REASON, A_CLAUSE_OF_ITS_OWN, AN_AGE_ALONE, _after_a_feeling,
    _a_heavy_reply_just_before, THE_STORY_GOES_ON, THIRD_PERSON, LENGTH_TAIL, SINCE_TAIL,
    LENGTH_KEEPS, THE_OLD_ONE, REPLACING, OLD_ONE_TAIL, the_old_one_aged, _the_length, _the_hours,
    _a_deadline, _an_hour_on_the_day, THE_NOUN_IS_AT, A_MARKED_HOUR, _the_figure_is_an_hour,
    _a_clock_time, _hours_family, AS_WELL, A_CHILD_IN_THE_LINE, PET_ADDED, PET_ALL_RIGHT,
    _a_pet_that_is_all_right, INTRODUCED_BEFORE, A_NAME_AFTER, _nothing_added_but_the_pet,
    A_VAGUE_MANY, ANIMAL_TAKEN_BACK, A_WANTED_ANIMAL, A_WANT_TURNED_DOWN, A_HAD_AN_ANIMAL,
    ANIMAL_HAD_ONCE, A_PET_WANTED, A_WANTED_ANIMAL_TAIL, _a_wanted_animal, _an_animal_wanted,
    _an_animal_they_had_once, PET_WORD, ANIMAL_COMING, PET_TAIL_COMING, PET_TAIL_COMING_MANY,
    _the_pets_are_coming, _the_animal_coming, _the_taken_back_animal, _an_animal_turned_down,
    _on_record, WISH_FOR_AN_ANIMAL, A_BREED_BEING_CHOSEN, _an_animal_only_planned,
    _the_wished_animal, _only_a_wish, _an_animal_taken_back, _the_pets_said, _about_them,
    NOBODY_AROUND, NOBODY_AROUND_ASK, ANYBODY_AT_ALL, OTHER_PERSON, GOING_HOME, ON_THE_MEND,
    BACK_AT_IT, GOING_HOME_TAIL,
)
from .ack_part_05 import (  # noqa: F401
    _a_remark_on_what_was_said, ON_THE_MEND_TAIL, BACK_AT_IT_TAIL, GOING_HOME_MINE,
    ON_THE_MEND_MINE, BACK_AT_IT_MINE, A_RELATION, _who_is_getting_better, a_person_getting_better,
    _the_words_of_the_last_two_turns, _with_the_time, A_MOVE, ALONE_AFTER_A_MOVE, ALONE_TAIL,
    ALONE_AFTER_A_LOSS, nobody_around, _WORDS, _THE_BOT_AS_SUBJECT, _SOMEONE_ELSE_IN_IT,
    _said_to_the_bot, _no_subject, _asked_last, _a_diary_plan, _plan_tails, PLACED_IN_THE_PAST,
    _about_a_body, JOB_TO_DO, JOB_HAS_A_DAY, JOB_TAIL, JOB_BEFORE, PAST_JOB, PAST_JOB_PLAIN,
    the_job_they_had, WHO_THE_FIGURE_IS, WHO_IS_IT, WHAT_OF_THEM, WHICH_ONES, POINTS_BACK,
    A_COUNT_OF_THEM, A_DATE_STILL_TO_COME, _the_chat_holds_something,
    _the_pronoun_points_at_somebody, _somebody_was_being_hurt, _who_the_figure_is,
    _what_the_pointer_is, A_WONDERED_CONDITION, A_WONDER_SAID_NO, WITH_AN_ARTICLE, A_CONDITION_KIND,
    CONDITION_INITIALS, CONDITION_FAMILIES, _the_route_for, _the_entry_names,
    _a_condition_they_wonder_about, RAISED, _a_spending_budget, THEIRS, _about_someone_else,
    _a_visit, _the_milestone, _a_workplace, FAMILY, _about_the_family, _just_a_liking, _heavy,
    _statement, _a_loss, _children_with_ages, _children_said, _adds_one_more_allergen, REPAIR_FRAME,
    _words, VAGUE, _names_nothing, _OPENS_WITH_A_LINK, MONEY_ONLY, _repairs,
)
from .ack_part_06 import (  # noqa: F401
    _the_unit_before, _bad_news_just_before, carries_the_story_on, _learned, _adds_a_detail,
    KIN_POSSESSIVE, A_COUNT_NOT_A_STATE, UNITS_OF_MEASURE, WHOS, _says_something, NO_REFERENT,
    POINTS_AT_ANOTHER, A_DECISION, REPORTS_AN_ACTION, POINTER_FILLER, NOT_A_THING_TO_HAVE_ANOTHER,
    ANOTHER_ONE, ANOTHER_ONES, BEFORE_ONE, SOMEONE_ELSE_POINTS_AT_ANOTHER,
    PRONOUN_POINTS_AT_ANOTHER, ANOTHER_ONE_FOR_SOMEONE, ANOTHER_SOME_FOR_SOMEONE,
    _the_person_the_pointer_is_about, _the_thing_the_chat_is_on, A_NAME_GIVEN,
    _a_name_the_store_holds, _something_they_avoid, _plural, ENDS_THE_THING_VERB, _is_a_contraction,
    A_DETERMINER, ENDS_THE_THING, NOT_A_SECOND_OF, _a_thing_the_line_named, _a_loss_just_before,
    _another_of_what_we_said, _only_the_correction_in_front, HAVE_GOT, HAVE_A, _only_a_dislike,
    only_a_dislike, _tells_it, _a_diet, FIGURE_LEAD, FIGURE_FILLER, FIGURE_UNIT, FIGURE_WORD,
    _only_the_figure, A_CONTINUATION, A_CLAUSE, A_SOMEONE, _the_rest_of_a_question,
    the_rest_of_a_question, NO_THEN_A_LINE, NO_THEN_A_LINE_ONLY, NO_LEAD, REACTION_PHRASES,
    REACTION_WORDS, _REACTION_CLAUSE, _after_a_reaction, _strip_lead_in, without_the_frame,
    COUNTED_STARS, ONE_STAR, STAR_COUNT, COUNTED_LETTERS, LETTER_COUNT, A_DEGREE, DEGREE_CLASS,
    _spoken, CONTRAST, CONTRAST_SAID_AGAIN, NOT_A_VALUE, PICK_FRAME, _pick_off, _tail_off,
    A_REASON_TAIL, A_CORRECTION_IN_FRONT, _reason_off, BETWEEN_VALUES, VALUE, MAKE_A_VALUE,
    VALUE_WORDS, UNITS_AFTER,
)
from .ack_part_07 import (  # noqa: F401
    _a_like_of_one_thing, a_limit_reply, _a_limit_reply, a_limit_for_the_plan, value_put_right,
    reply, _the_opening_instead, _what_a_wanted_animal_needs, _plain, a_job_to_do, _a_job_to_do,
    _a_thing_they_have, _frames, _echo, said_back, _contrast_off, _the_value_put_right, _a_value,
    _cut, FIRST_WORD, _tidy,
)
