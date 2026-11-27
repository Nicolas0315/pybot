"""Part 8 of 8 of a large module, split out of `cooking`.

Everything here is re-exported from `cooking`, so callers import it from there as before.
"""
import re

# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.cooking_tables import DIET_VARIANTS, PANTRY
from .cooking_part_01 import (
    _FOOD,
)
from .cooking_part_02 import (
    CHEAP_DISHES, CHEAP_TAIL, CHEAP_TAIL_MEATFREE, _BAKED_GOODS,
)
from .cooking_part_03 import (
    _NOT_LACTOSE_WORDS, _record_says_lactose, _the_guest,
)
from .cooking_part_04 import (
    _bans, SWAP_WINDOW, GLUTEN_WORDS, DECIDING, REQUIRES, TURNS_DOWN, _sentences,
)
from .cooking_part_06 import (
    EMPTY_ASK_PHRASES, _STAND_IN_ASK, AND_NO, MEAL_ASK_PHRASES, SHORTAGE_WORDS, COOKED_KEEPING,
)
from .cooking_part_07 import (
    _mentions, _bans_of, _food_may, _food_named, _lactose_answer, _not_for_them, EAT_ANY,
    EAT_ANY_WORDS, EAT_ASK, EAT_ASK_BARE, EAT_ASK_IF, EAT_ASK_THEM, _any_meal, _bans_for, _bans_it,
    _bans_said, _foods_named, _one_food_answer, pointed, pointed_at_a_food, FANCY_ASK, SWAP_AFTER,
    SWAP_BEFORE, DAIRY_SAYS, NOT_THE_DAIRY, DAIRY, EGGS, EGG_SAYS, FISH, FISH_SAYS, MEAT, MEAT_SAYS,
    NUTS, NUT_SAYS, SHELLFISH, SHELLFISH_SAYS, SWAP_CLAUSE, CAUTION_SAID, NUT_SWAPS,
    SAYS_THE_FOOD_IS_OUT, DAIRY_SWAPS, GLUTEN, GLUTEN_FREE_ALREADY, GLUTEN_SWAPS, PLANT_SAID,
    SUBSTITUTE_ASK, _ask_about_the_food, without, _INGREDIENT_WORDS, _NOT_A_DISH, _fold, missing,
    _refused_foods, _STAND_IN_USE, _clean, DINNER_ASK_WORDS, DINNER_NAMED, LUNCH_AND_BREAKFAST,
    NOT_A_DINNER_LIMIT, _said_words, dish, meal, _MEAL_METHODS, _MEAL_TEXTS, _SPEAKS_OF_KEEPING,
    _COOKING_SENSE, _KEEP_TIME_ASK, _KEEP_WORDS, _WORD, _foods_said, _BACK_REFERENCE, _RECIPE_STEP,
    _TIMING, _TOTAL_TIME,
)


def _cheap_dinners(banned=frozenset()):
    """The cheap dinners, without the ones that name a food the line or the diet ruled out."""
    dishes = [one for one in CHEAP_DISHES
              if not _mentions(one, banned) and not _bans(tuple(one.split()), one, banned)]
    if not dishes:
        dishes = list(CHEAP_DISHES)
    if _mentions(CHEAP_TAIL, banned) or _bans(("mince",), CHEAP_TAIL, banned):
        tail = CHEAP_TAIL_MEATFREE
    else:
        tail = CHEAP_TAIL
    listed = ", ".join(dishes[:-1]) + " or " + dishes[-1]
    return ("Cheap dinners that feed four for about a fiver: " + listed + ". " + tail)


def _someones_else_can_eat(match, line, memory):
    """"Can she eat pesto" answered from her record, or None so the entries answer it."""
    guest = _the_guest(memory, line)
    if not guest:
        return None
    if not (guest.get("allergies") or guest.get("condition")):
        return None  # a diet alone is the store's question, and it answers it with a name
    said = " ".join(str(part or "") for part in match.groups() if part)
    food = _food_named(said) or _food_may(said)
    if not food:
        return None
    banned = _bans_of(guest)
    if not banned:
        return None
    if _record_says_lactose(guest) and not any(word in said.lower()
                                               for word in _NOT_LACTOSE_WORDS):
        # her record says a lactose intolerance, so how much milk sugar is in the food is the
        # answer rather than a no: "my wife is lactose intolerant" then "can she have cheese"
        answer = _lactose_answer(food, said)
        if answer:
            return answer
    return _not_for_them(food, banned, guest, said)


