"""Part 1 of 8 of a large module, split out of `lookup`.

Everything here is re-exported from `lookup`, so callers import it from there as before.
"""
import re



try:  # the reading of a dream, so a dream of a thing is not the thing
    from ..memory import dream as _DREAM
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no rule
    _DREAM = None


import string  # noqa: F401


# Misspellings a domain lists as key words on purpose, mapped to the entries that list them, so its
# own answer can be reached from the misspelling itself ("how do i spell definately"). A word is
# only left out of the vocabulary below when the entries that use it are exactly the ones that
# registered it: then it is a misspelling and nothing else, and the slip reader keeps reading it as
# the right word. Without that, listing "adress" quietly stopped "who do i tel about my new adress
# after moving" from reaching the address answer, because a key word is never read as a slip.
SLIPS = {}


from ..understanding import lexicon  # noqa: F401


from ..understanding.normalize import LEXICON as COMMON_WORDS  # noqa: F401


from ..understanding.normalize import TIME_WORDS  # noqa: F401


# A sentence with a hole in it is filled with words out of the person's own line, and only the
# words that name something should go in. "is it ok to give water" hands the heartburn card the
# phrase "ok to" before the verb "give", and "Cut ok to out for a fortnight" is not a sentence
# anybody wrote: it is word salad in the middle of an answer. One content word is the whole test,
# so no list of foods, cities or machines has to be kept up to date.
GRAMMAR_ONLY = frozenset((
    "a", "an", "the", "and", "or", "but", "if", "so", "as", "at", "by", "for", "from", "in",
    "into", "of", "on", "onto", "over", "under", "to", "up", "with", "without", "about",
    "after", "before", "than", "then", "that", "this", "these", "those", "it", "its", "is",
    "are", "was", "were", "be", "been", "being", "am", "do", "does", "did", "doing", "done",
    "can", "could", "should", "would", "will", "shall", "may", "might", "must", "not", "no",
    "yes", "ok", "okay", "alright", "just", "also", "too", "very", "really", "quite", "more",
    "most", "much", "many", "any", "all", "some", "none", "every", "each", "i", "me", "my",
    "mine", "we", "us", "our", "you", "your", "he", "him", "his", "she", "her", "they",
    "them", "their", "there", "here", "when", "where", "what", "which", "who", "how", "why",
    "have", "has", "had", "having", "get", "gets", "getting", "got", "go", "goes", "going",
    "went", "give", "gives", "gave", "giving", "take", "takes", "took", "taking", "make",
    "makes", "made", "making", "eat", "eats", "ate", "eating", "eaten", "drink", "drinks",
    "drank", "drinking", "drunk", "again", "still", "always", "never", "sometimes", "often",
    "now", "today", "tonight", "yesterday", "tomorrow", "lot", "lots", "loads", "bit", "kind",
    "sort", "one", "ones", "thing", "things", "time", "times", "day", "week", "month", "year",
))


def names_a_thing(phrase):
    """Whether a phrase that fills a hole in a sentence names something.

    Used where the phrase came out of the person's own line. A phrase of grammar alone ("ok to",
    "not", "is it") fills no hole: the card says its plain answer instead of a broken sentence.
    A number is not a thing either - "Cut 3 out for a fortnight" is the same salad.
    """
    words = [word for word in re.split(r"[^a-z0-9']+", str(phrase or "").lower()) if word]
    return any(word not in GRAMMAR_ONLY and not word.isdigit() for word in words)


WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


# The table `re` keeps of compiled patterns holds 512 entries, and one turn asks for far more
# distinct ones than that: a knowledge row builds its bounds around its own key words ("\\b" +
# re.escape(word) + "\\b" for every food a meal idea rules out, every word of a word list, every
# row that looks for the thing it names), and each of those is a pattern the engine has not seen.
# Past 512 the table is thrown away whole, so the next call compiles its pattern from scratch:
# a five-line chat made `re` build 9,682 patterns, and the same chat run again built 8,976 more
# because the table had gone in between. A conversation is one process with a fixed vocabulary,
# so the table can hold every pattern a chat can build; with it held, that chat builds its
# patterns once and nothing on the second time round. Nothing a person hears depends on it - a
# compiled pattern matches exactly the lines its string did - and tests/test_lookup_speed.py
# holds that.
try:
    re._MAXCACHE = max(getattr(re, "_MAXCACHE", 512), 16384)
except Exception:  # noqa: BLE001 - a stdlib that keeps its table another way is not our crash
    pass


# The words a line asks with, never a thing a line is about. A key that names one of these as
# its subject ("can", "cans") would otherwise take every line that asks the question, since the
# form of "cans" includes "can": "can i still travel" was answered by the cool-bag card.
ASKING_MODALS = frozenset("can could would should may might must shall will".split())


# The words that follow a modal in a question and never follow a can of drink: "can i still
# travel", "can you keep it cold", "can we take it on the plane".
ASKING_SUBJECTS = frozenset("i you we they he she it u".split())


def _asking_with(typed, at):
    """True when the word at `at` is the line's own question word, not a thing in it."""
    if typed[at] not in ASKING_MODALS:
        return False
    if at + 1 < len(typed) and typed[at + 1] in ASKING_SUBJECTS:
        return True
    # The modal follows its subject instead of opening the question: "whats the cheapest thing i
    # can get", "the best one you can buy". A tin never follows a person that way - "i can" is
    # somebody and a verb - and without this the form of "canned" is the bare word "can", so the
    # frozen-and-tinned row took every line of that shape: "whats the cheapest funeral i can get"
    # and "cheapest thing i can get" were both answered with frozen vegetables.
    return at > 0 and typed[at - 1] in ASKING_SUBJECTS


MIN_SCORE = 4          # below this the line is not really about the entry


# "will", "can" and "should" are mostly verbs. An avoid word is matched loosely, so a bare one in an
# avoid list stands the row down for every "can I ...", "will my ..." or "should I ..." line - which
# is the commonest way a person opens a question. `avoid=("will",)` on the death-and-funeral rows
# meant "will my funeral cost" and "will i lose my photos" got a hedge, and `avoid=("can",)` on the
# tomato row meant "can i keep tomatoes in the fridge" got the generic fridge card. A bare modal in
# an avoid list was never meant as the verb: it is the noun, and these are the phrasings.
MODAL_PHRASES = {
    # the document, not the verb
    "will": ("a will", "my will", "the will", "in the will", "their will", "write a will",
             "will and testament"),
    # a tin, not the modal, and the plural is the same tin
    "can": ("can of", "cans of", "a can", "the can"),
    "cans": ("cans of", "some cans", "two cans", "three cans"),
}


# A feeling said out loud is the subject of the line, not the place it happens in or the thing
# it happens on. The entries keyed on a place are the ones that get this wrong, and the words are
# shared here so each of them can name the same list rather than grow its own: "i keep panicking
# at my desk" is a panic line that says where, and the posture answer ("most bad posture is the
# chair and the sitting still") misreads it as a question about the chair. Only feelings and moods
# belong here - a symptom is a subject of its own ("my back aches at my desk" is a posture line and
# must stay one), and so is a thing ("my chest hurts when i run").
FEELING_WORDS = (
    "panic", "panics", "panicking", "panicky", "panic attack", "panic attacks",
    "anxious", "anxiety", "worried", "worry", "worrying", "worries", "nervous", "on edge",
    "stressed", "stress", "stressing", "overwhelmed", "overwhelming", "freaking out",
    "depressed", "depression", "low mood", "feel low", "feeling low", "feels low", "feeling flat",
    "miserable", "crying", "cry", "tearful", "upset", "dreading", "dread", "hopeless",
    "exhausted", "drained", "burnt out", "burned out", "burnout", "fed up", "cant cope",
    "can't cope", "breaking down", "angry", "anger", "frustrated", "irritable", "snappy",
)


