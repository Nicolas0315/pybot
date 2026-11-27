"""Part 7 of 17 of the composer's safety net, split out of `fallback`.

Everything here is re-exported from `fallback`, so callers import it from there as before.
"""
import random
import re

from ..understanding.kinds import (two_ends_of_one_scale)

from .fallback_data import (
    ADVICE_AGAIN,
    ADVICE_COOL,
    ADVICE_COOL_WORDS,
    ADVICE_LENGTH,
    ADVICE_TIME,
    ADVICE_WORSE,
    BODY_PARTS,
    CARE_HURTS,
    CARE_POINTER,
    CARE_WORDS,
    CHECK_PHRASES,
    CHOICE_BETWEEN_PEOPLE,
    CHOICE_HEALTH,
    CHOICE_LIGHT,
    CHOICE_LIGHT_PICK,
    CHOICE_PEOPLE,
    CHOICE_PHARMACIST,
    CHOICE_STAKES,
    CHOICE_THERAPY,
    CHOICE_WEIGH,
    CRISIS_WORDS,
    EASING_FILLER,
    HEALTH_WORDS,
    HANDS_BACK,
    HELP_TAIL,
    NAMED_TYPES,
    PLASTER_IT,
    PRESENCE_LEFTOVER,
    SORE_HANDS,
    SORE_SERIOUS,
    SYMPTOM_WORDS,
    UNKNOWN,
    UNKNOWN_DECIDE,
    UNKNOWN_HEALTH,
    UNKNOWN_MONEY,
    UNKNOWN_WORD,
    UNKNOWN_WORRY,
    WHOLE_LIST_AFTER,
    WORD_ANYWHERE,
    _A_PERSON,
    _CREATIVE,
)

from .fallback_part_01 import (
    DECIDE_OPENING, DECIDE_SANITY, HANDS_IT_BACK, PLASTER_ON, _DEFINITION,
)
from .fallback_part_02 import (
    REPAIR_ANSWER, REPAIR_HOW, UNKNOWN, _a_call_for_help, _a_small_social_decide, _about_a_sore,
    _money_decision, _reads_as_worry,
)
from .fallback_part_06 import (
    ADVICE_CUE, ADVICE_LENGTH, NO_RELIEF,
)


def _someone_is_a_patient(clean, turns, look_back=4):
    """True when the line or the last few turns name a place that keeps someone in.

    The visit pools differ only in whether a ward is somewhere to go: "ask whoever is on the
    ward" is right after "my mum is in hospital" and wrong after "i cut my hand badly".
    """
    if IN_HOSPITAL.search(clean):
        return True
    for turn in turns[-look_back:]:
        if IN_HOSPITAL.search(str(turn.get("user") or "").lower()):
            return True
    return False


def unknown_pool(clean, words=()):
    """The pool for a question the bot cannot answer, chosen by the kind of question it is."""
    words = words or clean.split()
    if HANDS_IT_BACK.match(clean):
        return HANDS_BACK
    calling = _a_call_for_help(clean)
    if calling:
        return calling
    # A repair asked for as a method ("how do i make it right with her", "how do i make it up to
    # my mum"): the person has decided to apologise and wants the shape of it, which is a concrete
    # answer a friend gives. It is read before the decide gate because "how do i" is not one of
    # the shapes DECIDE_OPENING reads, and with the person named, because the same words about a
    # machine ("how do i fix my hoover") are somebody else's question.
    if REPAIR_HOW.search(clean) and set(words) & _A_PERSON:
        return REPAIR_ANSWER
    if _reads_as_worry(clean, words):
        return UNKNOWN_WORRY
    if _about_a_sore(clean, words):
        if set(words) & SORE_SERIOUS:
            return UNKNOWN_HEALTH
        return SORE_HANDS
    if PLASTER_ON.search(clean):
        return PLASTER_IT
    if any(phrase in clean for phrase in WORD_ANYWHERE) and not (_CREATIVE & set(words)):
        return UNKNOWN_WORD
    # "do i clean the head or the tray first" is not an unknown ask: it is an order, and the
    # light-choice reader never sees it (the shape is not a bare "x or y"). Read it here, after
    # the health and worry lines that must keep their own answer.
    if not _DEFINITION.search(clean) and _an_order_of_work(_choice_sides(clean), clean):
        return ORDER_OF_WORK
    if ((DECIDE_OPENING.search(clean) or DECIDE_SANITY.search(clean))
            and not _DEFINITION.search(clean)):
        if (set(words) & (HEALTH_WORDS | SORE_SERIOUS)
                or any(phrase in clean for phrase in CHECK_PHRASES)):
            return UNKNOWN_HEALTH
        if _money_decision(clean):
            return UNKNOWN_MONEY
        social = _a_small_social_decide(clean, words)
        if social:
            return social
        return UNKNOWN_DECIDE
    return UNKNOWN


def _advice_in(last):
    """Was the last answer something the person could do and report back on?"""
    return len(last) >= ADVICE_LENGTH or bool(ADVICE_CUE.search(last.lower()))


# A report on an answer is built from the answer's own words: the oven answer says "wipe it out
# with a damp cloth and a little vinegar" and the person comes back with "i wiped it and now its
# worse" or "i boiled it with vinegar and now its worse". No closed list of report words can hold
# every verb and every thing an answer names, and those words are the whole of the evidence that
# the line is about that answer - so a word the answer used counts as a report word here. What is
# left over still has to be in REPORT_FILLER, which is what keeps "i tried that new cafe" and "i
# wiped it and the dog ate the cloth" out of this reading.
#
# The past forms are built rather than looked up, because people write the step down in the past
# ("wiped", "scrubbed") and an answer says it with the verb or the -ing ("it takes some
# scrubbing"). The irregulars are the ones people use about a repair: "i took it off", "i left it
# on", "i put it back".
IRREGULAR_STEP = {
    "took": "take", "made": "make", "put": "put", "left": "leave", "kept": "keep",
    "set": "set", "cut": "cut", "held": "hold", "stood": "stand", "gave": "give",
    "got": "get", "ran": "run", "brought": "bring", "sent": "send", "found": "find",
    "told": "tell", "did": "do", "dug": "dig", "hung": "hang", "stuck": "stick",
    "bled": "bleed", "tore": "tear", "wore": "wear", "lit": "light",
    "burnt": "burn", "swept": "sweep", "wrung": "wring", "shut": "shut",
    "spun": "spin", "went": "go", "saw": "see", "drew": "draw",
}


# How the upshot is said is part of the report, not a claim about the thing. "i wiped it and now
# its clean" is the answer's own step plus "clean", and the oven answer never uses that word, so
# the gate rejected the line on the one word that was only saying it had worked. These are the
# words a verdict is written in, and each says nothing about a subject of its own. (Not the
# `VERDICT_WORD` regex above, which is chat's list of how a person says a thing annoyed them.)
REPORT_VERDICT_WORD = frozenset((
    "fine", "sorted", "clean", "cleaner", "clear", "cleared", "working", "worked", "works",
    "fixed", "ok", "okay", "normal", "done", "gone", "better", "worse", "good", "great",
    "brilliant", "perfect", "results",
))


NO_STEP = frozenset()


def _the_words_in(advice):
    """The words of an answer, with the past forms a report would write its steps in.

    An answer says a step with an -ing ("it takes some scrubbing", "leave it overnight") as
    often as with the verb itself, so the stem is read too: "scrubbing" gives "scrubbed" and
    "wiping" gives "wiped". Every form is built, never checked, because a form nobody writes
    only ever lets a word be read as one the answer used.
    """
    if not advice:
        return NO_STEP
    said = set(re.findall(r"[a-z']+", str(advice).lower()))
    if not said:
        return NO_STEP
    words = set(said)
    for word in said:
        if len(word) < 3:
            continue
        if word.endswith("ing") and len(word) > 4:
            stem = word[:-3]
            words.add(stem)              # cleaning -> clean
            words.add(stem + "e")        # wiping -> wipe, making -> make
            if stem[-1:] == stem[-2:-1]:
                words.add(stem[:-1])     # scrubbing -> scrub, stopping -> stop
    forms = set(words)
    for word in words:
        if not word:
            continue
        forms.add(word + "ed")               # clean -> cleaned, oil -> oiled
        forms.add(word + "d")                # wipe -> wiped
        forms.add(word + word[-1] + "ed")    # scrub -> scrubbed, stop -> stopped
    for past, base in IRREGULAR_STEP.items():
        if base in words:
            forms.add(past)
    return forms


