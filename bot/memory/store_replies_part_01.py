"""Part 1 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..memory import last_user, name, others, remember, remember_other, user
from ..memory import ack
from ..memory import condition
from ..memory import facts as extract
from ..knowledge import units
from ..memory.store_lines import REPEAT_ADVERB, LIMITS, RETRACT_SAY, KIN_ASK, IN_LAW_AFTER_TEXT
from ..memory.relations import CHAT_TAIL, _a_list_of_names, _animal_family
from ..modules.memory_tables import COUNT_ANIMAL, COUNT_BARE, WHEN_INVERTED, WHEN_INVERTED_SUBJECT
from bot.memory.corrected import _many



def _a_count_ask(low):
    """The animal a "how many" ask counts, or "" when the line is not that ask.

    "how many cats", "how many cats do i have", "how many have i got": the count the person
    gave is the answer. None when the line is not a count ask at all.
    """
    match = COUNT_ANIMAL.match(low)
    if match:
        word = match.group(1).lower().rstrip("s")
        return "pet" if word in ("pet", "puppie", "kitten", "bunnie", "horsie") else word
    if COUNT_BARE.match(low):
        return "any"
    return None


ASKED_ALL = re.compile(
    r"(?<!not )(?<!isnt )(?<!wasnt )\bwhat did i (?:just )?(?:ask|want to know)\b"
    r"(?![^.?!]*\babout\b(?!\s+(?:me|it|that|this|them|us|earlier|before|just now|first|"
    r"originally|already|so far|last time|the other day|that time)\b))"
    r"|\bwhat was it i asked\b"
    # The reminder wrapper drops off in `_bare` ("can you remind me what i asked about"), and
    # the ask arrives without its "did": the same rule as above - a time or nothing after
    # "about" is the whole conversation, a named thing is that one recall.
    r"|(?<!not )(?<!isnt )(?<!wasnt )\bwhat i (?:just )?(?:asked|want to know)\b"
    r"(?=\s*(?:about\s*)?(?:\?|$|again\b|please\b|before\b|earlier\b|just now\b|first\b|"
    r"then\b|so far\b|already\b|the other day\b))")


MORE_OF_IT = re.compile(r"\b(what|anything|everything)\s+(?:else|more|other(?: things?)?)\b")


FIRST_ASK_BARE = re.compile(
    r"\bwhat i (?:asked|said|tell|told)(?: you)?(?: \w+){0,2} (?:first|at the (?:very )?start|"
    r"at the (?:very )?beginning|in the (?:very )?beginning)\s*\??$"
    # "remind me where we started" is the same ask about the opening line, and without it the
    # wrapper came off to a line nothing claimed and the composer answered "Thanks for telling me"
    # to a question.
    r"|\bwhere (?:we|it|this|the (?:chat|conversation)) (?:all )?(?:started|began)\s*\??$"
    # "which question did i start with" is the same ask about the opening line. The words have to
    # name a question or a thing and a first, so an ordinary "which route did i take" is not one.
    r"|\bwhich (?:question|thing) (?:did i|i) (?:ask|asked|say|said|start with|started with|"
    r"begin with|began with)\s*(?:you\s*)?(?:first|with)?\s*\??$")


FIRST_ASK = re.compile(
    FIRST_ASK_BARE.pattern + r"|"
    r"\bwhat did i (?:ask|say|tell)(?: you)?(?: \w+){0,2} (?:first|at the (?:very )?start|"
    r"at the (?:very )?beginning|in the (?:very )?beginning)\s*\??$"
    r"|\bwhat (?:was|were) (?:the |my )?(?:very )?first (?:thing|question|message|line|one)"
    r"(?: (?:i|you) (?:asked|said)(?: you)?)?\s*\??$"
    r"|\b(?:how|where) did (?:we|(?:this|our|the) (?:chat|conversation)) (?:start|begin|get started)\b"
    r"(?=$|[?.!,]| (?:it|this|here|that|off|talking|chatting|the chat|this chat|the "
    r"conversation|this conversation)\b)"
    r"|\bwhat did i say (?:at |in )?the (?:start|beginning)\s*\??$"
    r"|\bdo you remember what i (?:asked|said)(?: you)? first\s*\??$"
    r"|\bwhat did i (?:ask|say) first\s*\??$"
    # The asking is often in front of the question - "can you remember what i told you at the
    # start", "do you remember what i said at the beginning" - and the capability card was
    # answering those with "nothing from before this chat, sorry" for a chat the store knows.
    r"|\b(?:can|could|do|did|would) you remember what i (?:asked|said|told)(?: you)?(?: \w+){0,2}"
    r" (?:first|at the start|at the beginning)\s*\??$"
    # The wrapper comes off in `_bare` before this is read, so the same ask arrives as a bare
    # clause: "do you remember what i asked you first" is read as "what i asked you first", and
    # that matched nothing - the line fell through to the quote-their-last-line reader and came
    # back as the turn before it ("Your own words were: ...") for a chat whose first line the
    # store has. The words after the verb are "you", the thing asked about and the time, in any
    # order: "what i said to you at the very start" is the same ask.
    r"|\bwhat i (?:asked|said|told|mentioned)(?: you)?(?: \w+){0,3}?\s+"
    r"(?:very |the )?(?:first|start|beginning|begin)\b\s*\??$"
    r"|\bmy first (?:question|message|line|words)\b\s*\??$"
    r"|\bwhat did i (?:ask|say|tell)(?: you)? when we (?:started|began|first)\s*\??$"
    r"|\bremind me how (?:this|we|the chat|the conversation) (?:started|began)\b"
    # The whole line has to be the meta-question. Filed as an ending only, "the argument
    # started when he came home late and i dont know how it started" was read as a question
    # about the chat and told "We're just beginning - you go first."
    r"|^(?:and |so |but )?(?:how|where) (?:did )?(?:this|the chat|our conversation|it)"
    r" (?:start|started|begin|began)\s*[?.!]*$")


REPEAT_TAIL = re.compile(r"\b" + REPEAT_ADVERB + r"\b", re.I)


REPEAT_ASK = re.compile(
    r"\b(?:say|said|repeat|tell me|read|hear|catch)(?: it| that| this)? again\b"
    r"|\bwhat did you (?:just )?say\b"
    r"|\bwhat did you tell me(?: (?:just )?now| earlier| before| so far)?\b"
    r"|\bwhat you (?:just )?(?:said|told me)\b"
    r"|\bcan you (?:repeat|say) (?:that|it)(?: again)?\b"
    r"|\bsay (?:that|it) once more\b"
    # The bare verb, which is the commonest way of all to ask and the one shape missing: "repeat
    # that", "repeat it please", "please repeat". Every other form here carries "again" or "say",
    # so a person who typed the verb on its own got the small-talk fallback ("Got it. Is there
    # anything you'd like a hand with?") with the answer they wanted still on the screen behind it.
    # The two guards already keep the rest out: REPEAT_START wants the line to open on the ask, so
    # "on repeat" and "i repeat myself" are not asks, and REPEAT_WORDS wants every content word to
    # be part of the ask, so "repeat the bit about resting it" still goes to the answer.
    r"|\b(?:please\s+)?repeat\b(?!\s+(?:after|myself|yourself))"
    # The same ask with the verb "say" and no "again": "say that slower", "say it simpler". The
    # person is not asking for a different answer, they are asking for that one again at a speed
    # they can follow, and the echo ("Got it — say that slower.") said nothing.
    r"|\bsay (?:that|it) (?:again|once more|slower|slowly|simpler|clearer)\b"
    # The same ask with the verbs people reach for when the answer was long: "explain that
    # again", "go over that again", "run that by me again". Every one of them names the last
    # thing said and nothing of its own, and REPEAT_WORDS keeps the rest out, so "go over the
    # rules of chess" and "explain why the sky is blue" stay about the thing. Before this the
    # line fell to the composer, and "explain that again" was answered "Got it - explain that
    # again" with the answer still on the screen.
    r"|\bexplain (?:it|that|this)(?: (?:again|once more|slower|more slowly|simply|more simply))?\b"
    r"|\b(?:go|walk|talk)(?: me)? (?:over|through) (?:it|that|this)\b"
    r"|\brun (?:it|that|this) by me\b"
    r"|\brun (?:it|that|this) (?:again|once more)\b"
    # The same ask pointed at a part: "the last bit again", "the last part again". "the last
    # bit" is the last thing said, not a thing of its own, so a line whose only subject is that
    # is asking for the answer again.
    r"|\bthe (?:last|final) (?:bit|part)\b"
    # The ask said as a complaint about the answer: "you lost me", "sorry you lost me there".
    r"|\b(?:you(?:'ve| have)? lost me|i lost you)\b"
    r"|\bwhat was that\b"
    r"|\bcome again\b"
    r"|\bpardon\b"
    r"|\bi missed (?:that|it)\b"
    r"|\bone more time\b"
    # A repeat ask that names the figure it wants: "how long did you say", "when did you say",
    # "how much did you say it was". The person is not asking what the bot is; they want the
    # figure out of the answer they already have, and the words in front of "did you say" say
    # which figure.
    r"|\b(?:how long|how much|how many|how often|how soon|what time|when|where)\s+"
    r"did you (?:just )?say\b"
    # "repeat that" and "repeat that please" ask for the last reply as surely as "say that again"
    # does, and "again" is not always said. Anchored at the end of the line so "repeat that
    # step" and "he repeats that every day" are about the thing and not about the conversation.
    + r"|\brepeat (?:that|it|this)(?:\s+" + REPEAT_ADVERB + r"){0,2}\s*[.!?]*$")


LAST_LINE_ASK = re.compile(
    r"\bwhat did you just say\b|\bwhat was that\b|\bpardon\b|\bcome again\b"
    r"|\bi missed (?:that|it)\b|\bdid(?:n't|nt) catch\b", re.I)


REPEAT_WORDS = frozenset("""
say said repeat again tell told speak word pardon missed catch hear one time just last line
remind reminded you please sorry thanks thank cheer cheers ta come that this it me now thing
slower slowly simpler clearer bit
explain explained go going through walk talk run ran by part parts lose lost there
how long much many often soon when where time
earlier ago previously minute moment before already so far up to now until now
""".split())


WHOLE_ASK = re.compile(
    r"^(?:(?:and|so|but|ok|okay|oh|right|well|yes|yeah|ta|please|then)\s+)*"
    r"(?:"
    r"in full|in the full|in full please|the full (?:thing|version|answer)"
    r"|the whole (?:thing|answer|lot|of it)|the whole of it please"
    r"|all of (?:it|that|this)|all of it please|both of (?:them|those)"
    r"|the lot|the lot please"
    r"|from the (?:top|start|beginning)|from the very (?:top|start|beginning)"
    r"|start (?:again )?from the (?:top|start|beginning)"
    r"|(?:say|tell me|give me) (?:it all|it in full|all of it|all of that|the lot)"
    r")"
    r"(?:[\s,]+(?:please|then|now|thanks|ta))*[\s.,!?]*$", re.IGNORECASE)


REPEAT_START = re.compile(
    r"^(?:(?:and|so|but|ok|okay|oh|then|well|right|hmm|um)\s+)*"
    r"(?:say|repeat|tell|read|hear|catch|can|could|would|will|what|sorry|pardon|please|thanks|"
    r"thank you|cheers|ta|come|again|"
    r"how|when|where|remind|reminded|one more|i missed|i didn't catch|i didnt catch|"
    r"explain|go|walk|talk|run|the|you|i lost|"
    r"didn't catch|didnt catch|do you|excuse me)\b")


REMINDER_MID = re.compile(
    r"\b(?:please |can you |could you |would you )?(?:remind me|tell me again|ask me again)"
    r"(?: again)?\b[\s,]*"
    # "do you know my age?", "do you remember what I do": the same reminder said as a question
    # about the bot's memory. The remembering word carries nothing of the fact, so it comes off
    # with the rest of the wrapper and the ask behind it is read like any other ("my age",
    # "what i do"). A question about the world in the same words ("do you know how to fix a
    # tap") loses only its opener, and no reader of the store answers what is left.
    r"|^\W*(?:do|did|can|could) (?:you|u) (?:still |actually |even |really )?"
    r"(?:know|remember|recall)\b[\s,]*")


REMINDER_HEAD = re.compile(
    r"^(?:(?:and|but|so|ok|okay|oh|also|right|well|sorry|hi|hey|just|quick|one more)\b[\s,]*)+")


REMINDER_TAIL = re.compile(r"(?:[\s,]*\b(?:again|please)\b)+$")


ABOUT_HEAD = re.compile(r"^(?:(?:and|but|so)\s+)?what about\s+")


ACTIVITY_ASK = re.compile(
    r"(?:\bwhat (?:was|am|were) i (?:making|cooking|baking|planning|doing|up to)|"
    r"\bwhat i (?:(?:just )?said )?(?:i )?was (?:doing|up to|making|cooking|baking|planning)|"
    r"\bwhat was i (?:going to|meant to) do)\b"
    r"(?!\s*(?:wrong|badly|bad|differently|silly|stupid|right|here|now))"
    # "what am i doing this week" asks what is coming up, not what they said they were doing.
    r"(?![^.?!]*\b(?:this|next|coming)\s+(?:week|weekend|month|year|monday|tuesday|wednesday|"
    r"thursday|friday|saturday|sunday)\b|\btonight\b|\btomorrow\b|\bcoming up\b)")


PLAN_WORDS = re.compile(r"\bwhat (?:am i|are we) planning\b|\bwhat (?:have|has) (?:i|we) got\b|"
                        r"\bwhat do (?:i|we) have\b|\bcoming up\b|\bon for (?:me|us)\b")


UP_TO_ASK = re.compile(r"\bwhat (?:am i|are we) (?:planning|up to)\b|"
                       r"\bwhat (?:was|were) (?:i|we) (?:planning|up to)\b"
                       r"(?!\s*(?:wrong|badly|bad|differently|silly|stupid|right))")


NAMED_ACTIVITY = re.compile(r"\bwhat (?:was|am|were) i (?:making|cooking|baking)\b|"
                           r"\bwhat (?:was|am) i planning to\b")


ACTIVITY_WORDS = re.compile(
    r"\b(?:making|cooking|baking|roasting|preparing|building|painting|writing|sorting|"
    r"fixing|mending|planning|organising|organizing|packing|knitting|sewing|decorating|"
    r"gardening|going to|off to|about to|having|doing)\b", re.I)


ACTIVITY_LOOSE = re.compile(
    r"\b(?:want|wanted|need|needed|thinking of|plan|plans|planned|trying|meant|going) to "
    r"(?:make|cook|bake|roast|prepare|build|paint|write|sort|fix|mend|plan|organise|organize|"
    r"pack|do|have)\b", re.I)


ASK_LINE = re.compile(r"^\s*(?:so |and |but )?(?:what|which|who|when|where|why|how|can|could|"
                      r"would|should|do|did|does|is|are|was|were|will|shall|have|has|remind|"
                      r"tell|any)\b", re.I)


DETAIL_START = re.compile(
    r"^(?:he|hes|she|shes|they|theyre|it|its|it's|his|her|hers|their|theirs|them|the|this|that|"
    r"these|those|my|our|also|plus|and|but|so|yes|yeah|no|nope|ok|okay|sorry|thanks|right|true)\b",
    re.I)


STOPWORDS = frozenset("""the and but for with that this have has had was were are been being its
it's they them their there here about into from just only also very really quite then than when
what which who how why where some any all one two three four five six seven eight nine ten""".split())


def _bare(folded):
    """The ask inside the reminder wrapper: "remind me what I'm allergic to" -> "what i am
    allergic to", "and my name again?" -> "my name"."""
    asked = REMINDER_MID.search(folded or "")
    bare = REMINDER_MID.sub(" ", folded or "")
    bare = ABOUT_HEAD.sub("", bare)
    bare = REMINDER_HEAD.sub("", bare)
    bare = REMINDER_TAIL.sub("", bare)
    bare = CHAT_TAIL.sub("", bare).strip(" ,.;:!?")
    bare = " ".join(bare.split())
    flipped = WHEN_INVERTED.match(bare)
    if flipped:
        # "when my interview is" -> "when is my interview": one order for every when-ask reader
        bare = f"when {flipped.group(3)} {flipped.group(1)} {flipped.group(2)}"
    elif asked:
        subject = WHEN_INVERTED_SUBJECT.match(bare)
        if subject:
            # "when i am going to rome" -> "when am i going to rome"
            bare = f"when {subject.group(2).split()[0]} {subject.group(1)} " \
                   f"{' '.join(subject.group(2).split()[1:])}".strip()
    return bare


