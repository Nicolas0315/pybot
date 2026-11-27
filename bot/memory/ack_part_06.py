"""Part 6 of 7 of the module, split out of `ack`.

Everything here is re-exported from `ack`, so callers import it from there as before.
"""
import re

from ..compose import loss, pick, trouble
from ..compose.badnews import reads_as_bad_news
from . import facts, named, taste, topics
from .facts import DAYS, MONTHS
from .ack_part_01 import (
    FACTS,
)
from .ack_part_02 import (
    DEATH_WORDS, WANTS_ANSWER, reads_as_an_ask, LEAD_IN,
)
from .ack_part_03 import (
    _the_line_before, DIGIT, TROUBLE, _ANSWER_OPENER, _ASKED_FOR, _ASKS_MIDWAY, _FAULT,
    _NOT_A_DETAIL, _NOT_A_DETAIL_SUBJECT, _SAID_YES_NO, _repaired, FRAGMENT, STATE, ITS_OWNS_AFTER,
    SHORT, SPEAK, TWO_PLACE, TWO_TO, TWO_VERB, WITH_SLASH, YES_AFTER, without_filler,
)
from .ack_part_04 import (
    THIRD_PERSON,
)
from .ack_part_05 import (
    _adds_one_more_allergen, REPAIR_FRAME, _words,
)


def _the_unit_before(memory):
    """The words the line before measures its figure in: "three times a week" -> "times a week".

    "i run 5k every morning" -> "every morning". Nothing when that line has no figure at all
    ("im tired") or when its figure is followed by nothing that measures it ("i finish at 5",
    "my appointment is on the 3rd"): a new figure with no unit of the old one is a number the
    bot would be making up a home for.
    """
    said = _the_line_before(memory)
    if not said.strip():
        return ""
    words = [word.strip(".,!?;:") for word in said.split() if word.strip(".,!?;:")]
    for index, word in enumerate(words[:-1]):
        figure = word.lower()
        if figure in ("a", "an", "the"):
            continue  # "a month" is the unit of "twice a month", not the figure
        if not (re.search(r"\d", figure) or figure in VALUE_WORDS or figure in DAYS
                or figure in MONTHS):
            continue
        tail = []
        for following in words[index + 1:index + 4]:
            if following.lower() in UNITS_AFTER and len(tail) < 3:
                tail.append(following.lower())
                continue
            break
        if tail:
            return " ".join(tail)
    return ""


def _bad_news_just_before(clean, memory):
    """Whether the line carries on a hard story the last turn or two began.

    The store files a fact and the echo hands it straight back, which is right for "my sister is
    called Meg". It is wrong in the middle of a story: after "im thinking of leaving my husband",
    "she took the kids to her mums" is the next line of it, not a detail to file, and "Noted:
    she took the kids to her mums" answers a marriage breaking up with a receipt.

    Both halves have to be true - bad news just before, and this line about someone else doing
    something - because a neutral fact told in a hard week is still a fact: "my sister is called
    Meg" after "my wife left me" is the one warm thing in the chat, and it must keep its echo.
    "Bad news" is read two ways because a person says it two ways: a break-up or a diagnosis
    (bot/compose/badnews.py) and a death (bot/compose/loss.py). "my nan died last week" then
    "he took the car" is the same story going on, and the car line was answering it with
    motorway advice.
    The other half of this rule is already in _learned, for a detail rather than a fact; asking
    it here covers the facts as well.
    """
    if not THIRD_PERSON.match(_strip_lead_in(clean)):
        return False
    for turn in (memory.get("turns") or [])[-2:]:
        if not isinstance(turn, dict):
            continue
        said = str(turn.get("user") or "").lower()
        if reads_as_bad_news(said) or loss.reads_as_loss(said):
            return True
    return False


def carries_the_story_on(text, memory):
    """Whether this line is the next line of a hard story the last turn or two began.

    The public reading of `_bad_news_just_before`, for the arbiter: a line that opens on someone
    else ("she took the kids to her mums", "she packed her things last night") is the story going
    on, not a request and not a fact to file. A question is never that - "what do i do about the
    kids" inside the same story is a real ask, and the modules that answer asks should have it.
    """
    if not isinstance(text, str) or "?" in text:
        return False
    clean = " ".join(text.split())
    if not clean:
        return False
    return _bad_news_just_before(clean, memory)


def _learned(text, memory=None):
    """The facts in the line for the store to keep, or an empty dict when there are none.

    The chat-speak is folded first: the store's patterns want "i am", and people type "im", so
    "thanks, also im vegetarian" is a diet like any other. A detail added to what we are already
    on counts too: "i work from home" and "i can put away about 200 a month" store no fact of
    their own, but they are theirs and worth answering with the thing itself rather than a stock
    line. Those come back as {"detail": True}, so the caller has something to say back while the
    store keeps its usual keys."""
    found = facts.extract(_spoken(text)) or facts.extract(text)
    kept = {key: value for key, value in found.items() if key in FACTS and value}
    if kept:
        return kept
    if _adds_one_more_allergen(text, memory):
        # "im allergic to peanuts" then "and milk too": the allergy on record with the milk in
        # it, said back the way a full "and im allergic to milk too" is.
        return {"allergies": _adds_one_more_allergen(text, memory)}
    if _adds_a_detail(text, memory):
        return {"detail": True}
    return {}


