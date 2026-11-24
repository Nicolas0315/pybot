"""Part 3 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from . import lexicon
from .kinds_part_02 import (
    CUE_FOLLOW, PHRASE_OPENERS, STATE_NOUNS, _a_verb_holds_it, _clause_follows, _state_before,
    _verb_after, FEELING_FILLER, SPEAKER_TAIL, OBJECT_MARKERS, TAIL_STOPS, TIME_MARKERS,
    STATE_JOINERS, VERB_ONLY_STATE, _a_copula_before, FEELING_NOT_MOOD, STATE_AS_FEELING,
    _copula_just_before, FEELING_SOUND_FRAME, _a_feeling_can_end_here, feeling_by_sound, CAPABILITY,
    CAPABILITY_CARRIER, CAPABILITY_FILLER, _works_on_the_speaker,
)


def cue_about_person(text, cue):
    """True when this feeling word says how someone feels, not what something was like.

    The word is found whole ("mad" is not in "made"), and it counts when it ends a clause or
    is followed by a preposition, a connective or a time word: "im mad", "she was cross with
    me", "driving me mad", "mad at my sister", "im mad now". It does not count when it comes
    straight before another word: "a mad day", "mad busy", "a sad film", "happy birthday".
    """
    if cue in PARTICLE_STATES:
        for found in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
            if _a_direction(text, found.start()):
                return False      # "im going down the pub" is a place, not a low
    if cue.split()[-1] in CUE_FOLLOW:
        # The cue ends on a preposition or a connective ("feel awful about", "no one to
        # talk to"): it already reads as how someone feels, so what follows adds nothing.
        return bool(re.search(r"\b" + re.escape(cue) + r"\b", text))
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
        if _a_verb_holds_it(text, match.start()):
            # "im moving flat on saturday" is a move to a flat, not a low mood: the verb in
            # front of the word takes it as its object, so the word is a thing here.
            continue
        rest = text[match.end():].lstrip()
        if not rest or rest[0] in ".,!?;:-|":
            return True
        following = rest.split()[0].strip(".,!?;:-|")
        if not following or following.lower() in CUE_FOLLOW:
            return True
        if following[:1].isupper() and following.lower() not in lexicon.COMMON:
            # A name after the feeling is the person being spoken to: "im mad Jess".
            return True
        if following.lower() in STATE_NOUNS and _state_before(text, match.start()):
            # "im in a mad mood" is the speaker's own state; "we went to a mad place" is a place.
            return True
        if following.lower() in PHRASE_OPENERS and _clause_follows(rest):
            # "im mad the dog ate the sausages" is a feeling and a clause; "a mad day at work"
            # is a phrase about the day, with no verb in it.
            return True
        if _speaker_before(text, match.start()) and _verb_after(rest):
            # A person is not a description. "im gutted mum cancelled" opens on a noun that is
            # nobody's phrase opener, so the words after it are read instead: a verb there is a
            # clause about the person's feeling, and "im mad busy today" has none.
            return True
    return False


def _speaker_before(text, at):
    """True when the words in front of a feeling word make it the speaker's own state.

    "i am gutted", "i was scared", "i feel low", with a degree word allowed in between
    ("im so gutted"). It says nothing about "i have a mad idea" or "we had a mad time".

    The words are read as typed, so the short forms are spelled out first: people write "im"
    far more often than "i am", and "im gutted mum cancelled" is the same feeling as "i am
    gutted my mum cancelled".
    """
    words = [word.strip(".,!?;:-|\"'").lower() for word in text[:at].split()]
    while words and words[-1] in FEELING_FILLER:
        words.pop()
    tail = " ".join(words[-5:])
    tail = re.sub(r"\bi'?m\b", "i am", tail)
    tail = re.sub(r"\bi'?ve\b", "i have", tail)
    if SPEAKER_TAIL.search(tail):
        return True
    # "my mood is low", "my energy is low", "my anxiety is bad": the speaker's own mood,
    # energy or nerves, named as a thing. Any other thing is still a thing ("my back is sore").
    recent = words[-4:]
    if "my" in recent:
        for word in recent[recent.index("my") + 1:]:
            if word in MOOD_NOUNS:
                return True
    return False


def _takes_an_object(text, end):
    """True when what follows a state cue turns it into an action with an object."""
    words = [word.strip(".,!?;:-|\"'").lower() for word in text[end:].split()]
    for pos, word in enumerate(words):
        if not word or word in TAIL_STOPS:
            return False
        if word in OBJECT_MARKERS:
            after = words[pos + 1:pos + 2]
            if word in TIME_MARKERS and after and after[0] in TIME_FILLERS:
                return False       # "i feel low this week": the week is when, not an object
            return True
    return False


def _object_after(text, cue):
    """True when any place this cue occurs in the line is followed by an object."""
    return any(_takes_an_object(text, match.end())
               for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text))


def _state_of_a_person(text, cue):
    """True when a person is what the feeling word is said of: "im low", "they were shattered".

    The word before the cue is the subject, skipping the joiners, so a thing is still a thing:
    "the battery is low", "the windscreen is shattered", "work has been awful lately".
    """
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
        if cue in SUPPLY_WORDS and _about_a_supply(text, match.end()):
            continue                       # "im low on milk": a shortage, not a mood
        if cue in VERB_ONLY_STATE and not _a_copula_before(text, match.start()):
            continue                       # "the dog pooped on the carpet": the pet's verb
        if _takes_an_object(text, match.end()):
            continue
        words = [word.strip(".,!?;:-|\"'").lower() for word in text[:match.start()].split()]
        while words and (words[-1] in STATE_JOINERS or words[-1] in FEELING_FILLER):
            words.pop()
        if not words:
            return True                    # "feeling low today": no noun, so the speaker
        subject = words[-1]
        if subject in PERSON_SUBJECT or subject in OTHER_PEOPLE:
            return True
        if subject in MOOD_NOUNS and "my" in words[:-1][-3:]:
            return True                    # "my mood is low", "my energy is low"
        if _speaker_before(text, match.start()):
            return True                    # "i feel low", "we were shattered"
        return False
    return False


def _said_of_the_speaker(text, cue):
    """True when this cue comes straight after a self cue: "im empty", "i feel out of sorts".

    A word that is also an ordinary word for a thing needs it: "the flat is cold" and "an empty
    shelf" name a thing's state, and "a blank page" a page's.
    """
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
        if _speaker_before(text, match.start()):
            return True
    return False


def _state_as_feeling(text):
    """True when a state word of the list above is the speaker's mood in this line."""
    words = [word.strip(".,!?;:-|\"'") for word in text.lower().split()]
    for pos, word in enumerate(words):
        if word not in STATE_AS_FEELING:
            continue
        if _thing_turned_down(words, pos):
            continue                       # "turn the heat down", "keep it down"
        if not _copula_just_before(words, pos):
            continue                       # "a down sleeping bag", "coming down with a cold"
        if _particle_is_a_place(words, pos):
            continue                       # "im going down the pub", "down the stairs"
        after = words[pos + 1] if pos + 1 < len(words) else ""
        if after in FEELING_NOT_MOOD:
            continue                       # "im down for that", "im terrible at maths"
        if _whose_state(words, pos) in ("self", "other"):
            return True                    # "im down", "she is really down", "my dog seems down"
    return False