# The words of a question that asks what to do, shared by the entries that answer one. A line
# like "what can i do about my dandruff" says the subject once and spends the rest of the line
# on the ask, so an entry that lists the subject and none of these words never reached it: the
# line scored 2, under MIN_SCORE, and the person got a hedge. These are the ask's own words and
# they name no subject, which is what makes them safe to share between domains: the subject
# still comes from the entry's first key part.
ASK_ABOUT = ("what", "how", "do", "can", "should", "help", "anything", "advice", "tips",
             "get rid", "rid", "stop", "treat", "treatment", "cure", "relief", "relieve", "ease",
             "prevent", "best", "works", "work", "deal with", "cope", "worse", "helps")


# A tooth that has just come out is a wound in the mouth, and almost every word around it is
# another answer's: "cold" is the cold (and the weather), "drink" is the units, "bleeding" is the
# gums, "eat" is when to eat, "jaw" is the click, "dentist" is the complaint about one. On today's
# main "i had a tooth out on tuesday and the gap still aches when i drink anything cold" was
# answered "A cold usually peaks in two or three days", and the person had a hole in their gum.
# So the rows either side stand down on these words and complaints.after-a-tooth-out answers.
# "Where does X come from" asks about the origin of the thing it names, and it is a shape of its
# own: the subject arrives once and the rest of the line is "does it come from". A row that lists
# only the "why/happen/cause" side of a question never reached one - "where does thunder come from"
# scored 2, the subject and nothing else, and went under MIN_SCORE, while "why does it thunder"
# reached the same row. These phrases are the shape and they name no subject, so a row can share
# them without becoming a question about anything else; the subject still comes from the row's own
# first key part. "where does electricity come from" was answered from the consumer unit before
# there was a row keyed on the origin at all.
ORIGIN_ASK = ("come from", "comes from", "came from", "come out of", "comes out of",
              "made from", "made of", "made out of", "made with", "where from",
              "is grown", "grown in", "grows on", "is mined", "is produced")


# A nose that is blocked is not a panic: "my baby cant breathe through her nose" is a cold, and
# the panic rows key on "cant breathe" and would take it. The phrases are the ones a parent
# types, and they say the breath is a nose rather than a lung.
NOT_A_NOSE = ("through my nose", "through your nose", "through his nose", "through her nose",
              "through their nose", "through the nose", "blocked nose", "blocked up nose",
              "stuffy nose", "bunged up nose", "nose is blocked", "nose is stuffy",
              "nose is bunged", "congested nose")


TOOTH_OUT = ("tooth out", "teeth out", "tooth removed", "teeth removed", "tooth pulled",
             "tooth extraction", "extractions", "tooth taken out", "teeth taken out",
             "had a tooth", "had my tooth", "had two teeth", "gap where", "where my tooth",
             "where the tooth", "the socket", "dry socket", "wisdom tooth out",
             "wisdom teeth out", "wisdom tooth removed", "after the extraction",
             "after my extraction", "after a tooth")


# A mouth line is a dental one even when its other words are a cold's: "my teeth hurt when i have
# a cold drink" and "my filling hurts when i drink something cold" were answered by the run-down
# colds row and the eating-when-ill row. Any row whose key carries "cold", "drink" or "eat" stands
# down on these, so the tooth answers keep their own lines.
TOOTH_OR_GUM = ("tooth", "teeth", "toothache", "filling", "fillings", "gum", "gums", "molar",
                "molars", "dentist", "dentists", "dental", "denture", "dentures", "enamel",
                "wisdom tooth", "wisdom teeth", "braces", "mouth ulcer", "gumline")


WORD_WEIGHT = 2


PHRASE_WEIGHT = 3


# A holiday somebody is saving for is a trip they are paying for, not the allowance they are owed
# at work and not a claim against the company that sold it. The two rows that own "holiday" answer
# the other two questions, and both took the saving one: "how much should i save for a holiday" got
# the 5.6 weeks of statutory leave, and "i need 2000 for a holiday how long will it take to save"
# got the 28-day package-travel deadline. The money row that answers a sum by a date says the
# right thing, so these rows stand down on the frame and it answers.
_SAVING_VERB = re.compile(
    r"\b(?:save|saves|saving|saved|put\s+away|putting\s+away|put\s+by|putting\s+by|"
    r"set\s+aside|setting\s+aside|afford|affords|affording)\b", re.I)


# "for a holiday" and not "for the summer": the thing the money is going towards. A number of
# days is not this ("i saved three days of holiday"), which is why the verb alone is not enough.
_SAVING_FOR_A_TRIP = re.compile(
    r"\bfor\s+(?:a|an|the|my|our|their|your|his|her|this|next)?\s*"
    r"(?:holiday|holidays|trip|trips|break|weekend\s+away|city\s+break|getaway)\b", re.I)


# "can i afford a holiday this year" says the paying without a "for": the verb and the trip are
# next to each other and nothing else is being weighed.
_AFFORD_THE_TRIP = re.compile(
    r"\bafford\b[^.;!?]{0,25}?\b(?:holiday|holidays|trip|breaks?|getaway)\b", re.I)


def saving_for_a_trip(understood):
    """False when the holiday in the line is one they are paying for, not one they are owed."""
    line = (understood or {}).get("clean") or (understood or {}).get("text") or ""
    if _AFFORD_THE_TRIP.search(line):
        return False
    return not (_SAVING_VERB.search(line) and _SAVING_FOR_A_TRIP.search(line))


# The improving verb in front of a subject is the ask, not a topic. People say "how do i get
# better at interviews", "how do i improve my mood", "how do i sort out my taxes", "how do i
# interview better" - the subject is named once and the rest of the line is spent on the verb,
# so an entry that lists the subject and none of these answered a line with nothing in it and
# the person got a hedge over an answer that exists.
#
# It goes in the entry's SECOND key part, next to the ask words, so the subject still has to be
# named: "which interview outfit is better" stays the outfit entry's, because the subject there
# is the outfit and "better" is the comparison, and a line naming no subject at all ("how do i
# get better at things") reaches nothing. That is also why `better` on its own is safe here: a
# second part credits one covered word, and this part is only ever read next to a subject part.
# A present asked for is a shopping question, not a how-to. "what can i buy my dad who likes
# fishing" was answered "A new fish needs the tank ready before it goes in", and "idk what to get my
# dad for his 60th, he likes fishing and old films" with the same fish card, because a gift line and
# a hobby line meet at the hobby word and the row that answers how to start the hobby scored first.
# The rows that teach an activity or how to look after an animal take this in their `avoid`, the way
# they already fend off the kitchen and the vet; the shopping rows own the present.
#
# Only the asking shapes, never a bare "get" or "buy": "i bought a new fish what do i need" is a
# care question with a purchase in it, and "how do i get into fishing" is not a present either.
PRESENT_ASK = (
    "gift", "gifts", "present", "presents", "gift idea", "gift ideas", "present idea",
    "present ideas", "christmas present", "christmas gift", "birthday present", "birthday gift",
    "what should i get", "what can i get", "what do i get", "what to get",
    "what should i buy", "what can i buy", "what do i buy", "what to buy",
    "what should i give", "what can i give", "what do i give", "what to give",
    "what would you get", "what would you buy", "what would you give",
    "get him", "get her", "get them", "buy him", "buy her", "buy them", "give him", "give her",
    "for his birthday", "for her birthday", "for their birthday",
    "for his christmas", "for her christmas", "for their christmas",
)