# The same verdict said as a fact about the thing rather than about the doing: "i wiped it and
# now its worse", "i scrubbed it and its worse now". The step is the answer's own verb (see
# REPORT_FILLER and `_the_words_in`), so all a report of that shape has of its own is the time
# word and the verdict - and read as neither, the line was nobody's: "i wiped it and now its
# worse" after the oven answer was answered as tiredness. "already" counts the same way ("its
# worse already"), and so does the verdict before the time word ("its gone worse now").
# The same report the other way round: the step worked and the thing is done. "i wiped it and now
# its clean" after the oven answer was nobody's - "wiped" is not a report word on its own (see
# `_the_words_in`), so the line reached the chat module, which read it as tiredness, and "i
# cleaned the port and now its fine" was told "You've already cleaned the port". A thing that is
# now fine is the end of the advice, and the answer to it is that it is sorted.
REPORT_NOW_FINE = re.compile(
    r"\b(?:now|already)\s+(?:its|it'?s|it is|they'?re|they are|things are|everything is)\s+"
    r"(?:all |much |a lot |so |loads |back to )?"
    r"(?:fine|sorted|clean|clear|working|fixed|fixed itself|ok|okay|normal|done|gone|"
    r"better|improved)\b"
    r"|\b(?:it|that|this) (?:worked|did it|did the trick|has done it|is sorted)\b"
    r"|\b(?:sorted|fixed) (?:now|already)\b"
    # People put the time word at the front as often as the back: "its working now", "its fine
    # now", "theyre sorted now". The first alternative reads only the front one.
    r"|\b(?:its|it'?s|it is|they'?re|they are|things are)\s+"
    r"(?:all |much |a lot |so |loads )?"
    r"(?:fine|sorted|clean|clear|working|fixed|ok|okay|normal|done|gone|better|improved)"
    r"\s+(?:now|again|already)\b")


WORSE_NOW = (
    r"\b(?:now|already)\s+(?:its|it'?s|it is|they'?re|they are|things are|everything is)\s+"
    r"(?:much |even |far |loads |a lot |so |still )?(?:worse|sorer)\b"
    r"|\b(?:much |even |a lot |far )?(?:worse|sorer)\s+(?:now|already|than before)\b"
    r"|\b(?:got|gets|getting|gone)\s+(?:much\s+|even\s+|a\s+lot\s+)?worse\b")


TRIED_WORSE = re.compile(
    r"\b(?:made (?:it|things|me) (?:worse|sorer)|made me worse)\b|" + WORSE_NOW)


TRIED_NO_CHANGE = re.compile(
    r"\b(?:(?:not|isnt|isn't|not really) (?:helping|helped|working|worked)|"
    # "none of that worked" and "none of it helped" are the same report as "it doesnt work", and
    # they were falling through to the fault reader, which asks about a boiler.
    # Said in the present tense it is the same report and the opposite of helped: "none of it
    # works" after "my laptop is broken" and after "my back hurts when i run" was congratulated
    # - "That's what you want to hear. Carry on with it" and "Good - that is the one to keep
    # doing" - because only the past tense was read and the helped pool took the words "it works"
    # out of the middle of the sentence.
    r"none of (?:that|it|them|these) (?:has |have )?(?:worked|works|helped|helps|done anything|"
    r"been any use|is working|are working)|"
    r"(?:did not|didnt|didn't|does not|doesnt|doesn't|wont|won't) (?:work|help|"
    r"do (?:it|anything|much))|"
    r"(?:hasnt|hasn't) (?:helped|worked)|no (?:change|difference|better|improvement)|"
    r"still the same|same as before|nothing (?:works|is working|has worked|has changed|"
    r"changed|yet|different|so far))\b")


# A report that says the trouble is still there: "ok done that, still dripping". The finished-step
# pool asked "Any change since you started?" of a line that had just said what the change was. It is
# read before the finished-step readings but after the ones that name a good outcome, because the
# person has told the answer the outcome and the only thing left to say is the no-change one.
STILL_THE_TROUBLE = re.compile(
    r"\bstill\b(?![^.?!]*\b(?:working|works|helping|helped|better|fine|good|sorted|"
    r"doing the trick)\b)")


# "still" is in the adverbs because "its still working" is the helped outcome said with a time in
# it, and the reader below takes a bare "still" for the trouble that has not moved.
TRIED_HELPED = re.compile(
    r"\b(?:(?:it|that|this|they)s? (?:is |are |seems? )?"
    r"(?:actually |really |definitely |properly |still )?(?:helping|helped|working|works|"
    r"help a bit|doing the trick)|helped (?:a (?:bit|little|lot|load))|"
    r"(?:a bit|lots|much|loads) better|feeling better|helps a bit)\b")


TRIED_IT = re.compile(
    r"\b(?:(?:i|we|ive|i've|weve|we've|i have|we have|i had|we had) "
    r"(?:did|tried|gave|used|started|have tried|had tried|went with) "
    r"(?:what you (?:said|suggested)|that|this|it)" + WHOLE_LIST_AFTER +
    r"|did what you (?:said|suggested|told me)|"
    r"(?:been|keep|still) (?:doing|trying|taking|walking|using) (?:it|that|this|them))\b")


# The same report with the subject dropped, which is how it is typed mid-conversation: "tried
# that", "tried it already". Anchored like DONE_IT, because "what tried that" is a question
# about somebody else.
TRIED_THAT_ONLY = re.compile(
    r"^(?:(?:ok|okay|alright|right|so|well|yeah|yep|yes|cool|fine|and|but|then|i|we|ive|i've|"
    r"weve|we've)\s+)*"
    r"(?:(?:have|had)\s+)?(?:tried|been trying)\s+(?:it|that|this|them)" + WHOLE_LIST_AFTER + r"\b")


# The report on the whole of it: "ive tried them all", "tried everything", "done them all". Read
# only when the bot's last answer offered nothing to pick from, because after a list of films the
# same words are a turn-down the store owns; after a paragraph of advice they are the person
# saying they have done what it said. Left in that case, the advice answer's second half came back
# as more work to do: "my knee hurts when i run" / "ive tried them all" got "Ice after a run and
# run on softer ground..." after the paragraph that already said it.
# These patterns live in their own file: this one grew past the 1 MB a clone may carry and
# every change to it was refused. Imported here in place of their definitions.
from .fallback_words import (  # noqa: F401 - read here by the patterns below
    ADVICE_AGAIN_ASK,
    ADVICE_COOL_ASK,
    ADVICE_TIME_ASK,
    ADVICE_TIME_WORDS,
    ADVICE_WORSE_ASK,
    AN_ANSWER_ABOUT_A_NO,
    ASKS_WHY,
    BURN_ASK,
    BURN_BLISTER_LINE,
    BURN_ON_IT,
    BURN_THING,
    BURN_WORD,
    CARE_SEEN_ASKS,
    DONE_IT,
    FEELS_BETTER,
    FEELS_NOT_BETTER,
    HYPOTHETICAL,
    IN_HOSPITAL,
    MEDICAL_PLACE,
    MOVE_ON,
    NOT_A_VISIT,
    OWN_NO,
    POP_A_BARE_IT,
    REFUSED,
    REFUSED_FAMILY,
    REFUSED_NOT,
    REFUSED_NO_OBJECT,
    REFUSED_PARTY,
    STILL_GOING,
    TRIED_THE_LOT,
    VISIT_ASK,
)