def _the_limits_on(entry):
    """The limits a read entry holds, as a dict, or {} for an entry that limits nothing."""
    if not isinstance(entry, dict):
        return {}
    return {key: entry[key] for key in LIMITS if entry.get(key) not in (None, "", [], {})}


def _the_limit_they_share(text, memory):
    """"im too" after "my son is allergic to nuts": the limit is the person talking's as well.

    A limit said of one person is shared by the next line and the line says nothing of its own,
    so the store is what gives it a meaning: it reads the limit out of the turn before (which it
    filed) and files the same limit on the other person. Nothing is filed when the turn before
    stated no limit, which is what keeps "i love pizza" then "me too" a taste, and "my son is 6"
    then "im too" an age nobody shares.

    Both directions are the same reader: "im allergic to nuts" then "my son is too" is the son's
    allergy, and it was a line the store only echoed back before. Returns the reply, or None.
    """
    who = extract.the_limit_they_share(text)
    if not who or not isinstance(memory, dict):
        return None
    turns = memory.get("turns") or []
    before = str((turns[-1] or {}).get("user") or "") if turns else ""
    if not before:
        return None
    said = extract.extract(before)
    if not isinstance(said, dict):
        return None
    about_them = [(str(entry.get("who") or ""), _the_limits_on(entry))
                  for entry in (said.get("others") or []) if isinstance(entry, dict)]
    about_them = [(relation, limits) for relation, limits in about_them if relation and limits]
    about_me = _the_limits_on(said)
    if who == "i":
        if not about_them:
            return None
        relation, limits = about_them[-1]
        for key, value in limits.items():
            remember(memory, key, value, text)
        return _said_of_a_shared_limit(limits, "", memory)
    if who == extract.LAST_PERSON:
        # "she is too", "he as well": the last person the chat named, out of the line before the
        # share (which is where a pronoun has an antecedent) and then the store's own person.
        named = [str(word) for word in (said.get("people") or []) if isinstance(word, str)]
        who = named[-1] if named else ""
        if not who:
            person = memory.get("person")
            who = str((person or {}).get("who") or "") if isinstance(person, dict) else ""
        if not who:
            return None
    if not about_me:
        return None
    remember_other(memory, dict(about_me, who=who), text)
    return _said_of_a_shared_limit(about_me, who, memory)