IMPROVE = ("get better at", "better at", "get better", "better", "improve", "improving",
           "improve my", "improvement", "sort out", "sort out my", "sort myself out",
           "work on", "work on my", "get good at", "good at", "get the hang of", "brush up on",
           "practise", "practice", "sharpen up")


# How a person states a complaint as a plain fact about themselves: "im stuffy", "i've got a
# cough", "i feel dizzy". These lines say the subject once and nothing else, so they score 2 and
# stop under MIN_SCORE, and a whole symptom that the knowledge base already answers was going to
# the chat module, which can only sympathise: "im constipated" was answered "Sorry to hear it - go
# easy on yourself today" while the constipation entry sat one word away.
#
# A phrase covers two words of the line, so a report phrase is enough of a second signal. It goes
# in the entry's subject part, next to the subject word, because a part credits only its best
# alternative: the longer wordings ("my nose is stuffy", "how do i stop feeling breathless")
# score exactly as they did before, and only the bare report is added.
# A line can ask the same job two ways and want two different things: "how do i clean the oven"
# is the method and "how often should i clean the oven" is the interval. The rows that hold both
# answers read these words to tell which was asked, so the second sentence of a method card is
# never the answer to a frequency question and the method is never the answer to "how often".
# They live here, in one place, because the tables in cleaning, cars and family all ask it the same
# way, and a row that spelled its own list differently answered some of the lines and not others.
HOW_OFTEN_WORDS = ("how often", "how frequently", "how regularly", "how many times", "often",
                   "frequently", "regularly", "how long between", "every how long", "frequency")


def the_line(understood):
    """The line as the readers read it, lowercased: what a reply callable checks its ask against."""
    understood = understood or {}
    return " ".join(str(understood.get(key) or "")
                    for key in ("clean", "norm_text", "plain")).lower()


def said_text(understood):
    """The line's own words as one string, from whichever reading has them.

    A reading carries `words` and `norm` as *lists*. Joining one is right; taking a list as the
    fallback for a string is not, and it failed quietly in a guard: `understood.get("words") or
    understood.get("norm") or ""` handed a list to `finditer` on a line whose `words` were empty,
    and the TypeError came out of the lookup, so the line lost its answer altogether - "What's
    15% of 80?" got "I don't know enough" while "what is 15% of 80" was fine. This is the one
    place that reads those two keys as text, so a row cannot make that mistake again.
    """
    if not isinstance(understood, dict):
        return ""
    for key in ("words", "norm"):
        taken = understood.get(key)
        if isinstance(taken, str) and taken.strip():
            return taken
        if isinstance(taken, (list, tuple)) and taken:
            return " ".join(str(word) for word in taken)
    return ""


def guard_passes(item, reading):
    """The entry's own test of the reading, run so that a broken one stands only itself down.

    A guard is called from inside the matcher, once per row the line reaches, so an exception in
    it used to take the whole lookup down and the line lost every answer it had, not just this
    row's. A row that cannot read the line is a row that does not answer it.
    """
    guard = getattr(item, "guard", None)
    if guard is None:
        return True
    try:
        return bool(guard(reading))
    except Exception:
        return False


def asks_how_often(understood):
    """True when the line asks the interval rather than the method.

    Takes the reading (`memory["understood"]`) or the line already flattened by `the_line`.
    """
    said = understood if isinstance(understood, str) else the_line(understood)
    return any(word in said for word in HOW_OFTEN_WORDS)


# Sanding is a job, not the bag. A key word is read through its endings, so "sanding" is a row's
# "sand" and "how long do i need to leave filler before sanding" bought a 25kg bag of sand, with a
# lesson in how many square metres it covers. The words cannot go in an avoid list: an avoid word
# is read through its endings too, so "sanding" there stands down every real bag of sand - "how
# much sand for a sandpit", "how much sharp sand under paving slabs" - which is half of the
# material rows. So the verb is read off the line instead: a modal in front of it ("do i need to
# sand", "should i sand it"), the tool ("sander", "sandpaper"), or the job's own words ("sand the
# door", "sand before painting"). Nobody asks for a bag of sand that way.
SANDING_JOB = re.compile(
    r"\bsanding\b|\bsanded\b|\bsandpaper\b|\bsand paper\b|\bsander\b|\bsanders\b"
    r"|\b(?:need|needs|needed|should|must|can|could|shall|will|would|got|better|have to|has to)"
    r"\s+(?:i\s+)?(?:to\s+)?sand\b"
    r"|\bto sand\b|\ba sand\b"
    r"|\bsand (?:it|them|this|that|down|off|back|first|before|after|with"
    r"|the wall|the walls|the wood|the floor|the door|the doors|the ceiling|the trim|the edges?)\b"
    r"|\bfiller\b|\bfilled and sanded\b|\bpolyfilla\b|\bwood filler\b|\bfilling knife\b", re.I)


def a_sanding_job(understood):
    """True when the line is about sanding something down, not about buying a bag of sand.

    Takes the reading (`memory["understood"]`) or the line already flattened by `the_line`.
    """
    said = understood if isinstance(understood, str) else the_line(understood)
    return bool(SANDING_JOB.search(said))


SAID_LEADS = ("im", "i am", "im really", "im so", "im very", "im all", "ive been", "ive got", "i have",
              "i have been", "i feel", "feel", "i keep getting", "i keep being", "i get")


def said(*words, leads=SAID_LEADS):
    """The phrases that make a one-word report of `words` reach an entry.

        entry("blocked-nose", (("nose", "sinuses") + said("stuffy", "bunged up"), (...)),
              "A blocked nose is swollen lining and mucus, so ...")

    so "im stuffy" and "i am bunged up" reach the answer that "my nose is stuffy" already had.
    """
    return tuple(f"{lead} {word}" for word in words for lead in leads)


# The frame around an advice ask: "what should i do about the lawn", "any tips for a hangover",
# "what helps a sore throat", and the same ask put after its subject ("i have a cold sore on my
# lip what helps"). The frame spends the line on the asking, so the subject inside it is the whole
# subject: read on its own, a subject that names an answer outright ("the mould on the ceiling")
# reaches that answer instead of an entry that shares one of the asking words, which is how "what
# can i do about the mould on the ceiling" reached the football boots.
_WRAPPED = (
    re.compile(r"^(?:and |so |ok |okay |hi |hello )?(?:what|anything|something)\s+"
               r"(?:should|can|could|would|do|will|shall)\s+i\s+"
               r"(?:do|use|try|take|put|buy)\s+(?:about|for|on)\s+(?P<subject>\S.*?)\s*\??$"),
    re.compile(r"^(?:and |so )?(?:what|anything)\s+(?:helps|works|is good)\s+"
               r"(?:for\s+|with\s+)?(?P<subject>\S.*?)\s*\??$"),
    re.compile(r"^(?:and |so )?(?:any|some|got any|have you got any|do you have any)\s+"
               r"(?:tips|advice|suggestions|ideas)\s+(?:for|on|with|about)\s+(?P<subject>\S.*?)\s*\??$"),
    re.compile(r"^(?P<subject>\S.*?)[,;:]?\s+(?:what|anything)\s+(?:helps|works)\s*\??$"),
)