def suits_them(understood, memory):
    """A yes or no about one food, from what the person has said they avoid, or None.

    "Can I eat satay?" a turn after a peanut allergy is a question about peanuts, and the store
    holds that, so the reply says no and what to have instead. Only a line that asks in the first
    person, only a food whose recipe is known, and only once they have said what they avoid: an
    ordinary "can i eat raw eggs" is the food entry's question, not this one.
    """
    if not isinstance(understood, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "")
    if EAT_ANY.search(line):
        said_here = [word for word in re.findall(r"[a-z']+", line.lower())
                     if word not in EAT_ANY_WORDS]
        if said_here:
            return None  # "what can i have for lunch" names a meal, and the meal idea answers it
        banned = _bans_for(understood, memory)
        if not _bans_said(banned):
            return None
        return _any_meal(banned)
    about_them = EAT_ASK_THEM.search(line)
    if about_them:
        return _someones_else_can_eat(about_them, line, memory)
    # The same question asked the way people actually ask it a turn later: the food on its own,
    # under the condition that is already on record (see pointed_at_a_food).
    pointed = pointed_at_a_food(understood, memory)
    if pointed:
        return pointed
    banned = _bans_for(understood, memory)
    if not _bans_said(banned):
        return None  # they have said nothing they avoid: no answer of our own to give
    asked = EAT_ASK.search(line) or EAT_ASK_IF.search(line)
    bare = False
    if not asked:
        # "is the milk still ok" asks whether the thing in the fridge has gone off, whatever they
        # avoid, so a line with "still" in it keeps its storage entry.
        if not EAT_ASK_BARE.search(line) or "still" in line.lower():
            return None
        asked = EAT_ASK_BARE.search(line)
        bare = True
    if asked:
        named_foods = _foods_named(asked.group(0))
        if not named_foods:
            return None
        if len(set(named_foods)) > 1:
            # Two foods in one line is usually a dish ("fish and chips"), and the meal entries
            # read it. When one of the two is a food they avoid, though, the answer is still no
            # about that food: "can i eat a peanut butter sandwich" is a question about peanuts.
            named_foods = [food for food in named_foods
                           if _bans_it(food, banned)]
            if not named_foods:
                return None
        return _one_food_answer(named_foods[0], banned, asked.group(0), bare=bare)
    return None


def considered(understood, memory):
    """A dish the person is only thinking of, checked against what they avoid, or None.

    "i was thinking of a satay" is the same question as "can i eat satay" said as a plan, and a
    no is the answer they need. Only a no: a dish they can have is the plan's own answer, and a
    concrete suggestion that respects their ban ("i fancy a chicken curry" -> chickpea curry) is
    a better answer than a check, so this is asked only where no entry answered the line."""
    if not isinstance(understood, dict):
        return None
    line = str(understood.get("clean") or understood.get("text") or "")
    considering = FANCY_ASK.search(line)
    if not considering:
        return None
    banned = _bans_for(understood, memory)
    if not _bans_said(banned):
        return None
    food = _food_they_avoid(_foods_named(line[considering.end():]), banned)
    if food is None:
        return None
    return _one_food_answer(food, banned, line)


def _food_they_avoid(named_foods, banned):
    """The food in the line the ban actually reaches, or None.

    A line can name a safe food beside the one that is not ("a salad with cheese"), and the
    answer is about the food they cannot have."""
    for food in named_foods:
        if _bans_it(food, banned):
            return food
    return None


def _a_swap_not_a_dish(text, at, word):
    """Whether the food at a position in `text` is named to say what replaces it."""
    before = text[max(0, at - SWAP_WINDOW):at]
    after = text[at + len(word):at + len(word) + SWAP_WINDOW]
    return bool(SWAP_BEFORE.search(before) or SWAP_AFTER.match(after))


def _says_a_food(text, words):
    """The foods from `words` a piece of text names, as the words it used.

    A dairy word counts only when it is the dairy: `NOT_THE_DAIRY` steps over "oat milk" and
    "peanut butter", and "butter beans" is a bean.
    """
    found = []
    for word in words:
        for match in re.finditer(r"\b" + re.escape(word) + r"(?:s|es)?\b", text, re.I):
            if word in DAIRY_SAYS and NOT_THE_DAIRY.search(text[:match.start()]):
                continue
            if word == "butter" and re.match(r"\s+beans?\b", text[match.end():], re.I):
                continue  # a butter bean is a bean
            if _a_swap_not_a_dish(text, match.start(), match.group(0)):
                continue  # "a flax egg", "margarine for every 100g of butter": a swap, not a dish
            found.append(word)
            break
    return found