def _is_or_are(words):
    """"dairy is off your plate", but "nuts are off your plate" and "nuts and dairy are too"."""
    if len([word for word in words if str(word).strip()]) > 1:
        return "are"  # two things said together are plural however each of them is spelt
    last = str(words[-1]).split()[-1] if words else ""
    return "are" if last.endswith("s") and not last.endswith("ss") else "is"


def _the_things(words):
    """The things named, as a person says them: "nuts", "nuts and dairy", "nuts, dairy and soya"."""
    said = [str(word).strip() for word in words if str(word).strip()]
    if not said:
        return ""
    if len(said) == 1:
        return said[0]
    return ", ".join(said[:-1]) + " and " + said[-1]


def _said_of_a_shared_limit(limits, who, memory):
    """The reply to a line that shares the limit: what it is, and whose it is now."""
    things = list(limits.get("allergies") or [])
    if things:
        named = _the_things(things)
        if who:
            return pick(("Then " + named + " " + _is_or_are(things) + " off " + _their_own(who)
                         + "'s plate too — I'll keep both of you in mind.",
                         "Right, " + named + " out for " + _their_own(who) + " as well, then.",
                         "So " + named + " " + _is_or_are(things) + " off the table for "
                         + _their_own(who) + " too. Both of you, then."), memory, ())
        return pick(("Then " + named + " " + _is_or_are(things) + " off your plate too — I'll "
                     "answer for both of you.",
                     "Right, " + named + " out for you as well, then.",
                     "So " + named + " " + _is_or_are(things) + " off the table for you too."),
                    memory, ())
    diet = limits.get("diet")
    if diet:
        if who:
            return ("Then " + str(diet) + " for " + _their_own(who) + " as well — I'll plan around "
                    "the two of you.")
        return pick(("Then " + str(diet) + " for you as well — I'll plan around the two of you.",
                     "Same for you, then: " + str(diet) + ". I'll keep that straight."),
                    memory, ())
    condition = limits.get("condition")
    if condition:
        named = _the_things(condition if isinstance(condition, (list, tuple)) else [condition])
        if who:
            # Said the way it is said: the condition is what the person is, so it goes after them
            # with "is", not held off with "has the same thing". "Then your mum is diabetic too"
            # reads as a friend would say it; the other wordings are for the second time.
            return pick(("Then " + _their_own(who) + " " + _is_or_are([named]) + " " + named
                         + " too — I'll keep it in mind for both of you.",
                         "Right, " + named + " for " + _their_own(who) + " as well, then. Both of "
                         "you.",
                         "So " + _their_own(who) + " has that too. I'll keep the two of you in "
                         "mind."), memory, ())
        return pick(("Then you have the same thing, " + named + " — I'll keep that in mind.",
                     "Same condition for you too, then: " + named + "."), memory, ())
    return None


def _their_own(who):
    """"your son", "your daughter": the reply names the person the limit is now on.

    Not `_theirs`, which is the composer's somewhere else: a reply that reads "off Son plate" is
    the person addressed as the relation they gave rather than as somebody in their family.
    """
    word = str(who or "").strip().lower()
    return "your " + word if word and word not in ("i", "me") else "your"


MEATLESS_DIET = re.compile(r"vegetarian|vegan|veggie|plant|pescatarian|flexitarian", re.I)


