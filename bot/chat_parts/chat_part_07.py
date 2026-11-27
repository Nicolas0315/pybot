"""Part 7 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import badnews, negated
from ..compose.goodnews import asks_for_news
from ..compose import loss as loss_reading


from .chat_part_02 import (
    GOOD_NEWS, NEWS_REPLIES,
)
from .chat_part_03 import (
    COPULA, FUNCTION_WORDS, INTENSIFIERS, INTENSIFIER_PAIRS, OWN_STATES, STATE_NOUNS, DETERMINERS,
    FEELINGS, NOT_WORDS,
)
from .chat_part_04 import (
    REPLIES,
)
from .chat_part_05 import (
    A_LABEL_ON_THE_PERSON,
)


def _the_weight_said(memory, feeling):
    """Note the pool this reply came from, and that a heavy line was answered, for the turn after.

    Written where the reply is chosen, so it lands in this module's copy of the memory: the
    arbiter keeps the copy of the module whose reply the person got, and a note made by a module
    that lost is thrown away with its copy. That is what makes the note trustworthy - it is only
    there when the heavy reply is the one that was said.
    """
    if not isinstance(memory, dict):
        return
    turns = memory.get("turns")
    index = len(turns) if isinstance(turns, list) else 0
    # Which pool the last answer came from: the turn after it reads this to know what was asked
    # of the person, so a hedge can tell "how are you" / "cant complain" apart from
    # "i lost my job" / "cant complain".
    memory["said_kind"] = {"kind": feeling, "turn": index}
    if feeling not in HEAVY_FEELINGS:
        return
    memory["heavy_reply"] = {"feeling": feeling, "turn": index}


# A person is not a thing that owns a feeling word. "he seems fine now but should i worry" is
# about the speaker's worry, however the clause before the word is shaped.
PERSON_WORDS = frozenset("""i we you he she they me us them him her who whoever someone somebody
anybody nobody everyone everybody people""".split())


# Words that stand for the person rather than for a thing of theirs ("im shattered", "ive been
# low"), so nothing in front of a feeling word when one of these is there can own it.
CONTRACTIONS = frozenset("""im ive id ill youre youve theyre thats its weve were dont didnt doesnt
wont cant isnt arent wasnt havent hasnt""".split())


# A word that names the effect a thing has on the person still says how the person is: "the film
# was really boring" is their boredom, and so is "work was boring today". A word a thing can carry
# on its own ("my phone battery is low again") is not one of these.
CAUSES_THE_FEELING = frozenset("""boring tiring exhausting annoying worrying frightening
scary draining relaxing depressing frustrating embarrassing confusing mad stressful overwhelming
knackering""".split())


# A verb of habit in front of a feeling word does not own it: "i keep crying", "she keeps
# getting upset", "we keep feeling low" are how the person is, not a thing the line named.
# Without this, "keep" was read as the subject and the feeling was never found, so the line fell
# to the routine reply for a thing that keeps happening ("Annoying. Is it the same every time?").
HABIT_VERBS = frozenset(("keep", "keeps", "kept"))


# The words that say a weight came off. The understanding engine reads "relieved" as a happy
# emotion (`kinds.POSITIVE`), and the cue reader that asks whether a feeling word is about the
# person does not count one with a clause after it ("a sad film"), so "im relieved hes gone" was
# left with the emotion and no word of its own and reached the celebration pool. Relief is read
# off its own words, whatever the clause after them says.
RELIEF_SAID = re.compile(
    r"\b(?:relieved|relief)\b|\b(?:what|such)\s+a\s+relief\b"
    r"|\bweight\s+off\s+(?:my|her|his|their|your)\s+(?:shoulders|mind)\b", re.I)


def _says_relief(clean):
    """True when the line says a weight came off, whether or not it calls the feeling a mood."""
    return bool(RELIEF_SAID.search(clean)) and not negated(clean, "relieved")


# A feeling said in a second clause is the person's, whatever the first clause named: "im
# relieved but i also feel sad" put "relieved" in front of the sad word, and the reader that asks
# what owns the word was reading the whole line rather than the clause it stands in, so the sad
# half was filed as a thing's and the line was answered as the relief. A conjunction or a comma
# starts a new clause, and the clause decides whose the feeling is.
CLAUSE_JOIN = frozenset(("but", "and", "so", "though", "tho", "because", "cos", "cause",
                         "although", "yet", "plus", "then", "also", "still", "even",
                         "except", "whereas", "while", "which"))


# A join word is only a boundary when a new subject stands between it and the feeling:
# "im relieved but i also feel sad" splits at "but" because "i" follows, and "my battery is so
# low" does not split at "so" because nothing but the intensifier sits after it, so the battery
# keeps the word. "then", "also", "still" and "even" are only ever adverbs here for the same
# reason they are in CLAUSE_JOIN at all: they can start a clause, but a clause needs a subject.
CLAUSE_SUBJECT = frozenset(("i", "im", "i'm", "ive", "i've", "we", "we're", "were", "weve",
                            "he", "hes", "she", "shes", "they", "theyre", "you", "youre",
                            "it", "its", "there", "theres",
                            "my", "our", "your", "his", "her", "their", "the", "a", "an",
                            "this", "that", "these", "those"))


def _starts_a_clause(after):
    """Whether the words after a join word up to the feeling name a subject of their own."""
    return any(word.strip(".,!?;:").lower() in CLAUSE_SUBJECT for word in after)


def _in_its_clause(before):
    """The words in front of a feeling word, back to the start of the clause it stands in."""
    for index in range(len(before) - 1, -1, -1):
        word = before[index]
        if word.endswith((",", ";", ":", ".", "!", "?",)):
            return before[index + 1:]
        if word.strip(".,!?;:").lower() in CLAUSE_JOIN and _starts_a_clause(before[index + 1:]):
            return before[index + 1:]
    return before


def _owned_by_a_thing(clean, match):
    """Whether the thing the line names before the word is what the word is about.

    "my phone battery is low again": the noun the copula is about is the battery, which is not
    a way for a person to be, so the word describes it. "my mood is low" and "ive been low all
    week" leave the noun empty or the person's own, so they are not owned by a thing.
    """
    if clean[match.start():match.end()].lower() in CAUSES_THE_FEELING:
        # ...unless the person is the word's own subject: "im boring" is a label on them and not
        # a mood of theirs (see A_LABEL_ON_THE_PERSON).
        return bool(A_LABEL_ON_THE_PERSON.search(clean))  # the thing is what made the feeling
    before = _in_its_clause(clean[:match.start()].split())
    owner = _owner(before)
    if owner in PERSON_WORDS:
        return False  # "he seems fine but should i worry" is about the speaker's worry
    if owner is not None:
        return owner not in OWN_STATES
    if not before:
        return False
    word = before[-1].strip(".,!?;:").lower()
    bare = word.replace("'", "").replace("\u2019", "")
    if (word in FUNCTION_WORDS or word in INTENSIFIERS or bare in CONTRACTIONS
            or word in HABIT_VERBS
            or COPULA.match(word) or (len(word) > 4 and word.endswith(("ing", "ly")))
            or " ".join(part.strip(".,!?;:") for part in before[-2:]).lower()
            in INTENSIFIER_PAIRS):
        return False  # a pronoun, a copula, a filler or an intensifier: nothing owns the word
    return word not in OWN_STATES  # "the heat down", "the oven low": the thing before it does


# The line says the state is the speaker's own with their own word for it: "my mood", "our
# stress". A thing of theirs ("my battery", "my wife") is not a state of theirs.
OWN_BEEN = re.compile(r"\b(?:i'?ve|ive|we'?ve|weve)\s+(?:been|had)\b")


def _own_state(clean):
    """Whether the line names a state the speaker is in, not a thing that belongs to them."""
    if OWN_BEEN.search(clean):
        return True  # "ive been low all week"
    words = [word.strip(".,!?;:").lower() for word in clean.split()]
    for index, word in enumerate(words):
        if word in ("my", "our") and any(near in STATE_NOUNS for near in words[index + 1:index + 3]):
            return True  # "my mood", "my low mood", "our stress levels"
    return False


def _carries_on(word):
    """Whether the word after a feeling word leaves it about the person: "nervous speaking"."""
    word = word.strip(".,!?;:").lower()
    if word in FUNCTION_WORDS:
        return True
    return len(word) > 4 and word.endswith("ing")  # a gerund says what they are doing


def _owner(before):
    """The thing a verb in `before` is about, when there is one: "my mood is" -> "mood"."""
    for index in range(len(before) - 1, -1, -1):
        if not COPULA.match(before[index].strip(".,!?;:")):
            continue
        # A filler is never the noun a copula is about: "i also feel sad" and "im still so low"
        # put an adverb between the subject and the verb, and reading "also" as the subject made
        # a feeling of the speaker's look like a thing's.
        subject = [word.strip(".,!?;:") for word in before[:index]
                   if word.strip(".,!?;:").lower() not in DETERMINERS
                   and word.strip(".,!?;:").lower() not in FUNCTION_WORDS
                   and word.strip(".,!?;:").lower() not in INTENSIFIERS]
        if not subject:
            return None
        # A state of a person is the state, however the phrase is built: "our stress levels"
        # and "my moods" are still the person's, and the last word before the copula is not
        # always the one that says so.
        for word in reversed(subject):
            if word.lower() in STATE_NOUNS:
                return word.lower()
        return subject[-1].lower()


# A thing of their own that wears them down, said with a copula and no "i": "my job is
# exhausting", "the commute is draining", "work is stressful at the moment". These words name the
# effect a thing has on the person, so the line is how they are, not a fact about the job -
# "my job is exhausting" came back as "Noted: your job is exhausting.". The thing in front has to
# be part of their life and not just any object, or "my dishwasher isnt draining" and "the pool is
# draining" would be read as a hard day.
HARD_ON_THE_PERSON = frozenset((
    "exhausting", "draining", "tiring", "knackering", "stressful", "overwhelming", "wearing out",
))


LIFE_THING_HARD = re.compile(
    r"\b(?:my |our |the |this |these )?(?:work|job|jobs|week|weeks|month|months|year|term|shift|"
    r"shifts|commute|project|deadlines?|course|coursework|placement|revision|school|uni|office|"
    r"team|rota|days?|nights?|mornings?|house|flat|move|money|kids|children|family|life)\b"
    r"[^.!?]{0,20}?\b(?:is|are|was|were|been|has been|have been|'s been)\s+"
    r"(?:(?:so|really|very|pretty|just|quite|absolutely|always|still|bloody|too)\s+){0,2}$",
    re.I)


def _hard_about_their_thing(clean):
    """True when a word of strain is said of a thing of theirs, not of an object."""
    for word in HARD_ON_THE_PERSON:
        at = clean.find(word)
        if at > 0 and LIFE_THING_HARD.search(clean[:at]):
            return True
    return False


# A person in front of a word of strain is the subject of it: "she is so draining", "my sister is
# exhausting", "they are tiring". The word never says how that person feels, so the reading of the
# person typing their own tiredness must not take it, and neither may the one about somebody else.
_OTHER_SUBJECT = re.compile(r"\b(?:he|she|they|him|her|them)\b", re.I)


WEARS_OTHER_PEOPLE_OUT = frozenset(("exhausting", "draining", "tiring", "knackering"))


# The words the guilt reading owns, so a denial can be read on them before the deed: "im not
# feeling guilty about cancelling" is a line about it not sitting heavy, not a confession.
GUILT_WORDS = ("guilty", "bad", "awful", "terrible", "rotten", "horrible", "ashamed", "sick")


# A period said after the feeling is when they felt it, not a second subject: "im still low this
# week" was read as a plan and nothing else, so the feeling was never found and the turn fell to
# the stock ack. Only the phrases whose whole meaning is "at the moment" are taken off, and not
# "lately" or "these days", which are the knowledge entries' cue for a tiredness that persists.
STATE_WHEN = re.compile(
    r"\s+(?:this|that|the current)\s+(?:week|month|year|morning|afternoon|evening|weekend)\b.*$"
    r"|\s+at the moment\b.*$|\s+right now\b.*$", re.I)


# "i want to cry" names no feeling word and has no "i feel" in it, so every rule below walked
# past it and the bot said "Noted: you want to cry.". Wanting to weep is not a plan: it is the
# saddest line a person writes. It is read here, before the rest of _feeling, so it needs its
# own guards - see WEEPING_WITH_JOY and the three below.
WANT_TO_WEEP = re.compile(r"\b(?:want|wanna|need|needs|would like|just want|really want)\s+to\s+"
                          r"(?:cry|weep|sob|bawl)\b|\b(?:feel like|feels like)\s+"
                          r"(?:crying|weeping|sobbing)\b|\bon the verge of (?:tears|crying)\b"
                          # The same line with a modal: "i could cry", "i might cry", "i could
                          # just sob". "Could" is how a person half-says it, and the modal was
                          # read as a plan - "honestly could cry" got a search hedge and
                          # "i might cry" got "Nice. Tell me how it goes."
                          r"|\b(?:could|might|may|would)\s+(?:just\s+|really\s+|honestly\s+|"
                          r"actually\s+|easily\s+)?(?:cry|weep|sob|bawl)\b"
                          # And the tears that are about to arrive.
                          r"|\babout to\s+(?:just\s+)?(?:cry|weep|sob|bawl)\b")


# Tears on a good day are not a reason to be sorry: "we won the cup and i want to cry" got the
# condolence line, and "i want to cry happy tears" lost the entry that explains crying.
WEEPING_WITH_JOY = re.compile(r"\b(?:with relief|of relief|happy tears|tears of joy|so relieved|"
                              r"laughing\b|\blaugh\b|could cry with|laugh(?:ed|s)? (?:so|until)|"
                              r"happ(?:y|ier)|relieved|proud|thrilled|excited|made it)\b", re.I)


# "why do i want to cry" is the answers lane's question: it wants the explanation the entry
# carries ("crying is a pressure valve"), and a condolence answers a different line.
WHY_THE_TEARS = re.compile(r"\b(?:why|how come|any idea why)\b", re.I)


# The weeping has to be theirs: "the film made me want to cry" is about the film, and "my dad is
# making me want to cry" is about him. Both got the condolence for the wrong person.
# The modal says whose tears they are: "he could cry" is not the speaker's, and a condolence is
# the wrong thing to give somebody about their brother.
SOMEBODY_ELSE = re.compile(
    r"\b(?:he|she|they|it|you|him|her|them|my \w+|his|her|their|your)\s+(?:\w+\s+)?"
    r"(?:could|might|may|would|is about to|was about to|were about to)\s+(?:just\s+|really\s+|"
    r"honestly\s+|actually\s+|easily\s+)?(?:cry|weep|sob|bawl)\b", re.I)


NOT_THEIR_TEARS = re.compile(r"\b(?:the|a|this|that) (?:film|book|show|programme|program|"
                             r"documentary|song|episode|video|story|news|game|series)\b"
                             r"|\b(?:it|that|this) (?:made|makes|had) me\b"
                             r"|\b(?:he|she|they|my \w+|his|her|their) (?:made|makes|make|"
                             r"is making|are making|had me|has me|keeps making) me\b", re.I)


# "i dont want to cry" and "im trying not to cry" are a fight against it, not a grief, and the
# condolence line reads as if they had said the opposite.
NOT_WANTING_IT = re.compile(r"\b(?:not|dont|doesnt|didnt|never|no)\b[^.?!]{0,24}\b(?:want|wanna|"
                            r"need)\s+to\s+(?:cry|weep|sob|bawl)\b"
                            r"|\btrying not to (?:cry|weep|sob|bawl)\b|\bholding back the tears\b",
                            re.I)


# Tears at a thing built to move you are being moved, not a low: "i keep welling up at
# adverts", "i keep tearing up at films", "i keep crying at weddings". The keeps shape reads
# a tears word as a mood that comes back, which is right for "i keep welling up" and wrong for
# a person who cries at the telly. A low the person names of their own ("i feel low and i keep
# crying at films") keeps the answer for the low.
MOVED_BY = re.compile(
    r"\b(?:at|during|watching|reading|listening to|over)\s+(?:a\s+|an\s+|the\s+|my\s+|some\s+)?"
    r"(?:film|films|movie|movies|advert|adverts|ad|ads|telly|tv|song|songs|"
    r"video|videos|programme|programmes|documentary|documentaries|book|books|show|shows|"
    r"series|episode|episodes|story|stories|photo|photos|picture|pictures)\b", re.I)


# The same, when the part of the thing comes between the little word and the thing: "i choked up
# at the end of the film", "i cried at the end of the book". NOT_THEIR_TEARS reads the bare "the
# film" and threw the person's own tears away, so the line matched nothing and the small-day pool
# answered it: "Good to hear. What was the best bit?". This shape only counts with a tears word in
# the line, so "we had popcorn at the end of the film" and "i left early at the end of the film"
# keep the reply they had.
MOVED_BY_PART = re.compile(
    r"\b(?:at|during|watching|reading|listening to|over)\s+(?:a\s+|an\s+|the\s+|my\s+|some\s+)?"
    r"(?:[a-z']+\s+){1,3}of\s+(?:a\s+|an\s+|the\s+|my\s+)?"
    r"(?:film|films|movie|movies|advert|adverts|ad|ads|telly|tv|song|songs|"
    r"video|videos|programme|programmes|documentary|documentaries|book|books|show|shows|"
    r"series|episode|episodes|story|stories|photo|photos|picture|pictures)\b", re.I)


# The person's own tears said as a verb, with no "im" and no "i want to" for the matchers above
# to hold on to: "i cry every morning", "i cry a lot", "i weep at night". The mood word was found
# and then thrown away, because the cue that makes it theirs was missing from the line, and the
# stock "I'm listening - say more if it helps" answered somebody who had just said they cry most
# days. The subject has to be the person writing, so "my daughter cried at the film" is left alone.
MY_TEARS = re.compile(
    r"\b(?:i|i've|ive|we|we've|weve)\b(?:\s+\w+){0,2}?\s+"
    r"(?:cry|crying|cried|cries|weep|weeping|wept|sob|sobbing|bawl|bawling|blub|blubbing|"
    r"welling up|welled up|welling|tearing up|teared up|choked up)\b"
    # "i dont want to cry" and "im trying not to cry" are a fight against it, and NOT_WANTING_IT
    # below has its own answer for those.
    r"(?!\s+(?:about|because|over)\s+(?:my|his|her|their)\s+\w+)", re.I)


# "I can't stop crying" is the composer's habit reading: it answers a repeated doing with "that
# sounds like a pattern rather than a one-off", which is the right question for it. The tears pool
# asks what brought it on, so the frozen tears keep the habit reply they already had.
CANT_STOP_IT = re.compile(r"\b(?:can'?t|cant|cannot|couldn'?t|couldnt)\s+stop\b", re.I)


# The person the tears belong to, when it is not the speaker: "i watched him cry", "we let her
# cry it out". The words of the match are looked at, not the whole line, so "my mum died and i
# cry every day" is still the speaker's crying.
SOMEONE_IN_THEIR_OWN_TEARS = re.compile(
    r"\b(?:him|her|them|me|us|you|my|his|their|your)\b", re.I)


# The words that name a low of their own, apart from the tears themselves: "i feel awful and i
# dont want to cry" is still an awful day, and the denial only takes the grief away.
_WEEP_WORDS = frozenset(("crying", "cry", "cried", "cries", "weepy", "tearful", "tears",
                         "in tears", "sob", "sobbing", "weep", "weeping", "wept", "bawl",
                         "bawling", "blub", "blubbing", "welling up", "burst into tears",
                         "bursting into tears", "tearing up", "tear up", "choked up"))


def _a_low_word(clean):
    """True when the line names a low feeling of its own, other than the crying it denies."""
    for _name, words in FEELINGS:
        for word in words:
            if word in _WEEP_WORDS:
                continue
            if re.search(r"\b" + re.escape(word) + r"\b", clean):
                return True
    return False


def _good_news(clean):
    """True when the line is small good news, which is what the module answers first."""
    flat = clean.replace("'", "")
    if asks_for_news(flat):
        return False
    return any(pattern.search(flat) for pattern in GOOD_NEWS)


# "i keep crying" is the same statement as "im always crying": the person is telling you how
# they are, not asking for a routine to be fixed. The reading only accepts "keep" as a cue that
# the feeling is theirs, exactly like "im" or "ive been", so the mood pools answer it instead of
# the routine reply ("Annoying. Is it the same every time?"). A line the knowledge base answers
# ("i keep crying at work", "... and i dont know why") keeps its entry - see `_respond`.
KEEPS_HOW_THEY_ARE = re.compile(r"\b(?:i|we)\s+(?:keep|keeps|kept)\b")


# The habit that says a mood comes back is the speaker's own: "i keep weeping" is a low that
# returns, and "we keep getting upset with each other" is the two of them, which the GP line
# answers with advice for the wrong thing. GOING_ON's own habit arm still reads "we keep
# feeling low", so a couple who both feel low keeps the answer it had.
KEEPS_HOW_I_AM = re.compile(r"\bi\s+(?:keep|keeps|kept)\b")


# A named low is its own line: "i feel really low and i want to cry" already has the sad pool's
# answer, and "i feel sad and i want to cry" is the same line with another word. The tears pool
# takes the lines where the tears are the whole of what was said - someone who wants to cry and
# has not said why - so a mood the person named stands it down (test_chat.
# WantingToCryIsAFeelingTest keeps the named low on its own reply).
#
# The low has to be the speaker's. "its been rough and i want to cry" and "i want to cry, work
# has been awful" name how the week went, not a mood the person is in, and standing the pool down
# on those dropped them into the "i want to X" capture - "Cry - fair enough. What's stopped it
# happening so far?" - so only "ive been low" counts, with the speaker as the subject.
A_NAMED_LOW = re.compile(
    r"\b(?:feel|feeling|felt|i'?m|im|i am|i'?ve|ive|i have)\b[^.]{0,18}?\b(?:low|sad|down|depressed|"
    r"miserable|heartbroken|devastated|hopeless|empty|numb|lonely|anxious|overwhelmed|"
    r"awful|terrible|dreadful|rubbish|crap|rough)\b")


def _weeping(clean):
    """True when the line says they want to cry, and nothing about it points somewhere else."""
    if not WANT_TO_WEEP.search(clean):
        return False
    if NOT_WANTING_IT.search(clean) or NOT_THEIR_TEARS.search(clean) or SOMEBODY_ELSE.search(clean):
        return False
    if WEEPING_WITH_JOY.search(clean) or WHY_THE_TEARS.search(clean):
        return False
    if A_NAMED_LOW.search(clean):
        return False
    return not _good_news(clean)


# The ways people say they are not doing well without naming a mood: the denial of coping, and
# the plain words for feeling bad. "im not coping" and "im struggling" got the neutral shrug
# ("Got it. Is there anything you'd like a hand with?"), which answers nothing a person said.
#
# Each shape carries its own guard, because these words are ordinary outside a mood: "im
# struggling to open the jar" is a jar, "im not managing the team any more" is a job, and "im
# rubbish at maths" is a skill (SKILL already takes "im not great at maths" out of the line).
# "not really" is not the line on its own: "im not really hungry" and "i am not really into
# running" are not a person who is not coping, and they were read as one. The intensifier only
# counts in front of the word that says how the person is: "not really coping", "not really
# managing at work", and "not really ok|okay|alright|fine|good", which is the mood said the
# softened way ("im not really ok" is not a person declining an offer).
NOT_COPING = re.compile(
    r"\b(?:not|never|isn'?t|isnt|ain'?t|aint)\s+(?:"
    r"(?:really|actually)\s+(?:ok|okay|alright|fine|good|well|myself|here|sleeping|eating)\b"
    # The mood word has to be the whole of what they said about themselves: "im not really good
    # at cooking" is a skill, and it is not this line.
    r"(?=\s*(?:$|[.,!?;]|\b(?:today|tonight|now|lately|right now|at the moment|these days|"
    r"recently|this week|this morning|tbh|honestly|really)\b))|"
    r"(?:(?:really|actually)\s+)?(?:coping\b|"
    r"managing\b(?=\s*(?:$|[.,!?]|any ?more|at all|at the moment|lately|right now|"
    r"at (?:work|home)|(?:my |the )?(?:work|job|kids|house|home|money)\b|"
    r"with (?:everything|it all|life|any of it|the kids|work|the money)))))")


# The speaker, then the shape: "im struggling", "i feel hopeless", "im falling apart". A bare
# adjective after "im" is not here: main reads `im crap` and `im a mess` with SELF_INSULT and the
# sad row (test_chat.ChatNamesTheFeelingTest, ChatSmallNewsTest), and two answers to one line is
# a routing fault, not a better answer.
NOT_COPING_SHAPES = re.compile(
    # The shapes the pool has always read, behind the speaker, as they were.
    r"\b(?:i'?m|im|i am|i feel|i felt|feel|feeling|i'?ve been|ive been|i have been)\b"
    r"[^.]{0,24}?\b(?:struggling\b(?!\s+to\b)|hopeless\b|numb\b|empty\b|"
    r"falling apart\b|at the end of my tether\b|can'?t keep going\b)"
    "|"
    # The same disclosure in the other words people use for it. "falling apart" was the only
    # one of these the pool knew, so a person who said "im having a breakdown" got "Got it -
    # you're having a breakdown", "im a wreck" got "You're a wreck, good to know" and
    # "im losing it" a thank-you with nothing in it.
    #
    # These words are said of other things far more often than of the speaker, so each arm
    # is fenced twice. The gap between the speaker and the shape may only hold the words
    # that hedge it ("im having a bit of a meltdown", "i feel like a total wreck"): that is
    # what keeps "im worried my boiler is having a breakdown" a line about the boiler. And
    # the shape has to be the whole of what was said about themselves, allowing a clause
    # that carries on or a time in front of it: that is what keeps "im cracking up at this
    # sitcom" (laughing), "im a wreck after that gym session" and "im going under the knife
    # next week" out of the pool.
    # "i had a meltdown at work", "ive just had a breakdown": the same disclosure in the past
    # tense, said about a day that has already happened. Without it the line was read as news
    # about a thing and answered "Got it. Is there anything you'd like a hand with?".
    r"\b(?:i'?m|im|i am|i feel|i felt|feel|feeling|i'?ve been|ive been|i have been|"
    r"i had|i'?ve had|ive had|i have had|i just had|i'?ve just had|ive just had)\b"
    r"(?:\s+(?:honestly|really|properly|totally|absolutely|just|so|very|quite|kind|sort|of|a|"
    r"an|the|bit|like|having|total|nervous|im|am|been|pretty|mostly|still)\b){0,6}?\s*"
    r"(?:cracking up\b|losing it\b|spiralling\b|going under\b|breaking down\b|"
    r"at breaking point\b|wreck\b|(?:having\s+|a\s+)?(?:(?:total|nervous)\s+)?"
    r"(?:meltdown|breakdown)\b)"
    r"(?=\s*(?:$|[.,!?;]|\b(?:and|but|so|because|though|cause|about|with|over)\b|"
    r"(?:at the moment|at the minute|right now|today|tonight|this (?:week|morning|month|year)|"
    r"lately|recently|these days|tbh|honestly|to be honest|"
    r"at (?:work|school|home|uni|night))\b))")


# How a bad day is said with an adjective: only behind "feel". "i feel rubbish today" is the
# plainest way of saying it, and "i feel terrible" is not "the service was terrible".
NOT_COPING_FEEL = re.compile(
    r"\b(?:i\s+feel|i\s+felt|feel|feeling)\b[^.]{0,16}?\b(?:like\s+)?"
    r"(?:rubbish|crap|terrible|awful|dreadful)\b"
    # The adjective has to be the whole of what the person said about themselves: "i feel
    # rubbish today" is a bad day, "i feel like a rubbish mum" is a verdict on themselves,
    # which is the self-blame pool's line (fallback's SELF_BLAME), not this one.
    r"(?![^.]{0,12}\b(?:at|with|in)\s+\w)"
    r"(?=\s*(?:$|[.,!?;]|\b(?:today|tonight|now|lately|right now|at the moment|these days|"
    r"recently|this week|this morning)\b))")


# The rest of the shapes do not need the speaker in front of them: the thing said is already
# only ever said about a person's state.
NOT_COPING_ANYWHERE = re.compile(
    r"\b(?:don'?t|dont|doesn'?t|doesnt|not)\s+feel\s+(?:like\s+)?(?:my|him|her|them)?self\b|"
    r"\b(?:everything|it all|it|life)\s+(?:is\s+)?(?:getting|get|gets)\s+on top of me\b|"
    r"\b(?:getting|get|gets)\s+on top of me\b|"
    # "ive had enough" is said about a job, the weather and a queue as often as about a life,
    # so only the object that makes it a statement about being here is read. Without it
    # "ive had enough of living" got the irritation pool - "Annoying. Walk it off for ten
    # minutes before you reply to anyone." - which is the worst answer in the bot for it.
    r"\b(?:i|we)\s*(?:(?:have|'?ve|'?d)\s+)?had\s+enough of\s+"
    r"(?:living|life|it all|everything|being here|all this)\b|"
    r"\b(?:i|we)\s+(?:don'?t|dont|do not)\s+(?:want|wanna)\s+(?:to\s+)?(?:be here|go on|carry on)"
    r"(?=\s*(?:$|[.,!?;]|\b(?:anymore|any more|any longer|like this|this way)\b))|"
    r"\b(?:i|we)\s*(?:'?m|am)?\s*(?:sick|tired)\s+of\s+(?:living|life)\b"
    r"(?=\s*(?:$|[.,!?;]|like this\b))")


# "i feel awful about what i said to her" is guilt about one thing, which the guilty pool
# answers better than the general low.
GUILT_ABOUT = re.compile(r"\b(?:awful|bad|terrible|dreadful|guilty)\s+about\b")


# "im going mad", "am i going mad", "i think im losing my mind": the idiom is fear about your
# own head, not anger. Bare "mad" is a word in the annoyed pool, so these lines were answered
# "Annoying. Walk it off for ten minutes before you reply to anyone" - advice for a row with
# somebody, given to a person frightened of themselves - and "im going crazy at work" got the
# busy-day line. The idiom is read as the not-coping disclosure it is, which is the pool with
# "is there anyone around you who knows it is like this" in it.
GOING_MAD = re.compile(
    r"\b(?:going|go|gone|went)\s+(?:mad|crazy|mental|insane)\b|"
    r"\blos(?:e|es|ing|t)\s+(?:my|the)\s+(?:mind|marbles|plot)\b|"
    r"\b(?:going|going\s+out)\s+of\s+(?:my|his|her|their)\s+mind\b")


# A day, a week or the office is "mad" when it was full-on, and the annoyed pool is written for a
# quarrel with somebody: "work was mad today" got "Annoying. Walk it off for ten minutes before you
# reply to anyone", which also put a second person in a line that has none - and the line that
# found it went on "...and i ate nothing all day", so the one thing worth noticing was not read.
# The subject is what tells the two apart: a place or a stretch of time is mad, and "im mad", "mad
# at him", "he made me mad" are still a person's anger.
MAD_ABOUT_THE_DAY = re.compile(
    r"\b(?:work|job|office|school|uni|college|shop|shops|town|roads|traffic|queues?|"
    r"term|day|days|week|weeks|month|months|morning|afternoon|evening|weekend|nights|it|its|"
    r"things|everything|life)\b"
    r"(?:(?:\s+(?:has|had|have|is|was|are|were|been|being|gets|got)\b)"
    r"|(?:\s*'(?:s|ve)\b)){1,3}\s*"
    r"(?:\s+(?:so|really|proper|properly|fairly|pretty|very|dead|bloody|totally|absolutely)\b)?"
    r"\s+mad\b(?!\s+(?:at|with|about)\s+(?:me|us|you|him|her|them|everyone|everybody|the\s+\w+))"
    r"|\bmad\s+(?:day|week|month|morning|afternoon|shift|one|busy|rush|time)\b")


# "struggling with my dissertation" is a piece of work, not a mood: a named thing takes it
# unless the thing is the whole of life.
STRUGGLING_ABOUT_A_THING = re.compile(
    r"\bstruggling\s+(?:with|through)\s+(?!everything\b|it all\b|life\b|all of it\b|"
    r"any of it\b|the kids\b|money\b|sleep\b|work\b|my mood\b|myself\b)\w+")


# The same disclosure asked as a question: a person who asks how to get through the week has
# just said they are in one. "im struggling this week" got the warm pool and "how do i cope"
# got the search hedge, which is the coldest answer in the bot to the warmest line.
#
# The asking word, the speaker, then a verb of lasting something out - so it is the shape that
# carries the reading, not the words "cope" or "through" on their own: "how do i get through
# to the council" and "how do i cope with my mother in law" name a thing to deal with and are
# somebody else's answers (a named thing takes the line, as STRUGGLING_ABOUT_A_THING says).
# "how do i cope with all this" and "how do i get through the week" name nothing but the
# person's own week, so they are this pool's.
HOW_I_GET_THROUGH = re.compile(
    r"\bhow\s+(?:do|can|will|should|am)\s+i\s+(?:"
    # "cope" only when nothing named follows it: a stress, loneliness or a mother in law is a
    # thing to cope with, and the card that answers it keeps the line. The word may be the whole
    # of what is left ("how do i cope"), or point at the span of it ("cope with it", "cope with
    # this"), or end at "with" once the span has been trimmed off ("how do i cope with ").
    r"(?:cope\b(?:\s+with)?\s*$|cope\b\s+with\s+(?:it|this|that|everything|all\s+of\s+it)\b"
    r"|cope\s+(?:it|this|that|everything)\b)"
    # the span of it may already be gone: chat reads these lines with a named time span
    # trimmed off, so "how do i get through this week" arrives here as "how do i get through "
    # the span is the only thing trimmed, so a line whose span was a named week arrives here
    # ending at the verb ("how do i get through "), and anything still after it ("customs",
    # "on 30k", "this traffic") is a thing to get through or live on, which is somebody
    # else's line - "this" only counts when it is the whole of what follows.
    r"|get\s+through\b(?:"
    r"\s*$|\s+(?:(?:all\s+)?this\b(?=\s*(?:$|[.,!?;]))|it\b"
    r"|the\s+(?:week|night|day|month|days|year)\b|today\b|tonight\b))"
    r"|deal\s+with\b(?:\s*$|\s+(?:all\s+this\b(?=\s*(?:$|[.,!?;]))|it\s+all\b))"
    r"|survive\b(?:\s*$|\s+(?:it\b|the\s+(?:week|day|month|night)\b))"
    r")"
    # the same said as not knowing how: "i dont know how to get through this"
    r"|\bi\s+(?:dont|don't|do\s+not|can'?t|cant|can\s+not)\s+know\s+how\s+to\s+(?:"
    r"(?:cope\b(?:\s+with)?\s*$|cope\b\s+with\s+(?:it|this|that|everything|all\s+of\s+it)\b)"
    r"|get\s+through\b(?:\s*$|\s+(?:(?:all\s+)?this\b(?=\s*(?:$|[.,!?;]))|it\b))"
    r"|deal\s+with\b(?:\s*$|\s+(?:all\s+(?:this|of\s+this)\b|it\s+all\b))"
    r")")


# "why do i always feel rubbish" is a question about the cause, and the answer to it is not a
# warm line about carrying something: it wants an explanation, so the pools stand down.
ASKS_WHY = re.compile(r"^\s*(?:why|how come|what makes|whats making|what'?s making)\b")


# "i feel terrible, i cant sleep" is a night nobody slept: the sleep answer is the only part of
# that line anyone can help with, and the bad-day pool's "nothing needs fixing this minute" is
# the opposite of what you say to someone who has not slept. So a night the person named stands
# the plain-adjective pool down, and the sleep entry keeps the turn.
A_NIGHT_NOT_SLEPT = re.compile(
    r"\b(?:sleep|slept|sleeping|awake|insomnia|up all night|no sleep|not sleeping)\b")


# The speaker, in the few words before the idiom: "im going mad", "am i going mad", "i think
# im losing my mind", "i feel like im going crazy". Without one of these in front, the line is
# about something else going mad - "work is going mad this week", "the kids are going mad",
# "were all going mad in this house" - and none of those is a disclosure about the speaker.
FIRST_PERSON_BEFORE = re.compile(r"\b(?:i|im|i'm|i am|i've|ive|me|myself)\b[^.]{0,9}$")


# "im going crazy at work" is distress in a place; "im going mad at the mess" is anger at a
# thing. The place is not the thing the anger is at, so it does not count as one.
IDIOM_PLACE = re.compile(r"^\s*(?:work|home|school|uni|college|night|the moment|the minute|"
                         r"times|first|least|times like this|it all|myself|me)\b")


# A place makes the line ambiguous: "im going crazy at work" is how people say swamped, and the
# busy-day line ("is there anything you can drop") is the right answer to it, while "i feel like
# im going crazy at work" is a person telling you about their head. The fear frame is what tells
# the two apart, so with a place after the idiom the frame is required.
FEAR_BEFORE = re.compile(r"\b(?:feel(?:s|ing)?\s+like|felt\s+like|think|thought|thinks|"
                         r"thinking|might\s+be|might|maybe|mightbe|worried|scared|afraid|"
                         r"wonder(?:ing)?|am\s+i|are\s+we|do\s+you)\b")


def _bad_day(clean):
    """True when the line is a bad day said with a plain adjective, not a disclosure."""
    text = " ".join(str(clean or "").split())
    if (ASKS_WHY.search(text) or GUILT_ABOUT.search(text)
            or A_NIGHT_NOT_SLEPT.search(text)):
        return False
    if not NOT_COPING_FEEL.search(text):
        return False
    return not STRUGGLING_ABOUT_A_THING.search(text)


# A mind that will not hold still, said with the part doing the thinking rather than a mood
# word: "my head is all over the place", "my brain is fried", "my thoughts are all over the
# shop", "im scattered", "im in a fog today". Nothing above reads it - the line names no task
# and no feeling the tables know - so most of these phrasings got the greeting module's stock
# "I'm listening - say more if it helps", which hands the work straight back to the person.
# The head has to be the speaker's own, so "the kids left their things all over the place" and
# "the shops are all over the place" stay where they are. "My head is spinning" is left out on
# purpose: that one is a body symptom, and its reply is the health entry's.
SCATTERED_MIND = re.compile(
    # A head that will not clear is said with the weather's own words and with a thickness: "my
    # head is cloudy", "my head feels thick", "my head is woolly", "i have brain fog". The same
    # words describe jam, soup and a tongue that is swelling, so only the person's own head,
    # brain or mind counts here.
    r"\b(?:my|our)\s+(?:head|brain|mind|thoughts|head's|thinking)\b[^.!?]{0,26}?"
    r"\b(?:all over the (?:place|shop|show)|fried|mush|scrambled|to mush|scattered|fog|foggy"
    r"|fuzzy|woolly|wooly|muzzy|cloudy|misty|thick|fogged|clogged\b"
    r"|(?:a |a right |a total |one )?mess\b)"
    r"|\b(?:my|our)\s+(?:head|brain|mind|thoughts)\b[^.!?]{0,20}?"
    r"\b(?:a|one)\s+(?:hundred|million|thousand)\s+miles\s+an\s+hour\b"
    r"|\b(?:i'?m|im|i am|i feel|i felt|feeling|feel)\s+(?:so |really |very |totally |"
    r"completely |pretty |a bit |kind of |kinda |all )*"
    r"(?:scattered|frazzled|all over the (?:place|shop|show)|in a fog|foggy|muzzy|woolly|fuzzy)\b"
    # "i have brain fog", "i get brain fog": the fog named as a thing the person has
    r"|\b(?:i|im|i'm|ive|i've)\s+(?:have|had|got|get|gets|keep getting)\b[^.!?]{0,4}?"
    r"\bbrain\s*fog\b")


def _scattered(clean):
    """True when the line says the speaker's own mind will not settle."""
    match = SCATTERED_MIND.search(clean)
    if not match:
        return False
    # "im not scattered, im just tired" denies it: the feeling pools already read a denied word
    # as not said, and this owes them the same reading.
    before = re.split(r"[.!?,;:]", clean[:match.start()])[-1].split()[-3:]
    return not any(word.strip(".,!?;:").lower() in NOT_WORDS for word in before)