def _adds_a_detail(text, memory):
    """Whether the line says something new about the thing we are on, with nothing to store.

    A person who adds a detail ("we live in a flat on the third floor", "i can put away about 200
    a month", "something without meat") is handing over the thing that makes the next answer
    theirs. Saying it back is what a friend does; the stock line ("got it, is there anything you
    would like a hand with?") could have come before any message at all.

    The guards matter more than the rule: there has to be a topic for the detail to belong to, the
    line has to say something the topic did not, and it must not be a question, a fault to
    troubleshoot or a misbehaviour to answer kindly.
    """
    if memory is None:
        return False
    # The line itself has been noted by the store before the reply is written, so the topic it
    # belongs to is the one we were on *before* it, not the line (topics.carried_topic).
    record = topics.carried_topic(memory, text) or topics.current(memory)
    if not record:
        return False
    clean = " ".join(str(text or "").split())
    read = _repaired(clean, memory)
    if "?" in clean or WANTS_ANSWER.search(read) or TROUBLE.search(read):
        return False
    if trouble.reads_as_trouble(read, read.split()):
        return False  # "my washing machine is leaking" is answered by trouble, not said back
    said_words = _words(clean)
    if len(said_words) < 2:
        return False  # "thanks", "same": nothing to say back on its own
    # A bare figure is a figure, not a detail: "actually 6" said back is "Got it - 6.", which
    # tells the person nothing they did not just type.
    if not re.search(r"[A-Za-z\u00c0-\u024f]", _strip_lead_in(clean)):
        return False
    # The same goes for a figure put in place of another when there is nothing to put it in
    # place of: "sorry i mean 800" after "im tired" is a figure and a repair frame and nothing
    # else, and "Got it — you mean 800" claims the bot is going with a number it does not hold.
    if not re.search(r"[A-Za-z\u00c0-\u024f]", REPAIR_FRAME.sub("", clean)):
        return False
    if len(clean.split()) <= 2 and not DIGIT.search(clean):
        return False  # "monday again": small talk, not a detail
    # After "my mum passed away on tuesday", the topic is grief: "it was sudden, i still expect
    # her to ring" is a comfort to give, never a fact to say back.
    carried = (record.get("text") or "") + " " + " ".join(
        str(turn.get("user") or "") for turn in (memory.get("turns") or [])[-3:]
        if isinstance(turn, dict))
    if DEATH_WORDS.search(carried) or _NOT_A_DETAIL_SUBJECT.search(carried):
        return False
    # The same goes for a detail given two turns after bad news: "some days are ok and some
    # aren't" after "we lost the baby last month" wants comfort, not a fact said back.
    for turn in (memory.get("turns") or [])[-2:]:
        if isinstance(turn, dict) and reads_as_bad_news(str(turn.get("user") or "")):
            return False
    known = set(_words(record.get("text") or ""))
    for earlier in record.get("details") or []:
        known |= set(_words(str(earlier)))
    if (_NOT_A_DETAIL.search(read) or _ANSWER_OPENER.match(read) or _ASKED_FOR.match(read)
            or _SAID_YES_NO.match(read) or _ASKS_MIDWAY.search(read) or _FAULT.search(read)):
        return False  # a farewell, a return to an old subject, or a yes/no read of the last turn
    return any(word not in known for word in said_words)


# "my mums called janet" is the mum's name, so said back it takes the apostrophe a person's name
# always has: "your mum's called janet". Without it "your mums called" reads as a crowd of mums.
KIN_POSSESSIVE = re.compile(
    r"\b(your (?:mum|mom|mother|dad|father|son|daughter|sister|brother|wife|husband|partner"
    r"|nan|nana|granny|gran|grandma|grandad|grandpa|aunt|auntie|uncle|niece|nephew"
    r"|boyfriend|girlfriend|fiance|fiancee))s"
    # A figure right after it is the person's age ("my mums 68"), which is the same possessive:
    # "your mums 68" reads like a typo, "your mum's 68" reads like a sentence.
    r"(?= (?:\d+|called|named|name|age|coming|doing|gone|been|had|has|is|was|turns|turned)\b)",
    re.I)


# A count of things after "i'm" is what they have, not what they are: "im 2 dogs" is "you've got
# two dogs", and the sentence people say is never "you're two dogs". The units of time are the
# ones that really are a state ("you're two years in", "you're five minutes away").
A_COUNT_NOT_A_STATE = re.compile(
    r"^you're ((?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve))\s+"
    r"([a-z]{2,}s)\b", re.I)


# A number and a unit of measure is a measurement, not a count of things: "im 2 dogs" is "you've
# got 2 dogs", but "im 90 kilos" is a weight and "im 6 weeks" is a length of time, and both are
# states a person is in. Every unit says so here rather than one rule per fact.
UNITS_OF_MEASURE = frozenset((
    "years", "months", "weeks", "days", "hours", "minutes", "seconds", "nights", "mornings",
    "evenings", "hrs", "mins", "secs",
    # weight
    "kilos", "kilograms", "kgs", "pounds", "lbs", "stones", "grams", "grammes", "ounces",
    # distance, drink and everything else measured
    "miles", "yards", "metres", "meters", "kilometres", "kilometers", "litres", "liters",
    "pints", "cups", "calories", "degrees", "inches"))


# The "who" of a clause, written the way people type it: "my sister whos 40 next week" is the
# same fact as "my sister is 40 next week", so the clause is said back with the apostrophe a
# person's "who's" always has.
WHOS = re.compile(r"\bwhos\b", re.I)


def _says_something(body):
    """Whether the words left after a repair frame say something, rather than naming a bare value.

    "i got the second interview" is a clause; "three", "the tap" and "caffeine" are the thing the
    person put in place of another and nothing else. A repair's own verb is kept for those, so the
    echo does not read "Got it - three", which no longer says three of what.
    """
    return facts._tail_has_a_verb(re.findall(r"[a-z']+", str(body or "").lower()))


# A pointer back with nothing in the chat to point at. The reader below answers a pointer from the
# thing the conversation is about, and on a first line there is no such thing: the reply said the
# pointer back - "Noted: your sister has the same one." - which is a sentence about a thing the
# person never mentioned, and a friend would ask which one. So a pointer with no thing behind it
# asks instead, and never states the pointer back.
NO_REFERENT = (
    "The same one as what?",
    "Which one do you mean?",
    "Same as what? Tell me what we are talking about and I will pick it up.",
    "I have lost the thread - which one do you mean?",
)


# A line whose whole subject is a pointer back at what the chat is already about: "we had another
# one", "my wife got one too", "we had one before". Nothing in it names a thing, so there is
# nothing to say back, and the thing they mean is the subject of the conversation.
POINTS_AT_ANOTHER = re.compile(
    r"\b(?:another one|one more|another|one too|one as well|one aswell|one before"
    r"|one of those|the same one|one like it|one like that)\b", re.I)


# A line that asks whether to have another is a decision, and the deciding readers answer it
# with the thing to weigh up. A pointer here would take that turn to say "Another puppy?".
A_DECISION = re.compile(
    r"\b(?:want|wants|wanted|should|shall|might|could|would|thinking|think|planning|planned"
    r"|considering|maybe|tempted|weighing|worth)\b", re.I)


# "we saw another one" after "we saw a fox in the garden" reports the same outing again, so the
# line points at nothing new: said back it is right ("you saw another one"), named it is wrong
# ("Two gardens, then"). A line that reports an action already done keeps its own answer.
REPORTS_AN_ACTION = re.compile(
    r"\b(?:saw|seen|read|made|bought|finished|started|watched|met|caught|found|killed"
    r"|sold|won|lost)\b", re.I)


# What is left of a pointer line once the pointer is taken out: the person, the verb of having,
# and the little words around them. A word outside this set is a thing of the line's own, and
# "i want another puppy" names its own thing and is never read here.
POINTER_FILLER = frozenset("""
i we you he she they it me my our your his her their its us them mine ours
the a an and but so also too as well just even still already now again then
had has have got gotten get gets bought buy buying made make makes making
finished finish started start read reading seen saw did do does doing
one ones another more of that this these those there here before after
""".split()) | frozenset(facts.RELATIONS) | frozenset("""
wife husband partner boyfriend girlfriend son daughter child kid kids baby mum mom mother
dad father brother sister friend mate colleague boss family parents in laws
""".split())