# Words that say nothing about what the ask is about, so a wrapper that carries only these has no
# subject to look up ("what should i do about it" is a follow-up, and the conversation has it).
_NOT_A_SUBJECT = frozenset(
    "a an the my your our their his her its it that this these those me us him them someone "
    "anyone everyone something anything nothing more less best good now then here there".split())


# A wrapper whose subject is really an idiom: "what do i do for a living" asks about their job,
# and "what helps for good" asks nothing at all.
_NOT_A_THING = frozenset(("a living", "a go", "a bit", "a while", "a change", "the best",
                          "my best", "a start", "the same", "a look", "a hand", "a try",
                          "a break", "a rest", "for good", "the day", "the weekend",
                          "it", "that", "this", "them", "anything"))


# The entries whose subject is one everyday noun and nothing else - a lawn, slugs, limescale, the
# condensation, snoring - and whose line therefore spends its other words on the asking. They are
# named here, in one place, because being asked about is a property of the entry, not of the
# domain it sits in: the ask around the subject is the second signal the one word cannot give.
# Any other entry keeps the two-word rule, so a word that only brushes past a key ("fly" for a
# fruit fly in "my fear of flying") can never answer on the strength of the ask.
ASK_FRAME_IDS = frozenset("""
    condensation damp limescale slug-control snoring snore-less hangover sore-throat
    sleep-trouble
    """.split())


# The words that turn the word after them into a description of the thing wanted rather than a
# name for a subject of its own: "im after something light" asks for a light film, not for the
# physics of light. Every one of them is an indefinite pronoun, which stands in front of an
# adjective and nothing else, so a subject that appears only behind one is not what the line is
# about. "what should i watch tonight, something light" was answered with photons, and "any good
# films out, something light" with the lighting circuit at the consumer unit.
AS_A_KIND = frozenset("something anything nothing everything".split())


MIN_TYPO_LENGTH = 4    # a three-letter word is a slip away from half the language


# "Ring" is a verb as well as a noun, and the verb is the commoner of the two by a long way. Every
# card keyed on the noun - a ring stuck on a finger, a ring on a hob, a ring that has gone dull -
# shares this list, because the same two words mean a phone call: "my ring is stuck" is the finger
# and "should i ring in sick" is work. Two of the shapes stood no chance of a guard on their own:
# the verb with no object after it ("ring in", "ring ahead"), and a line that carries its subject
# over from the turn before, which is how "i have a cold sore" then "should i ring in sick" got
# soap and dental floss - the carry-over met the two-signal rule with "cold sore".
# Read with loose forms, so "ringing the dentist" and "i rang the bank" are the same shape.
RING_AS_A_CALL = (
    "ring the", "ring my", "ring him", "ring her", "ring them", "ring you", "ring me",
    "ring someone", "ring somebody", "ring anyone", "ring anybody", "ring people",
    "ringing someone", "ringing somebody", "ringing people", "rang someone", "rang somebody",
    "ring a", "ring an", "ring about", "ring back", "ring up", "ring round", "ring around",
    "ring for", "ring to", "ring at", "ring and", "ring later", "ring tomorrow",
    "ring in", "ring sick", "ring ahead", "ring work", "ring first thing",
    "ring first", "ring instead", "ring again", "to ring", "should ring", "will ring",
    "can ring", "could ring", "would ring", "might ring", "must ring", "need to ring",
    "have to ring", "give a ring", "give her a ring", "give him a ring", "give them a ring",
    "give me a ring", "a ring round")


# The endings that make one word a form of another, so "radiaters" is one answer
# ("radiator", "radiators") rather than two, and a slip is not called ambiguous.
ENDINGS = ("iness", "iest", "ings", "ing", "ies", "ied", "ier", "ers", "est", "er",
           "es", "ed", "ly", "s", "y", "ness", "ful")


MIN_FORM = 3           # a loose form shorter than this is not the same word (weeing -> we)


class Entry:
    """One fact or piece of advice, keyed by the meaning of a line."""

    __slots__ = ("id", "key", "reply", "avoid", "bias", "ask", "slips", "domain", "fault",
                 "report", "guard", "shape", "explain", "lead", "outcomes")

    def __init__(self, id, key, reply, avoid=(), bias=0, ask=(), slips=(), fault=False,
                 report=False, guard=None, shape=(), explain=False, lead="", outcomes=()):
        self.id = id
        self.key = tuple(key)
        self.reply = reply
        self.avoid = tuple(avoid)
        self.bias = bias
        self.ask = tuple(ask)
        self.slips = tuple(slips)
        self.domain = ""
        # True when the answer is about the appliance itself rather than a dish cooked in it.
        # "My oven will not heat up" says the oven is not working, and a cooking answer that
        # needs an oven is no use to it - but the oven's own repair answer is exactly right,
        # so it is not held out by the same check.
        self.fault = fault
        # True when naming the complaint in the first person is the whole question. A symptom
        # is not asked about: "i have tinnitus", "ive got heartburn", "i have a bunion" say the
        # subject once and nothing else, so they score on one position and get a chat nod
        # ("Noted: you have tinnitus") while the answer sits one word away. Only rows that
        # answer a complaint opt in, because "i have a dog" is not a question about keeping one.
        self.report = report
        # An optional test of the whole reading, for an entry that is only an answer when
        # something in the line is not what its own key says: "the table leg is cracked" has
        # a skin state beside a body part, but the part belongs to the table, so the dry-skin
        # entry must stand aside for the repair. The test is a function of `understood`, so
        # the words stay in the knowledge base and the reading comes from the understanding
        # engine, the way `thing_state` reads `state_owner`.
        self.guard = guard
        # True when a figure in the line, read as a shape rather than as a word, is the second
        # signal the entry needs. Some keys are a list of the figures people type - the phone on
        # 2%, 1%, 5% - and the list can never hold every number: "my phone is on 4%" reached no
        # entry at all and was acknowledged back at the person. A shape says what the figure is
        # (a percentage at or below 20%), so one row answers the whole family. Only the entries
        # whose subject is already named count on it, and it is worth exactly one key word, like
        # `report`, so a figure alone still never answers a line.
        self.shape = tuple(shape)
        # True when a plain request to explain the subject is a question the row answers. The
        # plainest way people ask for a fact names it and asks nothing else - "what is sepsis",
        # "tell me about gout", "explain shingles" - so the line has one word of the row's key
        # and the row never comes within reach of it (the scorer wants two signals) and a chat
        # nod or a search hedge takes the turn. A row that answers a named thing opts in,
        # because "what is the best way to clean a sofa" is not a request to explain a sofa and
        # only a row whose subject is the thing asked about can read it as one.
        self.explain = explain
        # The sentence this row owes a line that asks a question of one shape, in the row's own
        # words: "Usually, yes" for the side-effects card, which opens on the leaflet and reaches
        # the verdict two sentences later. `bot/compose/lead.py::answer_first` puts it in front
        # when the line wants the shape it gives, and leaves the row alone on every other line,
        # so one field serves every shape and every domain without a word of the card changing.
        self.lead = lead
        # The sentence this row owes a line that asks how its subject turns out, when the card
        # itself is already on screen: ("survives", "Yes, if you do not switch it on: most phones
        # that get wet come back once they are dried out."). A follow-up like "will it be
        # alright" after the phone went in the sink names no subject of its own, so the only
        # answer is the row's, and the row's answer has been given already - read out again it
        # repeats a paragraph the person is looking at, and the turn used to give up and point
        # them at a search instead, over a subject the bot had just answered. The shapes are the
        # ones `bot/memory/narrow.the_outcome_asked` reads ("survives", "serious", "next",
        # "explain"), so the same reading decides which sentence is owed.
        self.outcomes = tuple(outcomes)

    def __repr__(self):
        return f"<Entry {self.id}>"


