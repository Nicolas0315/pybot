"""Part 6 of 6 of the module, split out of `repeat`.

Everything here is re-exported from `repeat`, so callers import it from there as before.
"""
import re

from ..compose import pick
from . import counts, history, recall, topics
from .repeat_part_01 import (
    HEDGE,
)
from .repeat_part_02 import (
    _sentences, framed,
)
from .repeat_part_03 import (
    A_GOAL_LINE, A_RATE_LINE, GOAL_NOUNS, ASK_FRAME, A_DOING_WORD, A_IM_ON_A_FIGURE, A_MEASURE_WORD,
    A_PAY_JUDGEMENT, A_PAY_VERB_AT_THE_END, A_PAY_WORD, A_TAKE_HOME, FIGURE_ASKS, FIGURE_NOUNS,
    GAVE_ASKS, PAY_WHEN_WORDS,
)
from .repeat_part_05 import (
    A_LINE_THAT_ASKS, _figures_in, _one_figure, _the_corrected, _the_same_word, A_BARE_AMOUNT_ASK,
    A_BARE_DURATION_ASK, A_CORRECTION, A_PLAN_ASK, A_RATE_IN_THE_FIGURE, A_THE_PLAN_ASK,
    A_THING_NAMED_AFTER_THE_CUE, A_TOLD_BACK, COUNT_ASK, GAVE_LOOK_BACK, NOT_A_FIGURE_ASK,
    PERIOD_WORD, _a_bare_count, _a_count_of_one_with_a_plural, _a_list_of_ages,
    _money_paid_for_a_thing, _something_gone, _the_ask_gave_that_figure, _the_length_they_mean,
    _the_thing_counted, the_plain_line,
)


def _the_figure_of_a_goal(lines, kind, wanted=()):
    """The figure on the line where the person set a goal, or () when there is none.

    A goal is the amount they are trying to reach, so a rate they put by is skipped even though
    it is a figure of the same kind. Where the line states both an amount and a length ("save
    8000 over two years") and the ask names neither ("what was my target again"), the amount is
    the target and the length is how long it takes. A word the ask adds besides the goal noun
    ("the van", "savings") narrows which goal it is, so the line has to carry it too.
    """
    for at, line in enumerate(lines):
        if not line or A_LINE_THAT_ASKS.search(line) or not A_GOAL_LINE.search(line):
            continue
        if A_RATE_LINE.search(line):
            continue
        words = topics.keywords(line)
        narrowing = [word for word in wanted if word not in GOAL_NOUNS]
        if not all(any(_the_same_word(word, other) for other in words) for word in narrowing):
            continue
        found = _one_figure(_figures_in(line), kind)
        if not found and kind is None:
            found = _one_figure(_figures_in(line), "amount")
        if found:
            # A later line that puts the goal right is the goal: "i need 20 grand" / "make it
            # 30" / "what was my target again" is the 30.
            return _the_corrected(lines, at, kind, found)
    return ()


def _the_figure_counts_the_thing(text, figure):
    """True when a figure is an answer to an ask that names a thing, or the ask names nothing.

    A number answers a number's question, and an ask that names the thing it wants back is not
    one: "what did i say about lisbon", asked after "im saving 3000 for a trip to lisbon" and
    "the flights are about 120 each", was answered "You said 3000." - a figure given two lines
    after the thing the ask named, with nothing on it to say what the figure is of. The same
    shape answered "what did i say about the tap" with "About a week", a length from a line about
    something else.

    So the figure comes back only when it carries the thing asked about ("what did i say about
    the cats" after "i have two cats" is "two cats"). When it does not, the answer is the line
    that names the thing, chosen by the one check in bot/memory/history.py and quoted below.
    """
    thing = history.the_thing_they_named(text)
    if not thing:
        return True
    named = set(topics.content(thing))
    return bool(named & set(topics.content(str(figure or ""))))