def _the_back_this_turn(text, memory):
    """The line that says what the bot has just stopped believing about somebody else.

    Only on the turn they lifted it: the note names the food, and said a turn later it answers a
    question nobody asked.
    """
    done = memory.get("reversal") if isinstance(memory, dict) else None
    if not isinstance(done, dict) or done.get("said") != " ".join(str(text or "").lower().split()):
        return None
    who = str(done.get("who") or "")
    food = str(done.get("food") or "").strip()
    if not food:
        return None
    theirs = "your " + who if who in extract.RELATIONS else "them"
    if done.get("kind") == "taste":
        # A taste is not a diet: "nothing off her plate" would read as food she cannot have.
        return pick(["Right \u2014 " + food + " back on the yes list for " + theirs + ", then.",
                     "Got it \u2014 " + theirs + " likes " + food + ", then.",
                     "Noted \u2014 " + food + " for " + theirs + " from now on, then."],
                    memory if isinstance(memory, dict) else {})
    return pick(["Right \u2014 " + food + " back on the plate for " + theirs + ", then.",
                 "Got it \u2014 " + food + " is back on the menu for " + theirs + ", then.",
                 "Fair enough \u2014 nothing off " + theirs + "'s plate, then."],
                memory if isinstance(memory, dict) else {})


def _still_holding(memory, animals):
    """True when a pet of that kind is still on the store, so the whole kind is not gone."""
    held = {str((pet or {}).get("animal") or "").strip().lower()
            for pet in ((memory.get("user") or {}).get("pets") or []) if isinstance(pet, dict)}
    return any(str(animal).lower() in held for animal in animals)


SIZE_UNITS = {
    "kg": "kg", "kilo": "kg", "kilos": "kg", "kilogram": "kg", "kilograms": "kg",
    "g": "g", "gram": "g", "grams": "g", "lb": "lb", "lbs": "lb", "pound": "lb",
    "pounds": "lb", "oz": "oz", "ounce": "oz", "ounces": "oz", "pint": "pint",
    "pints": "pint", "litre": "litre", "litres": "litre", "liter": "litre",
    "liters": "litre", "ml": "ml", "cm": "cm", "mm": "mm", "inch": "inch", "inches": "inch",
}


A_SIZE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(" + "|".join(sorted(SIZE_UNITS, key=len, reverse=True))
                    + r")\b", re.I)


SIZE_LINE_FILLER = frozenset((
    "its", "it", "is", "about", "around", "roughly", "mine", "ours", "the", "a", "an", "one",
    "weighs", "weigh", "weight", "of", "say", "like", "just", "not", "much", "more", "less",
    "over", "under", "approx", "approximately", "i", "have", "got", "ive", "thats", "that",
    "s", "and", "so", "yeah", "yes", "ok", "okay", "sorry", "actually", "probably", "think",
    "guess", "pretty", "already", "exactly", "nearly", "almost", "only", "total",
    "altogether", "definitely", "ish", "now", "still", "bought", "buy", "brought", "used",
    "was", "were", "we", "they", "it",
))


A_TIME = re.compile(r"\b\d+(?:\.\d+)?\s*(?:hour|hours|hr|hrs|minute|minutes|min|mins)\b",
                    re.I)


def _a_size(text):
    """The size a line names as one string ("2kg"), or None when it names none."""
    found = A_SIZE.search(str(text or ""))
    if not found:
        return None
    return found.group(1) + SIZE_UNITS[found.group(2).lower()]


def _only_names_the_size(text):
    """True when the line is the size and nothing else, so what it says is the answer itself."""
    flat = " ".join(str(text or "").lower().split())
    found = A_SIZE.search(flat)
    if not found or len(flat.split()) > 8:
        return False
    rest = (flat[:found.start()] + " " + flat[found.end():]).split()
    return all(word.strip(",.!?") in SIZE_LINE_FILLER for word in rest)


def _the_clause_that_works_it_out(answer, size):
    """The clause of `answer` that names this size with a time in it, or None.

    "20 minutes per 500g plus 20 minutes at 190C, so a 2kg bird takes roughly 1 hour 40 minutes"
    holds the figure for the size the person has just named, in the answer's own words. A clause
    that has the size but no time is something else about it ("put a 2kg bird in a large tin")
    and is not the figure the line is asking for.
    """
    for clause in re.split(r"[,;.]", str(answer or "")):
        flat = " ".join(clause.split())
        if not flat or not A_TIME.search(flat) or _a_size(flat) != size:
            continue
        flat = re.sub(r"^(?:(?:and|so|then|which means|that means)\b[\s,]*)+", "", flat, flags=re.I)
        if flat:
            return flat[0].upper() + flat[1:] + "."
    return None


FEEDING_ASK = re.compile(
    r"\b(?:enough(?:\s+(?:for|to\s+feed))?|feed|feeds|serve|serves|do|does)\s+"
    r"(?:the\s+|it\s+|that\s+|this\s+|all\s+|all\s+of\s+)?"
    r"(\d{1,3}|a couple|a few|a dozen|half a dozen|two|three|four|five|six|seven|eight|nine"
    r"|ten|eleven|twelve)\b", re.I)


HEAD_COUNTS = {"a couple": 2, "a few": 3, "a dozen": 12, "half a dozen": 6}


HEAD_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
              "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


SIZE_GRAMS = {"kg": 1000.0, "g": 1.0, "lb": 453.59, "oz": 28.35}


BIRDS = frozenset(("chicken", "turkey", "duck", "goose"))


ANSWER_PORTION = re.compile(
    r"\b(\d{2,4})\s*g\b[^.,;]{0,24}?\b(?:each|a person|per person|per head|a head)\b", re.I)


SO_A_SIZE = re.compile(r"\bso\s+(?:an?\s+)?(\d+(?:\.\d+)?)\s*(" +
                       "|".join(sorted(SIZE_UNITS, key=len, reverse=True)) + r")\b", re.I)


MADE_ONLY = re.compile(r"\b(?:only|just)\s+(?:made|cooked|done|got|had|bought|used|managed|"
                       r"did|knocked)", re.I)


FOR_A_COUNT = re.compile(
    r"\bfor\s+(?:the\s+)?(\d{1,2}|two|three|four|five|six|seven|eight|nine|ten|eleven"
    r"|twelve)\b", re.I)


def _the_portion_for_the_food(held, answers):
    """The (grams, unit, noun) portion the knowledge keeps for the food this chat is about, or None.

    The food is looked for in what the person said and in the answer that gave them the figure,
    and the most specific name wins: "chicken breast" is the meat off the bone at 200g, where
    "chicken" on its own is a bird at units.BIRD_GRAMS, so a line about a breast is never read as
    a whole bird.
    """
    best = None
    for names, amount, unit, noun in units.PER_PERSON + units.PER_PERSON_WHEN_COUNTED:
        for name in names:
            if not re.search(r"\b" + re.escape(name) + r"\b", held):
                continue
            score = len(name) + (2 if re.search(r"\b" + re.escape(name) + r"\b", answers) else 0)
            if best is not None and score <= best[0]:
                continue
            if name in BIRDS:
                best = (score, (float(units.BIRD_GRAMS), "g", name, True))
            else:
                best = (score, (float(amount), unit, noun, False))
    if not best:
        return None
    per, unit, noun, bone = best[1]
    if unit != "g":
        return best[1]
    # The answer's own portion is the one on the screen, so it is read first: a person holding
    # the 200g-of-chicken-each answer is not holding a bird measured on the bone.
    stated = ANSWER_PORTION.search(answers)
    if stated:
        return float(stated.group(1)), "g", noun, "on the bone" in answers
    return per, unit, noun, bone