# "the thing they mean" is not any word: a person in the family, a day, a length of time or a
# word that only points ("another") is not something a person has another of.
NOT_A_THING_TO_HAVE_ANOTHER = frozenset("""
another more one ones same other else lot bit piece time times day days week weeks
month months year years hour hours minute minutes while thing things stuff kind sort
""".split()) | frozenset(facts.RELATIONS)


# The pointer said back as a question about the thing, one of them or several. Every line names
# the thing, so the pool cannot be read out to a line about something else.
ANOTHER_ONE = (
    "Another {thing}?",
    "A second {thing}, then. How is it going?",
    "Another {thing} - what is this one like?",
    "Two {things}, then. How are they getting on?",
)


ANOTHER_ONES = (
    "More {things}?",
    "Another lot of {things}, then. How are they getting on?",
    "More {things} - how are the first lot doing?",
)


BEFORE_ONE = (
    "How does this one compare to the last?",
    "What happened to the first {thing}?",
    "Still got the first {thing}?",
)


# The pointer whose subject is somebody else: "i started a new job" / "my wife got one too" is
# not a second job of the person talking, so "A second job, then" is false about them. The thing
# is named, and the person it belongs to is the one the reply asks about.
SOMEONE_ELSE_POINTS_AT_ANOTHER = re.compile(
    r"\b(?:my|our)\s+([a-z]+(?:[- ](?:in[- ]law|law))?)\s+"
    r"(?:has|have|got|gets|bought|buys|wants|wanted|had|found|rescued|adopted|is getting"
    r"|is buying|is having)\s+"
    r"(?:another one|one too|one as well|one aswell|one of those|the same one|another)\b", re.I)


PRONOUN_POINTS_AT_ANOTHER = re.compile(
    r"\b(?:she|he|they)\s+(?:has|have|got|gets|bought|wants|wanted|had|found|rescued|adopted)\s+"
    r"(?:another one|one too|one as well|one aswell|one of those|the same one)\b", re.I)


ANOTHER_ONE_FOR_SOMEONE = (
    "Your {person} too, then. How is the {thing} going?",
    "Your {person} as well, then - what is the {thing} like?",
)


# They said the thing in the plural, so the reply does too rather than guessing at the one.
ANOTHER_SOME_FOR_SOMEONE = (
    "Your {person} has some too, then. How are the {things} going?",
    "Your {person} as well, then - how are the {things} getting on?",
)


def _the_person_the_pointer_is_about(body, memory):
    """The person the pointer line is about ("wife", "mum", "sister"), or "" for the person
    talking."""
    found = SOMEONE_ELSE_POINTS_AT_ANOTHER.search(body)
    if found:
        word = found.group(1).strip().lower()
        return "" if word in ("own", "self") else word
    if PRONOUN_POINTS_AT_ANOTHER.search(body):
        # "she got one too": the person is the last relation the chat named.
        for turn in reversed((memory.get("turns") or [])[-3:]):
            if not isinstance(turn, dict):
                continue
            said = str(turn.get("user") or "").lower()
            for word in facts.RELATIONS:
                if re.search(r"\bmy\s+" + re.escape(word) + r"\b", said):
                    return word
    return ""


def _the_thing_the_chat_is_on(memory):
    """The thing the chat is about, in the words the person used, whether they said one or
    several, and the plural: ("puppy", False, "puppies") or ("tomatoes", True, "tomatoes").
    ("", False, "") when the chat is not about a thing a person can have another of.

    The subject is kept as a stem ("tomatoe"), so the word is looked for again in what the person
    actually said: a reply that names the thing has to use their word for it, not the stem.
    """
    phrase = " ".join(str(topics.subject(memory) or "").split()).lower()
    if not phrase:
        return "", False, ""
    # The subject is a bag of the chat's words, and its last one was read as the thing: "my dad
    # died" then "we had another one" was answered "A second died, then.", and "we go to portugal
    # every year" then the same line "A second every, then." A thing a person can have another of
    # is named behind a determiner ("a puppy", "my bike"), so only those words are read, and a
    # line with none of them leaves the pointer to the reader that answers it as it stands.
    named_words = set()
    for turn in reversed((memory.get("turns") or [])[-3:]):
        if isinstance(turn, dict):
            named_words.update(_a_thing_the_line_named(turn.get("user")))
    named_words -= NOT_A_SECOND_OF
    if not named_words:
        return "", False, ""
    stems = {topics.stem(word) for word in named_words}
    stem = ""
    for word in re.split(r"[^a-z]+", phrase):
        if (len(word) > 2 and word not in named.NOT_THE_THING
                and word not in NOT_A_THING_TO_HAVE_ANOTHER
                and (word in named_words or topics.stem(word) in stems)):
            stem = word
    if not stem or stem in NOT_A_THING_TO_HAVE_ANOTHER or stem in facts.RELATIONS:
        return "", False, ""
    if _something_they_avoid(memory, stem) or _a_name_the_store_holds(memory, stem):
        return "", False, ""
    said = ""
    for turn in reversed((memory.get("turns") or [])[-3:]):
        if not isinstance(turn, dict):
            continue
        for word in re.findall(r"[a-z']+", str(turn.get("user") or "").lower()):
            if word == stem or topics.stem(word) == stem:
                said = word
                break
        if said:
            break
    said = said or stem
    return said, said != stem, _plural(said)


A_NAME_GIVEN = re.compile(r"\b(?:called|named|name is|name's|names)\s+([a-z']+)", re.I)


def _a_name_the_store_holds(memory, stem):
    """Whether the word is a name somebody or some animal was given, not a thing of its own.

    "my sister is called meg" then "my brother has one too" was read as a pointer at another
    one, and named it: "A second meg, then." A name is not a thing a person has another of, so
    a name the store holds - a pet's, a person's, or one given on the last turn or two - is left
    to the reader that answers the line as it stands.
    """
    if not isinstance(memory, dict):
        return False
    names = []
    known = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    for pet in known.get("pets") or []:
        if isinstance(pet, dict) and pet.get("name"):
            names.append(str(pet["name"]))
    for other in memory.get("others") or []:
        if isinstance(other, dict) and other.get("name"):
            names.append(str(other["name"]))
    person = memory.get("person")
    if isinstance(person, dict) and person.get("name"):
        names.append(str(person["name"]))
    for turn in (memory.get("turns") or [])[-3:]:
        said = str((turn or {}).get("user") or "") if isinstance(turn, dict) else ""
        found = A_NAME_GIVEN.search(said)
        if found:
            names.append(found.group(1))
    return any(topics.stem(name) == stem for name in names if name)