# Contact lost is how loneliness is most often said, and none of it names a feeling word: "i cut
# myself off from my friends last year", "ive stopped seeing my mates", "i havent spoken to anyone
# in weeks". Without this the line is a shrug ("I'm listening - say more if it helps"), and the
# first thing a person says about a year of it decides whether they say the rest. The advice is
# the one that gets somebody back in: one person, one small thing, and no apology for the gap.
#
# The speaker has to be the one who withdrew. "i cut myself off from everyone" is read anywhere in
# the line; the shapes below all open on the person ("i stopped", "i havent", "we drifted"), so
# "my mate cut himself off from his family" and "she stopped seeing her friends" keep their own
# turns - a line about somebody else is not the speaker's loneliness.
# "stopped seeing" takes any object and only a person makes it loneliness: a break-up ("i stopped
# seeing my ex"), the end of a course of therapy ("i stopped seeing my therapist", often a good
# thing) and a mood ("i stopped seeing the point") are three different things those words carry,
# and a lonely reply on any of them is the bot mishearing them (sapphire-jay, patient-shark, #4350).
APART_WHO = (r"(?:anyone|anybody|everyone|people|friends?|mates?|family|relatives?|neighbours?"
             r"|neighbors?|colleagues?|classmates?|workmates?|the lads|the girls|the others"
             r"|(?:my|our)\s+(?:friends?|mates?|family|parents|mum|mam|dad|mother|father"
             r"|brothers?|sisters?|kids?|children|cousins?|gran|nan|nana|grandma|grandad"
             r"|grandpa|aunt|auntie|uncle|folks|neighbours|neighbors))")