def _the_size_on_the_screen(turns):
    """The size the chat has in hand: the last one they named, or the one the answer worked out.

    "is that enough for 6" a turn after "how long do i roast a chicken" points at the size the
    answer did its arithmetic for ("so a 2kg bird takes roughly 1 hour 40 minutes"), and that is
    the amount on the screen. A size named further back is not read: the subject moves on, and a
    figure from five turns ago is as likely to be about something else.
    """
    for turn in list(reversed(turns))[:3]:
        size = _a_size(turn.get("user"))
        if size:
            return size
    for turn in list(reversed(turns))[:2]:
        worked = SO_A_SIZE.search(str(turn.get("bot") or ""))
        if worked:
            return worked.group(1) + SIZE_UNITS[worked.group(2).lower()]
    return None


def _size_in_grams(size):
    """The weight a size names, in grams, or None when it is not a weight."""
    found = A_SIZE.match(str(size or ""))
    if not found:
        return None
    grams = SIZE_GRAMS.get(found.group(2).lower())
    if not grams:
        return None
    try:
        return float(found.group(1)) * grams
    except (TypeError, ValueError):
        return None


def _the_figure_for_the_size_they_named(text, memory):
    """The figure the answer on the screen worked out for the size this line names, or None.

    "how long do i roast a chicken" answers with the rate and with the arithmetic for one size
    ("so a 2kg bird takes roughly 1 hour 40 minutes"), and the person then says "its 2kg". The
    figure for their size is already in the answer, and the store said "Thanks for telling me -
    I'm here if you want to dig into any of that": an acknowledgement of the one part of the
    chat that has a number in it.

    Only a line that is the size and nothing else counts, only when the size was not said before
    in this chat (an ask that carries the size reaches the entry by itself), and only for the
    figure the answer already worked out, so nothing is worked out here and nothing is invented.
    """
    if not isinstance(memory, dict):
        return None
    size = _a_size(text)
    if not size or not _only_names_the_size(text):
        return None
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    if not turns:
        return None
    for turn in turns:
        if _a_size(turn.get("user")) == size:
            return None
    # The size the answer worked its own arithmetic out for is already in front of them: "so a
    # 2kg bird takes roughly 1 hour 40 minutes" came back as "A 2kg bird takes roughly 1 hour 40
    # minutes." when they typed "its about 2kg". Handing the clause back repeats the one figure
    # they have just read. A size the answer did not work out (1.5kg, 2.5kg) is a different
    # matter and never reaches this function: the cooking entry answers those itself.
    worked = SO_A_SIZE.search(str(turns[-1].get("bot") or ""))
    if worked and worked.group(1) + SIZE_UNITS[worked.group(2).lower()] == size:
        return None
    return _the_clause_that_works_it_out(turns[-1].get("bot"), size)


def _retraction_this_turn(text, memory):
    """The short line that says the last thing they said is off the record, on the turn they said
    it."""
    gone = memory.get("retraction") if isinstance(memory, dict) else None
    if not isinstance(gone, dict) or gone.get("said") != " ".join(str(text or "").lower().split()):
        return None
    keys = gone.get("keys") or []
    shown = [item for item in (gone.get("shown") or []) if item]
    if "pets" in keys and shown:
        thing = " and ".join(shown[:2])
        return pick(["Right \u2014 " + thing + " is off the record, then.",
                     "Taken back \u2014 no " + thing + " on my list any more."], memory)
    if "plans" in keys and not [key for key in keys if key != "plans"]:
        return pick(["Right \u2014 that plan is off the record, then.",
                     "Taken back: I\u2019ve nothing about that trip from you now.",
                     "Scratch that, then \u2014 the plan is out."], memory)
    phrase = RETRACT_SAY.get(keys[0]) if keys else None
    if phrase:
        return pick(["Right \u2014 " + phrase + " is off the record, then.",
                     "Dropped. " + phrase[:1].upper() + phrase[1:] + " is gone.",
                     "Taken back \u2014 I\u2019ve nothing from you on record about it now."],
                    memory)
    return pick(["Right, that\u2019s off the record then.",
                 "Taken back \u2014 I\u2019ve nothing on record about it now."], memory)


THEIR_NAMES = re.compile(
    r"\b(?:they|them|their|the\s+(?:two|three|four))\b[^.?]{0,20}?"
    r"\b(?:call|calls|called|calling|name|names|named)\b"
    r"|\b(?:call|called|name|named|callin)\s+(?:them|the\s+(?:two|three|four))\b", re.I)


ASKS_IT_BACK = re.compile(r"\b(?:again|remind me|remind|did i|earlier|told you|told me)\b", re.I)


OWN_ANIMAL_LINE = re.compile(
    r"\b(?:my|our)\s+(?:[a-z'\u2019-]+\s+){0,2}(?:dogs?|pupp(?:y|ies)|cats?|kittens?|pets?|"
    r"rabbits?|bunn(?:y|ies)|hamsters?|fish|horses?|pon(?:y|ies)|parrots?|guinea\s+pigs?)\b"
    r"|\b(?:i|we)\s+(?:have|had|got|keep|kept|'ve|ve|also\s+have|also\s+got)\b")


NOT_THEIR_ANIMALS = re.compile(
    r"\b(?:my|our)\s+(?:sister|brother|mum|mother|dad|father|friend|neighbour|neighbor|aunt|"
    r"uncle|cousin|gran|grandma|grandad|grandpa|colleague|boss|son|daughter|wife|husband|"
    r"partner|niece|nephew|flatmate|roommate|landlord)\b[^.!?]*\b(?:has|have|had|got|keeps?|"
    r"wants?|wanted)\b"
    r"|\b(?:in|at|from)\s+the\s+(?:park|rescue|shelter|centre|center|vet)\b"
    r"|\bthe\s+(?:rescue|shelter|breeder|neighbour|neighbor)\b[^.!?]*\b(?:had|has|have)\b"
    r"|\b(?:i|we)\s+(?:met|saw|passed|watched)\b")


def _the_line_before_is_their_own_animal(memory, back=3):
    """True when the last line that named an animal named one of the person's own.

    A question can sit between the animal and the ask ("we have two dogs, rufus and nell" / "what
    do they eat" / "what are they called again"), so the lines that named nothing are walked past.
    The first line that did name an animal decides: theirs, or somebody else's.
    """
    for turn in reversed(list(memory.get("turns") or [])[-int(back):]):
        said = str(turn.get("user") or "").strip().lower()
        if not said:
            continue
        if NOT_THEIR_ANIMALS.search(said):
            return False
        if OWN_ANIMAL_LINE.search(said):
            return True
        if re.search(r"\b(?:dogs?|cats?|kittens?|pupp\w*|animals?|pets?|rabbits?|hamsters?|"
                     r"fish|horses?)\b", said):
            # An animal line all the same, and not one of theirs: the pronoun is not about their
            # animals either, so the walk stops here rather than reaching further back.
            return False
    return False


NO_RECORD = re.compile(
    r"^(?:you haven'?t told me|you (?:didn'?t|did not) tell me|i don'?t have|"
    r"there'?s nothing|i haven'?t got)\b", re.I)


ASK_AND_PERSON = frozenset("""what which who is are was were does do did can could would should
she he they them their her his him my our mum mom mother dad father son daughter sister brother
kid kids child children wife husband partner parents gran nan grandma granny aunt uncle cousin
baby stepmum stepdad mother father baby allergic allergy allergies allergie diet eat eats eating
eaten food foods drink drinks allergic had has have anything else one""".split())