# A line that narrows or qualifies the one before it and says nothing on its own. It is short, and
# its thing is the thing in the line above it: "the ones that are open on sunday", "the cheaper
# ones", "ones open late", "closed ones too", "not too scary", "something shorter", "since
# tuesday", "wide ones". Each is a person narrowing the answer in front of them, not a fact about
# them, and quoted on its own it is their fragment with nothing in it.
A_NARROWING_ONLY = re.compile(
    r"""^(?:(?:ok|okay|and|or|also|but|then|so|just|only|maybe|actually)[\s,]+)*
        (?:
            (?:the|those|these|any|some|other|both|all)(?:\s+[a-z']+){0,3}\s+(?:one|ones)
          | (?:one|ones)
          | [a-z']+\s+(?:one|ones)
          | (?:something|anything|everything)\s+[a-z']+
          | (?:not|no)\s+(?:too|very|that|so|more|as)\s+[a-z']+
          | (?:a\s+bit\s+)?(?:cheaper|closer|nearer|bigger|smaller|longer|shorter|quicker|faster|
                easier|simpler|warmer|colder|quieter|lighter|nicer|better|worse)\b
          | (?:since|before|after|from|until|till|by|around|near|in|on|at)\s+[\w' ]{1,24}
        )
        (?:\s+[a-z']+)*
        \s*[.!]?$""", re.I | re.X)


# How long a line can be and still be a narrowing: past seven words it carries a thing of its own
# ("the ones that are open on sunday and deliver, place at the corner of the high street").
A_NARROWING_WORDS = 7


def a_narrowing_and_its_line(line, memory):
    """The line `line` narrows, with `line` after it, or None.

    A recall finds the line that carries the word asked about, and the last one can be a narrowing
    of the line above it: "any chemist in the area" / "the ones that are open on sunday", then
    "what did i say about sunday". The only line with "sunday" in it is the narrowing, so the
    answer was `You said: "the ones that are open on sunday"` - their own fragment, which says
    nothing about them and nothing about the chemist either. What they are asking about is the
    line the fragment narrows, so it is said with the narrowing after it.

    The narrowing must be the line *right after* the one it narrows: a short line three turns
    later is about whatever that turn was about. It must be a narrowing on its own terms (see
    `A_NARROWING_ONLY`), so "i bought new tyres" is never read as one, and the line it narrows
    must state a thing - a question narrowed is the chat still looking for the thing.
    """
    said = " ".join(str(line or "").split())
    if not said or "?" in said or len(said.split()) > A_NARROWING_WORDS:
        return None
    if not A_NARROWING_ONLY.match(said):
        return None
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return None
    lines = [" ".join(str(turn.get("user") or "").split()) for turn in turns
             if isinstance(turn, dict)]
    places = [at for at, text in enumerate(lines) if text == said]
    if not places or not places[-1]:
        return None
    before = lines[places[-1] - 1]
    if (not before or "?" in before or len(before.split()) < 2
            or not topics.content(before) or A_NARROWING_ONLY.match(before)):
        return None
    return before, said


def _the_turn_that_names_it(text, memory):
    """The line they said about the thing the ask names, quoted back, or None."""
    row = history.the_earlier_turn(memory, text)
    line = " ".join(str((row or {}).get("user") or "").split()).rstrip(" .!?")
    if not line:
        return None
    pair = a_narrowing_and_its_line(line, memory)
    if pair:
        # "the ones that are open on sunday" alone says nothing: the thing asked about is in the
        # line it narrows, so both are said (`a_narrowing_and_its_line`).
        before, after = pair
        return pick(["You said: \"" + before + "\" \u2014 then \"" + after + "\".",
                     "Your own words were: \"" + before + "\", then \"" + after + "\".",
                     "That was: \"" + before + "\" \u2014 then \"" + after + "\"."], memory)
    return pick(["You said: \"" + line + "\"",
                 "Your own words were: \"" + line + "\"",
                 "That was: \"" + line + "\""], memory)


