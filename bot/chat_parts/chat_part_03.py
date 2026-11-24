"""Part 3 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import badnews
from ..compose import limit as limit_line


from ..memory import limit
from ..knowledge import lookup
from .chat_part_02 import (
    NEWS_REPLIES,
)


def _asked_about_the_effort(memory):
    """Whether the bot's last turn was the question this line is answering.

    The pools are read here rather than at the top of the file, because the replies they hold are
    written further down it.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not turns or not isinstance(turns[-1], dict):
        return False
    said = turns[-1].get("bot") or ""
    for kind in ("at_it", "on_a_form", "on_the_thing", "the_long_haul"):
        if said in NEWS_REPLIES.get(kind, ()):
            return True
    return False


# The two pools above are `chat` handing a decision back rather than answering the line: they say
# the choice is the person's and ask what matters to them. That is the right reply to "is that a
# good idea" on its own - it is better than the pool that signed the person off - but it is not an
# answer to the line, so the arbiter is told which replies read that way and does not let one win
# the turn off a module that said something about the thing (see
# `arbiter._a_real_answer_besides`). The patterns are cut from the pools themselves, so the
# declaration and the wording cannot drift, and a pool that gains a hand-back needs no change in
# the arbiter.
def _as_a_pattern(line):
    """One pool line as a pattern, its `{placeholders}` matching anything."""
    out = []
    for part in re.split(r"(\{[A-Za-z_]+\})", line):
        if part.startswith("{") and part.endswith("}"):
            out.append(".+")
        elif part:
            out.append(re.escape(part))
    return re.compile("".join(out))


HANDS_IT_BACK = tuple(_as_a_pattern(line)
                      for kind in ("judged", "judged_bare")
                      for line in NEWS_REPLIES[kind])


def hands_it_back(reply):
    """True when the reply is one of the pools above: a decision handed back, not answered."""
    said = str(reply or "").strip()
    return any(pattern.fullmatch(said) for pattern in HANDS_IT_BACK)


POSITIVE = {"good", "fine", "great", "ok", "okay", "alright", "nice", "well", "smile", "yay",
            "brilliant", "lovely", "cool", "sweet", "perfect",
            # The same words as ACK_WORDS below: a line that is only these and "im" is how the
            # person is, so it gets the plain "Glad to hear it." that "im good" gets.
            "grand", "chill", "content", "mint", "brill", "sound"}


FEELINGS = (
    ("tired", ("tired", "exhausted", "knackered", "shattered", "wiped", "sleepy", "bushed",
               "drained", "shattered", "done in", "no energy", "worn out",
               # The same tiredness said of the thing that caused it: "my job is exhausting",
               # "the commute is draining", "the week has been tiring". The word names what the
               # thing does to the person, so it is read here beside "worn out" - see
               # HARD_ON_THE_PERSON for the shape the line has to have.
               "exhausting", "draining", "tiring", "knackering", "wearing out",
               # "im beat", "im spent", "im zonked", "im pooped" and "im dead on my feet" are the
               # same passing tiredness as "im knackered": all five used to be read as an
               # introduction ("Nice to meet you, Beat.") or as an ache in the feet
               "beat", "spent", "zonked", "pooped", "dead on my feet",
               # "im fagged" and "im wrecked" are the same tiredness in the words people use
               # at the end of a day; "wrecked" is also said of a thing ("the car is wrecked"),
               # which `_says_how_the_person_is` keeps apart. Not here: "whacked" ("i whacked
               # my head on the cupboard" came out as tiredness), "frazzled" (already read as
               # its own feeling) and "cream crackered" (the rough-day pool answers it better).
               "fagged", "wrecked",
               # The same tiredness said as a phrase rather than one adjective. "im worn down",
               # "im used up" and "i feel like a zombie" were answered with the coldest line the
               # bot has ("I'm listening - say more if it helps") because the table only held
               # single words, and a person who says how they feel and gets nothing back says no
               # more. Not here: "washed out", which is mostly said after an illness, where the
               # recovery entry answers it better.
               "worn down", "used up", "like a zombie", "a zombie", "zombie")),
    # The morning after, and the other ways of saying "I am not well today". They are a state and
    # not a mood, and the pool that fits them is the rough-day one: water, food and an early
    # night. Before the fix these lines were read as an introduction ("Nice to meet you,
    # Hungover") or answered with "Got it. Is there anything you'd like a hand with?", which says
    # nothing back to someone who has just said they feel awful. After the tired group, because a
    # correction says both: "im not hungover just tired" is the tired line.
    ("rough_day", ("hungover", "hangover", "hang over", "hung over", "jet lagged", "jetlagged",
                   "jet lag", "cream crackered", "crackered")),
    ("stressed", ("stressed", "stress", "overwhelmed", "swamped", "under pressure", "too much on",
                  "pulled in every direction", "snowed under",
                  # Again the cause rather than the feeling: "work is stressful at the moment",
                  # "work is overwhelming". "hectic" and "full on" stay out, because BUSY_WORK
                  # answers those with the busy pool, which is the better reply.
                  "stressful", "overwhelming")),
    ("anxious", ("anxious", "anxiety", "nervous", "worried", "worry", "wound up", "on edge",
                 "panicking", "panic", "scared", "frightened", "restless",
                 # The same fear said as strong as it comes. "scared" and "frightened" were here
                 # and "terrified" was not, so "im terrified" named no feeling at all and fell to
                 # the stock nod, and "im excited and terrified" was read as the excitement.
                 "terrified", "petrified")),
    ("sad", ("sad", "down", "miserable", "low", "upset", "heartbroken", "gutted", "crying",
             "unhappy", "depressed", "not ok", "not okay", "not doing great", "not great",
             # The same denial in the words people reach for most: a good word about themselves
             # with a "not" in front is the low, not a refusal, so it is read here rather than
             # left to the plain "no" reply - "im not fine" was getting "No worries - say if you
             # change your mind", which answers a person who turned an offer down.
             "not fine", "not alright", "not so good", "not doing well", "not feeling great",
             "weepy", "tearful", "homesick", "rotten", "lousy", "meh", "rough", "crap",
             "rubbish", "numb",
             # The degrees of the same feeling, so "im sadder than i was last week" is answered
             # as the low it is rather than as an unnamed state.
             "sadder", "saddest", "more miserable", "worse than before",
             # The tears said as a verb, a state or an event: "i keep weeping", "i keep sobbing",
             # "i keep bursting into tears", "i keep welling up", "i keep having a cry" say the
             # same low that "i keep crying" says - and only "crying" was a word here, so the
             # others were read as nothing at all: "i keep weeping" got a shrug and "i keep
             # bursting into tears" got the routine reply for a thing that keeps happening
             # ("Annoying. Is it the same every time?") while the person was telling us about
             # their tears. The words are the family the weeping rule already knows
             # (WANT_TO_WEEP below), so both sides read the same line the same way.
             "cry", "cried", "cries", "weep", "weeping", "wept", "sobs", "weeps",
             "sob", "sobbing",
             "bawl", "bawling", "blub", "blubbing", "tears", "in tears", "welling up",
             "burst into tears", "bursting into tears", "tearing up", "tear up", "choked up",
             # The words for a low day that are not feeling adjectives: what is missing, what a
             # person says they are, and the mood said as a thing. "im flat" and "im hollow"
             # were read as an introduction ("Nice to meet you, Flat") and "im in a bad mood"
             # got "Noted!", because none of these is a word a sentence uses for its ending.
             "empty", "flat", "hollow", "blank", "dead inside", "nothing to give",
             "feel nothing", "like a failure", "like a mess", "like rubbish", "like crap",
             "like a burden", "like a fraud", "like nothing matters", "a mess",
             "in a bad mood", "in a low mood", "in a foul mood", "in a mood",
             "in a state", "in a right state", "out of sorts", "not myself",
             "not feeling myself", "off colour", "off form")),
    # The "feel X about" phrases are the same words GUILT_WORD holds further down, because a
    # regret said with "terrible" is the same regret as one said with "bad": "i feel terrible
    # about it" was missing here and got the flat "I'm sorry - that's frustrating" instead of the
    # guilt reply, while "i feel bad about it" got it.
    ("guilty", ("guilty", "ashamed", "embarrassed", "my fault", "feel bad about",
                "feel awful about", "feel terrible about", "feel dreadful about",
                "feel horrible about",
                "let them down", "let her down", "let him down",
                "let my family down", "should have been there", "wasnt there enough")),
    ("lonely", ("lonely", "alone", "isolated", "left out", "no one to talk to", "on my own")),
    # Being taken for granted is not the annoyed pool's quarrel ("cool off before replying to
    # whoever caused it"), and it is not loneliness either. Said as a phrase it was read by
    # nothing at all, and the line got "Got it. Is there anything you'd like a hand with?" - the
    # coldest thing the bot says, to a person who has just said something sore.
    ("unappreciated", ("taken for granted", "not appreciated", "unappreciated")),
    ("bored", ("bored", "boring", "nothing to do", "nothing to do")),
    ("annoyed", ("annoyed", "angry", "furious", "pissed", "irritated", "frustrated", "fed up",
                 "cross", "livid", "raging", "mad", "grumpy", "cheesed off",
                 "fuming", "miffed",
                 # "im mardy" was read as a name ("Nice to meet you, Mardy"): it is the northern
                 # word for grumpy, and it is nobody's introduction.
                 "mardy",
                 # The same worn-down words in the third person. The fed-up branch below keeps
                 # their first-person replies, but a line about somebody else ("my husband is
                 # browned off", "she is peeved") only reaches a feeling here, and without the
                 # words it was an echo: "Noted: your husband is browned off."
                 "browned off", "peeved",
                 # "stroppy" was in no list, so "im stroppy" got "Got it. Is there anything
                 # you'd like a hand with?" while "im mardy" and "im grumpy" were answered.
                 "stroppy", "stroppy with", "in a huff")),
    # A weight coming off is good news of a kind, and it is not an occasion. While "relieved" sat
    # in the happy group, "im relieved hes gone" and "my scan came back clear and im so relieved"
    # both got "Love that. Anything nice planned to go with it?" - a question about a party nobody
    # mentioned, asked about a death. The pool of its own says the relief back and asks what it
    # was, which fits the scan that came back clear as well as the long illness that is over.
    ("relieved", ("relieved", "relief", "such a relief", "what a relief",
                   "weight off my shoulders", "weight off my mind")),
    ("happy", ("happy", "great", "glad", "excited", "thrilled", "chuffed",
               "delighted", "buzzing", "made up", "over the moon", "brilliant news",
               # A good mood said without a feeling word in it: "im in a good mood", "life is
               # good", "feeling good", "cheerful today". Without these the line was filed as a
               # fact and said back - "You're in a good mood - noted." - which is not an answer
               # to anything.
               "good mood", "feeling good", "feel good", "in good form", "on good form",
               "cheerful", "cheery", "in a great mood", "great mood",
               # The degrees of the same feeling. "im happier" and "im happiest" name no feeling
               # above, so both fell to the stock nod, and "im happier" used to be read as
               # somebody called Happier before the state reading took it back.
               "happier", "happiest", "gladder", "gladdest")),
)