def _something_they_avoid(memory, stem):
    """Whether the thing the chat is on is something the person is allergic to or avoiding.

    "im allergic to nuts" then "my son has one too" points at the allergy the son shares, not at
    more nuts: the "one" the son has is the allergy, and "More nuts?" is the wrong reply to it.
    A thing the store holds as an allergy or as a food to avoid is not something a person has
    another of, so the pointer is left to the reader that answers the allergy.
    """
    if not isinstance(memory, dict):
        return False
    known = memory.get("user") if isinstance(memory.get("user"), dict) else {}
    meal = memory.get("meal") if isinstance(memory.get("meal"), dict) else {}
    for word in list(known.get("allergies") or []) + list(meal.get("avoid") or []):
        if topics.stem(str(word)) == stem:
            return True
    return False


def _plural(word):
    """The plural of a thing the person named, so a reply can say "two puppies"."""
    if word.endswith("s"):
        return word  # they said the plural already ("tomatoes", "roses")
    if word.endswith(("x", "z", "ch", "sh")):
        return word + "es"
    if len(word) > 2 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


# A contraction is never the thing a line names, and neither is a verb that is never a noun: "my
# tumble dryer isnt heating" named "isnt" (and the reply was "what is the isnt like?"), "my wages
# went in late" named "went", "my phone wont charge" named "charge", which is a verb there though
# it is a noun elsewhere ("a charge for the battery"), so no list of bad words can settle it. A
# verb *ends* the noun phrase rather than being its head, which is the rule the auxiliaries above
# already follow. The negations are a closed class. The verbs are only the forms that are never a
# noun in their own right - "heating", "leaves" and "left" are things a line can name, so they are
# not here.
ENDS_THE_THING_VERB = frozenset("""
aint arent cant couldnt didnt doesnt dont hadnt hasnt havent isnt mustnt neednt shant wasnt
werent wont wouldnt shouldnt
went gone came got gotten took taken gave given told said seen knew known kept
brought bought found goes comes says keeps sees knows thinks tells gives takes makes
""".split())


def _is_a_contraction(word):
    """Whether the word is a contraction ("isn't", "wont", "didnt") rather than a thing."""
    return "n't" in word or word in ENDS_THE_THING_VERB


A_DETERMINER = re.compile(
    r"\b(?:a|an|the|my|our|his|her|their|your|another|some|two|three|four|five|six|"
    r"seven|eight|nine|ten)\b", re.I)


# A word after the determiner that ends the thing named: "a new job" is a job, "a puppy for my
# son" is a puppy. Without a part-of-speech tagger the ends of a noun phrase are what can be
# named, so a link word, a pronoun, an auxiliary or an adverb takes the last word back.
ENDS_THE_THING = frozenset("""
in on at to for with from of about by into onto over under out up down off through across along
after before during since until while when where why how what which who whom whose that this
these those and but or so because if than then
i me you we us they them he him she it its am is are was were be been being have has had do does
did will would can could should may might must not no
very really quite too also just still again now last next
bit lot few couple other same whole rest most least more less only first
""".split())


# What nobody has another of: traffic, weather and homework are named behind a determiner like a
# thing is, but "A second traffic, then." is not a line about anything.
NOT_A_SECOND_OF = frozenset("""
traffic weather news advice information knowledge music homework housework work sleep noise mess
rubbish luck rain snow water wind light heat fun health pain stress exercise help space shopping
cleaning washing food drink dinner breakfast lunch tea coffee time money
""".split())


def _a_thing_the_line_named(text):
    """The head words of the noun phrases a line names behind a determiner: "we got a puppy last
    year" -> {"puppy"}, "i started a new job" -> {"job"}, "we called the puppy rufus" ->
    {"rufus"} (a name, so the caller stands down on it)."""
    words = re.findall(r"[a-z']+", str(text or "").lower())
    out = set()
    for at, word in enumerate(words):
        if not A_DETERMINER.fullmatch(word):
            continue
        head = ""
        for after in words[at + 1:at + 4]:
            if after in ENDS_THE_THING or len(after) <= 2 or _is_a_contraction(after):
                break
            head = after
        if head:
            out.add(head)
    return out