def _feeling_said_as_a_sound(text):
    """The feeling a word straight after "im" is the sound of, or None."""
    for match in FEELING_SOUND_FRAME.finditer(text):
        if _takes_an_object(text, match.end()):
            continue    # "im cross the road" is crossing it, and a word is not a mood there
        if not _a_feeling_can_end_here(text, match.end()):
            continue    # "im board certified" is a board
        name = feeling_by_sound(match.group(1))
        if name:
            return name
    return None


# "couldnt be better", "never been better", "i couldnt have been better": a negated copula in
# front of a comparative is the highest praise, not a good word that has gone missing. The
# missing frame is about a state the person has not had ("i cant remember the last time i felt
# happy", "i havent been happy in weeks"), and a comparative cannot be missing: it compares two
# times, and "better" says the later one is good. Read as the missing frame, every "couldnt be
# better" was answered with the condolence - the fault this rule set out to fix, upside down.
GOOD_WORD_BY_COMPARISON = re.compile(r"\b(?:better|best)\b", re.I)


# A demonstrative after a preposition stands for the thing already in play: "what do you do
# about that", "what can you do for it", "what do you do with these" are all about the thing and
# not about the bot. The carrier set below holds "about", "that" and "it" as words that carry no
# subject of their own, which is right for "what can you help with" and wrong the moment the two
# come together, because then the thing being pointed at is the subject.
REFERRING = frozenset("about for with to in on".split())


POINTED_AT = frozenset("this that these those it them".split())


def _capability_question(norm):
    """True for "what can you do?" and "what can you help with?"; False when the phrase is
    followed by something the person wants done ("with leftover rice", "me cook tonight") or
    points back at the thing in play ("about that", "for it")."""
    compact = [word for word in norm if word not in CAPABILITY_FILLER]
    for phrase in CAPABILITY:
        wanted = phrase.split()
        for start in range(len(compact) - len(wanted) + 1):
            if compact[start:start + len(wanted)] != wanted:
                continue
            tail = compact[start + len(wanted):]
            rest = [word for word in tail if word not in CAPABILITY_CARRIER]
            if rest:
                return False
            if any(word in REFERRING and i + 1 < len(tail) and tail[i + 1] in POINTED_AT
                   for i, word in enumerate(tail)):
                return False
            return True
    return False


# Questions about how the bot sees the person, rather than about a thing the person names:
# "do you like me", "what do you think of me", "are we friends". Read as ordinary questions they
# were answered as an opinion about something ("I'm easy on it - it's not a hill I'd argue from")
# or with the knowledge shrug. "do you like pizza" names something else and is left alone.
ME_ASKS = ("what do you think of me", "what do you think about me", "what do you reckon of me",
           "what do you make of me", "do you like me", "do you love me", "do you care about me",
           "are you my friend", "are we friends", "am i your friend", "do you miss me",
           "would you miss me", "will you miss me", "do you hate me", "am i annoying you",
           "do you think about me", "do you think of me", "do you ever think about me",
           "are you annoyed with me", "do you like talking to me", "do you enjoy talking to me",
           "do you like chatting to me", "do you like me talking to you")


# What people put after the ask and still leave it the ask: a tag of time ("what do you think of
# me so far"), of honesty ("... tbh") or of uncertainty ("... though"). A tag is not a new
# subject, so the phrase is still the whole question - "what do you think of me so far" was
# answered with the search shrug while "what do you think of me" had its own reply.
ME_TAIL = ("then", "though", "tho", "now", "honestly", "really", "lol", "haha",
           "tbh", "tbf", "ngl", "anyway", "still",
           # "so far", "at all": the two-word tags people end the ask with. Both words are
           # peeled from the end, so the ask underneath them is read as the whole question.
           "far", "so", "all", "at")


ME_LEAD = ("so", "ok", "okay", "oh", "yeah", "but", "well", "and", "honestly")


def _asks_how_the_bot_sees_me(norm):
    """True when the whole line asks the bot what it makes of the person.

    A tag of honesty is not a new subject: "what do you think of me tbh" is the same ask, and
    the chat-speak repair turns that tag into the words "to be honest" before this reads the
    line, so the softening phrases people end a feeling with are peeled off first. The same
    repair can also turn the "me" before the tag into "my" ("what do you think of me tbh" reads
    as "what do you think of my to be honest"), which is why the pronoun is read back: the ask
    is the ask, and the word in front of a tag is not a noun for the repair to fix.
    """
    words = list(norm)
    changed = True
    while changed and words:
        changed = False
        for phrase in MOOD_TAIL:
            size = len(phrase.split())
            if size < len(words) and words[-size:] == phrase.split():
                del words[-size:]
                changed = True
        while words and words[0] in ME_LEAD:
            words.pop(0)
            changed = True
        while words and words[-1] in ME_TAIL:
            words.pop()
            changed = True
    ask = words[:-1] + ["me"] if words and words[-1] == "my" else words
    return " ".join(words) in ME_ASKS or " ".join(ask) in ME_ASKS


# A line can ask who it is talking to without saying "you": "who is this" and "who am i
# talking to" are the plainest ways to ask the bot what it is, and both were read as naming
# nothing, so they got the search shrug. The ask is about the addressee only when the whole
# line is the ask, which is what these two shapes are; "who is it" is left out because that is
# as often a knock at the door, and "who is that" a third person in a story.
WHO_TALKING = frozenset("""talk talking speak speaking chat chatting message messaging
    text texting""".split())


WHO_A_THING = frozenset("""bot robot chatbot ai machine computer program human person""".split())


# The word a person adds to the end of the ask without changing it: "who did i just talk to
# then", "who am i talking to anyway". It is stripped before the shape is matched, so the
# same ask with a question tag on it is the same ask.
WHO_TAIL = frozenset("then please pls anyway again".split())


