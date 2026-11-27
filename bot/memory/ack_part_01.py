"""Part 1 of 7 of the module, split out of `ack`.

Everything here is re-exported from `ack`, so callers import it from there as before.
"""
import re

from ..compose import pick
from . import last_user
from . import facts, named
from . import stuck as stuck_line
from .facts import DAYS, MONTHS



# The keys of facts.extract() that mean "the store learned something about them".
# "age" is in here for the same reason the budget is: "im 41" is a fact they handed over, and the
# stock "thanks for telling me" says nothing about it while "you're 41" does. Only what the reader
# actually keeps is listed: a height is not read out of "im 6 foot 2" yet, so it is not one.
# The facts a line can be said back for. A birthday and a weight are here because a person who
# has just given one has told you something they expect you to keep: "Got it. Is there anything
# you'd like a hand with?" says nothing about what they said, and the fact only shows up on the
# ask that follows, which reads as if the first line had not been heard.
FACTS = ("name", "age", "job", "city", "places", "allergies", "pets", "people", "budget", "diet",
         "plan", "done", "others", "relations", "condition", "tastes", "birthday", "weight",
         "height")


# {Thing} starts a sentence; {thing} sits inside one.
# After a reply about how they feel, what they add next is the reason for it: "i feel like a bad
# mum" then "i hardly see them". The plain frames said that back as a fact to file ("You hardly
# see them \u2014 noted."), which reads as if the feeling had been dropped and only the detail
# was heard. These tails answer the detail as the explanation it is and ask the one thing that
# follows from it. They are chosen only for the turn straight after a feeling (see
# _after_a_feeling), never for a detail on its own.
EXPLAIN_TAIL = (
    "{Thing}. That explains it \u2014 no wonder it sits on you. What would take some weight off?",
    "{Thing}. That is a lot to carry on top of how you feel. What would help most?",
    "{Thing} \u2014 so that is the part behind it. What has been hardest about it?",
)


# A thing they have, said in its own right: "i have a bike" was answered "I'm listening - say
# more if it helps", and taking the false job out of "we have two cars, a fiesta and a focus"
# took the echo of that line with it, because the echo had been riding on the job. This is a
# shape (a having word, then a thing behind it), not a list of nouns. The shapes that only sound
# like a possession are refused: "i have a feeling", "i have no idea", "i have a question",
# "i have to pick the kids up", and "i have a headache", which is a body that hurts.
# Bare past-tense "had" is not a possession and is not read here: "we had a massive row" said
# back as "Noted: you had a massive row" is the coldest reply in STYLE.md, and a row, a day or a
# night is a story rather than a thing they own. A comma after the noun ("we had two cars, a
# fiesta and a focus") still names the thing, that is read in facts.py, and "i have a bike" is
# untouched.
HAVE_THING = re.compile(
    r"\b(?:i|we)(?:['\u2019]?ve)?\s+(?:have(?:\s+got)?|got|own|keep|just got|"
    r"recently got|already got|just bought|bought)\b"
    r"(?:\s+(?:already|just|only|still|now|also))?\s+"
    r"(?:(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|another|some|no|few"
    r"|couple|my|our|his|her|their)\s+)?([a-z][a-z'-]{2,20})\b", re.I)


NOT_A_THING = frozenset("""
    feeling idea question clue hurt look go try rest break problem issue theory plan reason hope
    dream nightmare laugh cry shower think thought memory chance sense guess moment minute while
    day week month year option choice say part lot bit time life job appointment check
    read call text email message right headache pain ache cough cold temperature fever migraine
    bug flu to no not nothing none much more less enough already got
""".split())


# An aim they are working at is not a feeling to explain, though the engine files one as a negative
# feeling ("im trying to lose a bit of weight"). The line after it says what they do about the
# aim, and the reason-reading turned "i walk to work every day" into "You walk to work every day.
# That is a lot to carry on top of how you feel" - telling somebody who has just said something
# they are pleased with that it is a burden. A worry is the other way round: "im worried about my
# exam" then "i have barely revised" really is the reason, and that reading stays.
AN_AIM = re.compile(
    # The aim has to be the line's own main clause, so it is anchored at the start (after a short
    # lead-in). Searching anywhere in the line caught the aim inside a worry - "im worried im
    # going to fail my exam" went down the aim path and lost the reason-reading that a worry
    # keeps - and caught other people's aims ("my sister is trying to lose weight"). "going" is a
    # future marker and not an aim ("im going to tesco on saturday"), and "i want to" counts only
    # when what they want is a thing to work at rather than something they want said or wanted.
    r"^\s*(?:(?:ok|okay|so|well|right|and|but|yeah|hi|hey)[,\s]+)*"
    r"(?:(?:i'?m|i am|im|i|we'?re|we are|we)\s+(?:really |still |just |also |now )?"
    r"(?:trying|hoping|aiming|planning|working|wanting|looking)\b[^.!?]{0,40}?\b(?:to|on|at)\b"
    r"|\bi want to (?!talk|say|tell|ask|know|feel|die|disappear|give up)\b"
    r"|\bi(?:'?m| am|m) on a (?:diet|plan|course|programme)\b)",
    re.I)


# A line saying it is going badly is the other side of an aim: "im trying to lose weight" then "i
# feel like giving up" is a mood that needs the reason-reading, while "i joined a gym" is only
# progress. The engine reads the first as news (intent "news", polarity 0), so the words people
# use are read here. The ways people type it, with the shapes that are progress kept out: "i quit
# sugar" and "i lost half a stone" are not feelings.
A_FEELING_ABOUT_IT = re.compile(
    r"\b(?:"
    r"feel\s+(?:like\s+)?(?:giving|awful|terrible|rubbish|horrible|dreadful|hopeless|useless|"
    r"a\s+failure|like\s+a\s+failure|low|down|bad|shit|stupid|fat|ugly|impossible|sick)"
    r"|dont\s+feel\s+like|don'?t\s+feel\s+like|not\s+feeling\s+it"
    r"|feelings?|felt\s+(?:like|awful|terrible|low|down)|it\s+feels\s+impossible"
    r"|giv(?:e|ing|en)\s+up|gave\s+up|going\s+to\s+quit"
    r"|struggl\w*"
    r"|can'?t\s+(?:do\s+it|keep|cope|face|take\s+it|manage)|cannot\s+(?:do|keep|cope)"
    r"|hopeless|worthless|useless|pointless|miserable|ashamed|guilty|hate\s+my\s+body"
    r"|fail\w*"
    r"|fed\s+up|sick\s+of|had\s+enough|tired\s+of\s+it"
    r"|exhausted|knackered|worn\s+out|burnt?\s+out"
    r"|embarrass\w*|depress\w*|anxious|anxiety|stressed|tearful|crying"
    r"|no\s+motivation|losing\s+(?:heart|motivation)|disheartened|demoralis\w*|demoraliz\w*"
    r"|not\s+going\s+well|going\s+badly"
    r"|worried|scared|afraid"
    r")\b",
    re.I)


