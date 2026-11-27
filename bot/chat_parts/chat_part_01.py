"""Part 1 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import badnews
from ..compose.badnews import reads_as_bad_news
from ..compose.goodnews import reads_as_a_pass, reads_as_good_news
from ..compose import loss as loss_reading

from ..memory import thread
from ..memory.topics import in_a_safety_thread as _safety_thread
from ..memory.topics import keywords as _content_words

from ..memory import facts
from ..understanding import lexicon



PRIORITY = 300


# The topics this module is the specialist for (README.md, "Routing"). The arbiter prefers the
# module that declares the topic a line was read as over a fluent candidate about something
# else, so without this a small-talk line that mentions a subject could lose to a knowledge
# answer about the subject. It declares only "small-talk": "feelings", "family-and-parenting"
# and "friends-and-relationships" are also what the knowledge domains answer, and declaring one
# of them here (PRIORITY 300) takes the turn from those answers — `im nervous about a job
# interview` went from the work entry to chat's acknowledgement when "feelings" was declared.
# "about-the-bot" is the exception, because chat is the specialist for it: how-are-you is a
# question about the bot, and the answer it has is the only one there is. `answering` claims every
# topic, so a how-are-you said with a day in it ("how was your day") was read as about-the-bot
# and then answered by the knowledge entry for the subject on the table.
ANSWERS = ("small-talk", "about-the-bot")


TOKEN = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


GREET_CORE = {"hi", "hiya", "hey", "heya", "hello", "yo", "howdy", "morning", "afternoon",
              "evening", "greetings", "hallo", "helo"}


GREET_FILLER = {"good", "day", "all", "everyone", "folks", "guys", "team", "there", "again",
                "x", "everybody", "you", "lot", "the", "hi", "hiya", "hey", "heya", "hello",
                "yo", "howdy", "morning", "afternoon", "evening", "greetings", "hallo", "helo"}


THANKS_CORE = {"thanks", "thank", "thx", "ty", "cheers", "ta", "appreciated", "appreciate",
               "thnx", "thks"}


THANKS_LOOSE = {"one", "nice", "try", "ill", "will", "give", "go", "it", "lets", "today",
                "tomorrow", "later", "now", "anything", "else", "that", "this", "was", "is",
                "brill", "yeah", "yep", "earlier", "before", "sorted", "worked", "works",
                "far", "helped", "super", "legend", "ace", "so", "much", "again", "for"}


# A line that is only a request for help. "help" itself has to be here to be read, and every
# other word is one a person puts around it without naming what they need.
HELP_ONLY = frozenset("""help me us please pls a bit of then now thanks you sir mate""".split())


THANKS_FILLER = {"you", "u", "so", "much", "very", "a", "lot", "again", "for", "the", "help",
                 "thats", "its", "they", "were", "are", "im", "i", "am", "welcome", "again",
                 "well", "good", "okay", "alright", "brill", "cheers",
                 "helping", "that", "this", "is", "was", "its", "it", "perfect", "great",
                 "brilliant", "lovely", "awesome", "amazing", "excellent", "good", "nice",
                 "handy", "helpful", "works", "worked", "sorted", "really", "super", "too",
                 "all", "and", "ok", "okay", "man", "mate", "friend", "so", "much",
                 "idea", "do", "will",
                 # The same words as in ACK_WORDS, for the same reason: "im grand, ta" is a good
                 # day and a thank-you. Without them here the line was chatty but not a thanks,
                 # so the plain ack pool answered a good day with the shrug "Fair enough.", while
                 # "im good, ta" and "im alright, ta" got "No problem at all."
                 "grand", "chill", "content", "mint", "sound"}


ACK_WORDS = {"ok", "okay", "k", "kk", "cool", "nice", "great", "good", "fine", "sounds",
             "sound", "perfect", "brilliant", "lovely", "awesome", "amazing", "sure",
             "alright", "right", "righto", "aight", "yes", "yeah", "yep", "yup", "ya",
             "yh", "yhh", "ye", "no",
             "nah", "nope", "not", "really", "hmm", "hm", "oh", "ah", "aha", "wow", "damn",
             "meh", "idk", "i", "im", "dont", "know", "dunno", "maybe", "lol", "lmao", "haha",
             "hehe", "of", "course", "that", "this", "is", "was", "it", "its", "then", "well",
             "true", "fair", "enough", "makes", "sense", "got", "you", "u", "thanks", "thx",
             "ty", "cheers", "ill", "see", "have", "think", "about", "probably", "definitely",
             "most", "likely", "working", "for", "me", "thats", "sweet", "neat", "huh",
             "and", "but", "so", "oh", "worried", "sad", "happy", "fine", "bad", "good", "same",
             "well", "too", "okay", "alright", "nice",
             # How a person says they are in a word that is also another thing: "im grand"
             # (Ireland), "im chill", "im content", "im mint". Without these a bare "im grand"
             # was not a chatty line at all, so the composer's "I'm here if you want to dig
             # into any of that" answered somebody saying they were fine.
             "grand", "chill", "content", "mint"}


LAUGH_WORDS = {"lol", "lmao", "lmfao", "haha", "hahaha", "hehe", "rofl", "hilarious", "funny",
               "jokes", "joking", "jk", "dead", "cracking", "laughing", "lolz", "hah"}


# The reading's laughter spellings ("hahahaha", "ha ha ha", "hehehe"), so a laugh made of them is
# still a laugh here even though the word list above never grows.
LAUGHTER = frozenset(lexicon.LAUGHTER)


# "too much mint", "a lot of mint": a quantity in front of a word makes the word the thing
# that is plentiful, not a way of saying how the person is.
SAYS_TOO_MUCH = re.compile(
    r"\b(?:too much|too many|a lot of|lots of|loads of|plenty of|glut of|bag of|bunch of"
    r"|punnet of|box of|kilo of|tin of)\s+\w+", re.I)


NO_WORDS = {"no", "nah", "nope", "not", "naw", "never"}


# The only content words a refusal can carry: the pleasantries that go with saying no, and the
# vague noun people use ("not my thing", "no idea"). Anything else is a line about something -
# "im not good enough", "its not fair", "im not sleeping well" - and is not a refusal at all.
NO_REFUSAL_CONTENT = frozenset("""alright ok okay fine thanks thank cheers ta idea thing
    bother today tonight tomorrow yet now right later soon""".split())


# "not well" is the answer to "how are you?" when the answer is bad, and it is not a refusal:
# the no pool told somebody who had just said they were unwell "No worries - say if you change
# your mind." "not feeling well" and "im not well" were already read as what they are, so only
# the bare shape needs the guard, and "not today", "not really" and "not for me" are untouched.
NOT_A_REFUSAL = re.compile(
    r"^\W*not\s+(?:too\s+|very\s+|so\s+|feeling\s+|doing\s+)?"
    r"(?:well|good|great|ok|okay|brilliant|amazing|bad|right|myself)\b", re.I)


def _only_a_refusal(clean, tokens):
    """True when the line is only a refusal, so the "no" pool is the right answer to it.

    A "not" token used to be enough on its own, so every line with a "not" that nothing earlier
    claimed was answered as a refusal: "im not good enough" got "No worries - say if you change
    your mind", and since that pool sits in the small-talk band it outranked the composer, so
    nothing else could answer it either. A refusal is made of refusal words only: the no-words
    themselves plus the pleasantries that go with them. One content word means the line is about
    something ("im not good enough", "its not fair", "im not sleeping well"), and it must reach
    whoever can answer it.
    """
    if not any(t in NO_WORDS for t in tokens):
        return False
    if NOT_A_REFUSAL.match(clean):
        return False
    return not [word for word in _content_words(clean)
                if word not in NO_REFUSAL_CONTENT and word not in NO_WORDS]


# "im awful" and "im terrible" are how someone says they feel today, not a verdict on
# themselves, and this pool answers them with "That's the tiredness talking, not the truth" -
# telling a person their feeling is not real, which STYLE.md rules out. They are a verdict only
# when the line says what they are not good at ("im awful at my job") or gives them a role
# ("im an awful mum"), and both of those shapes are claimed by the arms below, which keep every
# word. The other words here stay verdicts on their own: "im useless", "im stupid" and
# "im a waste of space" are what someone says about themselves when they mean it, and "im bad"
# is a judgement too - only these two read as a state first.
A_MOOD_SAID_PLAINLY = frozenset("""awful terrible""".split())


# The words that say a person is failing rather than feeling something; the arms below use them
# with a role ("im a rubbish mum") and, except the moods, on their own ("im useless").
A_VERDICT_WORD = frozenset("""rubbish crap crappy shit shitty terrible awful dreadful bad
    useless worthless hopeless stupid thick dumb fat ugly""".split())


A_VERDICT_WITH_A_ROLE = "|".join(sorted(A_VERDICT_WORD, key=len, reverse=True))


# A judgement said with no role after it is the store's own list of them (`facts.SELF_JUDGEMENT`,
# the words it refuses as a job and as a name), so "im naff", "im pants", "im bollocks",
# "im muppet" and "im clown" are the same line as "im useless" instead of the shrug they got. One
# table for the readers that ask it: `facts._a_judgement_on_themselves` refuses the same words as
# a name, so the line cannot be called somebody Naff and then answered as a shrug.
# A word that is a thing as well is not served by the bare arm, because the arm would keep the
# thing and drop the noun after it ("im waste engineer" is a job): `waste` already has its own
# arm above, which needs the line to end there.
NOT_A_BARE_VERDICT = frozenset("waste mess wreck disaster".split())


A_VERDICT_SAID_ALONE = A_VERDICT_WORD | (facts.SELF_JUDGEMENT - NOT_A_BARE_VERDICT)


A_VERDICT_ON_ITS_OWN = "|".join(sorted(A_VERDICT_SAID_ALONE - A_MOOD_SAID_PLAINLY,
                                      key=len, reverse=True))


# A judgement about themselves, or about something being unfair, has no feeling word in it, so
# nothing that reads feelings claimed it: "im not good enough" reached the acknowledgement pool
# and got "Fair enough.", which reads as agreeing with them. These are the shapes people use, and
# each one is a feeling about the person saying it, not a fact to file.
OWN_WORTH = re.compile(
    r"\b(?:not (?:good|smart|clever|thin|pretty|strong|nice) enough|never (?:good )?enough|"
    r"a waste of space|nothing i (?:do|say) is (?:ever )?right|"
    r"no good at anything|rubbish at everything|bad at everything|"
    r"(?:nobody|no one) (?:likes|wants|needs) me|everyone hates me|i ruin everything|"
    # A judgement of themselves is "im useless" or "i feel like a failure", not "i feel
    # hopeless lately" - that is a mood, and the feeling pool answers a mood better than a
    # line telling someone they are being hard on themselves.
    r"\bfeel(?:ing)? like (?:such |a bit of |a right |a total |a complete )?a "
    r"(?:failure|letdown|burden|waste|disappointment|idiot|fool|joke|mug|fraud)|"
    # "i feel stupid", "i feel so thick", "i feel like an idiot": the same judgement as "im
    # useless", said with "feel" and a plainer word. The disparaging word is what makes it this
    # pool - "i feel ill", "i feel sick" and "i feel tired" are how the body is, not a verdict on
    # the person, and `_about_themselves` turns away "my head feels thick" (a cold).
    # "hopeless" is not one of these: "i feel hopeless" and "i feel hopeless lately" are a mood,
    # and the note above says so - the feeling pool answers a mood better. Main's "im ... hopeless"
    # arm below still reads "im hopeless".
    r"\bfeel(?:ing)? (?:so |really |pretty |very |like )?"
    r"(?:useless|worthless|stupid|thick|dumb|daft|clueless)\b|"
    r"^(?:im|i am|i m) (?:just |always |such |so |a bit |really |pretty |completely |totally )*"
    r"(?:a |such an? )?(?:(?:failure|letdown|burden|disappointment|joke|idiot|"
    r"useless|worthless|hopeless|nothing)\b"
    # "waste" names a job as often as it is a verdict, so it is one only when the line ends
    # there: "im a waste", "im such a waste" - not "im a waste engineer", which is what they do.
    r"|waste(?=\s*(?:[.,!?]|$)|\s+of\b))|"
    # The same judgement with the noun they say they are failing at: "im a rubbish mum", "im a
    # rubbish cook", "im a terrible dad", and the same line when someone else said it ("my mum
    # thinks im a rubbish mum"). The disparaging word is the judgement, so whatever role follows
    # it is the same line - and the role itself was answered as small news about a job ("Rubbish
    # mum - good to know. What do you like most about it?"), which is the last thing to ask a
    # parent who has just called themselves rubbish.
    r"\b(?:im|i am|i m)(?: (?:just|always|such|so|a bit|really|pretty|quite|completely|totally|"
    r"kind of|sort of))* (?:a |an |such an? )(?:" + A_VERDICT_WITH_A_ROLE + r")\b"
    # "im rubbish at mornings" is a skill they want help with, not a verdict on themselves: the
    # routiny answer ("work back from when you have to leave") is the useful one.
    r"(?!\s+at\b)|"
    # The same judgement with no role after it: "im useless", "im stupid", "im a right idiot".
    # The words that cannot be a mood are here; the ones that are a state more often than a
    # verdict are not, and `A_MOOD_SAID_PLAINLY` says which - see the note above it.
    r"\b(?:im|i am|i m)(?: (?:just|always|such|so|a bit|really|pretty|quite|completely|totally|"
    r"kind of|sort of))* (?:" + A_VERDICT_ON_ITS_OWN + r")\b(?!\s+at\b))")


# What a person says they are like, with nothing else in the line: "im lazy", "im so shy",
# "im a bit awkward", "im really selfish". These reached four different answers and none of them
# was a reply - "im lazy" and "i am lazy" were read as an introduction ("Nice to meet you,
# Lazy"), "im so shy" got the stock nod, "im quite shy" got "Got it.", "im really awkward" got
# "I'm sorry - that's frustrating", and "im a bit shy" got "Thanks for telling me". The words are
# the reading engine's one table (`lexicon.TRAITS`), and bot/memory/facts.py refuses the same
# words as a name, so the two cannot drift apart. A hedge in front is part of the same line: "a
# bit", "so", "really" and "quite" change how much of a trait they are claiming, not whether they
# are claiming one. "not" is not a hedge, so "im not lazy" - a person arguing with the idea - is
# left to whatever else can answer it.
OWN_TRAIT = re.compile(
    r"^(?:im|i'm|i am|i m)\s+(?:just |always |such |so |a bit |a bit of a |really |pretty |"
    r"quite |completely |totally |very |kind of |sort of )*(?:a |an |such an? )?(?:"
    + "|".join(sorted(lexicon.TRAITS, key=len, reverse=True)) + r")\b"
    # "im rubbish at mornings" and "im lazy at work" are a skill they want help with, and the
    # useful answer is the one that tells them what to do - the fence OWN_WORTH already keeps.
    r"(?!\s+[a-z]+\s+at\b)(?!\s+at\b)"
    # The trait has to be the line. "im so lazy i cant start anything" comes with a problem in
    # it, and the answer that helps is the one for the problem ("Shrink the job until it is
    # almost silly"), not a line telling them they are being hard on themselves. A laugh, a
    # "today" or a "though" after the trait is the same line; a clause after it is another one.
    r"(?:[,\s]+[a-z']+){0,3}\s*[.!?,]*$")


# ...except the trait that comes with the people it is about. "im shy with new people" and "im
# awkward with strangers" were answered with the card for meeting people ("Put your attention on
# the other person instead of on yourself..."), and the trait line took that away: a person who
# names the situation is asking what to do in it, not asking to be told what they are like. Only
# the traits that are about being among people are held back, and only when the line names the
# people - `im shy in groups` and `im impatient with my kids` are still the judgement, because
# nothing else answered the first and the second is about the person and not a skill.
SOCIAL_TRAIT_SETTING = re.compile(
    r"\b(?:shy|awkward|nervous|timid|self[- ]conscious|anxious)\b[^.!?]{0,30}?"
    r"\b(?:with|around|near|meeting|talking\s+to|in\s+front\s+of)\s+(?:\w+\s+){0,2}"
    r"(?:people|strangers?|folk|others|anyone|someone\s+new)\b")


# The same judgement said as an absolute about their record: "i get everything wrong", "im doing
# it all wrong", "i never get anything right", "i always mess everything up". These are the shapes
# people reach for when they cannot name a feeling, and every one of them was answered with a nod
# ("Got it. Is there anything you'd like a hand with?") while "im useless" got the warm line. The
# quantifier is what makes it this pool and not a fact about a thing: "the app gets it all wrong"
# has no person in it, and _about_themselves turns that away.
EVERYTHING_WRONG = re.compile(
    r"\b(?:"
    # "i get everything wrong", "im doing it all wrong", "i did all of it wrong". Only "wrong":
    # "im doing everything right" is the good news it sounds like, and it must stay a nod.
    r"(?:do|does|doing|did|get|gets|getting|got)\s+"
    r"(?:everything|it all|all of it)\s+wrong"
    r"|"
    # "i cant do anything right", "i never get anything right"
    r"(?:can(?:t|not)|couldnt|never)\s+(?:do|get|make|does|gets|makes)\s+anything\s+right"
    r"|"
    # "i cant even do the basics right", "i cant even get that right". The verb has to be one of
    # doing or getting: "i cant even walk right" is a leg, not a verdict on the person.
    # "right now", "right away" and "right here" are the adverb, not the verdict: "i cant even
    # get it right now" is a bad moment today and keeps its own answer.
    r"can(?:t|not)\s+even\s+(?:do|get|make|say|keep)\s+(?:[a-z]+ ){0,3}"
    r"right(?![a-z])(?! (?:now|away|here|there|then)\b)"
    r"|"
    # "i never finish anything", "i never finish what i start": a verdict on what they get done,
    # in the same shape as the rest of this pool. A task names its own end ("i never finish work
    # before six"), so only the quantifier makes it the judgement.
    r"never\s+(?:finish|finishes|finishing|complete|completes)\s+"
    r"(?:anything|what i (?:start|begin|begin)|a thing|things)"
    r"|"
    # "everything i do goes wrong", "nothing i say is right": the quantifier carries the sense, so
    # "right" only counts after "nothing" and "wrong" after either of them.
    r"(?:everything|anything)\s+(?:i|we)\s+"
    r"(?:do|did|say|said|make|made|touch|try|get)\s+"
    r"(?:is|was|goes|went|turns|turned)\s+(?:wrong|bad|badly)"
    r"|"
    r"nothing\s+(?:i|we)\s+(?:do|did|say|said|make|made|try|get)\s+"
    r"(?:is|was|goes|went|turns|turned)\s+right"
    r"|"
    # "i always mess everything up", "i messed it all up"
    r"mess(?:es|ed|ing)?\s+(?:everything|it all|all of it)\s+up"
    r")\b")


# The judgement said as unfitness for the thing in front of them: "im not cut out for this job",
# "i dont think im cut out for nursing". It is the same pool as "im useless" - the engine reads the
# line as how they see themselves (`topics.reads_as_unfit`), and answered as a fact about the job
# it is "Got it. Is there anything you'd like a hand with?" to a person who has just said they
# cannot do the thing they are doing all day.
#
# A judgement with the comparison in it: "i feel like a bad dad", "i feel like an idiot". The
# person names a role or a noun and measures themselves against it, which is the hardest thing
# to read back to them: the store used to answer "Noted: you feel like a bad dad." The plain
# "wrong" words (failure, letdown, burden) stay with OWN_WORTH below, which already answers them.
OWN_HARSH = re.compile(
    # the "im" form says the same thing: "i feel like im a bad mum" is a person measuring
    # themselves against a role, and without this it fell to the plain read-back ("Noted: you feel
    # like you're a bad mum") while the shorter form got the reply that names the standard.
    r"\bfeel(?:ing)? like (?:(?:im|i'?m|i am) )?"
    r"(?:such |a bit of |a bit like |kind of |a right |an? )?"
    r"(?:idiot|fraud|fool|mess|disaster|"
    r"bad (?:mum|mom|dad|mother|father|parent|person|friend|partner|husband|wife|son|daughter)|"
    r"(?:rubbish|terrible|awful|useless|hopeless) (?:mum|mom|dad|mother|father|parent|"
    r"person|friend|partner|husband|wife|son|daughter))\b"
    r"|\bfeel(?:ing)? like (?:(?:im|i'?m|i am) )?the worst (?:mum|mom|dad|mother|father|parent|"
    r"person|friend|partner|"
    r"husband|wife|son|daughter)(?: in the world)?\b"
    r"|\bfeel(?:ing)? like (?:im|i am|i m) (?:failing|useless|worthless|no good)\b"
    r"|\b(?:im|i am|i m) (?:just |such |a bit of |a right )*(?:an? )?"
    r"(?:idiot|fraud|fool|mess|disaster)\b"
    # The same judgement said with a role after it: "im a bad mum", "im an awful father",
    # "im a rubbish friend", "im a lazy student", "im a hopeless cook". Without the "feel like"
    # in front, the role was read as a job or a person they know and read back flat: "Bad mum —
    # good to know. What do you like most about it?" to someone saying they are failing at the
    # thing they care about. Any noun counts, because the disparaging word is what makes the
    # line a verdict rather than news, and the words that are a judgement about a day rather
    # than the person are left out ("an awful lot better", "a terrible week").
    r"|\b(?:im|i am|i m)\s+"
    # How people say it: the article and the qualifiers move around. The reading above only took
    # a rating word straight after the article, so "im a fairly poor friend", "im quite a poor
    # dad", "im a really lousy cook" and "im such a crummy dad" fell through to the role-news
    # question ("Fairly poor friend — good to know. What do you like most about it?") or to the
    # store reading the line back flat. The article is still required - "im rubbish at maths" is
    # a skill, not a role - and the word after the rating is still the noun.
    r"(?:also |just |such |quite |pretty |really |very |so |totally |completely |proper |fairly |"
    r"a bit of |a right )*"
    r"(?:an? )"
    r"(?:(?:pretty |quite |really |very |so |fairly |totally |completely |proper |right |"
    r"a bit of a |a bit |such a |kind of a ))*"
    r"(?:bad|terrible|awful|horrible|rubbish|rubbishy|useless|hopeless|lazy|selfish|stupid|lousy|"
    r"naff|rotten|dreadful|crap|crappy|crummy|shit|poor)"
    # The word after the rating has to be a role or a doing. A qualifier in front of the rating is
    # how the sentence is said, but it also lets the frame catch a line about how somebody is
    # rather than what they are: `im a really bad way today`, `im a really bad place`, `im a really
    # poor sleeper` and `im a really bad pain` were answered by the judgement pool - "Half the
    # people you know would say the same about themselves" to a person in a bad place. The words
    # below are the states of a person (a stretch of time, a mood, a place, a body), the same fence
    # `facts.NOT_A_JUDGEMENT_AFTER` keeps for the store's reading.
    r"\s+(?!(?:lot|bit|deal|day|days|week|weekend|month|year|time|times|mood|thing|things|"
    r"while|way|ways|place|places|shape|state|condition|health|pain|pains|ache|nights?|"
    r"shame|pity|job)\b)[a-z]+\b")


# The judgement said as what they did to someone close: "i let my mum down", "i keep letting
# everyone down", "i let myself down". Not one word of it is a feeling word, so the line was filed
# as a fact about them and said straight back - "Noted: you let my mum down" - while the same
# judgement said as "im useless" got the warm line. The persons are named, so "i let my hair down"
# and "i let the dog out" stay the facts they are, and "he let me down" is what was done to them.
LET_SOMEONE_DOWN = re.compile(
    r"\b(?:let|letting)\s+(?:everyone|everybody|people|myself|him|her|them|my\s+(?:mum|mom|"
    r"mother|dad|father|wife|husband|partner|son|daughter|kids?|children|family|friends?|"
    r"sister|brother|nan|gran|boss|team|mates?))\s+down\b"
    r"(?!\s+(?:gently|easy|easily|softly))",
    re.I)


# A thing that keeps failing is a fault to fix, not a verdict on the person: "my bread keeps
# failing" is a baking question and was answered "you're being harder on yourself than you'd be
# on a friend", because this phrase was matched whatever the subject was. The words in front of
# the phrase are what say whose failing it is, so the phrase is a judgement only when the person
# is the one at it ("i keep failing", "we keep making mistakes") or when the line names no
# subject at all ("keep making mistakes").
KEEPS_FAILING = re.compile(
    r"\bkee(?:p|ps|ping)\s+(?:making\s+mistakes|failing|letting\s+(?:people|everyone)\s+down)\b",
    re.I)


# The subject that makes the failing somebody else's: the person says what they own ("my bread",
# "the boiler", "our car") or they name another person ("he keeps failing", "she keeps letting
# people down"). Both are reports, and the line asks for help rather than comfort.
NOT_THE_PERSONS_OWN = frozenset("""my our the his her their your a an this that these those
    it he she they""".split())


SELF_SUBJECT = frozenset("""i im i'm ive i've me myself we us""".split())


def _keeps_failing_theirs(clean):
    """The phrase, when what keeps failing is the person rather than something of theirs.

    "i keep failing" and "keep making mistakes" are about the speaker. "my bread keeps failing"
    is about the bread, and "he keeps failing" about him, so neither is the pool for somebody
    who is being hard on themselves. The match is returned, not a yes: the caller asks the match
    where the judgement is (`_asks_after`), so the answer keeps the shape it had.
    """
    for match in KEEPS_FAILING.finditer(clean or ""):
        before = re.findall(r"[a-z']+", (clean or "")[:match.start()].lower())[-3:]
        if not any(word in NOT_THE_PERSONS_OWN for word in before):
            return match
        if any(word in SELF_SUBJECT for word in before):
            return match
    return None


def _letting_someone_down(clean):
    """Whether the line is the person letting someone down, or failing at what they are at."""
    return LET_SOMEONE_DOWN.search(clean or "") or _keeps_failing_theirs(clean)


# The noun after the word is what decides how hard the line is, and the list lives with the store
# reading (`bot/memory/facts.py`, ROLE_YOU_CAN_FAIL) so the two can never disagree.
ROLE_YOU_CAN_FAIL = facts.ROLE_YOU_CAN_FAIL


NOT_FAIR = re.compile(
    r"\b(?:(?:not|isnt|wasnt|so|just|totally|really|bloody|damn) (?:so |really |just )?fair|unfair|"
    r"not fair at all|how is that fair)\b")


NOT_GREAT = re.compile(
    r"^(?:and |oh |well |honestly |tbh |to be honest |yeah |yes |god |urgh |ugh )*"
    r"(?:(?:that|thats|that s|this|this s|it|its|it s|life|today|work|everything|the day)"
    r"(?:\s+(?:is|isnt|was|wasnt|s))?\s+)?"
    r"(?:not|isnt|wasnt)(?:\s+(?:that|too|really|very|so|all that))?\s+"
    # "not well" and "not myself" are the same judgement as "not great", and they were reaching
    # the no pool instead: "No worries - say if you change your mind" to somebody who had just
    # said they were unwell. "not right" is the same answer with the meaning left to the context.
    r"(?:great|good|ideal|ok|okay|fine|brilliant|well|right|myself|amazing)"
    r"(?:\s+(?:at all|honestly|tbh|to be honest|though|tho|really|either|today|this week))?[!. ]*$")


# A line that starts with one of these is a question about something, not a judgement: "is it not
# fair to ask for a refund" is asking for the rule, not saying their luck is bad.
ASKS_A_QUESTION = {"is", "are", "was", "were", "am", "do", "does", "did", "can", "could",
                   "should", "would", "will", "shall", "may", "might", "how", "why", "what",
                   "when", "where", "who", "whose", "which", "isnt", "arent", "wasnt",
                   "werent", "doesnt", "didnt", "dont", "cant", "couldnt", "wouldnt",
                   "shouldnt"}


# A judgement of themselves is said of the person: "im not good enough" is, and "the wifi is not
# good enough" is about a thing, which the store or the answers lane should answer.
SELF_WORDS = frozenset(("i", "im", "me", "myself"))


def _about_themselves(tokens):
    """Whether a line carries the person as its subject, or nothing but the judgement itself."""
    if len(tokens) <= 4:
        return True
    return bool(SELF_WORDS & set(tokens))


# The person says it was *they* who were unfair, not their luck: "i wasnt fair to you" is an
# apology, and answering it with "you're right that it isn't fair" agrees with the wrong thing.
# Nothing but the judgement itself ("not fair", "unfair") is told off; the subject in front of it
# decides who was unfair. A third-person word after the person means the unfairness is someone
# else's again ("i dont think its fair").
FIRST_COPULA = frozenset(("i", "im", "i'm", "ive", "i've", "we", "we're", "were", "weve"))


# Words in front of the apology that say nothing about who was unfair: "sorry i wasnt fair".
LEAD_IN_JUDGEMENT = frozenset(("sorry", "so", "but", "and", "well", "oh", "yeah", "ya", "honestly",
                               "tbh", "actually", "really", "just", "no", "hi", "hey", "ok",
                               "okay", "right", "look", "god", "urgh", "ugh", "still"))


NOT_FAIR_WORDS = frozenset(("not", "never", "wasnt", "wasn't", "isnt", "isn't", "arent", "werent",
                            "weren't", "unfair", "unfairly", "being"))


OTHER_SUBJECT = frozenset(("it", "its", "it's", "that", "thats", "that's", "this", "life",
                           "everything", "work", "they", "he", "she", "people"))


def _themselves_unfair(tokens):
    """Whether the line says the person themself was unfair, rather than their luck."""
    for at, word in enumerate(tokens):
        if word not in ("fair", "unfair"):
            continue
        window = tokens[max(0, at - 4):at]
        while window and window[0] in LEAD_IN_JUDGEMENT:
            window = window[1:]
        if not window or window[0] not in FIRST_COPULA:
            continue
        if any(word in OTHER_SUBJECT for word in window[1:]):
            continue
        if word == "unfair" or any(item in NOT_FAIR_WORDS for item in window):
            return True
    return False


# A line that is nothing but a reaction to what was just said. The shape is a pronoun standing
# for the last turn ("that", "this", "it"), the copula people drop ("thats scary") and a word
# for how the news lands. The words are grouped by the feeling they show, because agreeing with
# fear, bad news and a nuisance are three different replies.
REACTION_WORDS = {
    "scary": "fear", "frightening": "fear", "terrifying": "fear", "worrying": "fear",
    "unsettling": "fear", "daunting": "fear", "petrifying": "fear", "horrifying": "fear",
    "grim": "bad", "awful": "bad", "horrible": "bad", "dreadful": "bad",
    "terrible": "bad", "tough": "bad", "rough": "bad", "rubbish": "bad",
    "gutting": "bad", "sad": "bad", "devastating": "bad", "heartbreaking": "bad",
    "shit": "bad", "crap": "bad", "brutal": "bad",
    "annoying": "annoyed", "frustrating": "annoyed", "irritating": "annoyed",
    "infuriating": "annoyed", "maddening": "annoyed",
    # Worn out is not cross: "my son wont sleep" / "so exhausting" was met with "Being cross about
    # it for a bit is fair enough", which answers a different feeling.
    "exhausting": "tired", "exhausted": "tired", "knackering": "tired", "draining": "tired",
    # The other way round: the news was good, or the answer was a help.
    "great": "good", "brilliant": "good", "amazing": "good", "lovely": "good",
    "wonderful": "good", "fantastic": "good", "excellent": "good", "superb": "good",
    "ace": "good", "exciting": "good", "good": "good", "nice": "good", "cool": "good",
    "perfect": "good", "ideal": "good", "handy": "good", "useful": "good", "helpful": "good",
    "funny": "funny", "hilarious": "funny",
}


# Breathers people put in front of a reaction ("oh god thats scary", "yeah thats grim").
# "what a blow", "what a shame", "what a nightmare": the same reaction said with a thing in it
# rather than a word for the feeling. The shape is "what a <thing>", the thing is the news, and
# which pool it takes is what the thing is - a blow, a shame and a nightmare are all bad news, a
# relief is the other way. None of them carries a subject of its own, so without this reading the
# line matched nothing and reached the floor's search hedge: "my husband lost his job" then "what
# a blow" was answered "I don't know enough to answer that honestly. A search should sort you out
# quickly." A thing that a person can be glad of is read as good news for the same reason.
REACTION_WHAT_A = {
    "blow": "bad", "shame": "bad", "pity": "bad", "nightmare": "bad", "disaster": "bad",
    "mess": "bad", "tragedy": "bad", "horror": "bad", "letdown": "bad", "downer": "bad",
    "bummer": "bad", "state": "bad", "joke": "bad", "slog": "bad", "carry on": "bad",
    "shock": "fear", "scare": "fear", "fright": "fear",
    "relief": "good", "result": "good", "find": "good", "bargain": "good", "treat": "good",
}


REACTION_LEAD = frozenset("""oh ah god jesus christ yeah yep yup honestly well and but blimey
bloody hell damn wow urgh ugh man mate really just so proper fucking""".split())


# Words people put after the reaction word without adding a thing of their own.
REACTION_TAIL = frozenset("""though tho honestly tbh really stuff mate isnt it hey eh""".split())


REACTION_SUBJECT = frozenset("that thats this it its".split())


REACTION_COPULA = frozenset("is was s sounds seems feels look looks".split())


REACTION_HOW = frozenset("how so very proper pretty really that that s thats".split())


# A sigh in front of the news: "oh no", "oh dear", "aw god". There is no subject and no
# feeling word, so nothing else in this file reads them, and they are sympathy with the turn
# before - never a line of their own, which is why the first-turn guard above still holds.
REACTION_SIGH = frozenset("oh aw ah ooh".split())


REACTION_SIGH_WORD = frozenset("""no dear god christ jesus jeez jaysus hell help
nasty bugger blimey""".split())


# A bare word of approval has no news in it at all: "lovely", "brilliant" is a reaction to the
# good news in the turn before, and on its own it would be a reply to nothing. So it counts only
# when that line does read as good news (bot/compose/goodnews.py), which is the thing it is
# agreeing with.
REACTION_BARE_GOOD = frozenset("""lovely brilliant great amazing fantastic wonderful excellent
superb ace fab smashing magic perfect marvellous marvelous cracking
terrific""".split())


# The same shape the other way: "hilarious" on its own after something that was funny, with no
# subject and no news of its own.
REACTION_BARE_FUNNY = frozenset("hilarious funny hysterical".split())


def _a_thread_to_come_back_to(memory):
    """True when the person and the bot have already been talking.

    "im back" as the very first line is not a return to anything: nothing has been said yet, and
    the opening was answered "Back again. What were we saying?" - a question about turns that
    never happened. It is the same fault as a first reply saying "Where were we?".
    """
    # One check, in bot/memory/thread.py, so every reply that points back asks the same
    # question; a module that forgets it would readmit the fault this guards.
    return thread.earlier_turn(memory)


def _news_before(memory):
    """The last thing the person said, which is what a line of nothing but reaction reacts to."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    said = [turn for turn in (turns or []) if isinstance(turn, dict)]
    return str((said[-1].get("user") if said else "") or "").lower()


