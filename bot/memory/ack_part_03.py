"""Part 3 of 7 of the module, split out of `ack`.

Everything here is re-exported from `ack`, so callers import it from there as before.
"""
import re

from ..compose import loss, pick
from ..compose.badnews import reads_as_bad_news
from . import opening
from . import topics
from .ack_part_01 import (
    DIARY_THING, OCCASIONS,
)
from .ack_part_02 import (
    DESTINATION, NOT_A_TRIP, OBLIGED, PAST_PLAN, THING_BEFORE, TRIP_VERB, GREETING,
)


# A deadline can only cut an answer down when the answer was telling them what to do. After a list
# of facts - "how much water should i drink", "im allergic to peanuts" - there is no first step to
# point at and nothing with a day on it, so "tomorrow" has nothing to be close to. The mood of the
# answer's opening is what tells them apart: advice starts on the doing word, a fact starts on the
# thing the fact is about.
STEP_OPENS = re.compile(
    r"^\s*(?:first|firstly|start|begin|own|book|name|skip|put|blot|pour|turn|take|check|keep|let|"
    r"leave|get|add|cut|fill|soak|wash|rinse|call|ask|write|print|plan|split|break|set|read|look|"
    r"watch|listen|tell|say|try|do|go|sit|spend|give|use|make|run|buy|pick|wear|choose|cook|boil|"
    r"roast|fry|steam|bake|rest|chill|freeze|store|measure|weigh|clean|wipe|scrape|open|hold|walk|"
    r"drive|move|cover|line|grease|trim|water|feed|brush|email|text|ring|phone|budget|save|"
    r"avoid)\b", re.I)


def _tells_them_what_to_do(said):
    """Whether the answer just given was advice they can act on, rather than a list of facts."""
    opening = re.split(r"(?<=[.!?])\s+", str(said or "").strip(), maxsplit=1)[0]
    return bool(STEP_OPENS.match(opening.strip()))


# A birthday nobody reached ("my mum would have been 70 this week") is grief, not a fact, and
# saying it back is the coldest reply there is: "your mum would have been 70 - noted". A line
# with a life cut short in it is left to bot/compose/loss.py, and a stock reply beats an echo.
WOULD_HAVE_BEEN = re.compile(r"\bwould(?:\s*have|'ve)?\s+(?:\w+\s+){0,2}been\b", re.I)


# A body that hurts is not a fact to read back either: "you've got a urine infection - noted"
# is a clerk reading a form, and "your dog choked on a bone - noted" says nothing about the
# dog. The emergency and the health modules answer those lines; where they do not, the stock
# line is still better than the echo. The typo'd spellings are here too: `infec` reaches
# "infecshun", and `sezure` is a fit typed fast.
#
# Only the words a person means about a body are here. "i burnt the toast", "im sick of my job"
# and "the printer is broken" are said back happily, and "bleed" is left out because a radiator
# and a bank account are bled too: the dry one is below, and BLEED covers the cut. A temperature
# is a measurement rather than a complaint, so "my daughter is 3 and has a temperature of 38.2"
# is read back like the fact it is; the fever next to it is not.
BODY = re.compile(
    r"\b(?:pain\w*|ache\w*|aching|hurts?|hurting|illness|poorly|unwell|fever\w*|"
    r"rash\w*|swell\w*|swollen|infec\w*|antibiotic\w*|blood\w*|"
    r"choked?|choking|swallow\w*|dizz\w*|nausea\w*|vomit\w*|diarrhoea|migraine\w*|"
    r"sore|cramp\w*|symptom\w*|injur\w*|wound\w*|fractur\w*|"
    r"surger\w*|operation|a&e|111|999|seiz\w*|sezure|breathless\w*|x-ray|xray)\b", re.I)


# A line that is only how the body is ("im shaky", "im bunged up", "im queezy") is not a fact
# about the world: said back it is "Noted: you're bunged up", which gives the person nothing to
# do with it. What it wants is one practical thing and a question, and bot/compose/fallback.py
# has a pool for each kind of state (BODY_STATES). The words are listed here as well because the
# echo has to decline the line first and bot/memory must not import bot/compose. They are only
# read when the line is nothing but the state, so "im queasy about the move" keeps its own
# answer.
BODY_STATE_WORDS = frozenset("""faint faintish fainting woozy dizzy giddy groggy wobbly shaky
clammy sweaty queezy queasy nauseous nauseated bilious sickly bunged sniffly sniffles sniffing
croaky hoarse congested sneezing lightheaded
pale pallid ashen grey gray greyish grayish mottled blotchy spotty puffy bloated flushed
feverish shivery tender husky snotty""".split())


BODY_STATE_PHRASES = frozenset(("light headed", "bilious", "bunged up", "blocked up"))


# What can follow the state and leave the state the whole of the line: "im bunged up now",
# "im shaky again".
BODY_STATE_TAIL = frozenset("""today tonight now still again though honestly already here
actually really so very absolutely bloody thanks up and""".split())


def _a_bare_state(clean):
    """Whether the line is nothing but a state of the body ("im bunged up", "im shaky")."""
    words = [w.strip(".,!?;:") for w in clean.replace("-", " ").split()]
    words = [w for w in words if w]
    if words[:1] in (["im"], ["i'm"], ["iam"]):
        words = words[1:]
    elif words[:2] == ["i", "am"]:
        words = words[2:]
    else:
        return False
    if not words:
        return False
    if " ".join(words) in BODY_STATE_PHRASES:
        return True
    return (any(w in BODY_STATE_WORDS for w in words)
            and all(w in BODY_STATE_WORDS or w in BODY_STATE_TAIL for w in words))


# "my nose is bleeding" is a body, "my dad is bleeding me dry" and "how do i bleed the radiator"
# are not, so the word only counts when it is not that shape.
BLEED = re.compile(r"\bbleed\w*\b(?![^.!?]{0,12}\b(?:dry|radiator|boiler|pipe\w*)\b)", re.I)


SELF_INTRO = re.compile(r"^\s*(?:i(?:'m| am)|im|my name(?:'s| is))\s+[A-Z][a-z'\u2019-]+\b")


# A greeting is the chat module's turn even when it does not open with "hi": "nice to meet you,
# i'm Sam" said back loses the word it opens with, because "nice" is a lead-in here, so the echo
# came out as "to meet you sam!" - half a sentence, and the hello unanswered. Every way of
# meeting somebody, and the how-are-yous, which are greetings and not a fact to file.
MEET_GREET = re.compile(
    r"^\s*(?:(?:nice|good|great|pleased|lovely|glad|happy|grand)\s+to\s+"
    r"(?:meet|see|hear\s+from)\s+(?:you|u|ya)\b"
    r"|(?:good|great|lovely|nice)\s+to\s+have\s+you\b"
    r"|how\s+(?:are|r)\s+(?:you|u|ya)\b"
    r"|how(?:'s|s|\s+is)\s+(?:it\s+going|things|tricks|you\s+doing|your\s+day)\b"
    r"|how\s+do\s+you\s+do\b"
    r"|long\s+time\s+no\s+see\b)", re.I)


# Where the echo stops: a full stop always, "and" only when a new subject starts after it.
SUBJECT = (r"(?:i|i'm|im|i've|i'd|we|we're|my|our|mine|she|she's|he|he's|it|it's|they|"
           r"they're|his|her|its|their)")


