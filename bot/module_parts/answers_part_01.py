"""Part 1 of 11 of a large module, split out of `answers`.

Everything here is re-exported from `answers`, so callers import it from there as before.
"""
import difflib
import re
import string

from .. import memory as mem
from ..compose import NEGATORS, lead
from ..knowledge import topics
# `repeat` is read by `_answer` on every line, so it is imported with the rest: inside the hook
# that declares a request for less, the import is there for `TAKES_AS_IT_COMES` and missing for
# the turn, and a module that raises is skipped without a word (the whole lookup went quiet).
from ..memory import named
# not `hope` or `matters` on their own: `_answer` and its helpers use those names for other things
from ..memory import topics as memory_topics  # not `topics`: this module has a `topics()` of its own
from ..memory import keywords
from ..memory import again as same_again  # the short of an answer already on the screen
from ..memory.again import DETAIL_AGAIN, SAME_ADVICE
# A request for less ("keep it brief", "shorter") is the answer they already have, cut down, and
# it is read before the lookup so the short form comes back rather than a new entry.
from ..memory.topics import ASK_ONLY, stem
from ..understanding import kinds
# `repeat` is used in `_answer`, not only in the one place that imports it locally: a
# request for less is cut from the answer in memory, which every answered line goes
# through. With the import inside that one function only, `_answer` raised NameError
# on every line, the runtime swallowed it as it is meant to, and the whole knowledge
# base went silent behind a greeting.
from ..memory import keywords
# The ask-for-less path cuts the answer already given down (`repeat.shorter_for`). #3748 imported
# it inside `TAKES_AS_IT_COMES` only, so `_answer` raised NameError on every line and the whole
# knowledge base fell through to chat: "how do i cook rice" was answered with "That's beyond what
# I know well, sorry".
from ..memory.narrow import flat, the_outcome_asked
from ..understanding import understand



PRIORITY = 0


# The keeping entries that state the fact for cooked food in general. They fit any food, so a
# question put to them says no more than the line already had, and reading one as *this* food's
# keeping fact is how a gardening question ("what size pot do i need for tomatoes" / "can i
# still use it") would get told about cooked food in the fridge.
GENERIC_KEEPING = ("fridge-life", "fridge-life-cooked")


# The topics this module is the specialist for: the union of what the knowledge domains answer,
# with the topic ids the understanding engine produces (bot/understanding/topics.py). The
# arbiter reads ANSWERS, so a knowledge answer beats small talk on a line read as being about a
# topic the knowledge base covers, and only there. It is derived from the domains on purpose: a
# new domain must not need someone to remember to edit this list.
ANSWERS = topics()


# Words that point back at what the last lines were about.
REFERRING = frozenset("it its that this them they one ones there these those".split())


# "do you cook much?", "can you reheat rice?" - a yes/no question put to the bot is not a
# follow-up about the dish just discussed, so the conversation's subject is not written into it.
ABOUT_YOU = re.compile(r"^\s*(?:do|does|did|are|is|can|could|would|will|have|has|were)\s+you\b",
                       re.IGNORECASE)


def _the_new_part(reply, memory, keep=3):
    """The part of the reply the last answer did not already say, when it stands on its own.

    "how long to boil chicken legs" then "does that change if theyre from frozen" reaches the
    same entry, and the entry has a sentence for the frozen case: the two answers open the same
    way and the second goes on. Declined as a repeat, the turn had no answer at all. Said whole,
    the person hears the paragraph they just read again. The sentence that was not in the last
    answer is the answer to this line, so that is what comes back.
    """
    said = str(reply or "").strip()
    mine = flat(said)
    if not mine:
        return None
    for turn in (memory.get("turns") or [])[-keep:]:
        if not isinstance(turn, dict):
            continue
        before = str(turn.get("bot") or "").strip()
        opening = flat(before)
        if not opening or not mine.startswith(opening) or len(mine) <= len(opening) + 15:
            continue
        if not said.startswith(before):
            continue
        added = said[len(before):].strip()
        if added[:1].isupper() and added.endswith((".", "!", "?")):
            return added
    return None


# A verdict said on its own in front of the answer - "Usually, yes." on a row that declares one
# (`bot/compose/lead.py`) - is not part of what the answer says. It is read off before two answers
# are compared, so a card that was said with its verdict in front is still the same card when a
# later line is given it again.
_BARE_VERDICT = re.compile(
    r"^[^.?!]{0,40}[.?!]\s+(?=.)", re.S)


def _without_the_verdict(text):
    """The reply without a sentence-long verdict in front of it."""
    said = " ".join(str(text or "").split())
    found = _BARE_VERDICT.match(said)
    if not found:
        return said
    head = found.group(0).strip().lower()
    if len(head.split()) > 6:
        return said
    if not re.search(r"\b(?:yes|no|not|never|always|usually|often|sometimes|normally|depends"
                     r"|mostly|generally|rarely|seldom)\b", head):
        return said
    return said[found.end():].lstrip()


_CARD_OPENINGS = None


def _card_openings():
    """The first few words of every card in the knowledge base, read once."""
    global _CARD_OPENINGS
    if _CARD_OPENINGS is None:
        heads = set()
        try:
            from ..knowledge import entries as _all_entries
            for item in _all_entries():
                said = getattr(item, "reply", None)
                if isinstance(said, str):
                    flat = " ".join(said.split())
                    if flat:
                        heads.add(flat[:40].lower())
        except Exception:  # noqa: BLE001 - a repeat is never worth a turn
            heads = set()
        _CARD_OPENINGS = heads
    return _CARD_OPENINGS


def _without_a_lead(text):
    """The reply without a sentence a row declared in front of one of its own cards.

    A row may declare the sentence a kind of line asks for (`entry(..., lead=("yesno", "Yes"))`,
    `bot/compose/lead.py`), and the reply the person heard is that sentence and then the card.
    The sentence answers the line it was read for: it is not part of the card, so a later turn
    that repeats the card does not repeat the sentence ("Same as before: No." answers a question
    nobody asked). Only a sentence in front of a known card is read off - a card of its own that
    opens "No - leave them whole." keeps its own words (`_without_the_verdict`).
    """
    said = " ".join(str(text or "").split())
    found = _BARE_VERDICT.match(said)
    if not found:
        return said
    rest = said[found.end():].lstrip()
    if not rest or rest[:40].lower() not in _card_openings():
        return said
    head = _without_the_verdict(said)
    return head if head and head != said else said