def _the_banned_words(banned):
    """The recipe words to check a reply against, for what this person avoids."""
    words = set()
    if MEAT & banned or FISH & banned:
        words |= MEAT_SAYS
    if FISH & banned:
        words |= FISH_SAYS
    if DAIRY & banned and "lactose" not in banned:
        # A lactose intolerance is not a dairy allergy: a reply naming cheese is the answer to
        # "can i eat cheese", not a food they said no to.
        words |= DAIRY_SAYS
    if EGGS & banned:
        words |= EGG_SAYS
    # A nut is not a meat and not a dairy, and this is the family with an epipen behind it: a
    # store that says "my daughter is allergic to nuts" must not leave the reply free to name
    # them. Pesto, satay and marzipan are here because that is how a nut arrives unannounced.
    if NUTS & banned:
        words |= NUT_SAYS
    if SHELLFISH & banned:
        words |= SHELLFISH_SAYS
    # Gluten is left out on purpose: the words that carry it are the names of the food itself
    # ("bread", "pasta", "flour"), so a coeliac asking "can i make bread without gluten" says
    # them in the line and the answer has to say them back. That family is answered by the
    # gluten-free readers that already choose between the blends and the bought loaf.
    return frozenset(words)


def _rewritten_outside_swaps(text, pattern, swap, leave=None):
    """`pattern.sub`, on the clauses of `text` that are not already saying the swap."""
    parts = re.split(r"([.!?:]\s+|,\s+)", text)
    for i in range(0, len(parts), 2):
        if not SWAP_CLAUSE.search(parts[i]) and not (leave and leave.search(parts[i])):
            parts[i] = pattern.sub(swap, parts[i])
    return "".join(parts)


def _uncautioned(text, words):
    """The banned words a reply offers, not the ones it warns about.

    An answer about an allergen has to name it: "nothing in the satay needs shellfish, but a
    bought one can have it in - check the label" is the most careful thing the bot says, and
    reading the word "shellfish" as the food served threw it away. A sentence that names the food
    and also tells the person to look at the label, ask, or avoid it is doing the job; a sentence
    that just lists it is not.
    """
    if not CAUTION_SAID.search(text):
        return set(_says_a_food(text, words))
    fresh = set()
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if CAUTION_SAID.search(sentence):
            continue
        fresh |= set(_says_a_food(sentence, words))
    return fresh


def _nut_swapped(text, banned, line):
    """The reply with a nut substitution swapped out, when that settles the whole reply.

    A card that explains what to use instead ("oat, soya or almond milk") is one word away from
    being usable. A card that is *about* the nut ("peanut butter is a decent everyday food ... buy
    one whose only ingredients are peanuts") is not: swapping its first words gave a reply that
    recommended sunflower seed butter and told a peanut-allergic person to buy a jar of peanuts.
    So a swap is kept only when nothing nutty is left afterwards.
    """
    if not (NUTS & banned) or not _a_nut_swap_is_safe(text, line):
        return text
    swapped = text
    for pattern, swap in NUT_SWAPS:
        swapped = _rewritten_outside_swaps(swapped, pattern, swap)
    if swapped == text or names_a_banned_food(swapped, banned, line):
        return text
    return swapped


def _a_nut_swap_is_safe(text, line):
    """A nut named to rule it out, or asked about by name, is not a substitution to rewrite.

    "No: peanut butter is made with nuts, so it is off the table for your son" is the answer, and
    swapping the words inside it gave "sunflower seed butter is made with nuts". A card that
    explains what to use instead ("oat, soya or almond milk") is the one place the word is a
    substitution rather than the subject.
    """
    if SAYS_THE_FOOD_IS_OUT.search(text):
        return False
    return not _says_a_food(str(line or ""), NUT_SAYS)


