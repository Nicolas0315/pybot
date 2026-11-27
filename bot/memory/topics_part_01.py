"""Part 1 of 8 of the module, split out of `topics`.

Everything here is re-exported from `topics`, so callers import it from there as before.
"""
import re




WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


STOPWORDS = frozenset("""
a an the and or but if so of to in on at for with without about as by from into over after
before between during out up down off again further then once here there when where why how all
any both each few more most other some such no nor not only own same than too very can could
should would will shall may might must do does did doing have has had having am is are was were
be been being i me my we us our you your he him his she her it its they them their this that
these those what which who whom whose
i'm i've i'll i'd don't doesn't didn't can't won't isn't aren't wasn't weren't it's that's
# A pronoun typed without its apostrophe is still a pronoun, and it is not a thing a line is
# about: "shes 84, what can we do" is "she is 84" with the apostrophe left off, and read as a
# word of its own "shes" stems to "sh", which no entry in the world is about. So the line was
# read as naming a subject of its own, the entry the chat was already on was dropped as not
# being about it, and a follow-up about the falls answer went to a search hedge - while the same
# line written "she is 84" was answered. The set is pronouns only: a word like "shed" or "his"
# that is spelt the same with or without an apostrophe is left alone.
shes hes theyre theyve theyll theyd himself herself themselves itself
like just really quite maybe perhaps also still even much many lot lots want needs need get got
make makes okay ok right well yeah one ones youd youre im ive id ill
actually honestly literally basically simply truly
""".split())


ACKS = frozenset("""
ok okay k kk cool nice great good yeah yep yes no nah nope lol haha ha hmm sure right wow oh ah yum
aha eh meh same thanks thx ty cheers ta fine alright aw brilliant perfect awesome interesting
true agreed indeed not much nothing much idk dunno maybe probably sounds sound idea love lovely
definitely exactly fair enough makes sense got it see later
""".split())


GREET = frozenset("hi hello hey hiya morning evening afternoon night bye goodbye".split())


REFERRING = frozenset("""
it its that this these those they them there their one ones he she him her his other same
""".split())


# The words a line uses to ask where to begin in an answer rather than to name a subject: "where
# do i start", "what should i do first", "what next". They are common enough in a record's own
# words that a bare one of them is no evidence the chat went back to that record.
ORDERING = frozenset("""
start starts started starting first next then else begin beginning later more again
""".split())


# A part of the thing in hand points back at it as hard as "it" does: "can i freeze the leftovers"
# after a chicken is about that chicken's leftovers, not about freezing as a subject. Without this
# the question opened a new subject and the chicken's own answer for "is that bad" was lost, while
# "can i keep the leftovers" stayed on the chicken because "keep" is no word the entries fight
# over - the same shape answering two ways. It has to be *the* leftovers and not a leftover word:
# a bare "bones" or "cores" is the subject of somebody's own question ("can i give the bones to
# the dog"), and only a part named as this one's - with a determiner - is a part of the thing in
# hand.
# "what about tea" after a question about water is the same question asked of another thing, not
# a new subject: the answer it wants is the one just given with tea in it ("tea counts towards
# it"). Leaving it as a new topic handed the thread to whatever else the tea line reaches, which
# was a dinner suggestion.
ABOUT_ANOTHER = re.compile(r"\b(?:what|how) about\b")


PART_OF_THE_ONE = re.compile(
    r"\b(?:the|these|those|my|your|its)\s+(?:leftovers?|rest|remainder|extras?|offcuts?|"
    r"trimmings|scraps?|peels?)\b|\bwhat(?:'s| is) left\b")


CONTINUATION_START = frozenset("""
and so but then also what how why when where which who whom whose can could should would will
is are do does did have has was were if
""".split())


# A property question ("how long per kilo?", "what temperature?") can carry one or two content
# words of its own ("per kilo") and still be about the thing the conversation is on.
# The words a property ask uses to name the detail it wants. With these taken out, a line that
# has nothing left is asking that detail of the thing the chat is on ("what temperature" after a
# cake); one with words left is asking about the thing those words name.
MEASURE_WORDS = frozenset("""
long much many far often hot warm temperature temp temps degrees centigrade fahrenheit
time heat size price setting what which
""".split())


# The words a line names a property with, and nothing else: "temp" and "degrees" are as much a
# measure as "temperature" is, and a line that says "what temp" after a sponge is asking about the
# sponge. It was read as a new subject and answered with body temperature, because the list had
# the long word and not the short one people actually type.
PROPERTY = re.compile(r"\bhow (?:long|much|many|far|often|hot|warm)\b|"
                      r"\bwhat (?:temperature|temp|temps|degrees|centigrade|fahrenheit|"
                      r"time|heat|size|price|setting)\b|"
                      r"\bper (?:kilo|kg|500g|person|head|each)\b")


# A line that asks which one of the thing to get leans on the thing just named, whatever else it
# says: "what kind should I get?" after a bike, "what breed?" after a dog, "which one would you
# get?" after a coffee machine. It names no thing of its own, so it is never a new topic.
KIND_ASK = re.compile(r"\b(?:what|which)\s+(?:kind|sort|type|breed|brand|model|make|size|one)\s*\?"
                      r"|\bwhich\s+(?:one|brand|model|make)\b"
                      r"|\bwhat\s+(?:kind|sort|type|breed)\b")


SWITCHERS = ("actually", "never mind", "nevermind", "by the way", "btw", "back to", "anyway",
             "new question", "different question", "forget that", "instead", "changing the subject",
             # The same job said as an apology: "sorry, it's a funeral", "my mistake, it's in
             # august". Whether the subject really changed is still decided by _only_details,
             # so a corrected date keeps the wedding and a corrected occasion does not.
             "sorry", "apologies", "my mistake", "correction", "no wait")


# "ok back to the boiler", "anyway, the laptop", "as i was saying, Rome", "sorry, back to the
# radiator": the line starts with a few chatty words and then names a topic already discussed.
# The line has to start that way, so "we're going back to London tomorrow" stays a statement.
RETURN_LEAD = re.compile(
    r"^(?:(?:ok|okay|so|right|anyway|sorry|and|but|well|oh|then|great|nice|yes|yeah|hmm|aha|ah)"
    r"[\s,]*)*(?:back\s+to|as\s+i\s+was\s+saying|as\s+i\s+said|coming\s+back\s+to|"
    r"where\s+were\s+we(?:\s+on)?|return(?:ing)?\s+to)\b\s*")


# "anyway, the laptop" names the topic again without saying so: a chatty lead-in and then a bare
# noun phrase, no verb. Only with a determiner, so "anyway my mum called" stays a new topic.
CASUAL_LEAD = re.compile(
    r"^(?:(?:ok|okay|so|right|anyway|and|well|oh)\s*[,\s]\s*)*(?:anyway\s*[,\s]\s*)")


CASUAL_OPEN = frozenset("a an the my our your that this those these".split())


CASUAL_VERB = frozenset("""
is are was were am be been being has have had got get gets went go goes called calls said say
says told tell tells keeps keep kept needs need wants want likes like loves love works work
doing does did do can could should would will
""".split())


# "back to work tomorrow" names a time, not a topic: the return has to name a thing, so a verb
# or a day of the week in it means the line is a statement about coming up, not a return.
RETURN_TIME = frozenset("""
tomorrow today tonight now later soon monday tuesday wednesday thursday friday saturday sunday
week weekend month year morning afternoon evening night
""".split())


# A line that asks something after the return marker is a request for an answer, not a bare
# "we were on this": the answer modules handle it with the topic put back in front.
RETURN_ASKS = frozenset("""
what how why when where which who whom whose can could should would will shall is are was were
am do does did have has had if whether
whats hows whys whens wheres whichs whos
""".split())


# Typing drops the apostrophe from "what's" and "how's", so "whats" is how the question word is
# usually written: "back to lisbon, whats good to see" names Lisbon and asks about it, but read as
# a word of its own "whats" was not the question word the split looks for, so the whole clause
# came back as the thing went back to ("lisbon whats good to see", four words, so nothing at all)
# and the line was not read as a return. The answer Lisbon got on turn one then came back word for
# word six turns later instead of being framed as the return it was. The forms are the question
# words a person writes with the apostrophe missing, so a shape learnt here is read everywhere the
# ask words are.
RETURN_ASKS = RETURN_ASKS | frozenset(
    word + "s" for word in ("what", "how", "where", "who", "when", "why", "which"))


def words(text):
    """The words of a line, with the apostrophe forms folded: "what's" -> "what", "you'd" ->
    "youd", so the grammar patterns see the plain word."""
    out = []
    for word in WORD.findall(str(text).lower().replace("’", "'")):
        if word.endswith("'s"):
            word = word[:-2]
        out.append(word.replace("'", ""))
    return [word for word in out if word]


def stem(word):
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("es") and word[-3] in "sxzh":
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def keywords(text):
    """The content words of a line: what it is about, without the grammar."""
    out = []
    for word in words(text):
        if word in STOPWORDS or len(word) < 3 or word.isdigit():
            continue
        key = stem(word)
        if key not in out:
            out.append(key)
    return out


# What a person is not doing, in the words that say so. The word after one of these is the thing
# that is going wrong, not the subject of the line: "my kids wont listen to me" is about the kids
# and the listening is what they will not do, so a bare ask after it ("what can i do") must not be
# widened with "listen" - read with it, the line reaches the music entry and a parent gets albums.
NOT_DOING = re.compile(r"\b(?:wont|won'?t|doesnt|doesn'?t|didnt|didn'?t|cant|can'?t|couldnt|"
                       r"couldn'?t|never|refuses? to|stopped|not)\s+([a-z']+)", re.IGNORECASE)


# A verb ending people put on a word they are talking about. "save" and "saving" are the same
# thing said twice, and so are "train" and "training"; a word family that cannot see that
# misses the recall it should have answered ("what did i say i was saving for?" after
# "im trying to save 3000 for a trip").
ENDINGS = ("ing", "ed")


def forms(word):
    """The word and the forms it takes with a verb ending on or off: {saving, save}.

    "running" drops the doubled letter to find "run", and "saving" puts back the "e" that
    "save" keeps, so both directions find each other. A root shorter than four letters is not
    a form of the word: "caring" is not about a car, "seeing" not about the sea."""
    word = str(word or "")
    out = {word}
    for ending in ENDINGS:
        if len(word) > len(ending) + 2 and word.endswith(ending):
            root = word[:-len(ending)]
            if len(root) >= 4:
                out.add(root)
            out.add(root + "e")
            if len(root) > 3 and root[-1] == root[-2] and root[-1] not in "aeiou":
                out.add(root[:-1])
    return out