# "my back fence", "the back door", "back garden": a fence, a door and a garden are all "back"
# something, and "back" is the house far more often than it is a spine. A key that needs two
# signals can take one from the line above - and a turn that carries the last line along says
# both at once: "the dog keeps digging under it, my back fence is rotten on one side" was answered
# with the manual-handling card ("Bend at the hips and knees rather than the waist..."). The row
# is right about a spine and wrong about a fence, so the place words are the fence.
PLACES_AFTER_BACK = (r"door|doors|fence|fences|gate|gates|gatepost|gateposts|garden|gardens|"
                     r"room|rooms|seat|seats|window|windows|wall|walls|yard|porch|lawn|path|"
                     r"pathway|step|steps|stairs|packet|packets|pocket|pockets|burner|burners|"
                     r"boiler|panel|panels|bed|beds|alley|bridge|road|lane|field|fields|"
                     r"paddock|plot|car|van|shed|garage|drive|driveway|garden")


BACK_OF_THE_HOUSE = re.compile(r"\bback\s+(?:%s)\b" % PLACES_AFTER_BACK)


# A back spoken about as a back: "my back", "the lower back", "a bad back", "his back".
THE_BACK_ITSELF = re.compile(
    r"\b(?:my|your|his|her|their|our|the|lower|upper|sore|stiff|aching|aching|bad|old)\s+"
    r"back\b(?!\s+(?:%s)\b)" % PLACES_AFTER_BACK)


# The household appliances whose own name can contain the name of one of their parts. "Heat pump"
# is the thing in the garden and the thing inside a tumble dryer; "fan" is an oven's, a car's and a
# desk's; "pump" is a pool's and a shower's. A row that answers the part, or the house system, has
# to stand down when the appliance's own name swallows the row's name, and the appliance's row then
# answers: "how much does a heat pump dryer cost" is a dryer's price, not a heat pump's. The test is
# the appliance phrase against the row's own names, so a plumber fitting a dishwasher is untouched.
APPLIANCE_NAMES = (
    "tumble dryer", "washer dryer", "heat pump dryer", "condenser dryer", "vented dryer",
    "washing machine", "fridge freezer", "fish tank", "pool pump", "shower pump", "fan oven",
    "microwave", "dishwasher", "dryer", "fridge", "freezer", "oven", "cooker", "hob", "kettle",
    "toaster", "vacuum", "hoover", "mower", "lawnmower", "strimmer", "radiator", "boiler",
    "car", "van", "motorbike", "bike", "bicycle", "aquarium", "hot tub")


def the_appliance_swallows_the_name(understood, names):
    """True when a named appliance contains one of `names` in its own name.

    "how much does a heat pump dryer cost" names the appliance `heat pump dryer`, which holds the
    row's name `heat pump`: the dryer's price is the question. "how much does a plumber charge to
    fit a dishwasher" names an appliance the row's names are not inside, so the plumber's price
    keeps its line.
    """
    parts = [str((understood or {}).get(part) or "") for part in ("clean", "text", "norm")]
    said = " " + " ".join(parts).lower() + " "
    names = [str(name).lower() for name in (names or ()) if str(name or "").strip()]
    if not names:
        return False
    for appliance in APPLIANCE_NAMES:
        if not re.search(r"(?<![a-z0-9])" + re.escape(appliance) + r"(?![a-z0-9])", said):
            continue
        # The row's own name has to be a part of the appliance's name, not the whole of it: a
        # boiler is the boiler and must keep its price, while "heat pump" inside "heat pump dryer"
        # is a dryer's part.
        if any(name in appliance and len(name) < len(appliance) for name in names):
            return True
    return False


def the_back_is_a_body_part(understood):
    """False when every "back" in the two lines is part of the house or the car.

    "my back fence is rotten" then "the dog keeps digging under it" is a fence question, and the
    manual-handling card is the wrong answer to it. A line that names the back itself - "my back
    hurts", "the lower back", "a bad back" - keeps its answer whatever came before.
    """
    said = str((understood or {}).get("text") or "").lower()
    above = str(((understood or {}).get("leans_on") or {}).get("text") or "").lower()
    both = said + " " + above
    if not BACK_OF_THE_HOUSE.search(both):
        return True
    return bool(THE_BACK_ITSELF.search(both))


def _avoid_words(parts):
    """The avoid list as a flat tuple of words.

    A module often shares these as a constant ("INFANT_RED_FLAGS"), and dropping that tuple into
    avoid= instead of adding it made an entry whose words were a tuple, which no word of a line
    can ever equal; the matcher only broke when it reached for the text of one. Flatten at the
    door, so a shared constant works whether it is added or nested, and so nothing that is not a
    word can reach the matcher.
    """
    flat = []
    for part in parts:
        if isinstance(part, str):
            # See MODAL_PHRASES: a bare modal is the noun, so it is expanded here rather than in
            # every domain that listed one, and a row added tomorrow is right without anyone
            # remembering to write the phrasing down.
            flat.extend(MODAL_PHRASES.get(part, (part,)))
        elif isinstance(part, (list, tuple, set, frozenset)):
            flat.extend(_avoid_words(part))
    return tuple(flat)


# --- he, she or they -------------------------------------------------------------------
# Some answers are about a second person: a present being chosen for someone, a cat that pushes
# things off the shelf. Writing "he" or "she" into the reply means the entry says the wrong word
# for half the people who reach it, and an entry is chosen by the thing it is about (the hobby, the
# animal), not by the person: "a present for my dad who's into gardening" was answered "She has
# told you what she likes", and "my tom cat keeps knocking things off the table" was answered
# "She is not being naughty". A reply built by about_them() reads the person off the line instead.
PEOPLE_MALE = ("dad", "father", "grandad", "grandpa", "grandfather", "stepdad", "brother",
               "husband", "boyfriend", "son", "uncle", "nephew", "bloke", "fella", "guy",
               "he", "him", "his")


PEOPLE_FEMALE = ("mum", "mother", "mam", "nan", "nana", "gran", "granny", "grandma",
                 "grandmother", "stepmum", "sister", "wife", "girlfriend", "daughter", "aunt",
                 "niece", "she", "her", "hers")


def about_them(template, male=PEOPLE_MALE, female=PEOPLE_FEMALE):
    """An Entry reply that says he, she or they according to the line.

    template uses {they} {them} {their} for the words and {has} {is} {likes} {loves} {self} for
    the verb and reflexive forms, so the same sentences work for one person, for a man, for a
    woman, and for a line that names nobody ("a present for someone into gardening" is "they").
    The first letter is capitalised so a template can be written the way it reads.
    """
    def reply(memory, reading):
        words = reading.get("words") or ()
        they = "they"
        for word in words:                      # a relation beats a stray pronoun
            if word in male:
                they = "he"
                break
            if word in female:
                they = "she"
                break
        plural = they == "they"
        fills = (("{they}", they),
                 ("{them}", "them" if plural else ("him" if they == "he" else "her")),
                 ("{their}", "their" if plural else ("his" if they == "he" else "her")),
                 ("{self}", "themselves" if plural else ("himself" if they == "he" else "herself")),
                 ("{has}", "have" if plural else "has"),
                 ("{is}", "are" if plural else "is"),
                 ("{likes}", "like" if plural else "likes"),
                 ("{loves}", "love" if plural else "loves"))
        out = template
        for token, word in fills:
            out = out.replace(token, word)
        return out[:1].upper() + out[1:]
    return reply