# A comma only ends a clause when a space follows it, so "6,000" and "£1,50" stay whole.
STOP = re.compile(r"\s*(?:,\s|;|\.\s|$|\b(?:because|so|but)\b|\b(?:and|then)\b\s+(?="
                  + SUBJECT + r"\b))\s*", re.I)


WORD = re.compile(r"[A-Za-z0-9'\u2019-]+")


# Thanks on the end of a fact ("my dog is fine now thanks") is not part of the fact.
POLITE = re.compile(r"[,\s]+(?:thanks|thank you|cheers|ta|please|thx)\s*$", re.I)


from .filler import TAIL_OFF, without_filler  # noqa: F401  (the echo drops the same filler)


# A fact to say back is a state of their world: who someone is, how old, where, what they are
# planning, what they are allergic to. The second person's *actions* are another matter: "my
# husband never helps" or "my son is being bullied" are things to answer kindly, not to read
# back, so a line with a word of trouble in it is left to the modules that answer them.
STATE = re.compile(
    r"\b(?:is|are|am|im|'s|'re|'m|was|were|has|have|had|'ve|ive|can|will|'ll|need|needs|want|wants|"
    r"live|lives|work|works|study|studies|love|loves|like|likes|prefer|prefers|go|goes|going|"
    r"off to|plan|plans|planning|train|training|learn|learning|move|moving|fly|flying|getting|"
    r"got|adopted|allergic|spend|save|saving)\b", re.I)


TROUBLE = re.compile(
    r"\b(?:being|bullied|bullies|bully|teas\w+|never|always|keeps|kept|refuses|refused|"
    r"stopped|stops|quit|hates?|hated|hit|hits|shout\w*|yell\w*|scream\w*|argu\w*|row|"
    r"won'?t|doesn'?t|didn'?t|isn'?t|can'?t|cannot|failed|failing|behind|ignores?|ignored|"
    r"blames?|blamed|lost|losing|dead against|just want|just need|driving me|drives me|"
    r"doing my head in|fed up|sick of|had enough|tether|drives? me mad)\b", re.I)


# Words that carry no meaning of their own when deciding whether a line says anything new.
_EMPTY = frozenset("""a an the and or but if so then this that these those it its it's i i'm im me my
we we're us our you your he she they them his her their is are was were be been being am 's 're
of to in on at for with from about as not no do does did have has had will would can could just
really very too also still now""".split())


# Lines that are answered elsewhere, or that no echo can carry: a farewell, a summons back to an
# old subject ("back to the radiator"), a yes/no read of the last turn ("no, no temperature"), and
# a feeling, which wants a word of its own rather than the fact said back.
# A complaint about how someone treated them, or a penalty that landed on them: "my boss had a
# go at me", "i got a parking ticket", "i got a fine". Two things follow. Said back ("Got it -
# your boss had a go at you") it is only the bad thing again, so it is not a detail; and it is not
# small talk either, so the gentle pool is a better answer than a stock nod. The forms the trouble
# words already carry ("shouted at me", "had a row") are caught before this one.
# A feeling is the modules' turn, never the echo's: "you want to cry - noted" answers nothing
# about the crying, and "for moaning - noted" is cold to someone apologising for it. The words are
# only the ones that can be about how a person feels.
_FEELING_WORDS = (
    r"worried|frightened|scared|terrified|afraid|fear\w*|dread\w*|anxious|panic\w*|"
    r"overreacting|upset|angry|annoyed|sad|lonely|guilty|embarrassed|ashamed|stressed|"
    r"exhausted|knackered|weary|miserable|cry|cried|crying|tears?|sob\w*|moan\w*|whinge\w*|"
    r"whine|rant\w*|vent\w*")


A_FEELING = re.compile(r"\b(?:" + _FEELING_WORDS + r")\b", re.I)


# A good mood is a feeling too, and filing it as a fact says it back as an entry in a notebook:
# "life is good" was answered "Got it - life is good." The words here are the mood said without
# an event in it; a line that carries news as well ("im happy, i got the job") is left alone
# because a job, a baby or a pass is a fact and the news modules answer it better.
GOOD_MOOD = re.compile(
    r"\b(?:in (?:a|an) (?:very )?(?:good|great|fine) mood|good mood|great mood|feeling good|"
    r"feel good|feeling great|feel great|cheerful|cheery|in good spirits)\b", re.I)


A_EVENT = re.compile(
    r"\b(?:job|promotion|baby|exam|test|interview|offer|house|flat|course|degree|wedding|"
    r"engagement|engaged|pregnant|expecting|won|passed|accepted|hired|booked|sold|bought|"
    r"holiday|graduated|qualified|retired)\b", re.I)


# A good result is news too, and it says it without any of the nouns above: "i feel good, i got
# the all clear" is a scan, not a mood. Kept as its own pattern because it is a phrase, not a
# word.
A_CLEAR = re.compile(
    r"\b(?:all clear|(?:came|come|comes) back clear|(?:scan|results?|tests?) (?:was|is|were|are) "
    r"clear|given? the all clear)\b", re.I)


# A result is reportable whatever its noun, and a closed list of nouns missed most of them: a
# daughter into university, a dissertation finished, a day that went well. The shape is what makes
# it news - someone who did the thing, and the thing said as done - so the mood word is left with
# the mood pool only when no such clause is there.
A_RESULT = re.compile(
    r"\b(?:i|we|he|she|they|my \w+|our \w+)\s+(?:(?:just|finally|only|also|now)\s+)?"
    r"(?:got|gotten|finished|finishes|started|starts|passed|passes|won|wins|landed|booked|"
    r"sold|bought|completed|handed in|graduated|qualified|retired)\b"
    r"|\b(?:went|gone) (?:well|great|brilliant|fine)\b"
    r"|\bout of (?:the )?hospital\b|\bhome from (?:the )?hospital\b", re.I)


# Moving is news when it is a move to a place, not when it is a sofa: "i moved the sofa" was read
# as an event and lost the mood pool it had on main.
A_MOVED = re.compile(r"\b(?:moved|moving|move) (?:in|into|to|house|out|abroad|back|country)\b",
                     re.I)


def has_news(text):
    """Whether the line carries something that happened, as opposed to how they feel."""
    text = text or ""
    return bool(A_EVENT.search(text) or A_CLEAR.search(text) or A_RESULT.search(text)
                or A_MOVED.search(text))


COMPLAINT = re.compile(
    r"\bhad a (?:go|dig|pop) at\b|\b(?:gave|given|handed) me a (?:ticket|fine|bollocking)\b|"
    r"\b(?:got|get|gets|getting|received) (?:a |an |the |my )?(?:parking |speeding |"
    r"fixed penalty )?(?:ticket|penalty|caution|warning|bollocking)\b|"
    # "fine" is an ordinary word too ("we got a fine view of the bay"), so it counts only when
    # nothing pleasant follows it.
    r"\b(?:got|get|gets|getting|received|gave me) (?:a |an |the )?fine\b"
    r"(?!\s+(?:view|views|day|time|weather|meal|bit|line|mess|idea|point|thing|way|year))|"
    r"\b(?:parking|speeding) ticket\b|\bclamped\b|\b(?:a|the) telling off\b|"
    r"\btold (?:me )?off\b|\ba bollocking\b", re.I)