# "low" and "high" are also dials, prices and batteries ("ok so low heat then", "the battery is
# low"), and the lead word "so" is loose enough to open a mood frame around them. A line whose
# "low" names a thing is not a line about how someone feels.
# "flat out" is a full week and "flat broke" is no money: the idiom, not the mood. It is taken
# out before a feeling word is looked for, the way a "low battery" is.
FLAT_IDIOM = re.compile(r"\bflat\s+(?:out|broke)\b|\bflat as (?:a|an) \w+")


# The good word is in the line and the rest of it says the good thing did not land: "i should be
# happy but im not", "i got the job and i dont feel happy", "i feel nothing". `negated` reads a
# negator in front of the word and "i should be happy" has none, so the line reached the pool for
# good news - "That's great news! Make the most of it." to a person saying it had not landed. The
# "but" clause has to be about how they feel, so "i passed but i dont have a car" is not read as
# a low, and a line that names a thing to be unhappy about is the complaint path below, not this.
NOT_LANDED = re.compile(
    r"\bbut\s+(?:i\s*'?m|im|i\s+am)\s+(?:not|n'?t)\b"
    r"|\bbut\s+i\s+(?:still\s+)?(?:don'?t|do\s+not|didnt|didn'?t)\s+(?:feel|felt)"
    r"\s+(?:it|that|anything|nothing|happy|glad|excited)\b"
    r"|\b(?:don'?t|do\s+not|didnt|didn'?t)\s+feel\s+(?:anything|nothing|it|happy|glad|excited)\b"
    r"|\bfeel(?:ing)?\s+(?:nothing|flat|numb|empty)\b")


# The words that say the user is telling us about news, without saying which: "great news" and
# "good news" are the phrase, and the branch that used to read them raw congratulated the line
# "i feel nothing after good news". Kept beside `NOT_LANDED` because the two are read together.
GOOD_NEWS_SAID = re.compile(
    r"\b(?:great|good|brilliant|amazing|wonderful|excellent|fantastic)\s+news\b")


# "any news on the strikes" is a request for the day's news about a thing, not small talk: the
# no_news pool below is the bot saying it has looked and found nothing, which it cannot know, and
# the composer's news reader says where the news lives instead. Their own news keeps the pool -
# "any news about my son", "any news on my refund" - because `LIVE_NOT_WORLDS` is the same reader's
# list of what a news site cannot answer (sky-turkey, on #7712).
ANY_WORLD_NEWS_ON = re.compile(r"\bany\s+news\s+(?:on|about|of)\s+\w")


# The good feeling words a person denies in front of the news: "im not happy about the good news".
NOT_GLAD_WORDS = ("happy", "glad", "pleased", "excited", "thrilled", "relieved")


# "bit of a mad one, my sister is coming to stay" is how people open with news: the "one" is the
# thing they are about to tell you, not the day they had, so the word in it is not their mood.
# "its been a mad one" has no "bit of a" and keeps the rough-day reading it deserves. "what a
# mad one" is not here: with nothing after it, it is the day they had ("what a mad one" after a
# shift), and the same three words cannot say which it is, so it keeps the mood reading.
ANNOUNCED_ONE = re.compile(r"\b(?:bit of a|a bit of a|a right|a proper)\s+"
                           r"(?:mad|weird|strange|funny|odd|daft|curious)\s+one\b")


# An opener is only a softener when there is news after it, and news names a thing or a person
# ("my boiler", "the bus", "my sister"). "bit of a mad one today", "bit of a mad one honestly"
# and "a proper mad one, i barely slept" have nothing of the sort after them: there is nothing to
# soften, so the opener is the day they had and "Rough one" is the answer that fits.
NEWS_AFTER = re.compile(r"\b(?:my|our|his|her|their|the|this|that|these|those|your)\s+[a-z]",
                        re.I)


# "im not myself", "i dont feel like myself", "i havent felt myself": the same low day, said as
# the absence of the person they are. Only the speaker's own - "my mum is not herself" is about
# her - so a first-person start is part of the pattern.
# "do you ever feel empty", "are you in a bad mood": the mood asked about is the bot's, not the
# speaker's, so the low-day reply would answer the wrong person.
ASKED_ABOUT_THE_BOT = re.compile(r"\b(?:do|are|were|have|has|did|can|could|would|will) "
                                 r"(?:you|u|ya)\b")


# "i feel like such a failure": a scale word between "like" and the thing a person calls
# themselves, which the plain phrase list does not reach.
SELF_INSULT = re.compile(r"\blike (?:such |a bit of |a total |a complete |an absolute |an utter |"
                         r"a right |kind of |sort of )?a (?:failure|mess|burden|fraud|waste|"
                         r"letdown|loser|nobody)\b")


# "in a mood for pizza" is an appetite, not a mood.
MOOD_FOR = re.compile(r"\bin (?:a|the) mood for\b")


NOT_MYSELF = re.compile(r"\b(?:im|i'm|i am|i)(?:\s+\w+){0,3}\s+(?:not|never|dont|didnt|havent|"
                        r"hasnt)\s+(?:\w+\s+){0,2}myself\b")


# Words that are an everyday noun as well as a state: "a flat", "an empty shelf", "a blank
# page". A determiner in front of one of these makes it the thing, not how the speaker feels,
# which is what keeps "im looking for a flat" out of the low-day reply.
THING_WORDS = frozenset("flat empty blank hollow numb".split())