def _asks_about_the_advice(clean, last):
    """The pool for a question about the advice just given, or None.

    Read only inside a care thread, after the bot has said what to do. Two gates and an order:
    the cooling pool needs an answer that cooled something, and the other three need an answer
    that gave a time. A line that asks what to do if it does not work ("what if it doesnt stop")
    is read before the time ask, which can share its words without being the question.
    """
    if ADVICE_COOL_ASK.search(clean) and any(word in last for word in ADVICE_COOL_WORDS):
        return ADVICE_COOL
    if not ADVICE_TIME_WORDS.search(last):
        return None
    if ADVICE_WORSE_ASK.search(clean):
        return ADVICE_WORSE
    if ADVICE_TIME_ASK.search(clean):
        return ADVICE_TIME
    if ADVICE_AGAIN_ASK.search(clean):
        return ADVICE_AGAIN
    return None


# A line that says someone is with them, or on the way, is the one piece of good news a person
# in an emergency can give. "Do what the emergency line says" answers nothing there: what they
# need is to hear that they are no longer alone with it (#264 followed this up from #205).
# The company needs a person in front of it: "what's wrong with me" contains "with me" and is a
# question about the person themselves, not news that someone arrived. "come in" needs an
# arrival subject too, or a cat wants to come in and gets a line about not being alone.
ARRIVING = re.compile(
    r"\b(?:neighbou?rs?|nurse|doctor|paramedic|ambulance|crew|flatmate|housemate|mate|friend|"
    r"sister|brother|mum|mom|dad|mother|father|carer|midwife|police|son|daughter|wife|husband|"
    r"partner|boyfriend|girlfriend|aunt|uncle|cousin|gran|nan|grandad|grandma)\b")


WITH_YOU = re.compile(
    r"\b(?:(?:is|are|was|were)\s+with\s+me|(?:is|are)\s+here|come\s+over|coming\s+over|"
    r"come\s+round|coming\s+round|on\s+(?:his|her|their|its)\s+way|on\s+the\s+way|"
    r"not\s+on\s+my\s+own|not\s+alone|sitting\s+with|staying\s+with|staying\s+tonight|"
    r"staying\s+the\s+night|next\s+door|neighbours?\s+(?:is|are|coming|here))\b")


def _feels_better(clean):
    """True for a line that says they are easing, and says nothing else.

    "i feel a bit better now" is a report on the emergency; "im ok now, where do i get a tetanus
    jab" is a question that happens to carry an easing, and answering it with "that's a relief"
    drops what the person asked. So the easing words and the thing that was easing are taken out
    and anything with content left means the line is about that instead.
    """
    if not FEELS_BETTER.search(clean) or FEELS_NOT_BETTER.search(clean):
        return False
    if "?" in clean or MOVE_ON.search(clean):
        return False
    for word in re.findall(r"[a-z']+", clean):
        if word in EASING_FILLER or word in SYMPTOM_WORDS or word in BODY_PARTS \
                or word in HEALTH_WORDS:
            continue
        return False
    return True


# The answer above can send them somewhere: "that needs an ambulance now", "ring 111 or your GP
# today", "a joint that won't take weight wants an X-ray today, at A&E". What that answer asked for
# is a route out of the house, so an easing after it is not the end of the thread. Only the opening
# sentence counts, because that is where a card puts the thing to do: the cut-hand card opens on
# the pressure and keeps "if it's still going after ten minutes, ring 999" for later, and a cut
# that eases is the easing to answer.
ROUTE_NAMED = re.compile(
    r"\b(?:999|911|112|111|a\s?&\s?e|a and e|accident and emergency|ambulance|paramedic|"
    r"urgent care|out of hours|x-ray)\b")


def _no_relief(memory, last=""):
    """True when the thread is one where feeling better does not mean being out of danger."""
    lines = [str(last or "")]
    for past in (memory.get("turns") or []):
        if isinstance(past, dict):
            lines.append(str(past.get("user") or ""))
            lines.append(str(past.get("bot") or ""))
    if any(NO_RELIEF.search(line.lower()) for line in lines if line):
        return True
    # A stroke that eases is still a stroke. "Glad to hear it, go steady for the rest of the day"
    # is the wrong thing to tell someone the answer above sent to A&E, so the easing keeps the
    # referral instead of sending them back to their day. A crisis answer is the exception:
    # nobody has been sent out and nothing has come back, so "the worst of it is passing" is the
    # pool an easing wants there.
    for past in (memory.get("turns") or []):
        if not isinstance(past, dict):
            continue
        said = str(past.get("bot") or "")
        if any(word in said.lower() for word in CRISIS_WORDS):
            continue
        opening = re.split(r"(?<=[.?!])\s", said.strip(), 1)[0].lower()
        if opening and ROUTE_NAMED.search(opening):
            return True
    return False


def _someone_is_arriving(clean):
    """True for a line that says someone is with the person, or on the way to them."""
    if WITH_YOU.search(clean):
        return True
    return bool(re.search(r"\b(?:come|coming|let)\s+(?:in|round)\b", clean)
                and ARRIVING.search(clean))


RESOLVED = re.compile(
    r"\b(?:it's|its|it is|that's|thats|that is|this is) (?:out|over|stopped|fine|done|ok|okay|"
    r"under control|settled)\b"
    r"|\bthe \w+ (?:is|has|have|'s) (?:out|stopped|arrived|come|came|gone|cleared|dried up|"
    r"here)\b"
    r"|\b(?:ambulance|paramedics?|fire brigade|fire service|firemen|crew|doctor|nurse|police|"
    r"medics?) (?:is|are|'s|have|has) (?:here|arrived|come|came|been|on the scene)\b"
    r"|\b(?:(?:i'm|im|i am|we're|were|we are|she's|shes|she is|he's|hes|he is|they're|theyre|"
    r"they are|you're|youre|you are) (?:ok|okay|safe|fine|alright|better|out of it))\b"
    r"|\b(?:bleeding|bleed|fire|smoke|pain|it) (?:has |'s )?stopped\b")


# "It's stopped bleeding now but the edges look a bit open": the close is the first half of the
# line, so the half that still needs a person wins and the answer keeps the care pointer.
NEEDS_SEEN = re.compile(
    r"\b(?:open|gaping|gapes|deep|swollen|swelling|infected|numb|dizzy|hurting|hurts|"
    r"throbbing|worse|getting worse|pus|red streaks)\b")


ALREADY_RANG = re.compile(
    r"\b(?:i|we|ive|i've|weve|we've|he|she|they|dad|mum|mom)\s+(?:have\s+|has\s+|already\s+)?"
    r"(?:rang|called|phoned)\b"
    r"|\brang (?:them|999|911|112|an ambulance|the ambulance)\b")


# The numbers that are a conversation rather than a dispatch: a person who has rung the
# samaritans, a crisis line or NHS 111 has done the right thing and nobody is coming to their
# door. The hold pools above are written for the 999 call ("the operator", "the crew are on
# their way", "keep the line open"), so they promised an ambulance that had never been sent.
A_HELPLINE = re.compile(
    r"\b(?:samaritans|116\s?123|988|crisis (?:line|text|team|service|number)|helpline|help line|"
    r"shout|papyrus|nhs\s?111|111|doctor|gp|surgery|out of hours|vet)\b")


# said about the speaker, not about the patient: "my mum is shaking" is a symptom and gets
# care advice, "i can't stop shaking" is the person and gets the pool above.
ABOUT_THE_SPEAKER = re.compile(r"\b(?:i|i'm|im|i am|i've|ive)\b")


