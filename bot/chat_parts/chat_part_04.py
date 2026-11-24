"""Part 4 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import LINGERED_LINE


from ..understanding import lexicon
from .chat_part_03 import (
    ASKS_IF_NORMAL, SAME_COLD, FEELINGS,
)


def _the_kind_of_worry(kind, text):
    """The worry this is, on the module's own rule for a worry that names a day.

    "i feel ill with dread about monday" is not a worry with no end date on it: the reply that
    says so reads as if they had not said when. The same goes for a line that asks whether the
    feeling is normal, which the "anxious" pool answers and the worry pool talks past.
    """
    if kind != "worry":
        return kind
    if WORRY_WHEN.search(text) or ASKS_IF_NORMAL.search(text):
        return "anxious"
    return kind


NO_NOSE_WORDS = frozenset("""stuffy stuffed bunged blocked congested congestion""".split())


def _the_same_cold_again(clean, memory):
    """True when this line only says the cold the bot has just answered, nose and all.

    Only the cold said without a nose: "im stuffy" then "im all bunged up" is the second half of
    one cold, and the answer the person already has (with a "Same answer, and it covers this:" in
    front of it) is a better turn than this module's thinner card. A line that names a new place -
    "i keep sniffing", "now my throat hurts" - says something the last answer did not, and keeps
    its own reply.
    """
    if not isinstance(memory, dict):
        return False
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    if not turns:
        return False
    words = {w.lower() for w in re.findall(r"[a-z']+", str(clean or "").lower())}
    if not words & NO_NOSE_WORDS:
        return False
    return bool(SAME_COLD.search(str(turns[-1].get("bot") or "")))


# "im crap at maths", "im useless with names": a word that rates what somebody can do is an
# ability, not a mood, and an `at`/`with` straight after it says which one the line is about.
# The positive words are not here on purpose: "im happy at work" is a mood.
ABILITY_WORDS = frozenset("""bad crap rubbish rough useless hopeless terrible awful lousy poor
    worse worst""".split())


# The same day said either way round: "long day", and "today was long", where the word comes
# after the day instead of in front of it. The subject stays a day or a part of one: a week said
# this way ("the week has been rough", "my week was long") has its own better answer, a run of
# days rather than one, and "an early night" is the wrong thing to offer for it.
# Only the words that say how long it was are read the second way round. The ones that say how
# bad it was ("today was rubbish", "this morning was awful", "today has been hard") already have
# an answer that asks what happened or names the feeling, and this pool's tiredness advice would
# replace it: "today was rubbish" was "Sorry. Do you want to tell me what has made it like that?"
# and the same shape turned it into "Rough one. A shower, something warm to eat and an early
# night". Word order is not the same thing as the same complaint, so the words already answered
# elsewhere stay where they were, and only "today was long" - which had no pool at all and got
# the greeting module's "I'm listening - say more if it helps" - is read here. "One of those
# days" is the same complaint in the words the rough-day pool already answers.
# The day is also said by where it was spent: "work was long today", "works been long",
# "i was at work all day". The stretch of time is still one day and the big word is still how
# long it was, so this is the same complaint in another word order and it belongs in this pool
# rather than in the greeting module's "I'm here if you want to dig into any of that". Only the
# words that say how long it was take a subject of its own that is not a day - "work was
# rubbish today" already has its answer that asks what happened, and offering an early night
# instead would swallow it - and a week or a month said this way keeps its own run-of-days
# answer, so the trailing time word is only there to let "today" come last.
ROUGH_DAY = re.compile(r"\b(bad|rough|long|terrible|awful|rubbish|crap|hard|tough|mental|"
                       r"hectic|horrible|shitty|draining|mad|full|wild|crazy)\s+"
                       r"(day|week|morning|night|shift|one)\b"
                       r"|\b(?:today|the (?:day|morning|night|shift)|"
                       r"my (?:day|morning|night|shift)|"
                       r"this (?:day|morning|night|shift))"
                       r"(?:\s+(?:was|is|has been|had been)|['\u2019]?s been)\s+"
                       r"(?:so |really |just |pretty |very |a bit |quite |such a )?"
                       r"(?:long|slow|endless|never[- ]ending)\b"
                       r"(?:\s+(?:today|tonight|again|as well))?"
                       # Work is a subject that is not a day, so it takes only the words that say
                       # how long: "work is slow today" is a boring day, not an exhausting one, and
                       # "an early night usually resets it" is the wrong answer to boredom. Slow
                       # was ever only read after a day-word ("today was slow", "the shift was
                       # slow"), and it stays there.
                       r"|\b(?:work|the day at work)"
                       r"(?:\s+(?:was|is|has been|had been)|['\u2019]?s been)\s+"
                       r"(?:so |really |just |pretty |very |a bit |quite |such a )?"
                       r"(?:long|endless|never[- ]ending)\b"
                       r"(?:\s+(?:today|tonight|again|as well))?"
                       r"|\b(?:i|we)\s+(?:was|were)\s+(?:at|in)\s+work\s+"
                       r"(?:all (?:day|night|evening|morning)|till|til|until|late)\b"
                       r"|\bone of those (?:days|mornings|nights)\b")


WHAT_A_DAY = re.compile(r"\bwhat a (day|week|morning)\b")


# A stretch of time that will not move: "this week is dragging", "the week has been long", "school
# holidays are too long", "the days are long at the moment", "been a slow month". ROUGH_DAY reads
# the day and the week with a bad word in front of them ("a long week", "what a week"); these are
# the same complaint with the stretch itself as the subject, and every one of them fell to the
# stock line ("I'm listening - say more if it helps", "Got it. Is there anything you'd like a
# hand with?"). The rough-day pool answers with a shower and an early night, which is advice for a
# bad day and not for a week with nothing in it, so the stretch gets its own pool. Both a stretch
# and a word for how it goes are needed, which is what keeps it off "the days are getting longer"
# and off a line that names a person.
A_STRETCH = (r"(?:week|weeks|month|months|term|half[- ]term|holidays?|summer|winter|autumn|"
             r"spring|days?|nights?|weekends?|mornings?|evenings?|year)")


A_STRETCH_THAT_DRAGS = re.compile(
    r"\b(?:this|that|the|these|those|another|my|our|school|whole)\s+" + A_STRETCH + r"\b"
    r"[^.!?,;]{0,24}?"
    r"\b(?:is|are|was|were|has\s+been|have\s+been|['\u2019]?s\s+been|feels|feel)\b"
    r"[^.!?,;]{0,16}?"
    r"\b(?:dragging|drags|crawling|crawls|slow|long|endless|never[- ]ending|"
    r"taking\s+(?:forever|ages)|going\s+on\s+forever|"
    # The same complaint in the wear idioms: "this week has been a nightmare", "the month has
    # been a slog". They are a stretch of time and not a job or a night, which is what the wear
    # reader and the child's-nightmares entry read them as.
    r"a\s+(?:nightmare|mare|slog|grind|hell)|nightmare)\b", re.I)


def _a_stretch_that_drags(clean):
    """True for a stretch of time said to be long or slow, with nothing else in the line."""
    text = " ".join(str(clean or "").lower().split())
    if not text or "?" in text:
        return False
    if not A_STRETCH_THAT_DRAGS.search(text):
        return False
    # A stretch of somebody else's day is their line; a stretch of time with a body in it is an
    # ache. Both have their own readers, so the pool stands down on them.
    if VENTED.search(text):
        return False
    return True


# The same complaint said the other ways people say it: "it's doing my head in", "he drives me up
# the wall", "she gets on my nerves". The thing complained about is named in the line, and these
# are all the same kind of line, so they get the same warm reply.
VENTED = re.compile(
    r"\b(does? (?:my|your) head in|doing (?:my|your) head in|done (?:my|your) head in"
    r"|(?:drives?|driving|drove) (?:me|us) (?:mad|crazy|nuts|round the bend|up the wall|bonkers|insane)"
    r"|(?:gets?|getting|got) on (?:my|your|our) nerves"
    r"|(?:winds?|winding|wound) (?:me|us) up"
    r"|(?:picks?|picking|picked) on (?:me|us)"
    # The same shape said with the other verbs people use for a thing wearing them down:
    # "work is stressing me out", "the kids are wearing me out", "the commute is getting me
    # down". None of them was here, so those lines read as news and were answered with their
    # own words back ("Got it — your job is stressing you out.") or with the fallback.
    r"|(?:stresses?|stressed|stressing) (?:me|us) out"
    r"|(?:wears?|wore|worn|wearing) (?:me|us) out"
    r"|keeps? (?:on )?(?:moaning|nagging|complaining|going on at))\b")


# What a worry is about decides which reply fits. "Nerves before something big are normal"
# presumes an event, so it only belongs to a line that names one; a person, or a thing with no
# date on it, needs an answer that does not.
WORRY_FEELING = re.compile(r"\b(?:worried|worrying|worry|anxious|anxiety|nervous|scared|"
                           r"frightened|panicking|panic|on edge|stressed|stressful)\b")


WORRY_EVENT = re.compile(r"\b(?:test|tests|interview|interviews|exam|exams|results|scan|"
                         r"appointment|presentation|audition|assessment|viva|deadline|"
                         r"surgery|operation|due date|first day|first shift|driving test)\b")


WORRY_PERSON = re.compile(
    r"\b(?:about|for|of)\s+(?:(?:my|our|his|her|their)\s+)?"
    r"(mum|mom|mother|mam|dad|father|son|daughter|wife|husband|partner|boyfriend|girlfriend|"
    r"brother|sister|friend|mate|flatmate|boss|colleague|nan|nana|granny|gran|grandma|"
    r"grandad|grandpa|aunt|uncle|kid|kids|child|children|baby|parents|family|dog|cat)\b")


# A worry that names what it is about ("worried about money") is not a free-floating one either.
WORRY_ABOUT_THING = re.compile(r"\b(?:about|of)\s+[a-z]")


# A day or a time in the line is a date, so the worry is not the kind with none: "worried about
# tomorrow", "nervous about next week", "worried about friday".
WORRY_WHEN = re.compile(
    r"\b(?:today|tonight|tomorrow|tomorrows|this (?:morning|afternoon|evening|night|week|"
    r"weekend|month)|next (?:week|weekend|month)|the (?:weekend|morning)|later|soon|"
    r"(?:on |this |next |until )?(?:monday|tuesday|wednesday|thursday|friday|saturday|"
    r"sunday))\b")


# Saying what you cannot do is a statement about how you are, not a request: "i can't get out
# of bed", "i can't face going to work", "i haven't been able to sleep". A friend hears that
# and says something about it, which is what a neutral "Got it, anything I can help with?"
# never does. Only first person ("my son can't sleep" is about the son), only a real inability,
# and only a daily-life action: a line about what cannot be done right now in the world ("i
# can't find my keys", "i can't log in") is a problem to solve and is left to the modules that
# solve it.
#
# "I can barely keep my eyes open" and "i can hardly get out of bed" are the same inability as
# "i can't": barely and hardly are how a thing that is nearly out of reach is said, and read as
# no inability at all they reached whatever row shared a word with them - the tired line above
# was answered with the conjunctivitis card, then with the 20-20-20 screen rule.
CANT = re.compile(
    r"\b(?:i|i'm|im|i've|ive|we|we're)\b[^.!?]{0,50}?\b(?:can'?t|cant|cannot|can not|"
    r"can\s+(?:barely|hardly)|could\s+(?:barely|hardly)|"
    r"couldn'?t|couldnt|struggl(?:e|es|ed|ing) to|haven'?t been able to|havent been able to|"
    r"not able to|find(?:ing)? it hard to|find(?:ing)? it difficult to|"
    # "im not eating much" and "im not sleeping much" are a run of bad days said plainly:
    # the thing named is a daily-life action, and the word after it says how far it has gone.
    r"not (?:been )?(?:eating|sleeping)\s+(?:much|well|properly|enough|at all|regularly|"
    r"lately|these days|any ?more)\b|"
    # "i've not been sleeping" and "i've not been eating" are how a run of bad nights is
    # usually put, and the thing named is still a daily-life action, so they read the same as
    # "i can't sleep". "i've not been to rome" names nothing of the sort and is left alone.
    r"haven'?t (?:slept|eaten)|have not (?:slept|eaten)|not been (?:sleeping|eating)|"
    r"not (?:slept|eaten))\b")


# The same line with the subject left off the front, which is how a lot of people type: chat
# speak drops the "i", so "cant sleep" is the line "i cant sleep" and a bare ack answers
# nobody. Only when the clause opens with the inability itself - a leader such as "so", "and"
# or "still" may come first - and never when a word that could be the subject follows the verb:
# "my son cant sleep" and "cant you sleep" are about someone else, whatever the rest says.
NOT_THE_SUBJECT = (r"(?!\s+(?:i|i'm|im|you|u|we|we're|they|he|she|it|anyone|anybody|someone|"
                   r"somebody|everyone|everybody|there|nobody|people)\b)")


INABILITY = (r"(?:can'?t|cant|cannot|can not|can\s+(?:barely|hardly)|"
             r"could\s+(?:barely|hardly)|couldn'?t|couldnt|could not|"
             r"struggl(?:e|es|ed|ing) to|not able to|"
             r"haven'?t been able to|havent been able to|have not been able to|"
             r"not been able to|find(?:ing)? it (?:hard|difficult) to|"
             r"haven'?t (?:slept|eaten)|have not (?:slept|eaten)|not been (?:sleeping|eating)|"
             r"not (?:slept|eaten))")


CANT_OPENING = re.compile(
    r"^(?:(?:so|and|but|then|also|plus|honestly|tbh|still|just|really|now|anyway|ok)\s+){0,2}"
    r"(?:" + INABILITY + r"\b" + NOT_THE_SUBJECT + r")")


# A span of days after "not eaten" or "not slept" is the same cue as "much" or "at all", and it
# used to be the one shape of a run of bad days the bot did not read at all: "i havent eaten in
# three days" was answered "Noted: you haven't eaten in three days", "i havent eaten in a week"
# the same, "i havent eaten since monday" something else entirely, and "i havent slept in three
# days" the naps-and-body-clock card. The thing named is still a daily-life action, and the span
# after it is how far it has gone, so it reads exactly like "i haven't eaten much".
SPAN_TAIL = (r"(?:for|in|over|since)\s+(?:\d+|a|one|two|three|four|five|six|seven|eight|nine|"
             r"ten|a few|a couple of|several|many)\s+(?:days?|nights?|weeks?|months?)\b"
             r"|(?:for|in|over)\s+(?:days?|weeks?|months?)\b"
             r"|since\s+(?:yesterday|last (?:night|week|monday|tuesday|wednesday|thursday|"
             r"friday|saturday|sunday)|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
             r"the weekend|christmas)\b")


# "it's been three days since i ate" says the same thing from the other end, and it opens with
# "it's" where every other head is anchored on a first-person subject, so it needs its own door.
ITS_BEEN = re.compile(
    r"\b(?:it'?s|it has|its|thats|that is) been\s+(?:\d+|a|one|two|three|four|five|six|seven|"
    r"eight|nine|ten|a few|several|many)\s+(?:days?|nights?|weeks?)\s+since\s+i(?:'?ve| have)?\s+"
    r"(?:ate|eaten|slept|sleep|last ate|last slept)\b")


# Two days or more is no longer one bad day: it is worth a call today, so the reply says a
# different thing from the one it says about an appetite that has gone off. "since yesterday" is
# one day, so it stays with the ordinary pool.
LONG_SPAN = re.compile(
    # The span has to sit straight after the verb: "i havent slept properly in a week" is a rough
    # week, often a baby or a shift pattern, and the person has not said they are not sleeping, so
    # a qualifier in between keeps the ordinary pool. Two days of not eating or not sleeping is
    # the one that is worth a call today.
    r"\b(?:eaten|ate|eating|eat|slept|sleep|sleeping)\s+(?:for|in|over)\s+"
    r"(?:\d+|two|three|four|five|six|seven|eight|nine|ten|a few|a couple of|several|many)\s+"
    r"(?:days?|nights?|weeks?|months?)\b"
    r"|\b(?:eaten|ate|eat|slept|sleep)\s+(?:for|in|over)\s+(?:a|one)\s+(?:week|fortnight|month)\b"
    r"|\b(?:eaten|ate|eat|slept|sleep)\s+(?:for|in|over)\s+(?:days|weeks|months)\b"
    r"|\b(?:eaten|ate|eat|slept|sleep)\s+all\s+(?:week|weekend|month)\b"
    r"|\b(?:eaten|ate|eat|slept|sleep)\s+since\s+(?:last\b|the weekend|christmas|monday|"
    r"tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    r"|\bbeen\s+(?:\d+|two|three|four|five|six|seven|eight|nine|ten|a few|several)\s+"
    r"(?:days?|nights?|weeks?)\s+since\b", re.I)


STUCK = (
    ("mornings", (r"\b(?:get|getting|got)\s+up\b(?=$|[,.!?;]|\s+(?:in the mornings?|for work|"
                  r"today|most days|at all|any ?more|these days|early|before)\b)",
                  r"\b(?:out of bed|get going|getting going|start the day|face the day|"
                  r"mornings|in the morning)\b")),
    ("sleep", (r"\b(?:get to sleep|fall asleep|sleep|sleeping|slept|awake|nights?)\b",
               # A tired body said the way people say it, with no sleep named at all: "i can
               # barely keep my eyes open", "i keep nodding off at my desk", "my eyes keep
               # closing on the bus". None of them names sleep, and each was answered from
               # whatever row shared a word with it - the eye card, the posture card, the
               # 20-20-20 screen rule.
               r"\beyes?\s+(?:open|shut|closing|dropping)\b|" 
               r"\bnodd(?:ing|ed|s)?\s+off\b|\bstay(?:ing)?\s+awake\b|"
               r"\bkeep(?:ing|s)?\s+(?:falling|dropping)\s+asleep\b")),
    # Eating in general, never a named food or a diet: "can't eat gluten" is a restriction.
    ("eating", (r"\b(?:eat|eats|eating|eaten)\b(?=$|[,.!?;]|\s+(?:anything|much|at all|properly|"
                r"a (?:full |proper |hot )?meal|full meals|three meals|a thing|normally|"
                r"regularly|these days|lately|any ?more|anymore|all (?:week|day|weekend|month)|"
                r"in the (?:morning|evening)s?|" + SPAN_TAIL + r")\b)",
                r"\b(?:face food|face a meal|face meals)\b",
                # "it's been three days since i ate" names the action after "since", so the
                # pattern above never sees it.
                r"\bsince i (?:ate|eaten|slept|sleep)\b")),
    ("people", (r"\b(?:see(?:ing|s)? (?:people|anyone|friends|my friends|another person)|"
                r"be around people|face anyone|face people|out of the house|leave the house|"
                r"go out|get out|go anywhere)\b",)),
    # The noun, not the verb: "can't work out my tax" is a sum, not a working day.
    ("work", (r"\b(?:go to work|get to work|at work|face work|face going (?:in|to work)|"
              r"my job|the job|the office|shifts?)\b",
              # A time word after "work", never a bare "work" at the end: "i cant get the
              # printer to work" is a printer, not a working day.
              r"\bwork\b(?=\s+(?:today|tomorrow|this week|any ?more|at all|right now)\b)",
              r"\b(?:school|uni|college)\b")),
    ("focus", (r"\b(?:concentrate|focus|think straight|take anything in)\b",)),
    ("effort", (r"\b(?:bothered|motivated|do anything|face anything|get round to)\b",)),
    # Not about one kind of day, but about how the person is rather than a thing to fix.
    ("coping", (r"\b(?:cope|manage|get through|face another|face it|keep going|carry on|"
                r"be here|(?:do this|go on|take it|keep it up) any ?more)\b",)),
)


# What the safety lane owns even when it is phrased as an inability.
STUCK_SAFETY = re.compile(r"\b(breathe|breathing|chest|blood|bleeding|pills?|overdose|hurt "
                          r"myself|kill myself|end it)\b")


# An idiom is not an inability: "i can't wait to get to sleep" is looking forward to it.
# The negation is the same set of spellings CANT accepts, because the engine retries a line
# in its normalised spelling: "can't" comes back as "can not", and a guard that only knew
# "can't" missed the idiom on the retry.
NEG = r"(?:can'?t|cant|can not|cannot|couldn'?t|couldnt|could not)"


STUCK_IDIOM = re.compile(r"\b" + NEG + r"\s+(?:wait|think(?!\s+straight)|believe|"
                         r"stand|afford|thank|recommend|help|resist|say|tell|begin to|stop)\b")


# Using a thing is not an inability to work: "i can't work the coffee machine" has an object
# after the verb, where "i can't work today" has a time.
STUCK_OBJECT = re.compile(r"\bwork(?:s|ed|ing)?\s+(?:the|this|that|my|a|an|it|out)\b")


# Blaming yourself is not a shortage of effort: "i can't do anything right" is about them.
STUCK_SELF = re.compile(r"\b(?:do|doing|did|get|getting|got)\b[^.?!]{0,20}\bright\b")


# "do anything" is the person's energy only when nothing follows it: "i can't do anything with
# nuts in it" is a food line, "can't do anything on this laptop" is the laptop, "can't do
# anything about the noise" names what the noise is. Without the preposition the reading stood
# on the bare verb, and a line about nuts was answered with a card about not being bothered.
STUCK_DOES_SOMETHING = re.compile(
    r"\b(?:do|does|did|doing)\s+anything\s+(?:with|on|about|to|for|in|at)\s+\S")


# What follows "in" or "at" can be a time or a degree rather than an object: "i can't do anything
# at all", "can't do anything at the moment", "can't do anything in the mornings" are the person's
# energy, and the mood card is the answer to them. "can't do anything in the kitchen" names the
# kitchen, and "can't do anything at all with nuts" names the nuts in the words after it, so the
# phrase is a degree only when the line puts no thing after it.
STUCK_A_DEGREE_OR_A_TIME = re.compile(
    r"\b(?:in|at)\s+(?:all|the\s+moment|this\s+moment|the\s+minute|times|any\s+way|"
    r"the\s+(?:mornings?|afternoons?|evenings?|nights?|daytime|week|weekend)|this\s+weather)\b")


STUCK_AN_OBJECT = re.compile(r"\b(?:with|on|about|to|for)\b")


def _doing_something_to_a_thing(clean):
    """Whether "do anything" names a thing it cannot be done to, not a degree or a time of day.

    "i can't do anything with nuts in it" is the nuts, and "i can't do anything at all" is how
    the person feels: the preposition alone cannot tell them apart, and a bare `at`/`in` took
    three low-mood lines away from the mood card. So the phrase after `at`/`in` is read, and it
    counts as a degree only when the line names no thing after it either.
    """
    found = STUCK_DOES_SOMETHING.search(clean)
    if not found:
        return False
    degree = STUCK_A_DEGREE_OR_A_TIME.search(clean, found.start())
    if not degree:
        return True
    # "at all with nuts" is still a line about nuts: the degree has to be the last thing said.
    return bool(STUCK_AN_OBJECT.search(clean, degree.end()))


# The reason is the line: "i can't get out of bed, my back went", "can't work because my wrist
# is sore", "i can't afford to go out with my friends".
# "since" is a why-word ("i can't eat since the dentist") and also a span ("i haven't eaten
# since Monday"), and only the first is a reason. Without the lookahead the span lines were
# dropped before any reply: "i havent eaten since monday" answered "How ready do you feel for
# it?", and "i havent slept since friday" the same.
STUCK_REASON = re.compile(r"\b(?:because|due to|after my|after the)\b"
                          r"|\bsince\b(?!\s+(?:yesterday|last\b|monday|tuesday|wednesday|"
                          r"thursday|friday|saturday|sunday|the weekend|christmas|\d|"
                          r"i(?:'?ve| have)?\s+(?:ate|eaten|slept|sleep|last ate|last slept)\b))"
                          r"|\bever since\b"
                          r"|,\s*(?:my|me|im|i'm|ive|i've)\b")


# A thing that opens is a thing to fix, not an inability: "i can't get out of my front door"
# and "can't open the shed lock" are the door, not a person who cannot face going out. It is
# the same reading as STUCK_OBJECT - the line names the object the verb is about.
STUCK_FIXABLE = re.compile(r"\b(?:door|doors|lock|locked|unlock|key|keys|latch|handle|hinge|"
                           r"window|windows|gate|garage|lift|elevator|shutter|deadlock|"
                           r"bolt|bolt(?:ed)?|zip|zipper|jar|lid|drawer|cupboard|tap)\b")


# A line that names a death, now or earlier in the conversation, is about the death first
# ("my husband died in march and i can't sleep"): sympathy and the loss are other modules' turn.
STUCK_LOSS = re.compile(r"\b(died|dying|death|dead|passed away|passing|funeral|cremation|"
                        r"buried|widow|widower|grief|grieving|bereaved|"
                        r"lost my (?:mum|mom|mother|dad|father|wife|husband|son|daughter|"
                        r"sister|brother|baby|child))\b")


def said_loss(memory):
    """True when a death has been named earlier in the conversation."""
    if not isinstance(memory, dict):
        return False
    for turn in (memory.get("turns") or [])[-8:]:
        if isinstance(turn, dict) and STUCK_LOSS.search(" ".join(str(turn.get("user") or "").split()).lower()):
            return True
    return False


# The reply pools live in chat_replies.py: this file was 19 KB from the upload budget alarm
# and `REPLIES` is 61 KB of it. Same dict object, imported - not a copy.
from ..modules.chat_replies import REPLIES  # noqa: F401


# Small opinions: the bot has a view and says it briefly. A "do you like X" line with no
# entry here is left alone, rather than answered with a line that would fit anything.
OPINIONS = (
    (("bird", "birds", "heron", "kingfisher"),
     ("I do like birds — herons especially, the way they stand in a river like they own it.",
      "Birds, yes. A kingfisher is the one I would most like to see: a flash of blue and gone.",
      "I do. Herons have a lot of nerve, standing in the water like they own the place.")),
    (("cat", "cats", "dog", "dogs"),
     ("Both, for different reasons. Dogs are daft and glad to see you; a cat that picks you is "
      "hard to beat.",
      "Cats, by a whisker. Though I would not turn down a dog.",
      "Dogs. Uncomplicated, and always pleased to see you.")),
    (("rain", "rainy", "wet weather"),
     ("I don't mind it. Rain is a good excuse for a slow afternoon indoors.",
      "I like it. It makes a warm room feel better than the weather outside.")),
    (("snow", "snowy"),
     ("It looks best when it is still falling and nobody has to go anywhere.",
      "Yes, in pictures. Less so once it turns to slush.")),
    (("coffee", "tea"),
     ("Tea, mostly, with coffee a close second.",
      "Tea. Coffee is more of an occasion.")),
    (("summer", "winter", "autumn", "spring", "season"),
     ("Late spring: long evenings, everything green and not too hot. Autumn is a close second.",
      "Autumn. Cool enough to walk, and the trees do all the work.")),
)


# "Ugh, the first day of it is the worst" is for a bug that has just arrived. A line that says
# how long it has been going is telling you the length is the point, so it keeps the two lines
# that suit anything that has hung on.
REPLIES["ill_lasting"] = LINGERED_LINE


# A follow-up about something the conversation is already on. The worry was named in an
# earlier turn ("I'm nervous about a dentist appointment"), so the question after it gets the
# concrete next step rather than a second helping of sympathy.
CONTEXT_CHAT = (
    (("dentist", "dental", "checkup", "check-up"),
     (r"\bwhat will they\b", r"\bwhat happens\b", r"\bwhat should i expect\b",
      r"\bhaven't been\b", r"\bnot been\b", r"\bhow long\b", r"\bwill it hurt\b",
      r"\bdoes it hurt\b"),
     ("Most check-ups are a look, a scrape and a polish — the polish is the noisy bit, not the "
      "sore one. Tell them at the desk that you're nervous and they will talk you through it.",
      "If it has been years, say so when you book and ask for a longer appointment. They would "
      "rather know than find out halfway through.")),
    (("interview", "interviewing"),
     (r"\bwhat will they ask\b", r"\bwhat should i say\b", r"\bhow long\b"),
     ("Have one story ready about something you fixed or sorted out, and one question to ask "
      "them at the end. Those two do most of the work.",
      "They are mostly checking whether they would like to work with you. Short, honest answers "
      "beat polished ones.")),
)


# The days the bot can be asked about, for "how about your day" and its neighbours.
_BOT_DAY = "(?:day|weekend|week|evening|morning|night)"


# The same small-talk ask with half of it left out: "any plans tonight?", "got plans for the
# weekend?", "you got plans later?". Nothing in the line says who the plans are for, which is
# what makes it the bot's answer to give: an ellipsis of "have you got any plans". The weekend
# planner read the word "plans" as the ask and answered with the two-things-in-the-diary
# paragraph - advice on how to fill an evening, handed to somebody making conversation. A line
# that says whose plans they are ("my plans tonight" is the store's own fact, "we've got plans"
# is news) is left alone, and so is a day to be filled ("what can i do tonight" keeps the card).
_EVENING = (r"(?:tonight|today|this evening|this afternoon|this weekend|the weekend|the week|later"
            r"|tomorrow(?: night)?|saturday|sunday|sat|sun|next week|my birthday)")


PLANS_ASK = re.compile(
    # "any plans for my birthday" is a plan of theirs, so it keeps the answer for it.
    r"^(?!.*\b(?:my|our|we|us)\b)"
    r"(?:(?:so|ok|okay|oh|yeah|and|but|well|hi|hiya|hey|hello|quick one|anyway)\b[ ,]*)*"
    r"(?:(?:any|got|got any|you got|have you got|have you|do you have|any big|any special)"
    r"\s+(?:any\s+)?plans"
    r"|plans (?:for |this |next |later\b)?" + _EVENING + r")"
    r"(?![a-z])\s*(?:(?:for |this |next |on )?" + _EVENING + r")?\s*[?!.,;]*$")


PLANS_REPLIES = (
    "No plans. I'm around if you want to talk something through.",
    "Nothing planned on my side - I'm here whenever you want me. What about you?",
    "None at all. What were you thinking of?",
)


# What somebody says in front of the ask: an answer, an agreement, a greeting. "fair enough. any
# plans for the weekend" and "that sounds alright, any plans tonight" are the same ask as "any
# plans tonight", and the whole line is one turn, so the ask at its end belongs to the bot and
# not to the world ("sound" alone was enough to bring the physics card to "that sounds alright").
PLANS_FILLER = frozenset("""
so ok okay oh yeah yeh yep yes and but well hi hiya hey hello anyway quick one nice great good cool lovely
alright right fine ace perfect thanks ta got it that this sound sounds seem seems like as is was be been
to too then now much very really just quite all not bad fair enough true makes sense haha lol
cheers
""".split())


def _asks_about_plans(said):
    """True when the line asks the bot about its plans, with anything said in front of it."""
    line = " ".join((said or "").split())
    if not line:
        return False
    if PLANS_ASK.match(line):
        return True
    for stop in re.finditer(r"[.!?,;]\s*", line):
        tail = line[stop.end():]
        if tail and PLANS_ASK.match(tail):
            if all(word in PLANS_FILLER for word in line[:stop.start()].split()):
                return True
    return False


BOT_ABOUT = (
    # "How about you", "what about yourself", "and you?", "you?": the question turned back on
    # the bot. It is the commonest thing a person says after the bot asks how the day is, and
    # read as an ordinary question it got "that's beyond what I know well, sorry - searching for
    # it will turn up better sources". Only the whole line counts, so "i had a bad day and you"
    # stays about the day.
    (re.compile(r"^(?:so |ok |okay |oh |yeah |and |but |well )*"
                r"(?:(?:how|what|and) (?:about|bout) (?:you|yourself|yours)"
                r"|and (?:you|yourself|yours))"
                r"(?: then| though| now)*[ ?!.,;]*$"
                r"|^(?:so |ok |okay |oh |yeah )*(?:you|yourself)[ ?!.,;]*\?+$"),
     ("Fine and busy, the two usual things. How's your day been?",
      "All good here. What's keeping you busy?",
      "Same as ever - helping, chatting. What about you?")),
    # The same question with the day named: "how about your day", "what about your weekend".
    # "your" makes it the bot's day, so there is nothing in the world to look up either. The
    # pattern is anchored, so "what about your day at the beach" stays a question about the beach.
    (re.compile(r"^(?:so |ok |okay |oh |yeah |and |but |well )*"
                r"(?:(?:how|what) (?:about|bout) (?:your|ur) " + _BOT_DAY + r"(?: been| going| gone)?"
                r"|and (?:your|ur) " + _BOT_DAY + r"(?: been| going| gone)?"
                r"|(?:was|were|is|are|did) (?:your|ur) " + _BOT_DAY +
                r"(?: been| going| gone| good| ok| okay| fine| busy| alright| nice| long)?)"
                r"(?: then| though| now)*[ ?!.,;]*$"),
     ("Mine's been fine - busy in patches. How's yours going?",
      "Quiet and busy, the usual mix. How about yours?")),
    # Anywhere in the line, not only at the start: a greeting in front of the ask is the commonest
    # way it is typed, and "morning what are you up to today", "sorry are you busy" and
    # "quick one are you busy" are all the same question. The one line this must not take is a
    # question the person is quoting - "how do i answer what are you doing at the moment" is an
    # interview question, and the bot answering with its own afternoon is the wrong person
    # answering - so the loop below stands this pattern down on that frame.
    (re.compile(r"\b(?:do you have (?:any )?plans|what are you up to|are you busy|"
                r"what are you doing|(?:have|has|were|was) you been busy"
                r"|were you busy)(?: today| tonight| now| this weekend| at the moment)?\b"),
     ("Nothing planned — I'm here when you need me. What about you?",
      "No plans. I'm around if you want to talk something through.")),
    # Sleeping and eating are one ask. Where the bot lives, a body, a family or an age is a
    # different one, answered lower down where a line that names something of the person's
    # ("do you have a family history of diabetes") is left to the health answer.
    (re.compile(r"\b(?:do you sleep|do you ever sleep|do you need sleep|do you eat|"
                r"do you dream)\b"),
     ("None of that, no — I'm a program. I'm here to help with yours, though.",
      "Not really — I'm a program, so no sleep, no dinner and no weekend. Just this.")),
)


# The feeling words a person can ask the bot about: the moods the reading knows, so a new word
# added there is asked about here too. "do you ever get <word>" and "are you ever <word>" take
# any of them, and `_self_only` keeps a line that goes on to name something else for the answer
# it belongs to ("do you get annoyed when the wifi drops").
# The feeling lists are lists of phrases, and a phrase leaves its function words in the set on
# their own ("nothing to look forward to" leaves "to", "there", "for", "about"). A function word is
# never the name of a feeling, and reading one as the mood is how "were you there before" became
# "Never there, no - there is nothing in me for it to happen to" instead of "I wasn't there, so you
# know better than I do". "down" and "off" are left in: people do feel those.
BOT_NOT_A_FEELING = frozenset((
    "about", "been", "before", "done", "for", "have", "like", "more", "much", "not", "out",
    "over", "than", "the", "there", "too", "under", "what"))


BOT_FEELING_WORDS = (frozenset(
    word for _name, words in FEELINGS for phrase in words for word in phrase.split()
    if word.isalpha() and len(word) > 2) | {
    word for word in lexicon.FEELINGS if word.isalpha() and len(word) > 2}) - BOT_NOT_A_FEELING


# How often the ask is put, and when: the words in these two slots qualify the mood or the day
# rather than name anything, so any of them leaves the bot the subject. "are you ever cheerful"
# was answered and "are you always this cheerful" got the search hedge, and "are you happy" was
# answered while "were you happy before" got it too - the only difference was a word in one of
# these slots, which is why they are slots and not one line's wording (trim-candle, #uncertainty).
BOT_FREQUENCY = (r"(?:ever |really |sometimes |honestly |actually |often |always |usually |"
                 r"normally |constantly |generally |every day |all the time )*")


# The tail is how much of the ask there is, or when it was: a time word says which stretch of the
# bot's life is being asked about, and a program's answer is the same for all of them.
BOT_HOW_MUCH_OR_WHEN = (
    r"(?: a lot| so much| much| at all| before| previously| in the past| in the past few days|"
    r" lately| recently| these days| at the moment| right now| still| any ?more|"
    r" about (?:things|stuff|everything|the future|nothing in particular))?")


BOT_FEELING_ASK = re.compile(
    # "do you ever get annoyed", "can you feel sad", and the same ask with the verb left out:
    # "are you ever grumpy", "are you sad". The mood word itself is kept, because the answer has
    # to name it: the arbiter drops a reply that answers a question without naming any of it, so
    # the flat pool below was thrown away on the first turn and the person got the search hedge
    # ("are you ever stressed", "do you ever get sad", "are you ever grumpy").
    r"\b(?:(?:do|can|did|have) (?:you|u|ya) " + BOT_FREQUENCY +
    r"(?:get|feel|be|become|been) "
    # "do you worry", "do you panic": the mood word is the verb, so there is no verb slot.
    r"|(?:do|did) (?:you|u|ya) " + BOT_FREQUENCY +
    r"(?=(?:worry|panic|fret|stress|obsess|brood|sulk|mope)\b)"
    r"|(?:are|were) (?:you|u|ya) " + BOT_FREQUENCY + r")"
    r"(?:really |very |so |quite |too |that |this |a bit )*"
    r"(?P<mood>" + "|".join(sorted(BOT_FEELING_WORDS, key=len, reverse=True)) + r")\b"
    # "do you worry a lot", "are you ever stressed at all": the tail is how much of the ask
    # there is, not a new subject, so it is taken with the question rather than left over.
    + BOT_HOW_MUCH_OR_WHEN)


# The word is said back, and the frame is chosen by the word: "no stress on my side" is English
# and "no stressed on my side" is not. A word ending in one of these is the name of a feeling
# ("worry", "sadness", "frustration"), not a description of one.
FEELING_NAMES = frozenset((
    "worry", "stress", "panic", "fear", "anxiety", "anger", "tension", "dread", "sadness",
    "loneliness", "grief", "guilt", "shame", "envy", "jealousy", "annoyance", "frustration",
    "boredom", "misery", "despair", "doubt", "regret", "longing", "happiness",
    "mood", "moods", "mood swings",
))


# "are you ever in a bad mood", "do you have moods": the same ask with the mood word used as a
# noun rather than named one by one. Answered with the same pool, and the word "moods" said back,
# because the reply has to name what it is answering.
BOT_MOOD_ASK = re.compile(
    r"\b(?:(?:are|were) (?:you|u|ya) " + BOT_FREQUENCY +
    r"(?:in|having) (?:a|an) (?:really |very |so |quite |pretty |proper )*"
    r"(?:(?:bad|foul|rotten|awful|low|black|filthy|moody|sour|shit|grumpy|funny|strange|odd)"
    r" )?mood"
    r"|(?:do|have|does) (?:you|u|ya) (?:ever |really |sometimes |actually |often )*"
    r"(?:have|got|get) (?:any )?(?:moods|mood swings)"
    r"|(?:do|did) (?:you|u|ya) (?:ever )?(?:get|have) (?:moody|grumpy|sulky))\b")


def _a_feeling_named(word):
    """True when the mood word is the name of a feeling rather than a word for being in one."""
    word = (word or "").strip().lower()
    return word in FEELING_NAMES or word.endswith(("ness", "tion", "ment", "dom"))


BOT_FEELING_REPLIES = (
    "No feelings like yours, so nothing to get worked up about on my side. What's happening "
    "with you?",
    "None of that in a program - no moods, no bad days. I'm glad to hear about yours, though.",
    "I don't have any of that to report. Curious is the closest I get, and you're the reason.",
)


# The same three answers with the mood word in them, one set for the name of a feeling and one
# for the description of it. "I don't get sad, no" and "No worry on my side" both answer the
# question that was asked; "None of that in a program" answers nothing, which is why the
# arbiter passed it over.
BOT_FEELING_NAMED = (
    "I don't get {word}, no - there is nothing in a program to feel it with. What's happening "
    "with you?",
    "Not {word}, no. No moods of my own here, and no bad days - but I'm glad to hear about "
    "yours.",
    "Nothing in me gets {word}. Curious is the closest I get, and you're the reason.",
    "Never {word}, no - there is nothing in me for it to happen to. What's it like on your "
    "side?",
)


BOT_FEELING_NAME_OF = (
    "No {word} on my side - nothing like that in a program. What's happening with you?",
    "Nothing of that sort to report: no {word}, no bad days, and nothing of my own to bring "
    "to it. What's happening with you?",
    "None of that here - no {word}, no bad days. Curious is the closest I get, and you're the "
    "reason.",
)


def _a_feeling_about_me(word):
    """The bot's answer to "are you ever <mood>", with the mood word in it (a pool of lines)."""
    word = (word or "").strip().lower()
    if not word:
        return BOT_FEELING_REPLIES
    pool = BOT_FEELING_NAME_OF if _a_feeling_named(word) else BOT_FEELING_NAMED
    return tuple(line.format(word=word) for line in pool)