def _a_thing_in_front(clean, word):
    """True when a determiner sits in front of this word: "a flat", "an empty one"."""
    if word not in THING_WORDS:
        return False
    at = clean.find(word)
    return bool(re.search(r"\b(?:a|an|the|this|that|my|your|our|their|his|her|its|any|no|another)"
                          r"\s+$", clean[:at]))


# "spent" is money as well as tiredness: "spent up", "spent all my money", "spent my wages".
SPENT_MONEY = re.compile(r"\bspent\s+(?:up|all|it|my|the|every|so\s+much)\b")


LOW_THING = re.compile(r"\b(?:low|high)\s+(?:heat|light|lighting|flame|setting|settings|"
                       r"temperature|temp|battery|charge|power|price|prices|cost|costs|rate|rates|"
                       r"speed|volume|sun|sugar|stock|budget|income|rent|wages|pressure|mileage|"
                       r"salt|fat|calories)\b")


# A tiredness that says when, or asks why, is a question about the cause, and the knowledge base
# has the entry for exactly that ("most constant tiredness is dull rather than medical ..."). The
# pool under "tired" is for a passing "im knackered", so a line with a recurrence in it is left to
# the entry that answers it: "im always knackered" got "Long one? Give yourself half an hour doing
# nothing before the next thing", which is advice for a hard afternoon.
TIRED_PERSISTENT = re.compile(
    r"\b(?:all (?:the time|day|week)|always|constantly|every ?day|every morning|each morning|"
    r"for (?:weeks|months|years)|these days|lately|recently|"
    r"no matter how much (?:i )?sleep|even after (?:a|my|sleeping)|"
    r"keep (?:falling asleep|getting|waking)|"
    r"(?:i )?(?:dont|do not|can'?t|cant) (?:know )?why|why am i|why do i|why is it|"
    # "is that why i feel wrecked" and "is it because i slept badly" ask for the cause rather
    # than saying how they are, so the same entry answers them and the passing pool does not.
    r"is (?:that|it|this) (?:why|because))\b")


# "i sleep 8 hours and im still tired" is the same question with the reason in it, and the entry
# answers it; "im still tired" on its own is the passing feeling the pool is for, so the sleep word
# has to be there too.
TIRED_DESPITE_SLEEP = re.compile(
    r"\bstill\s+(?:tired|exhausted|knackered|shattered|wiped out|drained)\b")


SLEEP_WORD = re.compile(r"\b(?:sleep|sleeping|slept|hours|nights?)\b")


# The gerunds that name something a person can feel guilt about. "about going to the dentist",
# "about getting a filling" and "about seeing him" are things ahead of them, not deeds, so a list
# beats "any word ending in -ing": the act has to be one you could apologise for.
ACT_GERUND = (r"(?:lying|cancell?ing|shouting|yelling|snapping|ignoring|forgetting|missing|"
              r"hurting|upsetting|breaking|cheating|stealing|taking|quitting|leaving|blaming|"
              r"criticis?ing|arguing|fighting|drinking|smoking|spending|eating|letting)")


IRREGULAR_DEED = (r"forgot|said|told|broke|ate|spent|let|left|made|took|went|drank|bought|sold|"
                  r"threw|woke|spoke|swore|drove|flew|kept|stood|ran|hid|lost|slept|bit|hit")


# "for not picking up" is a deed by its own shape: leaving a thing undone is what the person is
# holding against themselves, whatever the verb is. A plain gerund still has to be an act.
DEED_TAIL = (r"(?:about|for|over)\s+(?:not\s+[a-z]+ing\b|" + ACT_GERUND + r"\b)"
             r"|that\s+i\s+(?:[a-z]+ed\b|" + IRREGULAR_DEED + r")")


# Guilt is about a deed, not a thing: "i feel bad for not picking up" and "i feel terrible
# about cancelling" are guilt, while "i feel bad" is how the person feels in their body and "i
# feel bad for her" is sympathy for someone else. So a feeling word from the guilt family counts
# when a deed follows it, and only then: a gerund ("about cancelling") or the person's own
# clause ("that i forgot").
GUILT_WORD = (r"(?:bad|awful|terrible|rotten|dreadful|horrible|guilty|ashamed)")


GUILT_DEED = re.compile(
    r"\b(?:feel|feels|feeling|felt|feelin)\s+(?:so |really |very |a bit |bad |quite |pretty |"
    r"kind of |kinda |honestly |still )*" + GUILT_WORD + r"\s+(?:" + DEED_TAIL + r")")


# The illness pool answers "i feel sick" before any mood is read, so the two shapes that can
# only be guilt are kept apart from it: the person's own clause about something they did ("that i
# lied to her") and a thing they left undone ("about not going to her party"). A plain gerund
# ("about going to the dentist tomorrow") stays with the body, because it is dread of what is
# ahead, not a deed.
# Regret puts its deed in the object, so the guilt family's "feel bad about" shape never sees
# it: "i regret what i said" and "i regret telling her" were answered with the neutral filing
# line ("Thanks for telling me - I'm here if you want to dig into any of that"), which is the one
# reply that does nothing for someone who has just said they wish they had not done a thing.
# Only a deed to somebody counts. Regret about a choice - "i regret not going", "i regret moving
# here" - is not a confession, and "say it out loud to one person you trust" would be telling
# them to own up to a decision.
REGRET_DEED = re.compile(
    r"\bi\s+(?:really |so |genuinely |still |deeply |truly |honestly )?(?:regret|regrets)\s+"
    r"(?:(?:what|that)\s+i\s+(?:said|did|told|sent|wrote|shouted|texted|posted|lied|swore|"
    r"broke)\b"
    r"|(?:saying|telling|shouting at|lying to|snapping at|texting|sending|writing)\s+"
    r"(?:her|him|them|everyone|that|it|my\s+\w+|the\s+\w+)\b)")


SICK_DEED = re.compile(
    r"\b(?:feel|feels|feeling|felt|feelin)\s+(?:so |really |very |a bit |quite |pretty |kind of |"
    r"kinda |honestly |still )*sick\s+(?:that\s+i\s+(?:[a-z]+ed\b|" + IRREGULAR_DEED + r")"
    r"|(?:(?:about|for|over)\s+not\s+[a-z]+ing\b))")


# A body word is how a feeling is often felt, and the entry for a stomach has no feeling in it:
# "i feel sick to my stomach with guilt" was answered "Keep it plain and small: toast, crackers,
# rice", and "i feel sick when i think about it" with a bug passing through. The emotion after
# "with", or the thought the body reacts to, is the subject, so the body word is left to it. A bug
# named in the line ("sick with the flu") keeps its illness, and so does a body word with no
# feeling behind it ("i feel sick every morning", "my stomach hurts").
BODY_FEELING_SHAPE = re.compile(
    r"\b(?:feel|feels|feeling|felt)\s+(?:so |really |very |a bit |quite |pretty |kind of |"
    r"kinda |honestly |still |physically )*"
    r"(?:sick|ill|queasy|nauseous|dreadful|awful|rotten|terrible|funny|odd|strange|weird)"
    r"(?:\s+(?:to|in)\s+my\s+(?:stomach|gut|chest|throat)|\s+in\s+the\s+pit\s+of\s+my\s+"
    r"stomach|\s+all\s+over)?\s+"
    r"(?:with|from|about)\s+(?:the\s+)?"
    r"(?P<feeling>guilt|guilty|shame|ashamed|worry|worried|worrying|dread|dreading|anxiety|"
    r"anxious|panic|panicky|fear|fright|frightened|scared|nerves|nervous|stress|stressed|"
    r"uneasy|it all)\b")


# The stomach doing something, with the feeling named after it: "my stomach is churning with
# worry".
BODY_PART_FEELING = re.compile(
    r"\bmy\s+(?:stomach|gut|chest|heart)\s+(?:is\s+|keeps\s+|just\s+|literally\s+)*"
    r"(?:churning|turning|tightening|in knots|sinking|dropping|tight|jumpy|going|knotted)\s+"
    r"(?:with|at|over)\s+(?:(?:the\s+)?(?P<feeling>guilt|guilty|shame|ashamed|worry|worried|"
    r"dread|dreading|anxiety|anxious|panic|fear|fright|nerves|nervous|stress|stressed|uneasy)\b"
    r"|(?P<thought>the\s+thought\b|thinking\b|it\b))")


