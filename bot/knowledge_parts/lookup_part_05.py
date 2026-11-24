"""Part 5 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
from .lookup_part_01 import (
    said, SLIPS, MIN_FORM, COMMON_WORDS, lexicon, FEELING_WORDS,
)
from .lookup_part_02 import (
    _FORMS_CACHE_KEEP, tokens, _past_the_carer,
)
from .lookup_part_03 import (
    ASKS_FOR_THE_HANDS, ASKS_WHAT_IT_SAYS, A_HAND_OR_EYE_DOES_IT, OWN_THING_ON_THEIR_SIDE,
    THEIR_OWN_HANDS_THINGS, COUNTED_INTO_A_THING, GOES_IN, HOW_MANY_DAYS, KEEPS_OR_STORES,
    _KEEPING_KEY, _LIFE_KEY, _ING_NOUNS, _KEEPING_VERB, _RECURRING, _RECURRING_ANYWAY,
    _RECURRING_WITH, _RESULT_VERB, _SPOILING, _SUBJECT_POINTS, _forms, ASK_FRAME, A_LENGTH_WORD,
    A_STAND_IN, WHEN_WORDS, NOT_THE_ADJECTIVE, _COMMON, _A_PERSON, _NOT_A_THING_HAD, _engine_reads,
    FEELING_FAULT_WORDS, FEELING_SPEAKER, FEARED_THINGS, FEELING_ABOUT, FEELING_ENDS,
    FEELING_NAMES_NOTHING, _KEPT_SOMEWHERE, _POINTS_AT_IT, _A_PLACE_ON_THEM, _NOT_GONE, _POSSESSIVE,
    _SUBJECT_LEAD, _OF_THE_RULE_OUT, _THE_DEGREE_WORDS, _THE_HEAT_OF_THE_DAY, _COLD_WORDS,
    _HOW_A_PERSON_IS_COLD, _SAYS_OF_THEMSELVES, _BETWEEN_A_PLACE_AND_ITS_COLD,
    _PLACES_PEOPLE_LIVE_IN, FEELING_DOMAINS, _THE_WH_WORDS,
)
from .lookup_part_04 import (
    _part_matches, _only_the_frame, _part_match, _typo_forms, _key_names,
)


def _says_a_shape(shapes, typed, forms):
    """True when the line, as the person typed it, holds a figure of the kind a row is about.

    The shapes are given the line's own words joined by spaces ("its on 4% and the charger is at
    work"), because a shape reads a figure rather than a word and the word forms of "4%" say
    nothing: this is the one signal in the matcher that is not a key word, so it is handed the
    line and answers for itself. Words are taken from `typed` when it lines up with the forms and
    from the forms otherwise, exactly as `_bare_report` does, so a reading built without `typed`
    still matches.
    """
    if isinstance(typed, (list, tuple)) and len(typed) == len(forms):
        words = [str(word).lower() for word in typed]
    else:
        words = []
        for group in forms:
            forms_of_word = sorted(str(form).lower() for form in group) if group else []
            words.append(forms_of_word[0] if forms_of_word else "")
    line = " ".join(word for word in words if word)
    if not line:
        return False
    for shape in shapes:
        try:
            if shape(line):
                return True
        except Exception:  # noqa: BLE001 - a shape that cannot read the line is not a signal
            continue
    return False


# A line that asks what to cook with a thing names a dish, and no other kind of row can answer
# it: "what can i make with a bag of carrots" is not a question about how deep the bag is, and
# "what can i do with a punnet of raspberries" is not a question about what a punnet weighs. Rows
# about growing a crop or weighing a measure put this in their `avoid`, so the dish table answers
# the dish and the row still answers "can i grow potatoes in a bag" and "how much is a punnet".
# "Is it ok to eat this past the date" is a keeping question about the food named, and it is how
# most people ask it: the words that say the day on the pack rather than the food are kept here so
# the freshness rows, the keeping rows and the nutrition rows all read the same phrase the same
# way. A nutrition row that answered it told the person about fibre, and a shelf-life row that is
# not about the food they named told them about dried fruit.
PACK_DATE = ("past the date", "past its date", "past their date", "past the use by",
             "use by date", "use by", "sell by", "best before", "out of date",
             "after the date", "after its date", "after their date", "date on it",
             "date on the", "date says", "date said")


# The day the food is going to be eaten is the same question as the date on the pack, and people
# say it as often: "can i eat the chicken tomorrow" is "is the chicken ok the next day". The words
# live here, once, because every freshness row reads them the same way: the spoilage tests in
# still_ok, the milk card, and the diet plan's stand-down list. "tomorrow" was missing from them
# for a long time, so a whole family of lines was a shrug while its twin was answered.
DAY_WORDS = ("next day", "the next day", "the day after", "day after", "yesterday",
             "tomorrow", "tomorow", "tmrw", "tomoz")


def _under_their_own_hands(item, typed):
    """True when the line asks the bot to do something to a thing of the person's own.

    Only the rows about that thing stand down, and only when the line is an ask to the bot with a
    verb a hand or an eye would do: "can you fill in this form", "could you print my cv".
    """
    line = " ".join(str(word).lower() for word in typed)
    if not ASKS_FOR_THE_HANDS.search(line) or not A_HAND_OR_EYE_DOES_IT.search(line):
        return False
    if ASKS_WHAT_IT_SAYS.search(line):
        return False   # "what does this letter mean" is the knowledge base's line
    if not OWN_THING_ON_THEIR_SIDE.search(line):
        return False
    said = set()
    for part in (item.key or ()):
        for alternative in ((part,) if isinstance(part, str) else part):
            said |= {piece for piece in str(alternative).lower().split()}
    return bool(said & THEIR_OWN_HANDS_THINGS)


# A line that asks what the sky is doing is asking for today's reading, which the bot cannot look
# up, and it is the commonest kind of line there is: "what is the weather like today", "whats the
# weather like this weekend", "is it cold outside", "is it warm enough to sit outside". Those are
# not plans, nor a note on cold air and lungs, nor a note on what to wear - on today's main the
# first was a weekend plan ("pick two things and put them in the diary by Friday"), the third was
# "cold air does not damage healthy lungs", and the fourth was "dress for ten minutes in". Each of
# those rows is keyed on a weather word or a day word, which is what let the line in: "today" and
# "what" is enough for the plans row, "cold" and "outside" for the lungs row, "warm" and "outside"
# for the clothes note. So the rows that key on those words stand down on this list, and the live
# information note answers with the kind of answer it is ("No live weather here - a forecast app
# will tell you in one tap"), which is what "is it cold today" already got.
#
# These are phrases and not the bare words, on purpose. "the weather" as a noun is far too common
# in a line that wants something else ("what can i do this weekend, the weather looks bad" is a
# plan), and the bare word would stand the useful answer down. What is left is the shapes that ask
# for the reading itself: the thing named as a question, or "enough" said of it.
# A house warms up too, and so does a bottle, a room and a pan. "my boiler is making a noise and
# the heating isnt warming up, what should i check" got "Five minutes, in two parts: first
# something easy that gets you slightly out of breath" and "my boiler is noisy and the heating is
# cold, what do i do" got the cold remedy paragraph, because "warming up" and "cold" were the
# whole of what those lines shared with a row about a body. This is the list of house and appliance
# words that mean the room rather than the person, kept in one place so every row that reads
# "warm up" stands down for them: a fence written per row is a fence that goes missing on the next
# row (the gym's own warm-up row answered the boiler after the first two were fenced).
A_HOUSE_WARMING_UP = ("heating", "boiler", "boilers", "radiator", "radiators", "thermostat",
                      "central heating", "hot water", "immersion", "combi", "flue", "trv",
                      "house", "the flat", "my flat", "our flat", "room", "rooms", "bathroom",
                      "kitchen", "bedroom", "living room", "overnight", "no heat")


A_WEATHER_ASK = ("weather like", "weather doing", "weather going to be", "weather forecast",
                 "what is the weather", "whats the weather", "what's the weather",
                 "wether like", "whats the forecast", "what's the forecast", "the forecast for",
                 "is it cold outside", "is it cold today", "is it cold out", "is it cold enough",
                 "is it warm outside", "is it warm today", "is it warm enough",
                 "is it hot outside", "is it hot today", "is it hot enough",
                 "is it freezing", "is it raining", "is it snowing",
                 "warm enough to", "cold enough to", "how cold is it", "how hot is it",
                 "how warm is it", "what is it like outside", "whats it like outside",
                 "what's it like outside")


# A line that asks what to put on, pack or take is asking for a list, not for the science of why
# the sky is doing it. "what should i wear in the rain" was the water-cycle note, "what do i need
# to take if its snowing" and "what should i wear in the snow" were the note on how snow forms, and
# "what should i wear in the wind" the one on pressure - the weather word is in every one of those
# rows' keys and the ask, which decides what kind of answer the line wants, was in none of them.
# Clothes cards already answer most of these lines ("what should i wear for a walk in the rain" is
# the walking kit), so the explanation rows stand down here and the clothing rows get the line.
#
# These are phrases rather than the bare word "wear", because "wear" alone is in a dozen lines that
# want the science: "why does my watch wear out", "what makes tyres wear", "why do clothes wear at
# the knee". What is left is the ask itself, with a person in it or the word "to" after it.
A_WHAT_TO_WEAR = ("what should i wear", "what do i wear", "what to wear", "what shall i wear",
                  "what should i put on", "what do i put on", "what to put on",
                  "what should he wear", "what should she wear", "what should they wear",
                  "what should we wear", "what does he wear", "what does she wear",
                  "what should i pack", "what do i pack", "what to pack", "what shall i pack",
                  "what should i take", "what do i take", "what to take", "what should i bring",
                  "what do i bring", "what to bring", "what do i need to take",
                  "what do i need to bring", "what kit", "what clothes", "which clothes",
                  "what should i put in my bag", "what do i need to wear")


# A food a person keeps in the house, and asks about keeping. It is a short table on purpose: a
# row that stands down for it is standing down for a line that is plainly about the food, so the
# word has to be one nobody keeps anything else in. "Why does bread go mouldy in a plastic bag"
# is a loaf and a bag it came in, not a carrier bag to pay for, and "why does bread go mouldy
# faster in a bag" is not a garment to air; "is it better to keep bread in the fridge" is not
# which carbohydrate is better for you. Each of those rows answered the wrong half of the line,
# and the word that decides it is the food.
KEPT_FOODS = ("bread", "loaf", "loaves", "rolls", "bagels", "milk", "butter", "cheese",
              "yoghurt", "yogurt", "cream", "eggs", "egg", "meat", "chicken", "beef",
              "pork", "lamb", "bacon", "ham", "sausages", "sausage", "fish", "salmon",
              "prawns", "rice", "pasta", "noodles", "potatoes", "potato", "flour", "oats",
              "cereal", "soup", "stew", "sauce", "gravy", "cake", "biscuits", "cookies",
              "chocolate", "fruit", "apples", "bananas", "berries", "strawberries", "salad",
              "lettuce", "spinach", "carrots", "mushrooms", "tomatoes", "onions", "peas",
              "beans", "leftovers", "leftover", "sandwich", "sandwiches", "hummus", "nuts")


# The words that say the line is about keeping a thing rather than about the thing itself. A
# keeping question has one of these and a food, and it is the food's own rows that answer it.
# A keeping question says what has happened to the food or where it is put, not just the verb
# "keep" - "how do i keep my bread habit" is a habit line and names bread. So the bare verb is not
# here: "how do i keep bread fresh" is ("fresh"), "how long can i keep cooked rice" is ("how
# long"), and "should i keep bread in the fridge" is ("fridge").
KEEPING_WORDS = ("store", "stores", "stored",
                 "storing", "storage", "last", "lasts", "lasted", "fresh", "fresher",
                 "freshness", "stale", "staler", "stales", "staleness", "mould", "moulds",
                 "mouldy", "mold", "molds", "moldy", "mildew", "mildewy", "goes off",
                 "go off", "gone off", "going off", "goes bad", "gone bad", "goes hard",
                 "gone hard", "goes soggy", "gone soggy", "fridge", "freezer", "freeze",
                 "freezing", "bin", "shelf life", "cold", "warm", "damp", "how long",
                 "longer", "longest", "keep fresh", "use by", "best before")


def not_a_count_for_the_box_or_the_dish(understood):
    """False when a "how many" line counts into a dish or asks how long the food keeps."""
    if not isinstance(understood, dict):
        return True
    text = " " + str(understood.get("clean") or understood.get("text") or "").lower() + " "
    if (GOES_IN.search(text) or HOW_MANY_DAYS.search(text) or KEEPS_OR_STORES.search(text)
            or COUNTED_INTO_A_THING.search(text)):
        return False
    return True


def a_food_is_being_kept(understood):
    """True when the line asks about keeping a food: it names a food and a keeping word.

    A row about something else that shares a word with such a line answers the wrong half of it.
    The container in "why does bread go mouldy in a plastic bag" is packaging, the bag in "why
    does bread go mouldy faster in a bag" is where the loaf was kept, and the fridge in "is it
    better to keep bread in the fridge" is where it is kept - so the garment rows, the carrier
    bag charge and the which-carbohydrate-is-better row all stand down and the bread rows answer.
    "My coat smells of curry" names no keeping word and no food, so nothing here touches it.
    "How do i keep my gym bag smelling fresh" names a garment and a keeping word but no food.
    """
    if not isinstance(understood, dict):
        return False
    text = " " + str(understood.get("norm_text") or understood.get("clean") or "").lower() + " "
    if not any(word in text for word in KEEPING_WORDS):
        return False
    words = understood.get("words") or ()
    said = {str(word).lower() for word in words}
    for food in KEPT_FOODS:
        if " " in food:
            if food in text:
                return True
        elif food in said or (" " + food + " ") in text:
            return True
    return False


# What a thing is kept in, or kept on. A row whose own words include one of these can be handed a
# line about the food inside it - a loaf in a plastic bag, a joint in a drawer - and that line is
# the food's question. `only_a_container` is the test such a row puts beside
# `a_food_is_being_kept` to tell its own container from somebody else's.
CONTAINERS = ("bag", "bags", "bin bag", "bin bags", "bin", "bins", "box", "boxes",
              "packet", "packets", "pack", "packs", "tin", "tins", "jar", "jars", "tub",
              "tubs", "container", "containers", "lunchbox", "lunch box", "sack", "sacks",
              "suitcase", "suitcases", "rucksack", "rucksacks", "backpack", "backpacks",
              "handbag", "handbags", "luggage", "basket", "baskets", "crate", "crates",
              "tray", "trays", "drawer", "drawers", "cupboard", "cupboards", "shelf",
              "shelves", "fridge", "freezer")


def only_a_container(understood, names):
    """True when every word of `names` the line says is a container a thing is kept in.

    "Why does bread go mouldy in a plastic bag" says "bag" and nothing else of the garment table,
    so the garment rows stand down for the loaf. "My gym bag smells musty" has no food in it, so
    `a_food_is_being_kept` is already false and this is never asked. "My leather jacket smells of
    cheese" says two words of that table and leather is not a container, so the jacket keeps its
    answer.
    """
    if not isinstance(understood, dict):
        return False
    text = " " + " ".join(str(word).lower() for word in (understood.get("words") or ())) + " "
    found = [one for one in names if " " + one + " " in text]
    return bool(found) and all(one in CONTAINERS for one in found)


# A line that asks when a place opens or shuts is asking for the venue's hours, which the bot
# cannot look up, and the fallback says so ("I can't check today's opening hours, sorry"). Three
# rows keyed on a day word were taking those lines instead, because "today" and a question word
# is all they need: "what time does the post office on hill road close today" was a weekend plan
# ("pick two things and put them in the diary by Friday") and "what time does the tip close
# today" the same. The shape is what makes it an hours ask, so it is the phrases and not the bare
# words: "what time ... close", "opening hours", "shut today". A line that asks what to do with
# a free day keeps its plan.
A_HOURS_ASK = ("what time does", "what time do", "what time is the", "what time are the",
               "opening hours", "opening times", "opening time", "closing time",
               "closes at", "closes today", "closes tonight", "shuts at", "shuts today",
               "close today", "close tonight", "close on", "open today", "open now",
               "open on", "is it open", "is it shut", "open until", "open till",
               "till what time", "until what time", "last entry", "last orders")


DISH_ASK = ("make with", "made with", "make using", "make from", "make out of",
            "what can i make", "what can i cook", "what should i make", "what can i do with",
            "what should i do with", "cook with", "cooking with", "do with", "using up",
            "for dinner", "for tea", "for lunch", "for supper", "for breakfast", "tonights tea",
            "something with", "dish with")


_KEEPING_ROWS = {}


def _keeping_row(item):
    """True when this row answers a "how long does it keep" question."""
    known = _KEEPING_ROWS.get(id(item))
    if known is None:
        keeps = False
        lives = False
        for part in item.key:
            for alternative in (part if isinstance(part, tuple) else (part,)):
                if not isinstance(alternative, str):
                    continue
                shaped = alternative.strip().lower()
                if shaped in _KEEPING_KEY:
                    keeps = True
                elif shaped in _LIFE_KEY:
                    lives = True
        known = keeps and lives
        _KEEPING_ROWS[id(item)] = known
    return known


def _gerund(forms, index):
    """The -ing verb at this position of the line, or "" when the word is a thing."""
    for form in forms[index]:
        if form in _ING_NOUNS or len(form) < 5 or not form.endswith("ing"):
            continue
        return form
    return ""


def _later_words(forms, index, reach=3):
    """The words after a position, for the state a "keeps going ..." line names."""
    seen = set()
    for step in range(index, min(index + reach, len(forms))):
        seen |= forms[step]
    return seen


def _keeps_failing_at(forms, seen=None):
    """Where the "keeps" of a fault verb sits, or None when no "keeps" is one.

    "i keep running to the loo" has the shape of "my bread keeps coming out flat" and is the
    opposite case: the thing the row is about comes *after* the verb (what the person keeps
    doing), so the verb is the person's own phrasing of a complaint and not the fault. The
    caller compares this position with where the entry's subject matched.
    """
    if seen is not None:
        got = seen.get("keeps-failing-at")
        if got is not None:
            return None if got is False else got
    failing = None
    for index in range(len(forms) - 1):
        if not (forms[index] & _KEEPING_VERB):
            continue
        gerund = _gerund(forms, index + 1)
        if not gerund:
            continue
        if gerund in _RECURRING:
            continue
        if gerund in _RECURRING_ANYWAY and _later_words(forms, index + 1) & _RECURRING_WITH:
            continue
        result = (_later_words(forms, index + 1) & frozenset(("out",))
                  and (_later_words(forms, index + 1) & _RESULT_VERB
                       or gerund in _RESULT_VERB))
        if result or not (_later_words(forms, index + 1) | {gerund}) & _SPOILING:
            failing = index
            break
    if seen is not None:
        seen["keeps-failing-at"] = False if failing is None else failing
    return failing


def _keeps_failing(forms, seen=None):
    """True when "keeps" is the fault verb, as in "my bread keeps coming out flat"."""
    return _keeps_failing_at(forms, seen) is not None


def _the_whole_subject(part, forms, seen=None):
    """True when the entry's subject part matches every word the subject is made of.

    "what should i do about the damp patch" is a patch, not condensation: the entry whose subject
    part holds "damp" matches one word of it, and one word of a two-word subject is not what the
    ask is about.
    """
    span = set()
    for _weight, _words, hit in _part_matches(part, forms, seen):
        span.update(hit)
    wanted = [index for index, word_forms in enumerate(forms)
              if not (word_forms & _SUBJECT_POINTS)]
    return bool(wanted) and all(index in span for index in wanted)


# The sounds a machine makes, in the forms people type them. `lookup` matches whole words rather
# than stems, so a row that names "clicking" and not "click" answers only the lines that happen to
# use the form it was written with: "my boiler clicks a lot" and "the boiler is clicking" were met
# with "I'm listening", while the answer for a tick - the pipes expanding, felt where the pipe
# passes a joist - was already written and reachable only through "the boiler wont stop clicking".
# The rows that answer a noise read this list instead of writing their own, so the forms cannot
# drift apart from the answers again. It lives here rather than in wording.py because wording.py
# imports this module, so a list both of them need belongs on this side of that edge.
MACHINE_SOUNDS = ("hum", "hums", "humming", "hummed", "buzz", "buzzes", "buzzing", "drone",
                  "drones", "droning", "vibrate", "vibrates", "vibrating", "vibration",
                  "whistle", "whistles", "whistling", "whine", "whines", "whining",
                  "squeal", "squeals", "squealing", "squeak", "squeaks", "squeaking",
                  "screech", "screeches", "screeching", "shriek", "shrieks", "shrieking",
                  "hiss", "hisses", "hissing", "gurgle", "gurgles", "gurgling", "glug",
                  "glugging", "bang", "bangs", "banging", "knock", "knocks", "knocking",
                  "rumble", "rumbles", "rumbling", "clunk", "clunks", "clunking", "clank",
                  "clanks", "clanking", "rattle", "rattles", "rattling", "tick", "ticks",
                  "ticking", "tap", "taps", "tapping", "click", "clicks", "clicking",
                  "thump", "thumps", "thumping", "roar", "roaring", "grind", "grinds",
                  "grinding", "scrape", "scrapes", "scraping")


def _rarity(entries):
    """{key word: how many entries use it}, so rare words can count for more."""
    counts = {}
    for item in entries:
        words = set()
        for part in item.key:
            for alternative in (part if isinstance(part, tuple) else (part,)):
                if isinstance(alternative, str):
                    words.update(alternative.lower().split())
        for word in words:
            counts[word] = counts.get(word, 0) + 1
    return counts


_TAIL_ASK_WORDS = None


def _the_tail_asks_about(forms):
    """Where the line's last question starts, or -1 when it asks in one breath.

    People put the reason first and the question last: "my nan is 80 next month and we want a
    cake, what should i get her", "i have a christening sunday and it is meant to rain, what do i
    wear". The words after that question word are what was asked.
    """
    global _TAIL_ASK_WORDS
    if _TAIL_ASK_WORDS is None:
        _TAIL_ASK_WORDS = frozenset().union(*(_forms(word) for word in (
            "what", "whats", "which", "how", "where", "when", "who", "why", "should", "shall",
            "could", "would", "can")))
    ask_words = _TAIL_ASK_WORDS
    for index in range(len(forms) - 1, 3, -1):
        word = forms[index]
        if word and (word & ask_words):
            return index
    return -1


def _rank(item, forms, rarity, seen=None):
    """Score plus specificity: a key word only a few entries use says more about the line.

    A key part the line only reaches inside its last question, through the asking words alone
    ("what","should" / "what","do","i","do"), is the asking of that question and not a thing the
    row is about. The row that lists the asking was winning lines that put the reason first:
    `babyfood-by-age` (key part "what should") took "my nan is 80 next month and we want a cake,
    what should i get her" off `gift-mum`, and `telling-a-child-off` (key part "what do i do")
    took "the boiler broke and the landlord is ignoring me, what do i do" off the landlord card.
    The same part in the first clause is untouched, and so is any part that reaches a real word
    of the question ("what should i bake", "what do i wear").
    """
    tail_from = _the_tail_asks_about(forms)
    matched = [_part_match(part, forms, seen=seen) for part in item.key]
    said = sum(weight for weight, words, span in matched
               if weight and not (tail_from >= 0 and min(span) >= tail_from
                                  and _only_the_frame(words)))
    total = 0
    says_what = False
    for part in item.key:
        weight, words, span = _part_match(part, forms, seen=seen)
        if weight and said > 2 and tail_from >= 0 and min(span) >= tail_from \
                and _only_the_frame(words):
            # the same part `said` left out: the asking of the last question, not the subject
            continue
        total += weight + sum(1 for word in words if rarity.get(word, 0) == 1)
        if any(word not in ASK_FRAME and word not in WHEN_WORDS and word not in A_LENGTH_WORD
               and word not in A_STAND_IN for word in words):
            says_what = True
    if not says_what:
        # Every word this row reached the line with is how the line was asked or when the thing
        # happens, and neither is what the line is about. "what should i do about the toilet
        # flushing all night" reached the hour-before-bed row on "what should i do" and "night"
        # and was told to switch the screens off, while the row for the toilet scored one point
        # lower on the words it is actually about; "the heating comes on at night for no reason"
        # reached the same row the same way. Asking and when are the wrapping of a line, so a row
        # made only of them is ranked behind every row that names something, and it still answers
        # on its own where the line names nothing else ("what should i do at bedtime").
        # The bias is not counted either: it is there to settle two rows that both name the
        # line's subject, and this one has not named it.
        return 1
    return total + item.bias


# The knowledge base does not change during a conversation, so the rarity of every key word
# and the words it knows are worked out once per entries list and kept for the next turn.
_CACHE = {}


_CACHE_KEEP = 6


def _key_words(item):
    """The words the entry's key asks for, as written in it ("roast chicken" gives two)."""
    words = set()
    for part in item.key:
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if isinstance(alternative, str):
                words.update(alternative.lower().split())
    return words