def content(text):
    """The words a line is about, with the verb endings taken off and the grammar dropped.

    A recall ask keeps words the statement did not: "what did I say I was *wanted* to..." asks
    with "wanted", which is the grammar word "want" with an ending on it, and "saving" asks
    about the "save" the person actually said. Both are found by looking at the forms of each
    word rather than at the word as typed."""
    out = []
    for word in words(text):
        if len(word) < 3 or word.isdigit():
            continue
        # The word itself is checked before the stem: a grammar word can be shortened into a
        # word that is nobody's grammar word, and then it counts as a thing the line is about.
        # "this" stems to "thi" and "does" to "doe", so "what do you do about this" named a
        # thing of its own ("thi") that no entry is about and the entry reached with the topic
        # was thrown away as not being about the line, which hedged where main answered.
        if word in STOPWORDS:
            continue
        key = stem(word)
        if key in STOPWORDS or forms(key) & STOPWORDS:
            continue
        if key not in out:
            out.append(key)
    return out


def is_ack(text):
    """A short reply that answers the bot's last turn rather than starting a topic."""
    clean = " ".join(words(text))
    if not clean:
        return True
    if clean in ACKS or clean in GREET:
        return True
    parts = clean.split()
    if len(parts) <= 4 and any(w in ACKS or w in GREET for w in parts):
        return all(w in ACKS or w in GREET or w in STOPWORDS or len(w) <= 3 for w in parts)
    return False


def is_small_talk(text, kind=None):
    if kind in ("empty", "greeting", "thanks"):
        return True
    return is_ack(text)


def _a_place_the_line_moves(text):
    """The place a line moves a plan to, asked of the reader that reads the move.

    Imported inside the call rather than at the top: `facts` reads places through this module, so
    asking it at the top would close a circle.
    """
    from . import facts as _facts
    return _facts.a_moved_place(text)


def _asks_about_the_bot(read):
    """True when the understanding engine read the line as a question about the bot itself."""
    return isinstance(read, dict) and bool(read.get("about_bot"))


def _the_record_they_came_back_to(text, memory, record):
    """An earlier record of this chat that the line names, when the one in hand says nothing.

    "my knee hurts when i run" / "how long does chicken keep in the fridge" / "it hurts more in
    the morning": the chat moved to the chicken, and the line that comes back says "it" and
    "hurts". Read against the chicken it is a detail of the chicken, so the bot answered the
    symptom with sympathy and the knee it was about was gone. A record the chat already had, whose
    own words the line carries, is what the line is about.

    Only a word the record already has counts, and only when the record in hand shares none of the
    line's words - a follow-up that fits the thing in hand stays with it.
    """
    found = set(keywords(text))
    if not found or found & set(record.get("words") or ()):
        return None
    if found <= ORDERING:
        # A line that only asks where to begin names the answer in hand, not a subject: "where do
        # i start" and "what should i do first" carry one word each, and that word sits in an
        # earlier record's words for its own reason ("starts school"). Read as a return, the
        # chat went back to the school while the person was asking about the curry, and the
        # school card answered the ask. Only a line whose every word is one of these is left
        # alone, so "when does school start" and "what should i do first about the boiler" are
        # read as before.
        return None
    topics = memory.get("topics")
    if not isinstance(topics, list):
        return None
    for older in reversed(topics[-4:]):
        if older is record or (older.get("text") or "") == (record.get("text") or ""):
            continue
        if found & set(older.get("words") or ()) - set(REFERRING):
            return older
    return None


def _back_to(memory, record, text):
    """Make an earlier record the current one again, with the line's words added to it.

    Not `_resume`: nobody said "back to the knee", so there is no return to greet - the record is
    only what the rest of the bot reads this line against.
    """
    said = dict(record)
    kept = list(record.get("words") or ())
    said["words"] = (kept + [w for w in keywords(text) if w not in kept])[:12]
    memory["topic"] = said
    topics = memory.get("topics")
    if isinstance(topics, list):
        topics[:] = [other for other in topics if other is not record
                     and (other.get("text") or "") != (said.get("text") or "")]
        topics.append(said)
    return said


# An aim said as their own, with the deadline it is said against: "im trying to get fit before the
# holiday", "we're hoping to save 2000 by june". Only the frame people aim in, so a line that
# names a date of its own ("im going to portugal in may") keeps every word it has.
AIM_FRAME = re.compile(r"^\s*(?:(?:so|ok|okay|and|also|well|right|yeah|hi|hello)\b[, ]+)*"
                       r"(?:i'?m|im|i am|we'?re|we are)\s+"
                       r"(?:trying|aiming|hoping|planning|meaning|learning)\b", re.I)


# The deadline is what the aim is measured against, not what it is about.
A_DEADLINE = re.compile(r"\b(?:before|by|until|till|in time for|ready for|ahead of)\b", re.I)


# A question about a *part* of the thing in hand rather than about a thing of its own: "what is
# the food like" after "im going to rome in may", "how is the weather there", "is the beer any
# good". The aspect word is a side of the thing, not a new subject, so the line is about that
# thing still. Kept as a record of its own - text "what is the food like", words ["food"] - the
# place was gone, and the next ask ("what should i book") was read against nothing and shrugged
# at, while the answer two turns back was about Rome all along. Thirteen of mustard-boar's
# sixteen chats kept the subject because the aspect was asked with a pronoun ("what spices go in
# it"); every one that named the aspect instead lost it.
ASPECT_OF_IT = re.compile(
    r"\bwhat(?:'s| is| are| was| were)\s+(?:the\s+|their\s+|its\s+|his\s+|her\s+)?"
    r"[a-z][a-z'-]*(?:\s+[a-z][a-z'-]*){0,2}\s+like\b"
    r"|\bhow(?:'s| is| are| was| were)\s+(?:the\s+|their\s+|its\s+)?"
    r"[a-z][a-z'-]*(?:\s+[a-z][a-z'-]*){0,2}\s*$"
    r"|\bis\s+the\s+[a-z][a-z'-]*(?:\s+[a-z][a-z'-]*){0,2}\s+"
    r"(?:any\s+good|good|worth\s+it|worth\s+doing|ok|okay|decent|safe|expensive|cheap|nice)\b",
    re.I)


# A pronoun is not a side of the thing: "how are you" matched the shape of "how is the weather"
# and would have folded the whole conversation into the line, and "how is your back" is a body of
# its own rather than a side of the last thing said.
ASPECT_IS_A_PRONOUN = frozenset("""
    you me him her them us i we they he she your my our mine yours
""".split())


# A thing of the line's own, said with the possessives and the definite article: "my budget is 600
# pounds", "the oven is a fan one". "a" and "an" are left out - a detail often names one of the
# thing's parts - and so is a person ("my daughter is a vegetarian" is still about the meal).
OWN_THING = re.compile(r"\b(?:my|our|your|his|her|their|the)\s+([a-z]+)")


def _names_a_place_of_its_own(text, record, memory=None):
    """True when the line says where they are, about a place the chat is not already on.

    "how do i get rid of ants" / "i live in bristol" was kept as a detail of the ants question,
    so the knowledge base put the ants back into the line ("i live in bristol ant"), reached the
    ant entry and answered an ant's lifespan instead of the news about Bristol - and the eight
    lines people write after an answer (a place, a job, a swim on Tuesdays) were answered about
    the subject before them. The reading knows the line named a place of its own, and a place the
    chat is not on is a thing the next line can lean on ("what's it like there?", "is it
    expensive?"), which is what a topic is for. Only a place the reading itself found counts,
    never a word of the line at large, and never the question the chat is on: "which airport do
    i fly to in rome" is about the trip, not about a new place.
    """
    read = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(read, dict) or read.get("kind") == "question":
        return False
    known = set(record.get("words") or [])
    said = set(words(record.get("text") or ""))
    for found in read.get("entities") or ():
        if not isinstance(found, dict) or found.get("type") != "place":
            continue
        name = str(found.get("text") or "").strip().lower()
        if not name:
            continue
        if any(stem(part) in known for part in name.split()):
            continue
        if any(part in said for part in name.split()):
            continue
        return True
    return False


# A person who is part of the thing the chat is on, rather than a subject of their own: the
# companion joins the thing ("coming", "too", "with me") or is the person the thing is for, and
# the interest is said of them ("loves", "is into", "plays", "collects").
JOINS_THE_THING = re.compile(
    r"\b(?:too|as well|along|coming|comes|with (?:me|us))\b")


ABOUT_THE_PERSON = re.compile(
    r"\b(?:loves?|loved|likes?|liked|adores?|prefers?|collects?|plays?|wants?|enjoys?|hates?|"
    r"into|is (?:mad|crazy|obsessed) about|is a fan of|fans? of|is afraid of)\b")


PRONOUN_PERSON = re.compile(r"\b(?:he|she|they|him|her|them)\b")


# A question of how many, how much or how long is read as a sum whatever it is about, so its area
# says nothing about which subject it belongs to.
MEASURE = frozenset({"maths-and-numbers"})


def _a_part_of_the_record(read, record):
    """True when the reading says this line hangs off the record the chat is already on.

    "and the food" after a trip names a subject of its own - it reaches the food entry, so
    `_names_another_subject` reads it as a new thing and the trip stops being the chat's subject.
    But it is a part of the trip: the understanding engine walks back over a part line and reads
    the line after it against the trip, so the trip is what the next ask is answered from. Kept
    as the food's record instead, "and how do i get around" was widened with the food's words,
    the city was gone, and the entry that fit was the food card the person had just read.
    """
    if not isinstance(read, dict) or not isinstance(record, dict):
        return False
    leaned = " ".join(words((read.get("leans_on") or {}).get("text") or ""))
    return bool(leaned) and leaned == " ".join(words(record.get("text") or ""))


def _switches(text):
    """True when the line turns to a different subject ("actually it's a funeral").

    "I'm going to a wedding and need a suit" then "actually it's a funeral" then "what should I
    wear to that?" is not a follow-up on the wedding: the correction replaced the subject, so the
    record has to be started again from the corrected line. A word like "actually" or "instead"
    is the person saying the subject changed, and is_follow_up() already refuses these lines; the
    reading in memory["understood"] does not see it, which is what this guards.
    """
    low = " ".join(words(text))
    return any(low.startswith(s) or (" " + s + " ") in (" " + low + " ") for s in SWITCHERS)