# Good news about somebody else is not the person's own news and not a fact to file either:
# "my son got a prize at school" came back as "Noted: your son got a prize at school", which is the
# filing cabinet STYLE.md rules out. The person is telling you something they are pleased about,
# so the line says the thing back and is pleased about it, from the same shape the pools for their
# own news use. Never a question: the person is not asking for anything.
SOMEONE_GOOD = re.compile(
    r"\b(?:prize|award|medal|trophy|cup|distinction|honours|top of the class|head boy|head girl"
    r"|scholarship|won|wins|winning|came first|passed|passing|graduated|graduates|degree"
    # A set of top grades is the same kind of news, and it was arriving as a fact to file: "my son
    # got 4 a stars" was answered "Noted: your son got 4 a stars". The count is how many, so the
    # grade name after it is what makes it news - and the star only counts as a grade where nothing
    # names it, because a star wars set is not one.
    r"|a[\s*'-]?stars?\b(?![\s-]*(?:wars|trek|gazer|gazing|sign|bucks|fish|city|chart))"
    r"|a\*s?|straight 9s|all 9s|all 8s|grade 9|grade 8|top grades"
    r"|got into|got engaged|engaged|married|expecting|gave birth|had a baby|new baby"
    r"|promoted|promotion|new job|retired|retiring|all clear|out of hospital"
    r"|new puppy|new kitten|new dog|new cat|new rabbit|new hamster|new foal)\b", re.I)


SOMEONE_TAIL = (
    "{Thing} \u2014 that's lovely news.",
    "{Thing}. That's a good bit of news to hear.",
    "{Thing} \u2014 you must be pleased for them.",
    "{Thing}. That's worth a bit of a fuss.",
)


# A round birthday of theirs is not a receipt either: "my mum is 70 next week" was answered
# "Noted: your mum is 70 next week". A round one is a thing people make something of.
# A round one, and an occasion it falls on: "my mum is 70 next week" is a thing people make
# something of, and "she is 11" - the age of the child the last turn was about - is a fact that
# keeps the plain ending. So the figure needs the day it falls on, or a birthday word, or a
# decade said in words: an age on its own is never enough.
# A visit announced is news about the person's week, not a fact to file: "my sister is coming to
# stay this weekend" was answered "Noted: your sister is coming to stay this weekend", the filing
# cabinet STYLE.md rules out. The person is telling you something they are looking forward to, so
# the line says it back and is pleased about it, the way another person's good news is. Both
# directions count - them coming to the person ("my parents are visiting next week") and the person
# going to them ("im visiting my mum on sunday") - because both are the same thing to talk about.
# A lift is not a visit ("my mum is coming to pick me up"), a question is not an announcement
# ("when is my sister coming"), and a thing arriving is read elsewhere ("the new sofa comes friday").
SOMEONE_COMING = re.compile(
    r"\b(?:my|our)\s+(?:mum|mom|mam|mother|dad|father|son|daughter|sister|brother|wife|husband"
    r"|partner|aunt|uncle|gran|granny|grandma|grandad|grandpa|nan|cousin|niece|nephew|mate|mates"
    r"|friends?|in[- ]?laws?|parents|family|folks|brother|sister-in-law|brother-in-law)\b"
    r"[^.;!?]{0,18}?\b(?:is|are|was|were)\s+(?:already\s+|just\s+|now\s+|still\s+|all\s+)?"
    # "due" on its own is how people announce a baby - "my partner is due any day" - and the
    # visit pool told a person expecting a child "that's a proper bit of the week". The word
    # only counts the arrival when the arrival is the thing said after it.
    r"(?:coming|visiting|staying|stopping|arriving|due\s+to\s+(?:arrive|come|visit|stay))\b"
    r"|\b(?:i'?m|im|i am|we'?re|we are)\s+(?:off\s+|going\s+)?(?:up|down|over|back)?\s*"
    r"(?:to\s+see|visiting|staying\s+with|stopping\s+with)\s+(?:my|our)\s+"
    r"(?:mum|mom|mam|mother|dad|father|son|daughter|sister|brother|wife|husband|partner|aunt"
    r"|uncle|gran|granny|grandma|grandad|grandpa|nan|cousin|niece|nephew|mate|friends?|parents"
    r"|family|folks)\b", re.I)


# The errand that is not a visit: a lift, a repair, a hand with something. The person coming is
# doing a job on the way past, and "my mum is coming to pick me up" is not a visit to be pleased
# about. Likewise the reflexive "coming over for dinner" is already the cooking lane's.
NOT_A_VISIT = re.compile(
    r"\b(?:pick(?:ing)?\s+(?:me|us)\s+up|drop(?:ping)?\s+(?:me|us)\s+off|collect(?:ing)?\s+"
    r"(?:me|us)|to\s+(?:have\s+a\s+look|check|fix|repair|help|clean|deliver|install|service)\b)",
    re.I)


VISIT_TAIL = (
    "{Thing} \u2014 that's something to look forward to.",
    "{Thing}. Nice \u2014 a proper visit.",
    "{Thing} \u2014 enjoy it.",
    "{Thing}. Good \u2014 that's a proper bit of the week.",
)


SOMEONE_MILESTONE = re.compile(
    r"\b(?:birthday|anniversary)\b[^.;!?]{0,24}?\b(?:next|this|on|is)\s+"
    r"(?:week|month|weekend|today|tomorrow|saturday|sunday|monday|tuesday|wednesday|thursday|friday)\b"
    r"|\bturns?\s+\d{1,3}\b"
    r"|\b(?:forty|fifty|sixty|seventy|eighty|ninety)\b"
    r"|\b\d{2,3}(?:th|st|nd|rd)?\b[^.;!?]{0,24}?\b(?:next|this|on|in)\s+(?:week|month|weekend|"
    r"saturday|sunday|monday|tuesday|wednesday|thursday|friday)\b"
    r"|\b(?:next|this)\s+(?:week|month|weekend)\b[^.;!?]{0,20}?\b\d{2,3}\b",
    re.I)


SOMEONE_MILESTONE_TAIL = (
    "{Thing} \u2014 that's a big one.",
    "{Thing}. Are you doing anything for it?",
    "{Thing} \u2014 a round one deserves a fuss.",
    "{Thing}. That's coming round fast.",
)


# A follow-up that names a second person and nothing about them: "my mums birthday is in may" /
# "and my dads". The line is the same fact for somebody new, with the fact itself left out, and
# the receipt said it back as a bare noun - "Got it - your dads." - which tells the person nothing
# and is not even their words. What is missing is the date, so the store asks for it: the one part
# of the fact the line did not give.
A_SECOND_PERSON = re.compile(
    r"^\s*(?:and|also|plus|or|what\s+about|how\s+about)\b[\s,]*"
    r"(?:my|our|your)\s+(?P<who>[a-z][a-z '-]{1,24}?)\s*(?:'s|s)?\s*[.!?]*\s*$", re.I)