APART_FROM_PEOPLE = re.compile(
    r"\b(?:i|i'm|im|ive|i've|i'd|we|we're|were|weve|we've)\b[^.]{0,40}?"
    r"(?:cut (?:myself|ourselves) off|cut (?:myself|ourselves) (?:off )?from (?:everyone|everybody|"
    r"people|the world|society|friends|mates|family|my \w+|our \w+|contact|all of it|it all)"
    r"|shut (?:myself|ourselves) (?:away|off|in)"
    r"|(?:stopped|stopping) (?:seeing|speaking to|talking to|meeting) " + APART_WHO +
    r"|(?:not|haven't|havent|hadn't|hadnt) (?:seen|spoken to|talked to|heard from) (?:anyone|anybody|"
    r"any one|a soul|my \w+|our \w+|friends|mates|family)"
    r"|(?:never|hardly|rarely|don't|dont|do not) (?:see|speak to|talk to) (?:anyone|anybody|my \w+|"
    r"our \w+|people|friends|mates)"
    r"|(?:stopped|stopping) (?:going out|meeting up)"
    r"|(?:dont|don't|do not) (?:go out|see anyone|have any friends|have friends)"
    r"|(?:drifted apart|lost touch|no one to (?:talk|speak) to|nobody to (?:talk|speak) to))", re.I)