def _says_more_than_the_ask(low):
    """True when the line carries a word the ask about that fact does not need.

    "what is my mum allergic to?" is the ask alone; "is my son allergic to nuts? he had a rash"
    brings a food and a symptom with it, and those are the entry's, not the store's.
    """
    for word in re.findall(r"[a-z']+", str(low or "").lower()):
        if len(word) < 3 or word in ASK_AND_PERSON or word in GENERIC_WORDS:
            continue
        if word.rstrip("s") in ASK_AND_PERSON:
            continue
        return True
    return False


GENERIC_WORDS = frozenset("""the and but for with that this these those there here about into
from just only also very really quite then than when what which who whom whose why how some any

not dont doesnt didnt im ive its it's youre youve like want need know tell told say said again
please thanks ok okay""".split())


HOW_FAR_ALONG = re.compile(
    r"\bhow far (?:along|gone)\b|\bhow many weeks (?:is|are|am|along|pregnant|gone|in)\b"
    r"|\bwhat week (?:is|are|am) (?:she|he|they|it|i|i in)\b|\bhow many weeks (?:pregnant|along)\b",
    re.I)


OWN_LENGTH_ASK = re.compile(r"\b(?:am i|i am|im|i'm|do i|did i)\b", re.I)


def _a_length_i_have(memory, low):
    """True when a length ask is about a pregnancy this chat already holds the weeks for.

    An ask like that is about what the person said, not about the world: the answer is the number
    they gave, and no card knows it. Read as a question about the world it lost the turn to the
    dating card, which explained how a due date is worked out instead of saying "Eight weeks."
    """
    said = str(low or "")
    if not HOW_FAR_ALONG.search(said):
        return False
    holding = [entry for entry in others(memory or {})
               if isinstance(entry, dict) and isinstance(entry.get("weeks"), int)]
    named = [entry for entry in holding
             if re.search(r"\b" + re.escape(str(entry.get("who") or "")) + r"\b", said)]
    if len(named) == 1:
        return True
    if OWN_LENGTH_ASK.search(said):
        own = user(memory or {}) or {}
        return isinstance(own.get("weeks"), int) or bool(own.get("pregnant"))
    return bool(holding)


PET_NAME_AGAIN = re.compile(
    r"\bwhat(?:'s|s| is| was)\s+(?:his|her|its|their)\s+name\b"
    r"|\bwhat\s+(?:is|was|are|were)\s+(?:he|she|it|they)\s+called\b"
    r"|\bwhat\s+(?:did|do)\s+(?:i|we)\s+(?:call|name)\s+(?:him|her|it|them)\b", re.I)


PET_NAME_SETTLED = re.compile(
    r"\bwhat\s+(?:shall|should|will|would)\s+(?:i|we)\s+(?:call|name)\s+(?:him|her|it|them)\b",
    re.I)


NAME_PICKED_AGAIN = re.compile(
    r"\b(?:what|which)\s+name\s+(?:did|do|have)\s+(?:i|we)\s+"
    r"(?:pick|picked|choose|chose|go for|settle on|settled on|end up with)\b"
    r"|\b(?:what|which)\s+(?:did|do|have)\s+(?:i|we)\s+"
    r"(?:pick|picked|choose|chose|go for|settle on|settled on|end up with)\b", re.I)


def _offered_here(memory):
    """The names the bot itself put in front of them on the turn before, and what they are for.

    "what should i name it" is answered with three names, and the next line is one of them or a
    name of their own. That turn is a choice, not a fact to look up: parsed from the reply rather
    than from a list of names here, so whatever the answer offered is what can be picked.
    """
    offered = extract.names_offered(memory)
    if not offered:
        return None
    return {"animal": _animal_family(offered["animal"]), "names": offered["names"]}


def _name_they_answered(text, memory):
    """The name chosen in answer to the bot's own question or list:

        we got a puppy / What's its name? / biscuit
        what should i name it / For a cat: Miso, Willow or Pepper. / milo

    The word alone says nothing, so it is read as a name only when the reply right before it asked
    for one or offered some; anything longer than a word or two ("i dont know", "no idea") stays
    unanswered. A list that was answered by a name of their own ("milo", not one of the three) is
    still the choice: the question was "what should i name it", and the answer is the name.
    """
    return extract.a_name_picked(text, memory)


def _the_animal_of_the_pick(memory):
    """Which animal a name just picked is for: the one the list was about, or the one in play."""
    offered = _offered_here(memory)
    if offered and offered.get("animal"):
        return offered["animal"]
    turns = memory.get("turns") or []
    for turn in reversed(turns[-3:]):
        line = str((turn or {}).get("user") or "").lower()
        for word in re.findall(r"[a-z']+", line):
            if word in extract.ANIMALS:
                return _animal_family(word)
    pets = user(memory).get("pets") or []
    for pet in pets:
        if isinstance(pet, dict) and pet.get("animal"):
            return _animal_family(pet.get("animal"))
    return None


PLAN_LOW_START = frozenset("""in on the a an my our their his her its we i it that this there
you your you're youre you've you'll youd you'd i'm im we're save book get go see buy run start
finish take visit move learn do make find call pay email sort fix get see meet try keep""".split())


def _the_second_pet_said(fixed, memory):
    """A line that adds a second animal of a kind is answered as a pet of theirs, not echoed.

    "my cat is called milo" then "no we also have a cat called max" filed both cats and left the
    turn to the greeting, which said the person's line back with "Got it" in front of it - a
    receipt in their own words. The store has the two names, so the reply is the one thing there
    is to ask about two animals, from the same pool that answers one.
    """
    animal = str((fixed or {}).get("animal") or "").strip().lower()
    pets = [pet for pet in (user(memory or {}).get("pets") or ()) if isinstance(pet, dict)]
    named = [str(pet.get("name") or "") for pet in pets
             if str(pet.get("animal") or "").strip().lower() == animal and pet.get("name")]
    if len(named) < 2:
        return ""
    # A name is written the way a name is written, whatever case it was filed in.
    named = [name[:1].upper() + name[1:] for name in named]
    # "Two cats, Milo and Max", "Three cats, Milo, Tom and Ada": the count the store holds, said
    # in words the way a person says it.
    thing = (_many(len(named), animal)[:1].upper() + _many(len(named), animal)[1:]
             + ", " + _a_list_of_names(named))
    return pick(ack.PET_TAIL_MANY, memory or {},
                str((fixed or {}).get("said") or "")).format(Thing=thing)


NOT_THE_SAME = re.compile(
    r"^(?:(?:and|but)\s+)?(?:my|our)\s+(?P<who>[a-z]+(?:[ -]in[ -]law)?)\s+"
    r"(?P<no>isnt|isn['\u2019]?t|is\s+not|doesnt|does\s+not|wasnt|was\s+not)$", re.I)


def _the_limit_the_last_line_gave(memory):
    """The limit the line before stated, on the person that line was about, or None.

    It is theirs ("im allergic to nuts") or somebody else's ("my mum is vegetarian"), and it is
    only that line's: a line about the weather is not a limit with nothing after it, so "my son is
    too" following one carries nothing.
    """
    said = " ".join(str(last_user(memory) or "").lower().split())
    if not said:
        return None
    for entry in reversed(memory.get("facts_log") or []):
        if not isinstance(entry, dict):
            continue
        if " ".join(str(entry.get("text") or "").lower().split()) != said:
            continue
        value = entry.get("value")
        if entry.get("key") in ("allergies", "diet"):
            return user(memory)
        if entry.get("key") in ("other", "others") and isinstance(value, dict) \
                and (value.get("allergies") or value.get("diet")):
            return value
    return None


_RELATION = "|".join(sorted(extract.RELATIONS, key=len, reverse=True))