# "i feel sick when i think about it": the thought is the trigger, and there is nothing in the
# world to point at, so the pool is the worry with no date on it. The object is captured because
# only an unnamed thing is that: "i feel sick when i think about work" already has a better
# answer than a worry reply, and "i feel sick when i look at my phone" is a screen and not a
# memory. `look` needs the object it looks at to be the thing remembered, so it is read apart
# from the thinking verbs.
BODY_AT_THOUGHT = re.compile(
    r"\b(?:feel|feels|feeling|felt)\s+(?:so |really |very |a bit |quite |pretty |still )*"
    r"(?:sick|ill|queasy|nauseous|dreadful|awful|rotten|terrible|funny|odd|strange|weird)\s+"
    r"(?:when|whenever|every time|each time)\s+(?:i|we)\s+(?:"
    r"(?:think|thought|talk|hear|see|remember)(?:\s+(?:about|of|to|back\s+to))?|look\s+at)"
    r"\s*(?P<object>[a-z']+)?")


# The object a thought can point at without naming anything in the world.
# A body complaint with a "before" or "when" is about the thing coming, not the body: "i feel
# sick before every meeting" is nerves about the meeting, and "i get stomach ache when im
# anxious" names the feeling itself. The bug pool answered both with fluids and plain toast, and
# the worry pool below has the right answer for both, so the body word is left to it. A time of
# day ("i feel sick every morning") or a food is not an event and keeps its illness, and a
# dentist or a doctor is not one either: "i feel sick before the dentist" came back as a dental
# appointment to make, which is the wrong advice for a nervous stomach.
BODY_BEFORE_AN_EVENT = re.compile(
    r"\b(?:feel\s+(?:so |really |very |a bit |quite |still )*)?"
    r"(?:sick|ill|queasy|nauseous|stomach\s*(?:ache|achy|churn\w*|turns?|turning|in knots)?|"
    r"gut\s*(?:churn\w*|turns?|in knots)|churning stomach|butterflies)\b"
    r"[^.!?]{0,30}?"
    r"\b(?:before|when|whenever|every time|each time|at the thought of)\s+"
    r"(?:(?:i\s+am|im|i'm|i)\s+)?"
    r"(?:every|each|a|an|the|my|any|big|important)?\s*"
    r"(?:nervous|anxious|worri\w+|scared|panic\w*|stressed|dread\w*|exam\w*|meeting\w*|"
    r"interview\w*|presentation\w*|present\w*|speak\w*|talk\w*|call|date|wedding|party|"
    r"flight|test\w*|trip|appointment\w*|shift\w*|performance\w*|"
    r"match\w*|race\w*|audition\w*)\b", re.I)


THOUGHT_UNNAMED = frozenset((
    "it", "that", "this", "them", "her", "him", "you", "us", "everything", "anything",
    "nothing", "those", "these", "all", "what", "how",
))


# A symptom in the same line is a body that needs its own answer: "my stomach is churning with
# worry and i have diarrhea" is both, and the fluids line is the one they can act on. This
# stands the reading down the way an illness the line names already does.
SYMPTOM_IN_LINE = re.compile(
    r"\b(?:diarr\w*|throwing up|threw up|vomit\w*|being sick|been sick|the runs|"
    r"(?:a |the |my )?(?:temperature|fever)|dizzy|light[- ]?headed|"
    r"blood\b(?!\s+(?:test|pressure|sugar|type|group|donor|donation))|cramps?\b|"
    r"(?:can'?t|cant|couldn'?t) keep (?:anything|food|water) down|"
    r"keep(?:ing)? anything down)")


# "nerves before something big are normal" is the answer to a line that asks whether it is
# normal, and the worry pool presumes a feeling rather than a question.
ASKS_IF_NORMAL = re.compile(
    r"\b(?:is|was)\s+(?:that|this|it)\s+(?:normal|ok\b|okay\b|usual|weird|common)\b|"
    r"\bis that a (?:normal|thing)\b|\bam i (?:normal|weird|going mad)\b")


# An illness the line names is the subject, not a figure of speech.
BUG_NAMED = re.compile(
    r"\b(?:flu|covid|coronavirus|virus|bug|infection|migraine|headache|hangover|food poisoning|"
    r"the squits|d and v|chest infection|sore throat|tonsillitis|vertigo|morning sickness)\b")


BODY_FEELING_WORDS = {
    "guilt": "guilty", "guilty": "guilty", "shame": "guilty", "ashamed": "guilty",
}


def _line_as_read(text):
    """The line as the body readers want it: folded, with "sick with worry" read as worry."""
    clean = " ".join(str(text or "").lower().replace("’", "'").split())
    return badnews.without_the_figure_of_speech(clean)


def _a_limit(text, memory):
    """The reply for a line that only rules something out, or None.

    "recommend a film" / "no horror" was answered with a horror list, and "training the lead" /
    "no treats" with the treat again, because the word after "no" is a topic word like any other.
    The understanding engine reads the limit (`["constraint"]`, `["excludes"]`); the wording comes
    from the composer, which takes the thing out of the answer above.

    It stands aside where the knowledge base has an entry for the line as it stands: "no onion"
    after a curry is answered by the entry that says what to use instead, and "no heating" is a
    report about the boiler, not a limit on anything. Only a line nothing answers is read as a
    limit, so no entry ever loses its turn to this.

    A line that is only the limit is the exception (`bot/memory/limit.py`, `only_a_limit`). The
    entry the knowledge base has for the word after "no" is, by definition, the thing the person
    has just taken away: "no walking up hills" after a weight-loss plan reached the entry about
    riding a bike up a hill, which answers a cyclist, and it read as a fresh answer beside the plan
    already on the screen with the walking taken out of it.
    """
    read = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(read, dict) or not read.get("constraint"):
        return None
    try:
        if lookup.find(read) is not None and not limit.only_a_limit(text):
            return None
        reply = limit_line.reply_for(read, memory)
        if reply and isinstance(memory, dict):
            # The parts the limit left are what a "whats the first thing to change" a turn later is
            # about, and the answer itself is no longer the turn on the screen.
            memory["limit"] = {"said": reply, "steps": limit_line.steps_left(read, memory)}
        return reply
    except Exception:  # noqa: BLE001 - a limit that cannot be worked out claims no turn
        return None


"""A verdict the person has already reached on their own life.

"i live alone and love it" got the neutral nod ("I'm listening - say more if it helps"), "i
live on my own and wouldnt change it" the loneliness plan, "i got divorced and its the best
thing i ever did" "Sorry to hear that", "i quit my job and its great" a resignation letter and
"i work nights and love it" a lecture on the body clock. In every one of those the person has
already said how they read the thing, and the reply argues with them - the one thing a friend
never does.

The shape is what is read, never the topic: a statement about their own life, then a verdict on
it with the thing standing as "it"/"that"/"them" ("and love it", "and i dont miss it", "and
wouldnt change it", "and it works for us", "and its the best thing i ever did", "and no
regrets"). A verdict about somebody else ("my kids love it", "she loves it") is theirs and stays
with whoever can answer it, and so is a verdict on a thing they bought or made: "i bought an air
fryer and i love it" is a question about the air fryer, so a bare "love it"/"its great" is read
only when the fact in front of it is a change of life or the shape of their days.
"""


_SAY = r"(?:really|absolutely|totally|honestly|actually|still|just|genuinely)?"


_THING = r"(?:it|that|this|them|every minute of it)"


_TAIL = r"(?: a lot| so much| too| now| honestly| really| actually| already| anyway)*"