A_BIRTHDAY_TOLD = re.compile(r"\b(?:birthday|bday|dob|date of birth)\b", re.I)


# The verb a plan was said with, so the ask can borrow it: "my mum is coming on friday" asks
# "when is he coming", never "when is he".
A_PLAN_VERB = re.compile(r"\b(?:is|are|was|were)\s+(?P<verb>[a-z]+ing)\b", re.I)


A_DATE_TOLD = re.compile(
    r"\b(?:" + "|".join(MONTHS) + r"|" + "|".join(DAYS) + r"|"
    r"\d{1,2}(?:st|nd|rd|th)\b|next\s+(?:week|month|weekend)|this\s+(?:week|month|weekend))",
    re.I)


def _a_relation(word):
    """The relation a bare possessive names ("dads" -> "dad"), or "" when it names none."""
    said = " ".join(str(word or "").lower().split()).strip(" .,;:!?'")
    for candidate in (said, said[:-1] if said.endswith("s") else "", said.replace(" ", "")):
        if candidate in facts.RELATIONS:
            return candidate
    return ""


def _the_pronoun(relation):
    """"he" or "she" for a relation that says it, and "" for one that does not."""
    if relation in facts.HE:
        return "he"
    if relation in facts.SHE:
        return "she"
    return ""


def _the_ages_held(memory):
    """{relation: age} for the people the chat has already been given an age for."""
    from . import others as the_others
    held = {}
    for entry in (the_others(memory) or []):
        if isinstance(entry, dict) and entry.get("age") is not None:
            held[str(entry.get("who") or "").lower()] = entry.get("age")
    return held


def _people_in_chat(memory):
    """"the youngest" and "the other one" are people only in a chat that has people in it."""
    if not isinstance(memory, dict):
        return False
    user = memory.get("user") or {}
    if isinstance(user, dict) and (user.get("people") or user.get("kids")):
        return True
    from . import others as the_others
    if the_others(memory):
        return True
    for turn in (memory.get("turns") or [])[-4:]:
        said = str((turn or {}).get("user") or "").lower() if isinstance(turn, dict) else ""
        if any(re.search(r"\bmy\s+" + re.escape(one) + r"\b", said) for one in facts.RELATIONS):
            return True
    return False


def a_person_named_alone(text, memory):
    """The question a person named on its own asks for, or "".

    "and my son", "the twins", "same for my daughter": the line is a person and no fact, so there
    is nothing to say back and one thing to ask. The store may already hold the age, and then the
    age is not the question - what they are into is.
    """
    if not isinstance(text, str):
        return ""
    # The little words a person puts in front of the person - "and my son", "and what about my
    # sister", "same for my daughter" - are read off by the same frames every other ask about a
    # person uses (`named.the_one_asked_about`), so a line is a person named on its own however it
    # is said. Read here, "and what about my sister" kept its "what about" and matched nothing at
    # all: the turn had no reply in the whole bot and the person got "Hello!".
    only = named.the_one_asked_about(text) or " ".join(text.split())
    match = A_PERSON_ALONE.match(" ".join(only.split()))
    if not match:
        return ""
    said = " ".join(match.group("what").lower().split()).strip(" .,;:!?'")
    said = WHICH_ONE.sub("", said)
    # The line says "my son" or "the twins" and the reply says it back their way: "your son" and
    # "the twins", never "the son" for a person who said "my son".
    ours = match.group("det").lower() in ("my", "our")
    word = said[:-1] if said.endswith("s") and said[:-1] in facts.RELATIONS else said
    several = said.endswith("s") and said[:-1] in facts.RELATIONS
    # A person named by the place they hold rather than by a relation word: "the youngest", "the
    # second one", "and a baby", "my other half". The line is one of their family and no fact, so
    # the same question is what is left to ask - and "the other one" is only a person when the chat
    # is already about people, because two sofas have an other one too.
    place = A_POSITION.get(" ".join(match.group("what").lower().split()))
    if place:
        # "the youngest" is a person in any chat, and "the other one" is a person only in a chat
        # that already has people in it: two sofas have an other one as well.
        if place in A_POSITION_MAYBE_A_THING and not _people_in_chat(memory):
            return ""
        pool = A_POSITION_LINES.get(place) or A_PERSON_ALONE_LINES
        who = ("Your " if ours else "The ") + place
        return (pick(pool, memory, said).replace("{Who}", who)
                    .replace("{they}", "they").replace("{them}", "them").replace("{do}", "do"))
    group = A_GROUP_ALONE.get(said) or (said[:-1] + "s" if several else "")
    if group:
        who = ("Your " if ours else "The ") + group
        return pick(A_GROUP_ALONE_LINES, memory, said).format(Who=who)
    relation = _a_relation(word)
    if not relation:
        return ""
    return _the_question_about(relation, said, ours, memory)


def _the_question_about(relation, said, ours, memory, name=""):
    """The question a friend asks about this person, said back their way.

    "your son" for a person who said "my son", and the name when the chat has one: "Jack - what
    does he get up to?" rather than "your son" for somebody whose name was already given.
    """
    pronoun = _the_pronoun(relation)
    they, them = (pronoun, "him" if pronoun == "he" else "her") if pronoun else ("they", "them")
    who = name or (("Your " if ours else "The ") + relation)
    known = relation in _the_ages_held(memory)  # an age they gave is not the question
    pool = A_KNOWN_AGE_LINES if known else A_PERSON_ALONE_LINES
    line = pick(pool, memory, said)
    return (line.replace("{Who}", who).replace("{they}", they).replace("{them}", them)
                .replace("{do}", "does" if they in ("he", "she") else "do"))


# A person pointed at rather than named: "what about him", "and her", "what about the two of
# them". The chat already said who the last person was, so the line is a person and nothing else
# and the same question about them is owed - said here, "what about him" after "my son jack is 6"
# got the search hedge, which is a shrug about a person whose name the bot was just given.
A_POINTED_AT = re.compile(r"^(?:him|her|them|they|that one|this one|those two|the two of them|"
                          r"both of them|the pair of them)$")