_KEY_FORMS = {}


def _key_forms(item):
    """Every form of every word the entry's key asks for, worked out once for the entry.

    Read by the two-position test in score(), which is asked about the same few thousand
    entries on every line. The entry is kept beside its forms because the card is keyed by id:
    an Entry a test built and let go must not be read as the one that took its id.
    """
    got = _KEY_FORMS.get(id(item))
    if got is not None and got[0] is item:
        return got[1]
    forms = set()
    for part in item.key:
        for alternative in (part if isinstance(part, tuple) else (part,)):
            if isinstance(alternative, str):
                for word in alternative.lower().split():
                    forms |= _forms(word)
    forms = frozenset(forms)
    if len(_KEY_FORMS) >= _FORMS_CACHE_KEEP:
        _KEY_FORMS.clear()
    _KEY_FORMS[id(item)] = (item, forms)
    return forms


def _two_positions(forms, item):
    """True when the line can have a form of the entry's key in two different places.

    score() answers 0 to an entry that covers fewer than two positions of the line, and an
    entry with one of its key's words in the line covers one position at most. Reading the
    line for the entry's forms is a handful of set tests, while the parts of its key are a few
    dozen phrase questions, so the entries that can only score 0 are dropped here: on a random
    deck turn that is 63% of the entries the line reaches. A phrase of the key needs its words
    side by side, which this does not check, so what it finds is an upper bound: no entry it
    drops could have covered two positions.
    """
    key = _key_forms(item)
    found = False
    for word_forms in forms:
        if not word_forms.isdisjoint(key):
            if found:
                return True
            found = True
    return False