_HOW_I_READ_IT = re.compile(
    r"(?:^|,| and | but | so | though | - )"
    r"(?:"
    r"(?:(?:i|we)(?:'ve| have)?\s+)?" + _SAY + r"\s*"
    r"(?:love|like|enjoy|prefer)\s+" + _THING
    + r"|(?:(?:i|we)(?:'ve| have)?\s+)?(?:don'?t|dont|do not|never)\s+(?:miss|regret)\s+"
    + _THING
    + r"|(?:(?:i|we)(?:'ve| have)?\s+)?(?:wouldn'?t|wouldnt|would not|won'?t|wont)\s+"
      r"change\s+(?:it|a thing|anything)"
    + r"|(?:(?:i|we)(?:'ve| have)?\s+)?(?:no|zero)\s+regrets"
    + r"|(?:it'?s|it is|that'?s|that is)?\s*(?:fine|good|great|grand) by me"
    + r"|(?:it'?s|it is|that'?s|that is|it|that|this|i|we|they)\s+"
      r"(?:really\s+|just\s+|actually\s+)?(?:suits|works for|works with)\s+(?:me|us)"
    + r"|(?:it'?s|it is|that'?s|that is|it|that|this)\s+(?:perfect|ideal|great|brilliant|"
      r"lovely|fine|right)\s+(?:for|with)\s+(?:me|us)"
    + r"|(?:it'?s|it is|that'?s|that is|it|that)\s+(?:the\s+)?best\s+"
      r"(?:thing|decision|move|call|choice)"
      r"(?:\s+(?:i've|ive|i have|we've|weve|we have|i|we)\s*(?:ever\s+)?"
      r"(?:did|made|took|done))?"
    # The bare verdict, with no "for me" on the end: "and its great", "and its better now".
    # These are the ones a thing they made can also be ("i made a cake and its great"), so they
    # are read only off a fact that is a change of life or the shape of their days.
    + r"|(?:it'?s|its|that'?s|thats)\s+(?:great|brilliant|lovely|fine|better)\b"
    + r"|better now\b"
    + r"|(?:best|right)\s+(?:thing|decision|move|call|choice)\s+(?:i|we)(?:'ve| have)?\s+ever"
      r"\s+(?:did|made|took|done)"
    + r"|(?:i'm|im|i am|we're|we are)?\s*(?:really\s+|so\s+|very\s+)?happy\s+"
      r"(?:about|with)\s+(?:it|that|this)"
    + r"|(?:(?:i|we)(?:'ve| have)?\s+)?(?:never\s+been\s+happier|couldn'?t be happier|"
      r"couldnt be happier|couldn'?t ask for more|couldn'?t fault it)"
    + r"|(?:it|that|this)\s+(?:doesn'?t|does not|dont)\s+bother\s+me"
    + r")" + _TAIL + r"[.!]*$", re.I)


# A change of life, or the shape of their days. These are the facts after which "and love it" is
# a verdict on how they live rather than on something they made or bought.
_A_LIFE = re.compile(
    r"\b(?:quit|quitting|left|leaving|moved|moving|retired|retiring|divorced|split|stopped|"
    r"gave up|giving up|sold|packed in|dropping out|dropped out|went back|gone back|went part|"
    r"gone part|changed|switched|ended|finished|came out|binned|dumped|cut out|cut down|"
    r"live|living|lives|work|working|worked|shift|shifts|nights|single|married|rent|renting|"
    r"own my|owed|widowed|part time|full time|from home)\b", re.I)


# The verdicts that are the whole of what they said - "and its the best thing i ever did" - are
# not read off a thing they made, so they need no such fact in front of them. "and its great" is
# only a verdict on a life when the life is what changed or how they live it.
_A_LOOSE_VERDICT = re.compile(
    r"(?:it's|its|that's|thats)\s+(?:great|brilliant|lovely|fine|better)\b|better now\b"
    r"|(?:perfect|ideal|great|brilliant|lovely|fine|right)\s+(?:for|with)\s+(?:me|us)\b"
    r"|\b(?:love|like|enjoy|prefer)\s+(?:it|that|this|them)\b", re.I)


# The statement the verdict is on has to be about them, and it has to be a statement: "i wish i
# could love it" and "im not sure i love it" are not verdicts, and neither is a question.
_THEIR_OWN_LIFE = re.compile(
    r"\b(?:i|we|i'm|im|i am|we're|we are|my|our|i've|ive|we've)\b", re.I)


_NOT_A_VERDICT_YET = re.compile(
    r"\b(?:if|whether|wish|wonder|not sure|dont know|don'?t know|unsure|think i|thought i|"
    r"might|maybe|probably|hope|hoping|trying|want|wanted|would like|not at all)\b", re.I)


def _their_own_call(text):
    """The verdict the person has already reached, if this line is one, or None."""
    said = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    if not said or "?" in said:
        return None
    for match in _HOW_I_READ_IT.finditer(said):
        fact = said[:match.start()].strip(" ,;:-")
        fact = re.sub(r"(?:\b(?:and|but|so|though|honestly|tbh|well))\W*$", "", fact)
        fact = fact.strip(" ,;:-")
        if len(fact.split()) < 2 or not _THEIR_OWN_LIFE.search(fact):
            continue
        if _NOT_A_VERDICT_YET.search(fact):
            continue
        verdict = match.group(0).strip(" ,")
        if " by me" in verdict:
            return verdict      # "its fine by me" is a verdict on its own, not on a cake
        if _A_LOOSE_VERDICT.search(verdict) and not _A_LIFE.search(fact):
            continue
        return verdict
    return None


# "i feel sick that i can't keep anything down" is a condition, not a deed, so it stays with
# the body. Only a thing the person did belongs to guilt.
# In a how-to line, "without feeling guilty" names the thing the person wants to avoid, not a
# mood they are in: "how do i say no without feeling guilty" asks how to say no, and the feeling
# pool's "Right, not that one" took the say-no answer away. The `without` clause is cut before a
# feeling is read, so the action the line is about keeps the turn. Only a how-to ask: a statement
# like "i can't relax without feeling guilty" is left alone, because there the clause is part of
# how they feel. A feeling before the `without` ("i feel anxious about saying no without
# upsetting them") is kept too, because only the clause after it is cut.
AVOIDED_FEELING = re.compile(r"\bwithout\s+(?:feeling|being)\b[^.!?,;:]*")


def _without_the_feeling_avoided(clean, understood):
    """The line with a how-to's "without feeling X" clause taken out, or the line unchanged."""
    if not isinstance(understood, dict) or understood.get("kind") != "question":
        return clean
    if not any(ask in ("how", "steps") for ask in understood.get("asks") or ()):
        return clean
    return AVOIDED_FEELING.sub(" ", clean)


FEELING_LEAD = re.compile(r"\b(i'm|im|i am|i feel|i felt|feeling|feel|so|really|very|pretty|"
                          r"kinda|kind of|a bit|abit|a little|quite|totally|bit|just|"
                          r"today|now|again|honestly|still|am)\b")


FEELING_SELF = re.compile(r"\b(i'm|im|i am|i feel|i felt|feeling|feel)\b")


# "im not tired" is not a tired line: answering it with "give yourself half an hour doing
# nothing" tells the person what they just said they do not feel. A feeling word is only read
# as a feeling when the word in front of it is not a negation. The words that may sit between
# the two ("not really that tired") are the ones that change nothing about the negation.
NOT_WORDS = frozenset(("not", "never", "no", "hardly", "barely", "cant", "cannot", "dont",
                       "doesnt", "didnt", "isnt", "arent", "wasnt", "werent", "aint",
                       "nothing", "none"))


NOT_FILLERS = frozenset(("really", "that", "very", "so", "too", "even", "actually", "much",
                         "all", "particularly", "especially", "quite", "terribly", "longer",
                         "as", "this", "feeling", "feel", "felt", "been", "being", "am",
                         "im", "i'm", "i", "is", "was", "are", "were", "get", "getting",
                         "got", "seem", "seems", "look", "looks", "sound", "sounds"))


def _negated(clean, word):
    """True when every mention of this feeling word in the line is denied ("im not tired").

    "im not tired, im just bored" is a bored line, so one mention that is not denied is enough
    to read the feeling. Only the words immediately in front of the mention count, inside its
    own clause: in "i dont know why im so tired" the negation belongs to "know", and in
    "im not sleeping, exhausted" it belongs to "sleeping".
    """
    found = False
    for match in re.finditer(r"\b" + re.escape(word) + r"\b", clean):
        found = True
        before = re.split(r"[.!?,;:]", clean[:match.start()])[-1].split()
        index = len(before) - 1
        skipped = []
        while index >= 0 and before[index] in NOT_FILLERS:
            skipped.append(before[index])
            index -= 1
        if index < 0 or not (before[index] in NOT_WORDS or before[index].endswith("n't")):
            return False  # this mention is meant: the person does feel it
        if before[index] == "never" and any(w in ("so", "this", "more", "such") for w in skipped):
            # "ive never felt so tired" is the strongest tired there is, not a denial of it.
            return False
    return found


# "not happy with the service" is a complaint about a thing, and the sad pool ("be kind to
# yourself today") has nothing to do with it.
# Words that start a new thing to say after a denial: "im not hungover just tired" corrects the
# first feeling and says a second one. The negator belongs to the word before the correction,
# never to the one after it, and the wide window above would otherwise deny both.
CORRECTION_MARKERS = frozenset(("just", "only", "but", "though", "tho", "except"))