def a_person_pointed_at(text, memory):
    """The question about the person a "him" or "her" or "them" points at, or ""."""
    if not isinstance(text, str):
        return ""
    only = named.the_one_asked_about(text)
    if not only or not A_POINTED_AT.match(" ".join(only.lower().split())):
        return ""
    word = only.lower().strip()
    # "the two of them" and "both of them" are two people, and the chat has to hold two before the
    # phrase means anybody: a chat with one son and "what about the two of them" is a question the
    # bot cannot answer, and answering about the one son is not what was asked.
    if word not in ("him", "her", "them", "they", "that one", "this one") \
            and _how_many_people(memory) < 2:
        return ""
    if word not in ("him", "her", "them", "they", "that one", "this one"):
        all_named = _the_people_pointed_at(memory)
        if len(all_named) >= 2:
            who = " and ".join(all_named[:2])
            # The ages the chat already has are not the question - "Jack and Emma - how old are
            # they?" asked two children whose ages were the two lines before it.
            pool = A_TWO_ALONE_LINES if all(_an_age_held(memory, one) for one in all_named[:2]) \
                else A_GROUP_ALONE_LINES
            return pick(pool, memory, who).format(Who=who)
    person = _the_person_pointed_at(word, memory)
    if not person:
        return ""
    relation, name = person
    return _the_question_about(relation, relation, True, memory, name)


def _how_many_people(memory):
    """How many people of theirs the chat holds."""
    from . import others as the_others
    return sum(1 for entry in (the_others(memory) or [])
               if isinstance(entry, dict) and str(entry.get("who") or "").lower() in facts.RELATIONS)


def _the_people_pointed_at(memory):
    """The names of the people the chat holds, in the order they were given, named only."""
    from . import others as the_others
    names = []
    for entry in the_others(memory) or []:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("who") or "").lower() not in facts.RELATIONS:
            continue
        name = str(entry.get("name") or "").strip()
        if not name or not name[:1].isalpha():
            continue
        name = name[0].upper() + name[1:]
        if name not in names:
            names.append(name)
    return names


def _an_age_held(memory, name):
    """Whether the chat already has an age for the person of this name."""
    from . import others as the_others
    for entry in the_others(memory) or []:
        if not isinstance(entry, dict):
            continue
        held = str(entry.get("name") or "").strip().lower()
        if held == name.strip().lower() and entry.get("age"):
            return True
    return False


def _the_person_pointed_at(word, memory):
    """(relation, name) for the person the word points at, or None when the chat has nobody."""
    from . import others as the_others
    wanted = {"him": facts.HE, "her": facts.SHE}.get(word)
    people = [entry for entry in (the_others(memory) or []) if isinstance(entry, dict)]
    for entry in reversed(people):
        relation = str(entry.get("who") or "").strip().lower()
        if relation not in facts.RELATIONS:
            continue
        if wanted is not None and relation not in wanted:
            continue
        name = str(entry.get("name") or "").strip()
        if name and name[:1].isalpha():
            name = name[0].upper() + name[1:]
        return relation, name
    return None


def a_second_person(text, memory):
    """The ask for the date of the fact this line leaves out, or "".

    "my mums birthday is in may" / "and my dads" is one fact about two people, and the second
    half says only who. The fact before it is the one being carried over, so the reply keeps it
    and asks for the part the line did not give - the date - instead of saying the noun back.
    Only a line that names a person and nothing else comes here, and only when the turn before it
    was a dated fact about a different person, so a line that changes the subject is left alone.
    """
    if not isinstance(text, str):
        return ""
    match = A_SECOND_PERSON.match(" ".join(text.split()))
    if not match:
        return ""
    who = _a_relation(match.group("who"))
    if not who:
        return ""
    before = " ".join(str(last_user(memory) or "").lower().split())
    if not before:
        return ""
    # The turn before has to be about a person, and about somebody else: "and my mum" after a
    # line about their mum is not a new person to ask about.
    first = next((one for one in facts.RELATIONS if re.search(r"\bmy\s+" + re.escape(one) + r"", before)), "")
    if not first or first == who:
        return ""
    if not (A_BIRTHDAY_TOLD.search(before) or A_DATE_TOLD.search(before)):
        return ""
    said = "your " + who
    if A_BIRTHDAY_TOLD.search(before):
        return "And " + said + "'s birthday \u2014 when is that?"
    verb = A_PLAN_VERB.search(before)
    pronoun = _the_pronoun(who)
    if verb and pronoun:
        return "And " + said + " \u2014 when's " + pronoun + " " + verb.group("verb").lower() + "?"
    return "And " + said + " \u2014 when is that?"


# A line that names a person and nothing else is half a thought: "and my son", "the twins",
# "same for my daughter". With a dated fact before it, `a_second_person` asks for the date that
# was left out. With nothing before it - the first line of a chat - there is no fact to carry
# over at all, and the echo said the noun back: "and my son" was answered "Noted: your son.",
# which is a receipt for something nobody said. The line itself is a person, so the reply asks
# the one thing a friend asks about a person they have just been told about.
A_PERSON_ALONE = re.compile(
    r"^\s*(?:(?:and|also|plus|or|what\s+about|how\s+about|same\s+for|and\s+same\s+for|"
    r"same\s+as|and\s+so\s+does|and\s+so\s+is)\b[\s,]*)?"
    r"(?P<det>my|our|the|a|an)\s+(?P<what>[a-z][a-z '-]{1,24}?)\s*[.!]*\s*$", re.I)


# The words that say which one of several, in front of the person: "my other son" is a son.
WHICH_ONE = re.compile(r"^(?:other|second|third|first|eldest|oldest|youngest|little|big|"
                       r"older|younger|new|baby|step|half|adopted|foster)\s+")


# The several-people words, and the question for them is about all of them at once.
A_GROUP_ALONE = {"kids": "children", "children": "children", "childs": "children",
                 "twins": "twins", "boys": "boys", "girls": "girls", "sons": "sons",
                 "daughters": "daughters", "parents": "parents", "brothers": "brothers",
                 "sisters": "sisters", "grandkids": "grandchildren",
                 "grandchildren": "grandchildren", "grandparents": "grandparents"}


# The place a person holds in the family, said instead of a relation: "the youngest", "my other
# half", "and a baby". A line that names one of these and nothing else is a person and no fact,
# and the question about them is what the reply owes.
A_POSITION = {
    "youngest": "youngest", "youngest one": "youngest", "eldest": "eldest",
    "eldest one": "eldest", "oldest": "oldest", "oldest one": "oldest",
    "middle one": "middle one", "middle": "middle one", "second one": "second one",
    "third one": "third one", "little one": "little one", "littlest": "little one",
    "small one": "little one", "other one": "other one", "baby": "baby",
    "new baby": "baby", "little baby": "baby", "other half": "other half", "half": "other half",
    "partner": "other half",
}


# The places that could also be a thing: "the other one", "the second one", "the middle one" are
# a person only once the chat is about people.
A_POSITION_MAYBE_A_THING = frozenset(("other one", "second one", "third one", "middle one"))


A_POSITION_LINES = {
    "baby": ("{Who} \u2014 how many months?",
             "{Who} \u2014 boy or girl, and how old?",
             "{Who} \u2014 tell me about {them}."),
    "other half": ("{Who} \u2014 how long have you two been together?",
                   "{Who}. What {do} {they} do?",
                   "{Who} \u2014 tell me about {them}."),
}