def _asks_who_this_is(norm):
    """True for the whole-line ask about who the person is talking to."""
    words = tuple(norm)
    while words and words[-1] in WHO_TAIL:
        words = words[:-1]
    if words in (("who", "is", "this"), ("who", "am", "i", "talking", "to"),
                 ("who", "am", "i", "speaking", "to"), ("who", "am", "i", "speaking", "with"),
                 ("who", "am", "i", "chatting", "to"), ("who", "am", "i", "chatting", "with"),
                 ("who", "am", "i", "talking", "with"), ("who", "was", "i", "talking", "to"),
                 ("who", "was", "i", "speaking", "to"), ("who", "was", "i", "speaking", "with")):
        return True
    if words[:4] == ("who", "have", "i", "been") and len(words) in (6, 7):
        return words[4] in WHO_TALKING and words[5] in ("to", "with")
    if words[:3] in (("who", "did", "i"), ("who", "was", "i"), ("who", "am", "i")) \
            and len(words) in (5, 6):
        if len(words) == 6 and words[3] != "just":
            return False
        at = 1 if len(words) == 6 else 0
        return words[3 + at] in WHO_TALKING and words[4 + at] in ("to", "with")
    if words[:3] in (("am", "i", "talking"), ("am", "i", "speaking"), ("am", "i", "chatting")):
        if len(words) == 5 and words[3] in ("to", "with"):
            return words[4] in WHO_A_THING or words[4] in ("a", "an")
        if len(words) == 6 and words[3] in ("to", "with") and words[4] in ("a", "an"):
            return words[5] in WHO_A_THING
    if words[:2] in (("is", "this"), ("is", "it")) and len(words) in (3, 4, 5):
        rest = words[2:]
        if rest and rest[0] in ("a", "an"):
            rest = rest[1:]
        if rest and rest[0] == "real":
            rest = rest[1:]
        return bool(rest) and all(word in WHO_A_THING for word in rest)
    return False


# "where are you" and "where do you live" ask where the bot is, which is its own answer ("nowhere
# you could visit") rather than the one that says what it is. The tail is only the words a person
# adds to the ask itself; a real place after it ("where are you going on holiday") is their own
# subject and keeps its answer.
WHERE_BOT_TAIL = frozenset("""from based located at out of exactly then now though really actually
    please pls mate live living staying originally today currently""".split())


def _asks_where_the_bot_is(norm):
    """True for the whole-line ask about where the bot is."""
    words = tuple(norm)
    if not words or words[0] not in ("where", "whereabouts"):
        return False
    rest = words[1:]
    if rest[:2] == ("are", "you"):
        rest = rest[2:]
    elif rest[:2] == ("do", "you") and rest[2:3] == ("live",):
        rest = rest[3:]
    elif rest[:2] == ("you", "live"):
        rest = rest[2:]
    else:
        return False
    return all(word in WHERE_BOT_TAIL for word in rest)


# "how do i answer tell me about yourself", "what do i say when they ask what are you doing at
# the moment": the question in the line is somebody else's - an interviewer's - and the person
# wants the answer to give them, not the bot's own. The words ask about the bot only as a
# quotation, so every about-the-bot kind stands down and the knowledge base answers the line.
# The frame needs an ask about answering (answer, say, reply, respond); "how do i get you to
# listen" and "what do you say to that" are not it.
ANSWERING_A_QUOTED_ASK = re.compile(
    r"\b(?:how\s+(?:do|should|would|can|might|to)\s*(?:i|you|we)?|how\s+to|"
    r"what\s+(?:do|should)\s*(?:i|you|we)?)\s*[^.?!]{0,20}?"
    r"\b(?:answer|say|reply|respond)\b[^.?!]{0,40}?"
    r"\b(?:what|who|where|why|how|when|tell\s+me|do\s+you|are\s+you|can\s+you|your)\b",
    re.IGNORECASE)


# "how long can we talk for", "is there a limit to how long we can talk", "have you got all
# day", "how many messages can i send you". How long this conversation can run, and whether the
# person is keeping the bot too long. Nothing about the bot is on the web to look up, so the
# search hedge answered the question with the wrong advice, and the message template answered
# "how many messages can i send you" with three lines to write to somebody else.
# Every shape below names this conversation - talk, chat, keep going, all day - or asks the bot
# for its time, so a question about the person's own time keeps its own answer: "how long can i
# keep it in the fridge", "how long have i got to send this form" and "how many messages should
# i send my landlord" are not this. Each shape is read on the whole line, never on one word.
WHILE_ASK = re.compile(
    r"\bhow\s+long\s+(?:can|could|may|might|will|would|do|does)\s+(?:we|i|you|u|this)\s+"
    # The verbs of talking, and only those: "how long can i last without food" and "how long will
    # this last" name a thing of their own and are nobody's question about the chat.
    r"(?:[a-z]+\s+){0,2}?(?:talk|chat|keep\s+(?:going|talking|chatting)|carry\s+on|go\s+on)\b"
    # The bot's own time, and only that: "how long have you got" is the ask, while "how long
    # have you got to pay the bill" is about the bill and keeps its own answer.
    r"|\bhow\s+long\s+(?:have|has|do|does|did)\s+(?:you|u)\s+(?:got|have)\b"
    # "left" has to end the line: "how long have you got left" is the ask, while "how long have
    # you got left on the parking" is about the parking and keeps its own answer.
    # "for" has to be followed by the person or the moment, so "how long have you got for lunch
    # today" stays the lunch question it is.
    r"(?=\s*(?:$|[.!?]|for\s+(?:you|me|us|now|today)\b|on\s+you\b|today\b|now\b|then\b"
    r"|and\b|so\b|to\s+(?:talk|chat|keep\s+going|carry\s+on|go\s+on)\b)"
    r"|\s+left\s*[.!?]?$)"
    r"|\bhow\s+long\s+(?:are|will)\s+(?:you|u)\s+(?:be\s+)?(?:here|around|on)\b"
    r"|\bhave\s+(?:you|u)\s+got\s+(?:all\s+day|time|much\s+time)\b"
    # "we", not "i": "should i keep going" is the person's own activity - a run, a course, a row
    # - and "do you mind if i keep going" is said to the bot about the conversation.
    r"|\b(?:can|could|shall|should|may)\s+we\s+keep\s+(?:talking|going|chatting|on)\b"
    r"|\bdo\s+(?:you|u)\s+mind\s+if\s+i\s+(?:keep|carry|ramble)\b"
    r"|\bhow\s+much\s+time\s+(?:have|has|do)\s+(?:you|u|we)\s+(?:got|have)\b"
    r"|\bhow\s+many\s+(?:messages?|questions?|things)\s+can\s+i\s+(?:send|ask|give)\b"
    r"|\blimit\s+(?:on|to)\s+how\s+long\b[\s\S]{0,24}?\b(?:talk|chat|go\s+on|carry\s+on|"
    r"keep\s+going)\b")