# --- the shape of the ask ------------------------------------------------------------------
# The ways people ask where to get a thing that carry no question word of their own. "cheapest
# place to buy a freezer" and "best place to buy a kettle" name no place in the matcher's sense
# and ask nothing the reading calls `where`, but a place is what they want. This is not the
# shopping domain's key list, which is wider on purpose: that row also answers "cheapest
# freezer" and "best price on a fridge", where the person is comparing prices and a place is a
# reasonable answer. The guard below is narrower, because it stands a row aside: only the
# phrases that ask for a place count, so "which dishwasher is the cheapest to run" is left to
# the running-cost row.
WHERE_PHRASES = ("where to buy", "where can i buy", "where should i buy", "where do i buy",
                 "where to get", "where can i get", "where should i get", "where do i get",
                 "cheapest place", "cheapest shop", "best place to buy", "which shop",
                 "what shop", "who sells", "where sells")


# The things the price-comparison answer is written for: something sold as a model, with a
# warranty and a price history to compare. `shopping.where-to-buy-cheapest` builds its thing arm
# from this list and the verdict rows below stand aside from a place question about one of them,
# so the answer and the stand-aside cannot drift apart. A thing that is not here keeps its verdict
# rather than being left with nothing: the generic advice ("refurbished or graded stock", "ex
# display") is written for a machine, and a weighted blanket is not one.
PRICE_COMPARED = ("fridge", "freezer", "fridge freezer", "washing machine", "washer dryer",
                  "tumble dryer", "dishwasher", "oven", "hob", "microwave", "kettle", "toaster",
                  "hoover", "vacuum", "tv", "television", "laptop", "phone", "tablet", "sofa",
                  "bed", "mattress", "wardrobe", "pram", "pushchair", "car seat", "bike",
                  "boiler", "mower", "lawnmower")


def asks_where(understood):
    """True when the line asks where to get something, which is a place and not a verdict.

    "Where can i buy a cheap freezer" and "cheapest place to buy a tumble dryer" ask the same
    question as "where can i buy a kettle", and the shopping domain's `where-to-buy-cheapest`
    answers all three. The verdict rows never saw them: an appliance name and the bare word
    "buy" are all those need, so a freezer was told it is worth it if you use it three times a
    week, and a dryer the trade on dryers. A place is what the person asked for, so this is
    what stands a verdict aside - the reading's own `where`, and the buying-place phrases for
    the people who ask it without saying where.
    """
    if "where" in tuple((understood or {}).get("asks") or ()):
        return True
    words = (understood or {}).get("words") or ()
    text = " " + " ".join(str(word) for word in words).lower() + " "
    return any(phrase in text for phrase in WHERE_PHRASES)


# The pieces of a machine that are sold on their own: a door seal, a filter, a basket, an element.
# The price answer is written for the machine ("compare the exact model ... refurbished or graded
# stock with a real warranty"), and none of that is advice about a part. The part rows answer these
# where they exist, and where they do not, the verdict on owning the thing is what main says, and a
# verdict is no worse than advice about a warranty.
WHERE_PART_WORDS = ("spare", "spares", "part", "parts", "replacement", "door", "doors", "seal",
                    "seals", "gasket", "filter", "filters", "basket", "baskets", "tray", "trays",
                    "drawer", "drawers", "shelf", "shelves", "handle", "handles", "hinge",
                    "hinges", "lid", "lids", "element", "elements", "drum", "drums", "belt",
                    "belts", "pump", "pumps", "motor", "motors", "fan", "fans", "blade", "blades",
                    "brush", "brushes", "hose", "hoses", "pipe", "pipes", "knob", "knobs", "bulb",
                    "bulbs", "thermostat", "compressor", "descaler", "descale", "limescale")


def asks_where_a_shop_answers(understood):
    """True when the line asks where to get one of the things the price answer is written for.

    This is the guard the verdict rows use, and it is the same test the buying row applies to
    itself, so a verdict only steps aside when a better answer really takes the line. Asking where
    is not enough on its own: standing a verdict aside for a thing the buying row does not name
    left the person with a shrug, or with whatever unrelated row scored next ("where can i buy a
    coffee machine" was told to compare the price per kilo).

    A part is not the thing: "where can i buy a hoover filter" and "where do i get a new oven
    element" are pieces, and advice about comparing models, warranties and ex-display stock is
    written for the machine. The same goes for a bare follow-up: "where do i get one" three turns
    into a fridge door seal is the seal, so what the reading resolved it to has to end in one of
    these things - "tumble dryer" does, "fridge door" does not.
    """
    if not asks_where(understood):
        return False
    words = [str(word).lower() for word in ((understood or {}).get("words") or ())]
    if any(word in WHERE_PART_WORDS for word in words):
        return False
    text = " " + " ".join(words) + " "
    if any(thing in text for thing in PRICE_COMPARED):
        return True
    ref = str((((understood or {}).get("ref") or {}).get("it")) or "").strip().lower()
    if not ref:
        # "where do i get one" on its own names nothing at all: the buying row cannot know what
        # "one" is, so the rows that read the conversation keep the line
        return False
    return any(ref == thing or ref.endswith(" " + thing) for thing in PRICE_COMPARED)


# --- the thing that is broken ----------------------------------------------------------
# A repair answer is reached by the words landlord and broken whatever is broken, so the thing
# itself has to come off the line: "my washing machine is broken and the landlord wont fix it" was
# answered with a letter reading "The boiler has been broken since Tuesday and we have no hot
# water", and a toilet and a shower got that boiler too. A letter that names the wrong thing is
# worse than no letter, because it is the one message the person copies and sends. The words here
# are the faults people bring to a landlord, longest first, so "washing machine" does not become
# "machine" and "hot water" is not read as a shower.
THE_FAULT = (("washing machine", "washing machine"), ("tumble dryer", "tumble dryer"),
             ("tumble drier", "tumble dryer"), ("spin dryer", "tumble dryer"),
             ("dishwasher", "dishwasher"), ("fridge freezer", "fridge freezer"),
             ("fridge", "fridge"), ("freezer", "freezer"), ("microwave", "microwave"),
             ("cooker", "cooker"), ("oven", "oven"), ("hob", "hob"),
             ("central heating", "central heating"), ("heating", "heating"),
             ("hot water", "hot water"), ("radiators", "radiators"),
             ("radiator", "radiator"), ("boiler", "boiler"),
             ("shower", "shower"), ("bath", "bath"), ("toilet", "toilet"), ("loo", "toilet"),
             ("extractor fan", "extractor fan"), ("smoke alarm", "smoke alarm"),
             ("front door", "front door"), ("letterbox", "letterbox"),
             ("intercom", "intercom"), ("window frame", "window"), ("window", "window"),
             ("roof", "roof"), ("guttering", "gutter"), ("gutter", "gutter"),
             ("chimney", "chimney"), ("damp patch", "damp"), ("damp", "damp"),
             ("mould", "mould"), ("mold", "mould"), ("condensation", "condensation"),
             ("leak", "leak"), ("electrics", "electrics"), ("electric", "electrics"),
             ("plug socket", "socket"), ("socket", "socket"), ("lights", "lights"),
             ("light", "light"), ("tap", "tap"), ("sink", "sink"), ("drains", "drain"),
             ("drain", "drain"), ("pipes", "pipes"), ("pipe", "pipe"),
             ("stairs", "stairs"), ("ceiling", "ceiling"), ("floor", "floor"),
             ("wall", "wall"), ("fence", "fence"), ("lock", "lock"), ("garden", "garden"),
             ("garage", "garage"))