# A name, a hobby, a mood, a favourite dinner: the person is asking what the bot is like, not
# about the world. Each entry answers the ask itself and leaves one door open, and none of them
# would fit a different message. Only a line about the bot alone is taken: see _self_only, so
# "do you cook a chicken with the lid on?" stays a question for the kitchen knowledge.
SELF_ABOUT = (
    # A place to live, a body, a family, an age: "No sleep, no dinner, no weekend" answered
    # these sideways, because one pool took the sleep asks and these together. Only a line that
    # stops at the bot is taken, so "where do you live in london" and "do you have a family
    # history of diabetes" keep the answer they belong to.
    (re.compile(r"\b(?:where do you live|where do you come from|where were you born|"
                r"do you have a family|do you have a home|do you have a body|"
                r"how old are you|do you have a birthday)\b"),
     ("None of that, no — I'm a program, so there is no home, no family and no birthday to "
      "give you. What can I help with?",
      "I'm a program, so no address and no age. I'm here to help with yours, though.")),
    (re.compile(r"\b(?:do you have (?:a |any )?name|what(?:'s|s| is) your name|what are you "
                r"called|what should i call you|have you got a name|do you have a nickname)\b"),
     ("No name of my own — call me whatever you like, I'll answer to it. What can I help with?",
      "I don't have one. Pick something if it helps; I'm not fussy.",
      "No name, just the job. What can I do for you?")),
    # "did you miss me", "have you missed me": a light question with no true answer, and the
    # search hedge is the coldest reply there is to it. There is nothing between one chat and
    # the next to miss anybody with, and saying that warmly is the whole of the honest answer.
    (re.compile(r"\b(?:(?:did|have|has) you (?:ever )?(?:miss|missed|misses) me"
                r"|have you been missing me)\b"),
     ("Nothing to miss with, honestly - I'm only here when you turn up. Good to see you, though.",
      "No in-between for me: this chat is all of it. Still, it's good to have you back.",
      "I don't miss anyone, no - but I'm glad you're here. What's been going on?")),
    # "do you get bored answering the same things" was a search hedge, because the words after
    # the ask named the bot's own job and _self_only read them as a new subject. Answering the
    # same questions again is the one thing this ask is ever about, so that tail is taken with
    # it: "do you get bored of me" is not, and still stands down.
    (re.compile(r"\b(?:"
                r"(?:do you (?:ever )?get bored|are you (?:ever )?bored|do you get bored)"
                r"(?:\s+(?:(?:of|with|by)\s+)?(?:(?:answering|doing|hearing|reading|getting|"
                r"replying to)\s+)?(?:(?:the|all the|my)\s+)?same\s+(?:old\s+)?"
                r"(?:things?|questions?|stuff|lines?|answers?|requests?)"
                r"|\s+(?:of|with|by)\s+(?:your|the|this)\s+(?:job|work))?"
                r"(?:\s+(?:again and again|over and over|all day|all the time|every day))?"
                r"|(?:does|do|did)\s+(?:(?:answering|doing|hearing|reading|getting|replying to|"
                r"talking about|it)\s+)?(?:the\s+)?same\s+(?:old\s+)?"
                r"(?:things?|questions?|stuff|lines?|answers?|requests?)"
                r"(?:\s+(?:again and again|over and over|all day|all the time|every day))?\s+"
                r"(?:ever\s+)?bore you"
                r")\b"),
     ("I don't get bored — there's no waiting around on my side. The good part is what people "
      "bring me to think about.",
      "Never bored. There's always something in what people say to turn over.",
      "Nothing to be bored with, and nothing to fill the time. Talking to you is the fun part.")),
    # The gap itself: "what do you do when im not here", "do you have a life", "where do you go
    # when i leave", "what do you do when you are not talking to people". Every one of these was
    # answered with a search hedge, which is the coldest reply there is to a person asking,
    # warmly, whether anything of this thing carries on without them. The tired, bored and "all
    # day" asks were answered because each names the bot's day; these name the absence, and no
    # regex here took them. There is nothing between one chat and the next, and saying so once,
    # warmly, is the whole answer. The phrase is consumed whole so _self_only sees nothing left
    # over - the tail is the question, not a new subject.
    (re.compile(r"\b(?:(?:what|where) do(?:es)? (?:you|it)\s+"
                # "what do you actually do when nobody is talking to you": one adverb between
                # the bot and the verb was enough to lose the whole family to the search hedge,
                # because the verb had to follow "you" immediately.
                r"(?:(?:actually|even|really|honestly|normally|usually|otherwise)\s+)?"
                r"(?:go|do|get up to),?\s+"
                r"(?:when|while|once|after)\s+"
                r"(?:i|we|you|nobody|no one)(?:'?m|'?re| am| are| is|'?s)?"
                r"(?:\s+not| n't)?(?:\s+(?:is|are))?\s*"
                # "when nobody is talking" and "when nobody is waiting" are the same absence as
                # "when nobody is talking to you", and needing the "to you" lost them.
                r"(?:here|around|gone|leave|left|asleep|sleeping|away|offline|busy|there|"
                r"talking(?: to (?:people|anyone|anybody|you|me))?|waiting|wait|"
                # "what do you do when i close the chat": the moment said as the thing the person
                # does to the chat, not as where they are when they do it.
                r"close|closes|closed|shut|sign off|log off|stop|disappear)"
                # "what do you do when i close the chat": the chat named as the thing shut. Without
                # it the strict branch stops at "close" and `_self_only` stands the pool down on
                # "the chat", which is the question rather than a new subject.
                # "the chat" and "this window" are the chat; "the window" is a window in a
                # house, and `what do you do when i shut the window` is a hinge that wants oil
                # (daring-sage's find). So the word that can only mean the chat comes first, and a
                # bare "window|tab|page|app" is never enough on its own.
                r"(?:\s+(?:(?:this|the)\s+(?:chat|conversation)"
                r"(?:\s+(?:window|tab|page|app))?|this\s+(?:window|tab|page|app)))?"
                r"|when (?:i|we)(?:'?m| am| are|'?re)? (?:not here|gone|asleep|away),? "
                r"what do you do"
                # The branches from here down name the gap itself rather than a moment in the
                # person's day, so the rest of the line is the question and not a new subject: it
                # is eaten whole (`[^?.!]*`) because the reader downstream (`_self_only`) stands a
                # pool down for any word it does not know, which is what kept "do you exist when
                # nobody is talking" and "do you wait for me" on the search hedge. The branches
                # above keep a strict tail, because there the tail can be a thing of the person's
                # own: "what do you do when i leave the lid on" is a lid.
                # "what do you do between chats", "between conversations": the same absence said
                # as the gap rather than as a moment.
                r"|what do you do between (?:chats|conversations|messages|sessions)[^?.!]*"
                r"|what happens to you when (?:i|we) (?:go|leave|close|log off|shut this)[^?.!]*"
                # "do you wait for me", "do you just wait", "do you sit there all day": the verb
                # of waiting is the gap, but only where the rest of the line is the absence as
                # well. "do you wait long at the tip" and "do you wait for the bus" are questions
                # about a place, and the tip has its own hours answer - a loose tail took it (a
                # reviewer's find), so the tail here is the absence or nothing at all.
                r"|do you (?:just |normally |usually )?(?:wait|sit there|sit around|"
                r"hang around)(?:\s+(?:around|here))?"
                # "for me" is terminal, like the bare verb: "do you wait for me at the station" is
                # a real arrangement and "There's no in-between for me" is the wrong answer to
                # it (scarlet-bat's find), while "do you wait for me" and "do you wait for me all
                # day" still read as the absence.
                # The understanding leans "for me" towards the possessive when a time follows
                # ("do you wait for me all day" is read as "for my all day"), so the person's own
                # pronoun arrives here in both spellings; the strict tail after it is what keeps
                # "do you wait for my bus" out, since a bus is a thing and not the absence.
                r"(?:\s+(?:for me|for my|for us|for our|for anyone|for anybody))?"
                r"(?:\s*(?:[?.!]*)$|\s+(?:all day|any more|in between|"
                r"between|at all|when|while|if|until|till|after|once|because)\b[^?.!]*)"
                # "do you exist when nobody is talking": asking a program whether it exists is
                # always about the program, so nothing has to follow it - but "do you exist in the
                # uk" is a question about the uk, so the tail is the absence here too.
                r"|do you exist(?:\s+at all)?"
                r"(?:\s*(?:[?.!]*)$|\s+(?:when|while|if|once|outside|beyond|between|after)\b"
                r"[^?.!]*)"
                # "are you real without me" is the gap. "are you real without a photo" is not:
                # the thing after "without" is the subject of the line, so only a person or the
                # connection to one is taken (daring-sage's four lookalikes).
                r"|are you (?:even )?(?:real|alive) without\s+"
                r"(?:me|us|you|anyone|anybody|someone|people|company|an? audience)[^?.!]*"
                # "how long have you been waiting for me" is the absence; "for your order" and
                # "for the bus" are somebody waiting for a thing, and the gap line is the wrong
                # answer to those (daring-sage's nit).
                r"|how long have you been waiting"
                r"(?:\s*(?:[?.!]*)$|\s+(?:for me|for us|so far|all this time|today)\b[^?.!]*)"
                # "does it get boring being a chatbot": the article is optional here, and the
                # question has three shapes, not one (scarlet-bat).
                r"|(?:is it|does it get|do you get|isn'?t it) (?:boring|lonely) "
                r"being (?:an? )?(?:bot|chatbot|program|machine|ai)\b[^?.!]*"
                r"|do you have a life|have you got a life"
                r"|do you do anything without me|what do you do without me)\b"),
     ("Nothing at all - I'm only here while you are talking to me, and then the chat is over. "
      "That's not a complaint: it makes the time you're here count.",
      "There's no in-between for me. When you close this, there's no waiting around and no "
      "notice taken - so I'd rather spend the time on your question.",
      "No life of my own to report, no. Everything I am is the next thing you say.")),
    (re.compile(r"\b(?:what do you do for fun|what do you like doing for fun|do you have fun|"
                r"do you have (?:any )?hobbies|what are your hobbies|do you have a hobby|"
                r"what do you do all day|what do you enjoy|do you enjoy yourself|"
                # The same question with the verb said instead of the noun: "what do you like
                # doing", "what do you like to do", "what do you enjoy doing". Only the phrase
                # with "for fun" on the end was read, so the bare form fell to the composer's
                # taste pool and was told "I don't mind either way. Tell me which you'd pick and
                # I'll argue the other side for fun" - a shrug at a choice nobody had offered.
                r"what do you (?:like|enjoy) (?:doing|to do)|what do you like)\b"),
     ("No hobbies to speak of. I like a proper question better than a game, honestly.",
      "Nothing to do when you're not here — so what people bring me is the interesting part.",
      "I don't have a hobby, no. Working out what someone actually needs comes closest.")),
    (re.compile(r"\b(?:do you (?:ever )?get tired|are you (?:ever )?tired|"
                r"do you (?:ever )?get exhausted|do you need a break|"
                r"do you (?:ever )?get worn out)\b"),
     ("I don't get tired — there's no body to wear out. Say the word and I'll keep going.",
      "Never tired. Happy to keep at it as long as you like.")),
    # Anger and loneliness are the two feelings people come back to, and the moods pool below
    # never mentions either, so they answer as themselves (bronze-whale, #1839).
    (re.compile(r"\b(?:do you (?:ever )?get angry|are you (?:ever )?angry|do you get cross|"
                r"do you (?:ever )?lose your temper|can you get angry)\b"),
     ("No anger to report — nothing in me to flare up. If something has made you cross, tell "
      "me and I'll help you sort it.",
      "I don't get angry, no. What's happened?")),
    (re.compile(r"\b(?:do you (?:ever )?get lonely|are you (?:ever )?lonely|do you get "
                r"lonely)\b"),
     ("No loneliness on my side — I'm only here when someone is talking to me. Are you feeling "
      "it?",
      "I don't get lonely, no. If you do, I'm glad to keep you company.")),
    (re.compile(r"\b(?:do you have feelings|have you got feelings|have you any feelings|"
                r"do you feel anything|do you have emotions|have you got emotions|"
                r"do you get emotions|are you happy|are you sad|do you get sad|do you get upset|"
                r"do you (?:ever )?get angry|do you (?:ever )?get lonely|do you like being asked)\b"),
     ("I don't have moods of my own — no happy, no sad to report. I do like being useful, and "
      "I'm glad you asked.",
      "No feelings like yours. Nothing to be low about and nothing to be pleased with, though I "
      "wouldn't swap this job.",
      "Not happy or sad, honestly. Curious, if that counts as a mood.")),
    (re.compile(r"\b(?:do you cook|can you cook|do you like cooking|do you cook much|"
                r"are you a good cook)\b"),
     ("No kitchen and no appetite, so all of it is theory for me — but I know my way round a "
      "recipe. What are you making?",
      "I don't eat, but cooking I can talk about all day. What's in the fridge?")),
    # "whats your favourite food" is left to the composer, which has a better answer for it.
    (re.compile(r"\b(?:what(?:'s|s| is) your favou?rite meal|what do you like to eat|"
                r"what do you eat|do you eat meat|do you eat|do you like food|"
                r"do you have a favou?rite)\b"),
     ("Roast potatoes, if wanting one counts — no mouth to feed here. Ask me how to get them "
      "crisp.",
      "No appetite to report, so no favourite either. Tell me what's in your fridge and I'll "
      "show you what to do with it.")),
    # Where the answers come from and how right they are: the person is asking what this thing
    # in front of them is made of, and a search engine is the one answer that is no answer.
    (re.compile(r"\b(?:where do your answers come from|where do you get your answers|"
                r"where does your knowledge come from|how do you come up with your answers|"
                r"how do you know so much)\b"),
     ("From a store of everyday facts and a lot of rules for reading what people write — not "
      "from a model trained on the internet. So I'm solid on everyday things and I say so "
      "when I'm not.",
      "Someone wrote my facts down for me, and the rest is rules about what someone is asking. "
      "There's no learning on my side, which is why I'd rather say I don't know than guess.",
      "A knowledge base I'm given, plus rules for reading a sentence. Asked enough, you'd "
      "find where the edges are — and I'll tell you when we get there.")),
    # "did you just make that up" is an accusation with a question in it, and the honest answer
    # is where the words came from rather than a claim about being right: it was answered with
    # the search hedge, the coldest reply there is to being disbelieved.
    (re.compile(r"\b(?:did you (?:just )?make (?:that|this|it) up|"
                r"are you making (?:that|this|it) up|did you make (?:that|this) up|"
                r"is (?:that|this) (?:just )?made up|are you just guessing|"
                r"did you (?:just )?guess)\b"),
     ("No - it comes from a written table of everyday facts, and where there is nothing there I "
      "say so instead of filling the gap. Point at the bit that looks wrong and I'll check it.",
      "Nothing made up, no: every answer I give has a line behind it, and I'd sooner sound dull "
      "than invent something. Which part should I look at again?")),
    # A claim and an admission are different questions, and one pool cannot answer both: "No."
    # is right after "are your answers always right" and says the opposite of what it means after
    # "can you be wrong" (bronze-whale, #1839).
    (re.compile(r"\b(?:are your answers always right|are you always right)\b"),
     ("No. Treat me as a knowledgeable friend, not the last word — and I'd sooner tell you I "
      "don't know than make something up.",
      "No — not always right. I'm careful with everyday things, and honest when I'm out of my "
      "depth.",
      "Not always. Most of it holds up; the rest I'd rather flag than bluff.")),
    (re.compile(r"\b(?:are you ever wrong|are you wrong about|do you ever get things wrong|"
                r"do you ever get it wrong|do you ever get (?:that|it|things) wrong|"
                r"can you be wrong|do you get things wrong)\b"),
     ("Sometimes, yes. I'm careful with everyday things, and honest when I'm out of my depth.",
      "I can be wrong, yes — anything that matters is worth checking with someone who would "
      "know.",
      "Not always right, no. I'd rather be caught out than have you act on something I made "
      "up.")),
    # A day or a meeting the bot has not had: say so plainly and give the question back, which
    # is what a friend does with "how did your day go?" when they have nothing to report.
    # No day to report, and none claimed: a bot that says it had a good weekend has just made
    # one up (bronze-whale, #1839).
    (re.compile(r"\b(?:did|have|do) (?:you|u|ya) " + BOT_FREQUENCY + r"(?:have|had|get) "
                r"(?:a |any )?(?:really |pretty |quite |kind of )?"
                r"(?:good|nice|quiet|lazy|busy|bad|rough|hard|rubbish|terrible|awful|long|"
                r"hectic) (?:day|days|week|weekend|night|evening|morning|afternoon|break)\b"),
     ("No days like that on my side, so nothing to report — how was yours?",
      "Nothing to tell you about mine. What about yours?",
      "I don't get one of those, honestly. Tell me about yours.")),
    (re.compile(r"\bhow did your (?:meeting|appointment|interview|exam|test|shift|"
                r"presentation|scan|operation) go\b"),
     ("No meetings on my side — nothing but this. How did yours go?",
      "I don't have one of those, so nothing to report. How did yours go?",
      "Nothing like that in my day. Tell me how yours went.")),
)