def _a_loss_just_before(memory):
    """Whether the last turn or two is a death: that turn belongs to the feelings reader."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    for turn in turns[-2:]:
        if isinstance(turn, dict) and facts.DIED.search(str(turn.get("user") or "")):
            return True
    return False


def _another_of_what_we_said(clean, memory):
    """The reply to a line that only points at another of the thing the chat is about, or None."""
    if not isinstance(memory, dict):
        return None
    turns = memory.get("turns")
    body = clean.strip()
    if not body or "?" in body or len(body.split()) > 8:
        return None
    if A_DECISION.search(body):
        return None
    found = POINTS_AT_ANOTHER.search(body)
    if not found:
        return None
    left = [word for word in re.findall(r"[a-z']+", POINTS_AT_ANOTHER.sub(" ", body).lower())
            if word not in POINTER_FILLER]
    if left:
        return None  # the line names a thing of its own
    if (REPORTS_AN_ACTION.search(body)
            and found.group(0).lower() not in ("one before", "the same one")):
        return None  # the same action reported again, not a second of the thing
    if _a_loss_just_before(memory):
        # Nothing is another one beside a death: "my dad died" then "we had another one" was
        # answered "A second died, then.", which is the worst line the bot could give there, and
        # the feelings reader has that turn.
        return None
    one, several, plural = _the_thing_the_chat_is_on(memory)
    if not one:
        # A pointer with nothing behind it. There is no thing to name, and saying the pointer back
        # tells the person nothing ("Noted: my sister has the same one"), so the reply asks.
        return pick(NO_REFERENT, memory, seed_text=body)
    person = _the_person_the_pointer_is_about(body, memory)
    if person:
        # The pointer says the other person has one too, so the reply is about them, not a second
        # of the thing in this house.
        pool = ANOTHER_SOME_FOR_SOMEONE if several else ANOTHER_ONE_FOR_SOMEONE
        return pick(pool, memory, seed_text=body).format(
            person=person, thing=one, things=plural)
    if found.group(0).lower() == "one before":
        return pick(BEFORE_ONE, memory, seed_text=body).format(thing=one)
    if several:
        return pick(ANOTHER_ONES, memory, seed_text=body).format(things=plural)
    return pick(ANOTHER_ONE, memory, seed_text=body).format(thing=one, things=plural)


# A bare noun-phrase said back is kept with the repair's own words in front of it, so the echo
# says what the person was talking about: "sorry, i mean three" is "Got it - you mean three".
# A correction that says its own "no" and then the thing carries no such repair - "actually no, a
# scooter" came back as "Got it - no, a scooter", which hands the person their correction back
# instead of the thing they settled on. The opener is only a "no"/"nope" (with an optional
# "actually"/"oh"/"sorry" in front of it) whose whole tail is the thing.
def _only_the_correction_in_front(kept, body):
    """True when `kept` is `body` with nothing in front of it but the correction's own opener.

    The opener is read by the correction reading itself (`facts.is_a_correction_opener`), so every
    word that announces a correction there - "no", "no wait", "sorry", "actually", "scratch that" -
    is an opener here too. This list used to be its own pattern that only gave way to a "no", so
    "wait, four brothers" was said back whole and the person got their own opener handed to them:
    "Got it - wait, four brothers."."""
    kept = " ".join(str(kept or "").split())
    body = " ".join(str(body or "").split())
    if not kept or not body or kept == body:
        return False
    if not kept.lower().endswith(body.lower()):
        return False
    front = kept[:len(kept) - len(body)]
    return bool(front.strip() and facts.is_a_correction_opener(front))


# The person's contraction, kept in the bot's wording: "you've got", never "you have got".
HAVE_GOT = re.compile(r"\b(you|we)\s+have\s+got\b", re.I)


HAVE_A = re.compile(r"\b(You|you|We|we)\s+have\s+a\b")


def _only_a_dislike(body, found):
    """True when the line is a dislike of a thing and nothing else.

    "hates" and "can't" are in `TROUBLE`, which is there for a person being difficult: "my boss
    keeps shouting at me" is trouble and must not be filed away. A dislike is the same words about
    a thing — "i hate cats", "i cant stand cats" — and taking the taste verb out leaves nothing
    that reads as someone's misbehaviour.
    """
    if not (found or {}).get("tastes"):
        return False
    return not TROUBLE.search(taste.DISLIKE_IN.sub(" ", body))


def only_a_dislike(text, memory=None):
    """True when the line is a stated dislike of a thing and nothing else.

    "i hate cats" and "i cant stand cats" are facts about the person's taste, and both words are
    also words for a bad day ("hate", "can't"): read as mood they get "That sounds rough", which
    is an answer for an event that happened to them, not for a thing they do not like.
    """
    clean = " ".join(str(text or "").split())
    if not clean:
        return False
    return _only_a_dislike(_strip_lead_in(clean), _learned(clean, memory))


def _tells_it(clean, found=None):
    """Whether the line can be said back: a state of their world, not someone's misbehaviour."""
    body = _strip_lead_in(clean)
    others = [entry for entry in (found or {}).get("others") or [] if isinstance(entry, dict)]
    if any("name" in entry or "age" in entry for entry in others):
        # "my mums called janet and shes 72" is a fact about her: it is theirs to keep, however
        # long the sentence is.
        return True
    if facts.foods_ruled_out(found):
        # "my son cant eat fish" has a "cant" in it, but it is what the son eats, not something
        # he did to them: the store filed it as his allergy, and the line is a limit to say back.
        # Read as trouble it fell through to the plain acknowledgement, and the line they had
        # just told the bot came back as "Thanks for telling me" with nothing in it.
        return True
    if TROUBLE.search(body) and not _a_diet(found) and not _only_a_dislike(body, found):
        return False
    if (found or {}).get("done"):
        return True  # "i met my sister for lunch on friday" is theirs whatever its length
    return bool(STATE.search(body)) or len(body) <= FRAGMENT


def _a_diet(found):
    """"she doesn't eat meat" has a "doesn't" in it, but it is what she eats, not what she does
    to the person: the store read a diet in the line, so the negation is not a complaint."""
    if not isinstance(found, dict):
        return False
    if found.get("diet") or found.get("no_meat"):
        return True
    return any(entry.get("diet") for entry in (found.get("others") or [])
               if isinstance(entry, dict))


# The words in front of an age or a height, and the units it can arrive in: together they say
# whether the figure is the whole line or one clause of a longer one.
FIGURE_LEAD = re.compile(
    r"^(?:i\s*(?:'m|am)|im|i\s+just\s+turned|my\s+(?:age|height)\s+is)\b[\s,]*", re.I)


FIGURE_FILLER = frozenset("""year years yrs yr old this now today already and""".split())


FIGURE_UNIT = frozenset("""ft foot feet in inch inches cm m st stone pounds pound lbs lb
    kilo kilos kg metres meters""".split())


# The inches of a height said as a word ("im 5 foot ten"), which is one part of the figure and
# not a word added to it.
FIGURE_WORD = frozenset("""one two three four five six seven eight nine ten eleven""".split())


def _only_the_figure(clean):
    """Whether the line says nothing but an age or a height: "im 34", "im 6 foot 2", "im 34 this
    year". A figure inside a longer sentence is not the thing the sentence is about."""
    body = " ".join(FIGURE_LEAD.sub("", _strip_lead_in(clean)).split())
    words = [word.strip(".,!;:") for word in body.split()]
    words = [word for word in words if word and word.lower() not in FIGURE_FILLER]
    # "5 foot 10" and "175cm" are the same kind of line: a figure, and the unit it is counted in
    # may be stuck to the number ("175cm") or standing on its own ("5 foot 10").
    return all(re.fullmatch(r"\d{1,3}(?:st|nd|rd|th)?(?:(?:cm|m|ft|in|kg|st|lbs?)s?)?", word)
               or word.lower() in FIGURE_UNIT or word.lower() in FIGURE_WORD for word in words)


# A line that carries on the question they just asked names a thing - often with a time after it
# - and says nothing else: "whats the capital of australia" then "and the weather there in june".
# There is no verb and nobody in it, so it is not a fact about them, it is the second half of one
# question. Said back as a fact ("Got it - the weather there in june") it reports something they
# never told us, and the module that answers weather never sees the line.
A_CONTINUATION = re.compile(r"^(?:and|also|plus|or|what about|how about|and what about)\b", re.I)


# Anything that makes a clause a sentence about someone: a verb of any tense, the chat-speak form
# of one ("dont", "cant"), or a person ("i", "my", "we"). A tail has none of them.
A_CLAUSE = re.compile(
    r"\b(?:is|are|am|was|were|be|been|being|isnt|arent|wasnt|werent|has|have|had|hasnt|havent|"
    r"hadnt|do|does|did|dont|doesnt|didnt|will|wont|would|wouldnt|can|cant|could|couldnt|should|"
    r"shouldnt|shall|may|might|must|got|get|gets|getting|go|goes|going|went|gone|need|needs|"
    r"needed|want|wants|wanted|like|likes|liked|think|thinks|thought|know|knows|knew|take|takes|"
    r"taking|took|make|makes|making|made|start|starts|started|come|comes|came|live|lives|lived|"
    r"work|works|worked|feel|feels|felt|keep|keeps|kept|try|tries|trying|look|looks|looking|"
    r"plan|plans|planning|book|booked|hope|hoping|wait|waiting|see|saw|seen|say|says|said)\b",
    re.I)


A_SOMEONE = re.compile(
    r"\b(?:i|i'm|im|i've|ive|i'd|id|i'll|ill|me|my|we|we're|were|we've|our|us)\b", re.I)