# A pattern that finds a phrase as a whole word, compiled once for each phrase it is asked
# about. `re.search` compiles and caches its own patterns, but the cache is 512 entries and the
# knowledge base asks about thousands of phrases, so every other question re-compiled the
# pattern: on a random deck turn that was a fifth of the reply. The patterns are built from
# module-level words, so the card holds a few thousand and never grows with a conversation.
_BOUNDED = {}


_BOUNDED_KEEP = 40000


def _bounded(name):
    """The compiled pattern finding `name` as a whole word, worked out once for the phrase."""
    got = _BOUNDED.get(name)
    if got is not None:
        return got
    got = re.compile(r"(?<![a-z0-9])" + re.escape(name) + r"(?![a-z0-9])")
    if len(_BOUNDED) >= _BOUNDED_KEEP:
        _BOUNDED.clear()        # a card of patterns, not a leak; the next turn fills it again
    _BOUNDED[name] = got
    return got


def the_fault(template, when_unnamed, table=THE_FAULT):
    """An Entry reply that names the broken thing the person actually said.

    template carries {fault}, which becomes the noun from `table` that the line names, so a
    letter, a first check or a "who to call" answer can be about the person's own problem.
    `when_unnamed` is used instead when the line names no thing at all ("the landlord is ignoring
    me about repairs"). The generic words are deliberately not in the table: "repair", "fault" and
    "everything" are longer than "damp" and "oven", so they would win on a line that names both,
    and a letter about "the repairs" is the vagueness the person already had. Longest word first, and only the first fault named, because the
    letter quotes one and the person adds the rest.
    """
    wanted = [(re.compile(r"\b" + re.escape(word) + r"\b"), noun)
              for word, noun in sorted(table, key=lambda pair: len(pair[0]), reverse=True)]

    def reply(memory, reading):
        line = str(reading.get("text") or reading.get("clean") or "").lower()
        for pattern, noun in wanted:
            if pattern.search(line):
                return template.replace("{fault}", noun)
        return when_unnamed
    return reply


# A "how long" line can be about three different clocks: the appliance's life ("how long does a
# boiler last"), the appliance's own minute or two ("how long does a kettle take to boil"), or the
# job ("how long does a boiler repair take"). The job's words live here because every clock-asking
# entry was answering a repair question with its own numbers - a boiler's ten to fifteen years, a
# kettle's three minutes, and the fridge's three to four days for "how long does a fridge repair
# take" (urban-orange, quality). An entry whose key is a clock adds this to its avoid, and the job
# has the row that answers it.
# --- a food named in the line is a food question ----------------------------------------
# The words below are the food a line talks about, for the rows that are not about food at
# all: a nail row, a tin of paint. "my sourdough starter smells like nail varnish remover"
# carries nail, varnish and remover, so the nail-art row taught it two thin coats, and the
# paint-smell row answered it next. Both now stand down when the line names a food, which is
# what every real nail and every real painted wall is missing.
FOOD_SUBJECT = ("sourdough", "starter", "kombucha", "kefir", "ferment", "fermented",
                "fermenting", "hooch", "dough", "bread", "beer", "wine", "vinegar", "pickle",
                "yoghurt", "yogurt", "milk", "cheese", "butter", "meat", "chicken", "fish",
                "rice", "pasta", "potato", "potatoes", "food", "foods", "drink", "drinks",
                "juice", "curry", "stew", "soup", "cake", "biscuit", "biscuits")


# "my kettle has gone" is the same fault as "my kettle is broken": the thing is dead and the
# person has not said how. "Gone" is also what a colour, a picture or a smell does - "the telly
# has gone black", "the milk has gone off", "the soup went cold" - so the word is the thing's
# fault only where it is the whole of what the thing did, with nothing describing after it.
# The words after it that describe rather than name the fault: they hand the line back to the
# colour, the picture, the food and the heating rows, which are the ones that answer them.
HAS_GONE = re.compile(r"\b(?:has|have|had|'s|s|is|was)\s+(?:gone|went)\b(.*)$")


# A word that only says how much: "the kettle's gone all white inside" is the scale, not the
# element, and "gone really quiet" is a fan. The word after it is the one that decides.
GONE_INTENSIFIER = frozenset("""all a an really very so quite proper totally completely kind sort
    bit little lot bit too pretty well""".split())


GONE_STATE = frozenset("""black white blue green grey gray red pink yellow orange purple brown
    rusty fuzzy blurry funny fuzzy quiet noisy loud silent still cold hot warm cool dark dim
    blank off bad worse flat dead solid hard soft sticky lumpy dry wet sour mouldy stale numb
    bright pale gold silver cracked wet""".split())


# --- a machine that stopped is not a person who stopped working -----------------
# "stopped working" is the phrase for a machine that died and for a person who gave up their job,
# and the row about the year after work stops was reading both: "my oven has stopped working,
# what do i do" was answered with "That lost feeling is the usual thing and it has a shape", and
# the plug-and-fuse answer to the same line never got a hearing. The words cannot tell the two
# apart, because they are the same words; what tells them apart is the thing the line is about.
# The reading already types the nouns in it, so the test is on that type and on the phrase
# together, and no list of machines is kept here: the next machine somebody names is covered.
STOPPED_WORKING = ("stopped working", "stopped work", "stops working", "not working",
                   "isnt working", "isn't working", "packed in", "wont work", "won't work",
                   "wont start", "won't start", "wont come on", "won't come on",
                   "dead", "died", "has gone")


def a_thing_has_stopped(understood):
    """True when what stopped working is a thing in the line, not the person saying it.

    For "my oven has stopped working, what do i do" and "the washing machine has packed in" the
    subject is the machine, and the answer is the plug, the fuse and the door switch. For "i have
    stopped working", "i gave up work" and "im retired and feel lost" there is no thing in the
    line, so nothing is taken away from the rows about a person's own working life. A machine the
    person only mentions in passing ("i lost my job and the oven has stopped working") is not the
    subject and does not count, because the subject has to be one of the things named.
    """
    reading = understood if isinstance(understood, dict) else {}
    words = " ".join(str(word) for word in (reading.get("norm") or reading.get("words") or ()))
    line = " " + (words or str(reading.get("clean") or reading.get("text") or "")).lower() + " "
    line = line.replace(" | ", " ").replace("|", " ")
    if not any(" %s " % phrase in line for phrase in STOPPED_WORKING):
        return False
    things = [str(entity.get("text") or "").lower()
              for entity in (reading.get("entities") or ())
              if isinstance(entity, dict) and entity.get("type") == "thing"]
    if not things:
        return False
    subject = str(reading.get("subject") or "").lower()
    if not subject:
        return True
    return any(thing and (thing in subject or subject in thing) for thing in things)


def the_thing_has_gone(understood):
    """Whether "gone"/"went" is what the thing did, rather than the state it went into.

    True for "my washing machine has gone and it is not a year old", "the seal on my fridge door
    has gone" and "my kettle's gone"; false for "the telly has gone black", "the milk has gone
    off", "the soup went cold" and "the picture has gone funny", which name what came after, and
    false for "we went out and left the stew on the hob", which is nobody's fault.
    """
    reading = understood if isinstance(understood, dict) else {}
    said = [str(word).lower() for word in (reading.get("words") or [])]
    line = " " + " ".join(said) + " "
    if not said:
        line = " " + str(reading.get("clean") or reading.get("text") or "").lower() + " "
    after_gone = [found.group(1) for found in HAS_GONE.finditer(line)]
    for tail in after_gone:
        words = [word.strip("'.,!?") for word in tail.split()]
        words = [word for word in words if word]
        while words and words[0] in GONE_INTENSIFIER:
            words.pop(0)
        if not words or words[0] not in GONE_STATE:
            return True
    return False