# The chatty words a line opens with before it gets to the point: "ok so actually it's a funeral".
# They say nothing, so the switch is read after them.
_LEADS_IN = re.compile(r"^(?:(?:ok|okay|k|kk|so|well|oh|ah|and|but|um+|uh+|er+|hmm+|right|yeah|yep|"
                       r"also|plus|now)[\s,.!-]+)*", re.I)


# The courtesy and the pointing that come with a correction: "actually it's in august, sorry".
CORRECTION_NOISE = frozenset("""sorry apologies apology correction correcting wrong mistake
mean meant rather wait oh""".split())


# What a line can change without changing what the conversation is about: a when, a where, how
# many or how much. "actually it's in august" is the same wedding with a new date; "actually
# it's a funeral" is a different occasion. Numbers are already dropped by keywords().
DETAIL_WORDS = frozenset("""
january february march april may june july august september october november december
jan feb mar apr jun jul aug sep sept oct nov dec
monday tuesday wednesday thursday friday saturday sunday weekend weekday
morning afternoon evening night tonight today tomorrow yesterday day days week weeks
month months year years hour hours minute minutes oclock am pm
people person persons guest guests adult adults child children kid kids
pound pounds quid euro euros dollar dollars pence penny
kilo kilos kg gram grams litre litres liter liters pint pints cup cups tablespoon tablespoons
half quarter dozen
""".split())


# A plan to get one thing, said before the thing turns out to be another: "im thinking of getting a
# rescue greyhound" then "actually its a whippet" is the same plan with a different animal in it,
# not a new subject. A correction that only names the thing is read as a new subject on its own
# (`_switches`), which threw the plan away: the chat had nothing on record but the word "whippet",
# so the next line, "how much exercise does it need", named nothing of its own, found nothing to
# lean on, and was answered "I don't know enough to answer that honestly" - the reading was right
# and the record had forgotten the dog.
A_THING_ON_ITS_WAY = re.compile(
    r"\b(?:thinking\s+(?:of|about)|planning\s+(?:on|to)|hoping\s+to|considering|going\s+to|"
    r"about\s+to|thinking\s+we\s+might|might|may|could)\s+"
    r"(?:get|getting|have|having|adopt|adopting|buy|buying|rescue|rescuing|rehome|rehoming|"
    r"look\s+at|look\s+for|find|finding|pick|picking\s+up|collect|collecting|bring\s+home)\b"
    r"|\b(?:looking\s+(?:at|for)|shopping\s+for|on\s+the\s+lookout\s+for)\s+(?:a|an|another)\b"
    r"|\b(?:getting|adopting|rescuing|rehoming|wanting|want|wanted)\s+(?:a|an|another|one)\b", re.I)


# The correction itself: the line says what the thing is and nothing else. "actually its a
# funeral" after "im getting a rescue greyhound" is nonsense, so the plan has to be the thing the
# correction is about, and the words carry nothing else with them.
NAMES_THE_THING = re.compile(
    r"^\W*(?:(?:ok|okay|so|well|oh|ah|no|nope|sorry|actually|wait|hmm|erm?|um)\b[\s,.!-]*)*"
    r"(?:its|it'?s|it\s+is|that'?s|that\s+is|i\s+mean|i\s+meant|make\s+that)\s+"
    r"(?:an?\s+|the\s+|just\s+|only\s+|really\s+)?[a-z][a-z' -]{2,30}"
    # The courtesy that comes after the correction: "actually its a whippet, sorry" is the same
    # line, and read as one word more than a bare name it was a dog of theirs again.
    r"(?:\s*[,.!-]*\s*(?:sorry|apologies|thanks|thank\s+you|actually|though|then|i\s+think|hmm))*$",
    re.I)


FRESH_NAMES = 3      # a name brings at most this many words the plan has not got


# "my car is a 2015 fiesta" names a new thing however many numbers it has; "its about 6 hours" does not.
MY_THING_IS = re.compile(r"^\W*(?:my|our|the)\s+([a-z]+)\s+(?:is|are|was|were)\b")


SHORTHAND = re.compile(r"^\d+(?:\.\d+)?\s*[km]$|^\d+(?:\.\d+)?\s*(?:k|m)\b")


RECENT_TURNS = 3     # a detail belongs to the subject of the last few turns, not an old one


FRESH_WORDS = 2      # a detail brings at most this many words the subject has not got


# A line that only says when it started or how often, with no thing of its own: "since i moved
# here" after feeling lonely at weekends, "i drink about 3 coffees" after the headaches. It names
# nothing ("my", "a", "the" before a noun would be a thing), it reaches no entry, and it carries
# a when or an amount, so it is a fact about what the chat is on rather than a new subject.
#
# It has to stay a fact and not become the topic: the next short ask ("how do i meet people",
# "could it be that") is read against the topic, and a topic that is only a timeframe has nothing
# to read it against, so the turn ended in the search hedge two turns after the answer existed.
WHEN_OR_AMOUNT = re.compile(
    r"\b(?:since|for|about|around|started|began|start|most|every|each|last|this|next|"
    r"a day|a week|a month|a year|once|twice|times)\b|\b\d+\b")


# A thing of their own in the line: a determiner in front of a word. The line is then about that
# thing ("my car is a 2015 fiesta", "i started a new job last week") and starts its own topic.
NAMED_THING = re.compile(r"\b(?:my|our|your|his|her|their|the|a|an|some|any)\s+[a-z]")


# The words a line can name that are a fact about the thing in hand rather than a thing to move
# to: what it may cost, how old it is, how much time there is for it. A constraint said as a
# number ("my budget is 5k" after "im buying a used car") names a word the subject does not have,
# so the budget became the topic and the next short ask - "what should i check" - was read against
# a household budget and answered "write down what comes in each month". The person is still
# buying a car, and the budget is a fact about the car.
CONSTRAINT_IS = re.compile(
    r"^(?:my|our|the)\s+(?:budget|price|cost|age|salary|wage|wages|income|savings|time|"
    r"spending|tariff|allowance)\s+(?:is|was|'s)\b")


# The same fact said as a way of travelling rather than as a thing that is a figure: "we're on a
# budget, about 300 each" after "im going to edinburgh in march" is about the trip, and a follow-up
# with no noun of its own ("what should we see", "any good pubs") was read against the budget line
# and answered "write down what comes in each month" twice, the second time word for word.
ON_A_BUDGET = re.compile(
    r"^(?:we|i|were|im)(?:\s+(?:are|am|was))?\s+(?:on|under|within|keeping to|sticking to|"
    r"trying to keep to)\s+(?:a|the|our|my|tight|small|strict)?\s*budget\b")


# --- who the turn is about ---------------------------------------------------
# A conversation is full of lines about somebody else: "my mum moved in with us last month",
# then "she keeps forgetting where things are in the kitchen". The second line names nobody, and
# reading it as a follow-up on the *thing* of the first line is how a person worried about their
# mother's memory was handed a packing plan. So the store keeps the person the chat is about, and
# the modules that answer read it: `memory["person"] = {"who": "mum", "said": <their line>,
# "turn": 3}`.
WHO = frozenset("""
mum mom mam mummy mumma mother dad daddy father papa son daughter child kid baby toddler
partner husband wife spouse boyfriend girlfriend fiance fiancee sister brother sibling stepsister
stepbrother stepson stepdaughter nan nana gran granny grandma grandmother grandad grandpa
granddad grandfather grandparents grandparent aunt auntie uncle cousin nephew niece friend
flatmate housemate neighbour neighbor landlord landlady lodger manager
tutor childminder carer hairdresser barber instructor
""".split())


# "my mum", "our dad": the person the speaker names as their own. His, her and their are kept
# apart because "she keeps asking for her mum" names a *third* person - the one the person the
# chat is about is asking for - and the chat is still about her, not about her mother. Reading
# them as the person this speaker owns put the wrong name in the reply ("How long has that been
# going on with your mum?" to a line about a wife).
# The possessive is written without its apostrophe more often than with it - "my mums been in
# hospital a week", "my dads getting forgetful", "my sons at uni" - and a name with an `s` on the
# end is the same person as the name. Reading only the bare name left those lines naming nobody:
# "my mums been in hospital a week" fell back to whoever the chat was last about, and in a
# conversation that had opened on `my son is 16 and wants a motorbike` the ward answer said "That
# is a worrying place for your son to be" about the mother (quality watch, main d070657077b8).
# The `s` is read as part of the possessive rather than as a missing word, so "my mums" and
# "my mum's" are one reading, and "my mums been" answers about the mum.
WHO_SAID = re.compile(r"\b(?:my|our)\s+(" + "|".join(sorted(WHO, key=len,
                                                             reverse=True)) + r")(?:'s|s)?\b")


# The same names after his, her or their, which only count when the chat is not already about
# someone: "she keeps asking for her mum" on its own still says who is being asked for.
WHO_SAID_THIRD = re.compile(r"\b(?:his|her|their)\s+(" + "|".join(sorted(WHO, key=len,
                                                                         reverse=True))
                            + r")(?:'s|s)?\b")


# A line that opens with a bare pronoun is about the person the chat is already on, and a name
# that comes later in such a line can be what that person is asking about rather than a new
# subject. "my grandad has dementia" / "he keeps asking where my nan is" is the grandad asking
# after his wife: read as a new subject, the store moved the chat onto the nan, and the next
# short ask ("what do i say") was answered "a word with your nan's GP" about a woman nobody had
# said was ill. Only an indirect question moves the name off the subject this way - "he said my
# mum is ill" does report something about the mum, so it still names her.
A_BARE_PRONOUN_SUBJECT = re.compile(
    r"\A(?:and|but|so|then|now|also|still)?\s*(?:he|she|they|hes|shes|theyre)(?:'s|'re)?\b")


A_QUESTION_THEY_ASK = re.compile(
    r"\b(?:asks?|asked|asking|keeps? asking|kept asking|wonders?|wondered|wondering|"
    r"wants? to know|wanted to know|says?|said|tells?|told|thinks?|thought|forgets?|forgot|"
    r"remembers?|remembered)\b[^.?!]*?\b(?:where|what|when|why|how|who|if|whether)\b")


def about(memory):
    """The person the chat is about, as a record, or None."""
    record = memory.get("person") if isinstance(memory, dict) else None
    return record if isinstance(record, dict) and record.get("who") else None