def _the_rest_of_a_question(clean, before=""):
    """Whether the line is the tail of the question before it, with no fact of its own.

    "and the weather there in june" after "whats the capital of australia": a conjunction, a
    thing and a date, and nothing else. Three things have to hold, because each one alone is
    wrong somewhere:

    - there is a conjunction ("and", "also", "what about"), so it is the second half of something;
    - the rest has no verb and nobody in it, so it states nothing: "and i have two cats" and
      "also my knee is bad" are things they told us, "and the weather there in june" is not;
    - the line before it asked something. "i have two cats" then "and a dog" is a dog; "whats the
      capital of australia" then "and the weather there in june" is the rest of that question.
    """
    line = " ".join(str(clean or "").split())
    match = A_CONTINUATION.match(line)
    if not match:
        return False
    rest = line[match.end():].strip(" ,.;:-!?")
    if not rest:
        return False
    if A_CLAUSE.search(rest) or A_SOMEONE.search(rest):
        return False
    return reads_as_an_ask(before)


# The same reading for a module that is deciding whether a line is something they told us: the
# summary of the chat and the receipt said back both want it, and neither wants to import a
# private name across files.
the_rest_of_a_question = _the_rest_of_a_question


# A correction opens with "no,": "no, its wednesday not tuesday" said back as "no it's
# wednesday" reads like an argument. Only with the comma, because "no heating since friday" and
# "no one at work likes me" are the sentences themselves.
#
# The same frame in the words people actually type went into the echo whole: "no wait, i got the
# second interview" came back "Got it \u2014 no wait, you got the second interview", as though the
# steering were part of the fact, and "sorry, i mean saturday" as "Got it \u2014 Sorry, you mean on
# Saturday." `LEAD_IN` already has "sorry" and "actually"; what it never had was the repair's own
# verbs and the "wait" that follows them. Every form here needs its comma or its verb, so "no
# onions", "wait for the kettle" and "i mean it" keep the words they were said with.
# A bare "no" in front of a correction is the correction, not the fact: "my son is 8" then
# "no hes 9" was said back as "Got it - no he's 9", which hands the person their own contradiction
# and buries the thing that was put right. The forms above all need a comma or a verb; this one
# needs the rest of the line to open on the person or the thing itself, so "no onions", "no
# heating since tuesday" and "no hot water" keep the word that carries their meaning.
NO_THEN_A_LINE = (
    r"no\s+(?=(?:"
    # The person or the thing, as the subject of what follows, and its contraction: "no hes 9",
    # "no it was my idea not the kids", "no we went in june", "no the quiet is the best bit of
    # it", "no not the boiler the pump". Written as the words themselves rather than as every
    # phrase they can start, because the list of phrases had only the present tense in it and
    # missed the rest: "no it was my idea not the kids" came back as "Got it - no it was your
    # idea not the kids", the person's own contradiction handed back to them as the fact.
    r"i|im|i'm|we|we're|were|you|youre|you're|he|hes|he's|she|shes|she's|it|its|it's|"
    r"they|theyre|they're|this|that|thats|that's|these|those|there|"
    # And the thing named with its own word instead of a pronoun, or the right thing in front of
    # the wrong one: "no the blue one", "no my sister", "no our lass", "no not the boiler".
    # People write "no wifi" and never "no the wifi", so the article or the possessive is what
    # makes this the correction rather than the sentence.
    r"the|not|my|our|your|his|her|their"
    r")\b)")


NO_THEN_A_LINE_ONLY = re.compile(r"^\s*" + NO_THEN_A_LINE, re.I)


NO_LEAD = re.compile(
    r"^\s*(?:(?:"
    r"no\s*,"
    r"|" + NO_THEN_A_LINE +
    r"|(?:no\s+|oh\s+|sorry\s+|actually\s+)?(?:wait|hang\s+on|hold\s+on)\s*,"
    r"|(?:i\s+(?:meant|mean)(?:\s+to\s+say)?"
    # "i mean it" and "i mean that" are the emphatic use, not a repair: nothing replaces them.
    r"(?!\s*,?\s*(?:it|that|this|so)\b(?:\s*,?\s*\w+){0,2}\s*[.!?]*\s*$)"
    r"|you\s+mean|make\s+that)\b\s*,?"
    r"|(?:sorry|apologies|actually|oops|oh)\s*,"
    r")\s*)+", re.I)


# A reaction in front of the fact: "lucky you. i've got a bathroom to sort out" was said back as
# "Noted: lucky you. you've got a bathroom to sort out.", and "fair enough, i have a bathroom to
# sort out" as "Noted: fair enough. you have a bathroom to sort out." The reaction is the person
# answering the bot - or agreeing with it - and it is not part of the thing they are telling it,
# so a short clause of nothing but reaction words in front of the fact comes off before the fact
# is read. Three things keep it safe: the words are a closed table (a phrase like "no worries
# about the boiler" is not a reaction and keeps its words), the clause has to end in its own
# punctuation and be followed by more of the line, and "good luck with the interview" - a whole
# line, with no clause after it - is never touched.
REACTION_PHRASES = frozenset((
    "quiet one", "quiet day", "busy one", "busy day", "slow day", "long day", "not bad",
    "not much", "nothing much", "not a lot", "all good", "can't complain", "cant complain",
    "same as ever", "good thanks", "fine thanks", "no complaints", "same old", "usual stuff",
    "you too", "likewise", "went ok", "went well", "went fine", "so so", "so-so", "up and down",
    "not too bad",
))


REACTION_WORDS = frozenset("""
lucky you fair enough got it sounds good sound good great nice cool lovely perfect ace brilliant
oh dear dear me good luck well done makes sense same here me too that's right exactly agreed
no worries okay ok thanks ta cheers haha lol ha magic typical bless you what a shame that's a
shame of course indeed true sure yeah yes oh wow ouch yikes a
""".split())


_REACTION_CLAUSE = re.compile(r"^([^.?!,;:]{1,32})[.?!,;:]+\s*(?=\S)")


def _after_a_reaction(text):
    """`text` without a short reaction clause in front of it ("lucky you.", "fair enough,")."""
    match = _REACTION_CLAUSE.match(text)
    if not match:
        return text
    clause = " ".join(match.group(1).split()).lower()
    words = [word.strip("'\u2019") for word in match.group(1).split()]
    if not words or len(words) > 5:
        return text
    if clause not in REACTION_PHRASES and not all(word.lower() in REACTION_WORDS
                                                for word in words):
        return text
    return text[match.end():].strip()