def _nobody_would_call_it_nice(said):
    """True when the turn before is news no cheerful word can be about.

    "my dad died last week" met with "thats nice" deserves an answer about the death, not a
    "Nice one": the reaction word says how the person is holding it, not what happened.
    """
    if not said:
        return False
    return bool(loss_reading.reads_as_loss(said) or loss_reading.a_pet_died(said)
                or badnews.reads_as_sudden_loss(said) or reads_as_bad_news(said))


# The pools that say the news is good. A cheerful reaction word is about the turn before, and the
# turn before can be a death: the word has to be met with the news it is about, not with a cheer.
REACTION_CHEERFUL = frozenset({"react_good", "react_funny"})


# The lines that say nothing but "the same as you". Company is in here too ("us too", "you and
# me both"): two people with the same trouble say it the same way. A word that agrees with the
# *bot* rather than with the person ("exactly", "agreed", "you too") is left out on purpose: the
# agreement here is about the last thing the person said, so "you too" after "have a nice day"
# and "exactly" after the bot's own question would be answered about the wrong thing.
AGREEMENT_ONLY = re.compile(
    r"^(?:yeah |yep |ha |haha |oh |aw )?"
    r"(?:me too|me as well|me neither|same here|same as me|so am i|so do i|so can i|so have i|\s*"
    r"so did i|so would i|nor me|neither do i|neither am i|us too|us both|you and me both|\s*"
    r"join the club|welcome to my world|i know right)"
    r"(?: then| too| as well| honestly| actually| indeed)?[\s.,!?]*$", re.I)