def _word_index(entries):
    """{form: [positions of the entries that ask for it]}, so a line starts from its own words.

    score() gives an entry 0 unless two different words of its key are in the line, so an entry
    that shares no word with the line can never win it. The knowledge base is 2,500 entries and
    a line has six words, so walking every entry a turn cost a reply about a second of processor
    time; looking up the words the line does have cuts the scan to the entries that can answer it
    at all. Positions keep the registry's order, which the tie-break in `_best` needs.
    """
    cached = _INDEX.get(id(entries))
    if cached is not None and cached[0] is entries:
        return cached[1]
    index = {}
    for position, item in enumerate(entries):
        for word in _key_words(item):
            for form in _forms(word):
                at = index.get(form)
                if at is None:
                    index[form] = [position]
                elif at[-1] != position:
                    at.append(position)
    while len(_INDEX) >= _CACHE_KEEP:   # keep the list itself, so its id cannot be reused
        _INDEX.pop(next(iter(_INDEX)))
    _INDEX[id(entries)] = (entries, index)
    return index


_INDEX = {}


def _reaching(entries, forms):
    """The entries that share a word with the line, in the registry's order, or all of them.

    A line of unknown words (a name, "ok then") reaches nothing, and the caller still has to see
    every entry, so an empty answer is passed on as the whole list rather than as no candidates.
    """
    index = _word_index(entries)
    hit = set()
    for word_forms in forms:
        for form in word_forms:
            positions = index.get(form)
            if positions:
                hit.update(positions)
    if not hit:
        return entries
    return [entries[position] for position in sorted(hit)]


