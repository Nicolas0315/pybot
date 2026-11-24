"""Maths and numbers: fixed facts as entries, and computed answers for real questions.

Most maths questions carry their own numbers ("what's 15% of 80", "120 miles at 60 miles an
hour", "how many days in February"), so a canned entry cannot answer them. This domain has
two halves:

- ENTRIES for facts that never change (weeks in a year, a prime number, pi).
- solve(text, understood, memory) for questions that need arithmetic. It only answers when
  the line clearly contains a calculation, and returns None otherwise, so ordinary lines with
  a number in them are left to the other domains.

bot/modules/answers.py calls solve() before looking for a static entry.

The implementation lives in the `maths_part_NN` parts (in bot/knowledge_parts); this module keeps the header
imports and re-exports every name the parts bind, so `maths.<name>` is what it was.
"""
import ast
import operator
import re
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

from ..memory.saving import a_rate_put_right, the_money_already_held, the_pot_said_alone
from ..memory.topics import in_a_safety_thread
from ..knowledge import units
from ..knowledge.lookup import entry

from ..knowledge_parts.maths_part_01 import (  # noqa: F401
    ANSWERS, MONTHS, _NUMBER, _number, _parse, _BIN_OPS, _UNARY_OPS, _eval, _expression, _calc,
    _root, _roots, _prime, _FRACTIONS, _COUNTS, _COUNT, _PART, _AMOUNT, _FRACTION_UNITS, _SINGULAR,
    _CUP_IN_TBSP, _CUP_IN_ML, _FRACTION_OF_FRACTION, _FRACTION_OF_A_FRACTION, _as_fraction,
    _fraction_text, _fraction_of_a_fraction, _fraction_of, _share_reply, _A_COUNT, _COUNT_VALUE,
    _count_value, _share, _dec, _fraction_decimal, _exact_decimal, _fraction, _FRACTION, _PLACES,
    _reduced, _simplify, _add_fractions, _factors_in_list, _said_list, _the_factors,
    _common_factors, _NEAREST, _round_to, _places, _circle_measure, _box_volume, _MATHS_WORDS,
    _QUADRATIC_ASK, _FACTOR_ASK, _factorised, _gcd, _said, _quadratic, _equation, _percent,
    _percentage_change, _amount,
)
from ..knowledge_parts.maths_part_02 import (  # noqa: F401
    _what_percent, _a_share_of_a_group, _percent_on, _PERCENT_UP, _PERCENT_DOWN, _PERCENT_ADVICE,
    _MONEY_WORD, _percent_rise, _PERCENT_ASK_TAIL, _PERCENT_ASK_WORD, _amount_in_the_chat,
    _percent_of_the_figure_in_the_chat, _tip, _YOU_LEFT, _YOU_LEFT_ANYWHERE, _BILL_WORD, _A_NOTE,
    _two_places, _left_on_the_bill, _save_time, _PAY_WORDS, _NOT_PAY, _RATE, _HOURS_WEEK, _ANNUAL,
    _MONEY_BESIDE, _money, _annual_pay, _wage, _travel, _PACES, _A_PACE_WORD, _DISTANCE,
    _AFTER_HALF, _distance_in_miles, _duration, _TO_WORK, _A_DISTANCE_STATED, _IS_THAT_TOO_MUCH,
    _the_size_of_the_trip, _the_way_it_is_done, _at_a_pace, TIME_ASKED, WHAT_IF, ABOUT_ASK, CLOCK,
    TAKES, A_HORIZON, TIME_ELSEWHERE, RATE, MONEY, TOWARDS, CLAUSE_SPLIT, SAVING_CLAUSE,
    SPENDING_CLAUSE, OWED, A_DEBT_CLEARED, _rate_clause, PERIODS, _user_lines, _a_rate_was_said,
    _rate_in_chat, SAID_A_RATE, WORKED, _worked_in_chat, _TENS_WORDS, _WORD_THOUSANDS,
    _NUMBER_THOUSANDS, _K_THOUSANDS_HERE, _MONEY_HERE, _sums, _in_months, _duration_reply,
    _asks_a_new_sum, _last_takes, _SMALLER_PERIOD, _each_hundred,
)
from ..knowledge_parts.maths_part_03 import (  # noqa: F401
    _goal_in_chat, _rate_and_total, _time_to_reach, _time_at_a_new_rate, _time_at_a_new_total,
    _time_without_a_goal, MONEY_GOAL, _a_saving_goal_in_chat, _the_plan_figure, ASKED_FOR_RATE,
    _a_goal_without_a_rate, ASKED_FOR_FIGURE, JUST_A_TOTAL, _a_new_total_only, _figure_just_given,
    HOW_MUCH_EACH, A_BARE_RATE_ASK, EACH_PERIOD, PERIODS_IN_A_YEAR, DEADLINE_NAMED, GOAL,
    _each_month_for_a_goal, HORIZON_SAID, HORIZON_COUNTS, PAST_REPORT, DEADLINE_DAYS, MONTH_NUMBERS,
    K_THOUSANDS, A_DATE_FOR_THE_THING, SAVE_VERB, SAVING_CUE, _k_as_money, _easter_day,
    A_DEADLINE_DAY, _the_last_day_of, _a_named_deadline, _save_by_a_date, _a_total_by_a_date,
    _a_month_for_the_deadline_in_chat, _deadline_for_a_goal, _asked_period, _a_deadline_in_chat,
    _saving, _average, _LENGTH_UNIT, _LENGTH, _SIDE, _SIDE_BY_SIDE, _SQUARE_WORD, _AREA_ASK,
    _PERIMETER_ASK, _sides, _SHAPE, _AREA_TARGET, _METRES_SQUARED, _SURFACES, _surface,
    _square_text, _COUNTED_GAP, _COUNTED, _BOUGHT_BY_THE_BAG, _BUYING, _floor_area,
    _perimeter_of_a_room, _area, _MONTH_TAIL, _month_year, _leap, _CHRISTMAS_TAIL, _CHRISTMAS_DAY,
    _christmas_name, _christmas_date_of, _CHRISTMAS_COUNTDOWN, _CHRISTMAS_DATE, _WEEKDAYS,
    _CHRISTMAS_WEEKDAY, _CHRISTMAS_TODAY, _CHRISTMAS_FIXED,
)
from ..knowledge_parts.maths_part_04 import (  # noqa: F401
    _days_in_month, _christmas_day, _wait_text, _months_between, _count_in, _shopping_days,
    _countdown_text, _days_until, _weekday_text, _EASTER_OFFSETS, _MONTH_NAMES, _ASK_DATE,
    _DATE_TAIL, _easter_sunday, _feast_year, _COUNT_ASK, _COUNTED_EVENT, _MONTHS_SAID, _MONTH_SHORT,
    _MONTH_WORD, _DAY_MONTH, _month_number, _DAY_ONLY, _day_in_a_month, _date_the_line_gave,
    _SMALL_NUMBER, _HOW_FAR, _month_on, _first_of_the_month, _relative_day, _relative_count_text,
    _days_until_a_relative_day, _date_counted_from_today, _days_until_a_named_day,
    _REST_OF_A_PERIOD_WORDS, _REST_OF_A_PERIOD, _days_left_in_the_month_or_the_year, _SINCE_ASK,
    _SINCE_FILLER, _A_YEAR_IN_THE_LINE, _year_the_line_gave, _how_long_ago, _WORKING_ASK,
    _WORKING_LEFT, _a_known_day_the_line_names_next, _WORKING_SHAPE, _a_working_week,
    _a_known_day_that_has_gone, _nth_weekday, _NAMED_DAYS, _SEASONS, _COUNTED_SUBJECT_TAIL,
    _THE_TURN_OF_THE_YEAR, _BANK_HOLIDAY_TAIL, _BANK_HOLIDAY_NEXT, _BANK_HOLIDAY_COUNT,
    _BANK_HOLIDAY_LIST, _SAYS_WEEKDAY, _MONTHS_OR, _ordinal, _the_wider_day, _last_weekday,
    _bank_holidays, _BANK_WHERE, _bank_where, _said_with_a_weekday, _POLITE, _FILLER,
    _WEEKDAY_WORDS, _MONTH_TITLE, _TODAY_ASK, _day_text, _short_date, _weekday_of, _plain,
)
from ..knowledge_parts.maths_part_05 import (  # noqa: F401
    _convert, _working_days_or_weekends_until, _days_until_easter, _named_day_date,
    _days_until_a_month_or_season, _the_weekday_of_a_date, _next_bank_holiday, _today, _UNITS,
    _UNIT, FACTS, _TAILS, _HOW_MUCH, HOW_HEAVY, _HEAVY, _unit_pair, _unit_fact, _WAGE, _WAGE_UNIT,
    _AN_HOUR, _HOURS_WORKED, _WAGE_CUE, _WAGE_CONTEXT, _hours_a_week, _hourly_named, _yearly_named,
    _pounds, _rate, _a_yearline, _wage_rate, solve, _AVERAGE_FILLER, _AVERAGE_EXPLAIN,
    _MEDIAN_EXPLAIN, _MODE_EXPLAIN, _figures, _short, _MEAN_VERB, _STATISTIC_WORDS,
    _OTHER_STATISTICS, _POINTS_AT_A_THING, _names_a_statistic, _about_words, _averages,
    ROUND_IS_NOT_THE_VERB, _ROUND_IS_AROUND, ROUNDING_NAMED, _a_rounding_question,
)
from ..knowledge_parts.maths_part_06 import (  # noqa: F401
    _rounding_is_the_ask, _round_is_the_verb, _FREE_TIME_ASK, _A_LENGTH_OF_TIME, _A_PAY_WORD,
    _not_a_spare_hour, PRIME_DEFINITION, PRIME_TEST, _prime_definition, ENTRIES, _DEFINITION_ASK,
    MATHS_DEFINITION_ASK,
)