FRIGHTENED = re.compile(
    r"\b(?:scared|afraid|frightened|terrified|fear|fearful|panicking|panic|shaking|shaken|"
    r"trembling|dreading|dread|shocked|in shock|crying|in tears)\b")


# "im not scared", "nothing to be scared of": a line that turns the fear off is not the fear.
NOT_FRIGHTENED = re.compile(
    r"\b(?:not|never|no|nothing|isn't|isnt|aren't|arent|wasn't|dont|don't|doesn't)\b"
    r"(?:\s+\w+){0,3}\s+(?:scared|afraid|frightened|terrified|fear|panicking|panic|shaking|"
    r"trembling|shocked|crying)\b")


# A card that *tells* the person to ring, against one that only names the number as a threshold:
# "ring 999 now" is an emergency the bot is standing in the middle of, "if it won't stop, that's
# 999 or 911" is first aid that has just handed the person a red flag. The difference is the verb
# in front of the number, and it decides what the next line is: after the first aid the person
# wants the care line the card leaves ("get it looked at today"), not "ring 999 or 911 now" a
# second time for a cat scratch.
CALL_THEM_NOW = re.compile(
    r"\b(?:ring|call|phone|dial)\b(?:\s+\w+){0,3}\s*(?:999|911|112|an ambulance|the ambulance|"
    r"emergency services|the emergency services)\b")


# A first-aid card names the red flag as well as the care line, and the person's next line can be
# that flag met rather than a new subject. The fall card is the clear one: it hands over "cannot
# get up or put weight on it, who hit their head" as the point where the answer becomes 999, and
# then "im on blood thinners" or "it really hurts when i stand on it" is the same injury said
# worse. Because the card only names the number as a threshold, `CALL_THEM_NOW` reads the thread
# as not live and the person is sent to a pharmacist with a broken hip (quality watch, foo-06 and
# foo-07). These are the words that turn watch-it-&-see into ring-now, and the fall card is the
# one they turn; a scratch on a blood thinner is still a scratch.
STAKES_WORDS = re.compile(
    r"\b(?:blood ?thinners?|warfarin|apixaban|rivaroxaban|dabigatran|edoxaban|clopidogrel|"
    r"heparin|anticoagulants?)\b"
    r"|\b(?:i'?m|im|hes|he'?s|shes|she'?s|my (?:mum|dad|mother|father|husband|wife|partner|"
    r"gran|grandma|grandad|grandpa|nan))\s+(?:7|8|9)\d\b"
    r"|\b(?:7|8|9)\d\s*(?:years? old|years|yo)\b"
    r"|\b(?:can'?t|cannot|can not)\s+(?:put\s+)?(?:any\s+)?weight\b"
    r"|\b(?:confused|not with it|passed out|knocked out|blacked out|unconscious)\b"
    r"|\b(?:hurts?|agony|killing me|painful)\b[^.]{0,25}\b(?:stand|standing|walk|walking|"
    r"step|stepping|put weight)\b", re.I)


# The card those words make worse: first aid for a fall or a bang, where age, a blood thinner and
# not being able to weight-bear are exactly what turns "watch it" into "ring 999".
FALL_FIRST_AID = re.compile(
    r"\b(?:put weight|cannot get up|can'?t get up|hit (?:their|your|his|her) head|"
    r"head injury|fell|fall|bruising)\b", re.I)


# Words that keep a line inside an emergency the bot has just answered: the emergency itself,
# the injury, the people in it, and the practical questions people ask mid-crisis.
CARE_WORDS = frozenset("""
    safe safely unsafe outside out stairs stair lift door window smoke fire fires flame flames
    alarm spread spreading burn burned burning bleed bleeding blood cut cuts wound bandage
    dressing plaster pain painful hurt hurts hurting aching sore tender stinging smarting
    stiff swollen swelling bruised numb infected infection throbbing
    aspirin paracetamol ibuprofen painkiller painkillers antihistamine
    worse still soak soaking soaked wait waiting
    ambulance paramedic police operator emergency 999 911 112 doctor hospital nurse gp
    stitches stitch tetanus dressing nurse nhs walk-in centre clinic
    checked check conscious breathing breath awake faint dizzy vomit vomiting sick throwing
    collapsed collapse seizure stroke heart chest epipen inhaler insulin medicine dose
    cpr defib firefighter neighbour neighbor flat floor basement roof shaken shaking scared he she him
    her them they their there call calling rang ring
""".split())


# The weak half of that vocabulary: a pointer, not the incident. "should i call the plumber
# about the boiler" and "is there anything good on tv tonight" are ordinary lines that happen to
# carry one, so these words hold the thread only while the line brings no topic of its own.
# The injury itself, still going: "it's still stinging an hour later", "it's throbbing". A line
# that reports the damage needs the same thread even when some word of it reads as a topic of
# its own ("hour" is maths-and-numbers), so these are read before the line's own topic is.
CARE_HURTS = frozenset("""
    sting stings stinging stung throbs throbbing throbbed ache aches aching ached sore tender
    hurts hurting hurt pain painful swollen swelling bled blister blistered blisters
""".split())


CARE_POINTER = frozenset("""
    there call calling rang ring still wait waiting check checked out outside
""".split())


# "Out" is only a pointer when it is the speaker's own way out of the emergency ("am i out of
# danger", "should i go outside"). In "how do i get out of a parking ticket" the "out of" belongs
# to the ticket: it is a question about a thing, and reading it as a pointer answered a person in a
# heart-attack thread with "ring 999 or 911 now" about a parking fine (frank-shrew, #routing).
# The things you get out of *before* the emergency - a house that is filling with smoke, a car that
# has stopped in a live lane - are the way out and stay with the thread.
_POINTER_OWN_OBJECT = re.compile(
    r"\b(?:get|gets|getting|got|gotten|opt|opts|opting|opted|back|backs|backing|come|comes|"
    r"coming|came|pull|pulls|pulling|pulled|drop|drops|dropping|talk|talks|talking|talked|"
    r"sign|signs|signing|signed|wriggle\w*|wiggle\w*)\s+(?:me\s+|myself\s+)?out\s+of\s+"
    # "get out of it" / "get out of there" is the emergency itself, so a pronoun is left to the
    # pointer rule; "get out of this contract" names a thing and is not. A pronoun is the emergency
    # whatever follows it - "how do i get out of it fast" was read as an own object because "fast"
    # came after it - so only "this/that/there/here" need the end-of-line test, since a contract or
    # a hole follows those and a pronoun does not.
    r"(?!(?:it|them)\b)"
    r"(?!(?:this|that|these|those|there|here)\b\s*(?:$|[,.?!]))"
    r"(?!(?:(?:a|an|the|my|our|your|his|her|their)\s+)?(?:house|home|flat|building|block|"
    r"room|kitchen|bathroom|bedroom|bed|bath|car|van|vehicle|lift|elevator|water|door|way)\b)",
    re.I)


# The house words in that vocabulary are also the words of a household fault: "door", "window",
# "floor", "stairs", "flat", "roof". A fault said *of the house* is a DIY line, not the incident,
# so the burn thread must not answer "ok. also the oven door doesnt shut properly" with "keep an
# eye on it". Only the house thing as the subject of the fault counts: "the door is hot",
# "should i open the window" and "the smoke is coming under the door" are the incident, and
# "dont open the door" has the verb first, so none of them read as a fault (gray-palm, #routing).
HOUSE_FAULT = re.compile(
    r"\b(?:door|doors|window|windows|hob|oven|cooker|fridge|freezer|"
    r"washer|washing machine|dishwasher|boiler|radiator|tap|toilet|sink|cupboard|drawer|"
    r"handle|hinge|lock|seal|fan|element|shelf|stairs|stair|step|blind|shutter)\b"
    r"(?:\s+\S+){0,3}?\s+"
    r"(?:(?:doesnt|does not|dont|do not|wont|will not|isnt|is not|not)\s+"
    r"(?:shut|shuts|shutting|close|closes|closing|open|opens|opening|work|works|working|"
    r"fit|fits|fitting|lock|locks|locking|stay|stays|staying|sit|sits|properly|right)"
    r"|is\s+(?:broken|busted|jammed|stuck|loose|snapped|cracked|hanging)"
    r"|has\s+(?:snapped|come off|fallen off))"
    r"|\b(?:does|do)\s+(?:the|that|this|my|our)\s+(?:\w+\s+){0,2}"
    r"(?:door|window|hob|oven|cooker|fridge|freezer|tap|toilet|sink|cupboard|drawer|"
    r"handle|lock|shelf|stairs)\s+(?:shut|close|open|work|fit|lock)\b",
    re.I)