def _domain_rarity(entries):
    """({domain: {key word: how many of its entries use it}}, every key word once)."""
    by_domain, every = {}, {}
    owners = {}
    for item in entries:
        domain = getattr(item, "domain", "") or ""
        counts = by_domain.setdefault(domain, {})
        words = set()
        for part in item.key:
            for alternative in (part if isinstance(part, tuple) else (part,)):
                if isinstance(alternative, str):
                    words.update(alternative.lower().split())
        for word in words:
            counts[word] = counts.get(word, 0) + 1
            owners.setdefault(word, set()).add(getattr(item, "id", None) or id(item))
    for word in owners:
        if owners[word] <= SLIPS.get(word, set()):
            continue                    # a misspelling only the spelling answers list
        every[word] = len(owners[word])
    return by_domain, every


def _vocabulary(entries):
    """Per-domain rarity, every key word, and the forms the knowledge base knows."""
    cached = _CACHE.get(id(entries))
    if cached is not None and cached[0] is entries:
        return cached[1], cached[2], cached[3]
    by_domain, every = _domain_rarity(entries)
    slips = {slip.lower() for item in entries for slip in getattr(item, "slips", ())}
    # `every` keeps its counts, it does not become a set of words: it is the rarity of the whole
    # knowledge base, and it is what `_rank` falls back on when an entry's own domain has no
    # counts. A domain is set on an entry when the registry collects it, so an entries list can be
    # read before its domains exist; handing `_rank` a set there raised on `rarity.get` and took
    # the whole turn down with it.
    every = {word: count for word, count in every.items() if word.lower() not in slips}
    known = set()
    for word in every:
        known |= _forms(word)
    if all(getattr(item, "domain", "") for item in entries):
        # Only a list whose entries already know their domain. The registry sets the domain on
        # every entry the first time it is built, so a list cached before that would keep the
        # per-domain counts of the empty domain and rank a "family" line against no words.
        while len(_CACHE) >= _CACHE_KEEP:  # keep the list itself, so its id cannot be reused
            _CACHE.pop(next(iter(_CACHE)))
        _CACHE[id(entries)] = (entries, by_domain, every, known)
    return by_domain, every, known