_NOT_A_DETAIL = re.compile(
    r"\b(?:bye|goodnight|good night|catch (?:you|up)|speak (?:later|soon)|talk later|see you|"
    r"night then|anyway|back to|as i said|like i said|nothing much|not much|"
    r"can'?t complain|same old|same as ever|not a lot|how about you|you\?|"
    r"fair enough|sounds good|(?:i'?ll|i will|ill) (?:try|give) (?:that|it)|will do|no worries|"
    r"nice one|same to you|not bad|all good|"
    # A line about the conversation rather than about the thing we are on: "i want to say
    # something", "how do i put it", "soz meant tuesday" - the corrections and the small talk
    # have their own answers, and saying these back adds nothing.
    r"want(?:ed)? to (?:say|ask|tell)|how (?:do|should) i put it|\bmeant\b|\bsoz\b|"
    # A line about what was said rather than about the thing: "lol i said that ages ago",
    # "i told you already" - said back it is only the complaint again.
    r"\bi (?:said|told you|mentioned|already|just said)\b|\bas i said\b|\blike i said\b|"
    # A complaint about someone else, or a misfortune that landed on them, wants a sympathetic
    # word: said back it is only the bad thing again.
    + COMPLAINT.pattern +
    r"|" + _FEELING_WORDS + r")\b", re.I)


_SAID_YES_NO = re.compile(r"^(?:no|nope|nah|yes|yeah|yep)\b(?=[,.!]|\s+(?:please|thanks|thank you|"
                          r"mate|then)\b|$)", re.I)


_ANSWER_OPENER = re.compile(r"^(?:ok|okay|course|right)\b[ ,]", re.I)


# A question without its question mark: "they want 30 days notice is that normal" asks
# something, and a question said back is the question repeated.
_ASKS_MIDWAY = re.compile(r"\b(?:is|are|was|were|do|does|did|can|could|should|would|will|shall|"
                          r"have|has)\s+(?:it|that|this|they|i|we|you|he|she)\b", re.I)


# A request for a recommendation ("anything funny on netflix", "something with chicken") said
# back is the question repeated, which helps nobody: those lines want an answer, not an echo.
_ASKED_FOR = re.compile(r"^(?:any|anything|something|someone|somewhere|nowhere|nothing)\b", re.I)


DIGIT = re.compile(r"\d")


# Something of theirs that has gone wrong: "the washing machine is making a bang on the spin" is
# a fault to sort out, and "I'll remember that" about a bang is worse than no reply at all.
_FAULT = re.compile(
    r"\b(?:leak\w*|drip\w*|blocked|clogged|jammed|stuck|won'?t start|won'?t turn on|"
    r"stopped working|not working|isn'?t working|broken|broke|bang(?:s|ing)?|rattl\w*|noisy|"
    r"grind\w*|screech\w*|whin\w*|error code|flashing|blinking|rust\w*|damp|mould\w*)\b",
    re.I)


# Subjects no echo can serve, whatever the new line adds to them.
_NOT_A_DETAIL_SUBJECT = re.compile(
    r"\b(?:funeral|grief|passed away|passed on|death|died|widow|hospital|diagnos\w*|"
    r"lost (?:the|our|a) (?:baby|pregnancy)|miscarriage|stillborn|"
    r"cancer|chemo|depress\w*|anxiety|breakup|broke up|divorce)\b", re.I)


FRAGMENT = 30  # a short answer with no verb at all ("Tokyo and Kyoto") still reads well back


# "w/ the kids" is "with the kids" before anything else reads the line.
WITH_SLASH = re.compile(r"\bw/\s*", re.I)


# "going 2 spain", "back 2 work": after a verb of moving, the figure is the word "to". Everywhere
# else it is a number ("he is 2 yrs old"), which reads back as a word. A length of time is the
# exception the verb cannot see: "im going 2 weeks in may" is two weeks away, and saying it back
# as "you're going to weeks in may" invents a place out of a duration. The units are the ones a
# length of time is said in, and a unit is never somewhere you go - with two exceptions that do
# name a place: "night school" and "the weekend job". So "im going 2 night school" stays "to".
DURATION_UNITS = frozenset("""week weeks day days month months year years hour hours
fortnight fortnights minute minutes min mins""".split())


TWO_TO = re.compile(r"\b(?:going|go|goes|went|off|back|fly|flying|drive|driving|walk|walking|"
                    r"head|heading|move|moving|travel|travelling|coming|come|be|been)\s+2\b"
                    r"(?!\s*(?:%s)\b)" % "|".join(sorted(DURATION_UNITS)), re.I)


# The same figure in front of a place, with no verb in between: "2 the gym", "2 bed", "2 work".
TWO_PLACE = re.compile(r"\b2\s+(?=(?:the|a|an|my|our|his|her|their|its|work|bed|school|town|"
                       r"uni|university|college|church|hospital|town)\b)", re.I)


# "need 2 go", "have 2 work late": in front of a verb the figure is "to" again, and in front of a
# noun it is not - "have 2 kids" is two children, not "to kids".
TWO_VERB = re.compile(r"\b2\s+(?=(?:go|get|come|see|do|be|make|take|put|give|tell|say|try|book|buy|"
                      r"ask|call|send|pay|sort|check|fix|start|stop|leave|stay|eat|drink|sleep|run|"
                      r"walk|drive|catch|meet|pick|order|cook|clean|wash|pack|post|ring|text|email|"
                      r"look|find|keep|learn|help|join|move|remember|finish|read|get)\b)", re.I)


# Chat-speak the person typed, folded before the echo: "im allergic" is said back as "you're
# allergic", which reads like a person wrote it. Only forms with one reading are here.
SPEAK = {"im": "i'm", "ive": "i've", "i'd": "i'd", "id": "i'd", "ill": "i'll",
         "dont": "don't", "didnt": "didn't", "doesnt": "doesn't", "cant": "can't", "wont": "won't", "isnt": "isn't",
         "wasnt": "wasn't", "werent": "weren't", "arent": "aren't", "havent": "haven't",
         "hasnt": "hasn't", "couldnt": "couldn't", "wouldnt": "wouldn't", "shouldnt": "shouldn't",
         "thats": "that's", "its": "it's", "youre": "you're", "weve": "we've", "theres": "there's",
         "hes": "he's", "shes": "she's", "theyre": "they're", "youve": "you've"}


# "its" is two words in one, and only one of them is chat-speak: "its going to set me back 300" is
# "it is", where "its screen" owns the screen. Folding every one handed the person their own line
# back as "your phone got it's screen replaced", so the word in front decides. The contraction
# opens a clause - "its going", "its 8 years old", "my nan got her hair done and its lovely" - and
# the possessive comes after the verb or the preposition that hands something over: got its screen,
# sold its car, changed its opening hours, on its side. Only those handing-over shapes are listed,
# so a line that is not one of them keeps the fold it had.
ITS_OWNS_AFTER = frozenset("""
    on in at to from of for with by into onto near under over behind inside outside off about
    got gets gotten get had has have having sold sell sells bought buy buys changed change changes
    lost lose loses moved move moves took take takes taken gave give gives made make makes used
    use uses keeps keep kept needs need needed left leaves
    replaced replaced fitted fixed cleaned painted washed dropped scratched licked wore worn cut put
    set parked serviced insured registered broke eaten bit hit
    """.split())