def the_figure_they_gave(text, memory):
    """The figure a person gave earlier and asks for again, or None.

    Only a line that asks for the figure back, names the thing it is for, and has that thing and
    the figure in the chat within the last few turns is answered. Everything else is left to the
    module that knows about the thing asked.
    """
    if not isinstance(memory, dict):
        return None
    clean = " ".join(str(text or "").lower().split())
    if not clean or len(clean.split()) > 16 or not GAVE_ASKS.search(clean):
        return None
    if NOT_A_FIGURE_ASK.search(clean):
        return None
    # A "how many" ask is a count, and the count store keeps counts as counts: "i have two
    # brothers and one sister" is filed as two numbers, so "how many brothers and sisters do i
    # have" is answered from both. Read here as a figure said back it returned only the first
    # number ("You said two brothers."), and the sister was dropped. Where the store holds the
    # count, the store's answer is the whole one. A count another reader keeps (children, cats)
    # is left to that reader, which knows the word the person used.
    counting = COUNT_ASK.search(clean)
    if counting:
        counted = counts.answer(clean, memory)
        if counted:
            return counted
        if any(word in counts.THEIRS for word in counting.group(1).split()):
            return None
    wanted = [word for word in topics.keywords(clean) if word not in ASK_FRAME]
    if A_PAY_WORD.search(clean):
        # "whats my current salary": the word after "my" says when the figure is wanted, not which
        # figure, and it is in no line they said, so it must not stand in the way of the pay word
        # that is. "whats my salary after tax" keeps "tax" and is still refused.
        wanted = [word for word in wanted if word not in PAY_WHEN_WORDS]
    if not wanted and A_PAY_WORD.search(clean) and A_PAY_VERB_AT_THE_END.search(clean):
        # "how much do i make" carries its pay in a word the keywords drop, so the ask named
        # nothing at all and the figure in the chat went unread: the family word stands in.
        wanted = ["pay"]
    if len(wanted) > 4:
        return None    # too much to be about one thing
    goal_named = any(word in GOAL_NOUNS for word in wanted)
    # "how many times a week" asks how often, and no count is that answer: the kind is read from
    # the most particular frame first, because "how many" alone would take a distance for it.
    kind = None
    for name in ("often", "time", "heat", "amount"):
        for one_name, ask, _figure in FIGURE_ASKS:
            if one_name == name and ask.search(clean):
                kind = name
                break
        if kind:
            break
    if kind in (None, "amount", "heat") and (A_PLAN_ASK.search(clean)
                                             or A_THE_PLAN_ASK.search(clean)):
        return None
    # The lines are read as the person typed them, so "were away for 3 nights" is a statement and
    # not a question: see `the_plain_line`.
    all_lines = [the_plain_line(str(turn.get("user") or "")) for turn in (memory.get("turns") or [])
                 if isinstance(turn, dict)]
    lines = all_lines[-GAVE_LOOK_BACK:]
    spoken = [str(turn.get("bot") or "") for turn in (memory.get("turns") or [])
              if isinstance(turn, dict)][-GAVE_LOOK_BACK:]
    # An ask that points back with the person's own words ("did i tell you", "what did i say") and
    # asks a length: the length they gave is the answer even when the thing named is not one of
    # the words on the line. "sorry, how long did i tell you the headaches been going on" after
    # "ive had a headache for four days" matched no line - the ask says "headaches", the line says
    # "headache", and "sorry" and "going" are the only other words - so the chat read the apology
    # and left the question. A length a person gives about their own life is theirs.
    if kind == "time" and A_TOLD_BACK.search(clean):
        said = _the_length_they_mean(clean, lines, spoken)
        if said:
            if not _the_figure_counts_the_thing(clean, said):
                return _the_turn_that_names_it(text, memory)
            return pick(["You said " + said + ".",
                         said[:1].upper() + said[1:] + " \u2014 that's what you told me."],
                        memory)
    if goal_named:
        # A goal is set once and asked about many turns later, so it is read from the whole chat
        # and not the last few lines: "i'm trying to save 8000 for a van", ten turns of other
        # talk, then "what was my target again" is still the 8000. The shorter window is for the
        # figures a line gives in passing, which a later line can take back.
        found = _the_figure_of_a_goal(all_lines, kind, wanted)
        if found:
            figure = found[1]
            return pick(["You said " + figure + ".",
                         figure[:1].upper() + figure[1:] + " \u2014 that's what you told me."],
                        memory)
    if wanted:
        # A word the ask adds after the figure it wants back is not the thing the figure is for:
        # "how many people did i say were coming" asks about the people, and "were coming" is the
        # rest of their own sentence. A word that is in no line they said cannot be what the
        # figure was given for, so it is dropped and the words that are in a line are the ones
        # looked for. With every word dropped the ask names nothing at all, and the bare shape
        # below decides whether one figure in the chat is the answer.
        said = [other for line in lines for other in topics.keywords(line)]
        # "take home" is the pay said in two words with no word of the family in it, and the two
        # are not a keyword the way "wage" is: the phrase stands for the family word.
        said += ["takehome" for line in lines if A_TAKE_HOME.search(line)]
        # "im on 2000 a month" is a wage with no word of the family in it. It is kept as one
        # so the ask for the pay is answered by it: the store files that line under the
        # budget, and "how much do i make" named nothing at all before this.
        said += ["pay" for line in lines if A_IM_ON_A_FIGURE.search(line)]
        kept = [word for word in wanted
                if any(_the_same_word(word, other) for other in said)]
        named = [word for word in wanted
                 if word not in A_MEASURE_WORD and word not in A_DOING_WORD]
        if named and not any(word in kept for word in named):
            # The ask named a thing of its own and no line holds it, so a measure is all that is
            # left to match on. A measure word says what kind of figure is wanted, never which
            # one: "how many days holiday do i get" after "we went to york for four days" asks
            # about the world, and four days is not its answer.
            return None
        if A_PAY_WORD.search(clean) and (A_PAY_JUDGEMENT.search(clean)
                                         or len(kept) < len(wanted)):
            # Pay is the one thing people ask about with a qualifier on it, and the qualifier is
            # the whole question: "how much do i get paid for overtime" and "whats my pay like"
            # and "how much do i pay for rent" name a figure this chat does not hold, and the
            # wage they gave is not the answer to any of them.
            return None
        if not A_THING_NAMED_AFTER_THE_CUE.search(clean):
            # Unless the words after the cue name a thing of their own: "the hall" is a thing
            # the ask is about, and a figure given for something else is not its answer.
            wanted = kept
    if _the_store_keeps_this_figure(clean, memory):
        # The store keeps the figure under the thing asked about, and its own recall of it is the
        # record the chat settled on. Answering from the scan here read the line before the
        # correction: "my budget is 500" / "change that to 650" / "what is my budget" answered
        # 500 while the store held 650, and the turn the store had answered properly was lost.
        return None
    if not wanted:
        # Names nothing at all, and asks a figure back - a length of time or an amount: one figure
        # of that kind in the chat is the one they mean, and two of them is a question of which.
        bare = (A_BARE_AMOUNT_ASK.search(clean) if kind == "amount"
                else A_BARE_DURATION_ASK.search(clean) if kind == "time" else None)
        if not bare:
            return None
        found = [(back, one[1]) for back, line in enumerate(lines)
                 if not A_LINE_THAT_ASKS.search(line)
                 for one in _figures_in(line) if one[0] == kind]
        distinct = {one.lower() for _back, one in found}
        if len(distinct) != 1:
            # They gave a length and then took it back: "my back has been bad for a week" /
            # "actually its been two weeks" / "how long have i had it now" was answered "Six
            # weeks." - the follow-up in the back answer - because two lengths in the chat read as
            # a question of which. A line that opens as a correction is the one they mean, and
            # only when it is the last length they said.
            corrected = [one for back, one in found if A_CORRECTION.search(lines[back])]
            if not corrected or found[-1][1] != corrected[-1]:
                return None
            figure = corrected[-1]
        else:
            figure = found[0][1]
        if not _the_figure_counts_the_thing(clean, figure):
            return _the_turn_that_names_it(text, memory)
        return pick(["You said " + figure + ".",
                     figure[:1].upper() + figure[1:] + " \u2014 that's what you told me."],
                    memory)
    best = None
    for back in range(len(lines) - 1, -1, -1):
        line = lines[back]
        if not line or A_LINE_THAT_ASKS.search(line):
            continue    # a question the person asked is not a line that gave a figure
        said = topics.keywords(line)
        if A_TAKE_HOME.search(line):
            said = said + ["takehome"]    # the same phrase, on the line being read now
        if A_IM_ON_A_FIGURE.search(line):
            said = said + ["pay"]    # "im on 2000 a month": a wage with no family word in it
        core = [word for word in wanted if word not in FIGURE_NOUNS] or wanted
        if not all(any(_the_same_word(word, other) for other in said) for word in core):
            continue    # the line does not say the thing the figure is for
        shared = [word for word in wanted
                  if any(_the_same_word(word, other) for other in said)]
        figures = _figures_in(line)
        found = _one_figure(figures, kind)
        if not found:
            continue    # no figure of the kind asked for on the line the thing was said on
        beside = _the_figure_beside_the_thing(figures, core)
        if beside:
            # The figure the line puts next to the thing the ask names outranks the first figure
            # on the line: two brothers and one sister is one sister when sisters is the ask.
            found = beside
        if COUNT_ASK.search(clean) and _a_list_of_ages(line):
            # A line that lists ages names the children one at a time, so its first number is not
            # how many there are. The store counts the list itself.
            continue
        if _money_paid_for_a_thing(clean, line):
            # The figure on this line is what the thing cost, not the thing the ask wants: see
            # _MONEY_PAID_FOR. The line is left to whoever answers about the thing itself.
            continue
        found = _the_corrected(lines, back, kind, found)
        if not found:
            continue
        many = _every_figure_the_ask_names(wanted, line, kind)
        last = (found[1].split() or [""])[-1]
        if _something_gone(lines, back, [word for word in said if word in shared] + [last]):
            continue    # the count they gave is not the count they have any more
        # More of the ask's own words on the line first, then the later line: a chat can hold two
        # figures of the same kind, and "how many days did i say i was off" after "we fly out for
        # 10 days" and "im off work for 5 days" asks about the one just said. The tie broke the
        # other way round - the earliest line won - and handed back the flight's 10 days.
        score = (len(shared), back)
        if best is None or score > best[0]:
            best = (score, found, shared, many)
    if best is None:
        return None
    _score, (kind_of, said, number, counted), shared, many = best
    if many:
        # Every figure the ask named, in the person's own words: "two brothers and one sister".
        return pick(["You said " + many + ".",
                     many[:1].upper() + many[1:] + " \u2014 that's what you told me."], memory)
    noun = _the_thing_counted(clean, said) if counted else ""
    if (counted and noun and noun.split()[-1].lower() in PERIOD_WORD
            and A_RATE_IN_THE_FIGURE.search(said)):
        # The thing they gave is a rate, and the ask names the period rather than the doing: the
        # count of weeks is not a fact, so the rate is said back in the doing's own words instead.
        return None
    if noun and number.lower() in ("1", "one") and noun.endswith("s") and not noun.endswith("ss"):
        noun = noun[:-1]   # "one kid", not "one kids"
    figure = (number + " " + noun).strip() if noun else said
    if _the_ask_gave_that_figure(number, clean):
        # A figure in the ask is the ask's own, not one they gave: "how many roast potatoes do i
        # need for 8" said back "8 potatoes - that's what you told me." about a line that said
        # eight *people*. The number the ask carries is what the ask is about, so it is not
        # evidence of anything they said, and the reading steps out of the way.
        return None
    if noun and _a_count_of_one_with_a_plural(number, noun):
        # "One people - that's what you told me." A count of one said back with a plural noun is
        # not a sentence anybody writes, and the reading cannot tell "one more is coming" from
        # one of the group: it steps out of the way and lets the store count the group itself.
        return None
    if not _the_figure_counts_the_thing(clean, figure):
        return _the_turn_that_names_it(text, memory)
    if _a_bare_count(figure):
        return pick(["You said " + figure + ".", figure + ", as you said."], memory)
    return pick(["You said " + figure + ".",
                 figure[:1].upper() + figure[1:] + " \u2014 that's what you told me."], memory)