# A line about somebody else's withdrawal, or a question about how to do it to yourself in the
# ordinary sense ("how do i cut myself off from a cold caller"), is not this.
APART_SOMEONE_ELSE = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:\w+)\s+(?:cut|stopped|has stopped|had stopped|drifted)"
    r"|\bhow do i cut (?:myself|him|her|them) off from\b", re.I)


# A line that only takes in what was just said, or only asks for more of it: "ok", "cool", "i
# see", "and", "go on", "more". Either way the person is leaving the floor to the bot, and in a
# thread about something hard that is a request to stay with them, not the end of a chat. Narrow
# in both directions - "and then what did she say" names something and keeps its own answer, a
# thanks has a pool of its own, and a no is not this.
BARE_ACKS = frozenset((
    "ok", "okay", "right", "alright", "cool", "nice", "great", "good", "fine", "fair enough",
    "i see", "got it", "gotcha", "makes sense", "understood", "noted", "wow",
))


# Only the words that ask the bot to carry on, never the ones that ask what to do next: "what
# next", "then what", "and then what", "next" are the person asking a question, and this thread
# has answers to those ("i lost my job / what next" wants the redundancy steps, and "my dad is in
# hospital / what next" the visiting times). The floor line is the answer to "go on", not to a
# question, so those four are left to the module that can answer them.
BARE_CARRY_ON = frozenset((
    "and", "so", "then", "and then", "more", "go on", "keep going", "carry on", "going on", "on",
    "go on then",
))