def _opening(text, words=8):
    """The first few words of a reply: two answers that open the same way are the same answer.

    A card read out to a why line has its cause sentence moved to the front
    (`bot/compose/lead.cause_first`), and it is still the card that opened on its fix a turn ago.
    So a leading sentence that names itself as the cause is stepped over before the opening is
    read: without that, "why is my drain slow" then "how do i fix it" handed the whole card back
    a second time, because the repeat reading no longer recognised the answer it had just given.
    """
    said = _without_the_verdict(text) or ""
    parts = re.split(r"(?<=[.!?])\s+", said.strip())
    while len(parts) > 1 and lead._CAUSE_SENTENCE.match(parts[0]):
        parts.pop(0)
    return " ".join(" ".join(parts).lower().split()[:words])


def _most_of_it_said(reply, memory, keep=3, least=40):
    """True when a whole sentence of this answer is a sentence the bot has already given.

    A card can answer a fact with the answer it gave a turn ago and a lead-in on the front
    ("Nothing separate for stone - it is the same advice: ..."), which is the same paragraph a
    second time. A lead-in is not new advice, so it does not save the sentence.
    """
    said = " ".join(str(turn.get("bot") or "") for turn in (memory or {}).get("turns", ())[-keep:]
                    if isinstance(turn, dict))
    if not said:
        return False
    said = _flat(said)
    for sentence in re.split(r"(?<=[.;!?])\s+", str(reply or "")):
        # a lead-in ("Nothing separate for stone - it is the same advice: ...") is not advice,
        # so what follows the last colon or dash is the part that has to be new
        for part in (sentence, re.split(r"[:;]\s+|\s+[-—]\s+", sentence)[-1]):
            if len(part) >= least and _flat(part) and _flat(part) in said:
                return True
    return False


def _said_before(reply, memory, keep=3):
    """True when the bot has already given this answer (or one that opens the same way)."""
    turns = memory.get("turns") or []
    mine = _opening(reply)
    if not mine:
        return False
    for turn in turns[-keep:]:
        if not isinstance(turn, dict):
            continue
        if _opening(turn.get("bot")) == mine:
            return True
    return False


# The same line asked again gets the same answer, and saying it word for word twice in a row
# is what a machine does (STYLE.md, "Never answer the same way twice in a row"). The answer is
# still right, so it is given again rather than replaced; what changes is that the bot says it
# is giving it again, which also leaves room for the person to say what did not work. The
# wordings are the shared pool's, in `bot/memory/again` and `bot/memory/topics`, so that every
# lead-in the bot can put in front of an answer is in one place and can be read back off it.
AGAIN = tuple(memory_topics.REPEAT) + same_again.LIKE_I_SAID


# Asked a third time, the answer is not landing, so the bot says so and asks what went wrong
# rather than handing over the same paragraph again.
# The lead-ins that name the detail a follow-up asked about ("what about the biting"), and what
# each says when the answer already covers it. They live with the other frames, in
# `bot/memory/again`, so a reply under any of them can be read back to its answer.
WORD = re.compile(r"[a-z0-9']+")


# A follow-up can carry a verb of thinking or asking rather than a part of the thing ("what should
# we think about" after the dog answer): the verb is the asking, not a detail the answer can cover,
# so the lead-in must not name it ("Nothing separate for think" was the reply).
NOT_A_DETAIL = frozenset("""
think thinks thinking thought know knows knowing say says saying tell tells telling ask asks
asking wonder wonders wondering guess guesses guessing consider considers considering decide
decides deciding choose chooses choosing
# "reckon" is what a lot of people say for "think", and it is an ordinary word, so the repeat
# lead-in named it: "why am i always tired do u reckon" after the tiredness card came back
# "Nothing separate for reckon - it is the same advice: ...", which is a sentence about a word
# nobody asked about, and it reads worse than the plain "same answer" because "reckon" is not a
# part of anything. The line still carries the word - it is how the opinion is asked for, and the
# readers that answer one key on it - so it is dropped here, where the lead-in is chosen, and not
# from the reading.
reckon reckons reckoned reckoning rekon rekons reckin
""".split()) | frozenset("""
# Nor is the word a negation hangs on: "i dont know why" after the low-mood card came back
# "There is nothing separate for dont - it is the same advice", and "i have no idea why" named
# "idea". A line that says where the person has got to is not naming a part of the answer, so
# the words of not-knowing name nothing here.
dont doesnt didnt cant cannot couldnt wouldnt wont shant sure idea explain explains explained clue
""".split()) | frozenset("""
# The same verb said the other ways people say it: how somebody regards the thing is the asking,
# whatever verb carries it. "i want to start running but i find it boring" reached this lead-in as
# "Nothing separate for find - it is the same advice", where the word named is the person's own
# verb and the answer says nothing about it. The line is a repeat ask and gets the plain lead-in.
find finds finding found reckon reckons reckoning suppose supposes supposing imagine imagines
imagining feel feels feeling felt hope hopes hoping wish wishes wishing
""".split()) | frozenset("""
# How somebody hopes it will go is not a part of the thing either: "i want to start running but i
# hope it gets easier" came back "Nothing separate for easier - it is the same advice", which names
# a comparison the answer was never about. A comparative is the shape of the wish, not a subject.
easier easy better worse harder faster slower quicker sooner longer cheaper dearer
""".split()) | frozenset("""
# Nor is the opinion itself a part of the thing, and it is the word people reach for: covering
# the verb of thinking left the adjective behind, so "i want to start running but i find it dull"
# still came back "Nothing separate for dull - it is the same advice" while its nearest synonym
# "boring" was answered. How they regard the thing is not a part of the answer, whichever word
# they regard it with.
boring dull tedious pointless rubbish repetitive monotonous uninteresting
""".split()) | frozenset("""
# A time is not a part of the thing either: "she had a fall a week ago" came back "Nothing
# separate for ago - it is the same advice", which names a word nobody was asking about. The
# lead-in that says the answer covers it is the honest one for a line that only adds when.
ago today yesterday tomorrow tonight recently lately
week weeks month months year years day days
""".split()) | frozenset("""
# And a person nobody named is not a part of the thing: "someone else got the promotion" after
# the promotion answer came back "Same answer for someone: ...", which reads as a mistake. The
# plain repeat lead-in says the same thing without pretending it has narrowed anything.
someone somebody anyone anybody everyone everybody nobody none else another others other
""".split()) | frozenset("""
# Nor is how often: "is it ok to run every day" after another answer came back "Nothing separate
# for every - it is the same advice: <the answer before>", which names a word nobody asked about
# and reads as a sentence about nothing. A frequency says when the answer applies, not a part of
# the thing the answer is about.
every each once twice daily weekly monthly hourly yearly always never often sometimes
usually regularly rarely seldom
""".split())