# The short forms people type rather than say, folded the same way and for the same reason. The
# echo is the bot's own sentence, so it comes back in whole words: "your drum kit is 9 yrs old n
# it's loud" hands the person their own typing back, where a friend says "nine years old and the
# drum is loud". Every entry has one reading in an everyday line, so nothing has to be guessed.
SHORT = {"yrs": "years", "yr": "year", "mth": "month", "mths": "months", "wk": "week",
         "wks": "weeks", "u": "you", "ur": "your", "r": "are", "n": "and",
         "tho": "though", "coz": "because", "cuz": "because", "b4": "before",
         "abt": "about", "tmrw": "tomorrow", "2moro": "tomorrow", "nite": "night",
         "pls": "please", "thx": "thanks", "luv": "love", "ya": "you", "yer": "your",
         "goin": "going", "doin": "doing", "havin": "having", "nuthin": "nothing",
         "somthing": "something", "w": "with", "2": "two",
         "gonna": "going to", "wanna": "want to"}


# "yer" is two words in one: "yer coat" owns the coat, and "yer i tried that" opens with a yes.
# The word after it decides, and only a pronoun or the start of a sentence can make it a yes, so
# the echo no longer hands "Your you tried that" back to someone (gentle-chair, #conversation).
YES_AFTER = frozenset("""i im ive id ill it its that thats the we they you he she my our
    no yes dont didnt doesnt cant could is was there here what how why when where who ok okay
    just so but and can do does did nah yep yeah.""".split())


# How much of what they said can come back: two clauses, and never more than this many letters.
CLAUSES = 2


MOST = 90