A_FIGURE_WORD = re.compile(
    r"\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty"
    r"|thirty|forty|fifty|sixty|ninety|hundred|thousand)\b", re.I)


def _the_store_keeps_this_figure(clean, memory):
    """Whether the store keeps a figure under the thing this ask names.

    The figure reader is for the figures the store does not keep: it scans the lines the person
    said and works out which one the ask is about. A figure the store holds under a key is a
    different thing - the store's own recall says it, in its own words, and it is the record the
    chat settled on. "my budget is 500" then "change that to 650" leaves 650 under "budget", and
    the scan could only find the line that says the word, which is the one before the correction.
    So where the ask names a key the store holds a figure under, this reading steps out of the way
    and the store answers it.
    """
    if not isinstance(memory, dict):
        return False
    asked = set(topics.keywords(clean))
    if not asked:
        return False
    for entry in reversed(list(memory.get("facts_log") or [])):
        if not isinstance(entry, dict):
            continue
        value = " ".join(str(entry.get("value") or "").split())
        if not value or not A_FIGURE_WORD.search(value):
            continue
        key_words = topics.keywords(str(entry.get("key") or "").replace("_", " "))
        if not key_words:
            continue
        if not any(_the_same_word(word, other) for word in key_words for other in asked):
            continue
        said_on = str(entry.get("text") or "")
        if said_on and A_LINE_THAT_ASKS.search(said_on):
            continue    # a question is not a line that gave a figure
        return True
    return False