def _a_bare_acknowledgement(clean):
    """True when the line only takes in what was said, or only asks for more of it."""
    words = re.findall(r"[a-z']+", " ".join(str(clean or "").lower().split()))
    while len(words) > 1 and words[0] in ("ok", "okay", "right", "well", "so", "and", "but", "now"):
        words = words[1:]
    return " ".join(words) in BARE_ACKS | BARE_CARRY_ON


# The pools this module answers a piece of hard news from. The reply is in the memory as text and
# the note below only exists for the feelings, so the text is the second reading: "i lost my job"
# is not a feeling, and the sentence said back to it is the only trace of what it was answered as.
SORRY_KINDS = frozenset(("sad", "bad_day", "rough_day", "not_coping", "venting", "own_fault",
                         "not_fair", "not_enough", "worry", "worry_person", "guilty", "missing",
                         "lonely", "lonely_apart"))


SORRY_NEWS_KINDS = frozenset(("lost_job", "bad_news"))


SORRY_LINES = frozenset(line for kind in SORRY_KINDS for line in REPLIES.get(kind, ())
                        if "{" not in line) | frozenset(
                            line for kind in SORRY_NEWS_KINDS for line in NEWS_REPLIES.get(kind, ())
                            if "{" not in line)


# An answer that met what the person said as hard news, read from the bot's own line the way main's
# own nod rule reads it (see NEWS_MET below). The exact pool lines are the first reading; this is
# the second, for the heavy replies that come from a band this module cannot see - "i failed my
# driving test" is answered by the answers module, so there is no pool of mine to look in and the
# sentence "Sorry to hear it - it is a common day and it is not a verdict" is the record. The two
# arms main has and this one leaves out are "no wonder" and "hardest days", which are said about a
# phone that died and a bad week as readily as about a loss.
SORRY_MET = re.compile(
    r"\b(?:sorry to hear|i'm sorry|i am sorry|so sorry|really sorry|such sad news|"
    r"a lot to carry|that's rough|that is rough|how awful|that's awful|that's hard|that is hard|"
    r"a real loss)\b", re.I)