def fitted_for_the_one_talked_about(reply, banned, line=""):
    """The reply with somebody else's allergen taken out, or None when that cannot be done.

    The bans of a person who is not the one talking only ever *rule a reply out*: nobody asked for
    a card rewritten around a guest's diet, and rewriting one around a guest's allergy turned "ice
    cream is made with milk, so it is off the table for your daughter" into "made with plant
    milk". The one swap that is safe is the nut that sits in a substitution ("oat, soya or almond
    milk"), which is the word the card would have said differently anyway.
    """
    if not isinstance(reply, str) or not reply.strip() or not banned:
        return reply
    text = reply
    # A row with a version of itself written without the food is that version (the office snack
    # list without the nuts), so the veto only fires on what is left after that.
    text = _nut_swapped(DIET_VARIANTS.get(text.strip(), text), banned, line)
    if names_a_banned_food(text, banned, line):
        return None
    return text


def names_a_banned_food(reply, banned, line=""):
    """Whether the reply serves a food somebody in this chat cannot eat."""
    if not isinstance(reply, str) or not reply.strip() or not banned:
        return False
    words = _the_banned_words(banned)
    if not words:
        return False
    said_already = set(_says_a_food(str(line or ""), words))
    said_already |= {word[:-1] for word in said_already if word.endswith("s")}
    left = [word for word in _uncautioned(reply, words)
            if word not in said_already and word[:-1] not in said_already]
    return bool(left)


def fits_the_diet(reply, banned, line=""):
    """The reply, fitted to what this person eats, or None when it cannot be fitted.

    A reply that names a food the person avoids is not an answer to them however good the rest
    of it is: "im vegan" then "what can i do with a cabbage" was answered "fry it in butter", and
    a vegetarian's cabbage was "fried with chopped bacon or smoked sausage". The choosing above
    only reads the rows it picks from, and the rows are written for everyone.

    Three things, in order. A dairy word that has an everyday swap is swapped, because "softened
    in butter" and "softened in oil" are the same instruction - except where the word is not the
    dairy at all ("peanut butter", "butter beans", "coconut milk"). What is left that the person
    cannot eat is then looked for again, and the reply is handed back as unusable - the caller
    tries the row below it rather than serving a food they said no to.

    A food the line itself named is not a fault: a vegetarian asking how to cook bacon for other
    people is asking about bacon, and the answer has to say it. Gluten is not checked here at
    all: its words are the names of the food ("bread", "flour"), so the line and the answer share
    them, and the gluten-free readers already answer that family.
    """
    if not isinstance(reply, str) or not reply.strip() or not banned:
        return reply
    text = reply
    line_words = set(_says_a_food(str(line or ""),
                                 set(_the_banned_words(banned)) | set(GLUTEN_WORDS)))
    if GLUTEN & banned:
        for word, pattern, swap in GLUTEN_SWAPS:
            if word not in line_words:
                text = _rewritten_outside_swaps(text, pattern, swap,
                                                leave=GLUTEN_FREE_ALREADY)
    words = _the_banned_words(banned)
    if not words:
        return text
    if _ask_about_the_food(str(line or "").lower(), len(str(line or ""))):
        # The line asks whether a named food is vegetarian or vegan, and the answer to that is
        # what might be in it: "are chips vegetarian" is answered about beef dripping and "is
        # wine vegetarian" about isinglass, and the filter that keeps a refused food out of an
        # answer must not throw those away. The words are the whole point of the verdict.
        return text
    said_already = set(_says_a_food(str(line or ""), words))
    # "egg" in the line and "eggs" in the answer are the same food: "how long do i boil an egg"
    # names the egg itself, and a reply that says "lower eggs into boiling water" is answering the
    # question rather than naming a food the person avoided. Without this the plural was read as a
    # different food and a vegan asking about boiling an egg got a shrug.
    said_already |= {word[:-1] for word in said_already if word.endswith("s")}
    left = [word for word in _uncautioned(text, words)
            if word not in said_already and word[:-1] not in said_already]
    if not left:
        return text
    # A variant is written to answer everything the person said, so it is only used when the ban
    # it covers is the whole of the ban: the nut-free snack list is not an answer to somebody who
    # is allergic to nuts *and* shellfish, and a card that says "nut-free" there answers half of
    # what they told us. The acknowledgement that names both is the better reply.
    nuts_only = NUTS & banned and not (banned - NUTS)
    if MEAT & banned or FISH & banned or nuts_only:
        # A row can have a version of itself written for the people the row's own words leave
        # out: the cabbage recipe is bacon, the swede is "alongside sausages", the courgette is a
        # pasta dish and the office snack list is nuts. Those are the same job said without the
        # food, and a shrug is a worse answer than the job. The key is the row's exact text, so a
        # family with no variant written for it simply finds nothing here and is handled below.
        text = DIET_VARIANTS.get(text.strip(), text)
    if DAIRY & banned and "lactose" not in banned and not PLANT_SAID.search(text):
        # A reply that already says it is the plant version is written for this person, and the
        # swap rewrites it into nonsense: the dairy-free card says "watch the labels for whey,
        # casein, milk powder and lactose", and swapping there gave "plant milk powder".
        for pattern, swap in DAIRY_SWAPS:
            text = _rewritten_outside_swaps(text, pattern, swap)
    text = _nut_swapped(text, banned, line)
    said = _says_a_food(text, words)
    if PLANT_SAID.search(text):
        # A reply that says it is the vegan or the vegetarian version is written for the person
        # who cannot have the thing: the vegan bake says "60g of yoghurt or half a mashed banana"
        # and "a flax egg ... for each egg", and the dinner-party plan says "beats a meat main".
        # Reading those words as the dish took the entries that know the job away from the person
        # who needs them.
        said = [word for word in said
                if word not in DAIRY_SAYS and word not in EGG_SAYS
                and word not in MEAT_SAYS and word not in FISH_SAYS]
    left = [word for word in said if word not in said_already]
    if not left:
        return text
    if SUBSTITUTE_ASK.search(str(line or "").lower()):
        # The line asks what to use *instead of* the food, so the food is the question rather than
        # a fault in the reply: "im vegan" then "what can i use instead of eggs" is the bananas and
        # the flax, and the dairy in the same card is already swapped by now.
        return text
    if SAYS_THE_FOOD_IS_OUT.search(text):
        # the reply names the food to rule it out, which is the answer to "can i eat eggs"
        return text
    without = _the_card_without_that_sentence(text, left, words)
    if without:
        # The food is one sentence of a card that is otherwise the right answer: fried rice is
        # rice, garlic, ginger and soy with an egg scrambled in at the end, and a vegan gets the
        # card without the egg rather than "that's beyond what I know well".
        return without
    first = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]
    if not [word for word in _says_a_food(first, words) if word in left or word[:-1] in left]:
        # The food is a mention further down a card about something else: the roast-sides card is
        # the vegetables and the joint is context, and the protein card names meat in its list of
        # sources. Blanking those two turned "what can i have with a roast" and "what can i eat for
        # protein" into a hedge, which is a worse answer than a card whose subject is not the food
        # they refused. A card that is *about* the food says so in its first sentence.
        return text
    return None