# The verb the ask carries its own question on. In "how do i stop that" the last keyword is `stop`
# and it is the asking, not a detail, so it never becomes the thing the lead-in names.
# The words that point back at what was just said instead of naming a thing of their own.
BACK_POINTS = frozenset("""there it its that those these them they this one ones him her""".split())


ASK_VERB = re.compile(
    r"\b(?:how\s+(?:do|can|should|would|could)\s+(?:i|we)|how\s+to|"
    r"what\s+(?:do|can|should|would|could|will)\s+(?:i|we)|what\s+to|"
    r"where\s+(?:do|can|should|would|could)\s+(?:i|we)|"
    r"can\s+i|should\s+i|do\s+i)\s+([a-z']+)", re.I)


# The word that makes an -ed or -ing word a thing rather than the verb of the ask ("the seating",
# "the wedding"), so the frame-tail reading does not throw away a part they really named.
DETERMINER_BEFORE_DETAIL = frozenset(
    """the my his her their your our a an some both""".split())


# The same words, for joining a plural back onto the words that name it ("the custard tarts").
DETERMINERS = DETERMINER_BEFORE_DETAIL


# A word that is not part of the name of a part, so the search for it stops there: "what about the
# food for the kids" names the kids and not "food for".
STOP_BEFORE_A_PART = frozenset("""
    for and of in on at with about to from or the a an my his her their your our some both
    """.split())


# A sentence break, for the short version of an answer given a second time.
SENTENCE = re.compile(r"(?<=[.!?])\s+")


# A word that says how the answer landed is not a detail of it. "thats helpful" after the egg
# times was read as an ask about "helpful" and got "Nothing separate for helpful - it is the same
# advice: A soft one is the 5 to 6 minute egg...", which is the bot talking about its own words to
# somebody who had just thanked it for them. The praise belongs to the small-talk pool that answers
# a thank-you and a compliment, so the detail reading stands down and the line goes on to it.
PRAISE_WORD = frozenset("""
    helpful useful handy helpful great brilliant brill perfect lovely nice good sound sorted works
    worked working spot on exactly right clearer clear helpful interesting amazing fab fabulous
    wonderful excellent super ace wicked grand neat tidy
""".split())


# A word that names no thing is not a detail of the answer either. "what else can i do with it"
# asks for more of the answer, and read as a detail it gave "Nothing different for else I'm
# afraid: the same answer covers it - Take it off the heat...", a sentence about nothing: there is
# no part of the answer called "else". The ask is for the rest of what the entry knows, which is
# the repeat machinery's question, so the detail reading stands down and lets it answer.
# `more`, `other` and `another` are not in the set: they point at a part of the answer that has
# not been said yet ("the other half of it" is a real continuation), and only a word with no
# position in the answer at all is excluded.
NOTHING_WORD = frozenset("""
    else anything something nothing everything different instead anyway anyhow otherwise
""".split())


# A part of an answer is named, never a whole sentence about the person. "i work nights" after the
# neighbour's-dog advice named "nights", which that answer uses about the dog barking, and the words
# in front of it were walked back over the verb to "i", so the "part" was the entire line and the
# turn came back as "Everything about i work nights is in what I said above" - a fact handed back to
# the person who had just given it. A name never holds a subject, so a plural with one in front of
# it is a sentence about them, not a part of the answer to ask about.
SUBJECT_WORD = frozenset("""
    i im we us you he she they them theres thats it its one people
""".split())


# A word that adds emphasis or hesitation is not a detail either. "and when could they actually
# vote" after the women's-vote answer named "actually" as the part of the answer it asked about,
# and came back "Nothing separate for actually - it is the same advice: The campaign for women's
# votes split...". There is no part of a card called "actually": the line is the same ask with a
# softer word in it, so it is answered, not framed.
FILLER_WORD = frozenset("""
    actually really honestly seriously literally basically obviously definitely absolutely
    certainly clearly surely probably perhaps maybe quite rather even only just still again
    though although anyway anyhow then ok okay right please sure well so yes yeah
    hmm hmmm hm mhm mm um umm uhm uh er erm ah ahh oh ohh eh
""".split())


# A word that says what the thing is *like* is not a part of the answer either, and neither is the
# determiner in front of it. "when is the best time to buy a laptop" answered the calendar, and the
# same question said the other way - "when should i buy a new laptop" - came back "Nothing separate
# for **a new** - it is the same advice: Laptops and tablets are cheapest on Black Friday ...". The
# walk back from the end of the line had skipped `laptop` (the chat had just used it, so it names
# nothing new) and then taken the quality word beside it as the name of a part of the answer. There
# is no part of an answer called "a new", and "Same for a new: ..." is not a sentence: a quality
# word describes the thing and never names a piece of what the answer says about it. The same fault
# put "Same for a new" on the tv, the car and the phone, and "No separate fix for cheapest" on a
# bed.
A_QUALITY_WORD = frozenset("""
    new newer newest old older oldest young younger youngest
    cheap cheaper cheapest expensive pricey costly dear
    best better worst worse decent proper secondhand latest
    big bigger biggest small smaller smallest large larger huge tiny
    long longer longest short shorter shortest tall heavy light
""".split())


# A word that only joins one clause to the next is not a part of the thing. After the rescue-dog
# answer, "how long until my rescue dog settles" came back "Nothing different for until I'm afraid:
# the same answer covers it - Three months.": a person asking how long was told the bot had nothing
# separate to say about the word "until". `until` is a keyword of the ask ("how long until"), which
# is why the walk could reach it at all, so the joining words are named here and never said.
# A word that says where in the thing itself something goes - the end of the letter, the top of the
# form - is a part of what is already in hand, not a thing of its own. "i have to email my landlord
# about the damp" then "what should i write at the end of it" read `the end` as a thing the letter
# card never named, and the card stood down for a search hedge: the end of a letter being written is
# the letter's own last paragraph.
A_PLACE_IN_IT = frozenset("""
    end start beginning top bottom middle rest side front back corner last first
""".split())


A_JOINING_WORD = frozenset("""
    until till before after then when whenever while whilst during since once
    about if unless because than and or but so
""".split())