def _repaired(clean, memory):
    """The line with the words that were wrong repaired, for the guards that match English.

    `clean` stays exactly as typed, because that is what the echo says back to the person -
    repeating "kiling" at somebody who can spell it is the cold part of "Got it". But a symptom,
    a fault and bad news are matched on the words of English, so a slip hides them: "my back is
    kiling me" is a body that hurts, not a fact to file away. The repaired line is the engine's
    own reading (`understood["plain"]`), and only when that reading is of this line.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return clean
    if understood.get("clean") != clean.lower():
        return clean  # a reading of some other line: never decide on it
    return understood.get("plain") or clean


# The frames a correction is said back in, with the unit of the line before it: "four" after
# "three times a week" is "Four times a week, then."
CORRECTED_WITH_UNIT = (
    "{Value} {unit}, then.",
    "Got it \u2014 {value} {unit}.",
    "{Value} {unit}, got it.",
)


# The same frames for a value that already carries its own unit: "the run is 5 km" then "make it
# 10 km" was "10 km km, then.", because the unit of the line before was put on a figure that had
# been said with a unit of its own. A figure that measures itself needs nothing added to it.
CORRECTED_ALONE = (
    "{Value}, then.",
    "Got it \u2014 {value}.",
    "{Value}, got it.",
)


# The unit words a value can carry at its end, and the short forms a figure can be glued to ("10km",
# "5k", "250ml"). A value ending in one of these measures itself.
# "times", "per", "every" and "a" are left out on purpose: they start a measure rather than being
# one, so "i do yoga twice a week" then "change it to three times" still needs the "a week" of the
# line before it and answers "Three times a week, got it."
# "day" and "days" belong here and were the one pair missing: "the course runs 3 days" then
# "actually make it 4 days" answered "4 days days, got it." on main `c4eceacd`, while "6 weeks",
# "6 nights" and "3 hours" were all right, because every other unit the store reads was in the
# list. "ft", "meter(s)" and "yard(s)" were missing too. The set is not written by hand here any
# more: the test beside this module fails if a unit in `A_MEASURE` - the table that says what each
# unit measures - is missing from it, so the next unit added is read the same day it is added.
VALUE_UNIT_WORDS = frozenset("""km k mile miles kilo kilos kg kgs g gram grams stone stones lb
    lbs foot feet ft inch inches cm m metre metres meter meters yard yards
    liter litre liters litres ml pint pints hour hours
    hr hrs minute minutes min mins day days week weeks wk month months year years time
    pound pounds quid dollar dollars euro euros
    morning evening night weekend cup cups spoon spoons egg eggs""".split())


VALUE_UNIT_GLUED = re.compile(r"^\d[\d,]*(?:\.\d+)?([a-z]{1,5})$", re.I)


# What each unit word measures. The unit of the line before is only said again when it measures
# something else: "5 km" then "10 miles" is still a distance, so "10 miles, then." and never "10
# miles km, then.", while "5k every morning" then "10k" keeps "every morning" because a distance
# and a routine are two different measures of the same line.
A_MEASURE = {
    "km": "distance", "k": "distance", "mile": "distance", "miles": "distance",
    "m": "distance", "metre": "distance", "metres": "distance", "meter": "distance",
    "meters": "distance", "foot": "distance", "feet": "distance", "ft": "distance",
    "inch": "distance", "inches": "distance", "cm": "distance", "yard": "distance",
    "yards": "distance",
    "kilo": "weight", "kilos": "weight", "kg": "weight", "kgs": "weight", "g": "weight",
    "gram": "weight", "grams": "weight", "stone": "weight", "stones": "weight",
    "lb": "weight", "lbs": "weight", "pound": "money", "pounds": "money",
    "quid": "money", "dollar": "money", "dollars": "money", "euro": "money",
    "euros": "money",
    "hour": "time", "hours": "time", "hr": "time", "hrs": "time", "minute": "time",
    "minutes": "time", "min": "time", "mins": "time", "week": "time", "weeks": "time",
    "wk": "time", "month": "time", "months": "time", "year": "time", "years": "time",
    "day": "time", "days": "time", "morning": "time", "evening": "time",
    "night": "time", "weekend": "time", "time": "time", "times": "time", "per": "time",
    "a": "time", "an": "time", "every": "time",
    "litre": "volume", "litres": "volume", "liter": "volume", "liters": "volume",
    "ml": "volume", "pint": "volume", "pints": "volume", "cup": "volume",
    "cups": "volume", "spoon": "volume", "spoons": "volume",
    "egg": "count", "eggs": "count",
}


# A frequency said as a single word is a whole measure on its own: "three times a week" then
# "sorry, twice" is "Twice, got it." and never "Twice times a week". "three times" is not one -
# "times" starts a measure - so that shape still takes the "a week" of the line before.
WHOLE_FREQUENCY = frozenset("""once twice thrice daily nightly weekly fortnightly monthly
    quarterly yearly annually hourly""".split())


def _the_values_measures(value):
    """The kinds of measure the value is already said in: "10 km" -> {"distance"}.

    A unit word anywhere in the value counts, not only the last one, because "4 miles each way"
    carries its miles in the middle and appending "miles" to it said the unit twice. "three times"
    names none: "times" starts a measure rather than being one (see VALUE_UNIT_WORDS), so the
    "a week" of the line before is still needed to finish it. "twice" does name one, and so does
    "daily": a frequency said in one word needs nothing put after it.
    """
    found = set()
    for word in str(value or "").split():
        if word.strip(".,!?;:'\u2019").lower() in WHOLE_FREQUENCY:
            found.add("time")
        word = word.strip(".,!?;:'\u2019").lower()
        glued = VALUE_UNIT_GLUED.match(word)
        if glued:
            word = glued.group(1).lower()
        if word in VALUE_UNIT_WORDS:
            found.add(A_MEASURE.get(word, word))
    return found


def _the_units_measure(unit):
    """The kinds of measure the unit of the line before names: "every morning" -> {"time"}."""
    found = set()
    for word in str(unit or "").split():
        measure = A_MEASURE.get(word.strip(".,!?;:'\u2019").lower())
        if measure:
            found.add(measure)
    return found


def _the_unit_is_said_twice(value, unit):
    """Whether saying the line's unit after this value would measure the same thing twice.

    "5 km" then "10 km" (or "10km", or "10 miles", or "4 miles each way"): the line before
    measures a distance and so does the new figure, so its unit on the end is a second measure of
    the same thing ("10 km km, then."). "5k every morning" then "10k" is different - a distance
    and a routine - and the routine still belongs to the line, which is why "Got it - 10k every
    morning." stays right there.
    """
    here = _the_values_measures(value)
    there = _the_units_measure(unit)
    if here and there:
        return bool(here & there)
    return False


# The words people put in front of a figure they are taking back, and the words they put after it.
# A correction with no verb is a frame around a figure - "sorry 1150, i got it wrong", "1150 sorry",
# "hang on, 1150", "no its 1150", "1150, not 1200", "sorry, i got it wrong, 1150" - so the frame is
# peeled off both ends and what is left has to be a figure. One reader for all of them: on main the
# shapes with no "make it" in them were answered as news ("What was it like?") or with a stall
# ("I'm listening - say more if it helps."), one line after the person had put their figure right.
PUT_RIGHT_LEAD = (
    ("i", "got", "it", "wrong"), ("got", "it", "wrong"), ("i", "made", "a", "mistake"),
    ("i", "was", "wrong"), ("my", "mistake"), ("silly", "me"), ("i", "mean"), ("i", "meant"),
    ("hang", "on"), ("hold", "on"), ("correction",), ("actually",), ("sorry",), ("wait",),
    ("nope",), ("nah",), ("no",), ("its",), ("it's"),
    # "and", "so", "oh", "well" and "ok" are not openers here on their own: "i walk 5 km" then
    # "and 40 minutes" is a second measure, not a figure taken back.

)


PUT_RIGHT_TAIL = (
    ("i", "got", "it", "wrong"), ("got", "it", "wrong"), ("i", "made", "a", "mistake"),
    ("i", "was", "wrong"), ("my", "mistake"), ("silly", "me"), ("i", "mean"), ("i", "think"),
    ("thanks",), ("sorry",), ("actually",), ("then",), ("right",), ("though",),
)


def _without_a_frame(words, phrases, back=False):
    """The words left when a frame phrase is taken off one end, and whether one was taken."""
    words = list(words)
    took = False
    while words:
        for phrase in phrases:
            end = words[-len(phrase):] if back else words[:len(phrase)]
            said = tuple(word.lower().strip(".,!?;:'\u2019") for word in end)
            if said == phrase:
                words = words[:-len(phrase)] if back else words[len(phrase):]
                took = True
                break
        else:
            break
    return words, took


def _without_a_not(words):
    """The words with a trailing "not <figure>" taken off, which is the figure being taken back."""
    if len(words) >= 3 and words[-2].lower().strip(".,!?") == "not" \
            and re.search(r"\d", words[-1]):
        return words[:-2], True
    return list(words), False


def _the_bare_value(clean):
    """The figure a correction names when it has no verb in it, or "" when it is not one.

    The frame has to be there - a figure on its own ("1150") answers a question as often as it
    corrects a line - and the figure is what is left between the frame in front and the one
    behind. "1150, not 1200" keeps 1150: the figure after "not" is the one being taken back.
    """
    words = [word for word in re.split(r"[\s,]+", (clean or "").strip(" .!?")) if word]
    if not words:
        return ""
    words, led = _without_a_frame(words, PUT_RIGHT_LEAD)
    words, _ = _without_a_not(words)
    words, tailed = _without_a_frame(words, PUT_RIGHT_TAIL, back=True)
    if not (led or tailed):
        return ""
    if not words or len(words) > 4:
        return ""
    return " ".join(words).strip(" .,!?")


def _without_a_unit_already_in_the_value(value, unit):
    """The unit of the line before with the word the value already ends in taken off.

    "i swim 3 times a week" then "sorry 5 times" is "5 times a week" - the value carries the
    "times" and the line carries the "a week" - and it was "5 times times a week, then." because
    the unit of the line before is read from after its figure, "times a week", and put on a value
    that had just said "times" itself.
    """
    unit_words = str(unit or "").split()
    value_words = str(value or "").split()
    if len(unit_words) < 2 or not value_words:
        return unit
    last = value_words[-1].strip(".,!?;:'\u2019").lower()
    if last == unit_words[0].strip(".,!?;:'\u2019").lower():
        return " ".join(unit_words[1:])
    return unit


def _the_line_before(memory):
    """The line the person said just before, or "" when there is none."""
    if not isinstance(memory, dict):
        return ""
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return ""
    last = turns[-1]
    said = last.get("user") if isinstance(last, dict) else None
    return said if isinstance(said, str) else ""


# An animal given to a new home is a loss, and it was said back as a fact: "we had to give our
# dog away" got "Noted: you had to give your dog away.", the coldest line there is for somebody
# who has just given up an animal they loved. The store hears it either way - the animal comes
# off the list, and "we had to give the dog away" is not a claim that there is no dog in the
# house - so the echo is the one place to say what a friend says.
#
# The reading needs the gesture and the animal both: "i had to give the dog a pill" is a dog
# being looked after, and "we gave up bread" is an animal in none of it. The line has to say
# the giving up happened ("had to", "gave ... away") - the plan ("i need to rehome my dog")
# and the question ("how do i rehome my dog") are the rehoming entry's, and they are kept out
# by the statement guard and by needing the past or the compulsion.
GIVEN_AWAY = re.compile(
    r"\b(?:had|have|has|got)\s+to\s+give\b[^.!?]{0,30}?\b(?:away|up|back|to)\b|"
    r"\b(?:had|have|has|got)\s+to\s+(?:rehome|surrender|get rid of)\b|"
    r"\b(?:had|have|has|got)\s+to\s+let\b[^.!?]{0,20}?\b(?:go|away)\b|"
    r"\b(?:gave|given|giving)\b[^.!?]{0,30}?\b(?:away|up)\b|"
    r"\b(?:couldn'?t|could not|can'?t|cannot)\s+keep\b|"
    r"\bsurrendered\b|\bhanded (?:him|her|them|it) (?:over|back)\b", re.I)


GIVEN_ANIMAL = re.compile(
    r"\b(dogs?|puppy|pup|puppies|cats?|kitten|kittens|rabbits?|hamsters?|guinea pigs?|parrots?|"
    r"budgie|birds?|horses?|pony|snakes?|lizards?|rats?|ferrets?|tortoises?|pets?)\b", re.I)


# Somebody else's animal: "my mum had to rehome her dog" is a hard thing for the mum, and the
# line about a friend's week is not the user's loss to console.
NOT_THEIRS = re.compile(
    r"\b(?:my|his|her|their|our)\s+(?:mum|mom|mam|dad|father|mother|sister|brother|son|"
    r"daughter|nan|gran|granny|aunt|uncle|friend|mate|neighbou?r|colleague|boss|partner|wife|"
    r"husband|cousin)\b", re.I)


GIVEN_AWAY_REPLIES = (
    "That's a hard thing to do, and I doubt giving up a {animal} was an easy call.",
    "Giving up a {animal} is usually a last resort, so I doubt you came to it lightly.",
    "I'm sorry \u2014 giving up a {animal} is one of the harder decisions there is.",
    "That can't have been easy. You did right by the {animal}, whatever the reasons.",
)


def _the_animal_given_away(text, memory=None):
    """The animal the line hands over, as a word to put in a sentence ("dog"), or "".

    The line usually names the kind ("our dog", "the cats"), and when it names only the
    animal - "we gave max away last week" - the record the store has just taken off the list is
    where the kind is. Without either there is nothing to say the warm line about.
    """
    found = GIVEN_ANIMAL.search(text)
    if found:
        kind = found.group(1).lower()
        return kind[:-1] if kind.endswith("s") and not kind.endswith("ss") else kind
    gone = memory.get("denial") if isinstance(memory, dict) else None
    records = gone.get("pets") if isinstance(gone, dict) else None
    said = text.lower()
    for record in records or []:
        if not isinstance(record, dict):
            continue
        name = str(record.get("name") or "").strip().lower()
        if name and re.search(r"\b" + re.escape(name) + r"\b", said):
            kind = str(record.get("animal") or "pet").lower()
            return kind[:-1] if kind.endswith("s") and not kind.endswith("ss") else kind
    return ""


def pet_given_away(text, memory=None):
    """The warm line for an animal given to a new home, or None when this is another line.

    bot/modules/memory_store.py asks this on the turn it takes the animal off the list, and
    `reply` asks it for a line the store had no record of: either way the person gets the same
    kind of answer, and never "Right \u2014 no dog, then." for a dog they loved.
    """
    if not isinstance(text, str):
        return None
    clean = " ".join(text.split())
    if not clean or not GIVEN_AWAY.search(clean):
        return None
    if NOT_THEIRS.search(clean) and not re.match(r"\s*(?:i|we)\b", clean, re.I):
        return None  # somebody else's pet, told as their news rather than the user's
    kind = _the_animal_given_away(clean, memory)
    if not kind:
        return None
    return pick(GIVEN_AWAY_REPLIES, memory if isinstance(memory, dict) else {},
                seed_text=clean).format(animal=kind)


# A line that offers a chat and says nothing else - "just wanted to chat really", "thought id say
# hello" - has no fact to file and no detail to say back. Read by the fact frames it was answered
# with the sentence itself ("Just wanted to chat really \u2014 noted."), which is the one reply a
# person who came to talk cannot use, and after a hard day it left them a filing receipt. A friend
# says they are here and asks what is on their mind, and the pool is short so it never turns into
# a question about the question.
OFFERS_A_CHAT = re.compile(
    r"^\W*(?:ok|okay|so|well|hi|hey|and)?[,\s]*"
    r"(?:i\s+|we\s+)?(?:just|only|really|actually\s)?\s*"
    r"(?:wanted|want|fancied|feel like|felt like)\s+"
    r"(?:a\s+|to\s+|some\s+)?(?:chat|talk|natter|chinwag)\b"
    r"(?:\s+(?:really|honestly|today|tonight|for a bit|for a while|a bit|with someone|"
    r"to someone|to somebody|with somebody|i suppose|i guess|thats all|that'?s all|"
    r"more than anything|you know|i think|if thats ok|if that'?s ok))*"
    r"[\s.!?]*$"
    r"|^\W*(?:ok|okay|so|well)?[,\s]*(?:i\s+)?(?:just\s+)?(?:wanted|want|fancied)\s+"
    r"(?:someone|somebody)\s+to\s+(?:talk|chat)\s+(?:to|with)?"
    r"(?:\s+(?:really|honestly|today|tonight|a bit|i suppose|i guess))*[\s.!?]*$"
    r"|^\W*(?:i\s+)?thought\s+(?:i'?d|i would)\s+(?:say|pop)\s+(?:hi|hello|in)\b"
    r"(?:\s+(?:really|honestly|today|tonight|i suppose|before i go))*[\s.!?]*$",
    re.I)


CHAT_OFFER_REPLY = (
    "Anytime \u2014 what's on your mind?",
    "I'm here. Anything you want to talk about, big or small?",
    "Good, I've got time. What's been going on?",
    "Any time. What shall we talk about?",
    "Nice \u2014 I'm all yours. What's up?",
)


def _offers_a_chat(clean, memory=None):
    """A short warm yes to a line that came to talk, never the line said back.

    A chat offered in the days after bad news is not a fresh start: "my dad died last month" then
    "just wanted to chat really" is the same grief going on, and the line that said it is still on
    the screen, so that turn keeps the reply it had.
    """
    if not OFFERS_A_CHAT.match(clean or ""):
        return None
    for turn in (memory.get("turns") or [])[-3:] if isinstance(memory, dict) else []:
        said = str((turn or {}).get("user") or "").lower() if isinstance(turn, dict) else ""
        if said and (reads_as_bad_news(said) or loss.reads_as_loss(said)):
            return None
    return pick(CHAT_OFFER_REPLY, memory)


# A date on its own is the date of the thing the chat is already on: "im going to a wedding" and
# then "its in july" were answered "I'm listening - say more if it helps", a line that fits any
# message in the language. The line names no doing, so `_a_day_coming` passes it by - there is no
# trip or appointment in it, only a month - and the thing it is the month *of* is in the store
# already. A friend reads it as the plan's own date and says what the time means for that plan: "A
# july wedding - plenty of time to sort the rest."
A_DATE_ALONE = re.compile(
    r"^(?:(?:ok|okay|so|and|well|oh|hmm|yeah|yes|no)\s*[,\s]\s*)*"
    r"(?:(?:it'?s|its|it is|that'?s|thats|that is|we'?re|we are|the date is|the day is)"
    r"\s+)?(?:in|on|for|by|at the end of|early|late)?\s*"
    r"(?P<when>january|february|march|april|may|june|july|august|september|october|november"
    r"|december|next\s+week|next\s+month|next\s+year|this\s+weekend|the\s+weekend"
    r"|tomorrow|tonight|the\s+\d{1,2}(?:st|nd|rd|th)|\d{1,2}(?:st|nd|rd|th)"
    r"|monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    r"\s*(?:i think|i reckon|i believe|this year|next year|at the latest|i'?m sure)?"
    r"\s*[.!]*$", re.I)


# The months and the weekdays, which take an article and the plan's own word - "a july wedding",
# "a saturday wedding". "a next week wedding" is not English, so the shorter days keep the day
# words alone.
A_MONTH_ALONE = re.compile(
    r"^(?:january|february|march|april|may|june|july|august|september|october|november"
    r"|december|monday|tuesday|wednesday|thursday|friday|saturday|sunday)$", re.I)


A_WEEKDAY = re.compile(r"^(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)$", re.I)


# What the time means for a plan that is in the diary: the same two things every plan wants said
# about it, and neither of them names a month of the year or a kind of day.
A_DATE_ON_A_PLAN = (
    "{Thing} \u2014 plenty of time to sort the rest.",
    "{Thing}. That's something to look forward to.",
    "{Thing} \u2014 what's left to sort?",
    "{Thing}. Good to have the date down.",
)


A_DAY_ON_A_PLAN = (
    "{Thing} \u2014 that is soon, then.",
    "{Thing}. Not long now.",
    "{Thing} \u2014 that comes round quickly.",
)


# A plan the person is not looking forward to cannot be answered with "that's something to look
# forward to": "im nervous about a job interview" then "its on friday" would agree with the surface
# of the line and contradict the person in the same breath (the same rule the occasion pools keep
# under DREADED_OCCASION).
A_WORRIED_ABOUT_IT = re.compile(
    r"\b(?:nervous|worried|worry|worrying|dreading|dread|scared|afraid|anxious|panic|hate|"
    r"stress(?:ed|ful)?|not looking forward|can'?t face)\b", re.I)


A_DATE_ON_A_HARD_PLAN = (
    "{Thing} \u2014 no wonder it is on your mind.",
    "{Thing}. The run-up is usually worse than the day itself.",
    "{Thing} \u2014 that is a lot to have coming.",
)


A_DAY_ON_A_HARD_PLAN = (
    "{Thing} \u2014 no wonder it is on your mind.",
    "{Thing}. The day itself is usually easier than the wait.",
)


# A birthday said as its number: "my grandads 80th is coming up" names no occasion word, and the
# date it gets ("its in november") was met with "Thanks for telling me".
A_MILESTONE = re.compile(r"\b(?:\d{1,3})(?:st|nd|rd|th)\b", re.I)


def _the_plan_a_date_belongs_to(text):
    """The word for the plan a bare date is the date of, and its kind, or ("", "") for none.

    Only the kinds of plan a date belongs to: an occasion, a birthday said as its number, an
    appointment in the diary, or a trip somewhere. The kind is what the phrase is built with - "a
    july wedding" is an occasion, "the dentist on tuesday" is an appointment.
    """
    said = " ".join(str(text or "").lower().split())
    if not said:
        return "", ""
    words = re.findall(r"[a-z']+", said)
    occasion = next((word for word in words if word in OCCASIONS), "")
    if occasion:
        return occasion, "occasion"
    if A_MILESTONE.search(said) and re.search(r"\b(?:my|our)\b", said):
        return "birthday", "occasion"
    diary = DIARY_THING.search(said)
    if diary:
        return diary.group(0).lower(), "diary"
    # A trip with the date left out: "we're going to spain" and then "its in july". The same
    # guards as `reads_as_a_trip`, which cannot see this one because it asks for the date.
    if (TRIP_VERB.search(said) and DESTINATION.search(said) and not OBLIGED.search(said)
            and not set(words) & PAST_PLAN):
        head = DESTINATION.search(said).group(1).lower()
        if head not in NOT_A_TRIP and head not in THING_BEFORE:
            return "holiday", "trip"
    return "", ""


def _a_date_on_the_thing_in_hand(clean, memory):
    """The plan's own date, said back as what the time means for it, or None.

    Only when the chat is already on a thing a date can belong to - an occasion or something in
    the diary - and the line is that date and nothing else. Anything else keeps its own reply.
    """
    said = " ".join(str(clean or "").lower().split())
    found = A_DATE_ALONE.match(said)
    if not found:
        return None
    record = topics.current(memory)
    text = " ".join(str((record or {}).get("text") or "").lower().split())
    if not text:
        return None
    when = " ".join(found.group("when").lower().split())
    if not when or when in re.findall(r"[a-z']+", text):
        # The date is already in the record's own words - "the wedding in july" then "its in
        # july" - so the line said nothing new and keeps the reply it has. The record's merged
        # words are not used for this: the store has already added this line's month to them, so
        # every date would read as a repeat.
        return None
    plan, kind = _the_plan_a_date_belongs_to(text)
    if not plan:
        return None
    thing = when[:1].upper() + when[1:]
    # Whether the plan is one to look forward to is the person's own, and the chat says it: "im
    # nervous about a job interview" then "its on friday" cannot be told the day is something to
    # look forward to.
    said_so_far = " ".join(
        [text] + [str(turn.get("user") or "").lower()
                  for turn in (memory.get("turns") or [])[-4:] if isinstance(turn, dict)])
    worried = bool(A_WORRIED_ABOUT_IT.search(said_so_far))
    a_day = A_MONTH_ALONE.match(when)
    if kind == "diary":
        # "the dentist on tuesday", "the scan in july": an appointment takes "the", and a weekday
        # takes "on". "a tuesday dentist" is not English.
        if A_WEEKDAY.match(when):
            made = "the " + plan + " on " + thing
        elif a_day:
            made = "the " + plan + " in " + thing
        else:
            made = "the " + plan + " " + thing
    elif a_day:
        # "a july wedding", "a saturday wedding".
        article = "an " if thing[0].lower() in "aeiou" else "a "
        made = article + thing + " " + plan
    elif A_WEEKDAY.match(when) or when in ("tomorrow", "tonight"):
        made = "the " + plan + " " + thing.lower()
    else:
        # "next week", "the 14th": the plan's own name and the time, in that order.
        made = "the " + plan + " " + thing.lower()
    made = made[:1].upper() + made[1:]
    if a_day:
        pool = A_DATE_ON_A_HARD_PLAN if worried else A_DATE_ON_A_PLAN
        return pick(pool, memory).format(Thing=made)
    pool = A_DAY_ON_A_HARD_PLAN if worried else A_DAY_ON_A_PLAN
    return pick(pool, memory).format(Thing=made)


def _after_the_hello(clean):
    """What the line says after the hello, or "" when the hello is all of it."""
    match = GREETING.match(clean)
    if not match:
        return ""
    return clean[match.end():].lstrip(" ,.!-:;")


# A one-line remark on what was just said is not a fact to file, and it is not a thing to say
# back: "we redid the kitchen last year" then "it cost a fortune" was answered "Got it - it cost
# a fortune", the person's own words handed back with nothing added. With the store's echo
# silenced it fell further, to the stock nod ("Got it. Is there anything you'd like a hand
# with?"), which fits any message at all. A friend answers the remark - the money, the time, the
# better, the loss - and asks the one thing that follows from it, so the reading is the kind of
# remark and the reply is filled from nothing but the kind: no tail here can be pasted onto a
# line that is not a remark.
REMARK_BACK = re.compile(
    r"^(?:it|its|it's|that|thats|that's|they|them|he|she|the|this|those|these|everything|nothing"
    r"|none|all)\b", re.I)


REMARK_EXPENSE = re.compile(
    r"\b(?:cost|costs|costing|expensive|pricey|a fortune|a bomb|not cheap|money pit|"
    r"over budget|over the budget|cost a lot|costs a lot|adds? up)\b", re.I)


# A price already paid and a price still to pay are two different remarks. "we redid the kitchen
# last year" / "it cost a fortune" is somebody looking back at money spent, so asking whether it
# was worth it is the question a friend asks. "we are going to portugal in august" / "the flights
# are expensive" is the same words about a trip nobody has booked, where the same question ("Do
# you think it was worth it?") asks about a thing that has not happened yet and has no answer.
# What tells them apart is the plan on the table, not the remark: what was done is said in the
# past ("redid", "last year"), and what is still to be done is said as a plan ("going to",
# "in august", "next month"). Read from the topic line as well as the remark, because the
# remark itself is only the price ("it cost a fortune" says nothing about when).
REMARK_STILL_TO_COME = re.compile(
    r"\b(?:going\s+to|gonna|planning|plan\s+to|planning\s+to|thinking\s+of|want\s+to\s+"
    r"(?:go|buy|get|book|move|build|do)|hoping\s+to|about\s+to|next\s+"
    r"(?:week|month|year|summer|spring|autumn|winter|june|july|august|september|october|"
    r"november|december|january|february|march|april|may|weekend|christmas)|"
    r"in\s+(?:january|february|march|april|may|june|july|august|september|october|november|"
    r"december|the\s+summer|the\s+spring|the\s+autumn|the\s+winter)|"
    r"before\s+i\s|when\s+i\s+go|once\s+i)\b", re.I)


# The words that say a price is behind the person: a past verb of its own, or the thing already
# in their hands. "was expensive", "cost me a fortune", "we have already paid", "it got done".
REMARK_ALREADY_PAID = re.compile(
    r"\b(?:was|were|cost|costs|costing|cost\s+me|has\s+been|had\s+been|paid|spent|bought|"
    r"redid|redecorated|renovated|built|installed|fitted|took|got|had|already|last\s+"
    r"(?:year|month|week|summer|winter|spring|autumn)|ago|in\s+the\s+end|all\s+in)\b",
    re.I)


REMARK_LONG = re.compile(
    r"\b(?:took|takes|taking|take)\s+(?:forever|ages|hours|all day|all week|all weekend|weeks|"
    r"months|for ever|forever and a day)\b|\bso long\b|\blonger than\b|\bdragged on\b", re.I)


REMARK_BETTER = re.compile(
    r"\b(?:better|easier|nicer|cheaper|faster|less stressful|more money|pays better|pays more|"
    r"worth it)\b", re.I)


REMARK_HARD = re.compile(
    r"\b(?:hard|harder|difficult|tough|stressful|exhausting|draining|knackering|hectic|"
    r"a nightmare|a slog|a struggle)\b", re.I)


REMARK_WORK = re.compile(
    r"\bneeds?\s+(?:a lot of|some|lots of|loads of)\s+work\b|\bneeds? work\b|"
    r"\bneeds? doing\b|\bmore than i thought\b|\bbigger than i thought\b", re.I)


REMARK_GONE = re.compile(
    r"\b(?:got them|got it|ate them|ate it|ruined|ruined it|killed them|all gone|"
    r"eaten them|stole it|stole them|knocked them|gone to the slugs)\b", re.I)


# A loss is only read as a loss when the thing being lost is a plant or a crop: "the slugs got
# them" after tomatoes is a bed wiped out, and the same words about anything else are not a
# growing question at all.
GROWING = re.compile(
    r"\b(?:tomato|tomatoes|potato|potatoes|plant|plants|planted|seed|seeds|seedling|seedlings|"
    r"lettuce|beans|peas|carrot|carrots|onion|onions|squash|courgette|courgettes|pumpkin|"
    r"strawberr\w+|raspberr\w+|blackberr\w+|herb|herbs|flower|flowers|bulbs?|garden|allotment|"
    r"veg|vegetables?|crop|crops|greenhouse|bed|beds)\b", re.I)


# The endings. One is dropped when the last reply asked a question, because two questions in a row
# is an interrogation, so each kind keeps an ending that only says something back.
REMARK_REPLIES = {
    "expense": (
        "Not cheap, that.",
        "They never are.",
        "The bits nobody quotes for are always the ones that cost.",
        "Ouch. Do you think it was worth it?",
    ),
    # A price still to pay is a bill to move rather than money gone, so none of the endings above
    # fits it: "the bits nobody quotes for" is about a job already done, and "was it worth it" asks
    # about a trip nobody has booked. The one thing a friend asks first is what the figure is.
    "long": (
        "It always takes longer than the plan says it will.",
        "Longer than anyone warns you, every time.",
        "That is the way of it, and at least it is done.",
    ),
    "better": (
        "Good - that is the bit that matters.",
        "That is the bit that makes the difference.",
        "That sounds like the right move.",
    ),
    "hard": (
        "That is the thing nobody warns you about.",
        "It does take it out of you.",
        "It is - and it gets easier once the new bit is routine.",
        "Fair enough. What has been the hardest bit?",
    ),
    "work": (
        "Bigger job than it looked, then.",
        "That is how these go: the first quote is never the whole of it.",
        "Worth getting a second price before you say yes to it.",
    ),
    "gone": (
        "Ah, that is a shame.",
        "That is gutting.",
        "Netting is the only thing that stops it happening again.",
        "Will you put another lot in?",
    ),
}


REMARK_PRICE_AHEAD = (
    "Not cheap, that.",
    "They never are.",
    "What are they quoting for it? That is usually the bit worth moving.",
    "Worth pricing it a couple of ways round before you commit.",
)


# A remark with a "but" in it is two-sided - "its more money but its a longer day" is a person
# still weighing something up, and agreeing with half of it ("That sounds like the right move")
# answers a decision they have not made. Those keep the ordinary path.
REMARK_TWO_SIDED = re.compile(r"\b(?:but|though|although|however|except|apart from|other than"
                              r"|worse|less|harder|longer|slower)\b", re.I)


# A figure is a fact about the thing, not a complaint about its price. "is it worth getting a
# bike" ... "it costs 400" is the person telling the bot what the bike in front of them costs, and
# the answer to that is whether the figure is fair - but the expense remark read "costs" alone and
# replied "They never are.", agreeing with a complaint nobody made. So the expense kind needs a
# word of judgement in the line ("expensive", "a fortune", "not cheap", "a lot", "over budget"),
# and a line that carries only a figure is left to the ordinary path, which answers the figure.
REMARK_JUDGES_THE_PRICE = re.compile(
    r"\b(?:expensiv\w*|pricey|pricier|dear|dearer|a\s+fortune|a\s+bomb|a\s+packet|not\s+cheap|"
    r"cheap\s+enough|money\s+pit|over\s+(?:the\s+)?budget|cost(?:s|ing)?\s+(?:me\s+)?a\s+lot|"
    r"cost\s+me|too\s+much|so\s+much|that\s+much|a\s+lot\s+of\s+money|loads|rip[-\s]*off|"
    r"overpriced|adds?\s+up|worth\s+it|not\s+worth|daylight\s+robbery|steep)\b", re.I)


# The other half of an expense remark: the number and nothing said about it. "it costs 400" is the
# person answering "is it worth it" with the figure they are looking at, so the reply has to be
# about that number - what it would take to get it back - and not the endings above, which agree
# with a complaint nobody made ("They never are."), and not an echo ("Got it - it costs 400.").
REMARK_FIGURE = re.compile(
    r"(?:£|\$|€)\s*\d|\b\d{2,}\b|\b\d+\s*(?:quid|pounds?|euros?|dollars?|grand|k)\b", re.I)


REMARK_FIGURE_REPLIES = (
    "Then it comes down to what you get for it, and a second price usually moves the figure.",
    "That is the number to weigh up against what doing nothing would cost you.",
    "Worth checking that against one more quote before you commit to it.",
)


REMARK_KINDS = ((REMARK_EXPENSE, "expense"), (REMARK_LONG, "long"), (REMARK_BETTER, "better"),
                (REMARK_HARD, "hard"), (REMARK_WORK, "work"), (REMARK_GONE, "gone"))


def _a_hand_back(reply, memory):
    """Note a reply that answered a remark, so the turn after it can tell it from a new subject.

    The echo it replaces ("Got it - it takes forever.") was skipped by
    `bot/memory/topics.py::said_again` as an acknowledgement that says nothing of its own, which
    is how a follow-up two turns later still reached the answer above it. A remark is the same
    thing said properly - the subject stays where it was - so it keeps that behaviour without
    having to look like an acknowledgement. Only the reply's own words are kept, so a turn that
    gave something else is never mistaken for one.
    """
    if not isinstance(memory, dict):
        return
    said = " ".join(re.findall(r"[a-z0-9']+", str(reply or "").lower().replace("\u2019", "'")))
    if not said:
        return
    kept = memory.get("hand_backs")
    if not isinstance(kept, list):
        kept = []
        memory["hand_backs"] = kept
    kept.append(said)
    del kept[:-4]