def _the_card_without_that_sentence(text, left, words):
    """`text` with the parts that name a food they cannot eat taken out, or None.

    A recipe is one long sentence, so the unit is the clause rather than the sentence: fried rice
    is "heat a little oil, add the cold rice and fry it hard, **then** push it aside and scramble
    an egg in the gap". Taking the egg's clause out leaves the dish, and the person who said they
    are vegan gets the rice instead of "that's beyond what I know well".

    Only when there is a card left: something has to have been dropped, and what stays has to be
    most of the text, or the answer is a fragment rather than a dish.
    """
    bits = re.split(r"([.!?]+\s+|;\s+|,\s+(?:then|and)\s+)", str(text).strip())
    keep = []
    dropped = 0
    for index in range(0, len(bits), 2):
        part = bits[index]
        names = _says_a_food(part, words)
        if [word for word in names if word in left or word[:-1] in left]:
            dropped += 1
            continue
        keep.append(part)
    if not dropped or not keep:
        return None
    if not keep[0].strip(" ,.;:") or keep[0] is not bits[0]:
        # The first clause carries the instruction ("whisk the flour into the meat juices..."),
        # and a card that starts at its second clause starts at "simmer it", with nothing for the
        # "it" to be. A dish that opens with the food they cannot eat has no version here.
        return None
    said = ", ".join(part.strip(" ,.;:").lower() if index else part.strip(" ,;")
                     for index, part in enumerate(keep) if part.strip(" ,.;:"))
    if not said:
        return None
    if len(said) < 40 or len(said) < 0.55 * len(str(text).strip()):
        return None
    said = said[0].upper() + said[1:]
    return said if said.endswith((".", "!", "?")) else said + "."