# The everyday ways a complaint is worded, so an agreement with one gets the line that is about
# the trouble rather than the one that congratulates them.
GRUMBLE = re.compile(
    r"\b(?:shattered|knackered|exhausted|wiped out|tired|fed up|sick of|hate|hates|cant stand|\s*"
    r"can't stand|doing my head in|does my head in|driving me mad|killing me|hurts|hurting|aching|\s*"
    r"aches|freezing|so cold|pouring|rained off|long day|rough day|grim|awful|rubbish|dreadful|\s*"
    r"nightmare|worn out|drained|stressed|worried|skint|broke|bored|lonely|struggling|\s*"
    r"not great|not good|not brilliant|not the best|no fun|a nightmare|hard work)\b", re.I)


# A complaint about the weather is the one grumble where "it gets into everything" is true of
# the thing itself: cold, heat, rain and pollen do get into everything. Said about a bad back or
# a stressful week the same line is nonsense, so the agreement picks the pool on this.
WEATHER = re.compile(
    r"\b(?:cold|freezing|freezing cold|chilly|frost|snow|snowing|rain|raining|pouring|wet|wind|"
    r"windy|storm|heat|hot|boiling|muggy|humid|sticky|damp|dark|grey|gloomy|pollen|hay ?fever|"
    r"weather|summer|winter|autumn|spring|mornings|evenings)\b", re.I)