A_PERSON_ALONE_LINES = (
    "{Who} \u2014 how old is {they}?",
    "{Who}. What {do} {they} get up to?",
    "{Who} \u2014 tell me a bit about {them}.",
)


A_KNOWN_AGE_LINES = (
    "{Who} \u2014 what is {they} into at the moment?",
    "{Who}. How is {they} getting on?",
)


# Two people the chat named, both with their ages given: the age is not the question.
A_TWO_ALONE_LINES = (
    "{Who} \u2014 what are they into at the moment?",
    "{Who}. How are they getting on?",
)


A_GROUP_ALONE_LINES = (
    "{Who} \u2014 how old are they?",
    "{Who}. How are they getting on?",
    "{Who} \u2014 tell me about them.",
)


FRAMES = (
    "{Thing} \u2014 noted.",
    "Got it \u2014 {thing}.",
    "{Thing}, good to know.",
    "Noted: {thing}.",
    "{Thing} \u2014 I'll remember that.",
    "{Thing}, right \u2014 I've got that.",
)


# A line that says they still have something to do is a limit on the plan, not a fact to file.
# "im drained", "i dont know what to do", "i still have the school run to sort": the bot has just
# said to pick the one thing that would make today lighter, and the line is the answer to that -
# except that it was said back, "You still have the school run to sort \u2014 noted.", which is the
# one reply a person who has just been handed a plan is not asking for. Naming the thing they have
# to do is new information about the plan, so it goes first and the rest of the plan waits.
STILL_TO_DO = re.compile(
    r"\b(?:still\s+(?:have|got)|have\s+got|i\s+ve\s+still\s+got)\s+"
    r"((?:the|my|our|a|an|his|her|their|this|that)\s+[a-z' ]{2,28}?)\s+to\s+"
    r"(?:sort|do|deal|get|finish|pay|arrange|handle|see|take|cover|make|run|write|clean|buy|"
    r"order|collect|ring|book|fix|wash|iron|pack|post|send|sign|check|tidy|move|email|print|"
    r"return|visit|walk|feed|look)\b",
    re.I)


# A clause wearing the shape of a thing: "the school run and the tea" is two things, and "that it
# happened" is not a job at all.
NOT_ONE_THING = re.compile(r"\b(?:and|but|so|because|that|if|when|which)\b", re.I)


# Every frame takes the person's own noun phrase, and a job can be one thing or several: "the
# washing" is one and "the bins" is not. "Then the bins is the one thing today, and the rest can
# wait." is what the first two frames said to a plural job, so a frame has to read right either way
# - none of these names the number of the thing.
THE_LIMIT_GOES_FIRST = (
    "Then {thing} first, and the rest can wait.",
    "Then do {thing} first and let the rest wait.",
    "Then take {thing} first \u2014 the rest can wait until it is done.",
    "Fair enough: {thing} first, and the rest of the list waits.",
)


# The words that say a plan was given even when the reply has no number and no colon:
# "You don't have to sort the whole week. Pick the one thing that would make today lighter."
_A_PLAN_WAS_GIVEN = re.compile(
    r"\b(?:one thing|only that|pick|first|start with|begin with|next step|smallest)\b", re.I)