def _strip_lead_in(clean, keep_the_repair=False):
    """`clean` without the "hi, so," and the like in front of the fact.

    `keep_the_repair` leaves the repair's own verb on ("you mean three"), for a correction whose
    fact is a bare number or noun: "Got it - three." is not a sentence and no longer says three
    what, where "Got it - you mean three." is the person's own frame and still reads.
    """
    text = clean.strip(" ,;:-")
    # The bare "no" comes off either way: it is the person saying the last thing was wrong,
    # and a correction that keeps its own verb ("you meant with your flatmate") is not made
    # into a contradiction by leaving it on: "Got it - no you meant with your flatmate".
    text = NO_THEN_A_LINE_ONLY.sub("", text)
    if not keep_the_repair:
        text = NO_LEAD.sub("", text)
    changed = True
    while changed:
        changed = False
        # A greeting in front of a correction ("so, no wait, its tuesday") leaves the frame
        # exposed once the greeting has gone, so the frame is looked for again after each lead.
        bare = text if keep_the_repair else NO_LEAD.sub("", text)
        if bare != text:
            text, changed = bare, True
            continue
        for lead in sorted(LEAD_IN, key=len, reverse=True):
            low = text.lower()
            if low.startswith(lead) and low[len(lead):len(lead) + 1] in ("", " ", ",", ";", ":",
                                                                       "-", "!", "?", "."):
                text = text[len(lead):].lstrip(" ,;:-!?.")
                changed = True
                break
        if not changed:
            done = _after_a_reaction(text)
            if done != text:
                text, changed = done, True
    return text


def without_the_frame(clean):
    """"sorry, i mean saturday" with the apology and the repair taken off: "saturday".

    For a module that says a correction back in the person's own words: the frame is what they
    said to steer, not the thing they steered to."""
    return _strip_lead_in(" ".join(str(clean or "").split()))


# The count of top grades is written, not spelled: "3 a stars" is "three A*s". And a degree class
# is written "2:1", where the chat-speak fold spelled the first figure and left the second:
# "my son got a 2 1 in his degree" came back as "Your son got a two 1 in his degree".
COUNTED_STARS = re.compile(
    r"\b(?:(?:a|an)\s+)?(?P<count>[1-9]|1[0-2])\s+a[\s*'-]?stars?\b", re.I)


# One A* said without a count keeps its article: "my son got an a star in maths" came back as
# "Your son got an a star in maths", which is the person's typing handed back to them.
ONE_STAR = re.compile(r"\b(?:an?|one)\s+a[\s*-]?star\b", re.I)


STAR_COUNT = {1: "an A*", 2: "two A*s", 3: "three A*s", 4: "four A*s", 5: "five A*s",
              6: "six A*s", 7: "seven A*s", 8: "eight A*s", 9: "nine A*s", 10: "ten A*s",
              11: "eleven A*s", 12: "twelve A*s"}


# And a count of letter grades is written the way the grade is: "she got 3 a stars and 2 as" came
# back as "three A*s and two as". The letter only counts where the list ends or goes on to another
# grade, because "i got 2 as well" is a number and a word.
COUNTED_LETTERS = re.compile(
    r"\b(?P<count>[2-9]|1[0-2])\s+(?P<letter>a|b|c|d)(?:'?s|s)\b"
    r"(?=\s*(?:$|[,.;!?]|and\b|but\b))", re.I)


LETTER_COUNT = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
                9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


A_DEGREE = re.compile(r"\b(?:degree|degrees|uni|university|graduat\w*|honours|bsc|ba|masters?|"
                      r"phd|dissertation|final year)\b", re.I)


DEGREE_CLASS = re.compile(r"\b(?P<first>[12])\s*[:.\- ]\s*(?P<second>[12])\b")


def _spoken(said):
    """`said` with the chat-speak folded, so the echo does not read "im" or "dont" or "yrs"."""
    said = COUNTED_STARS.sub(lambda match: STAR_COUNT[int(match.group("count"))], said)
    said = ONE_STAR.sub("an A*", said)
    said = COUNTED_LETTERS.sub(
        lambda match: LETTER_COUNT[int(match.group("count"))] + " " + match.group("letter").upper()
        + "s", said)
    if A_DEGREE.search(said):
        said = DEGREE_CLASS.sub(lambda match: match.group("first") + ":" + match.group("second"),
                                said)
    said = WITH_SLASH.sub("with ", said)
    said = TWO_TO.sub(lambda match: match.group(0)[:-1] + "to", said)
    said = TWO_PLACE.sub("to ", said)
    said = TWO_VERB.sub("to ", said)
    out = []
    words = said.split()
    for place, word in enumerate(words):
        bare = word.lower().strip(".,;:!?")
        tail = word[len(word.rstrip(".,;:!?")):]
        after = words[place + 1].lower().strip(".,;:!?") if place + 1 < len(words) else ""
        before = words[place - 1].lower().strip(".,;:!?") if place else ""
        if bare == "yer":
            out.append(("yeah" if not after or after in YES_AFTER else "your") + tail)
        elif bare == "its" and before in ITS_OWNS_AFTER:
            out.append(word)  # the possessive: "got its screen", not "got it's screen"
        elif bare in SPEAK:
            out.append(SPEAK[bare] + tail)
        elif bare in SHORT:
            out.append(SHORT[bare] + tail)
        else:
            out.append(word)
    return " ".join(out)


# A correction said back whole repeats the wrong thing: "sorry, my budget is 400 a month not
# 300" came back as "your budget is 400 a month not 300 - I'll keep any suggestions inside it",
# which sounds like the bot took "not 300" as part of the budget. The old value is not part of
# the fact, so the echo stops before it. Only a contrast that is a value, not a verb, is cut:
# "i would rather not say" is not a correction, and "not" belongs in it.
CONTRAST = re.compile(r"\s*,?\s+not\s+(?P<old>[\w'’$£€.,:/-]+"
                      r"(?:\s+[\w'’$£€.,:/-]+){0,3})\s*$", re.I)


# The correction that puts the right value on the end of the thing said again: "hes not 4 hes
# 5", "shes not 7 shes 8", "im not 40 im 45". The wrong value is in the middle and the thing is
# named twice around it, so the front half of the line is not the fact - cutting there left the
# bare pronoun and dropped the number the person had just given ("Got it - he's.", "Got it -
# you're."). What is kept is the thing as it is said the second time, with the new value on it.
# The old value has to be a value, so "i am not sure i am ready" stays the statement it is.
CONTRAST_SAID_AGAIN = re.compile(
    r"^(?P<thing>[a-z]+(?:\s+[a-z]+){0,2})\s+not\s+(?P<old>[\w'’$£€.,:/-]+)\s+"
    r"(?P=thing)\s+(?P<new>[\w'’$£€.,:/-]+(?:\s+[\w'’$£€.,:/-]+){0,2})\s*$",
    re.I)


# Words that make the words after "not" a clause rather than the wrong value: after one of them
# the line is a statement ("i would rather not say", "im not sure yet"), not a correction.
NOT_A_VALUE = frozenset("""a an the any sure really very too that this it them me you him her us
say said tell go going gone get got want need like mind be been being am is are was were have
has had can could would should will do does did make take give put keep try yet even still
allowed able bothered""".split())