OTHER_ASK = re.compile(
    r"\b(?:what|which|who)\b[^?]{0,40}?\b(?:my|your)\s+(?:"
    + _RELATION + r")\b|"
    r"\b(?:does|did|is|was)\s+(?:my|your)\s+(?:" + _RELATION + r")\b|"
    r"\bwhat (?:does|did) (?:she|he|they) eat\b|"
    # "what is she allergic to?" about a person the chat knows: the relation is in the previous
    # line and the pronoun is the one who fits it, so the ask names nobody and read as nothing.
    r"\bwhat(?:'s|s| is| was)\s+(?:she|he|they)\s+(?:allerg\w*|not eat|eat)\b|"
    r"\bis (?:she|he|they)\s+allerg\w*\b|"
    r"\bwhat did i say (?:she|he|they|my|your)\b[^?]{0,30}?\b(?:eat|allerg\w*)\b|"
    r"\b(?:does|did) (?:she|he|they)\b[^?]{0,20}?\beats?\b", re.I)


OTHER_FACT = re.compile(r"allerg\w*", re.I)


WHO_IS_NAME_ASK = re.compile(
    r"\bwho(?:'s|s| is| was)\s+(?P<name1>[a-z][a-z'\-]{1,20})\b"
    r"|\bdo\s+(?:i|you)\s+(?:know|remember)\s+(?:a\s+|an\s+)?(?P<name2>[a-z][a-z'\-]{1,20})\b"
    r"|\bis\s+(?P<name3>[a-z][a-z'\-]{1,20})\s+(?:my|our)\s+(?P<who3>[a-z]+)"
    r"|\b(?P<name4>[a-z][a-z'\-]{1,20})\s+is\s+(?:my|our)\s+(?P<who4>[a-z]+)\s*[?.]?\s*$", re.I)


NAME_ASK_TAIL = frozenset("again then though please now too already anyway".split())


THEM = re.compile(r"\b(?:she|he|her|they|them|their|hers|his|him)\b", re.I)


OTHER_NAME_ASK = re.compile(
    r"\bwhat(?:'s|s| is| was| are)?\s+(?:do|did)?\s*(?:i|you)\s+call\s+(?:my|our)\s+"
    r"(?P<who1>" + KIN_ASK + r")\b"
    r"|\bwhat(?:'s|s| is| was)\s+(?:my|our)\s+(?P<who2>" + KIN_ASK + r")(?:'s|s')?\s+name\b"
    r"|\bwhat\s+(?:is|was|are|were)\s+(?:my|our)\s+(?P<who5>" + KIN_ASK + r")\s+called\b"
    r"|\bwhat\s+are\s+(?:my|our)\s+(?P<who3>" + KIN_ASK + r")\s+called\b"
    # The verb and the question mark are often left off: "my daughters name" is the same ask as
    # "what is my daughters name", and read as a statement it filed the word "name" as her name.
    r"|\bm(?:y|ine)\s+(?P<who4>" + KIN_ASK + r")(?:'s|s')?\s+names?\s*(?:again)?\s*\??\s*$"
    r"|\b(?:do|did)\s+(?:you|u)\s+(?:remember|know)\s+(?:my|our)\s+(?P<who6>" + KIN_ASK + r")(?:'s|s')?\s+name\b"
    r"|\b(?:do|did)\s+(?:you|u)\s+(?:remember|know)\s+what\s+(?:my|our)\s+(?P<who7>" + KIN_ASK + r")\s+"
    r"(?:is|was|are|were)\s+called\b"
    r"|\bremind\s+me\s+(?:what\s+)?(?:my|our)\s+(?P<who8>" + KIN_ASK + r")\s+(?:is|was|are|were)\s+called\b"
    r"|\bremind\s+me\s+what\s+(?:my|our)\s+(?P<who9>" + KIN_ASK + r")(?:'s|s')?\s+name\s+is\b"
    # the reminder wrapper comes off before this reader runs, so the ask arrives as a relative
    # clause: "remind me what my sister is called" reaches the store as "what my sister is called".
    r"|\bwhat\s+(?:my|our)\s+(?P<who10>" + KIN_ASK + r")\s+(?:is|was|are|were)\s+called\b"
    # "who is my friend" is the same ask as "what is my friend called" once the store has a name
    # filed for the person: the name they gave is the answer, and "I'd rather not guess" is a
    # denial of something they told us. The relation has to be the whole ask - "who is my friend
    # coming with" asks about the visit, not the name - so nothing may follow it but "called",
    # "again" and the question mark.
    r"|\bwho(?:'s|s| is| was)\s+(?:my|our)\s+(?P<who11>" + KIN_ASK + r")\s*(?:called|again)?[\s?.!]*$",
    re.I)


PRONOUN_NAME_ASK = re.compile(
    r"\bwhat(?:'s|s| is| was)\s+(?P<pos>his|her|their)\s+name\b"
    # "what are their names" is the same ask with the several of them said out loud: after "my
    # daughter emma is 4 and my son jack is 6" it was the search hedge.
    r"|\bwhat\s+(?:are|were)\s+(?P<pos4>his|her|their)\s+names?\b"
    r"|\bwhat\s+(?:is|was|are)\s+(?P<sub>he|she|they)\s+called\b"
    r"|\bwhat\s+(?:do|did)\s+(?:i|you)\s+(?:call|say)\s+(?P<obj>him|her|them)\b"
    r"|\b(?:do|did)\s+(?:you|u)\s+(?:remember|know)\s+(?P<pos2>his|her|their)\s+name\b"
    r"|\b(?:do|did)\s+(?:you|u)\s+(?:remember|know)\s+what\s+(?P<sub2>he|she|they)\s+"
    r"(?:is|was|are)\s+called\b"
    r"|\bremind\s+me\s+what\s+(?P<obj2>him|her|them)\s+(?:is|was)\s+called\b"
    r"|\bwhat\s+(?P<pos3>his|her|their)\s+name\s+(?:is|was)\b", re.I)


def _with_an_in_law(who, low):
    """The person an ask names with the "in law" it was said with: "brother in law"."""
    if not who:
        return who
    if extract.an_in_law(who):
        return extract.a_person_word(who)  # "brother-in-law" is filed as "brother in law"
    if re.search(r"\b" + re.escape(who) + r"s?" + IN_LAW_AFTER_TEXT, low or "", re.I):
        return who + " in law"
    return who


KIDS_ASK = re.compile(
    r"\bhow many (?:kids?|children|child)\b|"
    r"\bdo (?:i|we) have (?:any )?(?:kids?|children)\b|"
    r"\b(?:have|did) (?:i|we) (?:got|have) (?:any )?(?:kids?|children)\b", re.I)


KIDS_SOMEONE_ELSE = re.compile(
    r"^\W*(?:do|does|did|has|have|had|is|are|was|were)\s+"
    r"(?:my|our|his|her|their|your|you|the|she|he|they|them|it)\b", re.I)


KIDS_A_DECISION = re.compile(r"\b(?:should|shall|worth|afford|too many|enough|ok|okay|normal)\b",
                             re.I)


def _kids_ask(low):
    """Whether the line asks the person's own count of children."""
    match = KIDS_ASK.search(low) if isinstance(low, str) else None
    if not match:
        return False
    if KIDS_SOMEONE_ELSE.match(low[match.end():]):
        return False
    return not KIDS_A_DECISION.search(low)