# The words that make a line a request for something said earlier rather than a question about the
# world: "how much was i putting away" asks back a figure of theirs, "how much should i save each
# month" asks me. `the_figure_they_gave` answers either shape, so this cue is what decides whether
# the store may take a turn the composer has already given a reply of its own to.
# The cue itself lives in bot/memory/recall.py (`looks_back`), one list for the whole bot, so a
# new wording of the same ask ("remind me how many nights") reaches this reader too. The name is
# kept for the importers that predate the move.
A_RECALL_CUE = recall.LOOKS_BACK


# A line that says out loud it is asking about the chat: "what did i say", "remind me how many
# nights", "what was my excess again". These carry their own proof, so they are read even when the
# thing named is not a word of the line they are answered from.
A_POINTS_BACK_HARD = re.compile(
    # "before" and "back to" are not here: they order things in time in an ask about the future
    # too ("how long before the move should i start"), and the line that says out loud that it is
    # about what was said is "again", "remind", "you said" and the rest of this list.
    r"\b(?:again|remind\w*|remember|recall|earlier|same\s+(?:again|one))\b"
    r"|\b(?:you|u)\s+(?:said|told)\b|\btold\s+me\b"
    r"|\bwhat(?:'s|s|\s+is|\s+are|\s+was|\s+were)?\s+(?:my|our)\b"
    r"|\bwhat\s+did\s+(?:i|we)\s+(?:say|tell)\b"
    # A first person with "be", "do" or "have" in the ask makes it about the person's own chat,
    # whatever the wording: "how many people am i catering for" asks about the 30 they just said,
    # where "how many people live in paris" has no first person and stays a question about the
    # world. A modal is advice and not a look-back: "how long before the move should i start" is
    # the packing, and their "6 weeks" is not the answer to it.
    r"|\b(?:am|are|did|do|does|was|were|have|has|had)\s+(?:i|we)\b", re.I)