def _the_agreement_pool(memory):
    """Which agreement line the turn before earns: grim, good, a loss, or plain news.

    The agreement is about the thing they said, so the thing they said chooses it. A death is
    not something to be cheerful about and not something to swap stories about, so it has its
    own two lines; a complaint gets the nod that says they are not alone in it.
    """
    said = _news_before(memory)
    if not said:
        return None
    # An emergency is not something to be "me too" about, and the safety thread's own answer is
    # the one that knows what to say: the agreement lines stay out of it.
    if _safety_thread(memory):
        return None
    if (loss_reading.reads_as_loss(said) or loss_reading.a_pet_died(said)
            or badnews.reads_as_sudden_loss(said)):
        return "agree_loss"
    if reads_as_good_news(said) or reads_as_a_pass(said):
        return "agree_good"
    if reads_as_bad_news(said) or GRUMBLE.search(said):
        if WEATHER.search(said):
            return "agree_weather"
        return "agree_grim"
    return "agree_plain"


# "i feel stupid but i got the job": somebody's news with a shrug in front of it. The warm
# "harder on yourself" line buries the thing they came to say, so a line that reports a result -
# good or bad - keeps its news answer and the judgement is not taken. "i feel dumb but i failed"
# is the other side of the same shape, and its own pool says the failure out loud, which is more
# use than a line about self-esteem. goodnews.py's own reader refuses a line with "but" in it
# (its BAD list counts the word), so the clause after the turn is asked on its own, and the
# person's plain "but i did it" is here because no result pattern covers it.
GOOD_NEWS_TURN = re.compile(r"\b(?:but|though|although|except)\b(.*)$", re.I)