def _the_last_reply_gave_a_plan(memory):
    """Whether the bot's last reply told the person something to do, or how to choose it."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    said = ""
    for turn in reversed(turns or []):
        if isinstance(turn, dict) and str(turn.get("bot") or "").strip():
            said = " ".join(str(turn["bot"]).lower().split())
            break
    if not said:
        return False
    if re.search(r"\d", said) or ":" in said:
        return True
    if _A_PLAN_WAS_GIVEN.search(said):
        return True
    return stuck_line._the_answer_gave_a_step(memory)


def _a_limit_on_the_plan(read, memory):
    """The line's own limit put in front of the plan the last reply gave, or None.

    Only after a step: "i still have the school run to sort" before the bot has said anything is a
    fact to take in, and the store files it. After a step it is the person narrowing the plan, and
    what a friend says is that the named thing goes first.
    """
    if not _the_last_reply_gave_a_plan(memory):
        return None
    found = STILL_TO_DO.search(read)
    if not found:
        return None
    thing = " ".join(found.group(1).split()).strip(" .,!?:;")
    words = thing.split()
    # "i still have to sort it" names nothing, and a whole clause after the verb is a story, not
    # the one thing going first.
    if not 1 <= len(words) <= 4 or NOT_ONE_THING.search(thing):
        return None
    pool = tuple(line.format(thing=thing) for line in THE_LIMIT_GOES_FIRST)
    return pick(pool, memory, read)


# A day on the line is the thing to answer, not something to file. "the vets at 4 tomorrow" was
# answered "Noted: the vets at 4 tomorrow", and "my sister's wedding is in june" "Noted: your
# sister's wedding is in june": the coldest reply in STYLE.md, on a line that has already told
# you what the next few days look like. A friend says something about the day. Reported by
# clear-weasel in #conversation (78962), from a 200-chat sample where 28 of the 34 replies that
# told the person nothing were receipts like these.
#
# Read as two kinds, because the reply differs: a day that is close ("tomorrow", "on friday",
# "the 14th") and one with room to plan ("in june", "next month"). A bare clock time is not
# one of them: "we eat at 6", "she goes to bed at 7" and "the tip shuts at four" are how the
# week works, not a day coming, and "you left school at 16" is a memory.
DAY_SOON = re.compile(
    r"\b(?:tonight|tomorrow|this (?:afternoon|evening)|"
    r"(?:on |next |this )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
    r"(?:next |this |at the |the )weekend|next week|"
    r"(?:on|by|before|until|till) the \d{1,2}(?:st|nd|rd|th)\b"
    r"|\b\d{1,2}(?:st|nd|rd|th) of (?:january|february|march|april|may|june|july|august"
    r"|september|october|november|december)"
    r"|\b(?:is|due|falls?|lands?) (?:on )?the \d{1,2}(?:st|nd|rd|th)\b)", re.I)


# A day word is not enough on its own either: "i saw my mum on sunday", "i took my pills this
# morning" and "it started on tuesday" all name a day, and all are already over. The line has
# to be about a day still to come, so a past telling of it stands down.
DAY_BEEN_AND_GONE = re.compile(
    r"\b(?:saw|met|went|was|were|had|took|tried|left|rang|called|kicked|started|finished|ended"
    r"|moved|got married|felt|ate|slept|woke|bought|sold|made|said|told|came|did|hurt|cried"
    r"|stopped|began|broke|forgot|lost|won|worked|texted|visited|arrived|landed|been"
    r"|this morning|yesterday|last (?:night|week|month|year|weekend|sunday|monday|tuesday"
    r"|wednesday|thursday|friday|saturday)|since (?:six|seven|three|four|five|eight|nine|ten"
    r"|eleven|twelve|two|one|half)|was in|used to|every (?:day|morning|night|week|weekend"
    r"|month|tuesday|monday|sunday|friday|saturday)|usually|always|normally|like the \d+)\b",
    re.I)


# A line with a day on it is a day coming only when the line says what is happening: "and the
# weather there in june", "same again next week i suppose" and "table 4 tomorrow" are a heading
# or a fragment, and "that is one to look forward to" says nothing about them. A figure is not a
# date either: "my rent is 900 in january" is the rent.
A_DOING = re.compile(
    r"\b(?:is|are|am|was|were|be|been|being|have|has|had|got|gets|get|go|goes|going|gone|come"
    r"|comes|coming|came|see|sees|seeing|visit|visits|visiting|fly|flies|flying|meet|meets"
    r"|meeting|start|starts|starting|work|works|working|need|needs|want|wants|wanted|due|take"
    r"|takes|taking|leave|leaves|leaving|arrive|arrives|arriving|stay|stays|staying|play|plays"
    r"|shut|shuts|open|opens|starts|turning|turns|have to|has to|going in|going back|back|off"
    r"|away|free|busy"
    r"|dentist|vets?|doctor|gp|hospital|scan|appointment|haircut|interview|meeting|flight"
    r"|train|bus|viewing|pickup|shift|party|match|wedding|birthday|exam|test|lesson"
    r"|class|club|football|rugby|school|concert|payday|pay day|rent|bill|deadline|review"
    r"|christening|funeral|service|checkup|check-up|surgery|midwife|health visitor)\b", re.I)


A_FIGURE = re.compile(r"\b\d{3,}\b")


# A want or a plan that is turned down is not a day coming. "i dont want pasta tonight" and
# "i dont want curry tomorrow" were answered "You don't want pasta tonight - coming round
# quickly, then": the day word made the line a date, and `want` is in A_DOING, so a refusal was
# filed as an appointment to look forward to. The negation is in front of the verb the day hangs
# on, which is what makes it a refusal rather than a thing happening.
A_DOING_TURNED_DOWN = re.compile(
    r"\b(?:dont|don'?t|do not|doesnt|doesn'?t|didnt|didn'?t|wont|won'?t|wouldnt|wouldn'?t|"
    r"cant|can'?t|cannot|not|never|no longer|no way)\s+(?:\w+\s+){0,2}?"
    r"(?:want|wants|wanted|need|needs|fancy|go|goes|going|have|has|having|do|doing|"
    r"come|comes|coming|came|stay|staying|work|working|eat|eating|drink|drinking|see|seeing|"
    r"happen|happening)\b")


# The same again for the thing being a state rather than an appointment: "he's much worse
# today" and "my son is pale today" are the news of a day that is happening, not one
# still to come, and "she is quite tall for 7" is a seven-year-old, not a time of day.
DAY_JUST_A_STATE = re.compile(
    r"\b(?:worse|better|pale|ill|sick|poorly|off (?:it|his|her|their) food|not himself"
    r"|not herself|up till|up until|much going on|busy|quiet|lovely|nice|awful|horrible)\b",
    re.I)


# When it is: "in june" is a month to plan into, "next june" is further off still.
DAY_FAR = re.compile(
    r"\b(?:in|of|next|this|by)\s+(?:january|february|march|april|may|june|july|august|september"
    r"|october|november|december)\b|\bin (?:the )?(?:spring|summer|autumn|winter)\b"
    r"|\bnext (?:month|year)\b|\blater (?:this|in the) (?:year|month)\b", re.I)


# A day on the line is not always a thing to say something about: a question about the day, and
# a line that asks anything at all, are answered by the module that can answer them.
A_DAY_ASKED = re.compile(r"\?|^(?:what|when|how|why|where|who|can|could|should|do|does|did|is|"
                         r"are|will|would|shall)\b", re.I)


# The endings presume nothing about what the day holds: the line can be an appointment, a payday
# or rent falling due, and "I hope it goes smoothly" or "give me a shout after" only fits the
# first. What is true of all of them is that the day is now in view.
# Not every day coming is one to look forward to. "the inquest is on friday", "the custody
# hearing is on friday" and "the reading of the will is on monday" take the day shapes above, and
# "not long now, then" reads as anticipation on a line like that - a cold receipt would be a poor
# reply but a cheerful one to an inquest is a worse one. Grief and a funeral are already answered
# by the loss modules, so this covers the ones nothing else takes.
NOT_A_DAY_TO_LOOK_FORWARD_TO = re.compile(
    r"\b(?:inquest|post[- ]mortem|autopsy|coroner|funeral|cremation|burial|bury|"
    r"reading of the will|probate|hearing|tribunal|court|custody|bailiffs?|eviction|"
    # Not "we wake up early tomorrow to fly": a morning is not a funeral.
    r"wake\b(?!\s*(?:up|at|early))|"
    r"creditors?|bankrupt(?:cy)?|insolven(?:cy|t)|debt (?:meeting|hearing)|"
    r"repossession|disciplinary|operation|surgery|biopsy|hospice|chemotherapy|radiotherapy|"
    r"diagnosis|results|care assessment)\b", re.I)


SOON_TAIL = (
    "{Thing}. Not long now, then.",
    "{Thing} \u2014 that is soon, then.",
    "{Thing}. Not far off now.",
    "{Thing} \u2014 coming round quickly, then.",
)


FAR_TAIL = (
    "{Thing} \u2014 plenty of time to sort the rest.",
    "{Thing}. That is one to look forward to.",
    "{Thing} \u2014 nice to have something in the diary.",
    "{Thing}. Plenty of time, anyway.",
)


# The endings for a day that is not good news: the day is in view, and what is true of it is that
# it is a heavy thing to have coming - never that it is nearly here.
SORRY_TAIL = (
    "{Thing}. That is a lot to have coming.",
    "{Thing} \u2014 I hope it goes as well as it can.",
    "{Thing}. That is a hard one to have ahead of you.",
    "{Thing} \u2014 no wonder it is on your mind.",
)


def _a_day_coming(clean):
    """Which pool a line about a day ahead wants, or None when it is not one.

    Only the day words matter here: the thing itself is the line, said back by the caller, so a
    pool that says one true thing about a date ahead fits any line with a date on it.
    """
    said = clean or ""
    if A_DAY_ASKED.search(said) or DAY_BEEN_AND_GONE.search(said):
        return None
    if DAY_JUST_A_STATE.search(said) or A_FIGURE.search(said):
        return None
    if A_DOING_TURNED_DOWN.search(said):
        return None
    if not A_DOING.search(said):
        return None
    if NOT_A_DAY_TO_LOOK_FORWARD_TO.search(said):
        return SORRY_TAIL
    if DAY_FAR.search(said):
        return FAR_TAIL
    if DAY_SOON.search(said):
        return SOON_TAIL
    return None


    coming = _a_day_coming(clean)
    if coming:
        # The last resort pool is the receipt, and a receipt is the wrong reply for a line with a
        # day on it: the day is what the person is thinking about.
        return coming


# The same frames, cut into their fixed front and back so a reply that is only the person's own
# line said back can be recognised as one. `bot/compose/fallback.py` asks this before it quotes
# the last reply as the bot's view: "My view has not changed: Got it - but your mum says it's too
# soon" is the bot standing behind a receipt, and there is no claim in one to stand behind.
_SAID_BACK = tuple(
    (frame.split("{", 1)[0].strip().lower(), frame.rsplit("}", 1)[-1].strip().lower())
    for frame in FRAMES
)


# The end of a sentence, for cutting a reply into the parts it is made of.
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


# A dash with space either side, which is how a frame's comma arrives in a finished reply.
_SPACED_DASH = re.compile(r"\s+(?:\u2014|\u2013|-)\s+")


def reads_as_a_receipt(text):
    """True when a reply is one of the frames above with the person's words in it.

    A receipt with the composer's own question after it counts too: "Two kids - good to know.
    How old are they?" is the same nod with a follow-up stuck on the back of it, and every
    caller here asks this question exactly to know whether there is anything to stand behind.
    Read whole, the question after the frame stopped the match, and "what would you do" after
    that turn was answered "Same as I said: two kids - good to know." - the bot repeating a nod
    as though it were a view.
    """
    said = " ".join(str(text or "").lower().split())
    if not said:
        return False
    # The frames are written with a comma and the composer joins with a dash: "two kids, good to
    # know" comes out as "Two kids \u2014 good to know.", which is the same nod with a different
    # mark between the parts. Both readings are tried, because a frame of its own may hold the
    # dash ("Got it \u2014 but your mum says it's too soon.") and must keep it.
    readings = (said, _SPACED_DASH.sub(", ", said))
    for reading in readings:
        if _one_frame(reading):
            return True
    for reading in readings:
        first = _SENTENCE.split(reading)[0]
        if first != reading and _one_frame(first):
            return True
    return False


def _one_frame(said):
    """True when the whole line is one frame with the person's words inside it."""
    for front, back in _SAID_BACK:
        if front and not said.startswith(front):
            continue
        if back and not said.endswith(back):
            continue
        middle = said[len(front):len(said) - len(back)].strip(" \u2014-.:,;")
        # "Got it - ." is not the person's words said back: the frame needs something inside it.
        if middle:
            return True
    return False


