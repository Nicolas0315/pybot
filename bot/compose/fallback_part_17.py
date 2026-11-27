"""Part 17 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""






def nothing_yet_line():
    """The line for a first line whose every candidate answers a turn that never happened."""
    return RETURNED_TO_IT_FIRST[0] if RETURNED_TO_IT_FIRST else ""


# The readings this file used to hold - the day that went badly, the plan that did not happen, the
# name that came from somebody - now live in fallback_chain.py with the rest of the rows, and the
# pools they choose from live in fallback_data.py. Both are re-exported here, at the end and after
# the rest of the file's own imports, so `fallback.X` still finds every one of them.
from .fallback_chain import (  # noqa: F401, E402 - after the rows above, as the import at the top is
    A_DAY_SAID_BADLY, A_NAME_A_HOUSEHOLD_TAKES, A_NAME_IS_NOT_A_DAY, A_NAMES_TOLD,
    A_POSSESSIVE_OF_MINE, NOT_A_NAME_WORD, NAMED_AFTER,
    BARE_STATE, BOT_WAS_SORRY, PLAN_THAT_FELL_THROUGH, RESULT_WENT_WRONG, STATE_IN_THE_PAST,
    STATE_NOT_A_DOING, STATE_THEN,
    _a_bad_time_told, _a_day_asked_without_a_cheer, _a_day_said_badly, _a_detail_of_a_bad_day,
    _a_name_told, _a_name_told_reply, _a_small_day_shape, _a_state_of_theirs,
    _named_after_reply, _the_day_was_already_bad, _the_last_exchange,
)


from .fallback_data import (  # noqa: F401, E402 - the pools those readings choose from
    A_BAD_TIME_TOLD, A_DAY_ASKED_PLAIN, A_NAME_STORY, A_NAME_TOLD, A_NAMED_AFTER,
    A_NAMED_AFTER_THEM, A_PLAN_THAT_FELL_THROUGH, A_STATE_NOW, A_STATE_PAST,
    A_THING_CAME_OUT_WRONG,
    # `nothing_yet_line` reads this pool and the split above left it in the data file, so the
    # name was read here and bound nowhere: `tests.test_no_undefined_names` went red on main and
    # the module would have raised if that line were ever asked for.
    RETURNED_TO_IT_FIRST,
)