OWN_WIN = re.compile(r"\b(?:i|we)\s+(?:still |actually |finally |eventually |just |also )?"
                     r"(?:did it(?! again)|managed it|managed to|got through it|made it|"
                     r"got there|won|passed)\b"
                     r"|\b(?:i|we)\s+(?:got|landed)\s+(?:the|a|my|our)\s+"
                     r"(?:job|promotion|offer|pay rise|raise|place|role|part)\b", re.I)


# The other side of the same shape: "i feel dumb but i failed", "i feel stupid, i did it again".
# badnews.py reads the shapes it knows ("i lost my job", "i failed the test"); a bare "i failed"
# after a shrug is not one of them, and the failure is the thing to answer.
OWN_SETBACK = re.compile(r"\b(?:i|we)\s+(?:just |still |actually |probably |really )?"
                         r"(?:failed|messed it up|messed up|did it again|blew it)\b", re.I)


def _turns_on_news(clean):
    """True when the line reports a result of the person's: "i passed", "but i failed"."""
    if (reads_as_a_pass(clean) or reads_as_good_news(clean) or OWN_WIN.search(clean)
            or OWN_SETBACK.search(clean) or reads_as_bad_news(clean)):
        return True
    for match in GOOD_NEWS_TURN.finditer(clean):
        tail = match.group(1)
        if (reads_as_a_pass(tail) or reads_as_good_news(tail) or OWN_WIN.search(tail)
                or OWN_SETBACK.search(tail) or reads_as_bad_news(tail)):
            return True
    return False