# "am i boring you", "am i keeping you up", "do you want me to stop", "am i talking too much",
# "am i rambling", "do you mind me going on". The person is checking whether they are being a
# nuisance, which is a question about this conversation and only the bot can answer it. The
# search hedge answered eleven of these ("a quick search online will get you a solid answer"),
# the identity card answered "are you bored of me", and "am i boring you" was told to try a
# jigsaw - none of them answers the question somebody asked. Every shape here has the person or
# the talk as its subject and is in the present tense, so a line about a thing being dull ("the
# film was boring", "my job is boring") is not this.
KEEPING_ASK = re.compile(
    r"\bam i\s+(?:boring\s+(?:you|u)\b|keeping\s+(?:you|u)\b|a\s+bore\b|boring\b"
    r"|(?:talking|talk|going\s+on|rambling|wittering|waffling|droning)\s+too\s+much\b"
    # "going on" has to be the end of the line, or carry a qualifier of its own: "am i going on a
    # diet", "am i going on holiday" and "am i going on the bus" are plans, not the talk.
    r"|going\s+on(?:\s+(?:a\s+bit|and\s+on|too\s+long|like\s+this))?(?:\s*[.!?]\s*$|\s*$)"
    r"|rambling\b|wittering\b"
    r"|waffling\b|droning\s+on\b|wasting\s+(?:your|ur)\s+time\b)"
    r"|\bis\s+(?:this|it)\s+(?:boring\s+(?:you|u)\b|boring\b|dull\b|too\s+much\s+detail\b"
    r"|going\s+on\s+a\s+bit\b)"
    r"|\bdo i\s+(?:talk|go\s+on|ramble|witter|waffle)\s+too\s+much\b"
    r"|\bare (?:you|u)\s+(?:bored\s+(?:of|with)\s+(?:me|us|this|it)\b"
    r"|sick\s+of\s+me\b|fed\s+up\s+(?:of|with)\s+me\b|had\s+enough\s+of\s+me\b)"
    r"|\bdo you\s+mind\s+(?:me|my)\s+(?:going\s+on|talking|rambling|wittering)\b"
    r"|\b(?:am i|are we|was i)\s+wasting\s+(?:your|ur)\s+time\b")


# "do you want me to stop", "shall i go": the same question as above, but only when the stop is
# the whole of the line. "where should i go", "how often should i go", "should i stop for a bit"
# and "the oil light came on while i was driving, should i stop" are about the person's evening,
# their gym or their car, and "shall i stop taking the tablets" has a card of its own - every one
# of them would be answered "Not at all, carry on" by a search on the words alone.
STOP_ASK = re.compile(
    r"(?:(?:do|would)\s+(?:you|u)\s+want\s+me\s+to"
    r"|(?:do|would)\s+(?:you|u)\s+like\s+me\s+to"
    r"|(?:shall|should)\s+i"
    r"|(?:can|could)\s+i)\s+"
    r"(?:stop|quit|shut\s+up|leave\s+it)(?:\s+(?:now|then|talking|chatting|going\s+on))?"
    # A bare "go" is a plan - "should i go", "shall i go home", "should i go to the doctor" - so
    # it only counts when the bot is the one being left: "do you want me to go".
    r"|(?:do|would)\s+(?:you|u)\s+(?:want|like)\s+me\s+to\s+go(?:\s+now)?")


STOP_ASK_FILLER = frozenset("""so and but ok okay well now then sorry hmm erm um oh ah hey hi
right alright just also btw honestly""".split())


def a_stop_ask(line):
    """True when the whole line asks whether the person should stop or go."""
    words = [word for word in str(line or "").lower().replace(",", " ").split()
             if word not in ("", " ")]
    while words and words[0].strip(".,!?") in STOP_ASK_FILLER:
        words.pop(0)
    return bool(STOP_ASK.fullmatch(" ".join(words).strip(" .!?")))


# A word of mood or condition. "low" is a state when a person has it; it is a setting, a
# battery, or a shelf when a thing has it. `state_owner` says whose it is, so that a reply
# module consoles a person who is low and not a person who is asking about low heat.
STATE_WORDS = frozenset("""
low down rough tough hard heavy flat empty rubbish crap awful terrible horrible grim bad good
fine better worse ok okay upset sad miserable unhappy disappointed gutted stressed anxious
worried nervous scared frightened angry annoyed furious irritated frustrated bored tired
exhausted knackered shattered drained wiped sleepy swamped overwhelmed snowed fed unwell
poorly sick ill
mad cross fuming livid seething raging irate miffed peeved riled
""".split())


# The state belongs to the person when the thing it sits on is the person's own body, day or
# mood: "a rough day", "my back is sore", "a bad week at work".
PERSON_NOUNS = frozenset("""
day days week weeks month months year years night nights morning mornings evening weekend
term shift shifts sleep time times life mood work job school college uni class classes exam
exams test deadline presentation interview head back leg legs arm arms hand hands shoulder
shoulders knee knees foot feet ankle ankles neck chest stomach tummy hip hips throat eye eyes
ear ears tooth teeth skin hair voice nerves body health
""".split())


# Anybody a person can be low about is worth a kind word, so their state counts as the line's.
OTHER_PEOPLE = frozenset("""
he she they him her them his hers their mum mom dad mother father son daughter kid kids baby
babies toddler toddlers child children infant newborn boy boys girl girls teenager teen lad
partner husband wife boyfriend girlfriend friend friends brother sister family colleague boss
neighbour neighbor uncle aunt cousin gran grandma grandad grandpa nan nana mate mates
dog dogs puppy pup cat cats kitten doggy hamster rabbit rabbits guinea budgie parrot pet pets
""".split())


# A feeling can be a noun too, and then it is the person's own: "my anxiety is bad today". A
# head, a brain or a mind is the person's too, and not a thing that happens to be near them:
# "my brain is fried" is how they are, while "my back is sore" is still the back.
MOOD_NOUNS = frozenset("""anxiety stress worry worries nerves mood depression grief sadness
anger panic fear energy confidence motivation appetite sleep loneliness doubt
head brain mind memory concentration focus""".split())