# A line settling a choice carries the words of the settling as well as the thing: "actually make
# it a dog" was said back as "Noted: make it a dog" and "lets go with the focus" as "Got it — lets
# go with the focus", which hands the person the frame they put round the thing rather than the
# thing. The frame is the shape of the sentence, not part of what was chosen, so it comes off and
# the thing is said back on its own: "a dog", "the focus".
#
# Only the frames that can only be a pick. "going with" is also how a person says who they are
# going somewhere with ("we're going with the kids to spain"), so it is not here, and neither is a
# bare "go for".
PICK_FRAME = re.compile(
    r"^\W*(?:"
    r"(?:let'?s|let\s+us|i'?ll|we'?ll|i\s+will|we\s+will)\s+go\s+(?:with|for)\b"
    r"|(?:i|we)\s+(?:have\s+|had\s+)?(?:settled|decided|decide|settle)\s+(?:on|for)\b"
    r"|(?:i|we)\s+(?:have\s+|had\s+)?(?:opted|opt)\s+for\b"
    r"|(?:i|we)\s+(?:picked|pick|chose|choose)\b"
    r"|(?:i|we)'?ve\s+(?:settled|decided|gone)\s+(?:on|for|with)\b"
    r"|(?:make|makes)\s+(?:it|that)\b"
    r")", re.I)


def _pick_off(said):
    """`said` without the words that say a choice was made: "lets go with the focus" -> "the
    focus", "make it a dog" -> "a dog".

    A frame with nothing after it ("lets go with that") is left whole: there is no thing to say
    back, and the line is not an echo at all.
    """
    match = PICK_FRAME.match(said or "")
    if not match:
        return said
    rest = (said or "")[match.end():].strip(" ,;:-.!?\u2014")
    if len(rest.split()) < 1:
        return said
    return rest


def _tail_off(said):
    """`said` without the chat-speak hanging off the end, so the echo is the fact and not the
    filler: "im veggie tho" -> "you're veggie", "im veggie" unchanged."""
    said = without_filler(said)
    # The phrases the fact store trims before it files an item are not part of the fact said
    # back either: the store held "dairy" for "im allergic to dairy these days" and the echo
    # said "you're allergic to dairy these days, good to know".
    words = said.split()
    while words:
        low = " ".join(words).lower().strip(" ,;:-")
        cut = next((phrase for phrase in facts.FILLER_TAIL_PHRASES if low.endswith(phrase)), None)
        if not cut or len(words) <= len(cut.split()):
            break
        words = words[:-len(cut.split())]
    return " ".join(words).strip(" ,;:-")


# A correction comes with the reason it was made: "actually i mean 75 because i lost some",
# "no its 900 since the boiler went". The reason explains the change and is not part of the value,
# the same way the replaced value in "my budget is 400 not 300" is not part of it, so what is said
# back is the corrected fact. Only a line that corrects is trimmed: "im tired because i was up all
# night" is the whole fact, and the reason is what makes it one.
A_REASON_TAIL = re.compile(r"\s+(?:because|cos|coz|cuz|'cause|since)\b[^.!?]*", re.I)


A_CORRECTION_IN_FRONT = re.compile(
    r"^\s*(?:actually|no|nope|sorry|wait|oh|i\s+mean|i\s+meant|make\s+that)\b", re.I)


def _reason_off(said, clean):
    """`said` without the reason a correction gave for itself: "you mean 75 because I lost some"
    -> "you mean 75".

    The reason is the why of the change, not the value that changed, so a reply that names the
    value says the value: "you said 75 because." is the machine. A line that is not a correction
    keeps its reason, because there the reason is the fact ("you're tired because you were up all
    night").
    """
    if not A_CORRECTION_IN_FRONT.match(clean or ""):
        return said
    match = A_REASON_TAIL.search(said or "")
    if not match or not said[:match.start()].strip(" ,;:-"):
        return said
    return said[:match.start()]


# The words that can stand between the old value of a restated correction and the new one: the
# subject said again ("4 hes 5") or a pronoun and its verb ("4 my son is 5"). A unit word or a
# noun ("miles", "pm", "kids") makes two figures two different things rather than one value put
# right ("im not driving 5 miles its 10"), and the words of that line are left as they were.
BETWEEN_VALUES = frozenset("""he she it they we you i his her its their our my
is was are be been am just only now actually really still but
hes shes its theyre im youre were s""".split())


# What counts as the value a correction replaces: a number, an amount, or a day or month.
VALUE = re.compile(r"\d|^(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                   r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
                   r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|a|an|"
                   r"grand|quid|pm|am)$", re.I)


# A correction that puts a new value where the old one was, in the shape that names no old value:
# "make it four" after "im going to the gym three times a week", "make that 10k" after "i run 5k
# every morning". facts.CORRECTION_MAKE reads the same shape for the store, and the store can only
# correct a value it holds; a routine they described is not one, so these lines fell through every
# module to the search hedge ("That's beyond what I know well, sorry"), which is the one reply a
# correction must never get: the person is not asking a question, they are telling the bot
# something changed. The value goes back up with the unit of the line before it, when that line
# has one, so "four" arrives as "Four times a week, then." and not as a bare number.
MAKE_A_VALUE = re.compile(
    r"^\s*(?:(?:no|nope|sorry|ah|oh|ok|okay|right|and|so|well|actually|wait|hmm)[,.]?\s+)*"
    r"(?:make\s+(?:it|that)|change\s+(?:it|that)\s+to|switch\s+(?:it|that)\s+to)\s+"
    r"(?P<value>[^,.!?;]{1,40}?)\s*[.!]*\s*$", re.I)


# The words a value can be made of when it carries no digit: "four", "twice", "every day", "a
# grand", "10k" already has one. "make it stop" and "make it bigger" are the end of a sentence
# ("my boiler is broken" / "a new sofa"), and folding "Stop it is." into the chat is what the
# store already refuses to do.
VALUE_WORDS = frozenset("""half quarter past to oclock am pm once twice one two three four five six
seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen
twenty thirty forty fifty sixty seventy eighty ninety hundred thousand a an grand the
every of hour hours minute minutes week weeks day days month months year years time times per a
kilo kilos kg mile miles km pound pounds quid dollar dollars euro euros""".split())


# The words a line measures its figure in: "three *times a week*", "5k *every morning*". The new
# value of a correction is said back with them, so "make it four" after the gym line answers
# "Four times a week, then." and not a bare number.
UNITS_AFTER = frozenset("""times time a an per week weeks day days month months year years hour
hours minute minutes mile miles km kilo kilos pound pounds quid egg eggs cup cups spoon
spoons every morning evening night weekend""".split())