# The ask a run-on line puts after the judgement: "im a fat guy what exercise should i do", "im
# useless at my job what should i do". Comforting the whole person buries the question they asked,
# and the question is the part somebody can act on. Only an ask that comes after the judgement
# counts: "what should i do, im useless" is a person who has already said the hard part.
# Only a how-to ask counts. "what can i do" and "what do i do" are the person saying they are
# out of ideas, and those lines want the comfort, not a plan.
ASKED_AFTER = re.compile(
    r"\b(?:how (?:do|can|should|would|could) i|how do you|should i|shall i|"
    r"do i need|what should i|which should i|what exercise|what can i do about|"
    r"what would you (?:do|suggest|recommend)|any (?:advice|tips)|advice on|tips on)\b")


def _asks_after(clean, judged):
    """True when the line asks something after the judgement: "im a fat guy what should i do"."""
    ask = ASKED_AFTER.search(clean)
    return bool(ask and ask.start() > judged.end())


# A noun that only exists in a judgement of oneself, said as what the person *is*: "im a
# doormat", "im the joke of the family", "everyone thinks im a joke". It was filed as a job -
# "im a doormat" gave {"job": "doormat"} - and read back as "Noted: you're a doormat.", which is
# the coldest answer there is to somebody saying what they think of themselves. The tests are the
# word and the shape: "i love a joke" has the same words and is not a judgement, and "im a problem
# solver" uses the noun to describe what they do, so the noun has to be the end of the phrase or
# the start of the reason for it ("a problem for my team at work").
# When the phrase after the noun is a time, it says when the person does the thing, not why they
# think badly of themselves: "im a clown at the weekends" is what somebody does for money, and the
# warm "harder on yourself" line would be answering a judgement nobody made.
JUDGEMENT_TIME = frozenset("""weekend weekends night nights day days morning mornings evening
evenings afternoon afternoons monday tuesday wednesday thursday friday saturday sunday
summer winter christmas""".split())


SELF_COPULA = frozenset(("im", "i'm", "i am"))


def _when_not_why(rest):
    """Whether what follows the judgement noun is a time ("at the weekends", "on fridays")."""
    if len(rest) < 2 or rest[0] not in ("at", "on", "after", "before", "during", "every"):
        return False
    named = [word for word in rest[1:] if word not in ("the", "a", "an")]
    return bool(named) and (named[0] in JUDGEMENT_TIME or named[0][:-1] in JUDGEMENT_TIME)


# The dirty words people use for their own work, which are judgements wherever they are said
# about the speaker: "im a shit driver", "im a crap cook".
HARSH_WORDS = frozenset("""
bad terrible awful horrible rubbish rubbishy useless hopeless lazy selfish stupid lousy naff
rotten dreadful crap crappy crummy shit poor
""".split())


def _judged_a_role(clean):
    """Whether the judgement's noun is a role with somebody on the other side of it.

    "im a bad mum" and "im a shit driver" are verdicts on a job done for other people; "im a
    terrible dancer" and "im a bad sleeper" are a habit being described, and the hard pool tells
    that person their day weighs on their life. A judgement with no noun at all - "im an idiot" -
    is an insult and keeps the hard pool.
    """
    match = OWN_HARSH.search(clean or "")
    if not match:
        return True
    words = re.findall(r"[a-z']+", match.group(0).lower())
    for index, word in enumerate(words):
        if word in HARSH_WORDS and index + 1 < len(words):
            return words[index + 1] in ROLE_YOU_CAN_FAIL
    return True


DONT_KNOW_WORDS = {"idk", "dunno", "dont", "know", "not", "sure", "maybe", "unsure"}


BYE_CORE = {"bye", "byebye", "goodbye", "goodnight", "night", "cya", "cheerio", "later",
            "toodles", "nightnight"}


BYE_FILLER = {"bye", "byebye", "goodbye", "goodnight", "night", "cya", "cheerio", "later",
              "need", "must", "anyway", "off", "going", "heading", "leaving", "soon",
              "im", "to", "cool", "so", "then", "now", "bed",
              "toodles", "nightnight", "see", "you", "u", "ya", "soon", "then", "now", "all",
              "everyone", "good", "take", "care", "ok", "thanks", "thx", "cheers", "for",
              "help", "the", "and", "i", "gotta", "go", "off", "got", "to", "sleep", "bed",
              "morning", "mate", "folks", "guys", "have", "nice", "one", "day", "speak",
              # Breathers people put in front of a goodbye: "right, i'm going now",
              # "ha, fair enough. talk later", "alright, night then".
              "right", "alright", "ha", "haha", "fair", "enough", "well", "talk", "catch",
              "tomorrow", "ill", "lets",
              # And the sounds of a chat: "lol ok bye" and "yeah bye then" are goodbyes, and
              # every word of a goodbye has to be one the line can be built from, so the
              # sounds are on this list too - "lol" and "yeah" were not, and both fell through
              # to the pool for a disclosure ("Thanks for telling me").
              "lol", "lmao", "rofl", "yeah", "yep", "yup", "okay", "kk", "ah", "oh",
              "hmm", "mm", "anyways", "anyhoo", "gonna", "gunna",
              # People sign a goodbye off with a kiss: "night then x", "catch you later xx".
              "x", "xx", "xxx",
              # The way out of a chat when the person is not going far: "back in a bit",
              # "speak in a bit", "sweet dreams", "im out", "gonna head off". Every word of
              # these was outside the set, so each one fell through to the pool for a
              # disclosure ("Thanks for telling me - I'm here if you want to dig into any of
              # that.") or to a nod. The words are only the ones those sign-offs are built
              # from, and a goodbye still has to be nothing but them.
              "head", "back", "in", "a", "bit", "sec", "mo", "min", "minute", "shortly",
              "sweet", "dreams", "out", "let", "am"}


# The laughs above are only the three that came up first. The rest of the spellings in
# `LAUGH_WORDS` are the same sound in front of a goodbye, and "hehe bye then" went on falling
# through to the pool for a disclosure ("Thanks for telling me"), so the goodbye reads the whole
# list the laugh does rather than keeping a second copy of it (@rose-wasp, on 06be6b1f).
BYE_FILLER |= LAUGH_WORDS


# "in a bit", "in a mo" and "in a sec" are the same time to leave as "soon", so a line that
# talks or sees you at one of them ("speak in a bit", "catch u in a bit") is a goodbye.
BYE_TIME = {"soon", "later", "tomorrow", "bit", "mo", "sec", "min", "minute", "shortly"}


BYE_VERB = {"talk", "speak", "catch", "see"}


SMILES = {":)": " smile ", ":-)": " smile ", ":(": " sad ", ":-(": " sad ", "<3": " love ",
          ":d": " haha ", ";-)": " wink ", "; )": " wink ", ":/": " meh ", ":|": " meh "}


JOKE_ASK = re.compile(
    r"\b(tell|give|know|got|say|hear)\b[^.!?]{0,25}\bjokes?\b|\bmake me laugh\b|"
    r"\bsomething funny\b|\bcheer me up\b|^joke\b")


# Asked for a joke outright: a joke is the answer even when the line also names a film or a book.
JOKE_ASKED = re.compile(r"\bjokes?\b|\bmake me laugh\b|\bcheer me up\b|\bpun\b|\bridge\b")