# The modules that answer a hard thread from outside this one: a death, a body in trouble, a
# person in danger.
HEAVY_MODULES = frozenset(("loss", "grief", "safety", "urgent"))


def _the_heavy_line(memory):
    """The line the hard news was in, or "" when the last reply was not about something hard.

    The line is what seeds the pool, the way main's own `_the_nod` seeds it: with one seed for
    every thread the four lines collapse to whichever one an empty seed lands on, which is the
    stock line by another route - "i lost my job" and "my mum has cancer" got the same sentence.

    Three readings, because hard replies come from three places: this module's feeling pools note
    the turn they answered (see _the_weight_said); a piece of bad news is read from the sentence
    the bot said back, since that pool is not a feeling and leaves no note; and a death or an
    emergency is answered by another module entirely, so the module that took the last turn says
    it - "my dad died last week" goes to bot/modules/grief.py, which this one never sees.
    """
    if not isinstance(memory, dict):
        return ""
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return ""
    note = memory.get("heavy_reply")
    if isinstance(note, dict) and note.get("turn") == len(turns) - 1:
        line = note.get("line")
        if isinstance(line, str) and line.strip():
            return line
        theirs = turns[-1].get("user") if isinstance(turns[-1], dict) else ""
        return str(theirs or "")
    # The person can take a hard reply in over more than one turn ("i lost my job" / "ok" /
    # "and"), and the readings below are about the turn that carried the news, not about the
    # acknowledgement that followed it - which reads as nothing at all and would have the third
    # turn answered by whichever module takes a bare "and". So the walk goes back over turns that
    # only took something in, and stops at the last turn that said something.
    last = {}
    for turn in reversed(turns):
        if not isinstance(turn, dict):
            break
        last = turn
        if not _a_bare_acknowledgement(" ".join(str(turn.get("user") or "").lower().split())):
            break
    theirs = last.get("user")
    seed = str(theirs or "")
    if last.get("module") in HEAVY_MODULES:
        return seed
    said = last.get("bot")
    if isinstance(said, str) and (said.strip() in SORRY_LINES or SORRY_MET.search(said)):
        return seed
    # ...and the reading of the line itself, which is the third place a hard thread is written
    # down: a death and a piece of bad news are read by the engine's own readers before any module
    # answers, so "i got fired" and "my girlfriend left me" count even when the reply came from a
    # band this module cannot see.
    if seed.strip() and (loss_reading.reads_as_loss(theirs) or badnews.reads_as_bad_news(theirs)):
        return seed
    return ""


def _apart_from_people(clean):
    """True when the person says, in their own words, that they have lost touch with people."""
    text = " ".join(str(clean or "").split())
    if not APART_FROM_PEOPLE.search(text):
        return False
    return not APART_SOMEONE_ELSE.search(text)