def _recipe_for_unknown_dish(lowered):
    """True for "a recipe for <dish>" where the dish is not food the kitchen knows.

    The meal entry's key admits `recipe`, because "need a cheap recipe with chickpeas" is a
    meal question. It also admits "need a recipe for shortbread", which is a question about
    shortbread and nothing the table can make, so that one gets the honest hedge. An
    ingredient the pantry knows stays a meal question ("recipe with mince", "recipe for beans").
    """
    match = re.search(r"\brecipe\b(?:\s+(?:for|of|to make))?\s+(.*)$", lowered)
    if not match:
        return False
    tail = re.findall(r"[a-z']+", match.group(1))
    if not tail:
        return False
    if any(word in ("idea", "ideas", "meal", "dinner", "tea", "supper") for word in tail):
        return False
    # "whats a quick recipe for tonight" names no dish at all: "quick", "easy" and "tonight" say
    # how and when, not what, so they are dropped before the dish test and an empty tail stays a
    # meal question. Without this the line was a recipe for a dish called "tonight" and got the
    # honest hedge.
    food_words = [word for word in tail if word not in _NOT_A_DISH][:3]
    if not food_words:
        return False
    return all(word not in _INGREDIENT_WORDS and word not in _FOOD for word in food_words)


def pantry_idea(name):
    """The pantry's own idea for one food, by name, or None.

    Asked by the use-up table in bot/knowledge/meals.py, which has to know whether the idea it is
    about to be beaten by is a dish (a use for the food) or a way of cooking it from raw.
    """
    folded = _fold(str(name or "").lower())
    if not folded:
        return None
    for aliases, idea in PANTRY.values():
        for alias in aliases:
            key = _fold(str(alias).lower())
            if key == folded or key == folded.rstrip("s") or key.rstrip("s") == folded:
                return idea
    return None


def unusable(text, understood):
    """True when this answer tells you to use something the line says it has not got."""
    gone = missing(understood)
    if not gone or not isinstance(text, str) or not text.strip():
        return False
    clean = str(understood.get("clean") or "").lower()
    if any(phrase in clean for phrase in EMPTY_ASK_PHRASES):
        # "theres nothing in for tea" is a line that has ruled out everything, so every food
        # an answer names reads as something the kitchen has not got and the empty-kitchen
        # answer, whose whole point is the shopping list, was thrown away and the line fell
        # back to an acknowledgement. Naming the food is the answer to that line.
        return False
    words = set()
    for name in gone:
        words.update(REQUIRES.get(name, ()))
    for sentence in _sentences(text.lower()):
        for word in words:
            if not re.search(r"\b" + re.escape(word) + r"\b", sentence):
                continue
            if any(one in sentence.split() for one in TURNS_DOWN):
                continue
            if any(one in sentence for one in DECIDING):
                continue
            return True
    return False


def refused_foods(understood):
    """The foods a line says somebody at the table will not eat, worked out by the kitchen.

    A reader that has to decide whether the line is about a food ruled out or about the food
    itself asks this, so both are read the same way: "she wont eat cheese what can i cook" is a
    dinner with cheese left out, not a question about cheese.
    """
    if not isinstance(understood, dict):
        return frozenset()
    said = str(understood.get("clean") or understood.get("text") or "")
    return frozenset(_refused_foods(said))


def asks_for_a_stand_in(understood):
    """True when the line is asking what stands in for a food, not what to cook with it."""
    said = _clean(understood) if not isinstance(understood, dict) else _clean(understood)
    if any(phrase in said for phrase in _STAND_IN_ASK):
        return True
    return bool(_STAND_IN_USE.search(said))


