"""Part 8 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
from .lookup_part_01 import (
    said,
)
from .lookup_part_07 import (
    _the_best_entry,
)


def _said_as_a_report(understood, words, entries, reject=None):
    """The entry the same name gets inside a sentence, when the line is only a name, or None.

    A card is written for a thing being raised ("i have a nappy rash", "ive got an ear
    infection"), so the bare words of the name reach several cards at once and the nearest one
    is not the one the knowledge base would answer the same person with. Read the name as the
    report it is and let the ordinary search pick: the bare "head ache" opened the migraine
    card, while "i have a head ache" gets the ordinary-headache card, which every longer line
    about a headache already gets.
    """
    if not isinstance(understood, dict):
        return None
    said = "i have a " + " ".join(str(word) for word in words)
    second = dict(understood)
    second["clean"] = said
    second["words"] = ["i", "have", "a"] + [str(word) for word in words]
    # The reading of the bare name is the reading of a remark: what it pointed at, where it
    # happened and what it leaned on are not part of the name, and a search that uses them
    # answers a line nobody typed.
    for key in ("background", "intensifier", "intensifier_left", "leans_on", "topic_own",
                "past", "handoff"):
        second.pop(key, None)
    # The report is not a line the person typed, so it gets no second look at the context and no
    # name-alone reading of its own - which is also what stops this from recurring.
    return _the_best_entry(second, entries, reject, False)


# The signs that say the food in front of them is going or gone, in people's own words. A line
# carrying one of these is asking whether it is safe to eat, whatever else it says, and the meal
# tables in `meals.py` and `cooking.py` have to stand down on it: "my mince smells a bit is it
# still ok" was answered with a ragù and "my bacon smells funny is it ok" with a curry, because
# naming a food is all a dish table needs. A recipe for a suspect ingredient is worse than no
# recipe, so the sign is read before anything is suggested.
GONE_OFF_SIGNS = ("smells", "smell", "smelly", "smelling", "stinks", "stinking", "slimy",
                  "gone off", "went off", "going off", "has gone off", "have gone off",
                  "gone bad", "has gone bad", "has gone slimy", "have gone slimy",
                  "out of date", "past its date", "past the date", "past their date",
                  "use by", "use-by", "best before", "still ok", "still good", "still fine",
                  "ok to eat", "safe to eat", "is it off", "mouldy", "moldy", "funny smell",
                  "off smell", "bin it", "bin them", "throw it away", "throw them away",
                  "throw it out", "throw them out")


def says_it_has_gone_off(clean):
    """True when the line says the food has gone off, or asks whether it has.

    `clean` is the line as the reading hands it over. The words are matched inside the line
    because "smells" and "gone off" are said as part of a longer phrase ("it smells a bit",
    "the mince has gone off"), and a word-by-word test would miss them.
    """
    low = " %s " % str(clean or "").lower()
    return any((" %s " % sign) in low or (" %s" % sign) in low
               for sign in GONE_OFF_SIGNS)


def said_in_this_line(understood, memory=None):
    """The line's own words, with any earlier line put back out of it.

    A follow-up is read with the line before it in front of it ("can i freeze it" after "im
    making a chilli tonight" reads as "im making a chilli tonight can i freeze it"), which is what
    lets "how long does it need" reach the dish at all. The cost is that a row keyed on a word
    from the earlier line answers a line that never said it: the cooked pot's question was handed
    to the row about freezing the *vegetable*. A row that has to be about what this line names
    reads the line through here instead of `clean`.

    Two shapes carry an earlier line: `leans_on` (the reading says which line it leans on) and
    `said_now` (a module wrote the subject of the conversation into the line and kept the typed
    line beside it).
    """
    if isinstance(memory, dict):
        # the line as it arrived, kept by the module that reads the conversation
        typed = memory.get("asked_now")
        if isinstance(typed, str) and typed.strip():
            return typed.strip()
    if not isinstance(understood, dict):
        return ""
    typed = understood.get("said_now")
    if isinstance(typed, str) and typed.strip():
        return typed.strip()
    # A line that describes something and then asks ("im making a chilli tonight, can i freeze
    # it") keeps the situation in `setup` and the question in `focus`, and a reading that had an
    # earlier line written into it has the same shape. Either way the question half is the part
    # being asked, so it is the part this reader looks at.
    focus = understood.get("focus")
    if understood.get("setup") and isinstance(focus, list) and focus:
        return " ".join(str(word) for word in focus).strip()
    text = str(understood.get("clean") or understood.get("text") or "")
    leans = understood.get("leans_on")
    carried = str(leans.get("text") or "") if isinstance(leans, dict) else ""
    if carried:
        low, carried = text.lower(), carried.lower()
        if carried in low:
            text = low.replace(carried, " ")
    return text.strip()