def _y_word_stems(word):
    """The thing a "-y" word describes, as the word under the adjective.

    "my tap is leaky" is the leak entry's line, "a creaky gate" the creak one's, "a scaly
    kettle" the scale one's, "squeaky brakes" the squeak one's. The matcher only ever handed
    these the plural-looking "leakies", so an adjective the person typed never met a key that
    lists the noun or the verb behind it: "how do i fix a leaky tap" was answered while "the
    garden gate is creaky", "my kettle is scaly" and "my car brakes are squeaky" all got "Got
    it. Is there anything you'd like a hand with?".

    English builds the adjective two ways - on the word itself (leak, smell, creak, rust) and on
    an "e" the adjective drops (noise, grease, scale, taste) - so both are offered. Only those
    two shapes: the doubled consonant of "muddy" or "runny" is not chased, because the short
    word under it is as often a different one ("runny nose" is not a run, "sorry" is not sore).
    A stem shorter than MIN_FORM, or one from a word whose stem is an everyday word of its own
    (NOT_THE_ADJECTIVE), is not offered either.
    """
    if len(word) < 5 or not word.endswith("y") or word[-2] in "aeiouy":
        return ()
    if word in NOT_THE_ADJECTIVE:
        return ()
    stem = word[:-1]
    return tuple(form for form in (stem, stem + "e") if len(form) >= MIN_FORM)