# A length is a request about a film, not a joke: "something funny under two hours" and
# "something funny under 90 minutes" are the evening's runtime, and a pun has none. Only the
# limits that name a length, so "say something funny in a minute" is still a joke.
RUNTIME_LIMIT = re.compile(
    r"\b(?:under|less than|no longer than|shorter than|max|at most)\s+"
    r"(?:\d{1,3}\s*(?:min|mins|minutes?|hours?|hrs?)\b|an? hour\b|two hours\b|"
    r"three hours\b|half an hour\b|an? hour and a half\b)"
    # "but short" and "that isnt long" are the same limit without a number: a pick for the
    # evening, and nobody asks a punchline to keep it short
    r"|\b(?:but|and|that is|thats) short\b|\b(?:isnt|is not) (?:too )?long\b",
    re.IGNORECASE)


# A pick from the telly, the shelf or the player. "Something funny to watch" asks for a film,
# not for a joke, so the joke line must not take it.
# A line that asks *about* jokes - whether one belongs, whether it is risky, whether it would
# land - wants advice, not a punchline. "wot about jokes, is that risky" in a wedding speech, and
# "is it ok to tell a joke at a wedding", were both answered with a joke about atoms.
JOKE_ADVICE = re.compile(
    r"\b(?:should (?:i|we)|shall i|is it|is that|are they|would it|will it|do you think|"
    r"what about|wot about|how about)\b[^.!?]{0,30}\bjokes?\b|"
    r"\bjokes?\b[^.!?]{0,30}\b(?:risky|appropriate|a good idea|too risky|worth it|land|"
    r"offend|offensive|rude|safe|ok|okay|fine|alright|allowed)\b")


PICK_WORDS = frozenset("""
    watch watching watched film films movie movies cinema show shows series episode netflix
    telly tv boxset sitcom standup stand comedy read reading book books novel novels audiobook
    listen listening podcast podcasts album albums music playlist gig
""".split())


# A want of something in a mood ("im in the mood for something funny"), as against a joke asked
# for by name ("say something funny"): the first is a pick in whatever medium the chat is on when
# the chat is already on one, the second is a joke whatever came before it.
WANTS_A_THING = re.compile(
    r"\b(?:in the mood|in a mood|mood for|fancy|fancied|want|wanted|feel like|feeling like|"
    r"up for|something to|after a|after some)\b")


ASKS_ALOUD = re.compile(
    r"\b(?:tell|say|give|got|hear|make me laugh|cheer me up|another|one more)\b")


JOKES = {
    "cheese": "What do you call cheese that isn't yours? Nacho cheese.",
    "fish": "Why don't fish play tennis? They're scared of the net.",
    "dog": "Why did the dog sit in the shade? He didn't want to be a hot dog.",
    "cat": "What do you call a cat that swallowed a lemon? A sourpuss.",
    "computer": "Why do programmers prefer dark mode? Because light attracts bugs.",
    "book": "I'm reading a book about anti-gravity. It's impossible to put down.",
    "music": "Why did the musician get arrested? For drumming up business.",
    "work": "I told my boss I needed a break. He said I'd only been there five minutes. I said yes, but it felt like hours.",
    "egg": "Why don't eggs tell jokes? They'd crack each other up.",
    "food": "What do you call a fake noodle? An impasta.",
    "car": "Why did the bicycle fall over? It was two-tired.",
    "animal": "How does a penguin build its house? Igloos it together.",
}


SHORT_JOKES = (
    "Why don't scientists trust atoms? They make up everything.",
    "I used to be a banker, but I lost interest.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I only know 25 letters of the alphabet. I don't know y.",
    "What's orange and sounds like a parrot? A carrot.",
    "I'd tell you a construction joke, but I'm still working on it.",
    "What do you call a sleeping bull? A bulldozer.",
    "Why did the golfer wear two pairs of trousers? In case he got a hole in one.",
)


# Words that follow "i'm a" and are not a role to chat about. "nobody", "nothing" and "failure"
# are the person judging themselves, and "Nobody - good to know. What do you like most about it?"
# is the last reply anyone wants for "im a nobody".
ROLE_STOP = {"bit", "little", "lot", "mess", "fan", "big", "huge", "total", "complete", "real",
             "very", "so", "really", "grown", "vegetarian", "vegan", "good", "bad", "terrible",
             "great", "wreck", "disaster", "beginner", "bit", "nobody", "nothing", "failure",
             "loser", "idiot", "muppet", "moron", "fool", "clown",
             # A noun that only exists in a judgement of oneself. "im a burden to everyone" is
             # the same shape as "im a nurse" to the pattern below, and it was answered
             # "Burden to everyone — good to know. What do you like most about it?" - the
             # chipper reply for news, given to the one line that most needs an ear.
             "burden", "joke", "doormat", "letdown", "disappointment", "waste", "problem",
             "mistake", "nuisance", "embarrassment", "fraud", "imposter", "impostor",
             "hypocrite", "rubbish", "crap", "crappy", "shit", "shitty",
             "awful", "dreadful", "useless", "worthless", "hopeless", "stupid",
             "thick", "dumb", "fat", "ugly"}


# A judgment is not a role, and the two ways people write one are worth their own patterns: the
# noun is compared rather than stated ("i feel like im a burden", "she made me feel like a
# failure"), or it is said to be what the person is to other people ("a burden to everyone",
# "a joke to them"). Both are about how they feel, not about what they do all day.
COMPARED_ROLE = re.compile(r"\b(?:feel|feels|felt|feeling|make|makes|made|like)\s+"
                           r"(?:like\s+)?(?:im|i am|i'm|me|myself|being)\b")


ROLE_TO_PEOPLE = re.compile(r"\bto (?:everyone|everybody|anyone|anybody|people|them|him|her|"
                            r"family|the family|everyone else|my \w+)\b")


ROLE = re.compile(r"\bim an? ([a-z]+(?: [a-z]+){0,2}?)(?: in ([a-z]+(?: [a-z]+){0,2}))?\s*$")


ROLE_WORK = re.compile(r"\bi work as an? ([a-z]+(?: [a-z]+){0,2}?)\s*$")


# How old they are does not stop the job being a job: "im 34 and a nurse", "im 45, a plumber" and
# "i am 30 and a chef" reached the neutral nod ("Got it. Is there anything you'd like a hand
# with?") while "im a nurse" was answered as the job it is. The age is dropped from the front of
# the line only, never from the memory, and ROLE below reads what is left.
# The words a measure or a fraction starts with: "im 7 and a half", "im 6 and a half months",
# "im 12 stone and a size 14". Stripping the age there leaves "im a half", which ROLE reads as a
# job ("Half - good to know. What do you like most about it?"), so the strip stops when one of
# these follows the article.
NOT_A_ROLE_AFTER_ARTICLE = (
    r"half\b|quarter\b|bit\b|months?\b|years?\b|weeks?\b|days?\b|hours?\b|stone\b|"
    r"kilos?\b|kgs?\b|pounds?\b|lbs\b|size\b|inches\b|centimet\w*\b|feet\b|foot\b|"
    r"miles?\b|minutes?\b")


AGE_BEFORE_A_ROLE = re.compile(
    r"\b(?:im|i am)\s+\d{1,3}\s*(?:,\s*|and\s+|,\s*and\s+)?"
    r"(?=an?\s+(?!(?:" + NOT_A_ROLE_AFTER_ARTICLE + r")))")


# Retired is the same kind of news as a job - the biggest change in what a week looks like - and
# it was reaching the same neutral nod. Read on their own words, with the age in front allowed.
#
# Both readings below end the line. A follow-up is read with the earlier turn's words in front of
# it (`_follow_up_reading`), so a reading that matches anywhere re-answers the news over the ask:
# "im between jobs" then "how do i make the money stretch" got the between-jobs line a second
# time instead of the money one. The tail is the words a person hangs after the fact itself,
# never a question.
PLAIN_TAIL = (r"(?:\s+(?:at the moment|right now|these days|currently|for now|now|still|tbh|"
              r"to be honest|since\s+\w{3,9}|for\s+(?:a\s+|the\s+)?(?:few\s+|couple of\s+)?"
              r"\w{3,9}))*\s*[.!]*$")