CARE_ASKS = re.compile(
    r"\b(what|where|who) (do|should|can) (i|we) (do|go|ring|call|use|tell)\b"
    r"|\bis (it|he|she|that) (safe|ok|okay|normal|bad)\b"
    r"|\bhow (do|can) i (help|stop|treat)\b")


STILL_HERE = re.compile(
    r"\b(?:can|could|do|did)\s+(?:you|u)\s+(?:hear|see|read|understand|get)\s+(?:me|this)\b"
    r"|\b(?:are|r)\s+(?:you|u)\s+(?:still\s+)?(?:there|here|with\s+me|listening|awake)\b"
    r"|\byou\s+(?:still\s+)?(?:there|listening)\b"
    r"|\banyone\s+there\b")


def _is_presence_check(clean):
    """True when the line is only "are you there / can you hear me", and nothing more."""
    match = STILL_HERE.search(clean)
    if not match:
        return False
    rest = re.findall(r"[a-z']+", clean[:match.start()] + " " + clean[match.end():])
    return len(rest) <= 2 and all(word in PRESENCE_LEFTOVER for word in rest)


# "can you remember what i told you at the start", "do you remember what my boiler is doing":
# the asking-in-front-of-it form of a recall. The store keeps the line and can answer it, so the
# capability card ("nothing from before this chat, sorry") is the wrong reply and stands down.
RECALL_TAIL = re.compile(
    r"\bwhat (?:i|we) (?:told|said|asked|mentioned|wanted|needed)\b"
    r"|\bat the (?:start|beginning|outset)\b"
    r"|\bearlier\b|\bso far\b|\bwhen we (?:started|began|were)\b"
    r"|\bhow (?:this|we|the chat|it) (?:started|began)\b"
    r"|\bwhat i (?:was|have been) (?:on about|talking about)\b")


def _the_store_takes_it(clean):
    """The card stands down only on a line the memory store will answer.

    Two regexes that drift are how one line loses both answers: a recall tail that stood the
    card down on its own sent "can you remember anything so far" and "do you remember what i
    said at the beginning of this chat" to a search hedge, which is a worse reply than the card
    that was there before. So the store is asked, not guessed at - it keeps `FIRST_ASK`, and a
    line it does not claim keeps the card.
    """
    from ..modules.memory_store import FIRST_ASK

    return FIRST_ASK.search(clean) is not None


# "what are you" is the identity question only when the line stops there. A verb after it makes
# the line about the verb - "what are you watching", "what are you doing", "what are you making
# for tea" - and the phrase list took all three, so a person asking what to watch tonight got a
# description of the bot (main 2a8d7caf, from #5085 claiming the `identity` kind). The narrower
# shapes above are unaffected: they name the human or the bot, which no verb does.
# "what are you good at", "what are you best at": the ask for what the bot can do, said about
# the bot. The feeling reader takes "good" as a mood word and answered it "No feelings like
# yours, so nothing to get worked up about", which is a reply to a question nobody asked.
GOOD_AT_ASK = re.compile(r"\bwhat are you\s+(?:good|best)\s+at\b")


# "what are you wearing", "what are you wearing to the wedding": a clothes question about a
# body, and the bot has none. The feeling reader takes "wearing" as a mood word ("worn
# down") and answered the clothes line "None of that in a program - no moods, no bad days".
CLOTHES_ASK = re.compile(r"\bwhat are you\s+(?:wearing|going to wear|putting on)\b")


# "what are you like": the idiom, and the same ask as "what sort of thing are you". The
# feeling reader answered it as a mood question, which it is not.
LIKE_ASK = re.compile(r"\bwhat are you\s+(?:like|like then|like as a (?:bot|program))\b")


# "what are you a robot", "what are you, a chatbot": the noun after the words names what it is,
# so the line is the self-description even without the comma or the small-talk tail.
WHAT_ARE_YOU_NOUN = re.compile(
    r"\bwhat are you\s*,?\s*(?:a\s+(?:bot|robot|ai|chatbot|person|human|program(?:me)?)\b)|"
    # "what are you made of", "what are you built from": what it is, not what it is doing.
    r"\bwhat are you\s+(?:made|built|running|based)\s+(?:of|from|on|out of)\b")


WHAT_ARE_YOU = re.compile(
    r"\bwhat are you\b"
    # the line stops there, or asks with a small-talk tail: "what are you then", "really". "up to"
    # is not in the list: "what are you up to" asks what the bot is doing, and the honest answer
    # ("nothing of my own - what are you up to?") is a better reply than the self-description.
    r"(?=\s*(?:[?.!,]|$|\b(?:then|exactly|really|anyway|actually|currently|"
    r"at\s+the\s+moment|these\s+days)\b))"
    # or it asks what the bot does something for: "what are you using my data for" is about the
    # bot's use of the data, not about a data plan, and it was the self-description before.
    r"|\bwhat are you\b[^.?!]{0,40}?\bfor\s*[?.!]*$")


# A verb after "what are you" takes the line away from the self-description only when something
# can answer it: "what are you watching" has a film pick, "what are you making for tea" has the
# dinner card, but "what are you reading", "what are you good at" and "what are you afraid of"
# have no answer of their own, and standing the identity card down on those turned a vague truth
# ("I'm a chatbot - here to help and chat") into a search hedge or a mood line that does not fit
# the question. So the knowledge base is asked, not guessed at, the same way `_the_store_takes_it`
# asks the memory store before standing the recall card down.
def _the_answers_take_it(clean):
    """Whether the knowledge module will answer this line itself.

    Read only in the identity check, so the cost is one answer on lines that start "what are
    you". It has to be the module's own answer and not a lookup hit: `what are you eating` and
    `what are you seeing` reach an entry (`city-next`) that then has nothing to say about them,
    so an entry found is not an answer given. The memory store is asked the same way in
    `_the_store_takes_it`: the module that owns the answer says whether it has one.
    """
    try:
        from ..modules import answers

        return answers.respond(clean, {}) is not None
    except Exception:
        return False


# The same question the other way round: "will you forget this chat", "are you going to forget
# me", "will you forget what i said". Every one of them was answered by a pool that knows nothing
# about this bot - "That's beyond what I know well, sorry. Searching for it will turn up better
# sources" - or, for "will you forget what i said", by the card about a person's own memory loss.
# What they are asking is whether the chat is kept, which the memory answer says exactly.
# ...and the same question in every other auxiliary a person uses, because "will you forget" was
# the only one read. "do you forget things" and "can you forget things" were answered with the card
# about a person's own memory loss ("Most forgetting is not a lost file"), "did you forget what i
# said" with the card about a blank mid-sentence, and "have you forgotten already" and "have you
# forgotten me" with a search hedge. The bot is the one being asked about, and the memory answer is
# the honest one.
#
# Two wh-words in front are the fence: "how do you forget someone" and "why do you forget things"
# are questions about forgetting itself, and they keep their own answers. "What do you forget"
# stays with the bot, because what it forgets is the start of the conversation.
FORGETTING_ASK = re.compile(
    r"(?<!how )(?<!why )(?<!when )"
    r"\b(?:will|would|won'?t|do|does|did|can|could|have|has)\s+(?:you|u)\s+"
    r"(?:ever\s+|just\s+|soon\s+|really\s+|still\s+|already\s+|now\s+|then\s+)?"
    r"(?:forget|forgot|forgotten)\b"
    # ...unless it is somebody's errand: "did you forget to ring the vet", "did you forget
    # the milk". What makes a forgetting question one for the bot is what it names - what i
    # said, me, things, already, our chat - so an infinitive or a bare definite noun after
    # the verb is the person's own list and not this answer.
    r"(?!\s+(?:to\s+\w+|(?:the|your|my|his|her|their|a|an)\s+\w))"
    r"|\b(?:are|r)\s+(?:you|u)\s+(?:already\s+)?(?:going|gonna)\s+to\s+forget\b"
    r"|\b(?:are|r)\s+(?:you|u)\s+(?:already\s+)?forgetting\b", re.I)