ABOUT_A_NAME = re.compile(
    r"\b(?:what|anything|everything|much|else)\b[^?]{0,30}?\b(?:know|knows|knew|remember|"
    r"told|tell|said|say|mention|mentioned)\b[^?]{0,25}?\babout\s+([a-z][a-z'-]{1,20})\b|"
    r"\b(?:do|did|can)\s+(?:you|i)\s+(?:ever\s+)?(?:know|remember|tell|told|mention|say|said)\b"
    r"[^?]{0,30}?\babout\s+([a-z][a-z'-]{1,20})\b", re.I)


# The ask that wants the children as a group. It is read with every word a group of children goes
# by, not only "kids": "what do you know about my girls" and "what have you got on my sons" were
# both answered with the search hedge a turn after the same chat gave their ages, because the
# children were filed under the word the person used ("girls", "sons") and this asked for another.
CHILDREN_ABOUT = re.compile(r"\b(?:kids?|children|child|boys?|girls?|sons?|daughters?|"
                            r"twins?|lads?|lasses|youngest|eldest|oldest)\b", re.I)


ABOUT_PERSON_MORE = re.compile(r"\b(?:else|other|more|anything)", re.I)


EAT_ASK = re.compile(r"\b(?:eat|eats|eating|diet|vegan|vegetarian|pescatarian)\b", re.I)


FOOD_ASK = re.compile(r"\b(?:eat|eats|eating|eaten|food|foods|drink|drinks|drinking|diet|"
                      r"meal|meals|breakfast|lunch|dinner|snack|cook|cooking)\b", re.I)


DIET_ASK = re.compile(r"\bmy diet\b|\bwhat (?:do|did) i eat\b|\bwhat am i eating\b|"
                      r"\b(?:what|which) diet (?:am i|do i|did i|was i)\b|"
                      r"\bwhat (?:can|can't|cant|could) i (?:not )?(?:eat|have)\b|"
                      r"\bwhat do i not eat\b|\bam i (?:vegetarian|vegan|pescatarian|on a diet)\b",
                      re.I)


DIET_HOW_TO = re.compile(r"\bhow (?:do|does|can|could|should|would|might|to)\b|"
                         r"\bany (?:tips|advice|ideas|suggestions|ways)\b|"
                         r"\bways? to\b|\bwhat can i do\b|\bhelp me\b|\btips for\b", re.I)


DIET_FACT_ASK = re.compile(
    r"\bmy diet\b|"
    r"\bwhat do i not eat\b|"
    r"\bwhat (?:can't|cant|couldn't|could not|can not) i (?:eat|have)\b|"
    r"\bwhat (?:can|could) i not (?:eat|have)\b|"
    r"\bam i (?:vegetarian|vegan|pescatarian|on a diet)\b", re.I)


ASK_WORD = re.compile(r"\b(?:what|which)\b", re.I)


HELP_ASK = re.compile(r"\b(?:should|could|can|shall|cook|make|recipe|recipes|meal|meals|dinner|"
                      r"lunch|breakfast|snack|safe|help|suggest|ideas?)\b", re.I)


CANT_HAVE = re.compile(
    r"\b(?:can(?:not|\s+not|'?t)|could(?: not\b|n'?t)|must(?: not\b|n'?t)|"
    r"should(?: not\b|n'?t)|may not)\b[^?!.]{0,14}?\b(?:have|eat|drink)\b"
    r"|\bwhat\b[^?!.]{0,30}?\b(?:to )?avoid\b|\b(?:things?|foods?|stuff)\s+to avoid\b", re.I)


CAN_HAVE = re.compile(r"\bwhat\b[^?!.]{0,30}?\b(?:can|could)\s+\w+\s+(?:have|eat|drink)\b", re.I)


CAN_THEY_HAVE = re.compile(
    r"\b(?:can|could|should|may)\s+(?:he|she|they|him|her|them)\s+(?:have|eat|drink)\b"
    r"|\bis\s+[a-z][a-z'\u2019 -]{1,24}?\bok\s+(?:for|with)\s+(?:him|her|them)\b"
    r"|\bdoes\s+(?:he|she|they)\s+(?:eat|drink|have)\b", re.I)


CAN_THEY_HAVE_A_FOOD = re.compile(
    r"\b(?:can|could|should|may)\s+(?:he|she|they|him|her|them)\s+(?:have|eat|drink)\s+"
    r"(?!(?:for|with|at|on|in|to|instead)\b)[a-z]", re.I)


FOOD_HAS = {
    "dairy": frozenset("""milk cheese butter cream yoghurt yogurt custard latte cappuccino
        cheddar mozzarella feta parmesan brie ice cream ice-cream milkshake ghee paneer""".split()),
    "gluten": frozenset("""bread pasta flour wheat cereal biscuit biscuits cake pastry
        couscous cracker crackers noodles pizza baguette toast bun buns pitta pita rye barley""".split()),
    "wheat": frozenset("""bread pasta flour cereal biscuit biscuits cake pastry noodles
        couscous cracker crackers pizza baguette toast bun buns pitta pita""".split()),
    "sugar": frozenset("""cake chocolate sweets sweets biscuits jam honey syrup pudding
        ice cream ice-cream fizzy juice cola""".split()),
    "nuts": frozenset("""peanuts pesto satay muesli granola almond almonds cashew
        cashews hazelnut hazelnuts walnut walnuts pecan pecans pistachio pistachios
        marzipan praline nutella""".split()),
    "peanuts": frozenset("""peanuts pesto satay""".split()),
    "shellfish": frozenset("""prawns prawn shrimp shrimps crab lobster mussels scallops
        shellfish seafood""".split()),
    "fish": frozenset("""salmon tuna cod haddock sardines mackerel anchovy anchovies
        trout prawns""".split()),
    "eggs": frozenset("""egg mayonnaise mayo meringue omelette omelette frittata
        custard""".split()),
    "soya": frozenset("""tofu edamame soy soya miso tempeh""".split()),
    "sesame": frozenset("""tahini hummus sesame houmous""".split()),
}


STATED_THEN_ASKED = re.compile(r",\s*(?=(?:what|which|how|why|when|where|who|should|can|could|"
                               r"would|will|is|are|do|does|any)\b)", re.I)


ASKS_WITH_WH = re.compile(r"\b(?:what|which|how|why|when|where|who)\b", re.I)


def _the_ask_after_a_statement(low, memory=None):
    """The question clause at the end of a line that states something first, or the line itself.

    "my son is 7 and has a nut allergy, what can i pack him for lunch" is a question about a
    packed lunch, not about the allergy. A line whose first clause asks something too ("what is
    he allergic to, and what can he eat") is left whole: every clause is the ask there.
    """
    text = str(low or "")
    read = memory.get("understood") if isinstance(memory, dict) else None
    if isinstance(read, dict):
        # The understanding engine has already cut the line into its clauses, and its focus is
        # the one the person is asking about. `_folded` has taken the comma out by then, so the
        # cut cannot be made from the words alone.
        clauses = read.get("clauses")
        focus = read.get("focus")
        if isinstance(clauses, list) and len(clauses) > 1 and focus:
            asked = " ".join(str(word) for word in focus if str(word or "").strip()).strip()
            first = " ".join(str(word) for word in (clauses[0] or ()))
            # Only a fact said before the question is context for it. A question that comes first
            # ("whats a good dinner, my son is allergic to nuts") is still the whole line's ask,
            # and the fact at the end is part of it.
            if asked and asked != text.strip() and asked != first.strip():
                return asked
    parts = STATED_THEN_ASKED.split(text, 1)
    if len(parts) < 2 or ASKS_WITH_WH.search(parts[0]):
        return text
    asked = parts[1].strip()
    return asked or text