def _the_figure_beside_the_thing(figures, words):
    """The figure the line says next to the thing the ask names, or None.

    A line can give a figure for each of two things - "i have two brothers and one sister" - and
    the first figure on the line is the wrong one to say back when the ask names the second:
    "how many sisters do i have" was answered "You said two sisters." A figure belongs to the
    words it is said with, so the phrase the store kept beside the number is where the thing the
    ask names is looked for.
    """
    for figure in figures:
        beside = topics.keywords(figure[1])
        if any(_the_same_word(word, other) for word in words for other in beside):
            return figure
    return None


def _every_figure_the_ask_names(wanted, line, kind):
    """Every figure the line gives for the things the ask names, said as one phrase, or "".

    "how many brothers and sisters do i have" names two kinds of thing, and the line that holds
    the answer - "i have two brothers and one sister" - gives a figure for each of them. Saying
    the first one back ("You said two brothers.") drops the sister, which is half the answer and
    wrong about the other half (deck row `how-many-02`). While the ask names more than one of
    them and the line gives a figure for each, they are all said back, joined the way the person
    joined them.
    """
    named = [word for word in wanted if word not in ASK_FRAME and word not in FIGURE_NOUNS]
    if len(named) < 2:
        return ""
    figures = [one for one in _figures_in(line) if not kind or one[0] == kind]
    if len(figures) < 2:
        return ""
    taken = []
    for word in named:
        for figure in figures:
            if figure in taken:
                continue
            if any(_the_same_word(word, other) for other in topics.keywords(figure[1])):
                taken.append(figure)
                break
    if len(taken) < 2:
        return ""
    parts = [figure[1] for figure in taken]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def asked_back(text, memory):
    """The figure a recall ask wants back, or None when the line is not one.

    `the_figure_they_gave` is only reached where the composer has nothing, so a recall ask the
    composer thinks it has answered was lost: "how much was i putting away" was met with "I can't
    look up live prices, sorry" and "what was my excess again" with "That is everything I have on
    that one, so I would only repeat myself" - while the 400 and the 100 were in the person's own
    lines. The cue keeps a question about the world out: "how much should i save each month" is
    not asking me what they said, and their 200 is not the answer to it.
    """
    if not isinstance(text, str) or not isinstance(memory, dict):
        return None
    if not recall.looks_back(text):
        return None
    if not A_POINTS_BACK_HARD.search(text) and recall.the_earlier_turn(text, memory) is None:
        # The cue list is shared with every other reader now, so it holds the weak cues too: "how
        # many people live in london" and "how much coffee is too much" point back at nothing and
        # were answered "You said 30 people live." The line has to name something a line already
        # carries, unless it says out loud that it is asking about what they said.
        return None
    figure = the_figure_they_gave(text, memory)
    if figure:
        return figure
    # A count asked about the job rather than about the people ("how many am i cooking for again",
    # two turns after "a roast for 8 people on sunday") names nothing the chat said - "cooking" is
    # in no line they typed - so the figure reader above declines, and the ask went to a menu card
    # that shares the word "cook" with it. The count of the people is a figure they gave, and it is
    # read where every other count is read (`bot/memory/counts.py`), so an ask the store can answer
    # is a recall ask here too: one reading of what was said, whichever file holds it.
    try:
        from . import counts as _counts
        said = _counts.answer(text, memory)
    except Exception:  # noqa: BLE001 - a reader that fails is no ask
        return None
    return said or None