# The kinds of trouble a line reports about a person the user looks after, most specific first.
# This is a reading of the line, so it lives in the store rather than in the module that words the
# reply: which trouble the chat is on outlives one turn, and the reply that turn gets may come from
# another lane entirely ("she keeps forgetting where things are in the kitchen" is answered by a
# knowledge entry about forgetting). chat._about_someone words each kind; nothing here decides one.
PERSON_TROUBLE = (
    # A ward they have left is good news, and the reply a friend gives is not the ward's: "my mum
    # is out of hospital" was answered "That is a worrying place for your mum to be" about a woman
    # who had just come home, and "mum was discharged from hospital today" with "Noted: ...".
    # Read first, so the hospital pattern below only keeps the wards people are still on.
    ("homeward", re.compile(
        r"\b(?:out of|home from|back from|discharged from|released from|let out of|"
        r"came out of|come out of|got out of|getting out of)\s+(?:the\s+)?hospital\b")),
    # A person who is in hospital now is not waiting for a first appointment. The words people
    # use for an admission - "went into hospital this morning", "was taken in last night",
    # "admitted on Tuesday", "kept in overnight", "she is on the ward" - are not the "in hospital"
    # of the kind below, so the line fell through to "ill", which matches the word "hospital" in
    # it, and chat answered "Worth a GP appointment for your son this week rather than next month"
    # about a boy who was already on a ward (hearty-emu, #routing 81405). A serious diagnosis is
    # the same news: "my husband has been diagnosed with a brain tumour" is not a change to raise
    # at the next appointment, because there has been no next appointment yet.
    ("hospital", re.compile(
        r"\b(?:admitted|taken|took|rushed|whisked|brought|moved|transferred)\s+"
        r"(?:in|into|to|back to)\s+(?:the\s+)?(?:hospital|ward|icu|itu|a&e|a and e|resus)\b|"
        r"\b(?:went|gone|been|is|are|was|were|kept|staying|stuck)\s+(?:in|into|back in|"
        r"back into)\s+(?:the\s+)?hospital\b|"
        # "went to the hospital" is the same news when it is the person who is ill, and a visit
        # when it is not: "my mum went to the hospital to visit her sister" keeps its own answer.
        r"\bwent (?:in)?to (?:the )?hospital\b"
        r"(?![^.?!]{0,18}\b(?:visit|see|collect|pick|drop|meet)\b)|"
        r"(?<!work )(?<!works )(?:on|in)\s+the\s+(?:ward|stroke unit|coronary care)\b|"
        r"\bkept in (?:overnight|in|for observation|for tests)\b|"
        r"\b(?:in|into) (?:intensive care|icu|itu|resus)\b|"
        r"\bdiagnosed (?:with|as having)\s+(?:cancer|a (?:brain |lung |bowel |breast |bone )?"
        r"tumou?r|leukaemia|leukemia|lymphoma|motor neurone|parkinsons?|a terminal|"
        r"something serious)\b")),
    # Being in hospital already means the care is happening: the question is how they are, not
    # another appointment.
    ("hospital", re.compile(
        r"\b(?:in|at|on|still in) (?:the )?hospital\b|\bhad an operation\b|\boperation\b|"
        r"\bsurgery\b|\bbeing (?:seen|treated|looked after)\b")),
    # Something already known and being looked after: the reply is about this change, not about
    # getting the first appointment.
    ("known", re.compile(
        r"\b(?:diagnosed|diagnosis|has dementia|has alzheimers|already (?:has|had|sees)|"
        r"since the diagnosis|under the (?:doctor|hospital|memory clinic))\b")),
    # A home with staff in it is neither hospital nor a first appointment: what they notice day to
    # day is the record a GP works from.
    ("care", re.compile(
        r"\b(?:care home|nursing home|residential home|in a home now|a home now)\b")),
    ("memory", re.compile(
        r"\b(?:forget(?:s|ting|ful)?|forgot|memory|remember(?:ing)? (?:things|where|names)|"
        r"confus(?:ed|ing)|muddled|dementia|alzheimers?|wandering|getting lost|"
        # "he got lost coming back from his walk last week" was left to the knowledge base and
        # answered "I'm sorry - that's frustrating": the past tense and the other ways people
        # say it are the same kind as "getting lost", and the kind decides the reply.
        r"gets? lost|got lost|went missing|lost (?:her|his|their) way|"
        r"wander(?:s|ed|ing)? off|took a wrong turn|losing track|"
        r"repeat(?:s|ing)? (?:himself|herself|themselves|the same "
        r"(?:thing|story|tale|question))|"
        # "my dad keeps saying the same story" is how families describe the repetition before
        # anyone says the word "memory": with only "the same thing" here, the line was read as
        # no trouble at all, so the short ask after it ("is that a sign of anything") borrowed
        # the word "story" from the chat and got a story about the word "anything".
        r"say(?:s|ing)? (?:me |us )?the same (?:thing|story|tale|question)|"
        r"tel(?:l|ls|ling) (?:me |us )?the same (?:thing|story|tale)|"
        r"ask(?:s|ing)? the same question|"
        # The examples people give instead of the word "memory": a wrong name for a thing, a
        # brother's name for their own son, the same story twice.
        r"wrong (?:name|word|words|thing)|call(?:s|ed)? (?:me|him|her|us|them) "
        # a relative who rings too much is not a wrong name: "my daughter calls me every
        # night" was getting "take a note of what you have noticed to the GP"
        r"(?!(?:all|every|each|when|if|about|back|later|again|whenever|once|twice|from|at|"
        r"in|on|to|for|with|so|yesterday|today|tomorrow|constantly|loads|lots|more|less|too|"
        r"up|out|off|over|and|or|but|urgent)\b)\w+|mixed up|"
        r"says? the same thing|told me the same|the wrong day)\b")),
    ("falls", re.compile(
        r"\b(?:fell|fallen|fall|falls|falling|tripped|tripping|trip|unsteady|wobbly on "
        r"(?:his|her|their) feet|balance)\b")),
    # "low" is not the word on its own: low on money, low pay, low iron and low blood pressure are
    # about something else, so the mood word needs to be about them or about their spirits.
    ("low", re.compile(
        r"\b(?:low mood|low spirits|feeling low|seems? low|so low|very low|a bit low|"
        r"won'?t go out|wont go out|not eating|off (?:his|her|their) food|not themselves|"
        r"no appetite)\b")),
    # Sleep is how a body reports itself, and the low-mood answers are about a person going quiet
    # and off their life: "my baby is not sleeping" then "is that normal" was answered "Months of
    # it, or losing interest in everything, deserves an appointment", which is a withdrawal from
    # life and not a baby's night. It is read after "low", because a line that has both in it
    # ("not eating and not sleeping") is the withdrawal sentence, and going off food is often the
    # first thing a family notices about someone's spirits.
    ("sleep", re.compile(
        r"\b(?:not sleeping|not sleeping through|sleeping badly|not sleeping well|"
        r"up all night|awake all night|waking (?:up )?(?:all|every) night|not sleeping at night)"
        r"\b")),
    ("ill", re.compile(
        r"\b(?:poorly|unwell|chest infection|"
        # "keeps getting" is the everyday way to say a thing goes on, and most of what follows it
        # is ordinary: a child keeps getting out of bed, a dog keeps getting on the sofa, someone
        # keeps getting distracted. What makes it an illness is the thing they keep getting, so
        # the verb asks for one of those and nothing else: "keeps getting chest infections" is a
        # report for the GP, "he keeps getting out of bed" is the night-time routine.
        r"keeps (?:getting|having) (?:a |an |the )?(?:\w+ ){0,2}"
        r"(?:infections?|colds?|coughs?|cough|temperatures?|chest|bugs?|viruses?|virus|"
        r"migraines?|headaches?|nosebleeds?|faints?|blackouts?|tremors?|shakes?|"
        r"dizzy|dizziness|breathless|sick|unwell|worse|pain|pains|swollen)|getting worse|"
        r"got worse|in pain|aches?|aching|breathless|swollen|dizzy|dizziness|"
        r"doctor said|hospital|diagnosed)\b")),
)


# A child who bounces back up has not had the kind of fall the falls answer is about, and a
# diagnosis is not a change: "my grandma has dementia" is not news for the GP today, and the
# "make this change the GP's problem" answer would invent the change.
YOUNG_PERSON = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|[1-9]|1[0-2])\s*"
    r"(?:months?|years?)?\s*old\b|\bis (?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve)\b|\b(?:baby|toddler|newborn|little one|little boy|little girl|"
    r"schoolboy|schoolgirl|reception class)\b")


# A row with someone is not a fall, and this is where the reading decides it for every lane:
# "me and my mum fell out" and "my dad and i fell out last week" were read as the falls trouble -
# chat answered "Falls are rarely just age ... a GP can start on all three" and the knowledge base
# gave the falls review, with a falls clinic for someone who had said no more than that they had
# argued. Falling out *of* something is a fall ("my mum fell out of bed"), so the phrase is the
# fence, not the word "out".
FELL_OUT = re.compile(r"\bf(?:ell|all|alls|alling|allen)\s+out\b(?!\s+of\b)|\bfell\s+about\b")


FALLS_FINE = re.compile(
    r"\b(?:laughed|laughed it off|no harm|wasn'?t hurt|was not hurt|unhurt|not a scratch|"
    r"slept it off|got straight (?:back )?up|jumped (?:straight )?up|ran off|carried on|"
    r"waved it off|no damage)\b|"
    r"\b(?:he|she|they|it|hes|shes|theyre)(?:'s|'re)?\s+(?:is |was |seems |looks )?"
    r"(?:fine|ok|okay|alright)\b")


# A job is not an illness. The words for a ward are the same words for a workplace - "my mum
# works at the hospital", "he works on the ward", "she is a nurse at the clinic" - and the ward
# pool answered a job with "Sorry to hear that. How is your dad doing?", which is a reply to bad
# news about somebody's health. What tells them apart is not the place but the verb of work in
# front of it, so the place is read with that verb and the kinds that own a ward stand down. The
# ward pattern above already guards the two forms it can ("work on the ward"), with a lookbehind;
# this is the same reading for the rest, in the one place every kind passes through.
A_JOB_AT = re.compile(
    r"\b(?:works?|working|worked|starts?|started|starting|got a job|gets a job|getting a job|"
    r"hired|employed|shifts?|night shift|day shift|late shift|early shift|job|jobs|career|"
    r"boss|colleague|colleagues|manager|salary|wages|pay|overtime|contract)\b"
    r"[^.!?]{0,40}?\b(?:at|in|on|for|as)\b[^.!?]{0,14}?\b(?:the\s+)?(?:hospital|ward|unit|"
    r"icu|itu|a&e|a and e|care home|nursing home|hospice|clinic|surgery|pharmacy|practice)\b|"
    r"\b(?:my|his|her|their|our)\s+(?:new\s+)?(?:job|work|shift)\b|"
    r"\b(?:works?|working|worked)\s+(?:there|here|nights|days|shifts|full time|part time)\b")