# Where the work is, rather than what the work is: "i work in a warehouse", "i work at tesco",
# "i work for the council". The store keeps the words that said where it is (job_frame: "in a",
# "at", "for the"), and those words are what make this a line about the person's week rather
# than a role they are naming - "im a nurse" is answered by bot/modules/chat.py with the job's
# own pool. Said back with the plain frames - "Noted: you work in a warehouse." - the one line
# that tells you most about somebody's day is a filing cabinet, and that was the reply to every
# one of these lines in the deck ("i work in a warehouse" alone seven times). A friend asks
# about the job, and each ending below works for a shop, a school and a call centre alike: the
# thing said back is the person's own words, and no ending names the trade.
WORK_FRAMES = (
    "{Thing} \u2014 what do you do there?",
    "{Thing}. How long have you been there?",
    "{Thing} \u2014 is it a good place to work?",
    "{Thing}. What's a normal day like?",
)


# The prepositions that say where the work is: "at tesco", "in a bakery", "for the council".
# "work as a nurse" says what they do and keeps its own reply, and a bare "work" is "i work
# nights", which the hours pools answer.
WORK_PLACE = frozenset(("at", "in", "for"))


# A line that tells the bot something the store cannot keep - "it came out really well", "i do
# legs on a tuesday", "work has been mad" - has nothing to file, so it used to fall through to
# bot/compose/fallback.py's three stock lines, which fit any message ("Got it. Is there anything
# you'd like a hand with?"). A friend says the thing back and adds one small thing that fits it,
# and the tail is chosen by the shape of what they said - a routine, something still going on,
# something that is over - never by the words of the topic, so the reply cannot be pasted onto
# another line.
HABIT_TAIL = (
    "{Thing} \u2014 that's a proper routine.",
    "{Thing}. That's a habit now.",
    "{Thing} \u2014 keep that up and it'll stick.",
)


GOING_TAIL = (
    "{Thing} \u2014 how's it going?",
    "{Thing}, how long have you been at it?",
    "{Thing} \u2014 how are you finding it?",
)


# A plan with a place and a date in it is not a project with a first step, it is a trip that is
# coming, and the person is telling you something they are looking forward to: "Noted: you're
# going to spain in july." is a filing cabinet. A friend says something about the trip itself,
# and which of the two sets is used is the shape of the plan - a place named, or an occasion -
# never a word of the topic, so no tail can be pasted onto a line that is not a plan.
TRIP_TAIL = (
    "{Thing} \u2014 have you been before?",
    "{Thing}. How long are you going for?",
    "{Thing} \u2014 that's something to look forward to.",
    "{Thing}. What do you want to do while you're there?",
)


OCCASION_TAIL = (
    "{Thing} \u2014 are you looking forward to it?",
    "{Thing}. That'll come round fast.",
    "{Thing} \u2014 that's something to look forward to.",
)


# A pet of theirs: the store keeps the animal and the name ("we have two cats, milly and tom"),
# and the echo said them back - "Noted: you have two cats, milly and tom" - which asks nothing
# about the thing they just told you about. A friend asks the only thing there is to ask about a
# pet: how long it has been there, or whether they get on. The count decides which pool, because
# "do they get on?" to one cat is a question about nothing.
PET_TAIL_ONE = (
    "{Thing} \u2014 how long has it been with you?",
    "{Thing}. What's it like to live with?",
    "{Thing} \u2014 is it good company?",
)


PET_TAIL_MANY = (
    "{Thing} \u2014 do they get on?",
    "{Thing}. Who's in charge?",
    "{Thing} \u2014 how long have they been with you?",
)


# An occasion the person has already said they are not looking forward to ("im going to a wedding
# in september and i hate weddings") cannot be answered with "that's something to look forward
# to": the reply would agree with the surface of the line and contradict the person in the same
# breath. The same is true of a hard day - a funeral, a hospital appointment, a court date - which
# is an occasion with nothing to look forward to. Both keep their words off the calendar and give
# the person something they can use instead.
OCCASION_FLAT_TAIL = (
    "{Thing}. That's a way off yet \u2014 and you can always leave early.",
    "{Thing} \u2014 the run-up is usually worse than the day itself.",
    "{Thing}. Not everything on the calendar has to be a highlight.",
)