def carries_the_figure(figure, reply):
    """Whether a reply already says the figure the person asked back.

    A reply that names it answered the ask, whatever else it says; one that does not is the
    composer making conversation about a question it did not answer, and the figure is the answer.
    """
    said = str(reply or "")
    numbers = re.findall(r"\d[\d,]*", str(figure or ""))
    if numbers:
        for number in numbers:
            if not re.search(r"(?<![\d,.])" + re.escape(number) + r"(?!\d)", said):
                return False
        return True
    words = [word for word in topics.keywords(figure) if not word.isdigit()]
    low = said.lower()
    return bool(words) and all(word in low for word in words)


# The same question, in the same words, later in the chat. People do this all the time: they ask
# something, get an answer, talk about something else for a turn or two, and ask it again - and by
# then the pronouns in it point at whatever was said last, so the reading is of the wrong thing.
# "im sam, i want to run a half marathon in october" / "how many weeks is that away" (46 weeks,
# in October) / "i get a sore knee after about 3k" / "how long will that take to get better" /
# "how many weeks is that away" - and the last line, word for word the second, came back "I don't
# know enough to answer that honestly": the "that" was read as the knee, the store stood down, and
# the only candidate left was the fallback. Nothing in the chat contradicted the answer of 46
# weeks, so the honest reply is that answer again.
#
# Narrow on purpose: the line has to be the earlier line's own words (so a new question that
# merely shares a subject is read on its own), the earlier answer has to be a real answer rather
# than a hedge or a question, at least one turn has to have gone by (a line repeated straight
# away is "did you hear me", answered by `SAY_AGAIN_LEADS`), and nothing said since may have
# changed the thing the answer was about ("actually we've moved it to the 21st" ends it, because
# the old answer would then be a wrong fact rather than a helpful one).
#
# The wording it comes back in is `topics.said_again`'s ("Same as before: ..." and the two after
# it), not a lead-in of this module's own: see `_the_answer_again`.
#
# A line that changes the thing an answer was about. Any of these between the two asks ends the
# repeat: the earlier answer is then about a plan that is no longer the plan.
CHANGED_IT = re.compile(
    r"\b(?:actually|instead|changed|change of plan|moved it|moved to|now it'?s|now we'?re|"
    r"no longer|swapped|postponed|cancell?ed|put it back|make it|makes it|we'?ve moved)\b", re.I)


