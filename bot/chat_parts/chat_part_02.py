"""Part 2 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import badnews, pick
from ..compose.goodnews import MORE_OF_THE_NEWS, MORE_OF_THE_NEWS_ARRIVAL, MORE_OF_THE_NEWS_SCORE

from ..memory import stuck as stuck_line




# What is not a name: "we've moved to a new place", "i just moved in yesterday", "we moved in
# last week". There is nothing to say back about them, so the reply stays a plain one.
PLACE_NOBODY = re.compile(
    r"^(?:(?:a|an|the|my|our|their|his|her)\s+(?:new|different|other|another|old|same|"
    r"whole|nice|cool|good)\s+(?:place|city|town|flat|area|home|one))\b"
    r"|^(?:yesterday|today|tomorrow|tonight|now|soon|here|there|properly|recently|already|"
    r"by myself|on my own)\b"
    r"|^(?:last|this|next|the other)\s+(?:week|month|year|weekend|night|summer|winter|"
    r"spring|autumn|time|one)\b")


AWAY_WORDS = re.compile(r"\bfrom (?:a |the |our |my )?(?:holiday|holidays|vacation|trip|break|"
                        r"week away|weekend away)\b")


# A move, as opposed to living somewhere already: "we're moving to cork", "i'm relocating".
MOVING = re.compile(r"\b(?:moving|relocating|relocate|relocation)\b")


# A thing with a place inside it ("a small flat in manchester") is worth splitting; a place
# followed by a time ("edinburgh on monday", "bristol in jan") is not, and the time is not the
# place. So the split only happens when the phrase opens with a thing, and otherwise a time
# phrase is cut off the end.
PLACE_THING_OPENS = re.compile(r"^(?:a|an|the|my|our|his|her|their|this|that)\b", re.I)


PLACE_TIME = re.compile(
    r"\s+(?:in|on|at)\s+(?:the\s+)?(?:january|february|march|april|may|june|july|august|"
    r"september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"morning|afternoon|evening|night|weekend|weekends|spring|summer|autumn|winter|fall|"
    r"christmas|easter|half\s+term)\b.*$", re.I)


# A frame of time at the head of the phrase is not a place: "im moving in on friday" has no
# town in it at all, and the reply said "Moving to on Friday." The words after the preposition
# are the list above, so "in on friday" and "at christmas" are times, while "in cork" is Cork.
PLACE_TIME_OPENS = re.compile(
    r"^(?:in|on|at)\s+(?:the\s+)?(?:january|february|march|april|may|june|july|august|"
    r"september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"morning|afternoon|evening|night|weekend|weekends|spring|summer|autumn|winter|fall|"
    r"christmas|easter|half\s+term|\d)\b", re.I)


TRIP = re.compile(r"\b(?:(?:just )?(?:got back|im back|we re back))(?: from (?:a |the |our |my )?"
                  r"(?:holiday|holidays|vacation|trip|break|weekend away|week away))?\s*$")


PET_ANIMALS = r"(puppy|dog|cat|kitten|rabbit|hamster|parrot|horse|snake|lizard|guinea pig|fish)"


PET = re.compile(r"\b(?:ive got|i have got|i have|i got|weve got|we have|we got|i adopted|"
                 r"we adopted|i rescued|we rescued) an? (?:(?:rescue|new|little|baby) )*"
                 + PET_ANIMALS + r"\b")


PET_ANY = re.compile(r"\b" + PET_ANIMALS + r"\b")


GOOD_NEWS = (
    re.compile(r"\b(came out|turned out|went)\s+(great|well|brilliant|perfect|nicely|"
               r"better than|lovely)\b"),
    re.compile(r"\bi (won|nailed it|got the job|got in|got the place|"
               r"got the all clear)\b"),
    # A pass is not here: what was passed decides whether it is a result ("we passed the exam")
    # or a hand-over or a refusal ("we passed the salt", "we passed on the house"), and that
    # question is bot/compose/goodnews.py's.
    re.compile(r"\bwe (won|got it|did it)\b"),
    # A house is as big as a job, and main answered "we got the house" with "I'm listening - say
    # more if it helps." A scan coming back clear is the same shape: a result, said without any of
    # the words above.
    re.compile(r"\b(?:i|we) (?:got|have got) the (?:house|flat)\b"
               r"(?!\s*(?:valued|surveyed|painted|cleaned|checked|tested|insured|keys|key))"),
    re.compile(r"\b(?:scan|results?|tests?) (?:came back|come back|came out|was|is) clear\b"),
    re.compile(r"\b(the kids|everyone|the family|they) loved it\b"),
    re.compile(r"\bshe said yes\b|\bwe re having a baby\b|\bim having a baby\b"),
)


# "i lost my keys this morning" and "i lost my wallet on the bus" are lost things, and the
# bad-news pool would answer them with interview advice. Only a job-shaped thing counts here,
# so keys, a wallet, a passport and a phone reach their own lines.
LOST_JOB = re.compile(r"\b(?:(?:i|we)\s+)?lost (?:the|my|our|that|this) (?:job|work|role|"
                      r"position|contract|shift|hours|offer|placement|promotion|"
                      r"apprenticeship|client|deal|bid|order|tender)\b")


# The same news in the other words people use for it. A job that has ended has answers of its
# own in this family, and only "i lost my job" was reaching them: "i got sacked", "i was fired"
# and "they let me go" fell through to the gentle pool ("That sounds rough. If you want, I can
# help you think through what to do next"), which is the same news answered with a shrug - no
# reason in writing, no pay to check, no question about how it happened. The shapes are
# `badnews`'s own, so the ordinary senses stay ordinary: "i fired a pot in the kiln" and "i got
# fired up about the match" are an afternoon and a mood, and "my boss let me go home early" is a
# Friday. "Redundant" and "laid off" are not read here: bot/knowledge/work.py's `redundancy`
# entry already answers those, with the list to work through that somebody needs that week.
def _a_job_that_went(said):
    """Whether the line is the news that a job has ended, in any of the words people use."""
    return bool(LOST_JOB.search(said) or badnews.reads_as_a_sacking(said))


# The shortest ways of asking for the next step, which `stuck.STUCK` does not read: that pool is
# written for the longer asks ("i dont know what to do", "where do i start"), and this family is
# two words.
JOB_STEP_ASK = re.compile(
    r"^\W*(?:(?:and|but|so|well|oh|ok|okay|right|then|now|yeah)\s+)*"
    r"(?:now\s+what(?:\s+do\s+i\s+do)?|what\s+now|what\s+happens\s+now)"
    r"(?:\s+(?:then|now|next|though|tho|about\s+(?:that|it|this)))?\s*(?:\?|\.|!)*\s*$", re.I)


def _the_ask_after_a_job_that_went(clean, memory):
    """The first step in a job that has ended, for the shortest ask that follows that news.

    "i got sacked" then "now what" is the same hard day going on, and what it wants is the job's
    own first step (what the last pay and any notice money come to), not a shrug. The longer ask
    reaches `stuck.pool` already, which is where this pool comes from; only the two-word ask
    missed it.
    """
    if not isinstance(memory, dict) or not JOB_STEP_ASK.match(str(clean or "").strip()):
        return None
    turns = [t for t in (memory.get("turns") or [])[-3:] if isinstance(t, dict)]
    for turn in reversed(turns):
        said = " ".join(str(turn.get("user") or "").lower().split())
        if not said:
            continue
        if _a_job_that_went(said):
            return pick(list(stuck_line.JOB), memory, clean)
        if len(said.split()) > 2:
            # the conversation has moved on to something else
            return None
    return None


# Losing weight is not bad news ("i lost half a stone" got "give it a day before deciding
# anything"). It is a change in the body, and the useful question is whether it was meant. The
# perfect tense is the same news told a moment later ("i have lost weight", "ive lost a stone"),
# and without it here the fallback's "lost" reads the diet as a bereavement.
LOST_WEIGHT = re.compile(r"\b(?:i|ive|i have) lost (?:half a stone|a stone|"
                         r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*"
                         r"(?:kilos?|kg|pounds?|lbs?|stone)|"
                         r"(?:some|a lot of) weight|weight)\b")


BAD_NEWS = (
    re.compile(r"\b(didn't|didnt|did not) (get|make|pass|win)\b"),
    re.compile(r"\b(turned me down|turned us down|got rejected|got turned down|rejected)\b"),
    re.compile(r"\bi (failed|didn't pass|didnt pass)\b"),
    re.compile(r"\bwe lost (?:the|our) (?:contract|client|deal|bid|job|order|tender)\b"),
    # "they said no" is a refusal and a blow. "they said no infection" is what the bloods found,
    # and read as a refusal it was answered "That's gutting, especially after you put the work in.
    # Ask for feedback if you can" for a result that was good news. A no with a word of the thing
    # it rules out after it is a result, and bot/compose/fallback.py draws that same line for its
    # refusal reader (`REFUSED_NO_OBJECT`), so the test is asked here rather than kept in a second
    # list.
    re.compile(r"\b(she|he|they) said no\b(?!\s+(?!(?:way|chance|deal|thanks|thank|worries|"
               r"problem|dice|objection|to|about|on|again|twice|either|yet|at|for|so|and|but|"
               r"then|though|after|before|last|this|it|because|when|until|unless)\b)[a-z])"),
    re.compile(r"\bgot (cancelled|canceled|postponed)\b"),
)


# Something they did and came back from: "we went to the pub last night", "i went to the
# cinema on saturday", "we went for a walk at the weekend". The place is read out of their own
# words and given back to them, because "Thanks for telling me" fits a hundred lines and this
# one is easy to answer properly. The time phrase is what makes it a thing already done: without
# it ("we went to the pub") the line is as likely to be a plan, and plans are not my business.
# A count in front of a time, which people write as a word as often as a figure: "a few months
# ago", "six weeks ago", "a couple of years ago". The count can be left out altogether ("months
# ago" is the same thing), so the pattern is optional everywhere it is used.
TIME_COUNT = (r"(?:(?:a few|a couple of|a pair of|several|many|one|two|three|four|five|six|"
              r"seven|eight|nine|ten|a dozen|\d+)\s+)?")


WHEN_DONE = (r"(?:last night|last weekend|last (?:mon|tues|wednes|thurs|fri|satur|sun)day|"
             r"yesterday|the other night|the other day|at the weekend|over the weekend|"
             r"this morning|this afternoon|this evening|yesterday evening|yesterday afternoon|"
             r"at lunchtime|before work|after work|last week|last month|"
             r"on (?:mon|tues|wednes|thurs|fri|satur|sun)day(?: night)?|"
             # The same thing said with a longer view. "i went to rome last year" is a trip
             # already taken, and it was answered "I'm listening - say more if it helps",
             # which reads as if the trip were bad news.
             r"last (?:year|summer|winter|spring|autumn|fall|christmas|new year)|"
             + TIME_COUNT + r"(?:years|months|weeks|days)\s+ago|"
             r"(?:back )?in (?:19|20)\d\d|when i was (?:a kid|a child|little|young|small|"
             r"at school|\d+))")


# Company is the other way a line says a thing is already done: "i went to the cinema with my
# sister" has no "last night" in it, but the sister is who was there, so it is a report and not
# a plan. "we went to the pub" on its own still stays out of it.
#
# Company gets a pattern of its own rather than a place in the time phrase's alternation, and it
# only takes a line that ends at the company. In one alternation the lazy place group stops
# early, so "we went to a party with friends last night" read the place as "party" and lost the
# friends, and "i went to the gym with my friend and i pulled a muscle" read as a report about
# the gym. The time phrase always gets first refusal.
WITH_COMPANY = (r"with (?:(?:my|our|his|her|their|the)\s+[a-z][a-z' -]{1,24}|friends?|family|"
                r"a friend|some friends|a mate|mates)")


WENT_TO = re.compile(r"\b(?:i|we)\s+(?:went|popped|nipped|headed|took (?:us|my [a-z]+ and me))"
                     r"\s+(?:out\s+)?(?:to|for)\s+((?:(?:the|a|an|my|our|his|her|their)\s+)?"
                     r"[a-z][a-z' -]{1,26}?)\s+" + WHEN_DONE + r"\b")


WENT_TO_COMPANY = re.compile(
    r"\b(?:i|we)\s+(?:went|popped|nipped|headed|took (?:us|my [a-z]+ and me))"
    r"\s+(?:out\s+)?(?:to|for)\s+((?:(?:the|a|an|my|our|his|her|their)\s+)?"
    r"[a-z][a-z' -]{1,26}?)\s+" + WITH_COMPANY + r"\s*[.!]?\s*$")


# The same night out with the thing in the object instead of the place: "we went to see a film
# last night", "i watched the match with my dad". Only a thing people sit and watch is taken,
# so "i saw the doctor yesterday" and "we saw my mum" are left alone.
WENT_TO_SEE = re.compile(r"\b(?:i|we)\s+(?:(?:went|popped|nipped|headed)\s+(?:out\s+)?to\s+"
                         r"(?:see|watch)|watched|saw)\s+((?:(?:the|a|an)\s+)?[a-z][a-z' -]{1,20}?)"
                         r"\s+" + WHEN_DONE + r"\b")


WENT_TO_SEE_COMPANY = re.compile(
    r"\b(?:i|we)\s+(?:(?:went|popped|nipped|headed)\s+(?:out\s+)?to\s+"
    r"(?:see|watch)|watched|saw)\s+((?:(?:the|a|an)\s+)?[a-z][a-z' -]{1,20}?)"
    r"\s+" + WITH_COMPANY + r"\s*[.!]?\s*$")


WATCHED_THINGS = frozenset(("film", "films", "movie", "match", "game", "show", "play",
                            "gig", "concert", "band", "comedy", "comedian", "exhibition",
                            "opera", "musical", "football", "rugby", "cricket", "boxing",
                            "darts", "tennis", "grand prix", "race", "races", "ballet",
                            "documentary", "documentaries", "series", "episode", "box set"))


# How people say it when they liked it, or did not: "i watched a good film last night" is the same
# news as "i watched a film last night", and it was answered "Thanks for telling me - I'm here if
# you want to dig into any of that." because the word between the article and the thing is not
# the thing. The thing is the last noun of the phrase, so these are stepped over to find it.
WATCHED_DESCRIBER = frozenset(("good", "great", "brilliant", "lovely", "decent", "nice", "fine",
                               "really", "very", "quite", "proper", "properly", "actually",
                               "amazing", "excellent", "fantastic", "wonderful", "classic", "old",
                               "new", "funny", "sad", "scary", "weird", "long", "short", "whole",
                               "boring", "rubbish", "terrible", "awful", "bad", "poor", "dull",
                               "slow", "foreign", "animated", "local", "little", "small", "big"))


# The describers that are a complaint about the thing itself, rather than a word about what it
# was like ("a sad film", "a long film"). Only these are answered as a verdict, because "sorry
# the film wasn't up to much" is wrong about a film somebody loved and found sad.
SAID_POOR = frozenset(("awful", "terrible", "rubbish", "crap", "boring", "dull",
                       "dreadful", "disappointing", "overpriced", "soulless", "meh"))


# A place where nobody chooses to spend a good evening. "we went to the hospital last night" is
# not a night out and "glad it was a good one" is the wrong thing to say to it.
NOT_A_NIGHT_OUT = frozenset(("hospital", "a and e", "a&e", "ae", "casualty", "doctor",
                            "doctors", "gp", "dentist", "funeral", "court", "police",
                            "station", "prison", "cemetery", "crematorium", "care home",
                            "hospice", "morgue", "walk in centre", "bed", "sleep", "work",
                            "loo", "toilet", "bathroom", "shop", "shops",
                            # Somewhere people go in the ordinary run of a year. "i went to the
                            # gym last year" is about keeping it up, not a day out to ask
                            # about, and "Work - what was it like?" is a question nobody wants.
                            "gym", "school", "uni", "college", "nursery", "class", "church",
                            # The errands, which are the same kind of thing as the shop already
                            # above: "The bank - what was it like?" is a question with no answer.
                            "bank", "banks", "post office", "chemist", "pharmacy", "atm",
                            "cashpoint", "supermarket", "supermarkets",
                            # "a&e" arrives as "a e" once the line is flattened, and "a and e"
                            # loses its articles, so the set keeps the shapes it is asked about.
                            # A turn at the door of an emergency answered "A e - what was it
                            # like?" is the one line where a bright question is worse than a
                            # vague one.
                            "a e", "a and e department",
                            # The same again with the articles already gone, which is the shape
                            # the set is asked about once "a and e" has been stripped.
                            "and e", "and e department"))


def _not_a_night_out(place):
    """Is this somewhere nobody chooses to spend a good evening?

    Read three ways, because the set and the line do not spell a place the same: "a&e" arrives
    as "a e", and stripping the articles off "a and e" leaves "and e". The whole place is tried
    first, with "&" said as "and", and then the same with the articles taken off.
    """
    low = " ".join(place.lower().replace("&", " and ").split())
    if low in NOT_A_NIGHT_OUT:
        return True
    bare = " ".join(w for w in low.split() if w not in {"the", "a", "an"})
    return bare in NOT_A_NIGHT_OUT or bool(bare) and bare.split()[0] in NOT_A_NIGHT_OUT


# "we went to see a film last night" has a verb after "to", not a place: the film is the thing,
# and "See a film — what was it like?" says nothing.
NOT_A_PLACE_START = frozenset(("see", "watch", "visit", "meet", "pick", "collect", "get", "buy",
                               "look", "check", "drop", "deliver", "take", "fetch", "have",
                               "eat", "drink", "play", "do", "make", "book", "pay", "sort"))


# They already said how it went. Reading the place back and asking "how was it?" then sounds
# like the bot was not listening, so the line goes to the pool that answers what they said.
WENT_WRONG = re.compile(r"\b(?:awful|terrible|rubbish|crap|shit|shite|ruined|boring|dull|"
                        r"packed|rammed|empty|dead|quiet|freezing|soaked|dreadful|"
                        r"worst|cancelled|canceled|let ?down|argued?|argument|row|fight|"
                        r"nightmare|late|closed|shut|broke|broken)\b")


WENT_WELL = re.compile(r"\b(?:great|lovely|brilliant|amazing|excellent|fun|enjoyed|loved|"
                       r"best|good time|nice time|a laugh|buzzing|perfect)\b")


# A complaint about the thing itself: "we went to the pub last night but it was dead", "the
# match was dead boring". They have said how it went, so the thing is answered about rather than
# asked about. A complaint about somebody who was there ("we went to the pub with my mum and she
# was awful") is not this: the pub was fine, so nothing is said about the pub.
POOR_THING = re.compile(
    r"\b(?:it|that|this|they|the [a-z][a-z'-]*(?:\s+[a-z][a-z'-]*)?)\s+"
    r"(?:was|were|is|are)\s+"
    r"(?:(?:so|really|a bit|a little|pretty|quite|dead|proper|properly|totally|well|too)\s+)*"
    r"(?P<poor>awful|terrible|rubbish|crap|boring|dull|packed|rammed|dead|"
    r"freezing|dreadful|cancelled|canceled|a let ?down|soulless|disappointing|a waste|meh|"
    r"rude|overpriced|a rip ?off|shut|closed)\b", re.I)


def _poor_word(flat):
    """The word they used for how it went ("dead", "overpriced"), or None."""
    match = POOR_THING.search(flat)
    if not match:
        return None
    return " ".join(match.group("poor").split())


# The answer to "what was it like?": a short verdict, not a question. A line that only says
# "it was fine" is the middle and gets nothing, because either pool would be guessing.
VERDICT_WELL = re.compile(r"\b(?:lovely|great|brilliant|amazing|excellent|good|nice|fun|"
                          r"enjoyed|loved|best|a laugh|buzzing|perfect|decent|not bad)\b")


VERDICT_POOR = re.compile(r"\b(?:rubbish|crap|shit|shite|awful|terrible|boring|dull|quiet|"
                          r"packed|rammed|empty|dead|soulless|disappointing|let ?down|"
                          r"nightmare|waste|meh|bad|worst|rude|overpriced|freezing)\b")


# The weather a trip got: "it rained the whole week", "it was 40 degrees every day".
WENT_BAD_WEATHER = re.compile(
    r"\b(?:rain(?:ed|ing|y)?|wet|drizzle\w*|showers?|storms?|stormy|soaked|freezing|baltic|"
    r"boiling|scorching|heatwave|cloud\w*|damp|washout|washed out|miserable weather)\b")


STATUS = re.compile(r"\bon my (second|third|fourth|fifth) (coffee|cup|cuppa|tea|drink|beer|glass)\b")


JUST_DONE = re.compile(r"\bjust (finished|done|sent|booked|moved)\b")


JUST_STARTED = re.compile(r"\bjust started\b")


CAME_BACK = re.compile(r"\bjust got back\b")


# A trip they told me about, named by a place: "we went to lisbon", "i've been to japan", "we
# got back from spain on friday". These used to get "I'm listening - say more if it helps", which
# fits any message and says nothing about the trip. The place is what the reply is about, and it is
# kept so the next line about how it went is answered about the trip.
BACK_FROM = re.compile(
    r"\b(?:(?:i|we)\s+(?:just\s+|only\s+|recently\s+)?(?:got|came|come)\s+back"
    r"|(?:im|i am|we re|we are|were)\s+(?:just\s+)?back"
    r"|(?:i|we)\s+(?:just\s+)?(?:arrived|landed)\s+back)\s+from\s+(.+)$")


BEEN_TO = re.compile(
    r"\b(?:i|we|ive|weve|i have|we have)\s+(?:(?:also|just|only|once|finally|already)\s+)?"
    r"been\s+(?:to|in)\s+(.+)$")


WENT_TO_ANY = re.compile(
    r"\b(?:i|we)\s+(?:went|drove|flew|headed|popped|nipped|cycled|travelled|traveled)\s+"
    r"(?:off\s+|out\s+|over\s+|back\s+)?to\s+(.+)$")


# A trip still to come, one wished for, or one denied ("i have never been to japan") is not a
# trip they came back from, so none of these is read as news about one.
TRIP_NOT_YET = re.compile(r"\b(?:never|havent|hasnt|didnt|did not|not|no|wish|want|going to|"
                          r"gonna|plan to|planning|hope|hoping|soon)\b")


# The time phrase that makes "we went to cornwall" a trip already taken rather than a plan, and
# that lets a name the bot has no table for still be read as a place.
SOME_WHEN = re.compile(r"\b(?:last (?:year|summer|winter|spring|autumn|month|week)|yesterday|"
                       r"(?:" + TIME_COUNT + r"(?:years|months|weeks|days) ago)|"
                       r"(?:back )?in (?:19|20)\d\d|in (?:january|"
                       r"february|march|april|may|june|july|august|september|october|november|"
                       r"december)|when i was (?:a kid|a child|little|young|small)|"
                       # How often is not a date, but it says the trip already happened just as
                       # plainly: "we've been to cornwall twice" is not a plan.
                       r"(?:(?:" + TIME_COUNT + r"times)|once|twice|before|already)|"
                       r"for (?:a|one|two|three|four|\d+) (?:day|days|night|"
                       r"nights|week|weeks))\b")


# The time on the end of a place name: "we got back from portugal yesterday" is Portugal.
TRIP_TIME_TAIL = re.compile(r"\s+(?:yesterday|today|last (?:night|week|month|year|summer|"
                            r"christmas)|(?:this|next) (?:week|month|year)|"
                            r"(?:on|over) (?:the )?weekend|"
                            r"on (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
                            r"(?:" + TIME_COUNT + r"(?:years|months|weeks|days) ago)|"
                            r"(?:back )?in (?:19|20)\d\d|to (?:19|20)\d\d|"
                            r"when i was (?:a kid|a child|little|young|small)|"
                            # How often, which is not part of the name either: "we've been to
                            # cornwall twice" said the place was "Cornwall Twice".
                            r"(?:(?:" + TIME_COUNT + r"times)|once|twice|again|before|already)|"
                            r"for \w+ (?:days?|nights?|weeks?))\b.*$")


# Countries written short, which the place tables spell out ("the US" is "USA").
TRIP_SHORT_COUNTRIES = frozenset(("us", "states"))


PRESENCE = re.compile(r"^(?:hey |hi |oi |ok |okay )?(?:(?:are|r) (?:you|u)|(?:you|u)) "
                      r"(?:there|around|awake|listening|up)(?: (?:still|now|right now|or what))?[?.!]*$"
                      r"|^(?:are |is )?(?:anyone|anybody|someone) (?:there|around|home)[?.!]*$"
                      r"|^(?:still|you still) (?:there|with me|here|awake)[?.!]*$")


# The whole line is the pause: "hold on, is that for fresh or frozen" and "one sec, should i
# preheat the oven first" are questions, and answering "Take your time." tells the person to
# wait when they are waiting for us.
PAUSE = re.compile(r"^(?:ok |okay |right |alright )?(?:brb|be right back|one sec|one moment|"
                   r"give me a (?:sec|minute|mo)|hold on|hang on|2 secs|two secs)"
                   r"(?: a (?:sec|tick|minute|moment|mo|bit))?[?.!,]*$")


# The whole line is the not-knowing: "i dont know what to do", "idk what to do", "no idea what to
# do", "i dont know where to start", and the flat "im stuck" on its own. There is no subject in
# any of them, so there is nothing to answer and nothing to look up: on main they were a nod ("Got
# it. Is there anything you'd like a hand with?"), a stall ("I'm listening - say more if it
# helps") or a search hedge ("That's beyond what I know well"). A friend says that is a hard place
# to be and asks for the one thing on their mind. A line with a subject goes on past the phrase -
# "i dont know what to do about my job" - and is left to the thing it names, and so is a line with
# a tail that names one ("i dont know what to do with my life"), because main already answers
# those. Two shapes are deliberately not here: "im lost" and "im stuck in a rut", which main
# answers with a question and a real step.
_LOST_TAIL = (r"(?: ?(?:anymore|any more|now|right now|at all|really|tbh|honestly|today|at the "
              r"moment|again))*[?.!,]*$")


LOST_ONLY = re.compile(
    r"^(?:ok |okay |so |well |tbh |honestly |urgh |ugh )?(?:"
    # "i dont know what to do" and "idk what to do", and the same about where to start
    r"(?:i |we )?(?:(?:dont|do not) (?:really |actually )?know|dunno|dno|idk|dk) "
    r"(?:really )?(?:what to do|where to start|where to begin|what to do next)"
    # "no idea what to do", with or without the verb said out loud
    r"|(?:(?:i|we) )?(?:(?:have|ve got|got|had|hv) )?no idea (?:at all )?"
    r"(?:what to do|where to start|where to begin|what to do next)"
    # "im stuck", "i feel stuck" - not "im stuck in a rut", which has an answer of its own
    r"|(?:im|i am|i feel| i m|feeling|feel)(?: so| really| totally| a bit| kinda| kind of| quite)? "
    r"stuck"
    r")" + _LOST_TAIL)


# The same place reached the other way round: not the not-knowing but the effort that is not
# landing. "nothing is working", "ive hit a wall", "im not getting anywhere" and "im going round in
# circles" all name no subject either, and each of them used to get the placeholder the composer
# keeps for a line it did not understand - "I'm listening - say more if it helps", "Got it. Is
# there anything you'd like a hand with?" - while "im going round in circles" was read as a trip
# the person was taking ("Circles - nice. When are you going?"). What they are asking for is the
# same thing "im stuck" asks for, so they are read here with it.
#
# A word after the shape usually makes it a subject again - "nothing is working on my laptop" is a
# laptop's turn, "im not getting anywhere with my cv" is the cv's - so only the filler words a
# spoken line carries are allowed after it.
_AT_IT_TAIL = (r"(?:\s+(?:at all|today|right now|anymore|any more|now|for me|tbh|honestly|"
               r"seriously|still))?[?.!,]*$")


AT_IT = re.compile(
    r"^(?:ok |okay |so |well |tbh |honestly |urgh |ugh |god |christ |right )?(?:"
    r"nothing (?:is|seems to be|seems|i (?:do|try)|i m doing) (?:working|works)"
    r"|nothing works"
    r"|nothing is going right"
    r"|(?:it all|everything) keeps going wrong"
    r"|(?:i ve|i have|we ve|we have|ive|i|we) (?:just )?(?:hit|come up against) a "
    r"(?:wall|brick wall)"
    r"|(?:im|i am|i m|we re|we are|i feel|i m feeling) (?:just |really |still )?not getting "
    r"(?:anywhere|there|far)"
    r"|(?:im|i am|i m|we re|we are) (?:just |still )?(?:going|spinning) (?:round|around) in "
    r"circles"
    r"|(?:im|i am|i m) (?:just )?spinning (?:my wheels|in circles)"
    r")" + _AT_IT_TAIL)


# The answer to that question, which used to be the bot talking to itself: "nothing is working" was
# asked "what have you tried so far", and "ive been trying for weeks" got "Got it - you've been
# trying for weeks", "ive tried everything" got "Sounds alright. Anything good in it?" - the day
# pool reading a complaint as a thing done - and "i dont know what else to do" the placeholder.
# Only after the bot has asked, because "ive tried everything" out of the blue is a different line.
_HOW_LONG_AT_IT = re.compile(
    r"^(?:ok |okay |so |well |tbh |honestly |urgh |ugh |god )?(?:"
    r"(?:i ve|ive|i have|we ve|we have|i d|id) (?:been )?(?:tried|trying|been at it|at it|"
    r"having a go|giving it a go|working on it)(?: (?:for|since) [^.!?]{1,18})?"
    r"|(?:i ve|ive) tried (?:everything|it all|all of it|all sorts|everything i can think of|"
    r"literally everything)"
    r"|(?:there is|theres) nothing else (?:left )?to try"
    r"|nothing else (?:has )?(?:worked|to try)"
    r"|(?:i |we )?(?:dont|do not) know what else to (?:do|try)"
    r"|(?:i |we )(?:ve |have )?run out of ideas"
    r")(?: (?:now|already|again|honestly|tbh|yet))?[?.!,]*$")


# The thing they are stuck on, when it is something written or filled in: a cv, a form, an essay,
# an application. "im stuck with my cv" was answered "Annoying. Is it every time, or only now and
# then?" - a fault that keeps coming back - and "im stuck on this form" "Tell me what it does and
# I'll work out the next step with you", as if the form were a machine. Naming the thing is what
# the reply has to use: which part of it, because that is where the next step differs.
# Only the things that are somebody's own to write and that no card in the knowledge base answers
# on the line that names them: a tax return, an invoice and a spreadsheeted budget each have an
# answer of their own, and a claim here would throw it away.
# A form is not a cv: what a stuck cv needs is where to start writing, and what a stuck form needs
# is which boxes can be answered from a document the person already has. It is its own reading so
# the reply can say which one it is ("im stuck on this form" was given the cv advice).
_A_FORM = r"(?:[a-z]+\s+){0,3}forms?"


_A_THING_TO_MAKE = (r"(?:cv|r[ée]sum[ée]|cover letter|covering letter|personal statement|essay|"
                    r"dissertation|thesis|assignment|coursework|homework|report|blog post|"
                    r"uni statement"
                    r"|(?:(?:job|visa|course|college|uni|university|rental|tenancy|passport|"
                    r"membership|licen[cs]e|travel|grant)\s+)?applications?"
                    r"|" + _A_FORM + r")")


# The feeling of being stuck on its own, with nothing named: "i feel stuck", "i am so stuck",
# "feel like i am stuck". It was read as being about feelings, and the reply was the
# composer's placeholder for a remark - "Annoying. Is it every time, or only now and then?" - which
# reads it as an intermittent fault rather than a person at a wall. There is nothing here to answer
# either, so the reply does what a friend does: says the feeling is worth taking seriously and asks
# which part it is, because stuck is almost always one part rather than the whole of a life.
STUCK_FEELING = re.compile(
    r"^(?:ok |okay |so |well |tbh |honestly |urgh |ugh |right |god )?"
    r"(?:(?:i|we)\s+)?(?:just\s+|really\s+|so\s+|totally\s+|properly\s+|kind of\s+|sort of\s+|"
    r"a bit\s+|completely\s+)*"
    r"(?:(?:feel|feels|feeling|felt)\s+"
    r"(?:(?:like|that)\s+(?:(?:i|we)\s+(?:am|are)\s+)?)?"
    r"(?:so\s+|really\s+|totally\s+|properly\s+|kind of\s+|sort of\s+|a bit\s+|completely\s+|"
    r"very\s+|pretty\s+)*"
    r"(?:stuck|stuck\s+(?:again|now))"
    # "im so stuck" says the same feeling without the word "feel", and only with an intensifier
    # in front: a plain "im stuck" is the question the chat already asks ("what's the situation?"),
    # and it is a different turn from a person naming how the stuckness feels.
    r"|(?:i m|im|i am|we re|we are)\s+(?:so|really|totally|properly|completely|kind of|sort of|"
    r"a bit|very|pretty)\s+stuck)"
    r"(?:\s+(?:right now|at the moment|again|today|with (?:everything|it all|life)))?"
    r"[?.!,]*$")


_STUCK_ON = (r"^(?:ok |okay |so |well |tbh |honestly |urgh |ugh |right )?"
             r"(?:(?:i m|im|i am|i ve been|i have been|we re|we are|i|we)\s+"
             # "i feel stuck with my cv" is the same thing named: the feeling is how it reads, the
             # cv is what will not move.
             r"(?:feel(?:ing)?\s+)?"
             r"(?:still\s+|totally\s+|completely\s+|really\s+|a bit\s+|kind of\s+|sort of\s+|"
             r"so\s+)?"
             r"(?:stuck|stuck again|going nowhere|getting nowhere|not getting anywhere|blocked)\s+"
             r"(?:on|with|in)\s+|(?:i|we) (?:keep|keeps) getting stuck (?:on|with) )"
             r"(?:my|the|this|that|a|our|his|her|their)?\s*")


_STUCK_TAIL = (r"\b(?:\s+(?:again|all (?:week|day|morning)|for (?:days|hours|weeks)|"
               r"since \w+))?[?.!,]*$")


STUCK_ON_A_FORM = re.compile(_STUCK_ON + _A_FORM + _STUCK_TAIL)


STUCK_ON_A_THING = re.compile(_STUCK_ON + _A_THING_TO_MAKE + _STUCK_TAIL)


RETURNED = re.compile(r"^(?:ok |okay |right |alright )?(?:im |i am |we re |we are |were |we )?back(?: again| now)?"
                      r"(?:[, ]*(?:where were we|what were we (?:saying|doing|on about)|sorry))?[?.!]*$")


BID = re.compile(r"\b(?:guess what|you ll never guess|you wont believe|you won t believe|"
                 r"wait till you hear|wait until you hear|want to hear something)\b")


# The whole line is the leaving: "i am off to bed soon, what should i cook" carries a request
# and is answered by the cooking module, so a line that goes on past the leaving is not mine.
LEAVING = re.compile(r"^(?:ok |okay |right |well )?(?:im |i am |we re |we are )?"
                     r"(?:out the door|out of the door|just leaving|leaving now|leaving in a "
                     r"(?:min|minute|sec)|setting off|setting out|just off|off now)"
                     r"(?: now| soon| for (?:work|school|uni|a bit))?[!. ]*$"
                     r"|^(?:ok |okay |right |well )?(?:im |i am |we re |we are )?"
                     r"(?:off|heading off|heading|popping|nipping) (?:out|off|to) "
                     r"(?:work|bed|sleep|town|the shops|the shop|pick up|collect|school|uni|"
                     r"the gym|the pub|my mums?|my mums? place|my parents)"
                     r"(?: (?:now|soon|later|after this|in a bit|for a bit))?"
                     r"(?:[, ]*(?:see (?:you|ya)(?: later| soon| tomorrow)?|bye|goodnight))?[!. ]*$"
                     r"|^(?:ok |okay |right )?(?:im |i am )?(?:off out|out out|heading out|"
                     r"popping out|nipping out)(?: now| soon| for a bit)?[!. ]*$"
                     r"|^at work now[!. ]*$")


HOME_AGAIN = re.compile(r"^(?:ok |okay |well |only )?(?:(?:(?:i|we) )?(?:just )?(?:got|come|came|arrived) home"
                        r"|(?:im|i am|we re|we are) home"
                        r"|home)"
                       r"(?: (?:now|again|at last))?(?: (?:from|after) [a-z ]{1,24})?[!. ]*$"
                       r"|^(?:ok |okay |well )?(?:im |i am |we re |we are )?(?:just |only )?"
                       r"(?:got in|got back|back in|walked in|in now)"
                       r"(?: (?:now|again|at last|finally))?"
                       # The place they came back from is what the reply is about, so it has to be
                       # one the line itself says: "just got back from the dentist" has its own
                       # answer ("did they give you anything useful"), and "back from a week in
                       # cornwall" is a holiday, not the end of a working day.
                       r"(?: (?:from|after) (?:work|the gym|the shops|the shop|school|uni|"
                       r"town|lunch|the pub|my mums?|my parents))?[!. ]*$"
                       r"|^(?:ok |okay |well )?(?:just |only )?back from (?:work|the gym|the "
                       r"shops|the shop|school|uni|town|lunch|my mums?|my parents)"
                       r"(?: now)?[!. ]*$")


# On the way somewhere: "im on my way", "nearly there", "ten minutes away". The person is in the
# middle of something and has told the bot so; the pool that answered it ("Is there anything
# you'd like a hand with?") fits any line anybody ever sent.
UNDERWAY = re.compile(r"^(?:ok |okay |well |right )?(?:im |i am |we re |we are )?"
                      r"(?:(?:on my|on our|on the) (?:way|way there|way home|way in)"
                      r"|omw|nearly there|almost there|nearly "
                      r"home|almost home|halfway there|not far now|(?:\d+|ten|five|two|a "
                      r"few) (?:minutes|mins|min) away|just around the corner|nearly in)"
                      r"(?: (?:now|still|anyway))?[!. ]*$")


# In bed already, or awake since a time: the person is telling the bot about their night, and a
# friend says something about the night rather than "Is there anything you'd like a hand with?".
IN_BED = re.compile(r"^(?:ok |okay |well )?(?:im |i am )?(?:already |just )?(?:in|off to|going "
                    r"to|going off to) bed(?: already| now| at last)?[!. ]*$"
                    r"|^(?:im |i am )?(?:already )?(?:in bed|in my bed)(?: already| now)?[!. ]*$")


# The awake line is the whole line, like the shapes below it: "been awake since 3" is a state
# and a line that goes on ("been awake since 3 stressed about work", "and im scared") says
# something else as well, which its own reply answers better than advice about naps does.
AWAKE_SINCE = re.compile(
    r"^(?:ok |okay |well |so )?(?:been |i was |im |i am )?awake since (?P<when>\d{1,2}"
    r"(?::\d{2})? ?(?:am|pm|o clock|oclock)?|\d{1,2}(?::\d{2})?)\b[!. ]*$")


# A job the person has to do: "need to do a shop", "got to do the washing". It is not a question
# and not news anybody can answer, so the reply is a short line about the job.
ERRAND = re.compile(r"^(?:ok |okay |well )?(?:i )?(?:need|have|got|gotta|must|needs)(?: got)? to "
                    r"(?:do |run |get )?(?:a |the |some |my |our )?"
                    r"(?P<what>shop|shopping|food shop|big shop|wash(?:ing)?|laundry|ironing|"
                    r"cleaning|tidy up|tidy|hoover(?:ing)?|dishes|washing up)"
                    r"(?: done| later| today| tomorrow| before [a-z ]{2,20})?[!. ]*$")


WISH_LUCK = re.compile(r"\bwish me luck\b|\bfingers crossed\b|\bkeep your fingers crossed\b")


NEWS_REPLIES = {
    # Somebody asking whether the thing they are thinking of is a good idea, or whether what they
    # just did was: "is that a good idea", "would that work", "is it worth it" after "im thinking
    # of getting a cat". The pool they landed on said "Alright then \u2014 good luck with it.",
    # which agrees with them and then hands them the door, and would fit any message anybody ever
    # sent. The thing is in the thread, so it is named back, and the answer says the one true
    # thing about a decision that is not the bot's to make.
    "judged": (
        "Whether {thing} is the right move is yours to weigh, not mine. What is the bit you are "
        "unsure about?",
        "{Thing} — that is your call, not mine. Say what you would lose either way and I will "
        "lay it out with you.",
        "I cannot call that one for you. Tell me what matters most about {thing} and I will help "
        "you think it through.",
    ),
    # The same ask with nothing to name ("is that a good idea" as the first thing said, or after
    # a line with no thing in it). It still gets the honest answer rather than "good luck with it".
    "judged_bare": (
        "That is yours to weigh, not mine. What is the bit you are unsure about?",
        "Not a call I can make for you. Say what you would lose either way and I will lay it out.",
        "I cannot call that one for you. Tell me what matters most and I will help you think it "
        "through.",
    ),

    # Out of work is a hard stretch and one of the few places a stranger can be properly useful:
    # the reply says the hard bit and then offers the concrete help this bot has.
    "out_of_work": (
        "Between jobs is a job in itself. What sort of work are you after?",
        "That is a rough stretch. What are you applying for at the moment?",
        "How long have you been looking? Tell me the work you want and I will help with the CV "
        "or where to look.",
    ),
    # Leaving work is a change of life, not a role to ask a shop question about, and it is warm
    # news to most people: the reply asks about the days rather than the job.
    "retired": (
        "Retired - how are you filling the days?",
        "That is a big change. What does a normal week look like now?",
        "Retired, then. What have you been meaning to get to?",
    ),
    "job": (
        "A {x} — nice one. What's a normal day like for you?",
        "{X} — good to know. What do you like most about it?",
        "A {x}, busy job. How long have you been doing it?",
    ),
    "place": (
        "{place} — nice. How long have you been there?",
        "{place} — what's it like there?",
        "{place}? Good to know. Do you like it there?",
    ),
    # The place with the words they put with it: "leeds not far from the station" is both where
    # they live and what they wanted to say about it, so the reply carries both.
    "place_near": (
        "{place}, {near} — handy. What's the area like?",
        "{place} — {near}, then. Do you like it there?",
        "{place}, {near}. Sounds like a good spot.",
    ),
    "moving": (
        "{place} — that's a big move. Have you found a place yet?",
        "Moving to {place}. Exciting - what's the plan?",
        "{place} in the diary, then. Do you know anyone there?",
    ),
    "trip": (
        "Welcome back! How was it?",
        "Nice — a break does a lot of good. What was the best bit?",
        "Good to be back? What was the highlight?",
    ),
    # How many children they have is a fact with a number in it, and the count is what the reply
    # can use: "i have two kids" used to get the pool that says "Thanks for telling me — I'm here if
    # you want to dig into any of that", which files the best thing they have said all day.
    "kids": (
        "{X} — good to know. How old are they?",
        "{X}. What are they into at the moment?",
        "{X} — noted. Tell me about them.",
    ),
    # The same fact when the line already carried the ages: asking "How old are they?" of
    # "my two kids are 4 and 7" asks for the thing the person has just said.
    "kids_aged": (
        "{X} — noted.",
        "{X}. What are they into at the moment?",
        "{X} — good to know. Tell me about them.",
    ),
    # A trip they named: back from it, or been there. The place is said back to them and one
    # thing is asked about it, because a line that would fit any message says nothing about a trip.
    "back_from": (
        "Back from {X} — good trip? What was the best bit?",
        "{X} — nice. How was it?",
        "Welcome back from {X}. What was the best bit?",
    ),
    "been_to": (
        "{X} — lovely. What did you like most about it?",
        "{X} — what was the best bit?",
        "{X}, good call. Would you go back?",
    ),

    # A place nobody goes for fun: their own hospital, doctor, scan or result. The trip pools
    # above refuse these places on purpose ("The hospital — nice. How was it?" is the wrong
    # thing to say), and nothing else read them, so "im back from the hospital" fell through to
    # the neutral nod — "Thanks for telling me, I'm here if you want to dig into any of that" —
    # which is the same sentence for any message and says nothing about the visit. Each pool
    # below names the thing they said and follows it; two of the three do not ask at all, so a
    # run of these does not turn into an interview.
    # No line here puts the visit at a time of day: a scan at four or a night in A&E would be the
    # wrong morning, and the night pool below is the one for an evening.
    "med_visit": (
        # {X} rather than {Xb}: a test named by its letters needs its article back, or "MRI is
        # never a quick trip" reads like a heading.
        "{X} is never a quick trip. What did they say?",
        "Good to have {x} out of the way. Did they give you anything useful to go on?",
        "{X}, then. Any word on what happens next?",
    ),
    # The same visit with the evening gone: a night in A&E is a night, not a morning.
    "med_visit_night": (
        "{X} at night — that is your evening gone. Did they get you sorted?",
        "A night in {x} is the worst kind of long. How are you doing now it is over?",
        "Nobody wants {x} after dark. What did they say?",
    ),
    "med_results": (
        "Results back — that is the wait nobody enjoys. What did they say?",
        "{Xb} in, then. Anything you have to act on, or is it a wait-and-see?",
        "That was quick, or it felt long. What did they tell you?",
    ),
    # The same news about a thing the line says in the plural ("my scan results came back
    # clear"): "A clear scan results is" is the sentence a plural told with a singular pool.
    "med_clear_plural": (
        "Clear is what you want to hear — that is one thing off your mind.",
        "Clear {x} are the best kind of boring. That earns a proper evening off, if you ask me.",
        "That is the answer you were after. Worth telling whoever was worrying with you.",
    ),
    # A result that came back clear is good news and is said as such, once.
    "med_clear": (
        "Clear is what you want to hear — that is one thing off your mind.",
        "A clear {xb} is the best kind of boring. That earns a proper evening off, if you ask me.",
        "That is the answer you were after. Worth telling whoever was worrying with you.",
    ),
    # What the doctor said, said back with what it means for the next week. No diagnosis and no
    # dose of the bot's own: the reply stays with what they were told and what to do about it.
    "med_diagnosis": (
        "{A} {x} is annoying, but at least it is a named thing. Give it the resting they told "
        "you about rather than the resting that feels like enough.",
        "So {a} {x}, and nothing worse. Follow what they said even on the days it feels fine — "
        "that is the part most people skip.",
        "{A} {x} is treatable and boring to get over. It wants the time they said, not the time "
        "you would like.",
    ),
    # The check came back fine and there is still a job to do about it: "they said my knee is
    # fine but i should rest it". The good news is said first, because that is the news.
    # Resting sorts out a knee or a shoulder. It does nothing for cholesterol, a heart or blood
    # pressure, which are the other half of "they said my X is fine", so that half has its own
    # pool: the news is good and there is nothing to rest.
    "med_part_fine": (
        "Good news on the {xb}, then. The resting is the part that actually sorts it out, so "
        "give it the time they said.",
        "Fine on the {xb} is the best answer you could have got. Do the resting properly and "
        "it will settle.",
        "That is a relief. Boring advice next, but it is the advice: rest it for as long as they "
        "said, then build it up slowly.",
    ),
    "med_part_fine_result": (
        "{Xb} fine is the answer you want. Was that the whole check, or are they waiting on "
        "anything else?",
        "Good news about the {xb}, then — nothing to act on.",
        "{Xb} fine, then. That is one thing off your mind.",
    ),
    # Something they were given to wear or carry: a cast, a sling, a boot. The reply is about the
    # few weeks it means, in the plain terms of keeping it dry and letting other people help.
    "med_wearing": (
        "A {xb} is a good sign somebody took it seriously. Keep it dry, and let people carry "
        "things for you while the bone does the work.",
        "The {xb} is more boring than painful after the first day or two. Worth lining up "
        "something that only needs the one hand.",
        "So a {xb} for a few weeks. Ask them at the next check what you can still do, rather "
        "than finding out by trying it.",
    ),
    # A dressing is not a cast: it covers a wound for a day or two and comes off again.
    "med_dressing": (
        "A {xb} for a day or two, then, not weeks. Keep it dry and change it when they said "
        "to, and let them look at it if the skin round it goes hot or tight.",
        "Good - that is the part that keeps it clean while it closes. Leave it alone until they "
        "told you to change it, and keep it out of the bathwater.",
        "Not much to it, which is the point: keep it dry, do not pick at it, and ring them if the "
        "edge starts spreading red.",
    ),
    # A tooth out, a tooth pulled: out, and the care of it afterwards is the next day or two.
    "med_out": (
        "Out, then — that is the worst of it done. Ice it today, and take what they gave you "
        "before the numbing wears off.",
        "Glad it is out. Soft food for a day, and no straws while it heals, which nobody tells "
        "you until afterwards.",
        "So it is out. The ache settles in a day or two; if the bleeding carries on past that, "
        "ring them back.",
    ),
    "pet": (
        "A {pet} — lovely. How old is it?",
        "A {pet} — good to know. What's its name?",
        "Lovely. How's the {pet} settling in?",
    ),
    "pet_named": (
        "A {pet} called {name} — lovely. How's {name} settling in?",
        "{name} — good name for a {pet}. How old is {name}?",
        "Lovely — a {pet} called {name}. How's the first week going?",
    ),
    "good_news": (
        "That's brilliant. Nice one!",
        "Love that — well done. How are you celebrating?",
        "Good stuff. That must be a weight off.",
    ),
    # The best part of the news, said a turn after it: "i passed my driving test" / "first time",
    # "we won on saturday" / "2-0". The cheer has just been given, so the detail is the news again
    # and not a question: what came back was a card about the subject ("Most people need around 45
    # hours of lessons plus 20 hours of private practice before they pass", "That's 2") or the
    # floor. The pool is read by `goodnews.a_detail_of_the_news`, which only takes a short line
    # with nothing asked in it, after a cheer this module gave.
    "more_of_the_news": MORE_OF_THE_NEWS,
    "more_of_the_news_score": MORE_OF_THE_NEWS_SCORE,
    "more_of_the_news_arrival": MORE_OF_THE_NEWS_ARRIVAL,
    "bad_news": (
        "That's gutting, especially after you put the work in. Ask for feedback if you can — "
        "it usually says exactly what to change.",
        "Sorry to hear it. Give it a day before deciding anything, then look at what you can "
        "control next time.",
        "That stings. Most people who get these were turned down first, so it's worth one more go.",
    ),
    # "i lost my job" was answered from "bad_news", which talks about being turned down and
    # asking for interview feedback. A job you lose is not an application you failed.
    "lost_job": (
        "That's a blow. Give it a day before deciding anything, then check what you're owed: "
        "notice, holiday pay and anything in your contract.",
        "Sorry to hear it. However it ended, get the reason and the pay in writing before you "
        "agree to anything.",
        "That's hard. What happened - was it a surprise, or had you seen it coming?",
    ),
    "lost_weight": (
        "Was that on purpose, or has it been dropping on its own? If it's going without you "
        "trying, a word with the GP is worth it.",
        "Nice, if that was the plan. If it wasn't, it's worth getting checked - weight that "
        "comes off by itself shouldn't be ignored.",
        "How are you feeling in yourself otherwise? Losing weight by accident is the bit to "
        "keep an eye on.",
    ),
    "nothing_on": (
        "Nothing worth watching is annoying. Pick a film you already like rather than hunting for one.",
        "Try a film instead of channel-hopping — even one you've seen beats scrolling.",
    ),
    "status": (
        "One of those mornings, then. Anything you can push to tomorrow?",
        "The second cup says it all. What's making today busy?",
        "Coffee is doing the heavy lifting today, then.",
    ),
    # A place they went to and are telling me about. The reply names what they did back to them
    # and asks one thing about it, rather than a line that would fit any message at all.
    # The thing was named with their own word for it in front ("a good film"), so what is left
    # to ask is which one, not whether it was any good.
    "saw_it_told": (
        "{X} — which one?",
        "{X} — what was it?",
        "{X} — nice one. What was it called?",
    ),
    # They said how it went and the word was a complaint, so naming the thing and asking "what
    # was it?" would answer a line they did not write: "A film - what was it?" to "i watched a
    # rubbish film last night". The thing is still named, and the verdict is taken as said.
    "saw_it_poor": (
        "{X} — sorry it wasn't up to much. What was wrong with it?",
        "Shame about {x}. What wasn't right about it?",
        "{X}, and not a good one — what let it down?",
    ),
    # The same for a place that carries the complaint in front of it: "we went to a terrible
    # gig last night" is a night out, and "That sounds rough" is a line about a feeling.
    "day_out_poor": (
        "{X} — sorry it wasn't up to much. What was wrong with it?",
        "Shame about {x}. Would you give it another go?",
        "Ah, that's a shame about {x}. What let it down?",
    ),
    "saw_it": (
        "{X} — any good?",
        "{X} — what did you make of it?",
        "{X} — glad you got out for it. Was it good?",
    ),
    "day_out": (
        "{X} — how was it?",
        "{X} — what was it like?",
        "{X} — that's a good way to spend it. Tell me the best bit.",
    ),
    # The same, once they have told me it went well: no "how was it?", which would say I had not
    # heard them.
    "day_out_well": (
        "{X} and a good time — nice. What made it?",
        "Glad it was a good one. {X} beats a night in.",
        "{X} well spent, then. Those are the ones that make the week.",
    ),
    # How it went, asked after I asked: "we went to the pub last night" / "The pub — what was it
    # like?" / "it was lovely". The place is still on the table, so say something about it
    # rather than a line that would fit any short answer.
    "night_out_well": (
        "{X} — glad it was a good one.",
        "Good. {X} that lands is worth going back to.",
        "Nice one. That's the sort of evening that makes the week.",
    ),
    "night_out_poor": (
        "Shame about {x}. Do you think it was a one-off?",
        "Ah well — at least you know now. {X} can be hit and miss.",
        "Sorry to hear it. What was the letdown?",
    ),
    # The weather a trip got, said the turn after the place: "it rained the whole week" is how the
    # trip went, and saying it back to them ("Got it - it rained the whole week") answers nothing.
    # The wording stays away from which way the weather went, because the same pool answers a
    # washout in Cornwall and a heatwave in Spain.
    "night_out_weather": (
        "Shame about the weather. Did you get much out of {X} anyway?",
        "{X} in that weather is a hard one. Did you make the most of it?",
        "That's the risk with {X}. Would you go back another time?",
        "Weather like that can spoil a trip. Was any of it good?",
    ),
    # The same complaint said in the same turn as the evening ("we went to the pub last night but
    # it was dead"). They have already said how it went, so the word they used comes back to
    # them: "Sorry it was dead" answers what they said, where "how was it?" would say I had not
    # heard them.
    "night_out_poor_said": (
        "Sorry it was {p}. What was wrong with it?",
        "{P}, then — that's a shame. Do you think it was a one-off?",
        "That takes the shine off it. {P} — what was behind that?",
    ),
    # A move is not a task finished: it is weeks of boxes and a new area to learn, so it gets a
    # reply about the move rather than "What's next?" straight after one.
    "move_done": (
        "That's a big one, and the boxes are the easy bit. How's the settling in going?",
        "Big job. Being at home somewhere new takes longer than the unpacking does, so give it a "
        "few weeks before it feels right.",
        "Out of one place and into another — that's the week gone. Is the kettle unpacked yet?",
    ),
    "just_done": (
        "How did it go?",
        "Nice. What's next?",
        "Good. Take a minute before the next thing.",
    ),
    "just_started": (
        "How's it going so far?",
        "Nice. What made you start?",
        "Good for you. Keep it short and regular and it sticks.",
    ),
    "came_back": (
        "Nice — how was it?",
        "Any good?",
        "Good to have you back. Did you enjoy it?",
    ),
    "presence": (
        "Still here. What's up?",
        "Yep, right here — go on.",
        "I'm here. What's on your mind?",
    ),
    "pause": (
        "No rush. I'll be here.",
        "Take your time.",
        "Whenever you're ready — I'm not going anywhere.",
    ),
    "lost": (
        "That's a rough place to be. What's weighing on you most?",
        "Fair enough. Tell me what's going on and we'll find a first step together.",
        "Okay. Start with the part that's loudest — what's it about?",
        "Let's take it one bit at a time. What's the situation?",
    ),
    # The effort that is not landing is not the same turn as the not-knowing: they have been at it,
    # so the answer says something about the trying rather than asking what is wrong. Each wording
    # asks the one question that changes the next step - what has been tried, or which part fails.
    "at_it": (
        "That usually means the approach needs one change rather than more effort. What have you "
        "tried so far?",
        "Worth stopping before you push harder at it. Which part keeps letting you down - the "
        "start, the middle, or keeping it going?",
        "Nothing landing is often a plan that is too big for the week you have. What is the "
        "smallest piece of it you could finish today?",
        "That is the point where doing more of the same stops helping. What would count as it "
        "working?",
    ),
    # The answer to the first question: the effort is not the problem, so more of it will not help.
    "the_long_haul": (
        "Then it is not effort you are short of. What have you already ruled out?",
        "That is a lot of trying for the same result. Which part has moved at all, even a little?",
        "Everything tried and nothing landing usually means one step is wrong, not you. What does "
        "it look like when it works?",
        "So more of the same will not do it. What would tell you it had started to work?",
    ),
    # A thing they are writing or filling in and cannot get on with. The next step depends on which
    # part has them stuck, so the reply names the two that exist for every form and every essay:
    # what to put in it, and how it should read.
    # The feeling with nothing named. Each wording takes the feeling seriously and then asks the
    # one thing that turns it into a next step: which part, or what it is that will not move.
    "a_stuck_feeling": (
        "Feeling stuck is usually one part of it rather than all of it. Which part is it?",
        "That is worth taking seriously, not shrugging off. What is the thing that will not move?",
        "Stuck like that is tiring in a way that trying harder does not fix. What would shifting it "
        "even a little look like?",
        "Then something is jammed rather than you being bad at it. What is the thing you keep "
        "coming back to?",
    ),
    # A form is boxes to fill, not words to find. The help is which boxes can be answered from a
    # document they already have, which ones the notes at the top settle, and leaving the rest.
    "on_a_form": (
        "Forms are mostly copying, not writing. Which boxes can you answer from a paper you "
        "already have, and which are the ones you are stuck on?",
        "Read the notes at the top of it before the boxes: they say what the question actually "
        "wants, and most stuck boxes are a question read the wrong way.",
        "Fill in the ones you can from a document in front of you - name, dates, the numbers - "
        "and leave the rest blank for now. The blank ones are the question.",
        "Which part stops you - a box you cannot answer, or one you are not sure you have read "
        "right?",
    ),
    "on_the_thing": (
        "Which bit of it has you stuck - what to put in it, or how it should read?",
        "Then start with the part you already know the answer to, even the boring one - the "
        "first line down breaks the back of it.",
        "Is it the words that will not come, or not knowing what they want from you - those need "
        "different help.",
        "Do the facts first - names, dates, the numbers you can look up - and leave the wording "
        "until there is something on the page to word.",
    ),
    "returned": (
        "Welcome back. Where were we?",
        "Back again. What were we saying?",
        "There you are. Right, where did we get to?",
    ),
    "bid": (
        "Go on then — tell me.",
        "Now I'm curious. What happened?",
        "I'm listening. Spill it.",
    ),
    "leaving": (
        "Off you go. Tell me how it went later.",
        "Have a good one.",
        "Right — good luck with it.",
    ),
    "leaving_bed": (
        "Sleep well. I'll be here tomorrow.",
        "Night, then. Get a proper sleep.",
        "Off to bed — good. Talk tomorrow.",
    ),
    "home_again": (
        "Home at last. Feet up first, everything else after.",
        "Long day? Get something to eat before the rest of it.",
        "Nice one. What's the plan for the evening?",
    ),
    "wish_luck": (
        "Good luck! You'll be fine — you've prepared more than you think.",
        "Fingers crossed. Deep breath first, then go.",
        "Good luck — slow and steady beats perfect.",
    ),
    # The person says where they are or where they are going, and a friend says one short line
    # about it - not "Is there anything you'd like a hand with?", which fits every message ever
    # sent. `cutting` finds the person in the middle of a journey, `in_bed` a night already
    # started, `awake` a night that has gone wrong, `chore` a job waiting for them.
    "underway": (
        "No rush at this end — mind how you go.",
        "Safe trip. I'll be here when you land.",
        "Nearly there is the worst bit of any journey. Hope the rest is easy.",
        "Take your time. Nothing here is going anywhere.",
    ),
    "in_bed": (
        "Bed is the right call. Sleep well.",
        "Good. Get an early night while you can.",
        "In bed is the best place to be by this hour. Night.",
    ),
    "awake": (
        "Since {when}? That's a long stretch. Fingers crossed for a better night tonight.",
        "Awake since {when} is rough. A dark room and no phone is the only trick I know.",
        "{when} is a long time to be lying awake. Nap at the first chance you get.",
    ),
    "chore": (
        "The {what} can wait a minute. It always takes longer than you think, mind.",
        "Get a list or a podcast on and the {what} goes faster.",
        "Nobody ever regrets doing the {what} early. Not a fun one, though.",
    ),
}