# --- the food is what has gone off -----------------------------------------------
# "my chicken smells a bit, can i cook it" is a food-safety question, and the answers that were
# given were the ones that read the smell, not the food: the kitchen-smell row opened a window and
# simmered a pan of lemon ("cooking" and "smells" are two of its key words), and the chicken
# nutrition row answered "is my chicken still ok to eat" with what is in a chicken. Both are good
# answers to other lines. The rule they were missing is one sentence - when the line says the food
# it names has gone off, it is asking whether that food is still all right - and it belongs to the
# food, so it is written once here and `bot/knowledge/still_ok.py`'s rows answer it.
FOOD_NAMED = FOOD_SUBJECT + (
    "ham", "bacon", "sausage", "sausages", "beef", "pork", "lamb", "mince", "steak",
    "turkey", "salmon", "cod", "haddock", "tuna", "prawn", "prawns", "egg", "eggs",
    "tofu", "beans", "lentils", "leftover", "leftovers", "fruit", "berries", "veg",
    "vegetables", "salad", "gravy", "stew", "curry", "soup", "rice", "pasta",
    "noodles", "sandwich", "mayo", "mayonnaise", "cream", "custard", "pie", "quiche",
    "dinner", "lunch", "supper")


# How a food that has gone off is said to be gone, in two parts, because the verb alone does not
# say which way it went: "my chicken smells" is a complaint and "my roast chicken smells great" is
# not. So a smell is only the first half of it - the second half is what is said of the smell (or
# that nothing is said at all, which is the complaint: "my chicken smells, can i cook it").
SMELL_VERBS = frozenset(("smell", "smells", "smelled", "smelt", "smelling", "smelly",
                         "stink", "stinks", "stank", "stinking"))


# Said of the food itself, the state words are the whole question: "the milk has gone sour", "the
# ham looks slimy".
# The words between a food and "bad" that make it the food's condition rather than a verdict on
# it: "the ham has gone bad", "this chicken smells bad", "my milk is bad". They are the state
# verbs BEFORE_OFF already skips, plus the smell verbs that go with "bad" as their ending.
_BAD_IS_A_STATE = frozenset((
    "has", "have", "had", "is", "was", "are", "were", "been", "be", "being", "got", "gets",
    "getting", "gone", "went", "go", "goes", "going", "looks", "looked", "looking",
    "tastes", "tasted", "tasting", "smells", "smelled", "smelt", "smelling", "smelling"))


OFF_SAID_OF_FOOD = frozenset((
    "sour", "soured", "souring", "slimy", "slime", "tacky", "sticky", "mouldy", "moldy",
    "rancid", "curdled", "curdling", "rotten", "putrid", "funny", "bad", "dodgy", "grey",
    "fizzy", "bubbling", "discoloured", "discolored", "off"))


# A smell said to be a good one, or a comparison rather than a fault: "my roast chicken smells
# great", "my curry smells amazing", "my chicken smells of garlic". None of them is a question
# about whether the food is still all right, and a spoilage card given to one is an insult to
# dinner.
A_GOOD_SMELL = frozenset((
    "great", "good", "amazing", "lovely", "nice", "delicious", "fine", "wonderful",
    "fantastic", "incredible", "tasty", "better", "perfect", "heavenly", "divine", "ok",
    "okay", "alright", "lush", "yummy", "appetising", "appetizing", "gorgeous", "brilliant",
    "of", "like"))


# The few words a line puts between a food and how it has gone: "the milk has gone sour", "the
# chicken looks a bit grey". Anything else ends the search, so "chicken and rice smells" is the
# rice's smell and not the chicken's.
BEFORE_OFF = frozenset((
    "has", "have", "had", "is", "was", "are", "were", "been", "be", "being", "got",
    "gets", "getting", "gone", "went", "go", "goes", "going", "looks", "looked",
    "looking", "tastes", "tasted", "the", "my", "a", "an", "bit", "little",
    "now", "and", "just", "really", "very", "so", "still", "quite", "definitely",
    "starting", "to", "on", "properly", "seriously"))


# The same question asked without a word for a smell: "is my chicken still ok to eat", "has the
# ham gone off", "is this beef out of date". Each of these is a phrase rather than a word, and a
# food word still has to be in the line, so "is the wifi still ok" reaches nothing here. A bare
# "ok to eat" is not on this list on purpose: "is it ok to eat 2 eggs a day" is a diet question.
OFF_STATE_ASKS = ("still ok", "still okay", "still good", "still fine", "still safe",
                  "still alright", "still all right", "still edible", "gone off",
                  "going off", "gone bad", "went off", "gone past", "gone sour",
                  "gone mouldy", "gone slimy", "out of date", "past its date",
                  "past the date", "past their date", "use by", "best before",
                  "is off", "smells off", "are off", "smell off")


JOB_GUARD = ("repair", "repairs", "repaired", "repairing", "fix", "fixes", "fixed", "fixing",
             "install", "installs", "installed", "installing", "installation", "fit", "fits",
             "fitted", "fitting", "engineer", "engineers", "plumber", "plumbers", "callout",
             "call out", "call-out", "come out", "coming out", "swap", "swapping")


# "flat" is the word for a home and the word for a bake, a head of hair, a tyre and a note of
# music, and every row that keys one of those answers the others when the line is about where
# somebody lives: "my flat gets damp in winter" was the volume card (dry the hair upside down),
# "the flat gets baking in summer" the flat-bake card and "my flat gets cold" the run-of-colds
# card. The determiner is the difference - "my flat", "the flat", "in a flat" is a home, while a
# bare "flat" after hair, scone or tyre is not.
#
# It is a guard and not a word in the avoid list because an avoid phrase is read loosely: the
# words only have to be in the line, in any order and apart, so "my flat" in an avoid list threw
# away "my scones came out flat" and "my hair looks flat" - the very lines these rows are for.
# The guard reads the line itself, where the two words have to be next to each other.
#
# A verb of moving, renting or buying in front of the bare word is the same signal as the
# determiner: "we want to move flat before winter" has no "the" in it and still names a home,
# and it reached the seasonal-mood card while "we want to move the flat" did not - one word
# apart, opposite answers. "get my flat sorted" is the same home said as a job to do.
# "money off" is two things and the words that settle it are in the line: a discount on a thing
# ("money off a sofa", "money off my holiday") or money leaving a person ("money off my mum"). A
# borrowing word settles it, and so does a person after "off". No price conversation has either
# in it, so one test stands every price row aside and they all get the loan lines right together:
# six of seven `should i / can i / how do i borrow money off my <relative>` lines were answered
# with a shop's till script ("ask the person who can say yes, not the till ... offer about two
# thirds and settle in the middle") because a bare "money off" in a price row's key met them.
#
# It is one guard rather than a word in each row's avoid list because the rule is about the
# phrase, not about the row: every row that reads a price needs it, and a row that later adds
# "money off" to its key gets it by passing the same name.
_BORROWING_IN_THE_LINE = re.compile(
    r"\b(?:borrow(?:s|ed|ing|er|ers)?|lend(?:s|ing)?|lent|loan|loans|owed?|owes|tide me over)\b")