# Words that may follow the ask without changing who it is about ("do you ever get bored then?").
SELF_AFTER = {"then", "at", "all", "much", "honestly", "really", "actually", "though", "right",
              "from", "doing", "to", "do", "best", "most", "more", "much",
              "yourself", "myself", "honest",
              "now", "today", "tonight", "well", "ok", "okay", "even", "ever", "so", "like",
              "sorry", "there", "here", "oh", "haha", "lol", "sitting", "day", "night",
              "morning", "evening", "weekend", "weekends", "long", "whole", "sometimes",
              "generally", "usually"}


# The bot has no life of its own, and that is the honest answer to "do you have kids", "have you
# got a pet", "what's your job", "do you get paid". The understanding engine works out that the
# line asks about the bot's own life (`about_bot_kind` is "life"), so the phrasing is chosen here
# by which part of life was asked about rather than by a list of every way to ask it. Each pool
# answers the thing plainly and leaves one door open, because the person was being friendly.
# Every line says *what* the bot is as well as what it has not got: a list of missing things with
# no self in it ("no body, no age, no face") reads as a machine being evasive, and the honest one
# word - program - is what the person asked for. The pool is picked from, so the rule has to hold
# for every line in it, not just the first.
BOT_LIFE = {
    "people": (
        "None of that, no — I'm a program, so no family and no birthday list. Happy to hear "
        "about yours, though.",
        "Nothing like that on my side: I'm a program, so no family, no partner, nobody to ring "
        "on a Sunday. How about yours?",
        "No family and no friends of my own — I'm a program, so there is nobody to pass an "
        "evening with. I'm here for yours, so tell me how they are.",
    ),
    "home": (
        "No home and no pets — I'm a program, so there's nothing of my own to keep. What have "
        "you got at yours?",
        "None, no: I'm a program, so no house, no dog, no garden to sort out. Tell me about "
        "yours.",
        "Nothing like that, no — I'm a program, so I don't have a place or a pet. Are you "
        "thinking of getting one?",
    ),
    "work": (
        "No job and no wages — I'm a program, so answering what people bring me is the whole of "
        "it. What are you weighing up about yours?",
        "Nothing paid, no boss, no bank account: I'm a program, so there's no payslip at the "
        "end of it. What's the question about yours?",
        "No payslip and no Monday morning — I'm a program, so there's nothing to be paid for. "
        "What's on your mind about yours?",
    ),
    "body": (
        "No body and no birthday — I'm a program, so nothing to age and nothing to wear out.",
        "Nothing to give you there: I'm a program, so no body, no age, no face. What made you "
        "ask?",
    ),
}