# The turn after a reply about being lonely: "what can i do about it", "so what do i do". It is
# the ask people actually make, and on its own it was answered with a day out ("decide by the
# weather") or a hedge, both of which drop the loneliness the person just told us about. Only the
# words of the ask itself pass here, so a line that names a thing keeps its own answer.
LONELY_STEP_WORDS = frozenset("""and so ok okay right but well what how can could should shall
    do does i we about it that this now start fix sort change then much else next""".split())


# Nothing helping: the follow-up a person makes when the advice and the small things have not
# worked. The words are the whole line, so a thing that has stopped working keeps its own answer
# ("my laptop froze completely and nothing works" is the laptop).
NOTHING_HELPING = re.compile(
    r"\bnothing (?:seems to |really |ever |at all |much |has |had )?(?:help|helps|helped|work|works|"
    r"worked|(?:is|isnt|isn't) (?:helping|working))\b"
    r"|\bnothing (?:seems to )?makes? (?:any )?difference\b"
    r"|\b(?:ive|i've|i) tried (?:everything|it all|all of it)\b"
    r"|\b(?:doesnt|doesn't|didnt|didn't) (?:help|work|make any difference)\b"
    r"|\b(?:isnt|isn't|is not) (?:helping|working)\b", re.I)


def _idk_kind(memory):
    """Which "i dont know" the person needs: the one after a question, the one in a heavy chat, ...

    "i dont know" is never about itself - it answers what the bot said a turn before, so the pool
    is chosen by that. Two chats on main show why: after the bot asked "What's taking most of it?"
    (following "i feel really flat" / "work is just busy") the line got "No rush. If you tell me
    the options, I'll help you pick", which offers to choose between options nobody mentioned, and
    the same sentence came back in a chat about what to cook, where it is nearly right and still
    cold. A fog in a heavy chat is not a request for a shortlist.
    """
    if not isinstance(memory, dict):
        return "idk"
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return "idk"
    note = memory.get("heavy_reply")
    if (isinstance(note, dict) and note.get("feeling") in HEAVY_FEELINGS
            and note.get("turn") == len(turns) - 1):
        return "idk_heavy"
    last = turns[-1]
    said = str(last.get("bot") or "") if isinstance(last, dict) else ""
    if not said.strip():
        return "idk"
    if _offered_a_choice(said):
        return "idk_choice"
    if said.rstrip().endswith("?"):
        # The bot asked, and the person cannot answer it. A second question is nagging, and the
        # offer to "help you pick" is the wrong offer: the pool eases the question and leaves the
        # floor open.
        return "idk_asked"
    return "idk"


def _offered_a_choice(said):
    """Whether the bot's own last line put two or more things in front of the person.

    A comma and an "or" in the same clause is a shortlist ("Quick: tuna pasta in 15, macaroni
    cheese in 25, or a sausage traybake"). Nothing else here reads as one: a line that merely says
    the word is not a menu, and the choice pool would be as wrong as the plain one was.
    """
    for clause in re.split(r"(?<=[.!?])\s+", str(said or "")):
        # A shortlist reads "A, B, or C" and ends the sentence there. A bare comma and an "or"
        # anywhere in the clause is not enough: "squats or sit-to-stands, press-ups on the stairs
        # or in the kitchen" would read as a menu of three things to choose between.
        if re.search(r",\s*[^,.;:]{2,60},\s*or\s+[^,.;:]{2,60}\s*\.?\s*$", clause, re.I):
            return True
    return False


# The same follow-up with the small things named, on the turn after one: "ive tried going for a
# walk and it doesnt help". It is longer than the bare line, so the length is read with it.
# The line has to be about the trying and not about a thing: "my laptop wont turn on and nothing
# works" is the laptop, and the note on the turn before it is no reason to comfort anyone.
NOTHING_CONTINUED = re.compile(
    r"^(?:and\s+|but\s+)?(?:i(?:\s*'ve|\s*ve|\s+have)?\s*(?:tried|try|keep)|nothing|none of it|"
    r"it|that|this|they|even)\b", re.I)