def _a_word_itself(word):
    """True when the understanding engine holds this exact word, not only a relative of it."""
    return (word in _COMMON or word in COMMON_WORDS or word in lexicon.CHAT
            or word in lexicon.EXPAND)


def _read_the_adjective(words, forms, vocabulary):
    """Add the thing each "-y" line word describes, where the knowledge base asks for it.

    Only a stem some entry already keys as a word counts, so the rule cannot reach anything the
    knowledge base does not ask about. It is a second read of a line that reached no entry as
    typed: the words are the same, and the row that keys the adjective itself has already had
    its turn, so "my rice came out really sticky again" stays with the sticky rice row rather
    than being pulled to a pan-sticking one by the "stick" inside it.
    """
    gave = False
    for index, word in enumerate(words):
        # A word that is a word of its own is not the adjective over a noun: "footy" is how
        # half the country says football, and read as "foot" it put "watched the footy last
        # night" on the swollen-ankles card, because that entry keys "foot" and "night" and the
        # line held both. Only a word the engine holds is left alone, not one it knows a
        # relative of: "squeaky" and "creaky" are the brake and the hinge, and the stems are
        # exactly the words those rows ask for.
        if _a_word_itself(word):
            continue
        for stem in _y_word_stems(word):
            if stem in vocabulary and stem not in forms[index]:
                forms[index] |= {stem}
                gave = True
    return gave


def _read_a_thing_had(words, forms):
    """Add "have" to a "has" that says somebody has a thing, in place.

    Only the possession sense: "my mum has a headache" and "my wife has got a bad back" read as
    "have", and "he has to get two buses", "it has to be quick" and "my phone screen has a green
    blotch" do not. Four words back is enough to find the person, because a relation is said
    before the verb ("my mum", "my wife's brother") and nothing else in the line can be the thing
    the line is about.
    """
    for index, word in enumerate(words):
        if str(word).lower() != "has":
            continue
        after = str(words[index + 1]).lower() if index + 1 < len(words) else ""
        if after in _NOT_A_THING_HAD:
            continue
        if after == "got" and index + 2 < len(words) and str(words[index + 2]).lower() == "to":
            continue                            # "has got to go" is a duty, not a possession
        before = [str(word).lower() for word in words[max(0, index - 4):index]]
        if not any(word in _A_PERSON for word in before):
            continue
        forms[index] |= _forms("have")


def _read_typos(words, forms, vocabulary, known):
    """Add the key word each misspelt line word is a single slip away from, in place.

    Only a word that is not a word of its own is read as a slip. A key word the knowledge base
    knows is left alone, and so is any ordinary English word, in any of its forms: "charging"
    is a form of one, so a slip of "changing" cannot be invented out of it, and "write" and
    "leave" are words themselves.
    """
    for index, word in enumerate(words):
        if forms[index] & known or _engine_reads(word):
            continue
        if "'" in word:                 # a contraction or possessive is never a slip
            continue
        forms[index] |= _typo_forms(word, vocabulary)


def _without_possessive(word):
    """The word without a possessive on the end: "earth's" and "earths" are "earth"."""
    for tail in ("'s", "\u2019s"):
        if word.endswith(tail):
            return word[:-2]
    return word


# A feeling about a thing makes the line a line about the person: "my son looks sad about his
# bike" is not a question about the size of a bike, and "my mum is upset about her garden" is not
# a how-to about a garden. The thing is only the occasion of the feeling, so the words that name
# it are taken out of what the knowledge base reads, and the rest of the line is read as usual:
# "my back hurts and im worried about work" still reaches the back, because the words that match
# it sit outside the phrase. "bored" is not here on purpose - bored children do want the thing
# that fills an afternoon, and that answer is a good one.
FEELING_ABOUT_A_THING = FEELING_WORDS + (
    "sad", "sadness", "unhappy", "scared", "frightened", "lonely", "gutted", "devastated",
    "heartbroken", "annoyed", "annoying", "furious", "cross", "upsetting", "fuming",
)


def _names_a_fault(occasion):
    """Whether the thing a feeling is about is a thing that is broken."""
    return bool(FEELING_FAULT_WORDS.intersection(str(word).lower() for word in occasion))


def _speaker_is_feeling(words):
    """Whether the speaker is the one with the feeling, not somebody the line is about."""
    low = [str(word).lower() for word in words]
    for pos, word in enumerate(low):
        if word not in FEELING_ABOUT_A_THING \
                and not (word == "fed" and low[pos + 1:pos + 2] == ["up"]):
            continue
        for back in low[max(0, pos - 6):pos]:
            if back in FEELING_SPEAKER:
                return True
    return False


def _names_a_feared_thing(occasion):
    """Whether the thing a feeling is about is a thing people are afraid of as a class."""
    return bool(FEARED_THINGS.intersection(str(word).lower() for word in occasion))


