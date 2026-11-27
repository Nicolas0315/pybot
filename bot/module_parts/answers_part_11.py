"""Part 11 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""

# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..understanding.kinds import ANSWERING_A_QUOTED_ASK
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from .answers_part_02 import (
    WHO_IS_THE_BOT,
)
from .answers_part_10 import (
    respond,
)


def claims_instead(text, memory=None):
    """The arbiter's `CLAIMS_INSTEAD`: a line asking how to answer somebody else's question.

    "how do i answer what are your weaknesses" is the interview question said out loud, and the
    composer reads the words in it as a question to the bot about itself, so the identity card
    takes the turn as it comes and the person is told the bot has no news and no clock. The
    knowledge base has the interview answer, so the module says the line is its own answer - only
    where it really is: the frame is narrow, the bare identity ask is left alone, and a line the
    knowledge base cannot answer keeps its turn.
    """
    if not isinstance(text, str) or not ANSWERING_A_QUOTED_ASK.search(text):
        return False
    if WHO_IS_THE_BOT.search(text) or not isinstance(memory, dict):
        return False
    try:
        return respond(text, memory) is not None
    except Exception:  # noqa: BLE001 - no claim is better than a broken turn
        return False


CLAIMS_INSTEAD = claims_instead