# A line that is nothing but a plea for more advice: "any tips", "got any advice", "any tricks".
# It names no thing of its own, so no entry is the answer to it - the answer is the one in hand.
A_PLEA_FOR_TIPS = re.compile(
    r"^(?:and |so |ok |okay |well )?(?:(?:any|some|got any|got some|need some|need any|"
    r"want some|more|any more|another|a few|any other)\s+)?"
    r"(?:tips?|advice|pointers?|tricks?|hints?)"
    r"(?: (?:at all|then|please|too|now|really|anyway))*[.!?]*$", re.I)


# A word no name in English contains: an auxiliary, a question word, a joining word. Asked the
# calendar question a second way - "when are laptops cheapest" - the plural reader walked up to
# three words back from `laptops` and took the question with it, and the person was told "Everything
# about **when are laptops** is in what I said above". A name is the thing and its modifiers, so
# both walks back over a candidate stop at one of these.
NOT_IN_A_NAME = A_JOINING_WORD | frozenset("""
    am is are was were be been being do does did done have has had having should would could can
    will shall may might must not
""".split())


def _in_short(reply):
    """The first sentence of an answer, or the first two when the first is only a lead-in.

    Asked the same thing twice, a friend repeats the short form, not the whole paragraph; the
    long answer is still there on the next ask (AGAIN_HELP), so nothing is lost.

    A sentence a row declared for an earlier line ("No.", "Usually, yes.") is not part of the
    short form either: this line asks something else, and "Same as before: No." answers a
    question the person did not ask (see `_without_a_lead`)."""
    reply = _without_a_lead(reply)
    parts = same_again.quoted.sentences(reply, SENTENCE)
    if not parts:
        return str(reply or "")
    if len(parts[0]) >= 60 or len(parts) == 1:
        return parts[0].strip()
    return (parts[0] + " " + parts[1]).strip()


def _same_as_the_last_answer(text, memory):
    """True when this answer is the one the person has just been given, in any words.

    Word for word is the plain case. A list of picks is the same list when it names the same
    things, even where an entry words the ones it has picked differently ("*Groundhog Day*
    (funny)" and "*Groundhog Day* for comedy" are the same film), because what the person is
    owed for a taste they have just named is a pick they have not had.
    """
    last = mem.last_bot(memory) or ""
    if not last:
        return False
    if _flat(text) == _flat(last):
        return True
    named_now = set(PICKED.findall(text))
    return bool(named_now) and named_now == set(PICKED.findall(last))


# The things an answer picks out by name (*Arrival*, *Project Hail Mary*): two answers naming the
# same set are the same list of picks, however the sentence around them is put together.
PICKED = re.compile(r"\*([^*\n]{2,60})\*")


def _the_same_answer_in_other_words(text, memory):
    """True when this answer says what is already on the screen, close enough to notice.

    A carried ask ("what else", "and a pudding") has to buy the person something they have not
    just had. An entry that words its list differently and keeps two of its three dishes hands
    back the answer they have just read: "Quick: tuna pasta in 15, macaroni cheese in 25, or a
    chicken traybake if you have 40 minutes" after "Quick: tuna pasta in 15, a frittata in 20, or
    a chicken traybake if you have 40 minutes". On that pair the overlap is 0.92, while the film
    list's second evening is 0.03 and a card where a punt was is 0.25, so 0.7 tells them apart.
    """
    last = mem.last_bot(memory) or ""
    if not last:
        return False
    return difflib.SequenceMatcher(None, _flat(text), _flat(last)).ratio() >= 0.7


def _flat(text):
    """A line reduced to its words, so a repeated question matches whatever its punctuation."""
    return " ".join(WORD.findall(str(text or "").lower()))


# The turn where the answer the person has just read covers what the line names: the reply points
# at it in one sentence. Two wordings, because the answer either names the part or it does not -
# "the 28 tram" is on the Lisbon card, so the trams are in the answer rather than missing from it,
# while a card about a phone battery that never says "screen" cannot claim to have covered it.
A_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")


A_CLAUSE_FINE = re.compile(r"[,;:]\s+|\s+\u2014\s+")


A_CLAUSE_BREAK = re.compile(r";\s+|:\s+|\s+\u2014\s+|,\s+(?:and|plus|but|so|which|then|with)\s+")


A_OPENS_A_CLAUSE = re.compile(r"^(?:and|plus|but|so|which|then|with|also|also\s)\b", re.I)


A_SAYS_NOTHING = frozenset(("it", "this", "that", "they", "them", "one", "ones"))


# A clause says something when it has a figure in it or a verb: "Insurance 8 to 20 a month",
# "Ask the vet about the rest". "Pubs away from Temple Bar for music" names the part and says
# nothing - it is the card's list with the sentence taken off it, so the pointer is better.
A_SAYS_SOMETHING = re.compile(
    r"\b(?:is|are|was|were|be|been|has|have|had|does|did|do|can|could|will|would|should|must|"
    r"need|needs|cost|costs|keep|keeps|want|wants|get|gets|give|gives|use|uses|take|takes|book|"
    r"books|buy|buys|put|puts|try|tries|ask|asks|check|checks|avoid|avoids|work|works|help|"
    r"helps|last|lasts|make|makes|mean|means|come|comes|go|goes|say|says|pay|pays|save|saves|"
    r"hold|holds|fit|fits|wear|wears|eat|eats|drink|drinks|start|starts|set|sets|add|adds|mix|"
    r"stir|stirs|cook|cooks|freeze|freezes|leave|leaves|order|orders|ring|rings|call|calls|wait|"
    r"waits|run|runs|sit|sits|stand|stands|open|opens|close|closes|clean|cleans|wash|washes|"
    r"dry|dries|walk|walks|feed|feeds|soak|soaks|cover|covers|worth)\b", re.I)


def _says_something(clause):
    """Whether the clause reads as a sentence rather than a list with the sentence taken off."""
    return bool(A_SAYS_SOMETHING.search(clause) or re.search(r"\d", clause))