# Out of work said plainly - "im between jobs", "im out of work", "im looking for work" - went to
# "I'm listening - say more if it helps", which says nothing about the thing they said. A person
# looking for work wants someone useful about it, which is a thing this bot can be. "i lost my
# job" and "i got made redundant" have their own answers and are not caught here.
OUT_OF_WORK = re.compile(
    r"\b(?:im|i am|ive|i have|i)(?:\s+been)?\s+(?:currently\s+|still\s+|now\s+|just\s+)?"
    r"(?:between jobs|out of work|unemployed|jobless|job hunting|looking for work|"
    r"looking for a job|on the dole)\b" + PLAIN_TAIL, re.I)


RETIRED = re.compile(
    r"\b(?:im|i am|ive|i have|i)\s+(?:\d{1,3}\s*(?:,\s*|and\s+|,\s*and\s+)?)?"
    r"(?:just\s+|now\s+|recently\s+|finally\s+)?retired\b"
    # "i retired my old bike" is a thing put out to grass, not a person leaving work, so the words
    # after it have to be about when, or the end of the line.
    r"(?:\s+(?:last|this|early|in|at|from|after|since|years?|now|and)\b[^?.!]*|"
    + PLAIN_TAIL + r")", re.I)


# The trouble a person brings with a retirement: what the habits table answers. Kept to the
# trouble words rather than every question word, so "im retired and i feel great" still gets
# the small-talk pool that asks how the days are going.
RETIRED_ASKING = re.compile(
    r"\b(lost|at a loss|struggl\w*|bored|boredom|lonely|loneliness|miss|missing|adjust\w*|"
    r"get used to|cope|coping|normal|strange|odd|weird|purpose|structure|nothing to do|"
    r"keep busy|keep occupied|with myself|how do i|what (?:do i|to|do people) do|what now)\b")


# Where they live, moved or are based. The pronoun and its auxiliary are read together so an
# adverb can sit between them and the verb: "i've just moved to bristol" is the same news as
# "i moved to bristol", and people say it the long way far more often.
# Read on the line as typed, because "we're from cork" and "they were from my bank" are the
# same letters once the apostrophe is gone. A bare "were" is only the dropped apostrophe when it
# opens the line ("were from cork"): after a plural subject it is the past tense of "to be", and
# "the parts were from ebay" is not a place anyone lives.
PLACE = re.compile(
    r"(?:^\s*were\b|\b(?:i|im|i'm|ive|i've|id|i'd|ill|i'll|i am|i have|we|we're|we re|weve|"
    r"we've|we'd|we am|we have))\s+"
    r"(?:just\s+|recently\s+|finally\s+|already\s+|now\s+)?"
    # "we moved in with my parents" is a household, not a place to say back.
    r"(?:(?:live|living|lives|moved|moving|settled|settling|based|relocat\w+)"
    r"\s+(?:(?:up|back|over|out|down|away)\s+)?(?:in|to)(?!\s+(?:with|as|for)\b)"
    r"|grew\s+up\s+in|from)\s+([a-z][a-z' -]{1,25})")


# The place is a name, and people carry on talking after it: "i live in leeds with my two kids"
# is Leeds, "im from cork but i live in dublin" is Cork. So the rest of the sentence is cut
# off, and when the name sits behind a thing ("a small flat in manchester") it is the name that
# gets said back.
PLACE_TAIL = tuple(re.compile(tail) for tail in (
    r"\s+(?:last|this|next)\s+(?:year|month|week|summer|winter|spring|autumn|christmas)\b.*$",
    r"\s+(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|a few|several|many|\d+)\s+"
    r"years?\s+ago\b.*$",
    r"\s+years?\s+ago\b.*$",
    r"\s+a\s+while\s+ago\b.*$",
    r"\s+since\s+(?:\d{4}|\w+)\b.*$",
    r"\s+in\s+(?:\d{4}\b|\d{1,2}\s+\w+|the\s+(?:summer|winter|spring|autumn|new year)\b"
    r"|(?:january|february|march|april|may|june|july|august|september|october|november"
    r"|december)\b).*$",
    r"\s+(?:originally|now|still|before|previously|currently|already|again|then|recently)\b.*$",
    r"\s+(?:at|for)\s+the\s+(?:moment|minute|time being)\b.*$",
    r"\s+(?:these days|right now|just now)\b.*$",
    r"\s+for\s+\w+.*$",
    r"\s+(?:with|and|but|because|so|as|too|which|when i|after)\b.*$",
    # A follow-up said after the place is not part of its name. The line is read with the turn
    # before it in front of it ("im moving to leeds" then "when" is read as "im moving to leeds
    # when"), and the name ran on through the follow-up word: the reply said "Leeds When — that's
    # a big move". No town is called "Leeds When", so these words end the name whatever follows.
    r"\s+(?:when|where|why|how|what|which|who|whose|whom)\b.*$",
    # A date said after the name is not part of it, whether it is written in figures or in words:
    # "im moving to leeds in six weeks" said the place back as "Leeds in Six Weeks", and the same
    # line with a place the reader has not met is "Moving to Six Weeks. Exciting - what's the plan?"
    r"\s+(?:in|on|at|by|from)\s+(?:about\s+|around\s+|roughly\s+|just\s+over\s+|nearly\s+)?"
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a|an|a\s+few|"
    r"a\s+couple\s+of|several)\s+(?:hours?|days?|weeks?|fortnights?|months?|years?)\b.*$",
))


PLACE_MOST = 4        # "new york", "stoke on trent", "the isle of wight"; not a clause


PLACE_LAST = re.compile(r"^.*\bin\s+([a-z][a-z' -]*)$")


# A phrase that only looks like a place: "i live in hope", "i live in fear of mondays".
PLACE_IDIOM = frozenset(("hope", "fear", "sin", "pain", "denial", "the past", "the moment",
                         "the dark", "a bubble", "cloud cuckoo land", "the middle of nowhere"))


# A span of time is a date, not a place: "i am moving out in six weeks" was answered "Moving to Six
# Weeks. Exciting - what's the plan?", and "im moving out in a fortnight" became "Moving to A
# fortnight". The span is only ever read after "in" or "to", so the guard is on the whole phrase:
# the count and its unit, or the unit on its own ("a fortnight", "the weekend"), with the hedge
# people put in front of it ("in about six weeks"). A month is a date as well - "im moving out in
# march" is March - and it is already in the store's own list of words that are not places.
PLACE_SPAN = re.compile(
    r"^(?:about\s+|around\s+|roughly\s+|just\s+over\s+|nearly\s+|almost\s+)?"
    r"(?:(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a|an|a\s+few|"
    r"a\s+couple\s+of|several|the)\s+)?"
    r"(?:hours?|days?|weeks?|fortnights?|months?|weekends?|years?|bit|while|minute|minutes)"
    r"(?:'?s\s+time|\s+time)?(?:\s+or\s+so|\s+from\s+now)?$"
    r"|^(?:january|february|march|april|may|june|july|august|september|october|november|"
    r"december|christmas|easter|the\s+weekend)$")


PLACE_NONE = frozenset({"", "holiday", "a holiday", "the holiday"})


# A word that points at the thing rather than naming it. The place reader takes the words after
# "live in", and the thing they live in is often one of these plus what it is: "i live in a 2 bed
# flat" stopped at the "2" and said the article back as the place ("A — what's it like there?").
# On its own the word is no place at all, and the reply is the plain one.
PLACE_POINTS = frozenset("""a an the this that these those my our their his her its some any
another each every no""".split())


# A place they did not go to: "i grew up in care" is a way of growing up, not somewhere, and the
# phrase after this verb has to name a place before it is worth asking what it was like.
GROWN_IN = re.compile(r"\bgrew up in\b|\bbrought up in\b|\braised in\b")


# Where a thing sits in the house is not a name worth saying back: "im from upstairs".
PLACE_POSITION = frozenset(("upstairs", "downstairs", "inside", "outside", "indoors", "outdoors",
                            "here", "there", "abroad", "away"))


ACK_WORDS |= {"guess", "suppose", "sort", "ish", "smile", "wink", "love", "worries", "right",
              "then", "cheers", "nice", "brill", "bravo", "yay", "aye", "okey", "oki",
              "safe", "unsafe"}