PERSON_SUBJECT = frozenset("i im me us we myself ourselves nobody nothing everything things".split())


# Words skipped when looking back for the subject of a state word: auxiliaries, adverbs and
# determiners all sit between the subject and its state ("i have been really fed up").
BEFORE_STATE = frozenset("""
am is are was were be been being have has had having do does did feel feels feeling felt get
gets getting got seem seems seemed look looks looked sound sounds sounded taste tastes tasted
a an the so very really quite pretty too bit little lot kind kinda touch just still always again now
 today honestly totally all as than and but then of at with about over on in for from by my your
our their his its am i am not no never still even both either
will would shall should can could may might must wont cant cannot couldnt shouldnt wouldnt
ok okay right well cool sure yeah yep yes alright oh ah hmm hey hi so
""".split()) - {"i"}


# Words that end a state word's reach forward: "tired of work" is still the person who is tired.
PERSON_PREPOSITIONS = frozenset("of with about in at on".split())


# A word that starts a new clause: what follows it is not the noun this state belongs to
# ("pretty low since i moved here").
CONJUNCTIONS = frozenset("since because when while until though although if after before "
                         "whenever and but or yet".split())


BETWEEN_STATE_AND_NOUN = frozenset("""
a an the bit little lot of kind kinda up down out off on at with about over in for from by my
your our their his its so very really quite pretty too just still always again now today
honestly totally all as than
""".split())


# A word after the state that says when, not what: "i have been low all week", "feeling down
# lately". Without this the last word of such a line was read as the thing the state belongs to.
TIME_FILLERS = frozenset("""
morning afternoon evening night tonight noon midnight week weekend month year lately recently
afterwards afterward yesterday tomorrow nowadays midweek
""".split())


# What people put after a feeling to soften it. It says how they say it, not what they feel, so
# it is not the thing the feeling is about: "bit tired to be fair" and "bit rough to be honest"
# were read as a *thing* that is tired, because a word after the state word was taken for the
# noun it belongs to - and a reply that only consoles the person then consoled nobody.
MOOD_TAIL = ("to be honest", "if i am honest", "if im honest", "to be fair", "to tell the truth",
             "to be truthful", "to be blunt", "if anything", "i must say", "i suppose", "i guess")


MOOD_TAIL_WORDS = frozenset("tbh tbf ngl honestly though tho".split())


# The phrase is only filler when the clause still stands without it. "im not going to be honest"
# is about being honest, and the verb in front of the phrase is what says so.
MOOD_TAIL_TAKEN = frozenset("""going go goes went want wants wanted need needs needed try tries
    trying tried mean means meant promise promised learn learned learnt used rather hope hoping
    hate hates love loves have has had like likes prefer plan planning""".split())


def _without_mood_tail(clause):
    """The clause as it reads without the words people soften a feeling with on the end."""
    words = list(clause)
    changed = True
    while changed and words:
        changed = False
        if words[-1] in MOOD_TAIL_WORDS:
            words.pop()
            changed = True
            continue
        for phrase in MOOD_TAIL:
            size = len(phrase.split())
            if size >= len(words) or words[-size:] != phrase.split():
                continue
            if words[-size - 1] in MOOD_TAIL_TAKEN:
                continue          # "not going to be honest" is about being honest
            del words[-size:]
            changed = True
            break
    return words


def _last_subject_pos(words):
    """Where the last word of a clause that could be the thing its state is about sits."""
    for pos in range(len(words) - 1, -1, -1):
        word = words[pos]
        if word in BEFORE_STATE:
            continue
        if len(word) > 4 and (word.endswith("ly") or word.endswith("ing")):
            continue               # "actually doing fine": an adverb or a verb, not a subject
        if word.replace(".", "").isdigit() or word in NUMBER_WORDS:
            continue               # "my mum is 78 and not very good": a number is no subject
        return pos
    return None


def _last_subject(words):
    """The last word of a clause that could be the thing its state is about."""
    pos = _last_subject_pos(words)
    return None if pos is None else words[pos]


# "down" and "up" are as often a direction as a mood: "cant keep anything down", "turn the
# heat down". They carry a state only when a copula or a feeling verb comes first
# ("i am a bit down", "feeling down today").
PARTICLE_STATES = frozenset("down up out off in on".split())


# "ill" is a state only where a copula or a feeling verb makes it one: "she is ill" yes,
# "ill try that, thanks" is "I will", so a bare "ill" without one says nothing.
COPULA_STATES = frozenset("ill".split())


# Words that are a mood as well as an everyday noun: "a new flat" is a home, "i feel flat" is not.
NOUN_STATES = frozenset("flat".split())


# A state word followed by one of these and a thing is a shortage of the thing, not a mood:
# "im low on milk", "we are low on petrol", "im low in iron". The person who has run out of
# milk is not having a low day, so a supply takes the state off the person.
SUPPLY_WORDS = frozenset("low short".split())


SUPPLY_PREPOSITIONS = frozenset("on in of".split())


# The things a person can be low on and still be saying how they are: "im low on energy" is
# tiredness and "im low on confidence" is nerves, so a shortage of one of these is the mood and
# not a fact about the cupboard. Everything else that runs out (milk, petrol, tablets) is a
# supply, and a condolence for it is the wrong reply.
OWN_RESERVES = frozenset("""energy patience confidence motivation enthusiasm inspiration hope
    sleep focus concentration attention steam willpower batteries charge ideas""".split())


DEGREE = frozenset("""bit little lot kind sort very really so too pretty quite more most less
as enough""".split())


DETERMINERS = frozenset("the a an my your our their his her its this that these those it them".split())


# A state word that is also a particle ("down", "up", "off") is the way somewhere just as often
# as the way somebody is, and `cue_about_person` counts a particle whenever a preposition follows
# it, so "im going down the pub" was read as a low and answered with "Sorry to hear that. A walk
# and someone to talk to usually help more than sitting with it." The words of going are what say
# it is a place, and so is an article and a noun that is not a time - "down the shop", "down the
# road", "up the stairs" - while "down this week" and "down the whole week" keep their feeling.
MOTION_WORDS = frozenset("""go goes going went gone walk walks walking walked wander wandering
    head heads heading headed run runs running ran drive drives driving drove ride rides riding
    rode cycle cycles cycling cycled pop pops popping popped come comes coming came hurry hurries
    hurrying stumble stumbling jog jogs jogging climb climbing jump jumping fall falls falling
    fell race racing rush rushing dash dashing nip nipping shuffle shuffling off""".split())