def _the_part_in_the_answer(answer, detail):
    """The clause of `answer` that names the detail, said as its own sentence, or "".

    A follow-up that names a part of the last answer is owed the part. The answer above is on the
    screen, so the clause is not read out again - but a sentence about the conversation instead of
    about the thing ("Everything about insurance is in what I said above - there is no more than
    that") is what a person gets when the turn cannot find the clause, and it withholds the only
    line that answers them. Here it is found by name and handed back on its own.

    Only a clause that stands up as a sentence is used: four words or more, not opening on a
    joining word, and not a bare pronoun. A fragment is worse than the pointer.
    """
    last = (detail.split() or [""])[-1].lower()
    if len(last) < 3:
        return ""
    words = WORD.findall(str(answer or "").lower())
    if len(words) < 5:
        return ""
    # The loose split first, so the clause handed back keeps as much of its own sentence as still
    # reads as one; a list inside a sentence ("jabs and a microchip 60 to 100, neutering 60 to
    # 120 ..., insurance 8 to 20 a month") is one piece at that level and drops to the commas
    # only when no piece at the loose level both names the part and stands up.
    for splitter in (A_CLAUSE_BREAK, A_CLAUSE_FINE):
        for sentence in A_SENTENCE_BREAK.split(str(answer or "")):
            for clause in splitter.split(sentence):
                clause = clause.strip(" ,;:-\u2014")
                if not clause:
                    continue
                body = WORD.findall(clause.lower())
                if not any(_names_it(word, last) for word in body):
                    continue
                if len(body) < 4 or len(body) > 18:
                    continue
                if A_OPENS_A_CLAUSE.match(clause):
                    continue
                if body[0] in A_SAYS_NOTHING:
                    continue
                if not _says_something(clause):
                    continue
                clause = clause[0].upper() + clause[1:]
                if clause[-1] not in ".!?":
                    clause += "."
                return clause
    return ""


def _names_it(word, last):
    """Whether a word of the answer is the detail by name, or the stem of it."""
    if word == last:
        return True
    if len(word) < 4 or len(last) < 4:
        return False
    return word.startswith(last) or last.startswith(word)


SAID_ABOVE = (
    "Everything about {detail} is in what I said above \u2014 there is no more than that.",
    "All there is on {detail} is in the answer above, and nothing beyond it.",
    "{detail} is covered by the answer above; I have nothing to add to it.",
)


NOTHING_SEPARATE = (
    "There is nothing separate on {detail} \u2014 what I said above is the whole of it.",
    "Nothing more on {detail} than what I said above: it all comes under the one answer.",
    "There is no separate answer for {detail}: what is above is the whole of it.",
)


# A line that asks about how the thing turned out is not the part named and nothing else. "will it
# come back if i just wipe it" names the wiping, which the answer above covers, and the answer
# given back was "Everything about wipe is in what I said above" - a sentence about the
# conversation instead of about the wall, because the turn read the line as a part being named
# again and never saw the question in it. The question is what the person asked, so a line with
# one of these in it keeps the ordinary answer: this is only for a follow-up that names a part and
# asks nothing else ("what about the food", "and the trams").
ASKS_ABOUT_HOW_IT_TURNED_OUT = re.compile(
    r"\b(?:will|would|does|do|did|can|could|should|is|are|was|were|might)\s+"
    r"(?:it|that|this|they|them|those|these|i|we|you|he|she)\b", re.I)


def _a_part_named_in_the_line(text, memory, answer):
    """The part a follow-up names in the plural ("the pubs", "the trams"), or "".

    `_the_detail_named` keeps the words of the line as they were typed and looks for each of them
    among the keywords, which are stems, so a part named in the plural is never found: "what about
    the pubs" is looked for as "pubs" against "pub", and the turn gets no lead-in at all. Only a
    plural is read here - a word ending in "s" whose stem is one of the keywords - and only when
    the answer names it, because then the lead-in can say the answer covers it ("Same for the
    pubs: ..."). Anything else is the job of `_the_detail_named`, whose verb tests a bare ending
    never gets: "how do i make it work" names no part, and "work" is not one.
    """
    raw = WORD.findall(str(text or "").lower())
    wanted = {word for word in keywords(text) if len(word) > 2 and word not in ASK_ONLY}
    already = _said_before_now(text, memory)
    for index in range(len(raw) - 1, -1, -1):
        word = raw[index]
        if word in already or word in PRAISE_WORD or word in NOTHING_WORD:
            continue
        if len(word) < 4 or not word.endswith("s"):
            continue
        stem = word[:-1]
        if stem not in wanted:
            continue
        if not _named_in(answer, word):
            continue
        # "the custard tarts" is the part, not "tarts": the word or two in front of the plural are
        # part of its name when they are not a determiner ("the" is put back on in front of them).
        words = [word]
        before = index - 1
        while (before >= 0 and len(words) < 3 and raw[before] not in DETERMINERS
               and raw[before] not in ASK_ONLY and raw[before] not in STOP_BEFORE_A_PART
               and raw[before] not in PRAISE_WORD and raw[before] not in NOT_IN_A_NAME
               and raw[before] not in A_QUALITY_WORD):
            words.insert(0, raw[before])
            before -= 1
        if any(word in SUBJECT_WORD for word in words):
            continue
        name = " ".join(words)
        if before >= 0 and raw[before] in DETERMINERS:
            return raw[before] + " " + name
        return name
    return ""


def _short_form_of_the_last(answer, memory):
    """The answer last turn, when this turn's answer is only its opening, else ""."""
    last = str(mem.last_bot(memory) or "").strip()
    mine = _flat(answer)
    if not last or not mine or mine == _flat(last):
        return ""
    if not _flat(last).startswith(mine):
        return ""
    return last


def _answer_said(plan, memory):
    """How many of the turns just before this one already gave the plan's sentence.

    A follow-up asks the property in different words each time ("what temperature?" after "what
    temperature for a cake"), so the line is not the same twice and the count of the same line
    is 0. What is the same is the sentence we answered with, framed or not."""
    mine = _flat(plan)
    if not mine:
        return 0
    count = 0
    for turn in reversed(memory.get("turns") or []):
        if not isinstance(turn, dict) or mine not in _flat(turn.get("bot")):
            break
        module = turn.get("module")
        if isinstance(module, str) and module and module != "answers":
            # The sentence was said, but not as this module's answer to a question: a plan
            # announcement is answered with the entry's own paragraph by the store ("im planning
            # a trip" gets the countdown), and the line after it is the first question about
            # that paragraph. Counting it as said would answer "how long will it take" with
            # "Same as before:" in front of what was just read, where the part asked is what the
            # person needs (fast-shelf, #1848).
            continue
        count += 1
    return count


# Words that carry no subject: a sentence of an answer is about the same thing as the question
# when they share a word that is not one of these.
BARE = set("the a an i me my mine we our you your it its is are was were be do does did can could "
           "should would will shall may might to for of and or but in on at with about from that "
           "this these those there here what how when which why who whom whose if then so not no "
           "have has had get got make made much many more most some any".split())


def _carries(text):
    """The words of a line that say what it is about."""
    return {word for word in WORD.findall(str(text or "").lower())
            if len(word) > 2 and word not in BARE}