# What a line has to hold besides the job for it to be about somebody's health: a symptom, a
# change, or a worry in their own words. Closed on purpose - a job line that carries none of these
# is only news about work.
SOMETHING_WRONG = re.compile(
    r"\b(?:ill|unwell|poorly|sick|sickness|pain|painful|hurts?|hurting|aching|aches|worse|worst|"
    r"fell|fallen|falling|fainted|collapsed|diagnosed|diagnosis|dementia|alzheimers|cancer|"
    r"operation|surgery|admitted|in hospital|on the ward|intensive care|icu|a&e|"
    r"cant|cannot|can'?t|unable|stopped|keeps|kept|forgetting|forgetful|confused|"
    r"confusion|weak|weaker|breathless|bleeding|infection|temperature|"
    r"tests?|results?|scan|appointment|worried|worrying|worry|decline|declining|"
    r"not (?:been )?(?:himself|herself|themselves)|unsteady|dizzy)\b")


CHANGE = re.compile(
    r"\b(?:new|newly|worse|worsening|suddenly|all of a sudden|since|these days|lately|recently|"
    r"stopped|no longer|used to|gone downhill|going downhill|declin(?:e|ed|ing)|"
    r"getting (?:worse|more|confused|forgetful)|"
    r"(?:this|last) (?:week|month|couple of|few)|over the (?:last|past))\b")


# The turn of phrase that puts the worry after the news: "out of hospital but still very weak".
# The recovery is real, and it is not what the person is asking about.
A_WORRY_AFTER = re.compile(
    r"\b(?:but|however|though|except)\b|\bstill\s+(?:very\s+|quite\s+|really\s+)?"
    r"(?:weak|poorly|unwell|bad|badly|tired|no better|not himself|not herself|not themselves)\b")


# A child asking for the same story again is not a memory sign. The repetition reading is
# fenced for the person words that are usually a child, unless an age in the line says otherwise:
# "my son is 40 and says the same story" is still read, "my four year old says the same story"
# is not.
A_CHILDS_PERSON = re.compile(
    r"\b(?:son|daughter|kid|kids|child|children|little one|little boy|little girl|baby|"
    r"toddler|newborn|schoolboy|schoolgirl)\b|"
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|"
    r"fourteen|fifteen|sixteen|seventeen|\d{1,2})[\s-]*(?:year|yr)s?[\s-]*old\b")


A_GROWN_AGE = re.compile(r"\b(?:1[89]|[2-9]\d)\b|\b(?:eighteen|nineteen|twenty|thirty|"
                         r"forty|fifty|sixty|seventy|eighty|ninety)\b")


REPEATED_SAID = re.compile(
    r"\brepeat(?:s|ing)? the same (?:story|tale|question)|"
    r"\bsay(?:s|ing)? (?:me |us )?the same (?:thing|story|tale|question)|"
    r"\btel(?:l|ls|ling) (?:me |us )?the same (?:thing|story|tale)|"
    r"\bask(?:s|ing)? the same question\b")


def _after_an_emergency(memory):
    """True when the bot's last answer was an emergency, so nothing here is a topic to lean on.

    "my neighbour's flat is on fire" then "is it safe to go down the stairs?" is a follow-up,
    but the fire is not a subject to keep answering from: the kept words ("fire", "smoke")
    reach a knowledge entry about clearing cooking smells, and that entry then takes the turn
    from the careful continuation. Mid-emergency the topic starts again from the line itself,
    and bot/compose/fallback.EMERGENCY_AFTER holds the thread.
    """
    turns = memory.get("turns")
    if isinstance(turns, list) and turns and isinstance(turns[-1], dict):
        return turns[-1].get("module") == "safety"
    return False


# The shapes a line takes when it replaces something said before it: "sorry, it's a 10k, not a
# half", "no, Bristol not Leeds", "i meant jen", "make that july". Only the previous line is read
# this way, and only to stop a carry, so the pattern is allowed to be generous.
CORRECTION_LINE = re.compile(
    r"^[\W]*(?:oh|sorry|no|nope|actually|oops|wait|hang on)\b[^!?]{0,60}\bnot\b|"
    r"\b(?:i\s+meant|i\s+mean|make\s+that)\b|\bnot\s+(?:a|an|the)\s+[a-z]", re.I)


# The modules whose answers are the safety thread going on rather than a move away from it.
INSIDE_A_SAFETY_THREAD = ("carers_turn", "safety_cards")