# The nouns that make an article and a noun a length of time rather than a place: "im down the
# whole week" is a mood, and the adjective in front of the noun is why the noun is looked for
# rather than the next word.
TIME_AFTER_A_PARTICLE = frozenset("""week weeks month months year years morning mornings
    afternoon evenings evening night nights weekend weekends time times term terms day days
    while bit moment minute minutes hour hours""".split())


def _particle_is_a_place(words, pos):
    """True when the particle at `pos` is a place or a movement, not how somebody is.

    "im going down the pub", "im off down the road", "walking up the hill", "down the stairs": a
    word of going in front of it, or an article and a noun that is not a length of time behind
    it. "im down the pub" is the same line with the going left out.
    """
    if pos and words[pos - 1] in MOTION_WORDS:
        return True
    if len(words) - pos < 2 or words[pos + 1] not in DETERMINERS:
        return False
    return not any(word in TIME_AFTER_A_PARTICLE for word in words[pos + 2:pos + 5])


def _a_direction(text, at):
    """True when the particle at the character offset `at` is a place, not a feeling."""
    words = [word.strip(".,!?;:-|\"'") for word in text.lower().split()]
    pos = len(text[:at].lower().split())
    return pos < len(words) and _particle_is_a_place(words, pos)


MANIPULATE = frozenset("""turn turns turned turning keep keeps kept keeping put puts putting set
sets setting hold holds holding let lets letting shut shuts shutting slow slows slowing calm
calms calming take takes taking bring brings bringing""".split())


COPULA = frozenset("""am is are was were be been being feel feels feeling felt get gets getting
got seem seems look looks sound sounds still very really quite pretty so too bit little a""".split())


def _copula_before(words, pos):
    """True when the word before the state is a copula or a feeling verb, not a thing."""
    for word in reversed(words[:pos]):
        if word in COPULA:
            return True
        if word in BEFORE_STATE:
            continue
        return False
    return True            # nothing came before it here: the clause before carried the subject


def _noun_reading(words, pos):
    """True when the word here is a plain noun: "a new flat", "the flat"."""
    if pos and words[pos - 1] in DEGREE:
        return False
    return any(word in DETERMINERS for word in words[max(0, pos - 2):pos])


def _thing_turned_down(words, pos):
    """"turn the heat down", "shut it down": a verb, a thing, then a particle."""
    if pos < 2 or words[pos - 2] not in DETERMINERS:
        return False
    return pos == 2 or words[pos - 3] in MANIPULATE


NUMBER_WORDS = frozenset("one two three four five six seven eight nine ten eleven twelve".split())


# A named event is not an object: "the funeral was awful", "the exam went badly" are things that
# happened to the speaker, so the state word describes how it was for them, not the event.
EVENT_NOUNS = frozenset("""funeral christening wake christmas easter birthday wedding anniversary
exam exams interview scan operation surgery birth labour induction move housewarming holiday
holidays honeymoon funeral term semester deadline appraisal review probation""".split())


def _is_person(word):
    """True when the word can be the one who has a feeling: "i", "my mum", "my son"."""
    return (word in PERSON_SUBJECT or word in PERSON_NOUNS or word in MOOD_NOUNS
            or word in OTHER_PEOPLE or word in {"that", "this", "it"})


def _names_a_thing(words, at):
    """True when the word at `at` is a thing that was named: "the soup", "my phone battery"."""
    if words[at] in EVENT_NOUNS:
        return False               # "the funeral was awful": an event is the speaker's own
    return any(word in DETERMINERS for word in words[max(0, at - 3):at])


# The pronoun a relative clause opens with: the state after it belongs to the noun before it.
RELATIVE_SUBJECTS = frozenset(("that", "which", "who"))


def _names_somebody_else(words, at):
    """True when the words up to `at` name a person rather than a thing: "my 5 year old"."""
    return words[at] == "old" and "year" in words[max(0, at - 3):at]


def _whose_state(words, pos, head=None):
    """"self", "other" or "thing": whose state the word at `pos` is, as far as this clause says.

    `head` is where the state word starts when it is more than one word ("fed up"), so the
    subject is looked for before the whole state and the rest is read after it.
    """
    following = [word for word in words[pos + 1:]]
    subject_at = _last_subject_pos(words[:pos if head is None else head])
    if subject_at is not None and words[subject_at] in RELATIVE_SUBJECTS:
        # A relative clause is about the noun in front of it: "i have a houseplant that looks
        # sad" is about the houseplant, and "i have a lawn that looks sad" about the lawn. The
        # pronoun was read as the subject, it is not a person, and the state fell back to the
        # speaker - so the sad pool consoled someone about their lawn.
        earlier = _last_subject_pos(words[:subject_at])
        if earlier is not None:
            subject_at = earlier
    subject = None if subject_at is None else words[subject_at]
    if subject is not None and _copula_before(words, pos):
        # "i feel better today", "she is really down", "my dog has been sick": after a copula
        # or a feeling verb the state describes the subject, whatever loose words come after
        # it. Without this the unknown word at the end of the line made it a thing's state.
        if subject in OTHER_PEOPLE or _names_somebody_else(words, subject_at):
            return "other"
        if _is_person(subject):
            return "self"
        if _names_a_thing(words, subject_at):
            return "thing"         # "the soup tastes awful"
        return "self"              # "christmas will be hard": an event, hard for the speaker
    if following and following[0] in PERSON_PREPOSITIONS:
        if subject in OTHER_PEOPLE:
            return "other"     # "she is worried about the exam": her worry, not the speaker's
        if subject is not None and not _is_person(subject):
            return "thing"     # "the sun is low in the sky": a thing of the weather
        return "self"          # "tired of the noise", "worried about the exam"
    for word in following:
        if word in CONJUNCTIONS:
            break
        if word in BETWEEN_STATE_AND_NOUN or word in TIME_FILLERS:
            continue
        if word.endswith("ly") and len(word) > 4:
            continue            # "a bit down lately": an adverb, not the noun it belongs to
        if word in DETERMINERS:
            continue            # "down this road": the noun after it is the one that decides
        if word.endswith("ing") and len(word) > 4:
            return "self"       # "nervous speaking in front of people": a thing the person does
        if word in OTHER_PEOPLE:
            return "other"      # "my toddler is very sleepy": the child, not the person
        if word in PERSON_NOUNS or word in MOOD_NOUNS:
            return "self"
        return "thing"
    if subject is None:
        return "self"          # "feeling low today": no noun, so it is the person speaking
    if subject in OTHER_PEOPLE:
        return "other"      # "she is stressed about the exam", "my son is unwell"
    if subject in PERSON_SUBJECT or subject in PERSON_NOUNS:
        return "self"
    if subject in MOOD_NOUNS:
        return "self"
    if subject in {"that", "this", "it"}:
        return "self"          # "that sounds awful": the person is reacting to something
    if _names_a_thing(words, subject_at):
        return "thing"         # "the soup tastes awful", "my phone battery is low": a named thing
    return "self"              # "christmas will be hard": an event, and hard for the speaker


