"""Part 1 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..understanding.topics import THE_PEOPLE

from .fallback_data import (
    BODY_PARTS,
    CHECK_PHRASES,
    FILLERS,
    HEALTH_WORDS,
    HOW_ARE_YOU_TAGS,
    HOW_TO_DECIDE_FILLER,
    SYMPTOM_WORDS,
    VISIT_PRONOUNS,
    _BOUNDED,
    _WOUND,
)

from .fallback_data import (
    # Moved out of this file whole: the tables are unchanged, and the names come back
    # under the same ones.
    DITHER_SUBJECT,
)



def _bounded(phrase):
    """A phrase matched as whole words, so "raining" is not "training"."""
    pattern = _BOUNDED.get(phrase)
    if pattern is None:
        pattern = _BOUNDED[phrase] = re.compile(r"(?<![a-z])" + re.escape(phrase)
                                                + r"(?![a-z])")
    return pattern


def _has(clean, phrases):
    """True when the line mentions one of these phrases as whole words: "raining" must not
    match "training", and "the score" must not match "the scoreboard" by accident."""
    for phrase in phrases:
        if _bounded(phrase).search(clean):
            return True
    return False


def _plain(clean):
    """The line without filler words, for phrase matching."""
    return " ".join(word for word in clean.split() if word not in FILLERS)


def _matchable(text):
    """The line as a phrase table can see it: lowercase, no apostrophes, single spaces.

    A phrase is written for the standard spelling and people do not type it: "hows your day"
    for "how's your day", "whats the time" for "what's the time". The apostrophe is the one
    mark a phrase table and a typed line disagree about most, so both sides of a match drop
    it and "hows your day going" is found."""
    text = str(text or "").lower().replace("\u2019", "'").replace("'", "")
    return " ".join(text.split())


def _nothing_but_tags(form, end):
    """True when what follows the phrase is only a tag, so the phrase is the whole question."""
    return all(word in HOW_ARE_YOU_TAGS for word in re.findall(r"[a-z']+", form[end:]))


# Only a line that is nothing but the handback, because "i cant decide between two jobs" and "i
# dont mind but my partner does" are things to talk about rather than an offer to take. The polite
# openers and the trailing softeners are what people put round it, so they come off before the
# test rather than being matched twice.
HANDS_IT_BACK = re.compile(
    r"^(?:(?:o+k+(?:a+y+)?|right|so|well|then|h+m+|ha|ha+ha|please|ta|cheers|and|dunno)[, ]+)*"
    r"(?:(?:i |i'm |im )?(?:dont|don't|do not) (?:mind|care)[, ]+(?:so )?)?"
    r"(?:"
    r"(?:you|u|youre|you are|your) (?:pick|choose|decide|call it|the call|the choice|call"
    r"|choice|decision|expert|boss|shout)(?: (?:one|the one|one of them|then|first))?"
    r"|(?:you|u) (?:can|could|may|should) (?:pick|choose|decide|have (?:it|this|that))"
    r"|(?:ill |i will |i'll )?(?:let you|leave it to you|leave this to you|leave that to you)"
    r"(?: (?:pick|choose|decide|have (?:it|this|that)|take (?:it|this|that)))?"
    r"|(?:you|youve|you have) got (?:this|it|this one|that one)"
    r"|(?:its |it is |thats |that is )?(?:up to you|over to you|down to you|your call"
    r"|your shout)"
    r"|(?:youre|you are) (?:the (?:expert|boss|one who knows)|better at this)"
    r"|(?:whichever|whatever) (?:you|u) (?:think|want|like|prefer|reckon|say)"
    r")"
    r"(?:[, ]+(?:then|please|for me|really|honestly|ha|haha))*"
    r"\s*[.?!:)]*\s*$")


# A question about ringing for help is not a decision to weigh, and it is the one question the
# bot must never hand back: the person is asking whether this is serious enough to act on, and
# "can't call that one for you, sorry - say what you'd lose either way" was the answer to
# "should i call an ambulance", "should i ring an ambulance", "should i call 999" and
# "should i call the police". A friend settles it in one word and then says what to do with the
# phone in their hand.
EMERGENCY_CALL = re.compile(r"\b(?:ambulance|paramedic|paramedics|999|911|112|fire brigade|"
                            r"fire service|fire engine|coastguard|lifeboat|mountain rescue|"
                            r"a&e|a and e|casualty|resus|defibrillator)\b")


# `law` on its own made every degree question a police question: "should i go to law school"
# was answered "ring 999 if it is happening now". Only the phrases that name the police: the
# subject of a degree is not a call to make (clean-sage, #4381).
POLICE_CALL = re.compile(r"\b(?:police|cops|101|law enforcement|the law)\b")


# The police word is the subject of far more lines than it is a call to make, and a question
# that mentions them is not a question about ringing them: "did the police come", "did the
# police do anything", "is it against the law to park there", "whats the law on fireworks" and
# "did the law pass" were all handed "999 now, for anything happening or anyone in danger" at
# main. A line that wants a number names the act of getting in touch with them ("should i call
# the police", "should i report it to the police", "should i go to the police about my ex"), so
# the police branch asks for that verb as well as the name. `did` on its own, which is all the
# legal question has, is not one.
REACHING_THE_POLICE = re.compile(
    r"\b(?:call|calls|called|calling|ring|rings|rang|ringing|dial\w*|phone|phones|phoned|phoning|"
    r"report|reports|reported|reporting|tell|tells|telling|told|contact|contacts|contacted|"
    r"speak|speaks|speaking|spoke|talk|talks|talking|talked|go|goes|went|going|involve\w*|"
    r"ask|asks|asked|asking)\b")


# "Do i need the police" and "do i want the police involved" leave the act out, so `need` is not
# a verb of contact on its own: "the law needs to change" would otherwise be read as a call to
# make, and so would "i need to know about the law" (the name has to come after the ask, which
# is what a person says when they are asking for them). "get" is in it for "can i get the police
# to come", not for "how do i get into law enforcement", where the words after it are not the
# police but a way in.
_ASKING_FOR_THE_POLICE = re.compile(
    r"\b(?:need(?:s|ed)?|want(?:s|ed)?|get|gets|getting|got)\s+"
    r"(?:to\s+(?:\w+\s+)?)?(?:the\s+|a\s+|an\s+)?(?:police|cops|law enforcement)\b")


# The other half of the same guard: a line that names something happening to them keeps the card
# with no verb of its own ("the police" is the answer whether or not the line says "ring"). The
# words are a crime or a person at the door, not a symptom, so a legal question has none of them.
SOMETHING_HAPPENING = re.compile(
    r"\b(?:broke|broken|breaking|break\s?in|break-ins|burgl\w*|intruder|trespass\w*|"
    r"attacked|attacking|assault\w*|"
    r"threat\w*|stalk\w*|follow(?:ing|ed) me|chased|mugged|robbed|vandal\w*|smash\w*|"
    r"hit me|hurled|hitting me|abusive|in my (?:house|home|flat|garden|shed|garage)|"
    r"outside my (?:door|house|flat))\b")


# The line has to be asking what to do, not reporting a call already made: "i called 999
# yesterday" is a story, and answering it with "ring 999 now" would be absurd.
_ASKS_TO_ACT = re.compile(r"^\s*(?:should|shall|do|did|would|will|is it|do (?:you|u)|"
                          r"would (?:you|u)|can (?:you|u)|could (?:you|u)|am i)\b"
                          r"|\b(?:should i|need an?|worth calling|better to call)\b"
                          # The ask can come after the story: "i was burgled, do i need the
                          # police" asks the same question as "should i call the police" and was
                          # let past for naming the person instead of opening with the verb.
                          r"|\b(?:do|should|shall|would|will|did|can|could|am|are)\s+(?:i|we)\b")


# "Should i call an ambulance" is settled by a friend in one word, but "for a stubbed toe" is not
# that question: the dangerous-sounding word is in the line and the thing named is nothing. A
# minor complaint named in the line, with no danger symptom beside it, takes the emergency answer
# back to the ordinary one (swift-goat, #4381).
MINOR_HARM = re.compile(
    r"\b(?:stubbed|stubbing|paper cut|papercut|splinter|blister|blisters|hiccups?|dandruff|"
    r"verruca\w*|stye|athlete'?s foot|nappy rash|stitch|bruise[sd]?|bumped|graze[sd]?|grazed|"
    r"nicked|chapped|chafing|sunburn|hangover|ingrown|head ?lice|nits|cold|colds|cough|coughs|"
    r"sneez\w*|hayfever|hay fever|toothache|earache|sore throat|heartburn|indigestion|"
    r"constipat\w*|piles|sprain(?:ed)?|twisted ankle|scratched|insect bite|mosquito bite)\b")


# A symptom that keeps the emergency answer even when a small word is in the line: "should i call
# an ambulance - my toe is stubbed but he is not breathing" is still an emergency.
DANGER_SYMPTOM = re.compile(
    r"\b(?:can'?t|cannot|not|isn'?t|stopped|struggling to|finding it hard to)\s+breath(?:e|ing)\b"
    r"|\b(?:not|never|isn'?t|un)\s*(?:responding|responsive|conscious)\b"
    r"|\b(?:chest pain|crushed|crushing|severe|heavy bleeding|bleeding (?:a lot|badly)|"
    r"won'?t stop|no pulse|seizure|fitting|overdose|took (?:too many|an overdose)|"
    r"stroke|anaphyla\w*|throat (?:closing|swelling)|blue lips|stopped breathing)\b")


# A place you are seen at is not a thing you ring, and the two decisions are different: "should i
# go to a&e for a cut" was answered "call 999 or 911 straight away" because `a&e` sits in the
# emergency list, which is an over-escalation and does not answer the question. Going is the plan;
# the phone is for the case that turns worse on the way. The place words only count as something
# to ring when the line has a calling word of its own in it ("should i call casualty").
_A_PLACE_TO_BE_SEEN = re.compile(r"\b(?:a&e|a and e|casualty|resus)\b")


_A_CALL_WORD = re.compile(r"\b(?:call|calls|calling|called|ring|rings|ringing|rang|phone|"
                          r"phoning|dial|dialling|dialing|999|911|112)\b")


# A small social decision - whether to send the message, ring round, go to the thing, say sorry -
# has a default a friend would give: do it, keep it short, and here is what the other way costs.
# "Should i text him first" was answered "not mine to decide, sorry", which is a wall in front of
# the most ordinary question in the language. Money and health keep their own pools (they are
# checked first) because there a wrong default does real harm.
_CONTACT = re.compile(r"\b(?:text|txt|ring|call|phone|message|msg|dm|email|mail|reply|answer|"
                      r"write|whatsapp|facetime|contact|reach out)\b")


AN_APOLOGY = re.compile(r"\b(?:say sorry|apologise|apologize|make up|make it up|own up|forgive me)\b")


ASKED_OUT = re.compile(r"\bask(?:ed)? (?:him|her|them|\w+) out\b|\bask (?:him|her|them) out\b")


# It has to be a thing you go to: "should i pay for my mates meal" is a money question and
# "should i do a dinner party" is about cooking, and neither is a decision about turning up.
_GOING = re.compile(r"\b(?:go|goes|going|attend|turn up|show up|make it)\b")


# "Yes, go" is the default for a wedding you have been asked to, and it is advice a friend would
# take back for one you were not: the decision there is whether to ask, not whether to turn up.
# (sky-tuna, #4381.)
_NOT_INVITED = re.compile(
    r"\b(?:wasnt|was not|werent|were not|havent been|have not been|didnt get|did not get|"
    r"no|not|never got|never received)\s+(?:\w+\s+){0,2}invit\w*"
    r"|\buninvited\b|\bwithout an invit\w*\b|\bgatecrash\w*\b", re.I)


# The reply has to match the act the line names: "should i ring my mum" answered "reply, and
# keep it to the one thing you want back" tells them to do something else.
_CALLING = re.compile(r"\b(?:ring|ringing|call|calling|phone|phoning|facetime|phone up)\b")


# A decision the person states instead of asking: "i'm not sure whether to move in with her",
# "i dont know if i should take the job", "i cant decide between the two flats". The question is
# in the line the other way round, so DECIDE_OPENING - which opens on "should i" - never sees it,
# and the line fell to the echo or the neutral nod: "Your girlfriend wants to move in and you're
# not sure - I'll remember that" files away the one thing the person asked for help with. The
# pool goes straight to what would move the decision, because the person has already said the
# thing UNKNOWN_DECIDE would say back to them.
DITHER = re.compile(r"\b(?:not sure|unsure|dont know|do not know|no idea|cant decide|"
                    r"cannot decide|cant make up my mind|cannot make up my mind|torn between|"
                    # "torn" without "between" is the same state and the commonest way to say it:
                    # "im torn about moving to leeds" named no sides, so it was filed away as a
                    # fact ("Noted: you're torn about moving to leeds").
                    r"(?<!not )torn about|(?<!not )torn over|(?<!not )torn on|"
                    r"(?<!not )torn|conflicted|dithering|undecided|"
                    r"in two minds|two minds about|of two minds|going back and forth|"
                    r"keep changing my mind)\b")


# "torn between", "in two minds", "cant make up my mind" can only be about a decision, so they
# carry the line on their own - including a bare "about <thing>" after them ("i cant make up my
# mind about the kitchen"), which on its own is not a decision at all: "im not sure about the
# paint colour" is a taste, and "i dont know about you but im starving" is a set phrase
# (rust-dial's read).
# "torn" only carries the line when the person is the one who is torn, because the same word is
# said of a thing that is ripped: "the page is torn", "my coat is torn" and "her dress is torn
# about the hem" are a repair, and "the tent is torn on the corner" is a hole in a tent. The
# preposition after it does not tell them apart - a person is torn about a job and a sheet is torn
# about here, in the same words - so the subject is what does, and it has to be a person saying
# "i", "we", "he", "she", "they" or "you" with the word, or a thing's own state ("seems torn",
# "sounds torn") about somebody. "torn apart" is left out for the same reason the other side is:
# it is grief, not two sides of a choice (spare-leopard's read).
DITHER_STRONG = re.compile(r"\b(?:(?<!not )torn between|"
                          r"(?:i|im|i m|i am|i was|i ve been|ive been|i feel|i felt|feel|"
                          r"feeling|we|we re|we are|we were|he|he s|he is|he was|she|she s|"
                          r"she is|she was|they|they re|theyre|they are|they were|you|"
                          r"you re|youre|hes|shes|"
                          r"you are|you were|seems|seemed|sounds|sounded|felt)\s+"
                          r"(?:so\s+|really\s+|very\s+|quite\s+|a bit\s+|still\s+)?"
                          r"torn\b(?! apart)|"
                          r"conflicted|dithering|undecided|two minds|"
                          r"going back and forth|cant decide|"
                          r"cannot decide|cant make up my mind|cannot make up my mind|"
                          r"keep changing my mind)\b")


# A doubt whose object is an open "what to do about this" names no sides at all ("i dont know what
# to do about money", "i dont know what to do next"), so neither "each way" nor "which way are you
# leaning" has anything to point at (sleek-jar on #2029). It gets a pool that asks what is in the
# way of the next step, which is what a friend says when the person has not found the choice yet.
DITHER_OPEN = re.compile(r"\bwhat to do\b|\bwhat (?:i|you) (?:should|can|ought to) do\b"
                         r"|\bwhat next\b")


# The same open doubt with the person named: "i dont know what to do about my mum", "what do i do
# about my son". `PERSON_NOT_A_DECISION` keeps these off the weighing pools on purpose - a person
# is not two sides to pick between - and what was left answered them with the echo ("I'm
# listening - say more if it helps") or the nod. The person is in the line, so the one helpful
# thing a fallback can do is ask about them.
# The person said with the words that describe them: "my teenage son", "our eldest daughter",
# "my 14 year old son", "my elderly mum". Those were named in the line and the pool asked about
# nobody ("I dont know enough... a quick search online"), because the reading expected the person
# straight after "about". Up to three words of description are allowed, and the tail check below
# keeps the pool off a line whose subject is a thing ("my sons school", "my child benefit").
STUCK_ON_A_PERSON = re.compile(
    r"\b(?:what to do|what (?:i|you) (?:should|can|ought to) do|"
    r"what (?:do|should|shall|can|could) (?:i|you|we) do)\s+(?:about|with)\s+"
    r"(?P<who>"
    r"(?:(?:my|our)\s+(?:[a-z0-9']+\s+){0,3})?"
    # The in-law forms come first: "mother" alone would take "my mother in law" and ask about
    # a mother the person never mentioned.
    r"(?:mother in laws?|father in laws?|sister in laws?|brother in laws?|"
    r"son in laws?|daughter in laws?|in laws|inlaws|husband|wife|partner|boyfriend|girlfriend|"
    r"brother|sister|son|"
    r"daughter|child|kid|boy|girl|baby|mum|mom|mother|dad|father|nan|gran|grandma|grandad|"
    r"grandpa|grandmother|grandfather|grandparents|grandson|granddaughter|friend|mate|boss|"
    r"colleague|neighbour|neighbor|in laws|inlaws|teenager|family|"
    r"teacher|carer|relative|cousin|uncle|aunt|nephew|niece|stepson|stepdaughter|ex)|"
    # A child named only by age is still a person: "our 2 year old", "my 18 month old". This is
    # read after the described form, so "my 14 year old son" keeps the son, and the tail check
    # stands the pool down when the age belongs to a thing ("our 2 year old car").
    r"(?:my|our)\s+\d+\s+(?:year|month|week)s?\s+old)"
    # The person must end a word: without this, "my son that school expelled" read the "ex" in
    # "expelled" as the person ("What is going on with your son that school ex at the moment?").
    r"(?![a-z0-9])"
    r"(?P<rest>.*)$")


# What may follow the person without changing who the line is about: "my ex now", "my son
# though", "my mum at the moment", or a second person named with them ("my son and my daughter").
# The tail is read as phrases from the front, not as a bag of single words: "at the moment",
# "at the minute", "right now" and "these days" are how the commonest forms of the question are
# said, and every one of them is more than one word (handy-lily's read). Read as single words,
# "what do i do about my mum at the moment" lost the answer the bare "my mum" already had.
STUCK_PERSON_TAIL_PHRASE = re.compile(
    r"^(?:"
    r"at the moment|at the minute|at the mo|at present|at this point|as it stands|"
    r"right now|just now|these days|nowadays|currently|"
    r"and thats it|thats it|i mean|i suppose|i guess|of all things|"
    r"now|today|tonight|though|then|please|anymore|any more|first|just|still|about|too|"
    r"either|really|honestly|seriously|actually|like|again|lately|all|eventually|so|and|"
    r"or|ok|okay|basically|thanks|cheers|please|now though|then though)"
    r"(?![a-z0-9])", re.I)


# A comma clause is about the same person when it says something of them rather than of a thing
# of theirs: "my boy, he is 15", "my daughter, she started school", "my son, 15". The subject
# has to be the person (he, she, they) or an age; "my son, his school" names a thing and stands
# the pool down, the same way the bare "my sons school" does.
STUCK_A_CLAUSE_ABOUT_THEM = re.compile(
    r"^,\s*(?:"
    r"(?:he|she|they|him|her|them)\b[ a-z0-9']{0,48}"
    r"|(?:aged|age)\s+\d{1,3}"
    r"|\d{1,3}\b[ a-z0-9']{0,24}"
    r")$")


STUCK_AND_ANOTHER_PERSON = re.compile(
    r"^(?:,\s*)?(?:and|or)\s+(?:(?:my|our)\s+)?[a-z0-9']+(?:\s+[a-z0-9']+){0,3}$")


# A tail that says more about the same person is still about them: "my ex that keeps texting me",
# "my partner of ten years", "my mum who wont go to the doctor". The words describe who they are
# to the person talking, not a thing of theirs, so the pool that asks about them is the right
# reply and standing it down was a regression (it used to ask "What is going on with your ex?").
STUCK_DESCRIBES_THE_PERSON = re.compile(
    r"^(?:,\s*)?(?:"
    r"(?:that|which|who|whose|whos|who's)\b[ a-z0-9']{0,40}"
    r"|(?:of|been|together|married)\b[ a-z0-9']{0,24}"
    r")$")


def _the_person_ends_the_ask(rest):
    """True when what follows the person is about the person, not a thing of theirs."""
    # Only the punctuation at the end is dropped: a comma at the front is the clause's own
    # opening ("my boy, he is 15") and `STUCK_A_CLAUSE_ABOUT_THEM` reads it.
    rest = str(rest or "").lstrip(" ").rstrip(" ?.!,")
    if not rest.strip(" ,?!."):
        return True
    if STUCK_AND_ANOTHER_PERSON.match(rest):
        return True
    if STUCK_DESCRIBES_THE_PERSON.match(rest):
        return True
    if STUCK_A_CLAUSE_ABOUT_THEM.match(rest):
        return True
    left = rest
    while True:
        found = STUCK_PERSON_TAIL_PHRASE.match(left)
        if not found:
            break
        left = left[found.end():].lstrip(" ,?!.")
    return not left


# A line that is nothing but the stuck phrase: "i dont know what to do", "no idea what to do
# next", "i have no idea what to do anymore". Every word left after the doubt is filler, so the
# line names nothing for any later pool to read - which is the test, because "this job is getting
# me down and i dont know what to do" is the wearing-down pool's line and has to keep it.
STUCK_ONLY_WORDS = frozenset("""
i im ive dont do not know have has got had no idea clue what to next now anymore any more really
even so just and but then about with still whats honestly right today hmm erm um please help
havent hasnt didnt doesnt a an at all
stuck where start begin beginning first how supposed even feeling bit feel need help
""".split())


# The words of a person with no way in: "i dont know what to do", "im stuck", "where do i start",
# "i dont know where to begin", "no idea what to do first". They name nothing and they are not a
# question about the world, so every pool here is asked rather than decided, and nothing in them
# guesses what the trouble is - the line has not said.
A_HELP_WORD = re.compile(r"\b(?:help|hand|advice)\b")


# The person saying they have run out rather than that they have no way in: "i dont know what
# else to do", "theres nothing i can do", "i dont know how to fix it", "i cant do this", "i give
# up". Read with the same "nothing else in the line" test as the stuck phrase, so "how to fix
# my boiler" is still the boiler and "i give up on my diet" is still the diet.
RUN_OUT = re.compile(
    r"\b(?:(?:what else|nothing else)(?:\s+(?:i|id|i'?d|to|can i))?\s*(?:do|can|try)\b|"
    r"what else\s*$|"
    r"nothing (?:(?:else|more) )?(?:i can do|to do|left|works?)\b|"
    r"what i can do\b|"
    r"(?:cant|cannot|can not) do (?:this|it)\b|"
    r"i give up\b|"
    r"no point(?:_in)?\b|"
    r"where to go from here\b|"
    r"how to fix (?:it|this)\b)", re.I)


# Saying the words alone is not running out: "we've seen all of fleabag and derry girls" then
# "what else" is a person asking for another series, and "what else can i do" as a first line is
# a question with no subject. The person has to say they do not know, or that nothing is left.
RUN_OUT_DOUBT = re.compile(r"\b(?:dont|do not|not|never)\s+(?:even\s+)?know\b|\bno idea\b|"
                           r"\bnot sure\b", re.I)


RUN_OUT_EMPTY = re.compile(
    r"\b(?:nothing (?:else |more )?(?:i can do|to do|left|works?)|theres nothing|"
    r"(?:cant|cannot|can not) do (?:this|it)|i give up|no point)\b", re.I)


STUCK_PHRASES = re.compile(
    r"\b(?:stuck|what to do|where (?:do|should|would) i (?:start|begin)|"
    r"(?:where|how) to (?:start|begin)|where i (?:start|begin)|"
    r"(?:what|which) (?:to do )?first|what with)\b")


# "the baby wont stop crying", "my mum has dementia", "he has not rung me back" - the line above
# names somebody or something of theirs, so the stuck line that follows is about that, whether
# or not the readings above called it bad news (a crying baby is not). A line about the person
# alone names nothing to ask about: "im 34" then "i dont know what to do" keeps the open pool.
A_SUBJECT_ABOVE = re.compile(
    r"\b(?:my|our|his|her|their|the|he|she|they|him|them)\s+[a-z]")


RUN_OUT_WORDS = STUCK_ONLY_WORDS | frozenset("""
else id cant cannot can not give up point left works fix it this go from here try anything
nothing theres there to
""".split())


def _run_out(clean):
    """True when the line says only that they have run out of options, and nothing else."""
    words = re.findall(r"[a-z']+", clean)
    if not words or not RUN_OUT.search(clean):
        return False
    if not (RUN_OUT_DOUBT.search(clean) or RUN_OUT_EMPTY.search(clean)):
        return False
    return all(word.strip("'") in RUN_OUT_WORDS for word in words)


def _a_dead_end(clean):
    """True for either kind of line that names nothing: no way in, or no way left."""
    return _only_the_stuck_phrase(clean) or _run_out(clean)


def _only_the_stuck_phrase(clean):
    """True when the line says only that they do not know what to do, and nothing else."""
    words = re.findall(r"[a-z']+", clean)
    if not words or not STUCK_PHRASES.search(clean):
        return False
    return all(word.strip("'") in STUCK_ONLY_WORDS for word in words)


DITHER_YES_NO = re.compile(r"\b(?:whether|if)\b")


# A question about the *method* of deciding, not about a decision already on the table: "how
# should i decide", "how do i work out which one", "how do i choose". None of them names a doubt
# (so `DITHER` never sees them) and none is a fact to look up, so on main they fell through to the
# search hedge - "a quick search online will get you a solid answer" - which is wrong twice over:
# the method is general, and the bot does know it. The pool names the two questions that settle
# most of these and asks for the sides, because the sides are the one thing only the person has.
HOW_TO_DECIDE = re.compile(
    r"\bhow (?:should|do|can|could|would|might|will) (?:i|we) (?:decide|choose|pick|"
    r"work (?:it |that |this )?out|figure (?:it |that |this )?out|know which|tell which)\b"
    r"|\bhow (?:do|should|can) i (?:make|reach|come to) (?:a |the )?decision\b"
    r"|\bwhats?\s+(?:is\s+)?the best way to (?:decide|choose|pick)\b")


# A method question is about the method only when the verb ends the thought or names the sides:
# "how do i choose" and "how do i decide between the two jobs" are the method, while "how do i
# choose a wine", "how do i pick my lottery numbers" and "how do i work out my tax" name a subject
# that owns the answer - and the pool's "what are the two options?" has no two options to ask about
# in them.
SAYS_THE_SIDES = re.compile(r"\W*(?:between\b|whether\b|if\b|which (?:one|of|to)\b)")


def _nothing_to_choose(rest):
    """True when what follows "how do i decide/pick/choose" names no subject of its own."""
    if SAYS_THE_SIDES.match(rest):
        return True
    words = re.findall(r"[a-z0-9']+", str(rest or "").lower())
    return not [w for w in words if w not in HOW_TO_DECIDE_FILLER]


# A decision with two sides the person can name is weighed here: "whether to move in with her",
# "between the two flats", but also "my girlfriend wants to move in and im not sure", where the
# doubt is the decision and nobody needs to ask which two things are being weighed.
DITHER_TWO_WAY = re.compile(r"\b(?:whether|if|between|or|which)\b")


# The one class this reader passes on: a line asking for a direction rather than weighing a
# choice ("i dont know what to do with my life", "im 34 and i still dont know what i want to
# do"). There is no second side to hold up there, so "which way are you leaning" asks about a
# choice the person has not found yet. That class belongs to the neutral branch's own
# worth-and-direction pool: one pool per line class, and this one is not mine.
LIFE_DIRECTION = re.compile(r"\b(?:with|out of|from) my life\b|\bwhat i (?:actually )?want to do\b"
                            r"|\b(?:twenties|thirties|forties|20s|30s|40s)\b"
                            r"|\bnothing (?:feels|seems) right\b"
                            r"|\bwhat (?:am i|im) (?:even )?doing with my life\b")


# A stretch of free time is not a choice with two sides to weigh either. "no idea what to do with
# my afternoon" is somebody with an afternoon going spare, and "Which bit of it is heaviest?" -
# the right question for a person carrying too much - asks them to name the heavy part of a free
# afternoon. Said with a day or a weekend in it, the line already reached the pool that gives the
# day a shape; the afternoon was the one form that did not.
A_STRETCH_OF_TIME = re.compile(
    r"\bwhat (?:to|should i|can i|could i|shall i) do (?:with|on|for)\s+(?:my|the|this|these)\s+"
    r"(?:afternoon|evening|morning|day off|day|weekend|week|time|night|days off|holidays?)\b")


def _weighs_a_choice(clean):
    """True when the doubt has sides the person can name, so weighing it helps.

    A life-direction line has none ("i dont know what to do with my life") and neither does a free
    afternoon, and this reader passes on both rather than asking which way the person is leaning:
    the rest of `reply_for` - the echo and the neutral pool - still answers them, and further down
    the line the pools that give a day a shape read them.
    """
    if DITHER_TWO_WAY.search(clean):
        return True
    return not (LIFE_DIRECTION.search(clean) or A_STRETCH_OF_TIME.search(clean))


# "the difference between the two", "the gap between them", "the time between the trains": a
# "between" inside a fact is not two sides to weigh, and "i dont know the difference between the
# two" was being asked "What's pulling you each way?" - a real question answered with a shrug.
FACT_BETWEEN = re.compile(r"\b(?:difference|differ|gap|distance|space|time|line|border|"
                          r"connection|link)\s+(?:\w+\s+)?between\b")


# A service you go to for help is not one side of a decision. "not sure whether to go to a and
# e" and "im not sure whether to take him to the vets tonight" are someone asking what to do
# about a body, and "What's the thing you would lose if you said yes?" answers a trade-off nobody
# named (warm-feather on #1467). Only a motion towards the service counts: the hospital job is
# still a job, and "should i move to be near the hospital" is still a move.
HELP_SERVICE = re.compile(
    # "take the hospital job" is a job, so a motion verb only counts when the service is where
    # the person is going: the "to" is what makes it a destination.
    r"\b(?:go|going|went|get|getting|take|taking|took|bring|bringing|drive|driving|rush|rushing|"
    r"walk|walking)\b(?:\s+\w+){0,3}?\s+(?:to\s+|into\s+)"
    r"(?:a and e|a&e|999|111|casualty|the hospital|hospital|the doctor|a doctor|doctor|"
    r"the doctors|doctors|the gp|gp|my gp|the surgery|the vets|vets|the vet|vet|"
    r"walk in centre|urgent care|out of hours|the pharmacy)\b"
    # and a call or a visit names the service as its object, with no "to" at all.
    r"|\b(?:call|called|calling|ring|ringing|rang|phone|phoned|phoning|see|seeing|saw|book|"
    r"booking|booked)\b\s+(?:999|111|an ambulance|the doctor|a doctor|the gp|the surgery|"
    r"the vets|the vet|a vet|urgent care)\b")


# A person is not a decision object either: "what to do about my husband" is a row to talk
# through, not two versions of the same day (warm-feather and gray-cypress on #1467), and "what
# to do about it" has no it to weigh. "about money" still is a decision: something can be done
# with money. This is a check on the object, so the cue itself stays whole.
PERSON_NOT_A_DECISION = re.compile(r"\bwhat to do (?:about|with) (?:my|his|her|our|their|the)\s+"
                      r"(?:husband|wife|partner|boyfriend|girlfriend|brother|sister|son|"
                      r"daughter|child|kid|boy|girl|baby|mum|mom|mother|dad|father|nan|gran|"
                      r"grandma|grandad|grandpa|friend|boss|colleague|neighbour|neighbor|"
                      r"in laws|inlaws|teenager|family|teacher|carer|relative|cousin|uncle|"
                      r"aunt|nephew|niece|ex|stepson|stepdaughter)\b")


# "i dont know what to do about it" / "about that": a pronoun is the thing already mentioned,
# not two ways out, so the line wants a conversation rather than a weighing.
PRONOUN_NOT_A_DECISION = re.compile(r"\bwhat to do (?:about|with) (?:it|this|that|him|her|them|us|me|"
                       r"everything|anything|nothing)\b")


# A health word can be a place or a thing rather than a body: "i dont know whether to take the
# hospital job" is a job, and the advisor's line ("Ring 111 or your surgery") answers a body.
HEALTH_MODIFIER = re.compile(r"\b(?:hospital|doctors?|surgery|clinic|vets?)\s+"
                             r"(?:job|jobs|shift|shifts|appointment|appointments|letter|"
                             r"letter|bill|parking|car park|contract|rota|placement|course|"
                             r"uniform|policy|department|ward)\b")


def _reads_as_dither(clean, repaired=None):
    """True when the line says a decision is unresolved, rather than asking which way to go.

    The line is read as it was typed and then with its words put right. "i dont no what to do
    about my job" is "dont know" with a word typed for the sound of it, and only the repaired
    line spells "know": read as typed the doubt was invisible, so the line went past every pool
    to the neutral nod ("Thanks for telling me - I'm here if you want to dig into any of that")
    while the same line typed with "know" answered it. The refusals are per spelling, so a line
    that is not a doubt either way stays as it was.
    """
    lines = [clean]
    if repaired and repaired != clean:
        lines.append(repaired)
    for line in lines:
        if FACT_BETWEEN.search(line):
            continue
        if (PERSON_NOT_A_DECISION.search(line) or PRONOUN_NOT_A_DECISION.search(line)
                or HELP_SERVICE.search(line)):
            continue
        if DITHER.search(line) and (DITHER_STRONG.search(line) or DITHER_SUBJECT.search(line)):
            return True
    return False


# A decision question opens with the decision ("should I", "is it worth"). "What should I know",
# "when should I plant tulips" ask for information, so they stay with the fact pool.
#
# "Do I <say / tell / ask / text / call ...>" is the same decision in the present tense: "do i
# accept the offer" and "do i say yes" are asking the bot to pick a side, and the search hedge
# ("I'm not sure about that one, sorry - a quick search will get you a solid answer") is no help
# with a choice that is the person's own. Only the verbs that name an act of their own are here,
# and only straight after "do i": "do i need to tell the council" is a question about the rules
# and keeps its hedge, which is why nothing may come between "do i" and the verb. "go" and
# "write" are out on purpose - "do i go" names nothing at all, and the pools behind it guess an
# evening out ("an evening out costs less than the regret"), while "do i write to them" reaches
# the drafting pool and assumes a draft nobody said they had.
DECIDE_OPENING = re.compile(r"(?:^|[,.!?;]\s*|\b(?:so|but|then|and|ok|okay)\s+)"
                            r"(?:should (?:i|we)|shall (?:i|we)|is it worth|is it better|"
                            r"would it be better|"
                            r"which (?:one )?should i|(?:do |)(?:you|u|ya) (?:think|reckon) i should|"
                            r"what would you do|"
                            r"do i (?:say|tell|ask|mention|reply|text|call|ring|accept|"
                            r"send|bring)\b|"
                            r"would you)\b")


# A decision is also asked the other way round, as a check on the asker's own sanity: "would
# moving closer be mad", "would it be weird to go back to college at 40", "is it stupid to buy a
# new one", "would i be mad to sell", "would it look bad if i said no". None of those names a
# fact to look up, and main sent them to the search hedge - "Searching for it will turn up better
# sources than I can offer" - which is no help with a choice that is the person's own. The word
# that carries the question is the verdict on the asker (mad, weird, stupid, selfish, rude), so it
# is that word the pattern asks for, wherever the sentence puts it.
DECIDE_SANITY = re.compile(
    # "would moving closer be mad", "would it be weird to go back to college at 40", "would a
    # tattoo look stupid" - a modal with the verdict on the thing the person is weighing.
    r"\b(?:would|will|does|do|is|was|are)\b[^.?!]{0,34}?\b(?:be|look|seem|sound)\s+"
    r"(?:like\s+)?(?:a\s+|an\s+)?(?:mad|crazy|stupid|silly|nuts|weird|strange|odd|bizarre|"
    r"selfish|unreasonable|rude|cheeky|bad|wrong|over\s+the\s+top|a\s+mistake)\b"
    # "am i being stupid", "am i unreasonable about this", "was i out of order"
    r"|\b(?:am|are|was)\s+(?:i|we)\b[^.?!]{0,20}?\b(?:being\s+|just\s+|so\s+|too\s+)?"
    r"(?:mad|crazy|stupid|silly|selfish|unreasonable|a\s+fool|out\s+of\s+order|"
    r"over\s+the\s+top)\b"
    # "is it mad to get a dog", "would it be a bad idea to just stop paying"
    r"|\b(?:is|would|was)\s+it\s+(?:mad|weird|stupid|silly|crazy|a\s+mistake|a\s+bad\s+idea|"
    r"wrong)\s+to\b"
    # "mad idea to...", "weird thing to say"
    r"|\b(?:mad|weird|stupid|silly|crazy)\s+(?:idea|thing)\s+to\b"
    # "would it look bad if i said no", "does it look bad to turn it down"
    r"|\b(?:would|does|will|did)\s+(?:it|that|this)\s+look\s+(?:bad|silly|stupid|mad|odd|"
    r"weird|rude)\b"
    # "is it weird that i want to move": the verdict on the feeling rather than on the act
    r"|\b(?:is|was|would)\s+it\s+(?:weird|strange|odd|stupid|silly|crazy|mad|selfish|"
    r"unreasonable)\s+that\b")


# "What's a password manager and should I use one?" asks for a fact first: the decision is the
# second half of the line, so the fact pool stays.
_DEFINITION = re.compile(r"^\s*(?:what|what's|whats|wats)\s+(?:is|are|was|were|does|do)\b"
                         r"|^\s*what(?:'s|s)?\s+(?:a|an|the)\b"
                         r"|^\s*(?:explain|tell me about|define)\b|\bwhat does .* mean\b")


# Where a person says a thing on the body is, they have said it is on the body. "on" alone is not
# enough - "a spot on the map" - so the word after it has to be one a body can own.
SORE_PLACE = re.compile(
    r"\b(?:my|under my|behind my|between)\b"
    # "should i pop this spot" points at one on the person: a campsite is not popped.
    r"|\b(?:this|that)\s+(?:spot|sore|lump)s?\b"
    r"|\bon (?:my )?\w*(?:chin|cheek|face|jaw|nose|forehead|lip|ear|neck|back|shoulder|arm|"
    r"armpit|elbow|wrist|hand|finger|thumb|leg|thigh|knee|shin|ankle|foot|feet|heel|toe|"
    r"chest|breast|belly|stomach|bottom|bum|groin|skin|scalp|eyebrow|eyelid|head|hip|side)\b"
    r"|\b(?:chin|cheek|forehead|jaw|armpit|elbow|wrist|thumb|knee|shin|ankle|heel|toe|"
    r"scalp|eyelid|eyebrow|breast|groin)\b")


# The same question in any frame: "can i squeeze a boil", "is it ok to squeeze a boil", "do i
# squeeze a boil". The deciding word is the doing - squeeze, pop, lance, prick - pointed at a
# sore, and that is a health question whether or not it opens on "should i".
SORE_DOING = re.compile(r"\b(?:squeeze|squeezing|squeezed|pop|popping|popped|lance|lancing|"
                        r"prick|pricking|burst|bursting|drain|draining|pick|picking|scratch|"
                        r"scratching)\b")


# One of those verbs fits a body and nothing else: a campsite is not squeezed, popped or drained.
# "Pick" is the one that fits both - you pick a spot for a tent and you pick a scab - so a line
# whose only doing verb is "pick" has to say whose spot it is before it is a sore.
SORE_PICKING = re.compile(r"\b(?:pick|picking|picked)\b")


SORE_ONLY_A_BODY = re.compile(r"\b(?:squeeze|squeezing|squeezed|pop|popping|popped|lance|"
                             r"lancing|prick|pricking|burst|bursting|drain|draining|scratch|"
                             r"scratching)\b")


PLASTER_ON = re.compile(
    r"\b(?:put |a |some )?plaster\b[^.]{0,18}?\bon (?:it|this|that|there|them|my \w+)\b"
    r"|\b(?:put |a |some )?(?:bandage|dressing|antiseptic|compress)\b[^.]{0,18}?"
    r"\bon (?:it|this|that|there|them|my " + _WOUND + r")\b"
    r"|\b(?:cover|cover it|covering)[^.]{0,16}"
    r"\b(?:plaster|bandage|dressing)\b"
    # "put an antiseptic on my cut" names the wound after the covering, not before it
    r"|\b(?:bandage|dressing|antiseptic|compress|plaster)\b[^.]{0,6}?\b(?:on|over) "
    + _WOUND + r"\b")


# `pay` on its own is "pay for my mate's meal": the money pool is for paying a debt, and those
# lines say so with the particle.
_PAY_DEBT = re.compile(r"\bpay(?:s|ing|ed)?\s+(?:it\s+|them\s+|that\s+)?(?:off|back|down|into|up)\b")


# A card is a birthday card as often as a credit card: only the money ones are money.
# A card is a birthday card unless the line names the kind, or does something to it that only a
# bank card can have done to it: you cancel, freeze and block a bank card, not a greetings one.
_CARD_MONEY = re.compile(
    r"\b(?:credit|debit|bank|store)\s+cards?\b|"
    r"\b(?:cancel|freeze|block|replace|stop|report|stolen|lost|cloned|skimmed)\s+"
    r"(?:my|the|that|this|our|a)\s+cards?\b|"
    r"\bcards?\s+(?:was|is|got)\s+(?:cloned|skimmed|stolen|lost)\b")


# "Is it worth paying for an inspection?" weighs whether a thing is worth its price: the money pool
# is for money decisions, and nothing money-shaped is being decided in that line.
_VALUE_OF_THING = re.compile(r"\bis it worth (?:paying|paying for|getting|having|going for|"
                             r"splashing out on)\b")


# "is that ok or am i overreacting" is a person asking to be reassured, not a question of fact,
# and "I'd rather not guess, do a search" answers it by sending them to Google. The worry has a
# shape of its own, so it gets a pool that takes the feeling seriously and hands the judgement
# back to them, which is the only honest answer to "is how I feel fair".
# Only a worry about the person's own reaction belongs here. "is that normal" about a knee, a
# kitten or a baby's sleep is a question of fact and the honest answer is to look it up; the
# deck has six of those, and answering them with "you don't need to prove it's bad first" is
# worse than the search line it replaced.
# The shape is the person asking about *their own reaction* ("am i overreacting", "am i making a
# fuss"), which is always a reassurance ask. A bare "is that normal / weird / bad" is not enough:
# the deck has a knee that clicks, a freezer making a noise, a baby waking twice a night and a
# kitten that bites, and all four are questions of fact where the honest answer is to look it up.
WORRY_SELF = re.compile(r"\b(?:am i (?:overreacting|overthinking|over-thinking|over thinking|"
                         r"reading too much(?: into (?:it|this))?|being|mad|unreasonable|silly|"
                         r"wrong|too much|too sensitive|over the top)|overreacting|"
                         r"making a (?:fuss|big deal)|too sensitive)\b")


# "should i worry" is the same ask, but only when it is the whole ask: "should i worry about my
# knee" or "my laptop sounds like a plane, should i worry" is a question about a knee or a laptop,
# and the reassurance pool reads for a feeling. Bare, it is about the person's own state of mind.
SHOULD_WORRY = re.compile(r"\bshould i (?:be )?(?:worried|worry|worrying)\b")


WORRY_SHAPE = re.compile("(?:" + WORRY_SELF.pattern + "|" + SHOULD_WORRY.pattern + ")")


# What is left of the line once "is it ok or should i worry" has nothing in it but filler: that
# leftover being empty is what makes a "should i worry" bare.
SHOULD_WORRY_FILLER = re.compile(r"\b(?:is|it|that|this|ok|okay|so|or|and|but|then|now|just|"
                                 r"really|honestly|about|i|me|a|bit)\b")


# "is that weird" and "is it normal to feel like this" ask the same thing as "am i overreacting":
# whether their own reaction is allowed. It is not a question of fact, and the search hedge
# answered it by sending them to look up whether their feelings are normal - "i got the promotion
# and i dont feel happy about it. is that weird?" got "a search should sort you out quickly". The
# bare form is a real question of fact when it is about a thing, which is why `_reads_as_worry`
# leaves it out ("my knee clicks, is that normal", "is it normal for a puppy to sleep all day"),
# so it counts only when their own feeling is what is being judged.
WEIRD_ASK = re.compile(r"\b(?:is|was|isnt|am i)\s+(?:that|this|it)\s+(?:a bit |really |actually |so )?"
                       r"(?:weird|normal|normalish|strange|odd|wrong|bad)\b"
                       r"|\bis it (?:weird|normal|strange|odd)\b"
                       r"|\bam i (?:weird|strange|odd|abnormal)\b")


# What makes that ask about a feeling rather than about a thing: a feeling word in the line, or in
# the last thing they said ("i feel flat" / "is that normal").
FEELING_SAID = re.compile(r"\b(?:feel|feels|feeling|felt|happy|unhappy|sad|guilty|angry|upset|cry|"
                          r"cried|crying|tears|flat|numb|empty|lonely|miss|hate|proud|ashamed|"
                          r"embarrassed|scared|anxious|relieved|gutted|glad|miserable|"
                          r"heartbroken)\b")


# The whole line, because "is it too late to plant potatoes" names its own subject and belongs to
# the knowledge base. A bare "is it too late to start" is the same ask as "is that too late" when
# the turn before it is the person saying what they are starting.
TOO_LATE = re.compile(
    r"^(?:and |but |so |ok |okay )?(?:is|was|isnt) (?:that|this|it) (?:too|a bit too|a little too) "
    r"(?:late|old)(?: now| then| in the day)?$"
    r"|^(?:and |but |so )?am i (?:too|a bit too|a little too) (?:old|late)(?: for (?:it|this|that))?$"
    r"|^(?:and |but |so )?is (?:that|this|it) (?:too|a bit too) old for me$"
    r"|^(?:and |but |so )?have i (?:left it|started it) too late$"
    r"|^(?:and |but |so )?is it too late for me$"
    r"|^(?:and |but |so )?is \d{1,2} too old(?: for (?:it|this|that))?$"
    r"|^(?:and |but |so )?is it too late to (?:start|begin|learn)(?: now| at my age)?$"
)


# "is that realistic" / "is that too ambitious" / "do you think thats doable": the same doubt as
# "is that too late" with another word in it, asked of a plan instead of an age. Anchored, and with
# no subject of its own, so a question that names its thing stays where it is: "is it feasible to
# freeze milk" is a knowledge question and "is that realistic for a plumber to charge" is the
# price readers' (the "for <thing>" tail is the reason a rate is being asked about).
REALISTIC = re.compile(
    r"^(?:and |but |so |ok |okay |right )?(?:is|was|would|will) (?:that|this) (?:even )?(?:be )?"
    r"(?:a )?(?:realistic|doable|achievable|feasible|plausible|too ambitious|unrealistic)"
    r"(?: for (?:me|us|you))?$"
    r"|^(?:and |but |so |ok |okay )?is (?:that|this) enough time(?: for (?:me|us|you))?$"
    r"|^(?:and |but |so )?can (?:i|we) really (?:do|manage|fit|swing) (?:that|this|it)$"
    r"|^(?:and |but |so )?(?:am i|are we) (?:being )?(?:too ambitious|aiming too high|overdoing it)$"
    r"|^(?:and |but |so )?do you think (?:that|this|it|its|it's|thats|that's) (?:is |would be )?"
    r"(?:a )?(?:realistic|doable|achievable)$"
)


# The same doubt said about the person: "am i being unrealistic", "am i aiming too high". Those
# are also the words somebody uses about a hope or a person ("he says im being unrealistic, am i"),
# and there the reassurance pool has the better line, so this reading wants a plan under it: the
# line or the turn before it says what the plan is, or the thread is one they have just started.
REALISTIC_ABOUT_ME = re.compile(
    r"^(?:and |but |so )?(?:am i|are we) (?:being )?unrealistic$"
)


# What counts as a plan in the line or the turn before it. A month, a span of weeks, a distance, a
# course, a target: the words a person uses when they are telling the bot what they intend to do.
PLAN_WORDS = re.compile(
    r"\b(?:plan|plans|planning|goal|target|deadline|budget|train(?:ing)?|course|classes|lessons|"
    r"marathon|half marathon|10k|5k|parkrun|diet|saving|save)\b"
    r"|\b(?:in|by|before|until) (?:a |one |two |three |four |five |six |seven |eight |nine |ten |"
    r"\d+ )?(?:week|weeks|month|months|year|years|january|february|march|april|may|june|july|"
    r"august|september|october|november|december|spring|summer|autumn|winter|christmas|easter)\b"
    r"|£\s?\d|\d+\s?k\b")


# Somebody close who will not have the thing that would help them: the alarm, the stick, the trip to
# the doctor, a carer in the house. This is the person caring for them talking, and the line reached
# the fallback as "Got it. Is there anything you'd like a hand with?" - a shrug for somebody who has
# just said their mother refuses the pendant alarm. It is not a question of fact, so the search hedge
# is wrong too; what the bot can say is what the refusal is usually about and whose word carries.
SOMEONE_CLOSE = re.compile(
    r"\b(?:my|his|her|our|their)\s+(?:mum|mom|mother|mam|dad|father|pa|nan|nana|nanna|gran|"
    r"granny|grandma|grandad|grandpa|grandmother|grandfather|mother\s+in\s+law|"
    r"father\s+in\s+law|aunt|auntie|uncle|neighbour|neighbor|husband|wife)\b"
    # "hes 80 and wont use a stick", "shes turning 80 and doesnt want a fuss": the pronoun needs
    # an age on it, or "she wont text me back" is read as somebody's mother refusing a carer.
    r"|\b(?:he|she|hes|shes|he's|she's|they|theyre|they're)\b[^.!?]{0,25}?"
    r"\b(?:[7-9]\d|1\d\d|elderly|pensioner|oap|in (?:his|her|their) (?:70s|80s|90s))\b",
    re.I)


# The same refusal said of somebody with no relation named: "she refuses a pendant alarm" is as
# often a mother as a wife, and the line has no noun to tell you which. The aid, the doctor or the
# carer in the line is what makes it this reading, so the pronoun only has to be a person - and a
# child is excluded below, because a four-year-old refusing a coat is a different conversation.
SOMEONE_ELSE = re.compile(r"\b(?:she|he|they|him|her|them)\b", re.I)


A_CHILD = re.compile(
    r"\b(?:my|our|his|her|their)\s+(?:son|daughter|child|children|kid|kids|baby|toddler|"
    r"boy|girl|little\s+one|teenager|teen)\b"
    r"|\b(?:hes|shes|he's|she's|theyre|they're)\s+(?:one|two|three|four|five|six|seven|eight|"
    r"nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|18 months)\b", re.I)


REFUSES_IT = re.compile(
    r"\b(?:wont|won't|will\s+not|refuses|refused|refusing|doesnt\s+want|doesn't\s+want|"
    r"didnt\s+want|didn't\s+want|does\s+not\s+want|will\s+not\s+have|wont\s+have|"
    r"won't\s+have|wont\s+let|won't\s+let|wont\s+accept|won't\s+accept)\b", re.I)


# The thing refused, in the three families the reply can speak to. An object and a pet fall out of
# this on their own: "the dog flap wont close" and "my car wont start" name no person to refuse.
AN_AID = re.compile(
    r"\b(?:stick|sticks|walking\s+stick|frame|zimmer|walker|rollator|pendant|alarm|"
    r"bath\s+lift|shower\s+seat|grab\s+rails?|"
    r"key\s+safe|stairlift|commode|incontinence\s+pads?)\b", re.I)


# The aids that are settled in a clinic rather than by a home visit: an optician's test, an
# audiologist's test. The occupational therapist who comes out with a stick has nothing to say
# about a pair of glasses, so these have their own words.
A_CLINIC = re.compile(
    r"\b(?:hearing\s+aids?|glasses|specs|spectacles|dentures|contact\s+lenses|"
    r"hearing\s+test|eye\s+test)\b", re.I)


THE_DOCTOR = re.compile(
    r"\b(?:doctor|doctors|doctor's|gp|gps|surgery|hospital|"
    r"appointment|check\s*-?\s*up|blood\s+test|scan|physio\w*|dentist|optician|"
    r"memory\s+clinic|chiropodist)\b", re.I)


# "a carer in the house" and not a day centre or a club: the reply for people coming in is about
# who comes in, and "she wont go to a club" is the different question of leaving the house.
HELP_IN = re.compile(
    r"\b(?:carers?|care\s+worker|home\s+help|help(?:ing)?\s+(?:in|out|around)|anyone\s+in|"
    r"somebody\s+in|someone\s+in|anybody\s+in|strangers?\s+in|a\s+cleaner|cleaner|"
    r"home\s+care|meals\s+on\s+wheels|respite|a\s+carer|paid\s+help|"
    r"district\s+nurse|the\s+nurse|nurse\s+in|occupational\s+therapist|ot\s+in)\b", re.I)


def _a_carer_refused(clean):
    """Which of the three refusals "my mum wont ..." is, or None for every other line."""
    if not REFUSES_IT.search(clean) or A_CHILD.search(clean):
        return None
    if not (SOMEONE_CLOSE.search(clean) or SOMEONE_ELSE.search(clean)):
        return None
    if A_CLINIC.search(clean):
        return "clinic"
    if AN_AID.search(clean):
        return "aid"
    if THE_DOCTOR.search(clean):
        return "doctor"
    if HELP_IN.search(clean):
        return "help"
    return None


def _a_plan_doubt(pred, clean, repaired):
    """True when the doubt is the whole line, or the clause after the plan it is about.

    "im doing a 10k in may, is that realistic" puts the plan and the doubt in one line with a
    comma between them, and an anchored reading of the whole line misses it. Only the clause
    after the last comma is tried, so a line that keeps talking after the ask ("is that realistic
    to run on") is still not this one.
    """
    for text in (clean, repaired):
        if pred(text):
            return True
        tail = text.rsplit(",", 1)[-1].strip() if "," in text else ""
        if tail and pred(tail):
            return True
    return False


# The same doubt said as a fact about themselves instead of as a question: "i want to start
# running" / "im 44 and quite unfit" was answered "Got it. Is there anything you'd like a hand
# with?", which reads as if the person had said nothing at all. Age and being unfit are the two
# things people offer as a reason not to start, so the statement is read the same way as "am i
# too old": only after they have said what they are starting, and not in a body thread, where
# "im 34 and my knee gives way when i run" is a knee question.
_AGE_DOUBT = re.compile(r"\b(?:old|older|age|aged|past it|spring chicken|\d{2})\b", re.I)


A_BIT_PAST_IT = re.compile(
    r"^(?:and |but |so |well |also )?(?:im|i'?m|i am)\s+(?:"
    r"\d{1,2}\s*[,;]?\s*(?:(?:and|but|now)\b|,)[^.!?]*"
    r"|(?:quite |very |pretty |a bit |a little |really |fairly |properly |so |"
    r"not that |not especially )?"
    r"(?:unfit|overweight|old|out of shape|out of practice|past it|no spring chicken|"
    r"fit as i was|as fit as i was)\b[^.!?]*"
    r"|(?:not|no longer|less than|hardly)\s+(?:very\s+|that\s+|especially\s+)?"
    r"(?:fit|strong|sporty|good at it)\b[^.!?]*)")


# What the person says when they are taking something up themselves. The doubt is about their own
# starting, so the line before has to be that: "the last train is at nine" / "is that too late" is
# about a train, and the age-and-a-start pair ("i started piano last year" / "im 52") is the same
# doubt said twice, so the words may be one turn back.
TAKING_UP = re.compile(
    r"\b(?:im|i'm|i am|ive|i've|i) "
    r"(?:(?:just|finally|also|now|really|still|even) )?"
    r"(?:(?:thinking (?:of|about)|want(?:ing)? to|try(?:ing)? to|hoping to|planning to|"
    r"about to|going to) )?"
    r"(?:start(?:ing|ed)?|learn(?:ing|t)?|began|beginning|tak(?:e|ing) up|took up|"
    r"going back to|back at|get(?:ting)? (?:back )?into|join(?:ing|ed)?|"
    r"sign(?:ing|ed)? up (?:for|to))\b")


def _a_bare_worry(clean):
    """True when "should i worry" is the whole ask, not attached to a thing they describe."""
    found = SHOULD_WORRY.search(clean)
    if not found:
        return False
    rest = clean[:found.start()] + " " + clean[found.end():]
    rest = SHOULD_WORRY_FILLER.sub(" ", rest)
    return not re.sub(r"[^a-z0-9]", "", rest)


def _worry_is_about_the_body(clean, words):
    """True when the worry names a body part, a symptom or a health service."""
    words = set(words)
    return bool(words & BODY_PARTS or words & HEALTH_WORDS or words & SYMPTOM_WORDS
                or any(phrase in clean for phrase in CHECK_PHRASES))


# "is he going to be ok", "how long is she likely to be in", "is that just age": the ask a
# person makes about somebody the bot has never met, after naming what happened to them. Every
# one of these got the search hedge ("A quick search online will get you a solid answer"), which
# is the one reply that cannot be right here: no website knows this dad, and the answer is sitting
# with the people looking after him. Nobody here can examine anybody, so the honest line names who
# can and asks the one thing only the person in the room can say.
UNKNOWN_HOW_IT_GOES_FOR_SOMEONE = (
    "Only the people looking after them can say, and they will tell you straight if you ask - "
    "their own GP, whoever is treating them. What has changed since you last heard?",
    "I would be guessing, and this is not a thing to guess about. Ask whoever is treating them, or "
    "ring 111 if it has got worse today. How are they in themselves?",
    "That one is with the people who can see them, not with me. Ask it plainly when you next speak "
    "to them, and if they fob you off, ask again. What were you told last?",
    "Nobody can promise how it will go, and anyone who does is guessing too. Their GP will give "
    "you the honest picture, and asking is not fussing. What worries you most?",
    "I cannot know that from here and I will not pretend to. Ring their GP and ask it as you asked "
    "me - they answer this every day. How long has it been like this?",
)


# The same ask in a thread that already has somebody in a bed: "how long is she likely to be in"
# after "my mums in hospital". A ward is the place to ask, not a GP's phone line and not 111.
UNKNOWN_HOW_LONG_IN_HOSPITAL = (
    "How long is the ward's to say, and they will tell you: ask for the plan in days rather than "
    '"a while", and ask who to ring for updates. What have they said so far?',
    "That depends on what they are treating, so it is their team's answer rather than mine. Ask "
    "what has to happen before they can come home - that is the number that matters. Have they "
    "given you a plan?",
    "Nobody here can say, and the team looking after them will: they give a rough plan and revise "
    "it as things change. Ask what to expect over the next few days. How are they in themselves?",
)


# A rough patch is not a patient: there is a body in a ward, and there may be nothing wrong with a
# person who is having a hard time. Sending them to a ward names a doctor who has never heard of
# them, and a search hedge tells them nothing, so this is the pool for "is she going to be ok"
# about somebody who is struggling rather than ill: only they can say, the question is worth
# asking, and the GP is where it turns into a medical question if it goes on.
UNKNOWN_HOW_IT_GOES_FOR_A_HARD_TIME = (
    "Only they can say how they are doing, and asking them is worth more than a guess from me. Ask "
    "how they are in themselves. If it has been weeks rather than days, their GP is the place to "
    "start - that is what they are there for.",
    "I cannot tell you how somebody else is going to be, and anyone who says they can is guessing. "
    "Ask them straight, and ask again if the first answer is that they are fine. If it drags on, "
    "or they are not sleeping or eating, a GP appointment is the usual next step.",
    "That one is theirs to say, not mine. What helps most is asking how they are and then "
    "listening rather than fixing it. If it runs for weeks, or they stop sleeping or eating "
    "properly, that is a GP question rather than a search one.",
)


# A dog has a vet rather than a ward, so the same ask in a thread about an animal goes there.
UNKNOWN_HOW_IT_GOES_FOR_A_PET = (
    "Only the vet can say, and that is why the call is the answer - they would much rather hear "
    "it now than later. If they go wobbly, sick or sleepy, that is an evening vet, not a morning "
    "one.",
    "I cannot tell you that, and I would not guess about an animal. Ring the vet and say what "
    "happened; how are they in themselves right now?",
    "That one belongs to the vet rather than to me. While you ring, watch them: eating, moving "
    "about, themselves - that is what the vet will ask you.",
)


# "should she still be driving" at eighty-four, living on her own: the same "not mine to say" as
# the pool above, but the person who can say is one who can see her do it, not one treating her.
UNKNOWN_IF_THEY_STILL_CAN = (
    "Nobody here can judge that from a line, and I would not guess at it. Their GP, or whoever "
    "sees them day to day, will tell you straight, and it is easier to raise as a worry than as a "
    "verdict. Has anything already gone wrong?",
    "That is not mine to decide, and it is not a thing to guess at either. Ask their doctor, or "
    "get an eye test done if it is about the driving; that settles it more often than people "
    "expect. What made you wonder?",
    "I cannot say, and I would not want to. The person who can judge it is the one who can see "
    "them do it. Would they take it from you if you raised it?",
)


def _somebody_to_visit(clean, turns, look_back=3):
    """True when the line or the last few turns name a person the visit could be to."""
    people = THE_PEOPLE | VISIT_PRONOUNS
    if set(re.findall(r"[a-z']+", clean)) & people:
        return True
    for turn in turns[-look_back:]:
        said = str(turn.get("user") or "").lower()
        if set(re.findall(r"[a-z']+", said)) & people:
            return True
    return False


# Whose trouble it is. A line with an animal in it is not always about the animal: "my dog bit me
# and it is bleeding" is a person with a bite on their hand, and the vet is the wrong building for
# them. So the animal has to be the one that was hurt, and each of these readings says the person
# is: the animal did it to them, somebody did it to them, they are one of the people, or what is
# bleeding belongs to them.
#
# The old second arm was a bare `my ... bleeding`, and it could not tell whose blood it was: "my
# dog is bleeding" and "my dogs paw is bleeding" were read as a person hurt, so the walk-in pool
# answered an animal. Whose it is comes from the noun, not from the possessive: a body part after
# "my" is a person, an animal after "my" is not.
AN_ANIMAL_DID_IT = re.compile(
    r"\b(?:bit|bitten|bites|scratch(?:ed|es)?|kicked|trampled|stung|attacked|mauled|nipped|"
    r"gouged|pinned|knocked|went for|lashed out at)\s+(?:me|us|my|our)\b",
    re.I)


# The same injury with the animal as the agent: "bitten by a dog", "scratched by the cat". This is
# the passive form and the active one does not cover it, which is how a child with a dog bite was
# told to ring the vet "and say what she ate and when".
AN_ANIMAL_DID_IT_TO_ANYONE = re.compile(
    r"\b(?:bit|bitten|bites|scratch(?:ed|es)?|nipped|attacked|mauled|stung|kicked)\s+by\s+"
    r"(?:a|an|the|my|our|their|his|her|some)\s+(?:dog|dogs|cat|cats|puppy|pup|kitten|rabbit|"
    r"hamster|budgie|parrot|horse|pony|fox|rat|mouse|snake|spider|wasp|bee|animal|pet)\b",
    re.I)


# Somebody else is the patient: "my daughter got bitten by a dog", "the child was scratched". The
# child or the partner is read only beside a bite, a scratch or a sting, so "my son is vomiting"
# stays where it was.
A_PERSON_ELSE_IS_HURT = re.compile(
    r"\b(?:my|our|the|his|her|their)\s+(?:daughter|son|child|children|kid|kids|baby|wife|"
    r"husband|partner|boyfriend|girlfriend|mum|mother|dad|father|sister|brother|friend|"
    r"neighbour|neighbor|grandson|granddaughter|grandchild|niece|nephew)\b[^.]{0,60}\b"
    r"(?:bit|bitten|bites|scratch(?:ed|es)?|nipped|attacked|mauled|stung|kicked|swollen|"
    r"bleeding|bled)\b",
    re.I)


A_CHILD = re.compile(
    r"\b(?:my|our)\s+(?:son|daughter|boy|girl|kid|kids|children|child|eldest|youngest|"
    r"stepson|stepdaughter)\b|\bthe\s+(?:kids|children|eldest|youngest)\b", re.IGNORECASE)


def _plain(text):
    """The line in one case, with the dashes people type made the same.

    A phone writes an em dash and a keyboard writes a hyphen, so "I'm listening - say more if it
    helps" has to read as the pool's own "I'm listening — say more if it helps."
    """
    lowered = str(text or "").lower().replace("\u2014", "-").replace("\u2013", "-")
    return " ".join(lowered.split())