def _denies_an_earlier_word(clean, word):
    """True when the negator in front of this word is followed by a correction ("not x just y")."""
    for match in re.finditer(r"\b" + re.escape(word) + r"\b", clean):
        held = False
        for token in clean[:match.start()].split()[-4:]:
            if token in NOT_WORDS or token.endswith("n't"):
                held = True
            elif held and token in CORRECTION_MARKERS:
                return True
    return False


NOT_HAPPY_ABOUT = re.compile(r"\bnot\s+(?:very\s+|at all\s+|too\s+)?(?:happy|glad|pleased|thrilled|"
                             r"impressed|chuffed)\s+(?:about|with|at)\b")


INTENSIFIERS = frozenset("""
so really very pretty quite totally completely absolutely bloody proper dead super too this bit
kinda sorta madly
""".split())


INTENSIFIER_PAIRS = frozenset({"a bit", "kind of", "sort of", "a little", "a tad"})


# What may follow a feeling word used of a person: the end of the line, or a word that carries
# no thing of its own ("low again", "down today", "tired of work"). A noun after it means the
# word is describing that thing instead ("low heat", "long day" is handled by ROUGH_DAY).
DETERMINERS = frozenset("a an the my our your his her its their this that these those some".split())


# Nouns that name how a person is, so "my mood is really low" is still about the person.
STATE_NOUNS = frozenset("mood spirits energy mind head confidence sleep nerves anxiety stress "
                         "worry patience motivation".split())


OWN_STATES = frozenset({"i", "we", "me", "us", "my", "our", "myself", "ourselves"}) | STATE_NOUNS


COPULA = re.compile(r"\b(?:is|are|was|were|am|feels?|seems?|looks?|gets?|got)\b")


FUNCTION_WORDS = frozenset("""
a an the and or but if then than that this these those it its is are was were be been being
am do does did doing have has had having i me my mine you your yours we us our they them their
he she his her one so too very just also as at by for from in into of off on onto to up with
about after before again any can could should would will shall may might must not no yes now
here there what which who when where why how much many long today tonight tomorrow lately
honestly still already even only afterwards else as if because though although while since
always usually often never sometimes constantly permanently lately recently mostly seldom
""".split())


# Missing someone, and the days after a goodbye: "i miss her", "i still think about her every
# day", "i keep thinking about my ex". The words name a person and an ordinary verb, so without
# this the line is filed as a fact about the person and noted back ("Noted!") - it is a feeling,
# and the same kind as a low day.
STILL_ON_THEM = re.compile(
    r"\b(?:i|we)\s+(?:(?:really|still|keep|keeps|always|often|just|sometimes)\s+)*"
    r"(?:think(?:s|ing)?\s+(?:about|of)|remember(?:s|ing)?|"
    r"miss(?:es|ing)?|dream(?:s|t|ing)?\s+about)\s+"
    r"(?:her|him|them|it|my\s+(?:ex|wife|husband|partner|boyfriend|girlfriend|fianc\w*|"
    r"mum|mom|mother|dad|father|son|daughter|brother|sister|gran|granny|grandma|grandad|"
    r"grandpa|nan|nana|friend|best friend|dog|cat|old life|old job))\b")


# Affection said straight to the bot: "i love you", "love ya", "i like you", "you're my
# favourite", "you make me happy". None of it asks for anything and none of it is a fact about the
# person's life, so the plain ack pool answered it with its shrug - "Fair enough." to "i love you"
# reads as agreeing with them - and "you make me happy" was read as news about a good day ("Good
# for you! That sounds like it was worth the wait."). It is small talk, and the small warm answer
# is the reply. The bot does not say it back: it is a program, and "I love you too" from one is
# what STYLE.md's honesty rule is about.
FOND_OF_ME = re.compile(
    r"^(?:oh |ah |aw+ |haha |ha |ok |okay |well )*"
    r"(?:(?:(?:i|we)\s+)?(?:(?:really|so|do|just|properly|absolutely)\s+)*"
    r"(?:love|luv|adore)\s+(?:you|u|ya|yous)(?![a-z])(?:\s+(?:too|so much|so|a lot|loads|both|man))*"
    r"|(?:i|we)\s+(?:(?:really|so|do|quite|actually)\s+)*(?:like|fancy)\s+you(?![a-z])"
    r"(?:\s+(?:too|a lot|loads))*"
    r"|(?:you(?:'?re| are)|your)\s+(?:my\s+|the\s+)?(?:favourite|favorite|best)(?:\s+bot)?"
    r"|you\s+(?:(?:always|really|do|just)\s+)*"
    r"(?:made my day|make my day|make me (?:happy|smile|laugh|feel better)"
    r"|made me (?:happy|smile|laugh|feel better)|cheer me up|cheered me up))"
    r"(?:\s*,?\s*(?:honestly|really|truly|thank you|thanks|cheers|ha))*\s*[.!]*$")


# A line about somebody else's love is not this one: "i love my mum", "nobody loves me", "i dont
# love you" and "my husband loves you" all keep the readers that can answer them.
NOT_FOND = re.compile(
    r"\b(?:dont|don't|didnt|didn't|doesnt|doesn't|never|not|no longer|cant|cannot|stop|"
    r"nobody|no one|anyone|someone|her|his|their|our|mum|mom|mother|dad|father|partner|"
    r"husband|wife|kids?|son|daughter|friend|family|dog|cat|pizza|film|book|song)\b")


FOND_REPLIES = (
    "That's a lovely thing to say. Thank you.",
    "That's kind of you - I'm glad this is a good place to be.",
    "Thank you. You're good company yourself.",
    "That's kind. I'm always up for a chat like this one.",
)


def _fond_of_the_bot(clean):
    """True when the line is affection for the chat itself, and nothing else.

    The whole line, because affection with a subject of its own is about that subject: "i love my
    mum", "my husband loves you" and "nobody loves me" are not the bot being thanked. A negated
    or doubting form ("i dont love you") is not affection either.
    """
    line = " ".join(str(clean or "").lower().split()).strip(" .,!?:;")
    if not line or NOT_FOND.search(line):
        return False
    return bool(FOND_OF_ME.match(line))


# The bot itself: "i miss you", "i miss talking to you". Nothing has gone, so the missing pool
# ("it goes in waves, and the waves get further apart") is the wrong answer to it - the person is
# being warm about the chat, which is the small warm answer and never a fact about them.
MISS_ME = re.compile(
    r"\b(?:i|we)\s+(?:(?:really|do|so|just)\s+)*(?:miss|missed)\s+"
    r"(?:you|(?:talking|chatting|speaking)\s+(?:to|with)\s+you)\b"
    r"|\b(?:i|we)\s+(?:really\s+)?(?:keep\s+|still\s+)?think(?:ing)?\s+(?:about|of)\s+you\b")


MISS_YOU_REPLIES = (
    "That's kind. I'm here whenever you want to talk.",
    "Nice of you to say - I'm not going anywhere.",
    "Thank you. Same here - say what's on your mind.",
)


# Someone being warm about the bot itself: "you're really kind", "you have been a big help",
# "i like talking to you". None of it asks for anything, so the stock ack ("Noted!", "I'm here if
# you want to dig into any of that") reads like a filing cabinet. It is small talk and wants the
# small warm answer, and it is never read as a fact about the person.
KIND_TO_ME = re.compile(
    r"(?:\byou(?:'?re| are|'?ve been| have been| were| were being|'?re being)\s+"
    # "youre quite good at this" is the same compliment as "youre good at this", and without
    # "quite" in this list it read as nothing: the line fell through to the follow-up slot and
    # the person got the last answer served again ("Same as before: ..."). "pretty", "super"
    # and the rest are the same word doing the same job in everyday speech, so the list is the
    # hedges people actually type rather than one of them.
    r"(?:so |very |really |quite |pretty |super |genuinely |incredibly |absolutely |truly |"
    r"actually |always |properly |dead |well )*"
    r"(?:kind(?! of\b)|lovely|nice|sweet|helpful|great|brilliant|fab|fabulous|amazing|"
    r"wonderful|the best|a star|a legend|good fun|funny|good at this|good company)\b)"
    r"|(?:\byou(?:'?ve| have)\s+(?:been\s+)?(?:a\s+|an\s+)?"
    r"(?:big|huge|massive|real|great|proper)\s+help\b)"
    r"|(?:\bi\s+(?:really\s+|do\s+|quite\s+|actually\s+)?(?:like|enjoy|love)\s+"
    r"(?:talking|chatting|speaking)\s+(?:to|with)\s+you\b)"
    r"|(?:\bi\s+(?:really\s+|do\s+|quite\s+)?(?:like|enjoy|love)\s+this\b(?!\s+(?:recipe|song|dish|film|book|idea|one)\b))"
    r"|(?:\b(?:that|this)\s+was\s+(?:really |very |so |properly )?"
    r"(?:helpful|useful|great|lovely|kind of you|exactly what i needed)\b)")