def _the_sentence_asked(reply, text):
    """The sentence of an answer that answers a line asking for one part of it.

    A repeated question is answered again, and a friend gives the part asked rather than the
    whole of a two-part answer: "can i make the frosting the day before", asked again, is the
    plan's sentence about the day, not the keeps-sentence in front of it that the person has
    already read. The sentence that shares the most words with the line is that part, and the
    first sentence is the answer when no sentence shares anything with it.
    """
    sentences = [part for part in SENTENCE.split(str(reply or "")) if part.strip()]
    if len(sentences) < 2:
        return None
    wanted = _carries(text)
    best, best_score, best_length = None, 0, len(sentences[0])
    for sentence in sentences:
        score = len(wanted & _carries(sentence))
        # The tightest sentence wins a tie, as in a narrowed answer: "before you use it" is not
        # as good a match for "the day before" as the sentence that says the day.
        if score and (score > best_score or (score == best_score and len(sentence) < best_length)):
            best, best_score, best_length = sentence, score, len(sentence)
    if best is None:
        return None
    # A sentence said on its own does not open with the word that joined it to the one before. The
    # child-worry card reads "...being told it is nothing teaches them to hide it. Then take one
    # small step towards whatever they are avoiding...", and the second sentence said alone opens
    # on a "then" with no then in front of it. A step of an answer is already said without its
    # joining word (_first_step), and the same holds for any one sentence of it.
    joined = _JOINED_ON.match(best.strip())
    if joined:
        best = best.strip()[joined.end():]
        best = best[:1].upper() + best[1:]
    return best


# Asked for a figure the answer does not hold, repeating the answer is not an answer: "how long
# will that take" after the boiler checks gave the whole list back behind "Same as before:". A
# friend says what they cannot give and then gives the first step, so the honest line comes
# before the repeat wording.
NO_FIGURE = {
    "time": "I can't put a time on that one, sorry - ",
    "clock": "I can't put a time on that one, sorry - ",
    "heat": "I can't put a temperature on that one, sorry - ",
    "money": "I can't put a price on that one, sorry - ",
    "amount": "I can't put a figure on that one, sorry - ",
    "pressure": "I can't put a pressure on that one, sorry - ",
    "distance": "I can't put a distance on that one, sorry - ",
}


# A step ends where the next one starts: the opening of an answer is often one long sentence
# with the steps run together, and only the first of them is short enough to say again.
STEP_END = re.compile(r";\s+|,\s+(?:and|then|but)\s+|\.\s+|\.$")


# A length of time written in words is a time too: an entry that says "a fortnight" has answered
# "how long", and claiming otherwise would be worse than repeating it.
SPOKEN = re.compile(r"\b(?:fortnight\w*|overnight|all day|an hour|half an hour|a day|a week"
                    r"|a month|a year|a minute|a couple of (?:minutes|hours|days|weeks))\b", re.I)


# Any figure with a unit of time in it, relative or not: "30 minutes earlier" is still a length
# of time in the answer, so the answer is not one with no time in it.
TIMEISH = re.compile(r"\b\d+\s*(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?"
                     r"|months?|years?)\b", re.I)


# Nothing in an answer is a length of time, so the honest line says that rather than repeat it: the
# steps are the answer to a different question.
NO_STEP = "what I said there is the steps, not how long they take."


# A step said on its own does not open with the word that joined it to the one before: "then go
# for a plain chocolate sponge" started life as the second step of the answer.
_JOINED_ON = re.compile(r"^(?:and|then|so|but|also|now|next)(?:\s*,\s*|\s+)", re.I)


def _first_step(reply):
    """The first step of an answer, short enough to say on its own."""
    opening = SENTENCE.split(str(reply or "").strip())[0].strip()
    joined = _JOINED_ON.match(opening)
    if joined:
        opening = opening[joined.end():]
        opening = opening[:1].upper() + opening[1:]
    if not opening:
        return ""
    if len(opening.split()) <= 16:
        return opening if opening[-1:] in ".!?" else opening + "."
    # Only the clause the answer opens with: a later clause of a long sentence is a detail
    # ("all electric, put the immersion on a timer"), not the step to start with.
    first = next((one.strip(" ,;:") for one in STEP_END.split(opening) if one.strip(" ,;:")), "")
    for piece in (first, first.split(": ")[-1]):
        if 4 <= len(piece.split()) <= 20:
            return piece if piece[-1:] in ".!?" else piece + "."
    return ""


def _asks_of_another_subject(text, understood):
    """True when the line, read on its own, belongs to a different subject than the one it leans on.

    "what should i see there", after a city was described, is about that city: read alone it is
    still a travel question, and the answer on the screen is the answer. "what is there to eat"
    is about food: read alone it is a food question that only borrowed its "there" from the
    travel turn, and handing back the paragraph about the tram tells a person nothing they asked
    for (STYLE.md prefers the honest hedge to an answer that does not fit). What separates them
    is the subject the words carry by themselves, not the shape of the line.
    """
    if not isinstance(understood, dict) or not str(text or "").strip():
        return False
    alone = understand(text, {}) or {}
    own = alone.get("topic") or ""
    held = (understood.get("leans_on") or {}).get("topic") or ""
    return bool(own) and bool(held) and own != held


def _ask_verb(text):
    """The verb the ask leans its question on ("stop" in "how do i stop that"), or ""."""
    match = ASK_VERB.search(str(text or ""))
    return str(match.group(1) or "").lower() if match else ""


def _the_outcome_owed(item, text):
    """The sentence this row owes a line that asks how its subject turns out, or None.

    "will it be alright" after the phone went in the sink asks about the subject the last answer
    was about, and every sentence that answers it is already on the screen. A row that declares
    one (`entry(..., outcomes=(("survives", "..."),))`) has written that answer as a line of its
    own, so the turn gives the person that instead of a paragraph they have read.
    """
    which = the_outcome_asked(text)
    if not which or item is None:
        return None
    for shape, sentence in getattr(item, "outcomes", ()) or ():
        if shape == which and str(sentence or "").strip():
            return sentence
    return None


def _said_before_now(text, memory):
    """The words the person has already used in this chat, before this line."""
    seen = set()
    for turn in (memory or {}).get("turns") or []:
        if isinstance(turn, dict):
            seen.update(WORD.findall(str(turn.get("user") or "").lower()))
    return seen


# A word that corrects or softens the line rather than naming a part of the thing: "make it 3
# instead" names a new figure, and "instead" is not a detail the answer could have a sentence
# about - it made the lead-in read "Nothing separate for instead". The same for the openers
# people put in front of a correction ("actually", "no", "sorry", "wait").
A_CORRECTION_WORD = frozenset("""
    instead actually only just make again now please sorry wait really exactly still anyway
""".split())