# A capability ask that names a topic ("what can you help me cook tonight") is not answered
# with a tour of every domain: the honest, useful reply stays inside the topic and asks for
# the next detail. The topic is the one the engine read, so this needs no per-line matching.
HELP_TOPIC_ASK = re.compile(
    r"\b(?:what|how) (?:can|could) you (?:help|do)\b|\bwhat do you do\b|"
    r"\bwhat are you good at\b")


# The same ask with a word in front of it: "what else can you do", "what more could you do",
# "anything else you can do". The understanding engine reads the bare phrase (and its fillers,
# "actually", "exactly"), but `else` is not a filler - dropping it would change every line with
# "else" in it - so the word in front of the ask hides the capability answer, and a shrug is the
# worst possible answer to the first question a person asks a bot. The verb has to be the bot
# offering something and a "you" has to be there, so "what else can i cook with mince" and
# "anything else you want to tell me" stay ordinary lines. "what else can you do about my
# leaking boiler" is the same shape, and it stays ordinary too: see HELP_TAIL below.
HELP_ELSE = re.compile(
    r"\b(?:what|which)\s+(?:else|other|more)\b[^.?]{0,25}?"
    r"\b(?:can|could|do|does)\s+you\s+(?:do|help|offer|manage|cover)\b([^.?]*)"
    r"|\b(?:anything|something)\s+else\b[^.?]{0,20}?\byou\s+(?:can|could)\s+"
    r"(?:do|help|offer)\b([^.?]*)")


def _free_tail(tail):
    """True when nothing but subject-free words follow the offer."""
    return all(word in HELP_TAIL for word in re.findall(r"[a-z']+", tail or ""))


# Tastes: STYLE.md lets the bot have opinions ("I'd pick the train"), so a question about what
# it likes gets one. Sending someone off to search for the bot's own preference is not a reply.
# A bare choice ("Tea or coffee?") is an opinion ask too: two things, no verb.
CHOICE = re.compile(r"^[a-z' ]{2,20} or (?:the )?[a-z' ]{2,20}\??$")


# "is that ok or am i overreacting" has the shape of a choice and is not one: it asks to be told
# whether a feeling is fair, and answering "either is fine" there dismisses the worry. The tell
# is a second question, which needs a helper verb and its subject ("am i", "is that", "do you").
# "should i text him or call" has no such tail and is a real choice; the helper in the first half
# does not disqualify it.
CHOICE_WORRY = re.compile(r"\b(?:am|is|are|was|were|do|does|did)\s+"
                          r"(?:i|you|we|they|he|she|it|there|that|this)\b")


# How people put a choice to someone else: the frame in front of the first thing is the question,
# not one of the two things. "Should we get a pizza or a curry tonight" is pizza against curry, so
# the frame comes off before the line is read as a choice - otherwise the first side is "should we
# get a pizza", which is what the pick used to say back ("I'd go *Should we get a pizza*"): a bot
# quoting its own question mark as one of the options. The article goes with it, because "a pizza"
# against "a curry" is still pizza against curry.
CHOICE_FRAME = re.compile(
    r"^(?:"
    r"(?:should|shall|do|can|could|would|will|might)\s+(?:i|we|you|u)\s+"
    r"(?:get|have|buy|go\s+for|pick|choose|take|do|order|book|eat|drink|watch)?\s*"
    r"|(?:i|we)\s+(?:could|might|would|will)\s+"
    r"(?:get|have|buy|go\s+for|pick|choose|take|do|order|book|eat|drink|watch)?\s*"
    r"|(?:how\s+about|what\s+about|maybe|perhaps|instead\s+of)\s+"
    r")")


CHOICE_ARTICLE = re.compile(r"^(?:the|a|an)\s+")


# A choice put to the bot as a joint decision: "should we get a pizza or a curry tonight",
# "would you get a kitten or an older cat". "should i" is not this frame - that is the person's
# own life, and it asks for advice rather than for the bot's taste.
JOINT_FRAME = re.compile(
    r"^(?:should|shall|do|can|could|would|will|might)\s+(?:we|you|u)\b")


def _choice_advice(clean):
    """`clean` with a joint question frame taken off, for the advice-word test."""
    return _unframed(clean) if JOINT_FRAME.match(str(clean or "").strip()) else clean


def _unframed(clean):
    """`clean` without the question frame in front of a choice, and without its article."""
    line = CHOICE_FRAME.sub("", str(clean or "").strip())
    line = CHOICE_ARTICLE.sub("", line.strip())
    return line.strip()


# A refusal in front of the pair is a constraint, not a question of which: "i dont want pasta or
# rice tonight" was answered "I dont want pasta. I'd take that and not think about it again" -
# the bot picking one of the two things the person had just turned down - and "not pizza or
# curry" was quoted back as an option ("If you were hoping I'd say 'not pizza'"). The person has
# ruled both out, so there is nothing to pick between; the refusal and the domain cards answer it.
CHOICE_REFUSED = re.compile(
    r"^\s*(?:no|not|never|without|neither)\b"
    r"|\b(?:dont|don'?t|do not|doesnt|doesn'?t|didnt|didn'?t|cant|can'?t|cannot|won'?t|"
    r"wouldnt|wouldn'?t|shouldnt|shouldn'?t)\s+(?:\w+\s+){0,2}?"
    r"(?:want|wants|like|likes|love|eat|eating|have|having|drink|wear|do|doing|need|use|"
    r"fancy|stand|bother|manage)\b"
    r"|\ballergic\b|\bhate\b|\bcant have\b")


def _refuses_the_pair(clean):
    """True when the line turns both things down instead of asking which to take."""
    head = str(clean or "").split(" or ")[0]
    return bool(CHOICE_REFUSED.search(head))


def _is_a_choice(clean):
    """True for a bare "x or y" that names two things, not a question with a clause in it."""
    # "early or late" is one scale about one thing, not two things to pick between: "is easter
    # early or late this year" has the shape of a choice and asks where the date falls, and
    # "toss a coin" is a shrug at a question the calendar answers. The pairs live in the reading
    # so this and the `choice` ask agree on what a choice is.
    asked = CHOICE.match(clean) or CHOICE.match(_unframed(clean))
    return (bool(asked) and not CHOICE_WORRY.search(clean)
            and not two_ends_of_one_scale(clean)
            and not _refuses_the_pair(clean))


# "Which would you pick?" is a different question from "cats or dogs?": the choice is on the
# table already, usually in the answer the bot has just given ("*Groundhog Day* for comedy,
# *Knives Out* for a clever whodunnit, or *Arrival* if you'd rather think"). A friend picks one
# and says what tilts it; the search hedge ("I'd rather not guess") and the self-check of the
# identity pool ("I'm a chatbot, not a person") both answer nothing at all. STYLE.md lets the bot
# have a taste ("I'd pick the train"), and the honest version of that taste is one of the options
# it has just offered, so it costs no fact.
PICK_ASK = re.compile(
    r"\b(?:what|which|who)\s+(?:would|will|should|shall|do|did)\s+(?:you|u|ya)\s+"
    r"(?:pick|choose|get|buy|take|go\s+for|suggest|recommend|prefer)\b"
    r"|\b(?:what|which)\s+(?:do|would)\s+(?:you|u|ya)\s+(?:suggest|recommend|pick|prefer)\b"
    r"|\bwhich\s+one\s+(?:would|do|should|will)?\s*(?:you|u|ya)\b"
    r"|\b(?:any|some|got\s+any)\s+(?:suggestions?|recommendations?)\s*\??$")