# The same compliment said about the answer rather than the bot: "your advice was really useful",
# "thats helpful", "that helped a lot". KIND_TO_ME above reads "you are <adjective>"; these are
# the ways people praise the thing the bot just said, and they land in the same place, because a
# compliment is a closing move either way. The two shapes here are both unambiguous: "your
# <thing> was <praise>" can only be about the bot, and a demonstrative praise ("thats useful") is
# a compliment unless it is a question ("is that useful"), which the lookbehinds keep out, or
# a clause of a line that still asks something, which the end-of-line check keeps out.
PRAISED_ANSWER = re.compile(
    r"\byour\s+(?:advice|answer|reply|help|tip|tips|suggestion|explanation|list|idea)\s+"
    r"(?:\w+\s+){0,2}?(?:was|is|were)\s+"
    r"(?:really |very |so |properly |super |dead |actually )*"
    r"(?:useful|helpful|good|great|brilliant|spot on|sound|exactly right)\b"
    r"|\byou(?:'?re| are)\s+(?:really |very |so )?easy to talk to\b"
    r"|(?<!\bnot )(?<!\bnot very )(?<!\bwasnt )(?<!\bisnt )(?<!\baren't )"
    r"(?<!\bwas )(?<!\bis )(?<!\bthat\s)(?:\bthat|\bthats|\bthat's)\s+"
    r"(?:was\s+|were\s+|is\s+)?(?:really |very |so |properly |super )*"
    r"(?:helpful|useful|spot on|good|great|a lot of help|a big help|a real help)\b")


# A line that is nothing but the compliment: "great advice", "that helped a lot", "nice one".
# Whole line, because a third party can own the same words ("she gave me good advice") and a
# sentence with a subject of its own is about that subject, not about the bot.
BARE_PRAISE = frozenset((
    "great advice", "good advice", "sound advice", "brilliant advice", "top advice",
    "really useful advice", "really good advice", "such good advice", "what great advice",
    "great answer", "good answer", "lovely answer", "brilliant answer",
    "that helped", "that helped a lot", "that really helped", "that helped loads",
    "that helped so much", "thats helped a lot", "that was a lot of help",
    "thats just what i needed", "exactly what i needed",
    "thats great advice", "that's great advice", "that is great advice",
    # The same praise said with "helps": "that helps", "ok that helps", "this helps". The
    # thanks pool has no word for these, so the reading calls the line a thank-you and the
    # whole-line praise is what says it in the warm close the other compliments get.
    "that helps", "this helps", "that really helps", "this really helps",
    "that helps a lot", "that helps loads", "that helps so much",
))


# A compliment the person has already taken back is not a compliment: "i dont think thats great",
# "not sure that was great", "not sure its that helpful" were all answered "That's kind of you to
# say - glad it's useful", which congratulates them for the opposite of what they said. The not in
# front of a thinking or being-sure word belongs to that word - it is doubt about the praise, not
# the praise - so a doubt frame anywhere before the praise takes the whole line out of the warm
# close. The lookbehinds in PRAISED_ANSWER cover the short shape ("not that great"); this covers
# the long one, where the not is two or three words further back.
DOUBT_FRAME = re.compile(
    r"\b(?:dont|do not|didnt|did not|wouldnt|would not|cant|can not|couldnt|could not|"
    r"never said|hard to say)\b(?:\s+\w+){0,2}?\s+"
    r"(?:think|say|reckon|believe|find|fancy|call it)\b"
    r"|\bnot\s+(?:sure|certain|convinced)\b|\bunsure\b|\bnot convinced\b|\bi doubt\b")


# The agreement in front of a compliment is not part of it: "ok that helps", "yeah thats helpful".
BEFORE_PRAISE = re.compile(r"^(?:ok|okay|yeah|yep|yes|ah|oh|right|cool|so)\s+")


# A praise that is only a clause of a longer line is not a closing move: "thats helpful, but how
# do i get the lid off the jar" still asks a thing, and a thank-you would eat the question. So
# the praise has to be the last thing in the line, give or take a trailing thanks.
THANKS_AFTER = re.compile(r"\s*,?\s*(?:thanks|thank you|cheers|ta|anyway)\s*[.!]*$")


def _praised_the_answer(clean):
    """True when the line praises what the bot just said, not the bot or anybody else.

    "your advice was really useful" and "thats helpful" are compliments about the last answer,
    and nothing asks for anything, so they get the same warm close as "you're so helpful". The
    guards matter: "is that useful" is a question about something else, "she gave me good advice"
    is about her, and "well done" is about the person's own news - none of them is a move to
    close, so the reply they get now is left alone.
    """
    line = " ".join(str(clean or "").lower().split())
    line = line.strip(" .,!?:;")
    line = BEFORE_PRAISE.sub("", line)
    if not line:
        return False
    while True:
        core = THANKS_AFTER.sub("", line).strip(" .,!?:;")
        if core == line:
            break
        line = core
    if not line:
        return False
    if line in BARE_PRAISE:
        return True
    return any(found.end() == len(line) for found in PRAISED_ANSWER.finditer(line))


KIND_REPLIES = (
    "That's kind of you to say — glad it's useful.",
    "Thank you. That's what I'm here for.",
    "Nice of you to say - thank you.",
    "Glad it helped. Say the word if there's more.",
)


# A cold is a fact about the body, not a mood. "im coming down with a cold" has "down" in it, and
# "down" is one of the sad words, so the mood pool answered it with "a walk and someone to talk to
# usually help more than sitting with it" - advice for low mood, given to someone with a cold. The
# composer already has the right line for an illness ("rest, warm drinks and an early night"), so
# chat passes the line on and lets it answer. Only the person writing, and only a word for being
# unwell: "my son has a cold" is about him, and "im sick of my job" is fed up, not ill.
ILL_SELF = re.compile(
    r"\b(?:i|i'm|im|ive|i've|we|we're|were|weve|we've)\b[^.!?]{0,24}?"
    r"\b(?:coming down with|going down with|come down with|down with|full of|"
    r"got a|got the|getting a|getting the|have a|have the|had a|"
    r"battling|fighting off|suffering from|recovering from)\s+"
    r"(?:a\s+|an\s+|the\s+|some\s+|this\s+|that\s+)?"
    r"(?:cold|flu|bug|virus|cough|sore throat|temperature|fever|chest infection|sickness|"
    r"stomach bug|migraine|something)\b"
    # A bug in the code or a virus on the laptop is not an illness: leave those lines alone.
    r"(?![^.!?]{0,20}\b(?:code|app|apps|program|project|site|website|laptop|computer|pc|"
    r"phone|machine|system|server|build|repo|script|tests?|deploy)\b)"
    r"|\bi(?:\s+am|'?m|m)?\s+(?:not|really not|properly)\s+(?:well|feeling well)\b"
    r"|\bi(?:\s+am|'?m|m)?\s+(?:a bit\s+|really\s+|very\s+|quite\s+|so\s+|properly\s+|"
    r"pretty\s+|still\s+)*(?:ill|poorly|unwell)\b"
    r"|\b(?:i|ive|i've|we|we've)\b[^.!?]{0,20}?\b(?:feel|feels|feeling|felt|been|being)\s+"
    r"(?:a bit\s+|a little\s+|really\s+|very\s+|quite\s+|so\s+|pretty\s+|properly\s+)*"
    # "im sick of my job" is fed up and "i feel sick about the dentist" is dread: neither is an
    # illness, so the word is not one when a thing follows it.
    r"(?:ill|poorly|unwell|sick)\b(?!\s+(?:of|about|at|thinking)\b)"
    r"|\bi(?:\s+am|'?m|m)?(?:\s+\w+){0,2}?\s+under the weather\b", re.I)


