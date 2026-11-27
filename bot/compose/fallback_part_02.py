"""Part 2 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import re

from ..memory import last_user
from ..understanding.topics import IDIOM_PHRASES, THE_PEOPLE
from . import (badnews, loss,
               trouble)
from .badnews import (reads_as_bad_news)

from .fallback_data import (
    ANIMALS,
    APOLOGY_ANSWER,
    ASK_OUT_ANSWER,
    BODY_PARTS,
    BODY_SUBJECT,
    CALL_ANSWER,
    CONTACT_ANSWER,
    GO_ANSWER,
    GO_TO_BE_SEEN,
    HEALTH_WORDS,
    MESS_PLACES,
    MONEY_WORDS,
    NOT_PEOPLE_WORDS,
    RING_FOR_HELP,
    RING_THE_POLICE,
    SORE_AMBIGUOUS,
    SORE_WORDS,
    SYMPTOM_WORDS,
    THING_STATES,
    THING_SUBJECT,
    UNKNOWN,
    WILD_BIRDS,
    _A_PERSON,
    _A_SOCIAL_THING,
    _COPULA,
    _MONEY_NOUN,
)

from .fallback_part_01 import (
    PLAN_WORDS, TAKING_UP, AN_ANIMAL_DID_IT, AN_ANIMAL_DID_IT_TO_ANYONE, A_PERSON_ELSE_IS_HURT,
    _AGE_DOUBT, SHOULD_WORRY, WORRY_SELF, _a_bare_worry, _worry_is_about_the_body,
    SHOULD_WORRY_FILLER, _CARD_MONEY, _PAY_DEBT, _VALUE_OF_THING, SORE_DOING, SORE_ONLY_A_BODY,
    SORE_PICKING, SORE_PLACE, DANGER_SYMPTOM, EMERGENCY_CALL, MINOR_HARM, POLICE_CALL,
    REACHING_THE_POLICE, SOMETHING_HAPPENING, _ASKING_FOR_THE_POLICE, _ASKS_TO_ACT, _A_CALL_WORD,
    _A_PLACE_TO_BE_SEEN, AN_APOLOGY, ASKED_OUT, _CALLING, _CONTACT, _GOING, _NOT_INVITED,
)


def _a_plan_in_the_thread(clean, memory):
    """True when the plan the doubt is about is in the line or the turn before it."""
    for text in (clean, _the_line_before(memory)):
        said = str(text or "").lower()
        if said and (PLAN_WORDS.search(said) or TAKING_UP.search(said)):
            return True
    return _a_thing_they_started(memory)


# What happens to a person after an animal bite, and never to the animal: the jab, the hospital,
# the stitches. "do i need a tetanus" after "i was bitten by a dog" is the person's question.
A_PERSONS_TREATMENT = re.compile(
    r"\b(?:tetanus|rabies|jab|jabs|shot|shots|stitches|stitched|a&e|a and e|casualty|"
    r"minor injuries|triage|antiseptic|antibiotics?|wound|dressing|bandage)\b",
    re.I)


# The person's own body: "i am bleeding", "im bleeding", "my hand is bleeding", "my arm hurts".
# Only a body part counts after "my", because "my dog" and "my cat" are the animal.
A_BODY_PART = (
    r"(?:hand|hands|arm|arms|finger|fingers|thumb|thumbs|wrist|wrists|leg|legs|foot|feet|toe|toes|"
    r"head|nose|face|mouth|lip|lips|eye|eyes|ear|ears|knee|knees|shoulder|shoulders|back|side|"
    r"chest|stomach|ankle|ankles|heel|heels|shin|thigh|elbow|skin|neck|jaw|tooth|teeth|gum|gums|"
    r"nail|nails|cut|cuts|wound|wounds|bite|scar|knuckle|knuckles|palm|fist|forehead|cheek)")


A_PERSON_IS_BLEEDING = re.compile(
    r"\b(?:i|im|i'm|ive|i've|we|we're|weve|we've)\s+(?:am\s+|was\s+|are\s+|were\s+|"
    r"keep\s+|keeps\s+|still\s+|been\s+)?(?:bleeding|bled)\b|"
    r"\b(?:i|im|i'm|ive|i've|we|we're)\s+(?:still\s+|also\s+)?(?:hurting|in pain|sore)\b|"
    r"\bmy\s+" + A_BODY_PART + r"\b[^.]{0,30}?\b(?:bleeding|bled|hurts?|hurting|sore|"
    r"swollen|limp|infected|throbbing|bruised|broken|stings?|burning)\b",
    re.I)


# Whose body the injury is on when both a person and an animal are named, read from the order of
# the words. The passive form has no subject: "bitten by a snake" is the same words whether the one
# with the bite is the person or the dog, so `AN_ANIMAL_DID_IT_TO_ANYONE` read "my dog was bitten
# by a snake" as somebody's hand and answered "a&e or a walk-in centre can say for certain" about a
# dog. The order tells them apart: in "my dog was bitten by a snake" the animal comes before the
# verb, so the animal is the one who was hurt; in "i was bitten by a dog" it comes after.
AN_A_HARM_VERB = re.compile(
    r"\b(?:bit|bites|bitten|scratch|scratches|scratched|sting|stings|stung|kicked|attacks?|"
    r"attacked|mauled|nipped|gouged|trampled|lashed out at|went for|snapped at)\b",
    re.I)


AN_ANIMAL_WORD = re.compile(r"\b(?:" + "|".join(sorted(ANIMALS)) + r")\b", re.I)


def _the_animal_is_the_patient(said):
    """True when the animal named in this line is the one with the injury.

    Deliberately narrow: an animal before the verb of harm, and nobody's body named after it. "the
    dog bit my son" and "my dog scratched the baby" have the animal before the verb too, and there
    the person is the patient, so the object of the verb is read before the order is.
    """
    text = str(said or "").lower()
    animals = [m.start() for m in AN_ANIMAL_WORD.finditer(text)]
    if not animals:
        return False
    if AN_ANIMAL_DID_IT.search(text):
        return False
    verb = AN_A_HARM_VERB.search(text)
    if verb is None or min(animals) > verb.start():
        return False
    tail = set(re.findall(r"[a-z']+", text[verb.end():]))
    return not (tail & (THE_PEOPLE - ANIMALS))


def _the_person_is_the_patient(said):
    """True when what a line says is about somebody's body other than the animal's.

    One reader for the four ways a person is the patient: the animal did it to them, it did it to
    somebody in their family, they need the treatment an animal bite needs, or a body of theirs is
    the thing bleeding. The bare possessive is deliberately not one of them.
    """
    text = str(said or "")
    if not text or _the_animal_is_the_patient(text):
        return False
    return bool(AN_ANIMAL_DID_IT.search(text)
                or AN_ANIMAL_DID_IT_TO_ANYONE.search(text)
                or A_PERSON_ELSE_IS_HURT.search(text)
                or A_PERSONS_TREATMENT.search(text)
                or A_PERSON_IS_BLEEDING.search(text))


def _the_thread_is_an_animal(clean, turns, look_back=4):
    """True when the line or the last few turns are about an animal rather than a person.

    Read like `_someone_is_a_patient`: the care question ("should i take her tonight") does not
    name the animal again, so the thread has to say it, and a line naming one says it by itself.
    The animal also has to be the one in trouble - `_the_person_is_the_patient` keeps the person
    with the bite on their own hand out of the vet's waiting room, and keeps a dog's bleeding paw
    out of it too by not reading "my dog is bleeding" as somebody's blood.
    """
    said = str(clean or "").lower()
    recent = [str(turn.get("user") or "").lower() for turn in turns[-look_back:]]
    if _the_person_is_the_patient(said) or any(_the_person_is_the_patient(x) for x in recent):
        return False
    if set(re.findall(r"[a-z']+", said)) & NOT_PEOPLE_WORDS:
        return True
    return any(set(re.findall(r"[a-z']+", x)) & NOT_PEOPLE_WORDS for x in recent)


def _thread_is_about_someone_else(memory, look_back=3):
    """True when the last few things the person said were about somebody other than them.

    Read from the thread, not the line: "he cant do up his buttons yet" names the child only as
    "he", and the line after it is the bare ask.
    """
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    for turn in turns[-look_back:]:
        said = str(turn.get("user") or "").lower()
        words = {w[:-2] if w.endswith("'s") else w for w in re.findall(r"[a-z']+", said)}
        if (words & trouble.OTHERS) - NOT_PEOPLE_WORDS:
            return True
    return False


def _thread_is_about_a_pet(memory, look_back=3):
    """True when the last few things the person said named an animal.

    Read from the thread, not the line, because the line is the bare ask: "my dog keeps
    scratching" then "should i be worried". A wild bird that made a mess is not somebody with a
    doctor ("how do i clean bird poo off my patio"), so the mess shapes are left out.
    """
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    for turn in reversed(turns[-look_back:]):
        said = str(turn.get("user") or "").lower()
        words = {w[:-2] if w.endswith("'s") else w for w in re.findall(r"[a-z']+", said)}
        animals = words & ANIMALS
        if not animals:
            # The nearest line that names a subject is what the bare worry is about. A line about
            # the person's own state ("my dog died last year" / "i keep feeling odd" / "should i be
            # worried") is about them, however much of the week was spent at the vet: the vet line
            # answered that with "one visit settles it" about a dog that is already gone.
            if _the_speaker_is_the_subject(said):
                return False
            continue
        if animals <= WILD_BIRDS and words & MESS_PLACES:
            continue
        if loss.reads_as_loss(said) or badnews.reads_as_sudden_loss(said):
            return False
        return True
    return False


# Who the line is asking about: "he" and "she" point back at the thread, and a named relation
# says it in the line. The animals are here so that "is he going to be ok" after "my dog drank
# sea water" is read as a question for a vet rather than for a ward.
ASKED_ABOUT = re.compile(
    r"(?:he|she|they|(?:my|our|his|her|their)\s+(?:poor\s+|old\s+|little\s+|eldest\s+)?"
    r"(?:mum|mom|mother|dad|father|son|daughter|husband|wife|partner|boyfriend|girlfriend|"
    r"sister|brother|nan|nana|gran|granny|grandma|grandad|grandpa|baby|kid|kids|child|children|"
    r"friend|mate|neighbour|neighbor|aunt|uncle|cousin|little one|lad|lass|boy|girl|"
    r"dog|cat|puppy|kitten|pup|rabbit|hamster|horse|budgie|parrot|fish|pet))")


# "is he going to be ok", "will my mum be alright", "is she ok", "are they fine".
WHETHER_IT_GOES_WELL = re.compile(
    r"\b(?:is|are|was|were|will|would)\s+" + ASKED_ABOUT.pattern
    + r"\b\s+(?:going\s+to|gonna)\s+be\b"
    r"|\b(?:is|are|was|were)\s+" + ASKED_ABOUT.pattern
    + r"\b\s+(?:ok|okay|alright|all\s+right|fine|safe)\b"
    r"|\b(?:will|would)\s+" + ASKED_ABOUT.pattern
    + r"\b\s+be\s+(?:ok|okay|alright|all\s+right|fine|safe)\b"
    r"|\b(?:will|would)\s+" + ASKED_ABOUT.pattern
    + r"\b\s+(?:ever\s+)?(?:pull\s+through|make\s+it|get\s+better|get\s+worse|recover|"
    r"walk\s+again|come\s+round|beat\s+it|"
    r"be\s+(?:himself|herself|themselves|back\s+to\s+(?:normal|herself|himself|themselves)))\b"
    r"|\b(?:is|are|was)\s+" + ASKED_ABOUT.pattern
    + r"\b[^.?!]{0,25}\b(?:at\s+risk|in\s+danger)\b"
    r"|\bhow\s+long\s+(?:is|are|will|does|do|has|have)\s+" + ASKED_ABOUT.pattern + r"\b")


# "should she still be driving" is the same ask with a different answer: not how it will go, but
# whether an eighty-four-year-old who lives alone should be at the wheel. It is not the bot's to
# judge either, and the person who can is one who can see her do it.
WHETHER_THEY_CAN_STILL = re.compile(
    r"\bshould\s+" + ASKED_ABOUT.pattern + r"\b\s+still\b"
    r"|\bshould\s+" + ASKED_ABOUT.pattern
    + r"\b\s+be\s+(?:driving|working|living\s+alone|left\s+alone|on\s+(?:his|her|their)\s+own)"
    r"|\bis\s+" + ASKED_ABOUT.pattern
    + r"\b\s+(?:still\s+)?(?:ok|safe|alright)\s+to\s+(?:drive|live|work)\b")


# The same worry said with "it" instead of a person ("my dad has prostate cancer" / "is it going
# to be alright") or as a length ("how bad will it get", "how much longer has she got"). "It" is
# only a person's illness when the thread has an illness in it: "my dad's car is making a noise" /
# "is it going to be ok" is a garage question and keeps its own answer.
WHETHER_IT_GOES_WELL_ITSELF = re.compile(
    r"\b(?:is|was|will)\s+(?:it|this|that)\s+(?:going\s+to\s+be\s+|be\s+)?"
    r"(?:ok|okay|alright|all\s+right|fine|serious|bad|treatable|curable|terminal)\b"
    r"|\bhow\s+(?:bad|serious)\s+(?:will\s+(?:it|this|that)\s+get|is\s+(?:it|this|that))\b"
    r"|\bhow\s+long\s+(?:is|will)\s+the\s+recovery\b")


# "how much longer has she got", said about a ninety-two-year-old: a length of life, not an
# illness in the thread, so this one needs only the person the thread is about.
WHETHER_IT_LONGER_HAS_GOT = re.compile(
    r"\bhow\s+much\s+longer\s+(?:has|have|does|do)\s+" + ASKED_ABOUT.pattern + r"\b"
    r"|\bhow\s+long\s+(?:has|have)\s+" + ASKED_ABOUT.pattern + r"\b\s+(?:got|left)\b")


AN_ILLNESS = re.compile(
    r"\b(?:cancer|tumou?r|disease|illness|condition|infection|dementia|alzheimers?|"
    r"leuk[ae]mia|leuka?emia|arthritis|diabetes|epilepsy|lupus|ms|covid|long\s+covid|flu|"
    r"pneumonia|chemo|dialysis|transplant|bypass|operation|surgery|procedure|stroke|aneurysm|sepsis|"
    r"heart\s+failure|kidney\s+failure|liver\s+failure|ulcer|colitis|crohns?|asthma|"
    r"depression|anorexia|bulimia|eating\s+disorder|addiction|withdrawal)\b")


# A pet's worry is the vet's only when the thread says something is actually wrong with the
# animal: "my dog drank sea water" and "the vet saw my cat this morning" are, and "we are getting
# a puppy" / "will he be alright in a flat" is a question about space, not about a body.
A_PET_IN_TROUBLE = re.compile(
    r"\b(?:vet|vets|sick|ill|illness|disease|diagnosed|condition|hurt|hurts|injured|injury|"
    r"poison|poisoned|ate|eaten|drank|drunk|swallowed|choking|choked|limp|limping|bleeding|"
    r"bled|cut|wound|wobbly|unsteady|seizure|fit|fits|surgery|operation|collapsed|"
    r"not\s+eating|stopped\s+eating|off\s+(?:his|her|its|their)\s+food|worse)\b")


# "is that just age", said about the parent who keeps forgetting words the line before.
WHETHER_IT_IS_THEIR_AGE = re.compile(
    r"\b(?:is|was)\s+(?:that|this|it)\s+(?:just|normal|normal\s+for|ordinary)\b[^.?!]{0,30}"
    r"\b(?:age|her\s+age|his\s+age|them|him|her)\b")


# The people a thread can be about, as stems: "my mums in hospital" has to read as a person, and
# it spells its own relation with an s on the end.
_MY_PEOPLE = frozenset(w.rstrip("s") for w in """
    mum mom mother dad father son daughter husband wife partner boyfriend girlfriend sister
    brother nan nana gran granny grandma grandad grandpa baby kid child children friend mate
    neighbour neighbor aunt uncle cousin lad lass boy girl parent ex family stepson stepdaughter
    nephew niece grandson granddaughter sibling twin stepmum stepdad stepmother stepfather
    mother-in-law father-in-law son-in-law daughter-in-law sister-in-law brother-in-law
    godson goddaughter grandparent in-laws