# The words a line can be made of and still be asking the bot's own pick: the ask, the person
# and the plumbing, and nothing else. A line with anything outside this set names something
# ("what would you get a 5 year old for christmas", "what would you suggest for my back") and
# keeps its own answer, because there is a fact to look up rather than a taste to give.
# "What would you do?" is the same ask as "which would you get?" once the bot has named the
# options: the person is handing the decision back. With nothing on the table it is a question
# about their situation ("my mum died last week", "my landlord won't fix the boiler"), and the
# pools that read that keep it, so it is only a pick when a choice was already answered.
PICK_BACK = re.compile(
    r"^(?:and\s+)?(?:what|which)(?:\s+one)?\s+(?:would|do|did|should|will)\s+(?:you|u|ya)\s+do"
    r"(?:\s+(?:then|now|yourself))?\s*\??$")


PICK_WORD = re.compile(r"[a-z0-9']+")


# The option itself, as the bot offered it (a title in italics), and what the bot said about it:
# "*Knives Out* for a clever whodunnit".
PICK_TITLE = re.compile(r"\*([^*\n]{1,70})\*")


PICK_NOTE = re.compile(r"\s*(?:for|if|when|with)\s+([^.;,*)!?]{2,60})")


# "Suggest" and "recommend" are the same words whether the person wants a taste or advice, so a
# line asking that way with nothing offered is left to the pools that know the difference.
PICK_ADVICE = re.compile(r"\b(?:suggest|suggestions?|recommend|recommendations?)\b")


# "What would you do" is not a request for a pick (that is `PICK_ASK`), but after a trade-off it
# is asking the bot to lean, which is a different question from "what should I do about my knee".
# "what do i do" is not here: it is the how-to ask ("my boiler wont light but it is freezing /
# what do i do"), and a heating fault in winter answered with a pick between two sides is a coin
# flip. The lean answers "what *would* you do", "which would you pick" and "help me decide".
LEAN_ASK = re.compile(r"\b(?:what|which)\s+(?:would|should)\s+(?:you|u|ya)\b"
                      r"|\bwhich one(?:\s+would\s+you\b)?"
                      r"|\bhelp me decide\b")


# A trade-off the person has put down in their own words: "one pays more but the people are nicer
# in the other". The side after the "but" is the side they are committing to - that is what "but"
# does in speech - so a bare "what would you do" or "which would you choose" after one is a
# question a friend can answer: they say which side they would take and why. The answer picks the
# second side by name, because the reading has already checked that the span it came from has two
# sides in it - it does not hand the person their own sentence back, which STYLE.md forbids.
TRADE_OFF = re.compile(r"\b([a-z0-9][^.!?;]{2,70}?)\s+but\s+([^.!?;]{2,70})", re.I)


# The side after the but is not a side when it is a report of how something went ("i tried that
# but it didnt work", "the cream helped but its still sore"): there is nothing there to lean on.
NOT_A_SIDE = re.compile(r"\b(?:didnt|doesnt|don|did not|does not|no|not|never|nothing|still|"
                        r"stopped|failed|worse|hurts|hurting|sore|tried|again)\b", re.I)


# A side that is a verdict on the thing ("the job pays well but i hate it", "the flat is lovely
# but the neighbours are awful") is not a side to take: leaning on it tells a person to take the
# neighbours who are awful. A missed lean is a punt; a wrong lean is worse than main.
NOT_A_CHOICE = re.compile(r"\b(?:hate[sd]?|awful|terrible|horrible|dreadful|miserable|toxic|rude|"
                          r"nasty|worst|unbearable|disgusting|useless|pointless|exhausting|"
                          r"can'?t\s+stand|cant\s+stand|sick\s+of|fed\s+up|driving\s+me\s+mad)\b",
                          re.I)


# The side after the but, as the thing to pick rather than as a sentence about it: "the other has
# better brakes" is "the one with better brakes", "further from work" is "the one further from
# work", "the people are nicer in the other" is "the one where the people are nicer". A side that
# fits none of those shapes is not named, and nothing leans (see `_a_named_side`).
SIDE_HAS = re.compile(r"^(?:has|have|had)\s+(.+)$", re.I)


SIDE_IS = re.compile(r"^(?:it\s+is|it's|its|it\s+was|they\s+are|they're|she\s+is|he\s+is|"
                     r"that\s+is|that\s+are|that\s+was|that\s+were)\s+(.+)$", re.I)


SIDE_SUBJECT = re.compile(r"^(?:the|a|an|my|his|her|their|our|that|this|she|he|they|we|there)\b",
                          re.I)


SIDE_VERB = re.compile(r"\b(?:is|are|was|were|pays|costs|takes|gives|lasts|has|have|means|"
                       r"feels|sounds)\b", re.I)


# Whether the side after the but is the one worth wanting. "one is cheaper but the other has
# better brakes" is a plus after the but; "i like the office but the commute is grim" is a
# complaint, and naming it as the pick says to take the commute. So a side that reads as bad and
# not also as good is not named, and the line keeps the punt it had.
SIDE_GOOD = re.compile(r"\b(?:nicer|better|friendlier|closer|cheaper|bigger|quieter|cleaner|"
                       r"brighter|warmer|safer|newer|faster|kinder|easier|lighter|shorter|"
                       r"flexible|lovely|great|good|perfect|ideal|pays|earns|more\s+\w+)\b", re.I)


SIDE_BAD = re.compile(r"\b(?:grim|bad|worse|worst|less|fewer|painful|boring|stressful|noisy|"
                      r"dirty|loud|busy|cramped|old|small|tiny|dangerous|risky|annoying|"
                      r"exhausting|unpaid|long|longer|slow|further|farther|expensive|price|prices|"
                      r"priced|cost|costs|fee|fees|high|dear|commute)\b", re.I)


SIDE_ONE = re.compile(r"^((?:the|my|this|that|her|his|their)\s+\w+\s+one)\b\s*(.*)$", re.I)


SIDE_COPULA = re.compile(r"\b(?:is|are|was|were|isn't|aren't)\b", re.I)


SIDE_TAIL = re.compile(r"\s+(?:in|of|out\s+of)\s+(?:the\s+)?other(?:\s+one)?$", re.I)


SIDE_OTHER = re.compile(r"^(?:the\s+)?other(?:\s+one)?\s+", re.I)


# "i want to quit but i need the money" is not two options: it is a want and the thing in the
# way, and the side after the but there is the obstacle, so leaning on it tells a person who wants
# to leave their job to stay in it. Two things they could choose is the shape that can be leaned
# on, so a want on the near side or a cost on the far side stands the reading down.
DESIRE = re.compile(r"\b(?:i|we)\s+(?:really |just |so )?(?:want|wanna|would love|id love|need|"
                    r"wish|hope|keep wanting|have to)\b", re.I)


OBSTACLE = re.compile(r"\b(?:too|afford|rent|money|cost|time|hours|nervous|scared|worried|"
                      r"anxious|hard|tight|far|means|landlord|feel bad|guilt|awkward|risk)\b",
                      re.I)