# The illnesses honey and lemon is actually honest for: a throat, a cough, a nose, a chest, and
# the cold or flu behind them. A migraine, a fever with no cold in it or a plain "i feel ill" is
# not that illness, and "the first day of it is the worst" told somebody with a migraine nothing
# about a migraine, so the pool is chosen by what the line names.
COLD_NAMED = re.compile(
    r"\b(?:cold|flu|cough|throat|chest infection|runny nose|blocked nose|sniffles?|"
    r"sneezing|sneezes|temperature|shivery|hoarse|croaky)\b", re.I)


# A line that is only the complaint is the person saying they have it. "cough", "flu", "sore
# throat" are "i have a cough" with the front cut off, and they were answered with "Got it. Is
# there anything you'd like a hand with?" while the same words inside a sentence got the care
# line. The body parts are the shared reading's job ("headache", "stomach ache" -
# bot/understanding/body.py reads a bare part as the speaker's); this is the cold and the bug,
# which name no part. Nothing but qualifiers may be left over, so "honey for a cough" and
# "what helps a cough" keep their own reading.
COMPLAINT_ONLY = re.compile(
    r"^\s*(?:(?:a|an|the|my|some|really|very|so|bad|sore|slight|terrible|awful|horrible|"
    r"nasty|mild|chronic|another|chesty|bit of a|bit of)\s+)*"
    r"(?:flu|cough|coughs|chesty cough|chest infection|sneezes?|sniffles?|sniffly|shivery|"
    r"chills|bug|virus|sickness|temperature|fever|throat|sinus)\s*"
    r"(?:(?:and|or|with|plus)\s+(?:a |an |the |my )?"
    r"(?:flu|cough|coughs|sore throat|temperature|fever|headache|sniffles?|sneezes?)\s*)*"
    r"[.!]*\s*$", re.I)


# A cold sore is not a cold. "i have a cold sore" matched ILL_SELF ("i have a cold ...") and
# COLD_NAMED ("cold"), so the sympathy card for a cold answered it - "That's rotten. Take it easy
# today - honey and lemon, and don't push through it" - which is no help with a sore on the lip.
# The knowledge base has the cold-sore answer (health: cold-sore), so the line is left to it: the
# composer only stands aside for the sore itself, not for a cold said in the same line.
COLD_SORE = re.compile(
    r"\b(?:cold|fever)\s+(?:sore|sores|blister|blisters)\b|\bsore on (?:my|the) lip\b", re.I)


# A line that also says how the person feels is being told, not asked: "i have a cold sore and i
# feel awful" wants the sympathy before the pharmacy, so the sore does not stand the card down.
COLD_SORE_FEELING = re.compile(
    r"\b(?:awful|terrible|rough|miserable|poorly|dreadful|horrible|rotten|exhausted|"
    r"wiped out|knackered)\b", re.I)


# The cold itself, said by the part that is running: "i have a runny nose", "my nose is blocked",
# "im sneezing all morning", "i feel bunged up". ILL_SELF above wants the illness named ("got a
# cold"), so these lines got a nod, which reads as if the bot had not heard them. A nose is also
# the nose of a car, so the line has to be about the person's own.
COLD_SYMPTOM = re.compile(
    # the person's own, said with "my": "my nose is running", "my nose is blocked"
    # "my sinuses are blocked" already has its own answer further down, and a sinus is not a cold
    # every time, so only the nose is read here.
    r"\bmy\b[^.!?]{0,8}?\bnose\b[^.!?]{0,10}?\b(?:is |are |keeps |feels )?"
    r"(?:runny|running|blocked|bunged|stuffy|streaming|dripping|congested|sniffly)\b"
    r"|\bmy\b[^.!?]{0,10}?\b(?:runny|running|blocked|bunged|stuffy|streaming|dripping|"
    r"congested|sniffly)\b[^.!?]{0,8}?\bnose\b"
    # or the speaker has it: "i have a runny nose", "ive got blocked sinuses". The speaker has to
    # be the one with it: "the cat has a runny nose" is the cat's, and the cat does not want
    # honey and lemon.
    r"|\b(?:i|im|i'm|ive|i've|we|we're|we've)\b[^.!?]{0,14}?\b(?:have|has|having|had|got|"
    r"keep|keeps|keeping|with)\b[^.!?]{0,10}?\b(?:a |an |the |some |really |very |bit of a )?"
    r"(?:runny|running|blocked|bunged|stuffy|streaming|dripping|congested|sniffly)\b"
    r"[^.!?]{0,10}?\b(?:nose|sinus\w*)\b"
    # sneezing that keeps on: "i keep sneezing", "im sneezing all morning"
    r"|\b(?:i|im|i'm|ive|i've|we|we're|we've)\b[^.!?]{0,16}?\b(?:keep|keeps|been|still|"
    r"always|am|im|i'm)\b[^.!?]{0,10}?\bsneez\w*"
    # a body state said with "feel": "i feel bunged up", "i feel shivery"
    r"|\b(?:i|im|i'm|ive|i've|we|we've)\b[^.!?]{0,16}?\bfeel(?:s|ing)? (?:all |a bit |really |so )?"
    r"(?:bunged up|bunged|sniffly|shivery|hoarse|croaky)\b"
    # the cold said without the nose: "im stuffy", "im all bunged up", "im congested". A room
    # is stuffy and a sink is blocked up too, "im stuffed" is a full stomach and "i bunged the
    # washing in" is a bare "bunged", so the word only counts straight after the person with
    # nothing but a filler in between.
    r"|\b(?:i|im|i'm|ive|i've)\b"
    r"(?:\s+(?:all|really|so|very|a\s+bit|a\s+little|totally|properly|quite|that|bit|"
    r"still|now|again)){0,3}\s+"
    r"(?:feel(?:s|ing)?\s+)?(?:stuffy|stuffed\s+up|bunged\s+up|blocked\s+up|"
    r"congested|congestion)\b"
    # "im sniffly", "my nose is snotty": there is no other thing to be sniffly about, and the
    # cold pool is the answer it was being refused ("Got it. Is there anything you'd like a hand
    # with?"). "the dog is sniffing" is the dog, so the person has to be the subject.
    r"|\b(?:i|im|i'm|ive|i've)\b(?:(?!\b(?:dog|cat|puppy|kitten|baby|kid|boy|girl)\b)[^.!?]){0,16}?"
    r"\b(?:sniffly|sniffles|snotty)\b"
    # The verb needs a run of it behind it. "i keep sniffing" on its own is as much a habit as a
    # cold, and the routine card ("is it the same every time, or does it vary?") is the better
    # answer for it - "Sleep is the thing that actually helps" is not - so sniffling or sniffing
    # counts with a length: "all week", "all day", "since monday", "keeps", "been", "still".
    r"|\b(?:i|im|i'm|ive|i've)\b(?:(?!\b(?:dog|cat|puppy|kitten|baby|kid|boy|girl)\b)[^.!?]){0,16}?"
    r"(?:\b(?:all|every|since|for|the whole)\s+(?:day|week|morning|night|month|time)\b"
    r"|\bkeeps?\b|\bbeen\b|\bstill\b)"
    r"[^.!?]{0,16}?\b(?:sniffling|sniffing)\b"
    # ...and the same said of the head: "my head is stuffy", "my head is all bunged up". A head
    # is not stuffy for any other reason.
    r"|\bmy\s+head\b(?:\s+(?:is|are|feels?|feeling|gets?|keeps?))?"
    r"(?:\s+(?:all|really|so|very|a\s+bit|a\s+little|totally|quite|still|now|again)){0,3}\s+"
    r"(?:stuffy|stuffed\s+up|bunged\s+up|blocked\s+up|congested|congestion)\b", re.I)


# The same complaint said again, in the word the answer just given had in it. "im stuffy" then
# "im all bunged up" is the second half of one cold, not a new subject, and the answer to it is
# the answer just given with a "Same as before:" in front; the cold pool's plain card is thinner
# than the blocked-nose card it replaced. So a line whose symptom word the bot's last turn
# already named stands down here and leaves the repeat to the answers module. A different part
# ("now my throat hurts") shares no word with it and keeps this turn.
SAME_COLD = re.compile(r"\b(nose|blocked|bunged|stuffy|stuffed|congested|congestion|"
                       r"sinus\w*|sniff\w*|snotty|a cold)\b", re.I)