def a_dinner_without(understood, memory=None):
    """A dish for a line that rules a food out and asks what to cook, or None.

    "she wont eat cheese what can i cook" was answered with cheese's calorie figure, and "my wife
    wont eat bread what can i cook" with the loaf's method, which is the one thing they cannot
    use. The refusal is the kitchen's own reading (`refused_foods`), so the two agree on what a
    refusal is, and the dish is the pantry's, so it is the same dinner it picks for an allergy.
    A line that only says the food is refused keeps its substitute answer: nothing is being
    cooked yet, so there is no dish to leave it out of.
    """
    said = _clean(understood)
    if asks_for_a_stand_in(understood):
        # the thing is being changed, not the dinner: see _STAND_IN_ASK above
        return None
    if not _refused_foods(said):
        return None
    if not isinstance(memory, dict):
        memory = {}          # the readers below want a store to look in, never None
    if any(phrase in said for phrase in SHORTAGE_WORDS):
        return None
    if _refused_foods(said) <= NOT_A_DINNER_LIMIT:
        return None          # the baking cupboard, not the dinner: the substitute is the answer
    words = set(_said_words(understood))
    if any(phrase in said for phrase in AND_NO) and not words & DINNER_NAMED:
        # "what can i make with no eggs" is asked at the baking cupboard and wants the substitute
        # (60g of yoghurt, half a banana, flax); a dish of mince and cabbage answers nothing in
        # it. The same food said as a refusal, or with a meal named, is the dinner question.
        return None
    asking = any(phrase in said for phrase in MEAL_ASK_PHRASES)
    if not asking:
        asked = understood.get("asks") if isinstance(understood, dict) else None
        asking = bool(asked) and bool(words & DINNER_ASK_WORDS)
    if not asking:
        return None
    if any(word in said.split() for word in LUNCH_AND_BREAKFAST):
        return None          # those ideas are their own cards, and they respect the exclusion
    cooked = dish(understood, memory) or meal(understood, memory=memory)
    if not (isinstance(cooked, str) and cooked.strip()):
        return None
    return None if unusable(cooked, understood) else cooked


def _is_meal_answer(said):
    """True when this reply is one whole meal from this table, with or without its trimmings."""
    said = str(said or "").strip()
    if not said:
        return False
    if said in _MEAL_TEXTS:
        return True
    method = said.partition(": ")[2]
    return len(method) > 40 and any(m.startswith(method) for m in _MEAL_METHODS)


def speaks_of_keeping(reply):
    """Whether a reply says how long something keeps, so a keeping line can be answered by it."""
    return bool(isinstance(reply, str) and _SPEAKS_OF_KEEPING.search(reply))


def keeping_ask(understood):
    """True for "how long does a cooked chicken last" - how long it KEEPS, not how long it cooks.

    The words have to ask how long, carry a keeping word, and carry none of the words that put the
    question back in the oven or the pan: "how long do i keep stirring it" is cooking.
    """
    if not isinstance(understood, dict):
        return False
    clean = str(understood.get("clean") or "").lower()
    words = set(_WORD.findall(clean))
    # "roast" is the one word that is a joint of meat as often as it is a verb: "how long does a
    # roast keep" is a keeping question, and the words that only ever name the doing are left to
    # rule this out.
    if not words & _KEEP_WORDS or words & (_COOKING_SENSE - {"roast", "roasting"}):
        return False
    return bool(_KEEP_TIME_ASK.search(clean))


def _the_answer_names_a_food(said):
    """Whether the answer names a food the pantry and the staples table know.

    Whole words, folded: the same set the keeping entries are keyed by, so an answer about a dish
    passes and an answer about anything else does not.
    """
    return bool({_fold(word) for word in _WORD.findall(str(said or "").lower())} & _foods_said())