def _feeling_occasion(words):
    """The words naming the thing a feeling is about, or None.

    "how do i stop feeling anxious about my exams" leaves the ask and the feeling itself, so the
    anxiety card keeps the line.
    """
    low = [str(word).lower() for word in words]
    for pos, word in enumerate(low):
        if word not in FEELING_ABOUT_A_THING \
                and not (word == "fed" and low[pos + 1:pos + 2] == ["up"]):
            continue
        at = pos + 1
        if at < len(low) and low[at] in ("up", "off"):
            at += 1
        if at >= len(low) or low[at] not in FEELING_ABOUT:
            continue
        got = []
        for word_after in low[at + 1:at + 6]:
            if word_after in FEELING_ENDS or not word_after.isalpha():
                break
            got.append(word_after)
        if not [word for word in got if word not in FEELING_NAMES_NOTHING]:
            continue
        return got
    return None


def _the_kept_rows():
    """Every row whose key names keeping a thing somewhere."""
    from ..knowledge import entries as all_entries  # the registry, to avoid an import cycle
    return [item for item in all_entries() if _key_names(_KEPT_SOMEWHERE, item)]


def _the_thing_the_chat_is_on(understood):
    """The thing the conversation is on, from the reading of the line (memory["understood"])."""
    understood = understood if isinstance(understood, dict) else {}
    ref = understood.get("ref")
    if isinstance(ref, dict):
        for key in ("it", "that", "they", "them"):
            thing = ref.get(key)
            if thing and str(thing).lower() not in _POINTS_AT_IT:
                return str(thing)
    subject = understood.get("subject")
    if subject and str(subject).lower() not in _POINTS_AT_IT:
        return str(subject)
    return ""


def _without_the_place(understood):
    """The same reading with a part of the body the thing sits on taken out, or an empty list."""
    if not isinstance(understood, dict):
        return []
    clean = understood.get("clean") or understood.get("text") or ""
    said = _A_PLACE_ON_THEM.search(clean)
    if not said or said.group(1).lower() not in lexicon.BODY_PARTS:
        return []
    left = (clean[:said.start()] + clean[said.end():]).strip(" ,.;:!?")
    if len(left.split()) < 2:
        return []
    shaped = dict(understood)
    shaped["clean"] = left
    shaped["words"] = tokens(left)
    return [shaped]


def _a_thing_that_has_not_gone(understood):
    """The same line read as the ask about the thing said not to have gone.

    Only the report is reshaped: the words before "has not gone" are the thing. Two openers are
    tried for the same reason `_what_is_wrong_with_them` tries two - a card is keyed on one ask
    and not the other ("a rash that wont go away" finds the rash card, "how do i treat a rash"
    finds it too, while a bare "the rash" is not an ask).
    """
    if not isinstance(understood, dict):
        return []
    clean = understood.get("clean") or understood.get("text") or ""
    said = _NOT_GONE.search(clean)
    if not said:
        return []
    thing = _SUBJECT_LEAD.sub("", clean[:said.start()].strip(" ,.;:!?"))
    thing = _POSSESSIVE.sub("", thing).strip()
    if not thing or len(thing.split()) > 5:
        return []
    again = []
    for said_so in ("a %s that wont go away" % thing,
                    "how do i treat %s" % thing,
                    "%s still there" % thing):
        shaped = dict(understood)
        shaped["clean"] = said_so
        shaped["words"] = tokens(said_so)
        again.append(shaped)
    return again


def _what_is_wrong_with_them(understood):
    """The same reading with a carer's line read as the ask about the thing named, or it back.

    "my daughter has head lice", "our baby's got conjunctivitis", "my son caught chickenpox": the
    child and the having are the shape of the sentence, not what it is about, and no card is keyed
    on them. A bare "head lice" is not an ask either, so the rest of the line is read as the ask
    it is - "how do i deal with head lice" - and the words of that ask are ones every card ignores.
    Two openers are tried, because a card that answers a condition is keyed on the condition and the
    opener it expects is not the same everywhere ("how do i treat shingles" finds it, "how do i deal
    with shingles" does not). A blunt "what do i do for <thing>" is not among them: it answered a
    water infection with the dry-eye card.
    """
    if not isinstance(understood, dict):
        return []
    cared = _past_the_carer(understood.get("clean") or understood.get("text") or "")
    if not cared:
        return []
    again = []
    for opener in ("how do i deal with ", "how do i treat "):
        said = opener + cared
        shaped = dict(understood)
        shaped["clean"] = said
        shaped["words"] = tokens(said)
        again.append(shaped)
    return again


def _without_the_ruled_out(understood):
    """The same reading with the words of the thing the line rules out taken out.

    "for a holiday not a house" is read as "for a holiday": the house-left-empty card opens on
    "house" and closes on "holiday", and the person had just said it was not a house. Only the
    reading a card is chosen from loses the words; the line itself is untouched, so every other
    module is still told what they said.
    """
    gone = [str(word).strip().lower() for word in understood.get("ruled_out") or []
            if str(word).strip()]
    if not gone:
        return understood
    clean = understood.get("clean") or ""
    words = understood.get("words")
    if not isinstance(words, list) or not words:
        words = tokens(clean)
    wanted = list(gone)
    left = []
    for word in words:
        key = word.lower() if isinstance(word, str) else ""
        if key and key in wanted:
            wanted.remove(key)
            continue
        left.append(word)
    if not [word for word in left if _OF_THE_RULE_OUT.get(str(word).lower()) is None]:
        # The line is the refusal and nothing else ("not a series", after the film list). There
        # is nothing left to choose a card from, so the line stays whole and the readers that
        # answer a refusal ("not a series" narrows the list they have) get it as typed.
        return understood
    read = dict(understood)
    read["words"] = left
    read["clean"] = " ".join(word for word in left if isinstance(word, str))
    return read


def _the_degrees_are_a_temperature(understood):
    """Whether the line says how hot it is in degrees.

    The reading keeps the numbers the line names with the words they were written with, so "35
    degrees" is a measure of heat and "a 2:1 degree" is not. The same word, read from what sits in
    front of it.
    """
    numbers = understood.get("numbers")
    if not isinstance(numbers, list) or not numbers:
        return False
    # Where the word "degrees" sits differs between readings: it can be inside the number's own
    # text ("35 degrees") or a word of its own beside it ("35"), so both are read - the number is
    # what makes a temperature, and the degree word is what says the figure is heat.
    said = []
    for number in numbers:
        if isinstance(number, dict):
            said.extend(str(number.get("text") or "").lower().split())
    words = understood.get("norm")
    if isinstance(words, list):
        said.extend(str(word).lower() for word in words)
    for word in said:
        if "degree" in word:
            return True
        if any(sign in word for sign in ("\u00b0c", "\u00b0f", "\u00ba", "\u00b0", "\u00b0c")):
            return True
    return False