def _a_fact_about_the_person(memory):
    """True when the line states something about the person rather than asking about a part.

    The detail frame is for a follow-up that names a part of the answer being pointed at ("what
    about the trams"). A line that says something about the person - "i work nights", "i have a
    toddler", "we live in a flat" - names no part of any answer, and a fact about themselves is the
    one thing a friend never hands back. The reading says which it is, so no word list has to guess;
    the part-name reading still gets its turn first, so a real part is never lost to this.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    return (understood.get("kind") == "statement" and not understood.get("asks")
            and bool(understood.get("first_person")))


def _a_restatement_of_the_answer(memory):
    """True when the line tells the bot something rather than asking about a part of the answer.

    A question about a part ("what about the crate") is the framing's whole use, so it is never
    taken from it. A statement is the person adding what they know to the same subject, and what it
    names is the subject, not a part - the same test `_a_fact_about_the_person` makes.
    """
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    return understood.get("kind") == "statement" and not understood.get("asks")


def _all_of_it_in_the_answer(named, memory):
    """True when the answer just given already says every word of the part named."""
    said = WORD.findall(str(mem.last_bot(memory if isinstance(memory, dict) else {}) or "").lower())
    words = [word for word in WORD.findall(str(named or "").lower())
             if len(word) > 2 and word not in A_JOINING_WORD]
    return bool(words) and all(word in said or stem(word) in said for word in words)


# A word straight after a clause's subject is that clause's verb, and the line says so without
# naming the verb: "he bites when i stroke him" named `stroke` and answered "Same for stroke: that
# is usually over-stimulation ...", where nobody was talking about a part of the answer called
# "stroke". `stroke` is not on any verb list, and a list can only ever cover the verbs on it, so the
# test is the position rather than the word.
CLAUSE_OPENER = frozenset("when whenever if once after before while until as".split())


CLAUSE_SUBJECT = frozenset("i you he she it we they u".split())


NUMBER_OR_OWNER = frozenset("the my your his her their our this that a an".split())


def _the_clause_s_verb(raw, index):
    """True when the word at `index` is the verb of a when-or-if clause, whatever the word is."""
    if index >= 2 and raw[index - 2] in CLAUSE_OPENER and raw[index - 1] in CLAUSE_SUBJECT:
        return True
    # "when the heating comes on", "when my boiler fires": an opener, then a determiner and the
    # thing itself, and the next word is what the thing does.
    return bool(index >= 3 and raw[index - 3] in CLAUSE_OPENER
                and raw[index - 2] in NUMBER_OR_OWNER)


# A word in front of the part and the part are one name ("a scratch post", "my new bike"), and the
# bare head word is not a phrase anyone says: "will she stop if i get a scratch post" came back
# "Same answer for post: Put a tall scratching post..." - the part named as the one word the
# determiner had been stripped off.
MODIFIER_WORDS = 2


def _named_whole(raw, index):
    """The determiner and the words between it and `raw[index]`, when they name one part, or "".

    Only a determiner close in front of the word counts, and only when every word between them is
    a plain one: a preposition, a back-pointing word or a verb means the line has moved on, and the
    word on its own is what it is.
    """
    # A back-pointing word right after the head word means the name is over: in "what about the
    # second hand one" the part is "the second hand one" or nothing at all, and "the second hand"
    # is a clock hand. Walking back from that head word would name a part nobody said.
    if index + 1 < len(raw) and raw[index + 1] in BACK_POINTS:
        return ""
    # The head word itself has to be a part: where it is the verb, the words in front of it are a
    # clause, not a name, and "Same answer for my back hurts:" is not a sentence. `what about the
    # biting` and `what about the seating` keep their answers, because the determiner in front of
    # the word settles the name before this test runs.
    head = raw[index]
    if (head in kinds.VERBISH or head in NEGATORS
            or (len(head) > 4 and head.endswith(("ed", "ing", "s")))):
        return ""
    # A negated verb in front of the head word is the same tell: "my mate hasnt text" is a
    # sentence about a mate, and "Same answer for my mate hasnt text:" is not a sentence.
    if any(word in NEGATORS for word in raw[max(index - MODIFIER_WORDS - 1, 0):index]):
        return ""
    for back in range(index - 1, max(index - 1 - MODIFIER_WORDS, -1), -1):
        word = raw[back]
        before = raw[back - 1] if back else ""
        if before in DETERMINER_BEFORE_DETAIL:
            return " ".join(raw[back - 1:index + 1])
        if (word in STOP_BEFORE_A_PART or word in BACK_POINTS or word in NOT_A_DETAIL
                or word in FILLER_WORD or word in NOTHING_WORD or word in PRAISE_WORD
                or word in NOT_IN_A_NAME or word in A_QUALITY_WORD):
            return ""
        if word in kinds.VERBISH or (len(word) > 4 and word.endswith(("ed", "ing"))):
            return ""
    return ""


FIRST_PERSON = frozenset("""i im ive id ill i'm i've i'd""".split())


def _their_own_state(text):
    """True when the line is about the person themselves and asks nothing of the thing.

    A follow-up that names no part of the answer and says how the person is ("i dont know why",
    "im not sure why") has nothing to be told about: the card on the screen above is not a second
    answer, and reading part of it out again is the bot talking at somebody who has just said
    they do not know.
    """
    text = str(text or "")
    if ASKS_ABOUT_HOW_IT_TURNED_OUT.search(text) or _ask_verb(text):
        return False
    raw = WORD.findall(text.lower())
    return bool(raw) and raw[0] in FIRST_PERSON


def _named_in(part, detail):
    """True when `part` says the detail by name, so a lead-in may say the answer covers it.

    A word of three letters or more is the detail itself when it is the word, whole: the check
    used to need four letters, so "should i ring the vet" after the vet answer was told
    "Nothing separate for the vet" by an answer whose every other word is about the vet. The
    prefix reading is for the word that carries an ending ("bite" in "biting"), and it needs four
    letters on both sides, because three is where "cat", "gas" and "bin" start matching things
    that are not them.
    """
    last = (detail.split() or [""])[-1]
    if len(last) < 3:
        return False
    for word in WORD.findall(str(part or "").lower()):
        if word == last:
            return True
        if len(word) >= 4 and len(last) >= 4 and (
                word.startswith(last[:4]) or last.startswith(word[:4])):
            return True
    return False