""".split())


# A bed in a hospital says whose body the thread is about even when the word is not a relation.
A_PATIENT_STATE = re.compile(r"\b(?:hospital|pregnant|operation|surgery|diagnosed|chemo|"
                             r"ward|intensive\s+care|in\s+a\s+coma|on\s+a\s+drip)\b")


# A thread about somebody's body says whose it is, but a thread about a hard patch says nothing
# about one: "my mum is having a hard time" then "is she going to be ok" is a rough spell, not an
# illness, and a pool that answers "ask whoever is treating them, or ring 111" has invented a
# patient. The words here are the ordinary ones for trouble that is not a body's.
A_HARD_TIME = re.compile(
    r"\b(?:(?:hard|rough|bad|tough|difficult|dreadful|awful)\s+(?:time|times|week|weeks|month|"
    r"months|year|years|patch|spell|stretch|ride|few(?:\s+\w+)?|long(?:\s+\w+)?)\b|"
    r"struggling|struggles|struggled|having\s+a\s+go\s+of\s+it|feeling\s+low|feels\s+low|"
    r"down\s+in\s+the\s+dumps|grieving|grief|bereavement|lonely|loneliness|stressed|stress|"
    r"overwhelmed|burnout|burnt\s+out|burned\s+out|worried\s+sick|money\s+trouble|"
    r"out\s+of\s+work|lost\s+(?:his|her|their)\s+job|divorce|divorcing|split\s+up|"
    r"separation|argument|arguing|falling\s+out|fell\s+out|lonely)\b")


# What a thread needs for the pools that talk about treatment to be right: a body, a bed, or a
# thing that happened to one.
A_MEDICAL_THREAD = re.compile(
    r"\b(?:hospital|hospice|pregnant|operation|operations|op|ops|surgery|surgeon|surgeons|"
    r"diagnosed|diagnosis|chemo|chemotherapy|radiotherapy|treatment|treating|being\s+treated|"
    r"ward|intensive\s+care|high\s+dependency|in\s+a\s+coma|on\s+a\s+drip|anaesthetic|"
    r"anaesthetist|theatre|consultant|specialist|biopsy|transplant|dialys\w+|"
    # "results day" is a school day and "exam results" are not a body's: only a result of a test
    # on a person is, and that is said with a word that is already here.
    r"results?(?!\s+day)\b|"
    r"accident|accidents|crash|crashed|ambulance|casualty|a\s+and\s+e|ae|"
    r"broke|broken|fractur\w+|scald\w*|stitches|collapsed|fainted|"
    r"seizure|seizures|convulsion\w*|concussion|injured|injury|injuries|whiplash)\b"
    # A fall and a burn are a body's, but "fell out with her sister" is a quarrel and "burnt out"
    # is a state of mind: both are `A_HARD_TIME` shapes, so without this they read as an injury
    # and send a person who is struggling to a ward.
    r"|\b(?:fell|fallen|burn|burns|burned|burnt)(?!\s+out)\b")


def _the_thread_said(memory, look_back=3):
    """The last few things the person said, as one lowercase string."""
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    return " ".join(str(turn.get("user") or "").lower() for turn in turns[-look_back:])


def _a_person_in_the_thread(memory, look_back=3):
    """True when one of the last few lines is about a person, named as a relation or as a patient.

    `_thread_is_about_a_person` reads the same turns, but only from the words it was written for:
    "my mums in hospital" carries its own relation with an s on the end and a bed that says
    somebody is in it, and both mean the next line's "she" is a person rather than a machine.
    """
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    for turn in turns[-look_back:]:
        said = str(turn.get("user") or "").lower()
        words = {w[:-2] if w.endswith("'s") else w for w in re.findall(r"[a-z']+", said)}
        if {w.rstrip("s") for w in words} & _MY_PEOPLE or A_PATIENT_STATE.search(said):
            return True
    return False


def _a_pet_in_trouble(line, memory):
    """Whether the worry is about an animal that has something wrong with it.

    The animal has to be the thread's, in an animal thread and with no person named in the last
    two lines ("my dog drank sea water", but not "my dad's dog died"), and something in the line
    or the thread has to say the animal is hurt or ill.
    """
    if not _thread_is_about_a_pet(memory) or _a_person_in_the_thread(memory, look_back=2):
        return False
    said = _the_thread_said(memory)
    # "my cat had a rough few days" is the vet's too: for an animal a rough patch is being off
    # colour, and there is no such thing as a bad week at work for a cat.
    return bool(A_PET_IN_TROUBLE.search(line) or A_PET_IN_TROUBLE.search(said)
                or A_HARD_TIME.search(said))


SELF_WORDS = frozenset("i me my myself im ive id i'm i've".split())


# The words that make a first-person line about the person's own state rather than about the animal
# in it: "i keep feeling odd", "i feel anxious", "i cant stop thinking about it".
THEIR_OWN_STATE = re.compile(
    r"\bi\s+(?:keep|still|just)\s+(?:feeling|feel|thinking|worrying|crying)\b"
    r"|\bi\s*'?m\s+(?:feeling|worried|scared|anxious|sad|low|exhausted|knackered)\b"
    r"|\bi\s+feel\s+(?:odd|weird|strange|awful|terrible|anxious|worried|sad|low|numb|empty)\b"
    r"|\bi\s+cant\s+(?:stop|sleep|eat|shake|cope)\b"
    r"|\bi\s+havent\s+(?:slept|eaten|coped)\b")


def _the_speaker_is_the_subject(said):
    """True when a line is about the person and not about the animal it may also name.

    "i keep feeling odd" names nobody but the speaker, and the bare worry after it is theirs. The
    loss shapes are read in `_thread_is_about_a_pet` itself, because a line can name both.
    """
    return bool(THEIR_OWN_STATE.search(str(said or "")))


def _a_thing_they_started(memory, look_back=3):
    """True when the last few lines are the person taking something up themselves.

    "is that too late" is a doubt about their own starting, so the turn behind it has to be that
    start: "im learning to swim at 40", "i started piano last year" / "im 52". A train, a
    deadline or a booking leaves it False, and then the question is somebody else's to answer.
    """
    turns = [t for t in ((memory or {}).get("turns") or []) if isinstance(t, dict)]
    for turn in turns[-look_back:]:
        if TAKING_UP.search(str(turn.get("user") or "").lower()):
            return True
    return False


def _names_their_age(clean):
    """True when the doubt about starting is their age rather than their fitness."""
    return bool(re.search(r"\b\d{1,2}\b", clean)
                or _AGE_DOUBT.search(clean))


def _reads_as_worry(clean, words=()):
    """True when the line asks to be reassured rather than asking a question of fact."""
    words = words or clean.split()
    if _worry_is_about_the_body(clean, words):
        return False
    if WORRY_SELF.search(clean):
        return True
    return bool(SHOULD_WORRY.search(clean)) and _a_bare_worry(clean)


def _nothing_but_the_ask(clean, found):
    """True when the line is the doubt itself, with no subject named around it."""
    rest = clean[:found.start()] + " " + clean[found.end():]
    return not re.sub(r"[^a-z0-9]", "", SHOULD_WORRY_FILLER.sub(" ", rest))


def _without_the_idioms(said):
    """The words of a line with the phrases in `IDIOM_PHRASES` taken out.

    The tree already decides which body words are not bodies, in one list, for the topic of a
    line ("a pain in the neck", "run off my feet", "last legs"). The thread reader here had its
    own read of the raw words, so a thread that said "its on its last legs" about a washing
    machine was a thread about a body, and "is it worth fixing" rang 111 for a machine. One list,
    read by both, so a phrase about a thing cannot be a symptom in one place and not the other.
    """
    words = re.findall(r"[a-z']+", said)
    if not words:
        return set()
    taken = set()
    for phrase in IDIOM_PHRASES:
        size = len(phrase)
        for at in range(len(words) - size + 1):
            if tuple(words[at:at + size]) == phrase:
                taken.update(range(at, at + size))
    return {word for at, word in enumerate(words) if at not in taken}


# A question that points at a thing instead of naming it: "will that get better if i keep at
# it", "and will it stop", "is that normal". The pronoun is the whole subject, so the thread is
# what the answer has to fit.
_LEANS_ON_THE_THREAD = re.compile(r"\b(?:it|its|that|thats|this|they|them|those|these)\b")


# The topics a thread can be about and a question about "it" still be the thread's own: a line
# read as cooking ("will that cake keep overnight") names its subject even when a pronoun is in
# it, so only a line with no topic of its own, or a body's, counts as pointing at the thread.
_BODY_TOPICS = (None, "", "health", "fitness", "sleep")


# A machine in the thread is a thing, not a body. "the chain skips on the back gears" then "is
# it worth getting it serviced" is a bike - the body reading was taken from the word "back" in
# "back gears", and the cost rule (new in this cut) turned it into "a GP, a pharmacist or 111 will
# tell you", which is the wrong half of the world entirely. A thread that names one of these is a
# thread about a thing whatever body word is hiding in it.
_THREAD_MACHINES = frozenset("""
bike bicycle cycle chain chains gears gear derailleur boiler car van motorbike scooter washer
machine dryer dryers dishwasher fridge freezer oven cooker hob kettle toaster microwave hoover vacuum
mower lawnmower laptop phone tablet computer pc printer tv television stereo speaker speakers
headphones watch clock camera drill saw gate door window shed roof gutter tap shower radiator
pump fan fridge washing
""".split())


def _thread_names_a_machine(memory, look_back=4):
    """True when the last few things the person said named a thing that gets serviced or replaced.

    A body word in the same line outranks the machine word: "my knee keeps giving way and i watch
    it swell" and "my shoulder hurts when i lift the door at work" name a watch and a door, and
    both lines are about a body, so the thread is not the machine's and the cost rule stays out of
    it. The machine has to be what its own line is about.

    The nearest turn decides, because a thread moves on (good-shelf on #7382). "the window in my
    bedroom leaks" and then "my back keeps going" is a body thread that happens to have named a
    window first, and "is it worth fixing" after it is the GP line, not a part and a quote. A
    later line with a body word and no machine word ends the machine thread; a later line that
    says nothing of either ("i dread the phone call") leaves it standing, so "my back keeps
    going" / "the boiler is on its way out" / "is it worth fixing" still gets the cost rule.
    """
    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)]
    for turn in reversed(turns[-look_back:]):
        tokens = re.findall(r"[a-z']+", (turn.get("user") or "").lower())
        machine_at = [i for i, word in enumerate(tokens) if word in _THREAD_MACHINES]
        if not machine_at:
            if set(tokens) & (BODY_PARTS | SYMPTOM_WORDS | HEALTH_WORDS):
                return False
            continue
        body_at = [i for i, word in enumerate(tokens)
                   if word in BODY_PARTS or word in SYMPTOM_WORDS or word in HEALTH_WORDS]
        # A body word written beside the machine word is part of the machine's name ("the back
        # gears", "the back door", "the back wheel"), so it does not make the line a body line;
        # a body word anywhere else does.
        if all(any(abs(i - j) == 1 for j in machine_at) for i in body_at):
            return True
    return False


# The line's own candidate: "is it my shoes", "could it be my trainers", "maybe it's my age". The
# pronoun is in the line, but the line is not only pointing at the thread - it puts something of
# its own up as the cause, which is a question about that thing and not about the thread.
_A_CANDIDATE_OF_ITS_OWN = re.compile(
    r"\b(?:it|its|it['\u2019]s|this|that|these|those|they)\b[^.?!,;]{0,24}?"
    r"\b(?:my|our|his|her|their)\s+[a-z]")


def _a_thing_was_named(memory, look_back=4):
    """True when a line before the decision named a thing as well as a person.

    "my son rides his bike to school" / "should i bother fixing it or replace it" is a cost
    question about the bike: the person is only in the earlier line, not the thing being
    weighed, so the cost rule is the answer. "my marriage is on the rocks" / "is it worth fixing
    or shall i leave" names no thing at all, and a marriage is not a broken appliance. The
    reading of each earlier line is the understanding engine's own: it already says what a line
    names and what kind of thing that is, so nothing here keeps a second list of objects.
    """
    from ..understanding import understand  # noqa: PLC0415 - the reading of an earlier line

    turns = [t for t in (memory.get("turns") or []) if isinstance(t, dict)][-look_back:]
    for turn in turns:
        said = str(turn.get("user") or "")
        if not said.strip():
            continue
        for entity in understand(said).get("entities") or []:
            if str(entity.get("type")) == "thing":
                return True
    return False


def _money_decision(clean):
    """Whether the line decides something about money rather than about what a thing is worth."""
    said = set(re.findall(r"[a-z']+", clean))
    if not said & MONEY_WORDS and not _PAY_DEBT.search(clean) and not _CARD_MONEY.search(clean):
        return False
    if _VALUE_OF_THING.search(clean) and not said & _MONEY_NOUN:
        return False
    return True


def _about_a_sore(clean, words):
    """True when the line is about a thing on the body that can be squeezed, picked or covered.

    The doing verb is the question, but it needs a sore, and a sore needs to be the body's: a spot
    and a lump are places and things as well, so one of those words only counts when the line says
    where on the person it is ("my spot", "the lump on my back", "a spot on my chin").
    """
    if not SORE_DOING.search(clean):
        return False
    named = set(words) & SORE_WORDS
    if not named:
        return False
    if named - SORE_AMBIGUOUS:
        return True                     # a scab, a boil, a blister: no other reading
    if not SORE_PICKING.search(clean) or SORE_ONLY_A_BODY.search(clean):
        return True                     # "should i pop a spot" is a chin, not a campsite
    return bool(SORE_PLACE.search(clean))


def _a_call_for_help(clean):
    """The pool for a line asking whether to ring for help, or None when it is another question."""
    if not _ASKS_TO_ACT.search(clean):
        return None
    if _A_PLACE_TO_BE_SEEN.search(clean) and not _A_CALL_WORD.search(clean):
        if DANGER_SYMPTOM.search(clean):
            # "should i go to a&e, i can't stop bleeding" is not a drive, it is a call.
            return RING_FOR_HELP
        if MINOR_HARM.search(clean):
            # A stubbed toe does not need a department: the same stand-down the phone words get.
            return None
        return GO_TO_BE_SEEN
    if EMERGENCY_CALL.search(clean):
        if MINOR_HARM.search(clean) and not DANGER_SYMPTOM.search(clean):
            # The ordinary line for a minor thing, not the emergency one: a friend says no.
            return None
        return RING_FOR_HELP
    if POLICE_CALL.search(clean) and (REACHING_THE_POLICE.search(clean)
                                     or _ASKING_FOR_THE_POLICE.search(clean)
                                     or SOMETHING_HAPPENING.search(clean)):
        return RING_THE_POLICE
    return None


# A repair asked for as a method ("how do i make it right with her", "how do i make it up to my
# mum"), not as a yes or no. APOLOGY_ANSWER answers "should i apologise" and agrees first; the
# person here has already decided, so what they need is the shape of the thing. The person has to
# be named: "my hoover wont pick up" and "how do i fix it" is a machine, and the same words with
# nobody in them are somebody else's question.
REPAIR_HOW = re.compile(
    r"\bhow (?:do|can|could|should|would) (?:i|we)\b[^.?!]{0,40}?"
    r"(?:\bmake (?:it|things|this) (?:right|up)\b|\bmake up for\b|"
    r"\bput (?:it|things|this) right\b|\bsay sorry\b|\bapolog\w*|\bforgive me\b|"
    r"\bclear the air\b)")


REPAIR_ANSWER = (
    "Name the one thing you did, say sorry for it in a sentence, then ask what would help. Short "
    "and about them is what makes it land, and the explaining can come later if they want it.",
    "Do it soon, in person if you can. Say what you did rather than why you did it, and leave "
    "what they did out of it - that is the part that turns an apology into an argument.",
    "One sentence of sorry, then a question: what would make it easier? Most people would rather "
    "be asked than be given a longer apology.",
)


def _a_small_social_decide(clean, words):
    """The pool for an everyday social decision, or None when the line is a different question."""
    if ASKED_OUT.search(clean):
        return ASK_OUT_ANSWER
    if AN_APOLOGY.search(clean):
        return APOLOGY_ANSWER
    said = set(words)
    if _CONTACT.search(clean) and said & _A_PERSON:
        if _CALLING.search(clean):
            return CALL_ANSWER
        return CONTACT_ANSWER
    if said & _A_SOCIAL_THING and _GOING.search(clean) and not _NOT_INVITED.search(clean):
        return GO_ANSWER
    return None


# A method asked for in the person's own voice: "how do i practise", "where should i hang my
# washing", "when do i start". Read on the opening only. Everything with an entry has already had
# its turn before this is read (it stands in for the search hedge at the bottom of the fallback),
# so a line naming a thing the bot has a card for never reaches it.
# "how" and "where" only: a "when should i ..." ask is about timing, and the answer to it is a date
# or a season ("when should i plant tulips" is a calendar question with sources), not a method.
METHOD_OPENING = re.compile(r"^(?:so |ok |okay |and |but )?"
                            r"(?:how|where) (?:do|does|should|shall|can|could|would|might) i\b")


# Two shapes that look like a method ask and are not one, so they keep the answer they had.
#
# "how do i know if im ovulating" asks how to tell something about their body, which is a symptom
# card or a doctor's question, not a method with steps they have tried.
#
# "where can i get my brakes fixed round here" asks for a place: the bot cannot see who is near
# them, and the line it had ("I can't recommend anyone - I've no way to see who's near you...")
# says so and hands them the one thing that works. What have you tried so far is no help at all
# for a car with no brakes, so an ask that names something to obtain or a place to find it keeps
# its own pool.
HOW_TO_TELL = re.compile(r"\b(?:know|tell|check|find\s+out) "
                         r"(?:if|whether|the|a|an|my|your|his|her|its|it's|that|this|which|"
                         r"apart|the\s+difference)\b")


# A method asked about a product - a thing with a manual or a settings menu - is a lookup: "how do i
# take a screenshot on a windows laptop" has guides, and "what have you tried so far" is no way into
# it. The machine words are the ones the rest of the file already reads as things to be serviced;
# the software words are their company. "washing" alone is the laundry in the basket and not the
# machine, so "where should i hang my washing" stays the person's own evening.
_A_PRODUCT = _THREAD_MACHINES | frozenset(
    "router wifi broadband windows android iphone ipad ios mac app apps settings browser email "
    "excel word powerpoint gmail outlook instagram facebook whatsapp tiktok password account".split())


_A_PRODUCT = _A_PRODUCT - frozenset(("washing",))


NOT_A_METHOD = re.compile(
    r"^(?:so |ok |okay |and |but )?(?:how|where) (?:do|does|should|shall|can|could|would|might) "
    r"i (?:get|find|buy|hire|rent|book|order|locate|pick\s+up|put|keep|store)\b"
    # "how should i get ready", "how do i get up earlier", "how do i get better at drawing" are
    # methods; only a thing obtained is left out, so the phrasal and the comparative stay in.
    # "put", "keep" and "store" are the same shape as a thing obtained: "where do i put the bin
    # bags" wants a place somebody decides for you, and the bins and permits card has it, so the
    # placement ask keeps its own answer. Hanging washing is not that - nobody decides where it
    # goes but the person - and it stays a method.
    r"(?!\s+(?:up|better|going|started|through|on|out|round|back|dressed|ready|organised|there|"
    r"in|to)\b)"
    r"|\b(?:round here|near me|nearby|in my area|locally)\b"
    # A question about the bot itself ("how do i know you are telling the truth") is the bot's own
    # to answer, and "what have you got so far" is as much of a non sequitur as the search hedge:
    # it is left to the readings that answer questions about the bot.
    r"|\b(?:you|your|yourself)\b")


# "i overdosed on cake" is a joke about eating too much, and the 999 card belongs to a drug: a food
# word with no drug word on the line is the joke, so the emergency words pass it and the food lane
# answers it. "i overdosed on painkillers" keeps the call, and a drug word anywhere does.
OVERDOSE_FOOD = re.compile(
    r"\boverdos(?:e|ed|ing)\b[^.!?]{0,12}\b(?:on|of|with)\s+(?:the\s+|a\s+|some\s+)?"
    r"(?:cake|cakes|chocolate|sweets|candy|biscuits?|cookies|crisps|chips|chinese|curry|pizza|"
    r"ice\s*cream|cheese|coffee|tea|netflix|tv|telly|sugar|bread|"
    r"pastr(?:y|ies)|do(?:ugh)?nuts|burgers?|takeaways?|naps|love|pies?|pudding|trifle|"
    r"turkey|roast|stuffing|mince|gravy|easter\s+eggs?)\b")


OVERDOSE_DRUG = re.compile(
    r"\b(?:pills?|tablets?|paracetamol|ibuprofen|painkillers?|meds|medicines?|"
    r"sleeping\s+pills?|antidepressants?|insulin|heroin|heroine|cocaine|methadone|tramadol|"
    r"codeine|morphine|opioid|opiates?|drugs?|liquid|bottle|packet|pack|box|strip|blister|"
    # A drink is the drug, not the joke: "i overdosed on vodka" is the ambulance.
    r"alcohol|vodka|whisky|whiskey|wine|beer|gin|rum|brandy|tequila|lager|cider|champagne|"
    r"prosecco|ros\u00e9|spirits?|drink|drinking|booze)\b")


# Unresponsive *to* something is not unresponsive: "my baby is unresponsive to her new milk" is a
# feeding problem, "my boss was unresponsive to my emails" is a work one. safety.py carries the
# same tail guard for its own lines; the comma form ("... and unresponsive, call 999") stays an
# emergency because nothing follows the word.
UNRESPONSIVE_TAIL = re.compile(r"\bunresponsive\b\s*(?:to|when|whenever|if|because|as|after|"
                              r"with|about|on)\b")


# Except a feed: "my baby is unresponsive to her milk" is a parent saying the baby will not wake
# after a bottle, so the tail guard must not take the call away from it. The line is the same red
# flag as "my baby is unresponsive" and as "my baby is not responding to her feed".
FEED_TAIL = re.compile(
    r"\bunresponsive\b\s*(?:to|after|during|at|following)\s+(?:the|a|an|her|his|my|their|this|"
    r"that|some)?\s*(?:(?:new|old)\s+)?(?:milk|formula|feeds?|feeding|bottle|breast|solids|"
    r"weaning)\b")


def _the_thing_is_choking(clean, words):
    """True when a choking state belongs to a thing: the engine, the drain, the bike chain.

    Only the choking phrases are read this way: an engine chokes and so can a drain, but a thing
    does not stop breathing or go unconscious. Two halves make the test, and both are needed:
    a thing named right beside the state word, and no person anywhere in the line. A real
    choking emergency names a person ("my son", "she") or names nobody at all ("choking"),
    and both of those keep the ambulance.

    The thing has to be the **subject** of the state, the word just before "is choking" or
    "choking on", not merely a word in the window. gray-palm on #2088: `hes choking on a car key`
    has no token from `BODY_SUBJECT` (it has `hes`) and the window picks up `car`, so a window
    rule loses a child choking to the thing in his mouth. Reading the subject makes an unknown
    word - a name, a contraction, "the drain in the kitchen" - keep the ambulance, which is the
    right cost: a missed ambulance is the one thing this guard must not do.
    """
    if not any(phrase in clean for phrase in THING_STATES):
        return False
    if set(words) & BODY_SUBJECT:
        return False
    tokens = clean.replace("'", "").split()
    for i, word in enumerate(tokens):
        if word != "choking":
            continue
        before = tokens[max(0, i - 4):i]
        # "my car engine is choking": skip the copula so the subject is the word before it.
        while before and before[-1] in _COPULA:
            before.pop()
        if before and before[-1] in THING_SUBJECT:
            return True
    return False


# "i cant wake my baby up" is the same emergency as "wont wake", but only when there is a person
# to wake: "i cant wake up in the mornings" is a sleep habit.
CANT_WAKE = re.compile(r"\b(?:can ?t|cannot|could ?nt)\s+(?:wake|rouse)\s+(?:him|her|them|my|"
                       r"the (?:baby|child|kid|boy|girl|man|woman|old man|old woman))\b")


# "my husband wont wake up for work" is a habit, not an emergency: a wake-up line with a routine
# reason in it is about mornings, not about breathing.
ROUTINE_WAKE = re.compile(
    # The reason can be a place, a vehicle, an appointment or a start time: "wake up for the
    # school bus", "wake up before his exam", "wake up in time for her shift". safety.py carries
    # the same shapes; without them here the composer read the line as a collapse and rang 999
    # for a family trying to catch a train.
    r"\b(?:for|to|before|in time for|on time for) (?:work|school|college|uni|university|nursery|"
    r"childminder|the gym|his work|her work|their work|the (?:school )?(?:bus|train)|"
    r"(?:his|her|their|my|an|a) (?:exam|exams|test|appointment|meeting|interview|flight|"
    r"lesson|lecture|class|early start)|"
    # A shift is the same morning as work, and people name which one: "his early shift",
    # "her night shift", "the late shift at the hospital".
    r"(?:his|her|their|my|the|an|a) (?:early|late|night|day|double|morning|afternoon|evening)?\s*"
    r"shift(?:\s+(?:at|on|tomorrow|today|in)\b[^.]{0,25})?)\b|"
    r"\bto get (?:to|ready for) (?:school|work|college|uni|university|nursery)\b|"
    r"\bin the mornings?\b|"
    r"\bevery (?:morning|monday|tuesday|wednesday|thursday|friday|saturday|sunday|day|week)\b|"
    r"\bon (?:school )?(?:days|weekdays|mondays?|weekday mornings?)\b")


# "im choking on my words" is a stutter: the thing choked on is speech, so the airway word in the
# line is not about an airway. safety.py carries the same shape for its own card.
CHOKE_ON_A_WORD = re.compile(
    r"\bchok(?:e|ed|es|ing)?\s+on\s+(?:(?:my|his|her|their|your|our|the|a|an)\s+)?(?:own\s+)?"
    r"(?:words?|sentences?|speech|lines?|names?|syllables?|pronunciation)\b")


# "i overdosed on coffee", "an overdose of meetings": too much of a good thing, so the word is not
# an ambulance. A pill or a poison named in the line beats the treat words, and safety.py carries
# the same shape for its own card.
OVERDOSE_OF_A_TREAT = re.compile(
    r"\boverdos(?:e|ed|ing)\s+(?:on\s+)?(?:(?:the|a|an|my|his|her|their)\s+)?"
    r"(?:coffee|caffeine|tea|chocolate|cake|sugar|sweets|crisps|biscuits|cheese|ice\s+cream|"
    r"tv|telly|netflix|box\s+sets?|sleep|sun|sunshine|shopping|gossip|christmas\s+music|"
    r"work|meetings?|emails?|paperwork|spreadsheets?)\b"
    r"|\ban\s+overdose\s+of\s+(?:coffee|caffeine|tea|chocolate|cake|sugar|sweets|tv|telly|"
    r"netflix|box\s+sets?|sleep|sun|sunshine|shopping|gossip|work|meetings?|emails?|paperwork|"
    r"spreadsheets?|christmas\s+music)\b")


# ...but a tablet, an insulin dose or a poison in the line is the real thing whatever else it says.
OVERDOSE_A_PILL = re.compile(
    r"\b(?:pills?|tablets?|paracetamol|ibuprofen|insulin|meds|medicines?|bleach|antifreeze|"
    r"heroin|opioids?|tramadol|antidepressants?)\b")


# The faint that is still coming needs the first move, not the appointment. "im going to pass out"
# was answered "Ring 111 or your surgery this week", which is the right advice for a faint that
# has already happened and no use to somebody who is about to go down on a kitchen floor. The
# signs that make it an emergency are settled above this, so the same-day line is what is left at
# the end: sit or lie down now, then be seen today.
FAINT_COMING = re.compile(
    r"\b(?:about|going|gonna)\s+to\s+(?:pass\s+out|faint|black\s+out|collapse|go\s+down)\b"
    r"|\b(?:feel|feels|feeling|felt|think|thinking|look|looking)\s+(?:like\s+)?"
    r"(?:im|i'm|he|she|they)\s+(?:going|gonna|about)\s+to\s+"
    r"(?:pass\s+out|faint|black\s+out|collapse)\b"
    r"|\bnearly\s+(?:passed\s+out|fainted|blacked\s+out)\b"
    r"|\bmight\s+(?:pass\s+out|faint|black\s+out|collapse)\b"
    r"|\b(?:going|gonna)\s+(?:down|faint)\b")


# "i blacked out the windows with curtains" is a verb about a window, not a person going under.
BLACKED_OUT_A_THING = re.compile(
    r"\bblack(?:ed|ing)\s+out\b\s+(?:the|a|an|my|our|his|her|their|all\s+the)\s+"
    r"(?:\w+\s+){0,2}(?:window|windows|room|rooms|light|lights|sun|view|glass|door|doors)\b")


# A person has to be somewhere in the line for it to be about their sight: "everything went black"
# on its own is a power cut, and the lines about a thing have a thing in them, not a person.
BLACKOUT_PERSON = re.compile(
    r"\b(?:i|im|id|ive|me|my|myself|he|hes|she|shes|they|we|us|him|her|his|their|our)\b")


# A machine chokes on its fuel or its muck, not on a bit of food: "my car engine is choking" and
# "the traffic is choking the high street" are not a person in trouble, and the 999 card is the
# worst thing to say to either of them. The choke has to belong to the thing, with no person named
# anywhere in the line, so "my dad choked in the car" keeps every reading.
CHOKE_MACHINE = re.compile(
    r"\b(?:kitchen\s+sink|sinks?|drain\w*|pipes?|toilet|loo|gutter\w*|chimney|radiator|filter|"
    r"engines?|car|van|motorbike|mower|lawnmower|hoover|vacuum|dishwasher|printer|traffic|"
    r"weeds?|lawn|flowerbed\w*|bog|moss|inbox|budget|schedule|calendar|tears?)\b"
    r".{0,30}\bchok\w*\b"
    r"|\bchok\w*\b.{0,30}\b(?:on|with)\s+(?:fuel|petrol|diesel|weeds|leaves|moss|traffic|hair|"
    r"paper|dust|fat)\b")


# A pronoun object counts as a person: "the pipe is choking him" is a body in trouble with the pipe
# as the cause, and the thing word must not take the card from them.
CHOKE_BODY = re.compile(
    r"\b(?:he|she|they|them|him|me|us|i|his|her|their|mum|mom|mother|dad|father|son|daughter|"
    r"husband|wife|partner|brother|sister|friend|baby|child|kid|boy|girl|man|woman|gran|granny|"
    r"nan|grandad|grandma|grandpa|toddler|newborn|infant|mate|neighbou?r)\b")


TAG_CAN = re.compile(r"\bcan\b")


# A follow-up that is only the question ("is that why", "will it stop", "does that matter")
# names nothing for the bot to answer about. The search shrug told the person nothing at all -
# "ive tried a spray / will it stop" got "a quick search online will get you a solid answer" -
# and asking which bit is both honest and keeps the conversation going, which the shrug does not.
BARE_FOLLOW_UP = re.compile(
    r"^(?:and |so |but |ok |okay |right |also |well )*"
    r"(?:is|was|are|were|will|would|does|do|did|can|could|should|has|have|had)"
    r" (?:that|this|it|they|those|these|there)"
    # A tail of its own is a subject - "will it stop raining" is a weather question, not a
    # follow-up - so only the verbs a follow-up is made of may follow the pronoun.
    r"(?: (?:stop|help|work|matter|count|last|clear|ease|go|mean|hurt|pass|settle|fade|fix"
    r"|sort|change|show|be|get|keep|stay|take|worsen|spread|why|how|where)"
    r"(?: (?:up|off|away|out|long|better|worse|anything|enough|now|soon|all|of|it|then|again)){0,2})?"
    r"[?.!]*$")


# What makes the thread one of those: the same readings every other module uses for heavy news,
# asked of the person's own last line.
def _the_line_before(memory):
    """What the person said on the turn before this one, or "" on the first turn."""
    if not isinstance(memory, dict):
        return ""
    turns = [turn for turn in (memory.get("turns") or []) if isinstance(turn, dict)]
    return str(turns[-1].get("user") or "") if turns else ""


def _reads_as_heavy_news(text):
    """True when a line is heavy news - a death, a diagnosis, a loss - rather than an ordinary one.

    The wording pools are for somebody stuck on what to say; a person who says "my daughter died
    and i dont know how to tell my son" is not asking for a shape to put it in first, and the
    grief answer has to win. So the doubt-in-front-of-tell reading stands down on heavy news and
    the later branches read it as what it is.
    """
    said = (text or "").lower()
    return bool(said) and bool(loss.reads_as_loss(said)
                               or reads_as_bad_news(said)
                               or badnews.reads_as_sudden_loss(said))


def _the_thread_is_heavy(memory):
    """True when the line just before this one was heavy news rather than an ordinary turn."""
    return _reads_as_heavy_news(_the_line_before(memory))


# "should i turn it off" straight after the bot has answered about a faulty machine. The line
# reads as a question of taste by its grammar, so it reached UNKNOWN_DECIDE - "That's your call,
# not mine" - which is the one answer that helps nobody: whether to switch a knocking boiler off
# for the night is a fact about the boiler, not the person's weighing up. It was worst where the
# bot had already said to switch the thing off: "the plug socket is sparking" / "should i turn it
# off" got "that's your call" back at it.
# The pronoun has to be the machine, so a bare "should i turn it off" with nothing in the thread
# keeps its honest shrug, and the answer is only ever about a thing of the person's that runs.
SWITCH_OFF_ASK = re.compile(
    r"\b(?:should|shall|do)\s+i\s+(?:just\s+|really\s+|now\s+)?"
    r"(?:(?:turn|switch|shut|power|cut)\s+(?:it|that|this|them|those)\s+off"
    r"|(?:unplug|disconnect|isolate)\s+(?:it|that|this|them|those)"
    r"|stop\s+(?:using|running)\s+(?:it|that|this)"
    r"|take\s+the\s+battery\s+out"
    r"|switch\s+(?:it|that|this)\s+off\s+at\s+the\s+wall)")


# The machines this is asked about by somebody with one going wrong in front of them. A phone or a
# laptop is left out on purpose: "my phone gets really hot / should i turn it off" is a question
# about losing the thing for the evening, which is the person's own call after all.
SWITCH_OFF_THINGS = frozenset((
    "boiler", "boilers", "heating", "radiator", "radiators", "immersion", "pump", "pumps",
    "washer", "washing", "machine", "dryer", "tumble", "dishwasher", "oven", "cooker",
    "hob", "grill", "microwave", "kettle", "toaster", "shower", "socket", "sockets",
    "plug", "plugs", "extension", "fuse", "wire", "wiring", "alarm", "alarms", "smoke",
    "chimney", "extractor", "fan", "heater", "appliance"))


# A fridge and a freezer are the two where switching off is the worse advice: the fault is not
# going to burn the house down and a day without power to it is a bin bag of food. Both keep the
# honest answer they had.
# A stove is not switched off either - it is a fire, and it burns down - so a smoking wood burner
# keeps the answer it has rather than being told to turn itself off.
KEEP_IT_RUNNING = frozenset(("fridge", "freezer", "freezers", "fridges", "stove", "stoves",
                             "burner", "burners", "woodburner", "chiminea", "brazier",
                             "barbecue", "bbq", "smoker", "fireplace"))


# What makes it a fault rather than a machine the person is simply running: the noise, the water,
# the heat, the smoke. Without one of these the line is a question about the bill - "the heating is
# expensive / should i turn it off" is money, and "switch it off and have it looked at" is
# nonsense for it. The bot's own answer telling them to switch it off counts as the fault too.
SWITCH_OFF_FAULT = frozenset((
    "noise", "noisy", "knocking", "knocks", "knock", "banging", "bangs", "rumbling",
    "humming", "hums", "buzzing", "buzzes", "rattling", "grinding", "screeching", "squealing",
    "sparking", "sparks", "smoking", "smoke", "leak", "leaks", "leaking", "leaked", "dripping",
    "drips", "drip", "tripping", "trips", "tripped", "blowing", "blown", "fuse", "fault",
    "faulty", "broken", "broke", "stopped", "stops", "stopping", "cutting", "cuts", "hot",
    "overheating", "burnt", "burning", "scorch", "smell", "smells", "smelly", "beeping",
    "beeps", "chirping", "chirps", "flashing", "flashes", "error", "stuck", "jammed", "weak",
    "losing", "pressure", "condensation", "damp", "screech", "clunking", "clicking", "hissing"))


# Gas, carbon monoxide and a fire in the room are not "switch it off" turns at all: the safety
# line has already told them to get out and ring, and telling somebody to go back in and reach for
# a switch is the one thing that could hurt them. "Smoke alarm" is the exception - there the
# question is about the battery, not about going near a fire.
# Gas, carbon monoxide and fumes are never a "switch it off" turn: the safety line has already
# told them to get out and ring, and telling somebody to go back into a room and reach for a switch
# is the one thing that could hurt them.
SWITCH_OFF_GET_OUT = re.compile(
    r"\b(?:gas|gasoline|petrol|carbon monoxide|fumes?|flames?|ablaze|on fire|fire brigade)\b")


# Smoke is the same only when it is loose in the room. Where the bot's own answer has already told
# them to switch the thing off - "smoke coming out of my laptop" was answered "switch it off at the
# wall and unplug it" - the follow-up is asking whether they meant it, and confirming is the reply.
SMOKE_ABOUT = re.compile(r"\b(?:smoke|smoking|smoulders?|smouldering|scorch(?:ed|ing)?)\b"
                         r"(?!\s+alarm)")


# What the bot's own last answer said, when it had already told them to do it.
ALREADY_SAID_OFF = re.compile(
    r"\b(?:turn|switch|shut|power)\s+(?:it|that|this|the\s+\w+)\s+off"
    r"|\bunplug|\bleave\s+it\s+off|\boff\s+at\s+the\s+wall|\bswitch(?:ed)?\s+off|\bstop\s+the\s+cycle")


SWITCH_OFF_ALREADY = (
    "Yes - that is the thing to do, and I would do it now rather than after one more try. Off and "
    "left off is the safe place for it until somebody has looked at it.",
    "Yes, do that: off at the wall, and leave it off. Whatever is wrong with it does not get "
    "better for being run again tonight.",
    "Yes. Switch it off, unplug it if the plug is easy to reach, and leave it alone until it has "
    "been looked at properly.",
)


SWITCH_OFF_ADVISE = (
    "I would. Switch it off and leave it off, then get somebody to look at it - a fault you can "
    "hear or see is the one thing running it again makes worse.",
    "Yes - off, and a call to somebody who can look at it. A night without it is much cheaper "
    "than a night with it leaking, smoking or banging away.",
    "Turn it off and leave it off until somebody has seen it. If you can smell burning or see "
    "anything black, stop using it today rather than waiting for it to get worse.",
)


# Taking the battery out of a chirping smoke alarm is the one switch-off where the safe answer is
# no: the noise stops and so does the alarm, on the night it might be needed.
SWITCH_OFF_BATTERY = (
    "Swap it rather than leaving it out: a chirping alarm is annoying, an alarm with no battery in "
    "it is useless on the night it matters. If a fresh battery does not stop the chirp, take the "
    "whole unit down and get a new one - and if it is mains wired, take it off its base rather "
    "than leaving it with no battery at all.",
)


UNKNOWN = (
    "I'm not sure about that one, sorry — I'd rather not guess. A quick search online will "
    "get you a solid answer, and I can help you make sense of what you find.",
    "That's beyond what I know well, sorry. Searching for it will turn up better sources than "
    "I can offer; tell me what you find and I'll help you weigh it up.",
    "I don't know enough to answer that honestly. A search should sort you out quickly — and "
    "I'm happy to help with the rest of it.",
)


# "did you see the match last night" is not a person asking the bot to look something up: it is the
# first half of a conversation, and the search hedge ("A quick search online will get you a solid
# answer") tells them to go and read about their own evening. So the shape is read as the
# invitation it is and the reply asks for the story - the same turn a friend gives, and the one
# that lets the person say the thing they came to say. Two guards keep it off the lines that are
# not this: a thing of the person's own ("did you see my keys anywhere", "did you see the doctor")
# is a question the bot can help with, and so is a reading it genuinely cannot do from here (the
# forecast, the listings, the scores), which keep the honest hedge.
ASKED_IF_I_SAW = re.compile(
    r"^\s*(?:(?:and|so|but|oh|ah|anyway|anyways|well|hi|hey|right|now|look)\s+)*"
    r"(?:did|have|do)\s+(?:you|u)\s+"
    r"(?:see|seen|hear|heard|watch|watched|catch|caught|read|follow|following)\s+"
    r"(?:the|that|about|any|much)\b")


# The tail that makes it the person's own business rather than the day's news, and the one that
# asks the bot to have followed what the person said rather than the world.
NOT_THE_NEWS = re.compile(
    r"\b(?:my|our|mum|mom|dad|mother|father|wife|husband|partner|boyfriend|girlfriend|son|"
    r"daughter|kid|kids|child|children|baby|brother|sister|nan|grandma|grandad|granny|friend|"
    r"boss|manager|colleague|neighbour|landlord|doctor|gp|nurse|dentist|midwife|vet|surgeon|"
    r"appointment|letter|email|e-mail|bill|invoice|results?|test)\b"
    r"|\bwhat i (?:said|mean|meant|wrote|sent|told you|asked)\b")


# What cannot be done from here keeps its honest answer: these are lookups, not a chat.
LOOKED_UP = re.compile(
    r"\b(?:forecast|weather|news|listings?|scores?|results?|prices?|times?|timetable|"
    r"timetables|traffic|schedule|opening|hours|fixtures?|table|standings|reviews?|ratings?)\b")


# "did you see it" is the commonest way to ask, and "it" is only knowable from the line above:
# after "we watched the final together" the thing being asked about is the final, and the search
# hedge ("a quick search online will get you a solid answer") is an answer to a lookup nobody
# made. The referent is read from the previous turn and the noun has to be one you watch, so
# "my results came back" and "did you see it" is still the results, not a match.
SAW_IT = re.compile(
    r"^\s*(?:(?:and|so|but|oh|ah|anyway|anyways|well|hey|right|now)\s+)*"
    r"(?:did|have|do)\s+(?:you|u)\s+"
    r"(?:see|seen|hear|heard|watch|watched|catch|caught)\s+"
    r"(?:it|that|him|her|them)\b"
    r"(?:\s+(?:last night|the other night|yesterday|tonight|today|this morning|on saturday|"
    r"at the weekend|yet))?\s*\??\s*$")


WATCHABLE = re.compile(
    r"\b(?:match|game|final|semi(?:-final)?|film|movie|episode|documentary|show|series|"
    r"season|race|fight|gig|concert|play|debate|episode|highlights|"
    # A match is often named by its parts: "i saw the whole second half" is the thing they want
    # to talk about, and "did you see it" is the ask for it rather than a check on what they said.
    r"first half|second half|highlights|extra time|finale)\b")


# The rest of what people ask whether the bot saw: the day's news that is talked about rather
# than looked up, and the words that stand in for a match without naming one.
SAW_NEWS = re.compile(
    r"\b(?:election|football|rugby|cricket|tennis|boxing|olympics|formula one|f1|"
    r"the budget|budget|the bill|the vote|referendum|the debate|the interview|the speech|"
    r"the wedding|the funeral|the fight|the final|the match|the game|the semi)\b")


def names_the_thing_worth_watching(clean):
    """True when a "did you see the ..." line names something a person watches.

    "did you see the match last night" opens a conversation; "did you see the state of the
    kitchen", "did you see the queue at the post office" and "did you see the postman" are not
    about anything watched, and a match reply to them ("Not a bit of it. Tell me - what
    happened?") reads as a bot that was not listening. Only the noun the line names is read,
    and only the four words after it, so a later clause cannot make a line this one.
    """
    said = SAW_IT_OR_THE.match(clean)
    if not said:
        return False
    tail = " ".join(clean[said.end():].split()[:5])
    return bool(WATCHABLE.search(tail) or SAW_NEWS.search(tail))


SAW_IT_OR_THE = re.compile(
    r"^\s*(?:(?:and|so|but|oh|ah|anyway|anyways|well|hi|hey|right|now|look)\s+)*"
    r"(?:did|have|do)\s+(?:you|u)\s+"
    r"(?:see|seen|hear|heard|watch|watched|catch|caught|read|follow|following)\s+"
    r"(?:the|that|about|any|much)\b")


def reads_as_if_i_saw(text, memory=None):
    """True when the line asks whether the bot saw the thing the person is talking about.

    Held as one reading because it is used twice: where the reply is chosen, and where the
    composer says the line is its own (bot/modules/greeting.takes_as_it_comes). The memory store
    reads "did you see it" as a question about what the person just said - "Yes - you watched the
    final together" - at PRIORITY 7000, so the composer never got the line until it claimed it.
    """
    clean = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    if not clean or NOT_THE_NEWS.search(clean) or LOOKED_UP.search(clean):
        return False
    if SAW_IT.match(clean):
        return bool(WATCHABLE.search(str(last_user(memory) or "").lower()))
    if ASKED_IF_I_SAW.match(clean):
        return names_the_thing_worth_watching(clean)
    return False


SELF_WORDS = frozenset("""
learn learns learning learned learnt teach taught train trained
think thinks thinking thought opinion opinions view views judgement judgment mind brain
smart clever intelligent wise understand understands reason senses
mistake mistakes wrong right perfect honest
feel feels feeling feelings emotion emotions
alive living human person people body bodies family friends friend age old here located
program programmed code computer machine robot ai chatbot bot conscious consciousness aware
sentient knowledge know knows exist exists existence point purpose there
decide decides deciding decided decision decisions choose chooses choosing chosen choice
choices pick picks picking select selects sort sorts answer answers answering answered
regret regrets regretted regretting
sums sum maths math mathematics arithmetic add adds adding addition subtract multiply divide
total percentage percentages percent calculate calculation count counting
spell spells spelling spelled spelt grammar punctuation apostrophe comma commas typo typos
# The filler the same asks are said with ("can you add up", "can you spell it for me", "can you
# check my grammar") belongs here; the nouns a request is made of do not. `bill`, `check`, `word`
# and `split` were in this set for one revision and let a real request through to the card: "can
# you add up a bill" lost its Citizens Advice answer and was told the bot can do sums (red-robin,
# #11382). Every word left in `SELF_WORDS` has to be true of a line about the bot itself.
up a an for my it this that
""".split())