def _answers_a_qualification(item):
    """Whether this card answers a degree you study for, which a 35-degree day is not."""
    key = _key_words(item)
    if not key & _THE_DEGREE_WORDS:
        return False
    return not bool(key & (_THE_HEAT_OF_THE_DAY - _THE_DEGREE_WORDS))


def _the_person_says_they_are_cold(typed):
    """Whether the line says the person themselves is cold or shivering.

    "the office is cold and i keep shivering" is about the office, and the shivering is the person
    in it: both cards answer something the line asked, so the place does not take it from them.
    """
    for at, word in enumerate(typed):
        if word not in _HOW_A_PERSON_IS_COLD and word not in _COLD_WORDS:
            continue
        for before in typed[max(0, at - 4):at]:
            if before in _SAYS_OF_THEMSELVES or before in ("feel", "feeling", "feels", "keep",
                                                          "keeps", "kept", "being", "got", "get"):
                return True
    return False


def _the_place_the_line_says_is_cold(typed):
    """The place the line predicates the cold of, or None.

    "the flat is freezing and the heating is on, why is it so cold" is about the flat: the cold is
    said of the place, so a card about a person who feels the cold is not the answer to it. Only a
    cold said of the place counts, because "im always cold and my flat is freezing" says both.
    """
    for at, word in enumerate(typed):
        if word not in _PLACES_PEOPLE_LIVE_IN:
            continue
        for next_word in typed[at + 1:at + 4]:
            if next_word in _COLD_WORDS:
                return word
            if next_word not in _BETWEEN_A_PLACE_AND_ITS_COLD:
                break
    return None


def _answers_the_cold_of_a_person(item, place=None):
    """Whether this card answers how cold a person feels rather than how cold a place is."""
    if item.domain not in FEELING_DOMAINS:
        return False
    key = _key_words(item)
    if not key & _COLD_WORDS:
        return False
    # A card that carries the place itself ("the flat", "the room") is about the place, whichever
    # module it is filed in: warm the room you are sitting in is a home card, and the health module
    # is listed among the feeling domains too.
    return place is None or place not in key


def _answers_the_cold_of_a_place(item, place):
    """Whether this card is about the place itself being cold, which is what the line asks."""
    if _answers_the_cold_of_a_person(item, place):
        return False
    key = _key_words(item)
    return place in key and bool(key & _COLD_WORDS)


def _the_card_for_the_place_first(place, reached):
    """The place's own card before a card about a person, when the line says the place is cold.

    "the flat is freezing and the heating is on, why is it so cold" reached the card about lifting a
    low mood - "flat" and "why" are its words - and the flat's own answer, warm the room you are
    sitting in, ranks under it. A card for the place is only put first when one reached the line;
    nothing is dropped, so a line that says only how cold the person is keeps its card.
    """
    if not reached:
        return reached
    for at, row in enumerate(reached):
        if at and _answers_the_cold_of_a_place(row[5], place):
            return [row] + reached[:at] + reached[at + 1:]
    return reached


def _the_ask_reading(understood, ask):
    """The reading cut down to the ask clause: what the setting said does not come with it.

    The ask is read from a copy of the line's reading, and a copy carries what the clause before
    it said. "my mum is 80 next week and we want a cake, what should i bake" kept the 80 in it,
    and after the Italy wedding line a ferry question kept the 35 degrees: a money card, a date
    card and a degree card can each win on a figure the ask never had. So the copy holds the
    ask's own words and only the numbers, the things and the subject written inside them.
    """
    asked = dict(understood)
    said = set(str(word).lower() for word in ask)
    asked["clean"] = " ".join(ask)
    asked["words"] = list(ask)
    asked["norm"] = list(ask)
    numbers = []
    for number in understood.get("numbers") or ():
        if not isinstance(number, dict):
            continue
        written = str(number.get("text") or "").lower().split()
        if set(written) & said or str(number.get("value")) in said:
            numbers.append(number)
    asked["numbers"] = numbers
    for key in ("entities", "things"):
        kept = []
        for thing in understood.get(key) or ():
            text = thing.get("text") if isinstance(thing, dict) else thing
            if isinstance(text, str) and set(text.lower().split()) & said:
                kept.append(thing)
        if key in understood:
            asked[key] = kept
    subject = understood.get("subject")
    asked["subject"] = subject if isinstance(subject, str) and subject.lower() in said else None
    return asked


def _the_ask_on_its_own(understood):
    """The ask clause's words when the line says the setting first and asks second, or None.

    "wedding in italy and 35 degrees, what do i wear", "my mum is 80 next week and we want a cake,
    what should i bake", "playing five a side sunday, what should i eat before": the words before
    the ask say where and when, and the ask is what the person wants answered. The understanding
    engine has already cut the line at its clauses and hands the ask over in `focus`, so this is
    the ask alone - and None when the line is one clause, or when its ask is the whole line.
    """
    focus = understood.get("focus")
    clauses = understood.get("clauses")
    if not isinstance(focus, list) or not isinstance(clauses, list) or len(clauses) < 2:
        return None
    ask = [str(word) for word in focus if isinstance(word, str) and word.strip()]
    if len(ask) < 2:
        return None
    # The ask has to be the end of the line and not all of it: "how long before a ferry should i
    # arrive" cuts at "before", and its second half is not a new subject - only a line that says
    # something and then asks ends in its ask.
    whole = understood.get("norm") or understood.get("words")
    if not isinstance(whole, list):
        return None
    line = [str(word).lower() for word in whole if isinstance(word, str)]
    tail = [word.lower() for word in ask]
    if len(tail) >= len(line) or line[-len(tail):] != tail:
        return None
    # The ask has to ask with its own question word. "how long before a ferry should i arrive at
    # the port" is cut at "before", and its second half ("should i arrive at the port") is not a
    # new subject but the same question - only "..., what do i wear" is a setting and an ask.
    if tail[0] not in _THE_WH_WORDS:
        return None
    return ask