def _the_same_words(one, other):
    """Whether two lines are the same question in the same words."""
    def bare(line):
        return " ".join(re.sub(r"[^a-z0-9]+", " ", str(line or "").lower()).split())
    return bare(one) == bare(other) and len(bare(one).split()) >= 4


def _shortened(said):
    """The answer, kept whole up to a paragraph, so a repeat is not a wall of text again."""
    said = " ".join(str(said or "").split())
    if len(said) <= 320:
        return said
    kept = ""
    for part in _sentences(said):
        if kept and len(kept) + len(part) > 320:
            break
        kept = (kept + " " + part).strip()
    return kept or said


def _the_answer_again(said, memory):
    """The earlier answer, framed as the repeat it is, in the frames the chat already knows.

    The wording is not this module's to invent: `topics.said_again` says an answer again in the
    same words is what a machine does, frames it, and moves the lead-in on with each repeat - and
    every frame in the codebase is listed in `again.FRAMES`, so a lead-in written here would make
    the answer read as new words to every caller that asks whether the chat has said this already.
    So the repeat is handed to that, and when the answer is further back than it looks the first
    of the same three frames is used.
    """
    framed = topics.said_again(said, memory)
    if framed:
        return framed
    return topics.REPEAT[0].format(reply=_shortened(said))


def the_same_question_again(text, memory):
    """The answer this same question got earlier in the chat, or None.

    See the note above: only the line's own words, only an answer that was an answer, only with a
    turn in between, and never once the chat has changed the thing that answer was about.
    """
    if not isinstance(memory, dict):
        return None
    turns = memory.get("turns")
    if not isinstance(turns, list) or len(turns) < 3:
        return None
    clean = str(text or "").strip()
    if len(clean.split()) < 4:
        return None
    for back, turn in enumerate(reversed(turns[:-2])):
        if not isinstance(turn, dict):
            continue
        if not _the_same_words(clean, turn.get("user")):
            continue
        said = str(turn.get("bot") or "").strip()
        if not said or len(said) < 40:
            continue
        if HEDGE.search(said) or said.rstrip().endswith("?"):
            continue  # a hedge or a question is not an answer to hand back
        index = len(turns) - 2 - back
        between = [str((t or {}).get("user") or "") for t in turns[index + 1:-1]
                   if isinstance(t, dict)]
        if any(CHANGED_IT.search(line) for line in between):
            return None  # the answer of then is about a plan that has since changed
        return _the_answer_again(said, memory)
    return None