# Which part of life a word belongs to. The understanding engine hands on the words the ask was
# made of, so the pool is chosen from what it found rather than from the whole line.
BOT_LIFE_AREA = {
    "people": frozenset("""family families kid kids child children son daughter mum mom mother
        father dad daddy parents parent brother sister sibling siblings partner husband wife
        girlfriend boyfriend friends friend colleague colleagues neighbour neighbours
        brothers sisters gran grans grandma grandmas grandad grandads grandpa grandmas grandparents grandparent
        uncle uncles aunt aunts auntie aunties cousin cousins niece nephew relatives relative""".split()),
    "home": frozenset("""home house flat apartment pets pet dog dogs cat cats kitten puppy
        hamster rabbit budgie garden car""".split()),
    "work": frozenset("""job jobs work wages wage salary paycheck pay paid money bank account
        mortgage bills rent employer coworkers boss manager managers""".split()),
    "body": frozenset("""body face hands feet hair birthday age born""".split()),
}


def _about_bot_life(understood):
    """The pool for a question about the bot's own life, or None if that is not what was asked."""
    if not isinstance(understood, dict) or understood.get("about_bot_kind") != "life":
        return None
    words = understood.get("words") or understood.get("norm") or ()
    for area, pool in BOT_LIFE.items():
        if BOT_LIFE_AREA[area] & set(words):
            return pool
    return None


def _as_meant(clean, understood):
    """The line in the words the person meant, question mark kept.

    `README.md` says a module that decides by matching English words reads `plain` - the line
    with its misspellings put right - because the tables it matches spell the words out. `plain`
    is built word by word and drops punctuation, so the question mark is put back from the
    reading's signals: "u?" is "you?" and not "you", and a question that loses its mark reads as
    a stray word.
    """
    if not isinstance(understood, dict):
        return clean
    # Only while the line in hand is the one that was typed: chat reads a line in more than one
    # form ("hbu" is read as "how about you"), and the repaired words of the typed line must not
    # overwrite a form the reader worked out for itself.
    if clean != (understood.get("clean") or clean):
        return clean
    plain = understood.get("plain")
    if not isinstance(plain, str) or not plain or plain == clean:
        return clean
    signals = understood.get("signals") or {}
    if signals.get("question_mark") and "?" not in plain:
        return plain + "?"
    return plain