def similar(word, other):
    """Two words that are the same thing for this purpose: equal, or one carrying the other.

    "snails" and "snail" are one thing; "slug" and "slugs" are; "clean" and "cleaner" are not
    compared here, because the caller only passes words long enough for the stem to matter.
    """
    if word == other:
        return True
    if len(word) < 4 or len(other) < 4:
        return False
    return word.startswith(other) or other.startswith(word)


def _entry_words(memory):
    """The words the entry that has just answered is keyed on, all of them.

    Kept on the answer itself (`bot/memory/topics.remember_answer`), so a line naming another of
    the things that entry answers can be recognised without looking the entry up again.
    """
    kept = []
    answer = (memory or {}).get("entry_answer")
    if isinstance(answer, dict):
        kept.append(answer)
    others = (memory or {}).get("entry_answers")
    if isinstance(others, list):
        kept.extend(record for record in others if isinstance(record, dict))
    words = set()
    for record in kept:
        for key in record.get("keys") or ():
            words.update(WORD.findall(str(key).lower()))
    return words


def _what_they_typed(text, memory):
    """The words the person typed, given a reading with an earlier turn in front of it.

    The turn's own line is widened for a follow-up by putting the conversation's topic in front
    ("im learning to drive" + "how many lessons will i need"), and the knowledge base is then
    handed a line nobody typed (see `chat._follow_up_reading`). Everything below reads the
    person's own words for what the line names, so under that reading the topic comes back off
    the front: "how much does a puppy cost how much does a tattoo cost" is the tattoo question,
    and the puppy's answer is not about it.
    """
    if not isinstance(memory, dict) or not memory.get("joined_read"):
        return text
    read = memory.get("understood") if isinstance(memory.get("understood"), dict) else {}
    topic = str(((read.get("leans_on") or {}).get("text")) or "").strip()
    line = str(text or "").strip()
    if topic and line.lower().startswith(topic.lower()):
        return line[len(topic):].strip()
    return text


# The first word of an answer that can lose its capital behind a lead-in. Every frame above puts
# the answer after a colon ("Same for {detail}: {reply}"), so a sentence opener came out as
# "Same for cooker: They are the cut a slow cooker suits" - two sentences in one. The set is the
# closed class of openers that are never a name, so "Same for the pan: Cook it" keeps its capital
# and nothing that starts a reply with a proper noun is touched.
A_SMALL_OPENER = frozenset("""
    the a an this that these those they it there he she we you and but if so or then both most
    some many all any each other another not no
    # ...and the verb an answer opens with when it tells somebody what to do. "Same for
    # floorboards: Sand a wooden floor back to bare wood" and "The same goes for the bathroom:
    # Use a mid-sheen" both read as two sentences with the capital on, which is the fault
    # STYLE.md names; the verb is a common word, so it loses it.
    add allow apply ask avoid bake baste beat begin boil bring brush buy catch change check
    choose clean clear close cook cool cover cut defrost do drain drink dry empty fill find
    finish fit fix freeze get give go hang heat hold keep lay leave let lift line look make
    measure mix open paint peel pick place plug pour prepare press pull put rinse roll rub
    run sand scrape seal set shake shut simmer sit soak sort spray spread stand start stay
    steam stir stop store switch take talk tell test thaw think throw tidy tip try turn use
    wait wash watch wear wipe work wrap
""".split())


def _small_letter(body):
    """`body` with a sentence-opening pronoun, article or verb put in lower case after a lead-in."""
    first, _, rest = body.partition(" ")
    bare = first.rstrip(string.punctuation)
    if bare.lower() in A_SMALL_OPENER:
        return first[:1].lower() + body[1:]
    # A word the same answer says again later in lower case is a common word, not a name: "Sand
    # a wooden floor back to bare wood, vacuum the dust off" is one sentence, where "Paris is the
    # one, and paris in august is hot" is not what this is protecting. A name is said again with
    # its capital, so it keeps it.
    if bare[:1].isupper() and re.search(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(bare.lower()),
                                       rest):
        return first[:1].lower() + body[1:]
    return body


def _with_detail(detail, part, times, text="", memory=None, card=""):
    """`part` with the detail in front of it, said as what it is: the subject, or the same advice."""
    body = str(part or "").strip()
    if not detail or not body:
        return ""
    # Two frames saying the answer has not changed have been said; a third one about the bot's own
    # stock reads as the bot reporting on itself, and "nothing different for empty I'm afraid" also
    # makes an adjective in the line into a part of the answer. The person's own word takes the
    # lead-in's place from here. See `again.the_same_thing_underneath`.
    underneath = same_again.the_same_thing_underneath(text, body, times, memory)
    if underneath:
        return underneath
    if detail.split()[-1] in NOT_A_DETAIL:
        # The line asked what to think or what to say, not about a part of the thing: the answer
        # has not changed, and saying "Nothing separate for think" made it read as one word doing
        # another's job. The plain repeat lead-in is the honest one.
        return same_again.AGAIN[min(times, len(same_again.AGAIN)) - 1].format(reply=body)
    # The lead-in may only name what the answer itself names: see
    # `again.the_name_the_answer_says`, the one rule both frames use. It fixes the ask's own verb
    # being glued into the name ("a scratching post help") and the fragment left when the line
    # says "a bigger" and the answer only ever says "bigger".
    # The dictionary is the whole answer the person has, not only the sentence handed back: the
    # amount sentence of the paint card says "emulsion" and never "paint", while the card's own
    # opening names the paint. Reading the sentence alone dropped the person's word from the
    # lead-in and fell back to the plain frame, when naming it back is what the lead-in is for.
    named = same_again.the_name_the_answer_says(body, detail, card=card)
    if not named and _a_yes_no_ask(memory):
        # Nothing the lead-in could name, and a yes/no ask has no other word to build one from.
        # "Nothing separate for a bigger" claims the answer covers a fragment; the plain repeat
        # lead-in says the answer has not changed and hands it over with nothing glued in.
        return same_again.AGAIN[min(times, len(same_again.AGAIN)) - 1].format(reply=body)
    pool = DETAIL_AGAIN if named else SAME_ADVICE
    return pool[min(times, len(pool)) - 1].format(detail=named or detail,
                                                  reply=_small_letter(body))


def _a_yes_no_ask(memory):
    """True when the line asks yes or no ("would a service help")."""
    understood = memory.get("understood") if isinstance(memory, dict) else None
    if not isinstance(understood, dict):
        return False
    return "yesno" in (understood.get("asks") or ())