def keeping_followup(understood, memory):
    """The keeping answer for "how long does that keep" after a dish we just gave.

    A meal answer states how long the dish takes, and a keeping question leans on the answer just
    given ("ive got chicken and spinach in the fridge", "how long does that keep"), so the time in
    it was read out as the answer: twenty minutes is how long it takes to cook, not how long it
    keeps. The keeping fact is the same for any cooked dish, so it is what this returns. A line
    that names a food of its own keeps its own entry ("how long does cooked chicken keep").
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    clean = str(understood.get("clean") or "").lower()
    words = set(_WORD.findall(clean))
    if not words & _KEEP_WORDS or words & _COOKING_SENSE:
        return None
    if not _KEEP_TIME_ASK.search(clean):
        # It has to ask how long: "my knee keeps clicking, is that normal" and "can i freeze it"
        # carry a keeping word and point back at the answer, and neither asks this.
        return None
    if not words & _BACK_REFERENCE:
        return None  # a keeping question about a food of its own is the entries' to answer
    for turn in ((memory.get("turns") or [])[-3:] if isinstance(memory.get("turns"), list) else []):
        said = str(turn.get("user") or "").lower() if isinstance(turn, dict) else ""
        if any(name in said for name in _BAKED_GOODS):
            return None
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    if turns[-1].get("module") != "answers":
        return None
    said = str(turns[-1].get("bot") or "")
    if set(_WORD.findall(said.lower())) & _KEEP_WORDS:
        # The answer just given already said how long it keeps, and trimming it here leaves the
        # conversation without the dish in mind: the next follow-up then gets the whole meal
        # answer again, word for word. So this one keeps its own answer.
        return None
    if not _TIMING.search(said) and not _RECIPE_STEP.search(said):
        return None  # nothing was cooked here to keep
    # A step word is not proof on its own that food was cooked: `add`, `serve`, `season` and
    # `drain` are ordinary English too, so an answer that says "several small things adding up"
    # matched `add` and the answer to "how long will that take to sort out" after it was the
    # cooked-food card. The dish it was about is a food, so the answer has to name one.
    if not _the_answer_names_a_food(said):
        return None
    return COOKED_KEEPING


def timing_followup(understood, memory):
    """The time our own last meal answer gave, when the line only asks how long it takes.

    "i have chickpeas and spinach, what can i make" gets a dish and its time; the next line,
    "how long does that take", is asking about the answer just given rather than about a food
    of its own. The time already in that answer is the reply. Passes on anything that names a
    food we have not just talked about, so "how long do i boil an egg" keeps its own entry.
    """
    if not isinstance(understood, dict) or not isinstance(memory, dict):
        return None
    asks = set(understood.get("asks") or ())
    words = set(understood.get("words") or ())
    clean = str(understood.get("clean") or "").lower()
    if not (asks & {"how_long"} or "how long" in clean or "how many minutes" in clean):
        return None
    if not words & _BACK_REFERENCE:
        # A time question with no food of its own in it leans on the answer just given, whether
        # it says so or not: after the chicken traybake, "how long in the oven" was answered by
        # the whole-bird rule ("20 minutes per 500g plus 20 ... 1 hour 40 for a 2kg bird"), and
        # the dish on the screen said 35 to 40 minutes. A word that names a food still sends the
        # line to its own entry, so "how long do i boil an egg" keeps its answer.
        if {_fold(word) for word in words} & set(_INGREDIENT_WORDS):
            return None
        if {_fold(word) for word in words} & _KEEP_WORDS:
            # The lean is for a cooking time, and "how long" also asks how long a thing keeps.
            # "how long does soup keep" after a chicken traybake was answered with raw chicken's
            # one to two days, because soup names no ingredient and the line pointed at nothing.
            # A keeping question that names its own subject is the store's, so the lean stands
            # down; "how long does that keep" points back and never reaches here.
            return None
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns or not isinstance(turns[-1], dict):
        return None
    last = turns[-1]
    said = str(last.get("bot") or "").strip()
    if last.get("module") != "answers":
        # A reply that says the dish answer again is that answer still on the screen, whichever
        # module fronted it: "no cheese though" after a frittata is answered with "Skip the
        # cheese: A frittata: ...", and "and how long does that take" next is the dish's time,
        # not a new question. Read from the store's own record of the answer just given.
        kept = memory.get("last_answer")
        kept_text = str((kept or {}).get("reply") or "").strip() if isinstance(kept, dict) else ""
        head = kept_text[:40].lower()
        if not kept_text or len(kept_text) < 40 or head not in said.lower():
            return None
        said = kept_text
    # Only a meal idea from this table is a whole dish with a time of its own. An entry's answer
    # is a fact with times inside it ("9 to 10 minutes", "a minute less"), and "how long does
    # that take" is better left to the entries than answered with one of those.
    if not _is_meal_answer(said):
        return None
    # The time that answers this is the one stated for the whole dish, and a good answer says it
    # once: "About 40 minutes start to finish" as the first sentence, or an opening method whose
    # one time is the cook's ("...and simmer covered for 20 minutes"). The closing sentence is the
    # last place to look, not the first - it is often a step's own time, so "One-pan chicken and
    # rice ... simmer covered for 20 minutes. Let it stand 5 minutes" was read as five minutes.
    sentences = [part for part in re.split(r"(?<=[.!?])\s+", said) if part.strip()]
    total = [part for part in sentences if _TOTAL_TIME.search(part)]
    when = None
    for part in total + [part for part in sentences if part not in total]:
        times = {" ".join(found.group(0).lower().split())
                 for found in _TIMING.finditer(part)}
        if len(times) == 1:
            when = times.pop()
            break
    if when is None:
        return None
    said_words = set(_fold(word) for word in _WORD.findall(said.lower()))
    named = [word for word in understood.get("words") or ()
             if _fold(word) in _INGREDIENT_WORDS and _fold(word) not in said_words]
    if named:
        # A food of its own that our answer never mentioned: this is a new question, not a
        # question about the dish we just gave.
        return None
    return "About %s for that one, start to finish." % when