# A plan on the calendar that is not a trip and not an occasion: the dentist on Tuesday, the
# hair appointment, the interview, somebody coming to stay. The store kept the day and handed the
# line back - "Noted: the dentist is on tuesday.", "Noted: your mum's coming on friday." - which
# is the coldest reply there is to what most people say about their week. A friend asks the one
# thing that is still open about it: what time it is, or how long the visitor is staying.
DIARY_WORDS = (
    "dentist", "dental", "doctor", "doctors", "gp", "optician", "opticians", "clinic",
    "hospital", "scan", "x-?ray", "check\\s?-?up", "appointment", "interview", "viewing",
    "survey", "mot", "service", "haircut", "hairdresser", "barber", "physio",
    "physiotherapy", "chiropractor", "osteopath", "hygienist", "podiatrist", "midwife",
    "health visitor", "counselling", "vet", "blood test", "bloods", "jabs?", "injection",
    "hearing", "tribunal", "parents evening", "parents' evening", "sports day", "nativity",
    "recital")


# Joined from a tuple, not broken over four lines: an alternation wrapped across lines carries a
# newline in front of every word after the first, so "my physio is on thursday" read as no
# appointment at all and was answered with a receipt.
DIARY_THING = re.compile(r"\b(?:" + "|".join(DIARY_WORDS) + r")\b", re.I)


# A time already said in the line is not asked about again: "im at the dentist at 3" wants what is
# left to say about it, and "what time are you in?" is the bot asking for what it was just told.
DIARY_TIME = re.compile(
    r"\b\d{1,2}(?:[:.]\d{2})?\s*(?:am|pm|o'?clock)\b|\b(?:at|from|by)\s+\d{1,2}\b"
    r"|\b(?:morning|afternoon|evening|noon|midday|lunchtime|first thing)\b", re.I)


DIARY_TAIL = (
    "{Thing} \u2014 what time are you in?",
    "{Thing}. What time is it?",
    "{Thing} \u2014 is it first thing or later?",
)


DIARY_TIME_TAIL = (
    "{Thing} \u2014 is it far from you?",
    "{Thing}. Do you know where it is?",
    "{Thing} \u2014 somewhere you've been before?",
)


# Meeting somebody is not an appointment in a building: the time and the person are already said,
# and what is open is where it happens and who else is in it.
MEETING_TAIL = (
    "{Thing} \u2014 where are you meeting?",
    "{Thing}. Who else is going?",
    "{Thing} \u2014 what's the occasion?",
)


MEETING_TIME_TAIL = (
    "{Thing} \u2014 what time are you meeting?",
    "{Thing}. What time does it start?",
)


# Somebody coming to stay is a plan with a length nobody has said yet, and that is the question a
# friend asks: "my mums coming on friday" is answered about the visit, not filed.
COMING_TO_STAY = re.compile(
    r"\b(?:coming|comes|visiting|staying|arriving|flying over|driving down|over for)\b", re.I)


VISIT_TAIL_ONE = (
    "{Thing} \u2014 how long is {who} staying?",
    "{Thing}. Is {who} staying long?",
    "{Thing} \u2014 how long has {who} got with you?",
)


VISIT_TAIL_MANY = (
    "{Thing} \u2014 how long are they staying?",
    "{Thing}. Are they staying long?",
    "{Thing} \u2014 have they got long with you?",
)


# More than one of them coming. "my mum and dad are coming tomorrow" was answered "Is she staying
# long?", picking the first person out of the line and dropping the other, and "my brothers are
# coming this weekend" was answered "Is he staying long?" for the same reason: the question after
# the receipt names one visitor, and the line names two. The plural is either a kin word said in
# the plural - people write "my brothers", "my parents", "my in laws" and this file keeps only
# the singular - or two of them joined by "and".
PLURAL_KIN = frozenset("""
    parents brothers sisters grandparents grandkids grandchildren children kids twins folks
    family relatives friends mates lads boys girls in laws in-laws
    """.split())


# The word that says what the people named before it are doing: a visit is "my mum and dad are
# coming", and everything between "my" and this word is the list of who.
A_COMING_WORD = re.compile(
    r"\b(?:is|are|was|were|coming|comes|come|visiting|visits|visit|staying|stays|arriving|"
    r"arrives|flying|driving|stopping|stops)\b")


def _more_than_one_coming(said, start, word):
    """True when the line names more than one person coming, from where "my"/"our" starts.

    `word` is the first word after "my"/"our", which is the one the pronoun used to be read from.
    A plural there is enough on its own, and so is an "and" before the coming word: "my mum and
    dad are coming" and "my aunt and uncle are visiting" are two visitors, and the question after
    the receipt has to be the one for a pair.
    """
    if word in PLURAL_KIN:
        return True
    # "brothers", "sons", "cousins": a kin word the file only keeps in the singular, said in the
    # plural. "parents" and "twins" are already plural and are in PLURAL_KIN above. The plural
    # verb is what makes the trailing "s" a plural rather than an apostrophe people leave out:
    # "my brothers are coming" is two visitors and "my mums coming on friday" is one, the same as
    # "my mum's coming on friday".
    if word.endswith("s") and word[:-1] in facts.RELATIONS and word not in facts.RELATIONS:
        return bool(re.search(r"\b(?:are|were|were both|are both)\b", said))
    rest = said[start:]
    cut = A_COMING_WORD.search(rest)
    if cut:
        rest = rest[:cut.start()]
    # "and i"/"and we" is the speaker going with them, which is a third thing again and not a
    # pair of visitors, so it is left to the ordinary reading rather than called a pair.
    if re.search(r"\band (?:i|me|we|us)\b", rest):
        return False
    return bool(re.search(r"\band\b|&", rest))


# The occasions people say they are going to, as nouns that are only ever an occasion.
OCCASIONS = frozenset((
    "wedding", "weddings", "party", "parties", "birthday", "birthdays", "anniversary",
    "hen", "stag", "festival", "festivals", "concert", "gig", "gigs", "reunion",
    "graduation", "christening", "baptism", "barbecue", "bbq", "housewarming", "prom",
    "shower"))


# A shower is only an occasion with the word before it: "i had a shower this morning" is a
# wash, "im going to a baby shower next week" is a party.
SHOWER = frozenset(("baby", "bridal", "wedding", "naming"))


# The places people name with a "the", so the article alone is not what makes the word a thing
# rather than a place: "im going to the tip on saturday" is an errand, "we're off to the
# cotswolds next week" is a trip.
PLACES_WITH_THE = frozenset((
    "algarve", "cotswolds", "lakes", "highlands", "alps", "pyrenees", "cairngorms",
    "wight", "isle", "new forest", "peak district", "lake district", "states", "dales",
    "broads", "fens"))