BE_FORMS = frozenset("am is are was were".split())


# A state can be carried over to somebody without the state word being said again: "my plant is
# sad and so am i", "my plant is sad, me too", "my plant looks sad and i am too". The words after
# the state word are the only thing that says whose the second state is.
ECHO_CARRIERS = frozenset("""so and but yet or then as well too also just same here yes
me i we us im m""".split())


def _echoed_state(words):
    """"self", "other" or None: whose state a tail after a state word carries over, if any.

    `words` is what follows the state word ("and so am i", "me too", "and the kids too"). A tail
    that names no person carries nothing: "so is the weather" is not somebody's state.
    """
    if not words or len(words) > 6:
        return None
    carried = ((words[0] == "so" and len(words) > 1 and words[1] in BE_FORMS)
               or words[-1:] == ["too"]
               or words[-2:] == ["as", "well"]
               or words[-1:] == ["also"]
               or words[:2] == ["same", "here"]
               # "and i am": the person and a be-verb with nothing after it
               or (len(words) == 2 and words[0] in PERSON_SUBJECT and words[1] in BE_FORMS))
    if not carried:
        return None
    if words[:2] in (["same", "here"], ["me", "too"], ["same", "same"]):
        return "self"                # "same here" and "me too" name the speaker on their own
    if any(word in PERSON_SUBJECT for word in words):
        return "self"                # "and so am i", "me too"
    if any(word in OTHER_PEOPLE for word in words):
        return "other"               # "and so are the kids", "and my mum too"
    return None


def _carried_over(words, state_at):
    """The owner an echo after the state word hands the same state to, or None.

    The echo sits in the same clause as the state word more often than not ("my plant is sad and
    so am i" is one clause), so it is read from the words after the state rather than from a
    clause of its own.
    """
    tail = words[state_at + 1:] if state_at is not None else words
    while tail and tail[0] in CONJUNCTIONS:
        tail = tail[1:]
    return _echoed_state(tail)


def _state_owner(clauses):
    """"self", "other", "thing" or None: whose state the line names, if it names one."""
    owner = None
    carried = None             # the subject of the clause before: "i am so low today"
    # "work is stressing me out", "the kids are tiring me out": the state is the speaker's,
    # even though the sentence's subject is the thing. Without this the mood pools stand down
    # because the line names a thing of its own, and the person gets "Got it. Is there anything
    # you'd like a hand with?" for a line that says how they are.
    if _works_on_the_speaker(" ".join(
            " ".join(str(word) for word in clause) if isinstance(clause, (list, tuple))
            else str(clause) for clause in clauses)):
        return "self"
    for clause in clauses:
        words = _without_mood_tail(clause)
        # A clause that says "so am i" or "me too" carries the state named before it over to
        # whoever it names, without repeating the state word.
        if owner is not None and not any(word in STATE_WORDS for word in words):
            echo = _echoed_state(words)
            if echo == "self":
                return "self"
            if echo:
                owner = echo
        state_at = None
        for pos, word in enumerate(words):
            if word not in STATE_WORDS:
                continue
            state_at = pos
            if word in NOUN_STATES and _noun_reading(words, pos):
                continue                 # "moved into a new flat" is a home, not a mood
            if word in PARTICLE_STATES:
                if _thing_turned_down(words, pos):
                    owner = "thing"          # "turn the heat down": a knob, not a mood
                    continue
                if not _copula_before(words, pos):
                    continue                 # "keep anything down" is no mood either
            if word in COPULA_STATES and (pos == 0 or not _copula_before(words, pos)):
                continue                     # "ill try that, thanks" is not being ill
            head = None
            if word == "fed":
                if "up" not in words[pos + 1:pos + 2]:
                    continue
                head, pos = pos, pos + 1   # "fed up" is one state; the rest follows "up"
            whose = _whose_state(words, pos, head)
            if whose is None and carried in PERSON_SUBJECT | PERSON_NOUNS:
                whose = "self"      # the subject of the clause before: "im low, work is hard"
            if whose == "self":
                return "self"       # the person's own state is the one worth answering
            if whose:
                owner = whose
        if owner is not None:
            echo = _carried_over(words, state_at)
            if echo == "self":
                return "self"      # "... and so am i": the person is in the state too
            if echo:
                owner = echo
        carried = _last_subject(words) or carried
    return owner


def _about_a_supply(text, end):
    """True when the state word ending at `end` is followed by "on/in/of" and a thing.

    "im low on milk", "we are low on petrol", "im low in iron": the state is a shortage of the
    thing, so it is not the person's mood. The person who has run out of milk is not having a
    low day, and neither is a car that is low on petrol.
    """
    rest = [word.strip(".,!?;:-|\"'").lower() for word in text[end:].split()]
    if len(rest) < 2 or rest[0] not in SUPPLY_PREPOSITIONS:
        return False
    thing = rest[1]
    return thing not in OTHER_PEOPLE and thing not in PERSON_NOUNS \
        and thing not in PERSON_SUBJECT


def shortage_of(text):
    """The thing the line says has run out, or None when nothing has.

    `_about_a_supply` already keeps a mood word off "im low on milk", but leaving the line with
    no mood in it is not enough: the composer's own feeling cue ("im low") matched anyway and
    the person who was out of milk got the condolence for a low day. Naming the thing here means
    every module reads a shortage of milk instead of a mood, once, for every turn.
    """
    words = [word.strip(".,!?;:-|\"'").lower() for word in text.split()]
    for at, word in enumerate(words):
        if word not in SUPPLY_WORDS or at + 2 >= len(words):
            continue
        if words[at + 1] not in SUPPLY_PREPOSITIONS:
            continue
        thing = words[at + 2]
        # A word that only points at the thing ("the sun is low in the sky", "low in the
        # morning") is not the thing: the supply is what it names, so nothing is named here.
        if thing in DETERMINERS or thing in OWN_RESERVES or thing in OTHER_PEOPLE:
            continue
        if thing in PERSON_NOUNS or thing in PERSON_SUBJECT:
            continue
        return thing
    # "ive run out of tea bags" names no state word at all, so no supply shape above finds it.
    out = re.search(r"\b(?:run|ran|running) out of ([a-z]+)", text)
    if out and out.group(1) not in OWN_RESERVES and out.group(1) not in DETERMINERS:
        return out.group(1)
    return None