# A trade-off about a body, a feeling or somebody in care is not one to take a side on: "my back is
# killing me but i cant take time off work" / "what would you do" is a question about the pain, and
# answering "I'd take the half after the but" tells a person with a bad back to keep working.
# Read as words anywhere in the line, because the trade-off is the whole of it, not the span.
LEAN_NOT = re.compile(r"\b(?:sad|low|down|depress\w*|unhappy|miserable|lonely|crying|cry|"
                      r"grief|dying|died|death|funeral|diagnos\w*|cancer|checkup|"
                      r"worried|worry|worries|anxious|scared|afraid|panic\w*)\b", re.I)


# How a person types a choice: the helper verb in front of one side is not part of the thing
# ("should i text him" is "text him"), and a trailing "then" or "instead" is the person still
# thinking aloud rather than a third option.
CHOICE_SIDE_LEAD = re.compile(r"^(?:(?:should|shall|do|can|could|would|will|might|maybe)\s+i\s+)")


CHOICE_SIDE_TAIL = re.compile(r"\s+(?:then|instead|though|really)$")


# "chinese or indian tonight" names a dinner and a night, not "indian tonight": the pick is the
# thing, so a time word hanging off the end of a side comes off with the rest of the thinking out
# loud. "with dinner" stays - "beer with dinner" is the whole option.
CHOICE_SIDE_WHEN = re.compile(
    r"\s+(?:tonight|today|tomorrow|now|instead|this\s+(?:evening|afternoon|morning|weekend|week))$")


# "his side or mine", "my side or theirs": the same two people without a word this list has.
CHOICE_PERSON_SIDE = re.compile(
    r"\b(?:my|his|her|their|our|your)\s+side\b|\b(?:his|her|their)\s+(?:family|mum|dad|parents)\b")


# Two steps of one job are not two things to choose between: "mop first or hoover first", "dust
# the shelves or hoover first", "fold the washing or hang it out first", "wipe the sides before
# or after the floor". The light-choice pool took a side on all four because the shape is the
# same shape as "pizza or curry", and the side it took was a claim about the work rather than a
# taste: "Mop first" undoes the hoovering, and "Fold the washing" folds washing that has not been
# hung out. The bot has no taste about the order a job is done in, so it does not pick; it says
# the rule that decides it, which holds for nearly every pair of steps - the one that would spoil
# the other has to come last - and lets the person apply it to their own job.
ORDER_SIDE_END = re.compile(r"\b(?:first|last)$", re.I)


ORDER_BEFORE_AFTER = re.compile(r"\b(?:before|after)\s+or\s+(?:before|after)\b", re.I)


ORDER_OF_WORK = (
    "The step that would spoil the other one goes last, so nothing gets done twice. What are you "
    "doing it on?",
    "Work it out rather than guess: whatever makes a mess for the other step to clear up goes "
    "first. Which job is it?",
    "That is an order to work out, not a taste to pick: the messy step before the tidy one, and "
    "dry before wet. What are you doing?",
)


ORDER_WORD_TAIL = re.compile(r"\s*\b(?:first|last)\b\s*$", re.I)


ORDER_WORD_LEAD = re.compile(r"^\s*\b(?:before|after)\b\s*", re.I)


# "first or second gear" and "my first or my second" name two positions, not two steps of a job:
# a side with nothing left in it once the order word is gone is not a step.
ORDER_ONLY = frozenset("""first second third fourth fifth last later earlier next middle
    start end beginning one""".split())


def _an_order_of_work(sides, clean):
    """True when the two options are the steps of one job rather than two things to pick from.

    Read on the ends of the sides, so "tea or coffee first thing" (a time, not an order) is left
    alone, and on the "before or after" pair, which names the order without ever saying "first".
    """
    if ORDER_BEFORE_AFTER.search(str(clean or "")):
        return True
    if not any(ORDER_SIDE_END.search(side) for side in sides or ()):
        return False
    for side in sides:
        core = ORDER_WORD_TAIL.sub("", ORDER_WORD_LEAD.sub("", side)).strip()
        core = CHOICE_ARTICLE.sub("", core).strip()
        if core in ORDER_ONLY or len(core) < 2:
            return False
    return True


def _choice_sides(clean):
    """The two things a bare choice names, as the person typed them, or None.

    Only the shape `CHOICE` already matched comes here, so the two halves are short and there is
    one "or" between them. Each side loses the helper verb in front of it ("should i text him") and
    a trailing "then"/"instead", and one side with nothing in it leaves None: a pick needs two
    things to pick between.
    """
    parts = _unframed(clean).rstrip("?").split(" or ")
    if len(parts) != 2:
        return None
    sides = []
    for part in parts:
        side = CHOICE_SIDE_TAIL.sub("", CHOICE_SIDE_LEAD.sub("", part.strip()))
        side = CHOICE_SIDE_WHEN.sub("", side.strip())
        side = CHOICE_ARTICLE.sub("", side.strip()).strip()
        if not side or not re.search(r"[a-z]", side):
            return None
        sides.append(side)
    return sides


def _capital(side):
    """`side` with its first letter as a capital, which is how a name or an option starts."""
    side = " ".join(str(side or "").split())
    return side[0].upper() + side[1:] if side else side


def _named(side, memory=None):
    """`side` with any name in it spelled the way the person spelled it."""
    understood = (memory or {}).get("understood") or {}
    for entity in understood.get("entities") or ():
        if not isinstance(entity, dict) or entity.get("type") not in NAMED_TYPES:
            continue
        name = str(entity.get("text") or "").strip()
        if len(name) < 2 or name.lower() not in side:
            continue
        side = re.sub(r"\b" + re.escape(name.lower()) + r"\b", name, side)
    return side


def _a_pick(sides, clean, memory=None):
    """One side of the choice, said as a reply, and the other one quoted beside it.

    Which side is decided the way the wording is - from the line itself - so a line always gets
    the same pick and two different lines do not all lean the same way. The understanding engine
    has already found the names in the line ("manchester" is a place, not a word), so they go back
    to the spelling the person used before the side opens the sentence.
    """
    first, second = sides
    seed = sum(ord(letter) for letter in clean)
    take, other = (first, second) if random.Random(seed).getrandbits(1) else (second, first)
    return _capital(_named(take, memory)), _named(other, memory)


def _between_people(sides, clean):
    """True when the two things are two people rather than two things.

    Read on the sides, not on the whole line: a pick between people is a verdict on them, and
    "my mum or my dad for christmas" in the words for a crisp flavour is the worst reply here.
    `CHOICE_PERSON_SIDE` catches the same two people said as sides ("his side or mine").
    """
    for side in sides or ():
        if set(side.split()) & CHOICE_PEOPLE:
            return True
    return bool(CHOICE_PERSON_SIDE.search(str(clean or "")))


def _choice_light(clean, memory=None):
    """The pool for a light choice: a side when the line names two things, the quieter lines when
    it does not (a line with one side missing is not a pick anybody can make)."""
    sides = _choice_sides(clean)
    if sides is None:
        return CHOICE_LIGHT
    if _between_people(sides, clean):
        return CHOICE_BETWEEN_PEOPLE
    take, other = _a_pick(sides, clean, memory)
    return [line.format(pick=take, other=other) for line in CHOICE_LIGHT_PICK]


def _choice_pool(clean, memory=None):
    """A bare "x or y" is a light choice unless the line names something at stake: a medicine
    (ask a pharmacist), or money, a repair, a commitment (name what decides it)."""
    words = set(clean.split())
    if words & CHOICE_HEALTH:
        if words & CHOICE_THERAPY:
            # "therapy or medication" is not a pharmacy question: only one side is a medicine,
            # and a pharmacist cannot say whether talking therapy suits. Leave it to them.
            return CHOICE_WEIGH
        return CHOICE_PHARMACIST
    if _an_order_of_work(_choice_sides(clean), clean):
        # Before the stakes: "should i repair the boiler first or the radiator" is an order too,
        # and "whichever you would regret less" answers a question about cost, not about order.
        return ORDER_OF_WORK
    if words & CHOICE_STAKES:
        return CHOICE_WEIGH
    return _choice_light(clean, memory)
