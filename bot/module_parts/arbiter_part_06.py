"""Part 6 of 6 of a large module, split out of `arbiter`.

Everything here is re-exported from `arbiter`, so callers import it from there as before.
"""

from .arbiter_part_01 import (
    _a_past_that_is_not_there, _seed,
)
from .arbiter_part_04 import (
    _an_answer_it_already_gave,
)
from .arbiter_part_05 import (
    _choose,
)


def choose(text, memory, candidates):
    """Return the index of the chosen candidate.

    candidates: [{"module": name, "priority": PRIORITY, "reply": text}], highest PRIORITY
    first. memory["turns"] holds the earlier turns of the conversation.
    """
    try:
        index = _choose(text, memory, candidates)
    except Exception:  # noqa: BLE001 - the arbiter must never lose a turn
        index = _seed(candidates)
    index = _a_past_that_is_not_there(index, candidates, text, memory)
    return _an_answer_it_already_gave(index, candidates, text, memory)