# The things a question about the bot's own life is made of: what a person has and a program
# does not. "do you have kids", "have you got a pet", "what's your job", "do you get paid" all
# name one of these and nothing else, so the bot is the subject of the line. A question to the
# bot that names something of the world keeps its own topic: "do you have a recipe for soda
# bread", "do you have a dog lead i can borrow", "do you have any tips for kids parties" all
# carry a word outside this set.
BOT_LIFE = frozenset("""
family families kid kids child children son daughter mum mom mother father dad daddy parents
parent brother brothers sister sisters sibling siblings gran grans grandma grandmas grandad
grandads grandpa grandparents grandparent uncle uncles aunt aunts auntie aunties cousin cousins
niece nephews relatives relative partner husband wife girlfriend boyfriend friends friend
home house flat apartment town hometown address pets pet dog dogs cat cats kitten puppy hamster
rabbit budgie garden
job jobs work boss manager managers employer colleague colleagues coworker coworkers wages wage
salary paycheck pay paid money bank account mortgage bills rent
body face hands feet hair
birthday age born
name nickname
car cars
""".split())


# The words an ask about the bot's own life is carried by: the ask itself, articles and the few
# everyday words that say nothing about the world. Nothing that could name a subject is here,
# so "do you have a dog lead" and "how's your day" keep their own reading.
BOT_LIFE_FILLER = frozenset("""
a an any some the your you u ur yourself yours own much many really actually ever then now
yet already also too about of for at in on like and or there both coming come came best
""".split())


# The shapes the ask takes. A line has to be one of these and be made of the words above, so a
# question that turns the same words on the world ("do you have a dog that bites") is not read
# as a question about the bot.
BOT_LIFE_ASK = re.compile(r"""
    (?: (?:do|does|did)\s+(?:you|u|ya)\s+(?:have|has|got|get|own|need|want)
      | (?:have|has)\s+(?:you|u|ya)\s+got
      | (?:what|whats|what's|who|whos|who's|whose|which|how)\s+
        (?:is|are|was|were|s|does|do)?\s*(?:your|ur)
      | (?:are|is|was|were)\s+(?:you|u)\s+(?:a|an)
      # "were your mum and dad there", "was your brother there too", "are your parents
      # coming": the thing asked about is the bot's own family, said from the front with no
      # "do you have" in it. Read as an ordinary question it reached the search hedge - "I
      # don't know enough to answer that honestly" to somebody asking whether the bot's mum
      # was at a party - when the bot knows the answer perfectly well: no family at all. The
      # rest-gate below still has to pass, so "is your shop open" and "were your prices
      # online" name something outside the bot's own life and are left alone.
      | (?:are|is|was|were)\s+(?:your|ur)
    )\s*
""", re.VERBOSE)


# "How long have you been going", "how long have you been around", "since when have you been
# here", "how long have you been talking to people": the subject is the bot and the span asked
# about is its own life, which it can answer (nothing before this chat, nothing after it). Read
# as an ordinary "how long" the line was a maths reading, so the savings entry answered "how long
# have you been talking to people" with a line about a queue at the kettle, and "how long have
# you been around" got the search hedge. Only the words a life like that is described with may
# follow the ask, so "how long have you been cooking that stew" and "how long have you been a
# teacher" keep whatever they were.
ITSELF_LONG = re.compile(r"""
    ^\s*(?:so\s+|ok\s+|okay\s+|ah\s+|oh\s+|and\s+|but\s+)*
    (?: how\s+(?:long|many\s+years)
      | how\s+old
      | since\s+when
    )
    \s+(?:have|has|did)\s+(?:you|u|ya)\s+(?:been|be|start|started|go|going|got|get)
    \b
""", re.VERBOSE)


# What can follow the ask when the bot's own life is what was asked about. A real subject on the
# end ("cooking that stew", "a teacher", "the book club") is outside this list and keeps its
# reading, because the person is asking how long the bot has been doing a thing of the world.
ITSELF_LIFE = frozenset("""
going around round about here there online alive running working doing this that it stuff
things talking chatting answering people folks folk to with us in on at now
""".split())


def _how_long_itself(norm):
    """True when the line asks how long the bot itself has been going.

    "how long have you been going", "how long have you been around", "how long have you been
    talking to people": the answer is the bot's own and there is nothing in the world to measure
    or look up, so the line is about the bot. A word of the world after the ask ("how long have
    you been cooking that stew") leaves the line to the topic it names.
    """
    said = " ".join(norm)
    match = ITSELF_LONG.match(said)
    if not match:
        return False
    return not set(said[match.end():].split()) - ITSELF_LIFE


# "When did you start", "when were you built", "how long ago did you start": the same question
# about the bot's own beginning, said the other way round. Read as an ordinary "when" it was the
# search hedge - "that's beyond what I know well, sorry" - which is the one answer a question
# about itself must not get. The tail is the same fence as the "how long" ask, and a shorter one:
# "when did you start running" is a person asking about exercise, so none of the doing words
# count on their own here.
ITSELF_WHEN = re.compile(r"""
    ^\s*(?:so\s+|ok\s+|okay\s+|ah\s+|oh\s+|and\s+|but\s+)*
    (?: when\s+did\s+you\s+(?:start|begin|first\s+start)
      | when\s+were\s+you\s+(?:made|built|started|made\s+up)
      | how\s+long\s+ago\s+did\s+you\s+(?:start|begin)
    )
    \b
""", re.VERBOSE)


# What may follow the "when" ask. Nothing at all is the commonest, and these are the words the
# bot's own life is said with and nothing else: a thing of the world after the ask ("running",
# "your job", "the diet") is outside the list and keeps its reading.
ITSELF_WHEN_TAIL = frozenset("""
going out this that it stuff then today now here online working answering helping
""".split())


def _when_itself(norm):
    """True when the line asks when the bot itself started.

    "when did you start", "when were you built", "how long ago did you start": the answer is the
    bot's own (nothing came before this chat), so the line is about the bot and the knowledge
    base has nothing to look up.
    """
    said = " ".join(norm)
    match = ITSELF_WHEN.match(said)
    if not match:
        return False
    return not set(said[match.end():].split()) - ITSELF_WHEN_TAIL