def in_a_safety_thread(memory):
    """True while the bot's last real answer was an emergency and nothing has answered since.

    A number said out loud mid-emergency is not a savings plan: someone who has just been told
    to ring 999 and then says "i can put away 250 a month" has not changed the subject, and an
    arithmetic answer would take the turn from the careful continuation that thread needs. Any
    module that answers from memory rather than the line itself asks this first.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    for turn in reversed([t for t in turns if isinstance(t, dict)][-3:]):
        module = turn.get("module")
        if module == "safety":
            return True
        if module in INSIDE_A_SAFETY_THREAD or module in ("greeting", None):
            # An answer inside the thread is the thread going on, not the subject changing:
            # `carers_turn` answers the turns after the card in the words for the person it is
            # about ("The drink is the part that makes the rest of it more likely"), names no
            # number, and keeps no three words of the card - so the thread was read as over two
            # turns in, and the amends question after it was handed to the chat's own pool while
            # `carers_turn` had the answer beside it (mint-brick, #13830).
            continue
        return False
    return False


# The question words people type without the apostrophe: "whats good to see", "hows the boiler
# been". `words` folds "what's" to "what" but leaves "whats" as one word, so a return line split at
# its ask word did not split, and "back to lisbon, whats good to see" named the whole clause
# ("lisbon whats good to see", five words) and so named nothing: the return was never marked, the
# guide came back word for word five turns later, and `tests.test_long`'s repeat rule failed on
# main. Only the wh-words: "its" is a possessive as often as it is "it is".
WH_WORD_WITHOUT_ITS_APOSTROPHE = re.compile(r"\b(what|how|when|where|why|who|which)s\b")


# A helper right after the thing opens a question about it ("back to the laptop, is it worth
# servicing?", "the boiler, does that include the service?"). A helper followed by a participle or
# an adverb is the line's own verb instead: "anyway my knee has been clicking up the stairs" was
# cut at "has" and read as going back to "my knee", so the line opened no new topic and the next
# "is that bad" was answered about the flat from two turns before.
HELPER_ASKS = frozenset("""
is are was were am do does did have has had can could should would will shall if whether
""".split())


# A participle says the thing is doing something, and the ending alone cannot tell "clicking"
# from "everything": "back to the laptop, is everything ok?" names the laptop, and reading
# "everything" as the line's verb threw that question away. The words that say something is
# happening are listed instead, so a word that only ends the same way stays part of the question.
ING_VERBS = frozenset("""
aching acting adding asking baking beating becoming beginning biting bleeding boiling breaking
breathing bringing building burning buying calling carrying catching changing clicking climbing
closing coming cooking costing coughing counting crying cutting dancing dealing deciding digging
doing drawing dreaming dressing driving dropping drying eating expecting failing falling feeding
feeling filling finding finishing fitting flying following forgetting getting giving going growing
happening hating having hearing helping hiding hitting holding hoping hurting itching jumping
keeping kicking knocking landing laughing leaking leaning learning leaving lifting listening
living looking losing making meaning meeting missing moving needing opening paying picking playing
pointing pressing pulling pushing putting raining reaching reading relaxing remembering riding
ringing rising running saying seeing selling sending shaking showing singing sitting sleeping
sliding smelling smiling sneezing speaking spending spilling standing starting staying stealing
sticking stopping struggling studying swimming taking talking tasting teaching telling thinking
throwing ticking tightening trying turning waking walking wanting washing watching wearing
weighing winning wondering working worrying writing
""".split())


VERB_PHRASE_AFTER = frozenset("""
been being had got gotten not no never still always just already also now going getting doing
making taking coming putting seeing saying starting trying
""".split())


# A modal is followed by a bare infinitive and never by a participle: "would asking why hurt my
# chances" is a question of its own, and cannot be the thing doing something. "back to the
# promotion, would asking why hurt my chances" was read as "the promotion would asking" - the
# line went back to nothing, so the answer from three turns before came back word for word with
# no lead-in. The other helpers ("is", "has", "was") carry the name's own doing, as in "anyway my
# knee is clicking" / "my knee has been clicking", and those still do.
MODALS = frozenset("would could should can will shall may might must ought".split())


def the_thing_asked_again(memory, text=""):
    """The line a person went back to, with the ask they made on it, or "".

    "back to lisbon, what should i see" is one breath: the return and the question about the
    thing returned to. The line as typed is read for its own words, and "back" is a body part,
    so the back-pain card answered a question about Lisbon. The store has already put the thing
    back on the table (`_resume`), so the ask is read with that thing in front of it - "lisbon
    what should i see" - which is the line the card for it is keyed on. Only a return the store
    marked as carrying an ask, and only when the thing is named in the line, so a return that
    asks nothing ("back to the boiler") is still the store's greeting.
    """
    record = resumed(memory)
    if not isinstance(record, dict) or not record.get("asks"):
        return ""
    thing = " ".join(str(record.get("asked") or "").lower().split())
    line = " ".join(str(text or "").lower().split())
    if not thing or not line:
        return ""
    at = line.find(thing)
    if at < 0:
        return ""
    tail = line[at + len(thing):].strip(" ,;:.-")
    if not tail:
        return ""
    return thing + " " + tail


def the_thing_went_back_to(memory):
    """The thing named after a return opener ("the boiler" out of "coming back to the boiler")."""
    record = resumed(memory)
    if not isinstance(record, dict) or not record.get("asks"):
        return ""
    return " ".join(str(record.get("asked") or "").lower().split())


def _the_answer_on_the_return(memory, said):
    """Put the answer that belongs to the topic gone back to on top of the kept answers.

    The kept answers are what a follow-up that names nothing of its own is answered from ("what
    should i do first", "how long does that take"), and the newest of them is normally the right
    one because the newest answer is about what the chat is on. Going back to an earlier topic is
    the one case where that is false, and the store already knows it: it makes the returned topic
    current. Without this, the answer to the topic they went back to sat behind the answer to the
    subject in between:

        my boiler keeps losing pressure
        my daughter is 6 and starts school in september
        anyway back to the boiler   -> "Back to the boiler, then. What did you want to know about
                                        it?"
        what should i do first      -> "Apply through your council by 15 January ..."  (school)

    So the answer whose key words are the returned topic's is moved to the end of the list, which
    is all the follow-up readers need to draw on it. It stays in the same list, so a reader that
    checks the answer was really given (`newest_answer`) still checks it, and an answer about
    nothing the topic names leaves the list alone.
    """
    kept = memory.get("entry_answers")
    if not isinstance(kept, list) or len(kept) < 2:
        return
    wanted = {form for word in keywords(said.get("text") or "") for form in (word, stem(word))}
    wanted -= STOPWORDS
    if not wanted:
        return
    best, best_score = None, 0
    for record in kept:
        if not isinstance(record, dict):
            continue
        forms = {form for key in set(record.get("keys") or ()) for form in (key, stem(key))}
        score = len(wanted & (forms - STOPWORDS))
        if score > best_score:
            best, best_score = record, score
    if not best or best is kept[-1]:
        return
    kept.remove(best)
    kept.append(best)
    memory["entry_answer"] = best


def resumed(memory):
    """The earlier topic the user went back to on this turn, or None.

    Set by note(); the turn is the number of turns when the line was read, so an answer module
    knows the return happened just now and not three turns ago.
    """
    record = memory.get("returned")
    if not isinstance(record, dict) or not record.get("text"):
        return None
    if record.get("turn") != len(memory.get("turns") or []):
        return None
    return record


def current(memory):
    """The current topic record, or None."""
    record = memory.get("topic")
    if isinstance(record, dict) and record.get("text"):
        return record
    return None


def _forms(word):
    """The word and the verb it may be built from: "saving" -> "saving", "sav", "save"."""
    forms = [word]
    if len(word) > 5 and word.endswith("ing"):
        base = word[:-3]
        forms += [base, base + "e"]
    elif len(word) > 4 and word.endswith("ed"):
        base = word[:-2]
        forms += [base, base + "e"]
    return forms


def alike(one, other):
    """Two content words name the same thing: "saving" finds "save 5000", "cakes" finds "cake"."""
    for left in _forms(one):
        for right in _forms(other):
            if left == right:
                return True
            if len(left) >= 4 and len(right) >= 4 and (left.startswith(right)
                                                       or right.startswith(left)):
                return True
            if len(left) >= 5 and len(right) >= 5 and left[:5] == right[:5]:
                return True
    return False


def find(memory, text):
    """An earlier topic matching what the user named ('back to the laptop', 'back to saving')."""
    wanted = keywords(text)
    if not wanted:
        return None
    for record in reversed(memory.get("topics") or []):
        have = record.get("words") or []
        if any(alike(word, other) for word in wanted for other in have):
            return record
    return None


# "Thanks. How long does it take?" is a follow-up: the thanks is a courtesy, not the question.
LEAD_ACKS = ACKS | GREET


def _this_line(record, memory):
    """True when the topic record was written for the line being answered right now."""
    turn = len(memory.get("turns") or []) if isinstance(memory, dict) else 0
    return record.get("turn") == turn


def context(memory, n=2):
    """The last n topic texts, oldest first, for understanding a follow-up in context."""
    records = memory.get("topics")
    if not isinstance(records, list):
        return []
    return [r.get("text", "") for r in records[-n:] if r.get("text")]


# Words that say how much or how long rather than what about: a line made only of these is
# asking about the thing the line before was about ("how long will it take, start to finish?").
# The asks that want a figure out of the answer: these are what a borrowed fact can get wrong.
MEASURED = frozenset(("how_long", "how_much", "how_many", "how_often", "time", "heat",
                      "money", "amount", "temperature"))


# A request to carry on rather than a question about what was just said: "what should I do
# about it?" asks for the next step, not for a sentence of the last answer.
PROCEED = ("what should i do", "what do i do", "what now", "what next", "then what",
           "what about now", "where do i go from here")


ASK_ONLY = frozenset("""
long much many time times often usually cost costs price prices worth expensive cheap cheaper
temperature hot warm cold heat minute minutes hour hours day days week weeks month months year years
step steps best first next last thing things way ways take takes long quick quickly soon
start finish it that them they there this these those one ones again
""".split())


# A question word in front of a subject names nothing: it is the asking, not the thing.
_LEAD_QUESTION = re.compile(r"^(?:whats?|which|how|when|where|who|why|do|does|did|is|are|"
                            r"can|could|should|would|will)\s+", re.I)


# The phrase after these belongs to someone else: "a birthday cake for my son" is about the cake.
_RELATION = re.compile(r"\b(?:for|with|to|about|because|from)\s+(?:my|our|his|her|their)\b")


# A "without" clause on a method question says what to leave out, and the thing left out is not
# what the conversation is about: after "how do i stop snoring without a machine" the follow-up
# "is there anything else" put the machine back in ("is the stop snoring machine anything
# else") and got the plug's fuse answer, because the subject kept the word the answer had just
# dropped. Only a question that asks how, though - "my first christmas without her" is about the
# absence, and that line's subject is the christmas and the person.
_FRAME_ASK = re.compile(r"\b(?:how|what|which|where|when|any way|ways|can|could|should|help)\b")


_WITHOUT_CLAUSE = re.compile(r"\s*\bwithout\b.*$")


# The verb a plan opens with is part of the action, not part of the thing: "cook a turkey" is
# about the turkey. Kept as a list of the verbs people start a plan with.
_VERBS = ("bake", "cook", "make", "build", "write", "paint", "plant", "grow", "fix", "clean",
          "decorate", "buy", "book", "prepare", "host", "throw", "plan", "learn", "start",
          "assemble", "sew", "knit", "roast", "boil", "fry", "grill", "set", "sort", "get",
          "replace", "repair", "install", "paint", "renovate", "organise", "organize")


# The words a wish or a plan opens with, and the verbs it can hand over to. A phrase that starts
# with one of these is naming the thing it wants, not the wanting: "we are thinking of getting a
# dog" is about the dog, and read as "thinking getting dog" the follow-up "how long will it take"
# asked the whole phrase a question and got an answer about toenails back.
_WISH = ("thinking", "thought", "thinking about", "considering", "planning", "hoping", "wanting",
         "looking", "interested", "keen", "trying", "dreaming", "weighing up")


_ACTION = ("get", "getting", "have", "having", "lose", "losing", "go", "going", "save", "saving",
           "learn", "learning", "try", "trying", "start", "starting", "stop", "stopping",
           "quit", "quitting", "book", "booking", "take", "taking", "do", "doing", "see",
           "seeing", "buy", "buying", "move", "moving", "change", "changing", "adopt",
           "adopting", "rescue", "rescuing")


# A verb with its particle is how a thing is reached, not the thing: "how do i get rid of slugs"
# is about the slugs, and with the particle left in the store called the chat "rid slug" - a
# recap said "We were on the rid slug", and the follow-up "will they come back" had a subject no
# module could use. The verb on its own is stripped further down (`_LEAD`); this takes the
# particle with it. Only pairs people say as one word are listed, so "i went back to work" and
# "it came back after a week" are untouched: back is not a particle of those verbs.
_PHRASAL = (
    "get rid of", "getting rid of", "got rid of", "get out of", "getting out of",
    "get on top of", "getting on top of", "get on with", "look after", "looking after",
    "look into", "looking into", "cope with", "coping with", "deal with", "dealing with",
    "put up with", "putting up with", "run out of", "running out of", "ran out of",
    "take care of", "taking care of", "keep up with", "keeping up with", "kept up with",
    "keep on top of", "keeping on top of", "keep track of", "keeping track of",
)


_PHRASAL_RE = re.compile(r"\b(?:" + "|".join(sorted((re.escape(p) for p in _PHRASAL),
                                                    key=len, reverse=True)) + r")\b")


def _gerund(verb):
    """The -ing form of a verb, spelled the way people spell it: get -> getting, make -> making."""
    if verb.endswith("ie"):
        return verb[:-2] + "ying"
    if verb.endswith("e") and not verb.endswith(("ee", "ye", "oe")):
        return verb[:-1] + "ing"
    if (len(verb) > 2 and verb[-1] not in "aeiouwxy" and verb[-2] in "aeiou"
            and verb[-3] not in "aeiou"):
        return verb + verb[-1] + "ing"
    return verb + "ing"


_VERB_WORDS = tuple(sorted({v for v in _VERBS} | {_gerund(v) for v in _VERBS if len(v) > 2}))


_WISH_RE = re.compile(
    r"^(?:(?:please|so|and|but|well|ok|okay)\s+)?"
    r"(?:i'?m|im|i\s+am|we'?re|we\s+are|i\s+have|i'?ve|"
    r"(?:i|we|you|they|he|she)\s+(?:am|are|is|was|were))?"
    r"(?:\s+(?:also|still|just|really|probably|maybe|now|only))?\s*"
    r"(?:" + "|".join(sorted(set(_WISH) | set(_ACTION), key=len, reverse=True))
    + r")\b(?:\s+(?:to|of|about|on|at|into|up|for))?\s+(?:(?:a|an|the|another|some|any|my|our)\s+)?")


_LEAD = re.compile(r"^(?:please\s+)?(?:i'?m|im|i\s+am|i\s+(?:want|need|would like|'?d like)|"
                   r"we'?re|we\s+are|i'?ve|i\s+have)?\s*"
                   r"(?:to\s+)?(?:(?:" + "|".join(_VERB_WORDS) + r")\s+)"
                   r"(?:a|an|the|my|our|some|any|two|three|this|that)?\s*")


# A correction opens with words that say "not the last thing, this one": "actually it's a
# funeral", "sorry, a funeral", "no i meant a funeral". They are not part of the thing the chat
# is on, so "what should i wear" after one asks about the funeral and not about "actually".
_CORRECTION_LEAD = re.compile(
    r"^(?:(?:no|nope|sorry|apologies|actually|oops|correction|wait)[\s,.!-]+|"
    r"my\s+mistake[\s,.!-]+|"
    r"i\s+(?:mean|meant|said|did\s+meant|didn'?t\s+mean)\s+(?:to\s+say\s+)?|"
    r"(?:its|it'?s|that'?s)\s+(?:actually\s+)?)+", re.I)


# A time is not the thing a chat is about. "im going to a funeral on friday" is about the
# funeral, and the follow-up "what should i wear" is about the funeral too; keeping "friday" on
# the end made the subject's head a day of the week and the follow-up read as being about that.
_TIME_WORDS = frozenset("""monday tuesday wednesday thursday friday saturday sunday
january february march april may june july august september october november december
week weekend month year morning afternoon evening night tonight today tomorrow yesterday
soon later midday noon am pm clock oclock""".split())


# "I'm thinking about getting a bike", "I'm looking at a new laptop": the opening says they are
# considering something, and the thing is what comes after it. Without this the subject carries
# the considering with it ("thinking getting bike") and no module that reads it can use it.
# The word that opens the phrase a person uses when they are deciding: "i'm thinking about
# getting a bike", "i'm looking at a new laptop", "i'm after a sofa". They name the thing they
# are considering, not a thing they have, and it is the thing a "which one?" is about.
#
# "getting" and "buying" only open one when a determiner or an adjective comes next, because the
# same words are states and not purchases: "we're getting married next year" is about a wedding,
# and stripping "getting" leaves "married", a word that fits half the knowledge base.
_CONSIDERING = re.compile(
    r"^(?:(?:i'?m|im|i am|we'?re|we are)\s+)?(?:"
    r"(?:thinking (?:of|about)|looking (?:at|for|into|round at)|considering|in the market for|"
    r"keen (?:on|to)|after)"
    r"|(?:getting|buying)(?=\s+(?:a|an|the|some|any|another|my|our|your|their|his|her|its|this|"
    r"that|these|those|new|used|second|old|decent|proper|cheap|good|nice|little|big|small|first|"
    r"one|two|three)\b))\s+")


# "getting married", "buying a house": the "getting" of a purchase opens a phrase about the thing
# only when the thing follows it. What follows these words here is a state or a verb, so the line
# is not about a purchase and its own verb is part of what it is about.
_BUYING_A_STATE = re.compile(
    r"^(?:(?:i'?m|im|i\s+am|we'?re|we\s+are)\s+)?(?:get|getting|buy|buying)\b(?!\s+(?:a|an|the|"
    r"some|any|another|my|our|your|their|his|her|its|this|that|these|those|new|used|second|old|"
    r"decent|proper|cheap|good|nice|little|big|small|first|one|two|three)\b)")


# A word that only counts or measures: a sum of money, a weight, a length of time. It is the unit
# of a figure, never the thing a chat is about on its own.
_A_FIGURE = frozenset("""pound pounds quid euro euros dollar dollars grand kilos kilo kg stone
    stones lb lbs ounce ounces gram grams litre litres pint pints mile miles minute minutes hour
    hours week weeks month months year years""".split())


# The chatty words in front of an announcement: "and one more thing", "ok so quick question".
_HANDOFF_THROAT = re.compile(
    r"^(?:(?:and|oh|ooh|ok|okay|so|but|right|ah|er|um|hmm|also|plus|hey|ta|anyway|then|just|"
    r"well|sorry)[\s,:-]*)+")


# The days that are a date and not an event with things to arrange. "my son's birthday is next
# saturday" says when, and what the line is about comes after the "and": the cake they are going
# to bake. A wedding or a party is left out on purpose, because "i have a wedding in june and i
# have to do a speech" is about the wedding and the speech is part of it.
_DATE_OCCASIONS = frozenset(stem(word) for word in
                             """birthday birthdays anniversary christmas xmas easter""".split())


# The words a date is made of besides the day itself: "next", "this", "on".
_DATE_FILLER = frozenset("""next last this coming on in at the of""".split())


# What somebody is making: the verb and the thing it makes ("bake him a cake", "doing a cake").
# A determiner has to follow, so "i dont know what to do" and "i have no idea what to get her"
# are not read as a thing being made.
_MAKING_A_THING = re.compile(
    r"\b(?:make|making|bake|baking|cook|cooking|prepare|preparing|build|building|do|doing)\s+"
    r"(?:\w+\s+){0,2}?(?:a|an|the|some)\s+[a-z']+")


_PEOPLE = frozenset()


def _the_people():
    """The words that name a person in the user's life ("my son"), in the forms keywords keeps.

    facts.py's own list, imported late: facts.py reads this module through named.py, so an import
    at the top of the file would come back with a half-built module. Read once and kept, because
    gist runs on every line.
    """
    global _PEOPLE
    if not _PEOPLE:
        from .facts import RELATIONS
        _PEOPLE = frozenset(form for word in RELATIONS for form in (word, stem(word)))
    return _PEOPLE


# "my flat is small", "the kitchen is tiny", "our bedroom is cramped": a line that only says
# how much room there is is about the thing we were already on, not a subject of its own. In
# "im thinking of getting a cat" / "my flat is small" / "what should i get for it", the flat
# says how much room the cat's things may take, and the "it" in the last line is still the cat.
_ROOM_LIMIT = re.compile(
    r"^(?P<head>(?:my|our|the|his|her|their|this|that|your)?\s*[a-z' ]{0,18}?)\s*"
    r"(?:is|are|was|were|seems|feels|gets)?\s*"
    r"(?:a bit |really |quite |very |so |too |dead |proper )*(?:small|tiny|cramped|poky|narrow)$")


# Only a space inside the home folds back into the subject the conversation was already on: a
# flat, a kitchen or a bedroom is what limits the cat's things. A garden, an allotment or a van
# named with its size is a new thing, and "the garden is small" / "what should i plant in it"
# is about the garden - folding that back answered it about the cat.
_HOME_SPACES = frozenset((
    "flat", "house", "home", "room", "rooms", "kitchen", "bedroom", "bedrooms", "bathroom",
    "lounge", "hall", "hallway", "landing", "garage", "loft", "attic", "basement", "cellar",
    "study", "porch", "conservatory", "utility",
))


# A follow-up that asks how long the thing takes, with the thing left out: "how long will it
# take?". The action in it ("lose a stone", "learn spanish") is what the question is about, and
# it is what the knowledge base is indexed by, so the ask is written out with it on the end.
DURATION_ASK = re.compile(r"\bhow (?:long|many (?:hours|days|weeks|months|minutes|years))\b")


# The words a bare duration ask is made of. Anything else in the line ("how long does it keep in
# the fridge") is a question of its own: it names the thing it is about and is left alone.
DURATION_WORDS = frozenset("""
how long many much hours hour days day weeks week months month minutes minute years year will
would does do did is was it that this one they them take takes taken cost costs last lasts
to for the a an in at on about
""".split())


# The verbs an ask about time can be about: "how long does it take to <verb> ...". A topic that
# is a thing rather than an action ("my boiler is making a noise") is not here.
ACTION = frozenset("""
learn lose get fix build paint clean save train study grow cook bake make do sort finish write
read find repair install set move pack apply book plant hire buy sell replace service bleed
insulate lay tile sand plaster dig compost prune knit sew drive fly travel play practise
practice teach organise organize plan prepare recover heal quit stop start cut reduce pay earn
pass sit cycle swim run walk redecorate declutter tidy clear chop boil roast freeze iron mend
patch sharpen assemble
""".split())


# The words that come before an action the person does themselves: "i want to lose a stone",
# "im trying to quit sugar", "we're planning to move". Everything before the action has to be
# one of these, or the action is somebody else's: "my boiler is making a noise" is about the
# boiler, and the answer to "how long will it take" is not "to make a noise".
PERSON_LEAD = frozenset("""
i we me us my our she he they her his their them 'm im am was were is are have had been
really just also still only
want wanna wanted need needed try trying plan planning plans hope hoping think thinking
like 'd would will going keep keeping kept start started starting get getting got
""".split())


# An action named as the thing to do is about the person doing it ("the best way to learn
# spanish", "any tips for how to save"): after these words the action is theirs.
ACTION_AFTER = frozenset("to of about".split())


# One attribute of the thing on the table, asked on a line of its own. After "im making bread" the
# person's next line is "and the oven temperature", which names no thing at all: the entries read
# the word "oven" and answered the repair card ("the heating element is almost always the fault"),
# and after "she wants a bike" the line "which size" reached the women's clothes chart. The thing
# is on the table and the attribute is the whole of the line, so it is written out with the thing:
# "oven temperature for bread", "how long does a chicken take", "what size bike do i need".
ONE_ATTRIBUTE = (
    (re.compile(r"\b(?:temperature|heat)\b"), "oven temperature for {thing}"),
    (re.compile(r"\b(?:time|timing|duration)\b"), "how long does {thing} take"),
    (re.compile(r"\b(?:size)\b"), "what size {thing} do i need"),
    (re.compile(r"\b(?:price|cost)\b"), "how much does {thing} cost"),
)


# Every word such a line can have: the attribute itself and the frame around it, and nothing else.
# A line with one word more is about something of its own ("and the oven fan is noisy") and keeps
# the answer it had.
ATTRIBUTE_WORDS = frozenset("""the a an and so ok okay or what which how about oven temp
temperature heat time timing duration size price cost much long does do i need it take
for of""".split())


# A thing named on the line before, unless that line named a count or a person rather than a
# thing: "im making bread" / "for 6 people" / "and the oven temperature" is still about the bread.
NOT_A_THING = frozenset("""it its that this these those they them there here thing things one
ones more less some any people person someone anyone everybody everyone you u me us we i""".split())


# A line that ends in a state is complaining about a thing, not naming one: "my bus is always
# late" is a bus that keeps coming late, and "the time" after it is how late, not "how long does
# bus alway late take" (which reached the coach fares). The word the line ends on is the state.
A_STATE = frozenset("""late early broken broke leaking noisy loud quiet slow fast cold hot warm
freezing boiling dirty clean empty full stuck blocked jammed wrong old new cheap expensive
rubbish useless dead faulty missing gone off mouldy soggy dry wet burnt raw undercooked""".split())


# A line that adds a fact or a limit to what we are already on, without naming it again:
# "he's allergic to nuts" after a cake, "we've only got 50 pounds" after a present.
DETAIL = re.compile(
    r"\b(?:allerg\w*|intoleran\w*|vegetarian|vegan|coeliac|gluten|free\b|diet\w*|budget|cheaper|"
    r"expensive|afford|only (?:got|have)|no (?:time|room|oven|car)|can't|cannot|couldn't|"
    r"doesn't|don't|won't|hate[sd]?|love[sd]?|prefer[s]?|instead|substitut\w+|swap|without|"
    r"left ?over|freez\w*|reheat\w*|shelf life|keeps? for)\b", re.I)


# The words a key uses to say what is being asked rather than what it is about: a key of
# ('chicken', ('how long', 'time', 'cook', 'oven')) is about a chicken, and the ask half of it
# says nothing about the subject of a follow-up.
ASK_PART = frozenset("""how what when where why which who whose long much many time often far
soon""".split())


# What a thing costs is asked for, not named. These are the words the price table keys its
# second group with: "how much does a plumber charge" is about the plumber, and "i charge it
# every night" is about nothing the price table knows. They are read as asking words only where
# the question is whether the line named the subject of an entry (see `_asked_only`), not
# everywhere: a price line is still a subject of its own for the rest of the store.
PRICE_ASK = frozenset("""charge charges charging costing cost costs price prices priced quote
quotes quoted fee fees rate rates expensive cheaper afford free worth payable""".split())


# The words that ask for advice, which name no thing of their own: "any tips for a long shift"
# asks how to get through a shift, and the "tips" in it says how the ask is put, not what it is
# about. Every card in the body table is keyed to the phrase "any tips for", so reading it as a
# word the line named made the knee card the subject of a line about a shift: the chat lent the
# line its old subject ("... knee hurting") and the card answered a question nobody asked.
# These are read as asking words only where the question is whether the line named the thing, the
# same places PRICE_ASK is read that way - a line about a rubbish tip still leans on "tip".
ASKS_FOR_ADVICE = frozenset("""tip tips advice advise advising hint hints help helps helping
ideas idea suggestion suggestions thoughts thought recommend recommended""".split())


# The words that start the part of a complaint saying what brought it on: "my back has been
# killing me **since i moved the sofa**". The thing named after them is the cause, not the
# subject of the complaint; "when" is left out because "my knee hurts when i run" is a line about
# the running as much as the knee, and its follow-up belongs to the running answer.
CAUSE_OF_THE_COMPLAINT = re.compile(r"\b(?:since|after|because|from)\b")


# Words that point back at a *thing* we were on. "he", "she", "him" and "her" are left out on
# purpose: a pronoun about a person points back at that person, not at the thing the chat was
# about, so "she keeps forgetting where things are in the kitchen" after "my mum moved in with
# us last month" must not be read with the move glued onto it - the entry that reached was the
# packing plan, which is advice for a different problem.
# "he" and "she" are here on purpose: "she likes gardening and wine" after "my mums birthday is
# on saturday" is a detail of that birthday, and widening it is what makes the gift answer work.
# What a pronoun about a person does *not* mean is that the line is a follow-up question on the
# thing we were on, so `person()`/`about()` below keep who it is, and a line that reports
# something not right about them is answered about them (bot/modules/chat.py, _about_someone).
REFERRING_WORDS = frozenset("""it its that this these those they them there their one ones
he she him her his""".split())


# "Is it worth paying a plumber or shall I have a go" is not about the thing we were just on:
# that "it" is the sentence's own subject and the real subject comes after it, so the line
# pointed back at nothing and yet drew on the last answer's sentence. "Is it worth it" does
# point back, so only the frame with a word after it is dropped.
DUMMY_IT = re.compile(
    r"\b(?:is|was|would|will)(?:n't)?\s+it\s+(?=(?:worth|ok|okay|better|best|rude|normal|"
    r"fine|safe|possible|legal|allowed|weird|strange|acceptable|polite|sensible|wise|cheaper|"
    r"easier|harder|a good idea|a good thing|too late|too soon)\b"
    # The frame brings its own subject along: a word like "a", "the" or "my" before the noun
    # says the line is about a thing of its own ("is it worth paying a plumber"). Without one
    # the line is about what we were already on ("is it worth scarifying in autumn" after the
    # lawn), so its "it" does point back and the frame stays.
    r"[^?]*\b(?:a|an|the|some|any|my|your|our|their|his|her|another|one|two|three)\s+\w)")


# Words that aim a question at something without naming it: "how often should I go?" is a whole
# question about the thing the last line was about, and nothing in it reaches an entry.
ASK_MORE = frozenset("""often frequent frequently regularly sooner soonest longer quick quicker
soon best good""".split())


# A verb that only stands in for the action of the topic: "how often should I go?", "when do I
# use it?", "what should I do?". It names no subject, so it is not what makes the line its own.
STAND_IN = frozenset("""go going gone get getting do doing done use using happen happening
happens be is are was were should shall can could would will want wants need needs have has
take taking start starting help helps helping check checks checking put putting place try tries
trying fix fixing sort sorting ease easing improve improving avoid avoiding prevent preventing
change changes changing add adding expect expecting""".split())


# A line about the chat itself - what the bot knows, what was said - is not a line about the
# topic: "what do you know about me" after "i'm trying to save money" is the store's own
# question, and reading it as the saving ask gives the money advice to somebody who asked what
# the bot had kept. The words name nothing, so only this list can tell the two apart.
ABOUT_THE_CHAT = re.compile(
    r"\b(?:what\s+(?:do|did)\s+you\s+(?:know|remember|have|hear|got)"
    r"|what\s+have\s+(?:i|you)\s+(?:told|said|mentioned|got)"
    r"|what\s+did\s+i\s+(?:say|tell|mention)"
    r"|what\s+(?:am\s+i|are\s+we)\s+(?:up\s+to|on\s+about|planning|doing)"
    r"|remind\s+me\s+(?:what|who|when|where)"
    r"|what\s+were\s+we\s+(?:talking|speaking|on)\s+about"
    r"|do\s+you\s+(?:remember|know)\s+(?:me|my|what|who|that))\b")


# A line that asks something: a question mark, or a question word at the start of one of its
# clauses. Only asking lines are read with the topic's words carried over them.
# The ask words, with the contraction people type instead of the apostrophe: "whats a good
# breakfast" is the same ask as "what is a good breakfast", and read as a statement it was not an
# ask at all - so the follow-up "and for lunch" found no question to put lunch into and the
# breakfast answer came back, then the "covered above" card claimed lunch was in it.
ASK_CUE = re.compile(
    r"\?|(?:^|\b)(?:what|which|how|why|when|where|who|whose)(?:'?s|'?re)?\b"
    r"|(?:^|\b)(?:should|shall|can|could|would|will|does|did|is|are|am|any|anything"
    r"|something\s+else)\b")


# A line that is only the thing it asks about, with the asking left off: "any games?", "and
# drinks", "what about pudding", "anything else". People ask this way in the middle of a plan -
# the plan is on the table, so the question is about a part of it that the line just names. On its
# own the line is a statement ("any games" has no verb and no question word in front), so it is
# read as the ask it is: the thing named, asked about in the situation the chat is on.
ELIDED_ASK = re.compile(
    r"^(?:(?:ok|okay|so|and|also|plus|or|then|right|yeah|yes|oh|em|um)\s+)*"
    r"(?:any|anything|something|more|else|another|other|rest|what\s+about|how\s+about|"
    r"idea|ideas|tip|tips|thoughts|suggestions)\b")


# A line that puts a new thing in the place of the one the question asked about: "how much
# protein in porridge oats" / "and in a slice of bread" / "what about two slices". People talk
# this way over several turns - the ask is settled and only the thing changes - and the line on
# its own carries no asking at all ("and in a slice of bread" has no question word and no verb),
# so it is read as the last question asked with its thing said again.
SAME_ASK = re.compile(r"^(?:(?:ok|okay|so|and|also|plus|or|then|right|yeah|yes|oh)\s+|"
                      r"(?:what|how)\s+about\s+)", re.I)


# A line that only counts ("what about two slices") names the thing it counts in the turn before.
COUNTING = frozenset("""one two three four five six seven eight nine ten eleven twelve a an some
few couple half slice slices piece pieces cup cups bowl bowls portion portions glass glasses
handful handfuls tin tins can cans spoon spoons tablespoon tablespoons teaspoon teaspoons each
more""".split())


# The words the question puts before the thing it asks about: everything up to the preposition
# that introduces it ("how much protein in", "how many calories in", "what is the best time for").
THE_TAIL = re.compile(r"\b(?:in|for|of|at|on|with|from|into|about)\b", re.I)


# A follow-up that puts the pronoun where the subject belongs: "how long does it take?" after
# "im buying a house" asks how long the thing the chat is on takes, and the knowledge base
# answers exactly that with the subject in the pronoun's place ("how long does buying a house
# take"). The whole line has to be the shape - a line that names its own subject after the verb
# ("how long does it take to get a passport") carries nothing.
LONG_IT_TAKES = re.compile(
    r"^\s*(?P<head>how long (?:does|do|will|would|is|are|should|can|could))\s+"
    r"(?:it|that|this|they|he|she)\s+take\s*[?.!]*$", re.I)


# The person the topic opens with, so the phrase can stand on its own: "im buying a house" is
# "buying a house", and "i want to learn the guitar" is "want to learn the guitar".
TOPIC_OPENS_WITH = re.compile(r"^\s*(?:i(?:'m|m| am| have| 've| want| need)?|we(?:'re|re| are)?|"
                              r"i've|ive|i'd|id)\s+", re.I)


# How long to stay is asked with the place in the line ("how many days in edinburgh"), and the
# knowledge base keeps a table of days per city. A follow-up that asks it without the place -
# "how many days", "how many nights", "how long should i go for" - is about the trip the chat is
# on, so the place the topic names goes into the line where that table wants it.
STAY_ASK = re.compile(r"\b(?:how (?:many|much) (?:days|nights|time)|how long)\b")


# The words the line may be made of and still be nothing but that ask: "how long should i go for"
# is the whole question, "how many days should i rest my ankle" is a question about an ankle.
STAY_ONLY = frozenset("""how many much long days day nights night should shall i we you go going
there it for a an the in of time stay staying spend would will do can could need needs then""".split())


# A city in the topic is the place of a stay only when the topic says the person is going there.
# "why is edinburgh so windy" and "i live in edinburgh" name the same city, and a holiday length
# is no answer to either: the frame is what makes the city the place of a trip.
TRIP_FRAME = re.compile(
    r"\b(?:going|go|goes|off|trip|holiday|vacation|visit|visiting|fly|flying|travelling|traveling|"
    r"travel|heading|head|booked|booking|break|away|weekend|nights?|days)\b", re.I)


# The words that say the city is where somebody lives, or where they have been: the same city in
# the same kind of line, and only a trip frame in front of it makes it somewhere they are going.
LIVES_THERE = re.compile(
    r"\b(?:live|lives|living|lived|move|moves|moved|moving|relocate|relocating|relocated|"
    r"emigrate|emigrating|grew up|grow up|born|work|works|working|commute|commuting)\b", re.I)


# The words that stand in for the subject: "when do those go in" after tomatoes is "when do
# tomatoes go in", and the subject added to the end of the line reaches nothing.
POINTING_WORD = re.compile(r"\b(?:it|that|this|those|these|them|they|one|ones)\b", re.I)


A_BARE_MEASURE = re.compile(r"\b(?:how much|how many|how often|how long|how far|how soon)\b")


# The words a measure ask is made of. What is left of the line is the thing it asks about.
MEASURE_WORDS = frozenset("""cost costs costed price priced charge much many more less long often
far soon take takes taking time times need needs needed spend spent pay paid get got worth
there it that this""".split())