def _nothing_helped_just_before(memory, clean):
    """Whether the last reply already said nothing was helping, and this names the small things.

    Read from the bot's own line in the history rather than a note this module leaves: the pool's
    lines are only ever said for this, and the arbiter keeps the copy of the memory of the module
    whose reply the person got, so a note is not always this module's to keep.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list) or not turns:
        return False
    last = turns[-1]
    said = " ".join(str(last.get("bot") or "").split()) if isinstance(last, dict) else ""
    if not said or len(clean.split()) > 12:
        return False
    return bool(said in REPLIES["nothing_helps"] and NOTHING_CONTINUED.search(clean))


def _as_said(clean, understood):
    """The line with the words that were wrong put right, for the matchers that read English.

    The reading records each repair in `plain` - "bout" is "about", "tird" is "tired", "worrid"
    is "worried" - and a matcher that decides by a word has to see it, or the same line typed at
    speed and typed carefully take two different branches. Only the spelling changes: no word is
    added, moved or taken away, so a pattern that needs a little word in front of a name ("worried
    about my mum") finds it here and misses it in the words as typed.
    """
    if isinstance(understood, dict):
        plain = understood.get("plain")
        if plain:
            return " ".join(str(plain).lower().split())
    return clean


# A modal in front of a state of being does not make a plan. "i think i might be depressed",
# "i may be getting depressed", "i could be low" all matched the plan marker ("i might"), and the
# plan pool congratulated a person who had just said they may be depressed: "Nice. Tell me how it
# goes." The feeling reader could not see the state either, because the modal sits in front of it -
# "i think im depressed" was answered as a feeling, and the same line with "might be" in it was
# given the plan. So a modal in front of "be" and a feeling word is read as the feeling it is: the
# line is rewritten as "im <state>", and every reader below sees the state of being. Only a feeling
# word is rewritten, so "i might be late" is still the plan-or-worry it was.
MIGHT_BE = re.compile(
    r"\bi\s+(?:think\s+(?:that\s+)?i\s+)?(?:might|may|could|probably)\s+(?:also\s+|just\s+|"
    r"honestly\s+|actually\s+)?be\s+(?:(?:getting|feeling|a\s+bit|very|really|pretty|quite|so|"
    r"too|this|kind\s+of|sort\s+of)\s+)*(?P<state>[a-z]+)", re.I)


# A verdict asked about a choice - "would i be mad to sell", "is it stupid to buy a new one",
# "would moving closer be mad" - asks for a judgement, and the feeling word in it is the verdict
# the person wants rather than a report of anger. The reading takes "mad" as anger, so the annoyed
# pool answered these: "Annoying. Walk it off for ten minutes before you reply to anyone", which is
# advice for a quarrel, given to somebody weighing up a decision. The question frame plus a word
# that has to follow it (to X, if X, or the end of the line) is what separates the verdict from a
# mood: "im mad", "im mad at my boss" and "is she mad at me" keep their own replies.
A_VERDICT_ASKED = re.compile(
    r"\b(?:would|will|am|is|are|was|were)\s+"
    r"(?:i|we|it|that|this|they|he|she|you|a|an|the|going|moving|getting|leaving|buying|"
    r"selling|quitting|starting|taking|doing)\b"
    r"[^.!?]{0,40}?\b(?:mad|crazy|stupid|daft|weird|selfish|silly|unreasonable|idiot|bad)\b"
    r"(?=\s*(?:$|[.,!?;]|to\b|if\b|for\b|about\b|that\s+(?:i\s+(?:want|should|need|can|could|"
    r"may|might)|we\b|my\b|they\b|he\b|she\b)))", re.I)


# A yes/no question about the thing the answer above named: "is that too low", "is it too high",
# "was that too much". The word after "that" is the measurement, so none of these is a mood, and
# the ones that name a feeling word ("low", "heavy") are the ones the mood reader used to take.
A_QUESTION_ABOUT_A_FIGURE = re.compile(
    r"^(?:so |and |but |ok |okay |sorry |oh |hmm |wait |right )*"
    r"(?:is|was|are|were) (?:that|this|it)(?: a bit| a little| way| much)? (?:too )?"
    r"(?:low|high|heavy|light|much|little|many|few|big|small|long|short|often|late|early)\b")


# A ward they have left is not a ward they are in. "im glad, my mum is out of hospital" carries an
# event, and the news reader the mood branch stands aside for does not answer it: the store reads
# "hospital" as the trouble and the reply says "That is a worrying place for your mum to be". Until
# a recovery has a news reply of its own, the line keeps the mood reply rather than that one.
LEFT_BEHIND = re.compile(
    r"\b(?:out\s+of|home\s+from|back\s+home\s+from|came\s+home\s+from|come\s+home\s+from|"
    r"discharged\s+from|released\s+from)\s+(?:the\s+)?hospital\b")


# A feeling that has been going on for weeks is a different line from the same feeling today,
# and the pools above answer today: "i feel anxious all the time" was given "Nerves before
# something big are normal", which presumes a date, and "i cry all the time" got a nod. Only the
# mood kinds: a headache or a tiredness that keeps coming back is the knowledge entries' line,
# and a machine that keeps switching off is nobody's mood.
GOING_ON = re.compile(
    r"\b(?:all the time|all day every day|every day|every single day|most days|"
    r"most of the time|constantly|non ?stop|day after day|week after week|"
    r"for (?:weeks|months|years)|keep (?:feeling|crying|being)|keeps? feeling|"
    r"always (?:feel|feels|feeling|angry|sad|anxious|worried|down|low|crying|tearful))\b")


# The cues of GOING_ON that say how long or how often, and not only that it happens again: the
# same list without its two habit arms (`keep crying|feeling|being`). The weeks-of-it pool is
# written for these: "i feel sad all the time" has said how often, while "i keep crying" has only
# said it comes back, and that line gets the `recurring` pool instead. A habit line that does give
# a length ("i keep feeling low for weeks") names one of these cues too, so it still gets it.
GOING_ON_LONG = re.compile(
    r"\b(?:all the time|all day every day|every day|every single day|most days|"
    r"most of the time|constantly|non ?stop|day after day|week after week|"
    r"for (?:weeks|months|years)|always (?:feel|feels|feeling|angry|sad|anxious|worried|"
    r"down|low|crying|tearful))\b")


# The kinds that are a mood rather than a thing happening to them or to a part of them: a
# headache that keeps coming back is a knowledge entry's line, not a mood's, and "im tired all
# the time" has its own answer.
# Loneliness and guilt keep their own pools even when they have gone on for weeks: "a weekly
# club is the quickest way to see the same faces" answers "i feel lonely all the time" better
# than an appointment does.
# Cross with themselves, rather than with whoever caused it: "im so annoyed with myself", "im so
# cross with my own stupidity", "i could kick myself", "i feel frustrated with myself". The
# annoyed pool is written for somebody else being in the way ("say it out loud to whoever caused
# it"), which is a second person in a line that has none. "im annoyed with my sister" is not
# this: the words after "with" name someone else.
AT_MYSELF = re.compile(
    r"\b(?:annoyed|angry|cross|furious|frustrated|irritated|fed up|pissed off|mad)\b"
    r"[^.!?]{0,25}?\b(?:with|at)\s+(?:myself|me\b(?!\s*(?:too|as well)))\b|"
    r"\b(?:with|at)\s+myself\b|"
    r"\bmad at me for\b|\bcross with my own\b", re.I)


# The idiom that says the same thing without a feeling word: "i could kick myself", "i could
# strangle myself for that". It is crossness with their own mistake, so it takes the same pool -
# and it is read before the greeting, which used to answer "Got it - you could kick yourself."
KICK_MYSELF = re.compile(r"\bi could (?:kick|strangle|shake) myself\b|\bkick myself for\b", re.I)


AT_MYSELF_REPLIES = REPLIES["at_myself"]


# A part of the person getting worse is a body or a faculty question, not a rough day: the engine
# reads "my memory is getting worse" as `unwell`, its word for being under the weather, and the
# rough-day pool answered it with "a shower, something warm to eat and an early night usually
# resets it". A memory, a hearing or a knee that is getting worse has its own answer in the
# knowledge base, and this row stands aside for it (see `_feeling` below).
# A part of them, or a faculty, said as going off: "my memory is getting worse", "my eyesight has
# got worse". The line is about the part, so a pool line about them in general is the wrong reply
# when a card answers the part.
A_FACULTY_GETTING_WORSE = re.compile(
    r"\bmy\s+(?:memory|memories|recall|forgetfulness|hearing|sight|eyesight|vision|balance|"
    r"mobility|breathing|joints?|knees?|hips?|back|hands?|skin|teeth|gums|grip)\b"
    r"[^.!?]{0,30}?\b(?:getting|got|is|are|has been|have been)\s+"
    r"(?:so |much |a lot |that )?(?:worse|bad|badly)\b")


# The same worry worn differently: the memory said as a comparison with how it used to be, as a
# state ("im getting forgetful", "my wife says im scatty"), as something being lost, or as a run of
# slips. Each is a shape rather than a phrase, because the words people use for it are endless and
# the card is the same card.
OWN_MEMORY_OFF = re.compile(
    r"\bmy\s+(?:memory|memories|recall|forgetfulness)\b[^.!?]{0,30}?"
    r"\b(?:isnt|is not|wasnt|not|no longer|never)\s+(?:what|as|as good|up to|reliable)\b|"
    r"\b(?:im|i am|i'm)\s+(?:getting|becoming|so|very|quite)\s+"
    r"(?:forgetful|scatty|absent[- ]minded|forgetfull)\b|"
    r"\b(?:im|i am|i'm)\s+losing\s+my\s+(?:memory|recall)\b|"
    r"\b(?:i\s+(?:keep|am constantly|constantly|always)\s+forgetting\s+"
    r"(?:everything|things|words|names|where|what))\b|"
    r"\bcant\s+remember\s+(?:things|names|words|where|what|how)\b"
    r"[^.!?]{0,25}?\b(?:used to|any\s?more|anymore|lately|these days|now)\b|"
    r"\b(?:worried|worry|worries|worried sick)\s+about\s+my\s+(?:memory|recall|forgetfulness)\b|"
    r"\bis\s+my\s+(?:memory|recall)\s+(?:ok|okay|normal|going|getting|all right|alright)\b|"
    r"\b(?:scared|worried|frightened|terrified)\s+(?:that\s+)?(?:im|i'm|i am)\s+"
    r"(?:getting|losing)\b|"
    r"\b(?:does|is|do)\s+(?:forgetting|this|that)\s+(?:mean|a sign of)\s+dementia\b|"
    r"\bmy\s+(?:memory|recall)\s+(?:is|has been)\s+(?:terrible|awful|rubbish| shocking|bad)\b")


MOOD_KINDS = frozenset(("sad", "anxious", "annoyed"))


# The pools that answer something heavy the person is carrying. The line after one of them is
# usually the reason for it - "i miss my mum" then "she lives in spain" - and the store's
# acknowledgement reads that (bot/memory/ack.py, _after_a_feeling) so the reason is not filed
# away flat. The engine's own reading misses some of these lines ("i miss my mum" is filed as
# news), so the pool the composer answered from is the record that survives the turn.
#
# Pools that are warm about a passing mood are not here: "im bored" then "i finished my book"
# is not a reason for anything, and the reply that follows a heavy line ("that is a lot to
# carry") would be wrong said about it.
HEAVY_FEELINGS = frozenset(("missing", "sad", "lonely", "lonely_apart", "not_coping", "bad_day",
                            "rough_day", "worry", "worry_person", "guilty", "venting",
                            "not_enough", "own_fault", "not_fair",
                            # The comparisons a person draws about themselves ("i feel like im
                            # letting everyone down", "i feel like nobody listens") and the week
                            # that has gone wrong ("nothing is going right") are the same weight
                            # as the feeling words, so the line after one is answered as the
                            # reason for it ("You hardly see them - so that is the part behind
                            # it") rather than echoed back as a fact. "feel_like_good" is not
                            # here: nothing follows from a good one.
                            "feel_like_not_enough", "feel_like_load", "feel_like_left",
                            "feel_like_adrift", "against_me"))


# The people a line can be about instead of the person talking, so their hospital is left to
# `_about_someone` rather than answered here as if it were the user's own visit.
SOMEBODY_ELSE = re.compile(
    r"\b(?:he|she|they|him|her|them|his|hers|their|mum|mom|mother|dad|father|son|daughter|"
    r"wife|husband|partner|brother|sister|friend|grandma|grandad|gran|nan|nanna|aunt|uncle|"
    r"cousin|colleague|boss|neighbour|neighbor)\b", re.I)
