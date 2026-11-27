"""Part 2 of 8 of the module, split out of `kinds`.

Everything here is re-exported from `kinds`, so callers import it from there as before.
"""
import re

from . import lexicon
from .kinds_part_01 import (
    GREETINGS, SELF_ONLY_STATE, A_BROKEN_HEART, BROKEN_HEARTED, BROKE_A_HEART, HEART_IN_A_STATE,
    EMOTION_WORDS, OWN_PERIOD_FILLER, OWN_PERIOD_HEADS, OWN_PERIOD_NOUNS, OWN_PERIOD_REACH,
    OWN_PERIOD_STOPS,
)


# The words for a good day that are also another thing: "grand" is a sum of money, "sound"
# is a noise, "chill" is a cold, "content" is what is in a letter. Said about the speaker they
# are how the person is - "im grand ta", "im sound thanks", "im chill" - so they count as a good
# feeling only there, and "the sound of the boiler" or "the content of the email" carries none.
SAYS_HOW_THEY_ARE = frozenset("""alright alrighty grand sound chill content brill mint
    sorted""".split())


STATING_VERB = frozenset("""am is are was were feel feels feeling felt do does doing be been
    seem seems look looking""".split())


SPEAKER = frozenset(("i", "we"))


NEWS = ("i just", "i finally", "today i", "yesterday i", "we got", "we are getting",
        "i got", "i have just", "i have just", "guess what", "big news", "i start",
        "i started", "i finished", "i passed", "i failed", "i moved", "we moved")


ABOUT_BOT = ("are you a bot", "are you real", "are you human", "are you an ai",
             "are you alive", "are you ok", "do you have feelings", "your name",
             "do you remember", "can you remember", "how old are you", "what are you called",
             "are you a chatbot", "are you a person")


ABOUT_BOT_END = ("what are you", "who are you", "what are you exactly")


ROBOT_WORDS = frozenset("bot chatbot robot ai human person machine program real alive".split())


# A man, a woman or a sex word is the bot's own only when the line asks whether it is one.
# "do you like men" asks for an opinion, so the man is the thing liked, and the answer to a
# taste is the bot's own view ("No strong view on that one. What's yours?") rather than the
# line that says what the bot is.
GENDER_WORDS = frozenset("male female man woman men women boy girl".split())


TASTE_VERBS = frozenset("like love prefer fancy enjoy hate dislike".split())


def _a_person_they_like(norm):
    """True when a sex word is what the bot is asked to like, not what it is."""
    for at, word in enumerate(norm):
        if word in TASTE_VERBS and set(norm[at + 1:]) & GENDER_WORDS:
            return True
    return False


# The internet and the data are the bot's own only in a line that also says what it was made or
# trained on. "were you trained on the internet" is about the bot; "what are you using my data
# for" is about the person's own data and keeps the phone answer it had.
LEARNED_ON = frozenset("data internet".split())


def _a_thing_they_own(norm):
    """True when the data or the internet in the line is not what the bot was made of."""
    if not set(norm) & LEARNED_ON:
        return False
    return not set(norm) & (SELF_ASK - LEARNED_ON)


# The products people name when they think there is a model behind the bot. A line that names
# one says what the bot is ("so youre claude"); an ask that names one asks whether there is a
# model under this at all, which is the reading that already had the answer for it.
ASSISTANT_NAMES = frozenset("claude chatgpt gpt gemini copilot siri alexa bard".split())


# The ask has to be the whole line: "is this chatgpt good for essays" is about the essays, and
# "are you claude" is the one that asks what is under the bot.
PRODUCT_ASK_WORDS = 7


PRODUCT_ASK_TAIL = frozenset("then really though now huh yeah or not at all literally exactly "
                             "still please pls tho".split())


# A question whose every word is about the bot is about the bot, however it is phrased: "do
# you have hobbies", "who made you", "what should i call you". SELF_WORDS are the words that
# only a question about the bot uses; SELF_ASK are the ones that make the ask about it, so a
# line with a "you" in it that names anything else ("how do you spell necessary", "what can
# you do with leftover rice") is left to the topic. Nothing here is matched alone: the whole
# line has to be made of these words for the reading to call it about the bot.
SELF_WORDS = frozenset("""you your yourself yours
name called call
made make create created built build built trained train programmed program designed design
wrote written
origin creator
hobbies hobby fun looking look looks
plans plan
bored busy tired awake
feel feelings dream dreams dreamt sleep eat
real alive human person bot robot ai chatgpt gpt claude gemini copilot siri alexa bard
understand remember recall forget
chat talking talk chats answering answer
doing get
from tell
heart soul souls emotion internet data male female man woman men women
model models llm llms personality single married live learn learnt asleep
cry laugh hungry drunk boy girl gender old young
okay ok alright fine""".split())


SELF_ASK = frozenset("""name called call made make create created built build trained train
programmed program designed design wrote written origin creator hobbies hobby fun looking look
looks plans plan bored busy real alive human person bot robot ai chatgpt gpt claude gemini
copilot siri alexa bard understand
remember recall forget get from tell heart soul souls emotion internet data
male female man woman men women personality single married live sleep eat dream dreams
asleep cry laugh hungry drunk boy girl gender old young""".split())


SELF_FILLER = frozenset("""what why how who where when which whose is are was were am do does
did can could will would shall should have has had a an the any some your you yourself yours
i me my at from about like of for to with now then today tonight ever actually really even
still just so much very both all or either on in by using up and so then ok okay""".split())


# "not" is a filler only in front of the bot's own name ("youre not chatgpt", "are you not
# real"). Behind any other verb it is the line's own negative, and the clause it opens is
# about something else: "what do you do when you cant sleep" is a question about sleep, and
# reading it as a question about the bot answered it with the identity line.
# A contraction carries its "not" in front of the subject, so "cant you sleep" reaches this
# line as "can not you sleep" with the bot two words after the not; and the subject can sit in
# front of the auxiliary too ("you cant sleep" is "you can not sleep"). The bot is the subject
# of that clause in both, and the clause is the whole line, so the not is still the bot's own.
NOT_AFTER_THE_BOT = frozenset("you youre your u ur ya are is this it thats that".split())


# The bot word that stands right after a "not" came with the contraction: "cant you sleep",
# "wouldnt you like to know", "didnt you understand me" are all somebody asking about the bot.
NOT_BEFORE_THE_BOT = frozenset("you u ur ya your yourself yours".split())


# The word a "not" leans on when the subject came first: "you can not sleep".
NOT_AUX = frozenset("""can could will would do does did are is was were am have has had
    should shall""".split())


# A clause of the line's own opens here, and the bot named after it is the person's, not the
# line's subject: "what do you do when you cant sleep" keeps its sleep question.
CLAUSE_OPENERS = frozenset("""when whenever if once after before until till while since
    as because unless though although""".split())


# What the bot can do, asked about the bot itself: "what can you do?", "what can you help
# with?". It is about the bot only when nothing else follows: "what can you do with leftover
# rice", "what can you help me cook tonight", "what do you do when your boiler breaks" ask
# about the rice, the dinner and the boiler, and the topic has to decide those.
CAPABILITY = ("what can you do", "what do you do", "how do you work", "what can you help",
              "how can you help", "how do you help", "what can i ask you",
              "what are you good at", "what are you for", "what kind of things can you help")


CAPABILITY_FILLER = frozenset("actually exactly really just still even then now here please "
                              "mate pal though anyway so also "
                              # An "else" or "other" in front of the ask asks the same thing:
                              # "what else do you do", "what other things can you do" are what
                              # a person says after "are you a bot", and the doings pool was
                              # answering them "Nothing much, honestly - no day of my own to
                              # spend." A lead word in front ("so what else do you do", "and
                              # what else can you do") is the same ask too.
                              "else other and but oh yeah ok okay well um hmm".split())


# "else" and "other" are not carriers when a subject follows them, so the subject test below
# still keeps "what else can you do about my leaking boiler" as an ask about the boiler.
# Words that carry no subject of their own, so "with" in "what can you help with" is not one.
# Articles are carriers too because a real subject keeps its noun: "what do you do with a spare
# room" is still about the room. "living" is the one that is only ever the idiom: "what do you do
# for a living" asks what the bot does, and it was read as a question about a living.
# A time or an occasion is not a subject either: "what can you do this weekend", "what do you do
# on weekends", "what can you do in five minutes". The words that make up the time phrase carry
# nothing, and a real subject on the end still keeps its noun, so "what can you do with two
# apples" is about the apples and "what can you do on a rainy day" keeps its day.
CAPABILITY_CARRIER = frozenset("""
    with for about me us at in on during here around then now any anything
    a an the living this that these those next last another more some all
    usually often
    tonight today tomorrow later evening morning afternoon night week weekend
    time times day days evening evenings night nights week weeks weekend weekends
    month months year years hour hours minute minutes second seconds while bit
    one two three four five ten fifteen twenty thirty sixty couple few half
""".split())


CORRECTION = ("i meant", "i mean", "sorry i meant", "rather than", "not ", "actually i",
              "correction", "i said", "no wait", "wait no", "oops i meant", "scratch that")


# Asking the bot what it is doing is conversation, not a question about the world: "what u up
# to", "what you been up to", "you up to much", "much going on". The test is the whole line, so
# a line that names anything else ("what are you doing about the leak", "what are you doing on
# saturday") keeps its own kind and its own topic.
# The words that turn "going on" into a question about the world ("anything going on tonight").
GOING_ON_WHEN = frozenset("""tonight today tomorrow later week weeks weekend morning evening
    night saturday sunday monday tuesday wednesday thursday friday now""".split())


DOING_FILLER = frozenset("""what whats u you ya r are is doing do up to too much been have
    has lately now today tonight then at the moment anything something nothing going on this
    week new else still with watcha whatcha wotcha watchu whatchu doin mate pal buddy love
    lovey hon hun then friend""".split())


# A day already spent, said after the ask: "what have you been up to at the weekend", "what did
# you do yesterday", "where were you last night". The bot has no Saturday ahead of it, so a day
# still coming is left alone and keeps the fence above: "what are you doing on saturday" is the
# plan the person is asking about. The past auxiliary is what tells the two apart.
BEEN_WHEN = frozenset("""yesterday today last night nights morning mornings afternoon afternoon
    evening evenings weekend weekends week weeks day days these all the at over on in this since
    so far lately recently""".split())


BEEN_SAID = frozenset("""did done been were was had doing do up where get got""".split())


# A span of time the bot is supposed to have spent somewhere: "where have you been all day",
# "where have you been lately", "where were you last night". The line is a place question, but
# the place asked about is the bot's own time, and the answer "no address" is the answer to a
# different question. Without a span the plain "where have you been" keeps its place reading,
# which the chat module answers honestly ("nowhere you could visit"). "hiding" is here because
# "where have you been hiding" is the same ask with a joke in it.
SPENT_TIME = frozenset("""all whole day days night nights week weeks lately recently since far
    these hiding""".split())


STILL_COMING = frozenset("""tomorrow tonight later next""".split())


SMALL_TALK = ("how are you", "how is it going", "how's it going", "how is your day",
              "how's your day", "nice to meet you", "what's up", "how do you do",
              "lovely weather", "freezing", "raining", "sunny", "long week", "busy day")


ASK_KEYS = ("how_long", "how_much", "how_many", "how_often", "what", "why", "how", "when",
            "where", "who", "which", "yesno", "choice", "recommend", "steps", "opinion",
            "compare", "definition", "write", "maths", "list")


# Short lines that answer the bot's last turn rather than start a new thought.
SHORT_REPLIES = ("not much", "nothing much", "same here", "me too", "you too", "no idea",
                 "not really", "sort of", "kind of", "fair enough", "sounds good",
                 "sounds great", "good idea", "will do", "i will", "i agree", "me neither",
                 "makes sense", "got it", "for sure", "why not", "of course", "i guess",
                 "that is fair", "no worries", "all good", "very funny", "so true",
                 "not bad", "not a lot", "not a clue", "no bother", "i suppose", "guess so",
                 "u too", "you as well", "same to you", "back at you", "hbu", "wbu", "nmu",
                 "true that", "fair point", "good point", "my pleasure", "any time",
                 "not really sure", "i think so", "hopefully", "probably", "definitely",
                 "absolutely", "exactly", "agreed", "correct", "right", "true",
                 "i dont know", "dont know", "i dunno", "dunno", "who knows", "no clue",
                 "search me", "you know", "not sure", "no idea to be honest",
                 "i do not know", "do not know", "not much", "how about you",
                 "i know right", "you are welcome", "no problem", "same old", "same as always",
                 "what about you", "not too bad")


# Idioms of agreement whose words are the shape of a request: "tell me about it" is "I know,
# you're telling me", not an ask for a briefing, and "you can say that again" is the same
# agreement said louder. The whole line has to be the idiom, so "tell me about the boiler" is
# still the ask its words look like. Kept apart from SHORT_REPLIES because the reply these
# want is not the flat ack: the person has just agreed with something the bot said, so the
# answer carries the agreement back and leaves the floor open.
# Written the way the normaliser spells a line: the apostrophe is gone and the contractions are
# opened out ("don't i know it" arrives as "do not i know it").
AGREEMENT_IDIOMS = ("tell me about it", "you are telling me", "do not i know it",
                    "you can say that again", "you are not wrong", "preaching to the choir",
                    "you and me both", "i know right", "i hear that", "amen to that")


def agreement_of(text):
    """The idiom of agreement the whole line is, or None: "tell me about it", "you and me both".

    The idiom has to be the whole line, or the whole of its first clause: "tell me about it, i
    had one last year" agrees and then says why, and the normaliser writes the clause mark that
    tells the two apart. Anything tighter is the ask the words look like - "tell me about the
    boiler", and also "tell me about it properly", which wants a fuller answer and not a nod.
    """
    said = " ".join(text.lower().replace(",", " ").split())
    first = " ".join(said.split("|")[0].split())
    flat = " ".join(said.replace("|", " ").split())
    return next((phrase for phrase in AGREEMENT_IDIOMS
                 if flat == phrase or first == phrase), None)


EVENT_WORDS = frozenset("""asked told said got went started finished had was were just
today yesterday tomorrow week weekend month year moved passed failed lost found bought sold
paid booked applied interview job trip visit party birthday meeting doctor dentist school
work flat house car dog cat baby wedding holiday""".split())


MATH_WORDS = frozenset("plus minus times divide divided percent percentage half double "
                       "triple sum total average calculate equals".split())


DEFINITION = ("what is a", "what is an", "what are", "what does", "difference between",
              "meaning of", "explain")


# "what are" is the start of two different asks. Said of a thing it asks what the thing is
# ("what are capers", "what are the rules"), which is a definition. Said of a person it asks
# what they are doing with their time ("what are you up to", "what are you doing today",
# "what are we having for dinner"), which is a question, not a definition, and reading it as
# one sent the line to the search hedge instead of the answer.
ASKS_ABOUT_A_PERSON = re.compile(r"\bwhat (?:is|are|r) (?:you|u|ya|we|us|they)\b")


# A bare "what is X", with no article, is the same definition ask: "what is burnout", "what is
# copd", "what is polenta". The phrase list above needs "what is a" or "what is an", so 208 of the
# 266 bare forms on the deck carried no definition at all: the reply was a proper definition and
# there was no label to read it against.
BARE_DEFINITION = re.compile(
    r"^\s*(?:(?:and|but|so|then|ok|okay|right|oh|well|now|sorry|hi|hello|please)\s+)*"
    r"what(?:'s|s| is| are| was)?\s+(?:is|are|was)\s+([a-z][a-z'\u2019-]{1,28})"
    # Not a definition: something compared or judged ("whats french food like", "what is scotland
    # for a weekend"), a purpose ("what is this for"), a live figure or listing ("what is today's
    # date", "whats showing at the odeon", "what is the weather").
    r"(?![^?]*\b(?:like|for|worth|good|cheap|cheapest|easier|easiest|better|best|worse|worst|"
    r"date|time|day|weather|price|cost|news|forecast|temperature|showing|playing|opening|"
    r"score|length|size)\b)", re.I)


# The head word of a bare "what is X" that names nothing to define: an article or pronoun ("what
# is it", "what is this"), a preposition ("what is in the fridge", "whats behind it"), a state
# ("what is happening", "whats coming up"), a number ("what is two thirds of a cup"), or a word
# for no particular thing ("whats something cheap to do tonight").
NOT_A_DEFINITION_HEAD = frozenset("""a an the my your our his her their its this that these
those it i you we they he she there on in up out off about wrong going happening happened next
new best better missing too more most so all any some not just for to with from of at by under
over behind inside between near against than left coming showing playing occurring eating cooking
red one none something anything nothing everything someone anyone everyone two three four five
six seven eight nine ten half quarter third quarter percent percent cheapest easiest quickest
longest shortest biggest smallest largest worth nice easy good double triple eleven twelve thirteen fourteen fifteen sixteen seventeen
eighteen nineteen twenty thirty forty
fifty sixty seventy eighty ninety hundred thousand million""".split())


def _has_any(text, phrases):
    return any(phrase in text for phrase in phrases)


# The greetings and weather words, as the normalised line spells them: the apostrophe is gone by
# then, so "how's it going" arrives as "how is it going".
SMALL_TALK_WORDS = tuple(tuple(phrase.replace("'s", " is").replace("'", "").split())
                         for phrase in SMALL_TALK)


# What may be left over once the greeting itself is taken out and the line is still only small
# talk: the filler of a spoken greeting ("how are you doing then mate", "sunny again today"), the
# greeting that came in front of it ("hiya, how are you doing") and the short function words that
# carry it. A word that names something - a thing, a job, a dish, a verb of doing - is a second
# subject, so the line is not small talk: "raining cats and dogs" is a saying, "the pipes are
# freezing" is about the plumbing and "how are you supposed to defrost a turkey" is a cooking
# question.
# What people call each other in a greeting: a term of address is filler, not a subject, so
# "how are you today my friend" is a greeting and not a line about a friend.
ADDRESS_WORDS = frozenset("""love hun hunny hon dear darling duck pet chuck sweetheart sweetie
    son sunshine mate mates friend friends guys folks""".split())


SMALL_TALK_LEFTOVER = frozenset("""
a an the for of in on out up there here it its is are was were be been am has
and or so but then now again today tonight tomorrow lately already still very really too
quite just all right well good fine bad ok okay not no thanks thank you thx ta cheers ty
u ya mate mates friend friends guys folks everybody everyone hope your way doing going
getting had have last this week month day morning evening night long busy how what about
with us we i around yet even ever only mostly to at by from much appreciated appreciate
my your our their both all two
""".split()) | ADDRESS_WORDS | frozenset(word for greeting in GREETINGS for word in greeting.split())


def small_talk_only(norm):
    """True when the line is a greeting or a word about the weather and nothing else.

    The greeting is taken out first and what is left has to be filler, which is what keeps the
    phrase from matching inside a longer thought: "raining" is small talk in "raining again"
    and weather in "raining cats and dogs"; "how are you" is a greeting, and "how are you
    supposed to defrost a turkey" is a question about a turkey.
    """
    if not norm or len(norm) > 10:
        return False
    for phrase in SMALL_TALK_WORDS:
        size = len(phrase)
        for at in range(len(norm) - size + 1):
            if tuple(norm[at:at + size]) != phrase:
                continue
            rest = set(norm[:at]) | set(norm[at + size:])
            if not rest - SMALL_TALK_LEFTOVER:
                return True
    return False


# What a feeling word can be followed by and still be about how someone feels: a preposition
# ("mad at him"), a connective ("sad that it rained"), a time word that ends the thought
# ("im mad now"). Anything else after it makes the word describe that thing instead: "a mad
# day", "mad busy", "a sad film" say nothing about how the person feels.
CUE_FOLLOW = frozenset("""at with about of by from for in on into onto upon out up down off
away back over under than if as while since during after before until though although unless
around through toward towards even again too also just still yet ever never always sometimes
often usually mostly all any some every each both either neither most much more less least
enough quite pretty really very so that when because and but or now today yesterday tonight
this these those tbh tho atm rn lol haha innit actually
inside outside deep down lately
tomorrow honestly though still lately recently afterwards anyway here there one
i me my mine myself you your yours yourself he him his she her hers it its itself we us our
ours ourselves they them their theirs themselves who whom whose what why how where which
whether is are was were am be been being will would shall should can could may might must
have has had having do does did doing done dont didnt doesnt wont cant im ive ill id youre
theyre thats its gonna going gotta
to as please pls thanks thank cheers sorry sick stiff silly rotten
mate man bro dude guys folks everyone everybody buddy pal bud hon hun love sir madam team""".split())


# The openers of a phrase that says what a thing was like ("a mad day", "a sad film") rather
# than how someone feels. When one of these follows a feeling word, the words after it decide:
# a phrase with a verb in it is still about the person ("im mad the dog ate it"), a bare noun
# phrase is about the thing ("a mad day at work").
PHRASE_OPENERS = frozenset("""the a an this that these those my your his her its our their some
any no every each another one""".split())


# Words that say the words after a feeling word are a clause of their own: a helper verb, a
# verb written in the past, or one of the ordinary irregular ones people use about a day.
CLAUSE_VERBS = frozenset("""went got came said saw made took gave found lost left ran broke fell
kept met paid put sent sat stood thought told won wrote bought brought caught chose drove flew
forgot heard held hit knew ate drank slept woke bit spoke spent built burnt burned grew threw""".split())


# Words that say a clause follows a feeling word when the words themselves do not: a helper, or
# the negations that repair one ("im gutted mum will not come", "im worried she did not eat").
CLAUSE_HELPERS = frozenset("""is are was were am be been being will would shall should can
could may might must have has had having do does did doing not never just still already yet""".split())


# A feeling word in front of one of these is still about the person, because the noun is a state
# a person is in and not a thing beside them: "im in a mad mood", "i was in a low state", "shes
# in a right temper". Only the article in front of it says so - "we went to a mad place" names a
# place - so the words before the feeling have to end on "in a"/"of a" and the like.
STATE_NOUNS = frozenset("""mood state spirits temper frame mind head shape form headspace
mindset humour humor moodstate""".split())


STATE_TAIL = re.compile(r"\b(?:in|of)\s+(?:a|an|such\s+a|a\s+right|a\s+real|a\s+proper|"
                        r"the|this|that)\s*$")


# "i am gutted", "i was scared", "i feel low": the feeling is the speaker's own, so a clause
# after it is what the feeling is about rather than a description of a thing.
SPEAKER_TAIL = re.compile(r"\bi (?:am|was|feel|felt|have been|had been|do feel|did feel"
                          r"|am feeling|was feeling|been feeling|have been feeling"
                          r"|had been feeling)$"
                          # "i woke up feeling numb", "i sat there feeling empty": the feeling
                          # verb is what matters, whichever words came before it.
                          r"|\bi(?: \w+){1,3} (?:feel|feeling|felt)$"
                          # "we are shattered", "we were gutted": the same state said of us.
                          r"|\b(?:we|us) (?:are|were|feel|felt|have been|had been|do feel"
                          r"|did feel|are feeling|were feeling|been feeling)$"
                          r"|\bwe(?: \w+){1,3} (?:feel|feeling|felt)$"
                          # "were shattered": people write "we're" as "were".
                          r"|^were$")


# Words ending in -ing that are things or names, so the guard below leaves them alone: "im at the
# building in the morning" is not a verb holding the word after it.
ING_THINGS = frozenset("""morning evening ceiling building wedding pudding clothing shopping
    offering meeting parking lighting heating bedding flooring roofing fencing bedding
    thing something nothing anything everything king ring string spring wing sing bring swing
    going being doing having making taking coming""".split())


# The -ing words that take no object. "im moving flat" and "im renting flat" are a move and a
# tenancy: the verb in front of the feeling word takes it as the thing the verb acts on. A verb of
# posture, movement or becoming takes no object at all - what follows it is what the person is
# doing it *as*, or where they are - so "im sitting sad", "im running flat", "im becoming sad"
# and "im staying sad" are all the person's own state, said with the verb still going on. Read as
# objects, ten of those lines lost the condolence they had and got a card about the next thing.
ING_TAKES_NO_OBJECT = frozenset("""
    act acting appear appearing arrive arriving become becoming come coming fall falling feel
    feeling get getting go going grow growing keep keeping lie lying live living look looking
    remain remaining rest resting rise rising run running seem seeming sit sitting sleep sleeping
    sound sounding stand standing stay staying turn turning wait waiting walk walking work
    working""".split())


def _a_verb_holds_it(text, at):
    """True when the word in front of a feeling word is a verb doing something to it.

    "im moving flat on saturday" is a move to a flat and "im renting flat next month" is about
    the tenancy, but both read as a low mood because a feeling word followed by a preposition
    counted as the person's own state. An -ing word in front of it is the verb that takes it as
    its object, wherever the person cue sits - but only a verb that can take an object at all
    (ING_TAKES_NO_OBJECT), because "im sitting sad" is the person's own state with a verb going
    on beside it, not a thing done to the sadness. A copula or a feeling verb is let through,
    because those are what make the word describe the person: "i was feeling flat", "my tomato
    plants are looking sad".
    """
    words = [word.strip(".,!?;:-|\"'").lower() for word in text[:at].split()]
    if not words:
        return False
    last = words[-1]
    return (last.endswith("ing") and last not in FEELING_CUES_BEFORE
            and last not in ING_THINGS and last not in ING_TAKES_NO_OBJECT)


def _state_before(text, at):
    """True when the words before a feeling word say the state is the speaker's own.

    "im in a mad mood", "i was in such a low state", "in a right temper": a preposition and an
    article in front of the feeling word are what make the state noun next to it the person's.
    """
    words = [word.strip(".,!?;:-|\"'").lower() for word in text[:at].split()]
    return bool(STATE_TAIL.search(" ".join(words[-4:])))


def _verb_after(rest):
    """True when a clause follows a feeling word: a helper or a verb in the next few words."""
    words = [word.strip(".,!?;:-|\"'").lower() for word in rest.split()[:5]]
    for word in words:
        if word in CLAUSE_HELPERS or word in CLAUSE_VERBS:
            return True
        if len(word) > 3 and word.endswith(("ed", "ing")):
            return True
    return False


def _clause_follows(rest):
    """True when the words after a feeling word are a clause: "the dog ate it", "my sister
    forgot my birthday". False for a bare phrase that describes the thing: "day at work".
    """
    words = [word.strip(".,!?;:-|'\"") for word in rest.split()]
    end = len(words)
    for i, word in enumerate(words):
        if word and word[-1] in ".,!?;:-|":
            end = i + 1
            break
    clause = [word.lower() for word in words[:min(end, 8)] if word]
    if not clause:
        return False
    for word in clause[1:]:
        if word in CUE_FOLLOW or word in CLAUSE_VERBS or word.endswith("ed"):
            return True
    return False


# A body part is "upset" too, and that is a stomach rather than a mood: "my stomach is upset".
BODY_SUBJECT = frozenset("""stomach tummy gut belly back leg legs arm arms head throat chest skin
eye eyes ear ears tooth teeth stomachs""".split())


def _a_body_part_before(text, cue):
    """True for "my stomach is upset", where the word before the cue is a body part."""
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
        before = [word.strip(".,!?;:-|\"'").lower() for word in text[:match.start()].split()]
        before = [word for word in before if word not in FEELING_FILLER and word != "is"]
        if before and before[-1] in BODY_SUBJECT:
            return True
    return False


# The words that can stand between a person and their state: "im so shattered", "they were
# really low", "my mum is pretty awful".
STATE_JOINERS = frozenset("""am is are was were be been being feel feels feeling felt still
really very so too pretty quite a bit little just now also always lately today tonight""".split())


# A state word that is also something a person does takes an object: "i wiped out the savings"
# and "he upset the cart" are actions, not how somebody is. A determiner or a possessive after
# the word is the object, so the state has to stop first (at a clause word, or the end of the line).
OBJECT_MARKERS = frozenset("""the a an my your his her their our this that these those
another every some any no""".split())


# A demonstrative in front of a time word opens a time phrase, not an object: "i feel low this
# week" names when the week was, and "im shattered every morning" the mornings. The week is not
# something the person felt low out of, the way "i wiped out the savings" is.
TIME_MARKERS = frozenset("this that these those every each".split())


TAIL_STOPS = frozenset("""after before since until when if and but so because though while
than then too also still now today tonight lately recently honestly about at in on of for to
with by from as like""".split())


def _state_cue(cue):
    """The word in `SELF_ONLY_STATE` this cue is built on, or None: "wiped out" is "wiped"."""
    if cue in SELF_ONLY_STATE:
        return cue
    head = cue.split()[0]
    return head if head in SELF_ONLY_STATE else None


# A state word that is also what an animal does: "im pooped" is tired, "the dog pooped on the
# carpet" is the dog. The state has to be carried by a copula or a feeling verb, so the same word
# said of a pet with nothing in front of it is the pet's doing.
VERB_ONLY_STATE = frozenset("pooped".split())


# What carries a state onto a subject: "im pooped", "i was pooped after the run", "we both feel
# pooped". Intensifiers between it and the word are skipped ("im so pooped").
COPULA_BEFORE = frozenset("""im am is are was were be been being feel feels felt feeling
get gets got gettin look looks looked seem seems seemed sound sounds sounded""".split())


def _a_copula_before(text, start):
    """True when a copula or a feeling verb comes just before `start`: "im so pooped"."""
    words = [word.strip(".,!?;:-|\"'").lower() for word in text[:start].split()]
    while words and (words[-1] in FEELING_FILLER or words[-1] in ("both", "all")):
        words.pop()
    return bool(words) and words[-1] in COPULA_BEFORE


# A word that rates what somebody can do is not a mood: "im crap at maths" and "she's rubbish
# at school" are about ability, and the same word on its own is the mood ("im crap today").
# The reply side keeps its own copy of this list; both say the same thing.
ABILITY_AT = re.compile(r"\b(?:bad|crap|rubbish|rough|useless|hopeless|terrible|awful|lousy|"
                        r"poor|worse|worst)\s+(?:at|with)\b")


# A feeling word in front of its own episode is still the feeling: "im having a panic attack",
# "she had two anxiety attacks". A word that runs on into another word usually describes that
# word ("a mad day"), but these nouns name nothing except the feeling itself, so they cannot
# turn it into a description.
EPISODE_NOUNS = frozenset("attack attacks episode episodes spell spells".split())


def _names_an_episode(text, cue):
    """True for "panic attack": the cue runs into the noun for its own episode."""
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b\s+(\w+)", text):
        if match.group(1).lower() in EPISODE_NOUNS:
            return True
    return False


# "down" says how somebody is, and it is a direction or a particle just as often: "turn the heat
# down", "keep it down", "a down sleeping bag", "coming down with a cold". The feeling list never
# carried the word, so "i have been down all week" was read as news and handed back as an echo.
# It names a feeling only in the shape that leaves no other reading - a copula or a feeling verb
# right before it ("im down", "feeling down today", "i have been a bit down all week"), the
# speaker or somebody named having it, and nothing after it that makes it agreement or a shortage
# ("im down for that", "down to my last tenner"). The list stays a list of one: the same rule on
# "bad", "terrible" or "heavy" reads a bad back, a terrible cough and heavy legs as a low day.
STATE_AS_FEELING = frozenset(("down",))


# What the word is followed by when it is agreement or a shortage rather than a mood.
FEELING_NOT_MOOD = frozenset("""for to on at""".split())


# The only words allowed between the verb and the state: degrees, and the small adverbs people
# put there. Anything else means the verb belongs to another word - "coming down with a cold",
# "get him to sit down" - and the state there is a particle or an adjective, not the feeling.
FEELING_FILLER = frozenset("""a an bit little lot kind kinda sort so too very really quite pretty
    just still always again now today totally honestly also either all more most less as
    enough well""".split())


# The words that can make a state word describe somebody: a copula or a feeling verb. "a" and
# "the" are in `COPULA` because they let a state describe the noun after them ("a bit low"), and
# a determiner before "down" is the opposite case - "a down sleeping bag", "the down pillow".
FEELING_COPULA = frozenset("""am is are was were be been being feel feels feeling felt get gets
    getting got seem seems seemed look looks looking sound sounds sounded""".split())


# Words that stand between a person and a feeling word without taking it as their object: the
# copulas and the feeling verbs ("i was feeling flat", "the plants are looking sad"). Every other
# -ing word in that place is doing something to the next word.
FEELING_CUES_BEFORE = FEELING_COPULA | frozenset("feel feels feeling felt".split())


def a_broken_heart_shape(text):
    """True when the line says a heart is broken, in any of the shapes people type it."""
    low = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    return bool(HEART_IN_A_STATE.search(low) or BROKEN_HEARTED.search(low)
                or BROKE_A_HEART.search(low) or A_BROKEN_HEART.search(low))


# The words that put the broken heart on somebody else: "her heart is broken" is a friend's
# trouble, and the sad pool's advice is written for the person who is in it.
NOT_THEIR_OWN = frozenset("""her his their your mum mom mother dad father son daughter husband
    wife partner friend sister brother child kid boss neighbour neighbour's nan gran""".split())


# The people a heart can belong to without being the speaker's. "she is heartbroken" and
# "my dad was broken hearted" are somebody else's trouble, and the card about a broken heart is
# written for the person who is in it. Only a person who is the *subject* of the line counts:
# "her heart is broken" puts the heart itself first, and a heart is a part of a person, so
# reading whose it is takes more than the word in front of it.
A_PERSON_ELSE = frozenset("""mum mom mother dad father son daughter husband wife partner
    friend sister brother child kid boss neighbour nan gran""".split())


A_PERSON_IS_THE_SUBJECT = re.compile(r"^(?:he|she|they|him|them)\b")


# A heart said as the thing the line is about: "his heart is broken", "my mums heart is broken".
# A heart is a part of a person, and whose it is takes reading the person, not the word in front
# of it - so a line that makes the heart the subject is left to the row that already answered it.
A_POSSESSED_HEART = re.compile(r"\b(?:my|our|her|his|their|your|the|a|an)\s+(?:\w+'?s\s+)?hearts?\b")


def _somebody_elses_heart(text):
    """True when the broken heart the line names is somebody else's, and the line says whose.

    "she is heartbroken" and "my mum is heartbroken" give another person as the subject and the
    feeling after it, which is their state and not the speaker's. It is read from the words,
    because there is no state word here for `_state_owner` to hang an owner on - "heartbroken"
    is a feeling but not a state word - so without this the line is nobody's, and the speaker's
    card answers somebody else's trouble.
    """
    low = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    if not a_broken_heart_shape(low) or _a_broken_heart_is_theirs(low):
        return False
    if A_POSSESSED_HEART.search(low):
        return False                     # "his heart is broken": the heart is the thing said
    if A_PERSON_IS_THE_SUBJECT.match(low):
        return True                      # "she is heartbroken", "they are broken hearted"
    words = low.split()
    if len(words) > 1 and words[0] in ("my", "our", "the"):
        person = words[1].strip(".,!?'\"")
        if person in A_PERSON_ELSE or person[:-1] in A_PERSON_ELSE:
            if words[2:3] in (["heart"], ["hearts"]):
                # "my mums heart is broken" - the possessive apostrophe is often missing, so the
                # heart sitting right after the person is the case this reads anyway: the heart
                # is the thing the line is about, and whose it is takes more than that.
                return False
            return True                  # "my mum is heartbroken", "my wife said she is heartbroken"
    return False


HAVE_A_BROKEN_HEART = re.compile(r"\b(?:i have|i've got|ive got|i got|i had)\b[^.]{0,24}broken heart")


def _a_broken_heart_is_theirs(text):
    """True when the heart the line breaks is the speaker's own.

    "my heart is broken" and "im broken hearted" are the person's, and so is "i have a broken
    heart". "her heart is broken" and "my mum's heart is broken"
    are somebody else's, and "how do i get over a broken heart" is one in general - the sad
    pool's advice is written for the person who is in it, so only the speaker's own heart
    counts. The owner is read from the word in front of the heart, because that is where the
    line puts it, and a name or a relation with an "s" on it ("mums heart", "friends heart")
    is as much somebody else's as "her".
    """
    low = " ".join(str(text or "").lower().replace("\u2019", "'").split())
    if not a_broken_heart_shape(low):
        return False
    words = low.split()
    starts = [match.start() for match in
              (re.search(r"\bhearts?\b", low), re.search(r"\bbroken\b", low)) if match]
    at = len(low[:min(starts)].split()) if starts else 0
    window = words[max(0, at - 2):at]
    owner = window[-1] if window else ""
    if HAVE_A_BROKEN_HEART.search(low):
        return True                      # "i have a broken heart"
    if BROKE_A_HEART.search(low):
        return False    # "he broke my heart" is an event, and the break-up answer has it
    if owner in NOT_THEIR_OWN or owner.endswith("'s") or (
            owner.endswith("s") and owner not in ("is", "was", "this", "its", "us")):
        return False                     # "her heart", "my mum's heart", "mums heart"
    if any(word in ("my", "our") for word in window):
        return True                      # "my heart", "my poor heart"
    if owner in ("a", "an", "the"):
        return False                     # "a broken heart" is the thing being talked about
    return not re.search(r"\b(?:her|his|their|your)\b", low) \
        and bool(re.match(r"^(?:i|im|i'm|ive|i've|we|we're|weve|we've|our)\b", low))


# The polite way of saying a day is not great. These are the whole answer to "how are you", and
# they carry no word of mood at all, so "could be better" was read as no feeling and got a search
# hedge ("that's beyond what I know well, sorry. Searching for it will turn up better sources").
# The line has to be made of nothing else, because the same words compare things: "the sauce
# could be better" is about the sauce, "ive been better since the op" is good news, and
# "i couldnt have been better" is the best day of their life.
HEDGED_LOW = frozenset((
    "could be better", "could be better i suppose", "been better", "not so good", "not too good",
    "not so great", "not that good", "not that great", "so so"))


# The good answer with a shrug on the end. "fine i guess" is not fine: it is fine with a doubt
# after it, and the composer answers the bare "fine" with "Fair enough", which is the reply to
# somebody who does not want to talk about it. The doubt has to be the last thing in the line,
# and what it is doubting has to be the whole answer, so "ok thanks" stays the fine it is and
# "i did well i guess" is not read as a low. "not bad" is deliberately not here: it is already a
# fine, and "not bad i suppose" is the same fine said more carefully - "glad to hear it" is the
# right reply to it, not the sad pool.
HEDGED_DOUBT = ("i suppose", "suppose", "i guess", "guess", "ig", "i spose", "s'pose", "i gues")


HEDGED_OK = frozenset((
    "ok", "okay", "fine", "alright", "all right", "good", "well", "grand", "not too shabby"))


# The words a person wraps the answer in, which are not part of it: "could be better thanks",
# "been better tbh", "well, could be better". Taken off both ends, and only from the ends, so
# "im better than i was" and "the sauce could be better" keep their words.
HEDGED_WRAPPER = frozenset("""
    im i am well yeh yeah yep oh ah eh hmm hm its it it's is honestly to be totally quite
    thanks thank you ta tbh tbf lol ig i guess suppose today love mate and you you
    honest really sure actually kinda sorta atm currently now very pretty
""".split())


def _a_hedged_low(text):
    """True when the whole line is the polite way of saying not great: "could be better".

    The reading hands this the line with a bar where one clause ends and the next begins
    ("could be better | you"), so the bar is punctuation like the rest of it.
    """
    words = [word.strip(".,!?;:-'\"|") for word in str(text or "").lower().split()]
    words = [word for word in words if word]
    doubted = False
    for phrase in HEDGED_DOUBT:
        count = len(phrase.split())
        if len(words) > count and " ".join(words[-count:]) == phrase:
            words = words[:-count]
            doubted = True
            break
    while words and words[0] in HEDGED_WRAPPER:
        words.pop(0)
    while words and words[-1] in HEDGED_WRAPPER:
        words.pop()
    answer = " ".join(words)
    return answer in HEDGED_LOW or (doubted and answer in HEDGED_OK)


def _copula_just_before(words, pos):
    """True when a copula or feeling verb sits directly before the word, degrees aside."""
    for word in reversed(words[:pos]):
        if word in FEELING_FILLER:
            continue
        return word in FEELING_COPULA
    return False


# A thing that is doing something to the person, said with a verb instead of a word for how
# they are: "work is stressing me out", "the kids are tiring me out", "this is worrying me".
# The feeling is in the verb's -ing, the person it happens to is "me", and nothing in the line
# is a word this file's lists know - so `work is stressing me out` read as no mood at all and
# was answered "Got it. Is there anything you'd like a hand with?" while "im stressed about
# work" got the stressed pool. The verb says which feeling: the stem is the state.
WORK_ON_ME = {
    "stresses": "anxious", "stressing": "anxious", "strains": "anxious",
    "straining": "anxious", "worries": "anxious", "worrying": "anxious", "worried": "anxious",
    "frets": "anxious", "fretting": "anxious",
    "drains": "tired", "draining": "tired", "drained": "tired",
    "tires": "tired", "tiring": "tired", "exhausts": "tired", "exhausting": "tired",
    "exhausted": "tired", "wears": "tired", "wearing": "tired", "wore": "tired",
    "worn": "tired",
    "annoys": "angry", "annoying": "angry", "annoyed": "angry",
    "irritates": "angry", "irritating": "angry", "irritated": "angry",
    "frustrates": "angry", "frustrating": "angry", "frustrated": "angry",
    "bugs": "angry", "bugging": "angry", "bugged": "angry",
    "bothers": "angry", "bothering": "angry", "bothered": "angry",
    "winds": "angry", "winding": "angry",
    "upsets": "sad", "upsetting": "sad", "depresses": "sad", "depressing": "sad",
    "depressed": "sad",
    "scares": "anxious", "scaring": "anxious", "scared": "anxious",
    "frightens": "anxious", "frightening": "anxious", "frightened": "anxious",
    "confuses": "confused", "confusing": "confused", "confused": "confused",
}


# The words that may sit between the verb and the person it acts on ("stressing me right out").
ACT_ON_FILLER = frozenset("""so right really totally absolutely just always still all quite""".split())


# The parts of the body a line can name as the thing doing it. `BODY_SUBJECT` above is the list
# a state word is read against; a joint that aches is the same case for this rule ("my knee is
# bothering me") and is added here rather than there.
PARTS_OF_ME = BODY_SUBJECT | frozenset("""knee knees shoulder shoulders hip hips neck ankle
    ankles wrist wrists hand hands finger fingers toe toes elbow elbows foot feet jaw tooth
    teeth sinuses earache toothache headache migraine backache""".split())


# The words that may sit in front of the verb without making it somebody else's: the copulas
# a thing gets ("the noise is bothering me"), the adverbs people put there, and the words that
# make a habit of it ("it keeps waking me up").
ACT_ON_LEAD = frozenset("""am is are was were be been being keep keeps kept get gets got
    always every still just really totally so very all quite sometimes often daily""".split())


def _works_on_the_speaker(text):
    """The feeling a thing does to the speaker, or None: "work is stressing me out".

    Only the shape <thing> <verb> me/us, and only a verb whose stem is a feeling, so "he
    stressed the point" is not it. The person acted on has to be "me" or "us": "the kids are
    tiring my mum out" is her state, not the speaker's.
    """
    words = [word.strip(".,!?;:-|\"'()").lower() for word in str(text or "").split()]
    for pos, word in enumerate(words):
        feeling = WORK_ON_ME.get(word)
        if not feeling:
            continue
        lead = None
        for back in range(pos - 1, max(pos - 4, -1), -1):
            if words[back] in ACT_ON_FILLER or words[back] in ACT_ON_LEAD:
                continue
            lead = words[back]
            break
        if lead in ("i", "i'm", "im", "me", "my", "myself", "we", "our"):
            continue                   # "im stressing me out" is nobody's line
        named = [word for word in words[max(pos - 4, 0):pos] if word not in ACT_ON_FILLER]
        if any(word in PARTS_OF_ME for word in named):
            # "my knee is bothering me", "my back is annoying me": the thing doing it is a part
            # of the body, so the line is about a pain and not about a temper. The anger pool's
            # "walk it off for ten minutes before you reply to anyone" is advice about somebody
            # who annoyed you, and it was worse here than the line's shrug.
            continue
        if lead and (lead.endswith("nt") or lead in ("not", "never", "no")):
            continue                   # "it doesnt stress me out" is not being stressed
        acted_on = None
        for ahead in range(pos + 1, min(pos + 4, len(words))):
            if words[ahead] in ACT_ON_FILLER:
                continue
            acted_on = words[ahead]
            break
        if acted_on not in ("me", "us"):
            continue                   # "...is tiring my mum out": her state, not the speaker's
        return feeling
    return None


def _skeleton(word):
    """A word with its vowels taken out: the letters that carry how it sounds."""
    return "".join(letter for letter in word.lower()
                   if letter.isalpha() and letter not in "aeiouy")


_SOUND_CUES = None


def _sound_cues():
    """({skeleton: {emotion name: cues}}, every single feeling word) this file knows."""
    global _SOUND_CUES
    if _SOUND_CUES is None:
        index = {}
        known = set()
        for name, cues in EMOTION_WORDS.items():
            for cue in cues:
                if " " in cue:
                    continue
                known.add(cue)
                if len(cue) < 4:
                    continue
                index.setdefault(_skeleton(cue), {}).setdefault(name, []).append(cue)
        _SOUND_CUES = (index, known)
    return _SOUND_CUES


def feeling_by_sound(word):
    """The feeling a word is the sound of, when it is not the feeling's spelling, or None.

    People type "im board" for bored, "im tried" for tired, "im anxty" for anxiety. Each is
    another word or no word, so the misspelling fixer may not touch it - but in the "im" frame
    the word says how the person is, and the vowels are what chat typing loses. Only a word
    that keeps the feeling's consonants, in order and with the same first letter, is read this
    way, and only when one feeling matches: "board" is bored, "im cory" and "im karen" stay
    names because no feeling sounds like them.
    """
    if not isinstance(word, str):
        return None
    low = word.strip().strip(".,!?;:'\"()").lower()
    if len(low) < 4 or not low.isalpha():
        return None
    index, known = _sound_cues()
    if low in known:
        return None      # the feeling as it is spelt: the reading's own rules decide
    if low in lexicon.COMMON_NAMES:
        # A name is not a feeling however it sounds: "im lisa" shares "lose"'s consonants and
        # "im alan" shares "lonely"'s, and both are the second line of a chat ("hi im lisa").
        return None
    matches = index.get(_skeleton(low)) or {}
    found = sorted({name for name, cues in matches.items()
                    if any(cue[:1] == low[:1] for cue in cues)})
    return found[0] if len(found) == 1 else None


# "im board", "i am tried", "i feel anxty": the frame that makes a word the person's state.
FEELING_SOUND_FRAME = re.compile(r"\b(?:im|i am|i feel|i felt)\s+(?!not\b|never\b|no\b)"
                                 r"(?:(?:so|really|very|totally|proper|dead|well|quite|pretty|"
                                 r"slightly|kinda|kind of|a bit|a little|a tad)\s+)*"
                                 r"([a-z]{4,})\b")


# What may follow a feeling word: a complement ("bored of this", "anxious about it"), a
# degree with nothing after it, or the end of the clause. A word that is a thing as well is
# only the feeling when one of these follows - "im board certified", "im board exams" and
# "im board paper" are about a board, and the deck has nobody who is bored certified.
SOUND_FOLLOWS = frozenset("""of at in with about over by again today tonight now already too
    as anymore stiff out""".split())


def _a_feeling_can_end_here(text, end):
    """True when what follows the word lets it be the state rather than the thing."""
    rest = text[end:].lstrip()
    if not rest or rest[0] in ".,!?;:":
        return True
    return rest.split()[0].strip(".,!?;:'\"") in SOUND_FOLLOWS


def _a_period_of_their_own(text, cue):
    """True when the state word describes a day or a week the speaker had.

    "i had a low day", "ive had a low few weeks", "today was a low day": the state stands in
    front of the period, so nothing in front of it is a person. The head of the clause has to be
    the speaker or the day itself, or the period belongs to something else ("the battery was low
    all day") and the state is that thing's.
    """
    for match in re.finditer(r"\b" + re.escape(cue) + r"\b", text):
        after = [word.strip(".,!?;:-|\"'").lower() for word in text[match.end():].split()]
        seen = 0
        while after and seen < 3 and after[0] in OWN_PERIOD_FILLER:
            after.pop(0)
            seen += 1
        if not after or after[0] not in OWN_PERIOD_NOUNS:
            continue
        before = [word.strip(".,!?;:-|\"'()").lower() for word in text[:match.start()].split()]
        for word in reversed(before[-OWN_PERIOD_REACH:]):
            if word in OWN_PERIOD_STOPS:
                break
            if word in OWN_PERIOD_HEADS:
                return True
    return False


# A thing that acts on the speaker is a feeling about the speaker, and the thing is its cause.
# "work is stressing me out", "my mum is doing my head in", "the kids are wearing me out" all read
# as no mood at all: the only feeling word in the line is a verb with the speaker as its object,
# and the cue table wants the word said *of* someone ("im stressed"). So each line was answered
# with its own words read back - "Got it - work is stressing you out." - or with a card about the
# noun instead of the feeling ("my mum is doing my head in" got the anxiety-and-sleep card). The
# verb says which feeling it is, and the subject in front of it is the cause, which is what the
# answer should be asking about.
ACTS_ON_THE_SPEAKER = (
    (r"(?:stress|stresses|stressing|overwhelm|overwhelms|overwhelming|worry|worries|worrying|"
     r"panic|panics|panicking)\s+(?:me\b|my head\b)", "anxious"),
    (r"(?:wear|wears|wearing|wore|tire|tires|tiring|exhaust|exhausts|exhausting|drain|drains|"
     r"draining|kill|kills|killing|knacker|knackers|knackering)\s+me\b", "tired"),
    (r"(?:get|gets|getting|got|bring|brings|bringing|brought)\s+me\s+(?:down|low)\b", "sad"),
    (r"(?:do|does|doing|done)\s+my\s+(?:head|brain|nut|swede)\s+in\b", "anxious"),
    (r"(?:drive|drives|driving|drove)\s+me\s+(?:mad|crazy|nuts|mental|insane|"
     r"up the wall|round the bend|round the twist)\b", "angry"),
    (r"(?:annoy|annoys|annoying|irritate|irritates|irritating|frustrate|frustrates|frustrating|"
     r"bug|bugs|bugging|wind|winds|winding)\s+me\s+up\b", "angry"),
)


# ... and not when the person is joking about it: "this is killing me lol" is a laugh, and a line
# that laughs at itself is not asking for a feeling answer.
LAUGH_AT_THE_END = re.compile(r"\b(?:lol|lmao|haha|hah|heh|jk|joking|kidding|honestly)\b[\s.!?]*$")


# A part of the body is the subject of its own line and has its own card: "my back is killing me"
# is a back, and "my feet are killing me" is a long day standing up. The verb is the same as in
# "the commute is killing me", so what is in front of it decides.
A_BODY_SUBJECT = frozenset(
    "back neck knee knees feet foot leg legs arm arms hand hands shoulder shoulders hip hips "
    "ankle ankles wrist wrists elbow elbows joint joints muscle muscles tooth teeth jaw ear ears "
    "eye eyes head stomach chest ribs rib side spine sciatica period periods boob boobs tit tits "
    "throat shoulder-blade".split())


def _acts_on_the_speaker(text):
    """The feeling a line about something acting on the speaker carries, or None."""
    if LAUGH_AT_THE_END.search(text):
        return None
    for pattern, name in ACTS_ON_THE_SPEAKER:
        for match in re.finditer(r"\b(?:" + pattern + ")", text):
            before = text[:match.start()].split()[-2:]
            if any(word.strip(".,!?;:'\"") in A_BODY_SUBJECT for word in before):
                continue
            return name
    return None


# "im getting worse" is the same state as "im worse", and only the first person is read this way:
# "its getting worse" about a leak, a cough or the traffic names something else's state.
GETTING_WORSE = re.compile(r"\b(i'?m|i am)\s+getting\s+(worse)\b", re.I)


# "im no better" is the comparison said the other way round, and it is the one people use about a
# medicine that has not worked. "better" alone is not read as a state - "im a bit better" is the
# good news, and the pool that answers it is the one that says keep going - so only the denial is
# folded into the comparison the reading already knows.
NO_BETTER = re.compile(r"\bno\s+better\b", re.I)


# "worse off" and "no better off" are about money or circumstances, not the body: "we re no better
# off than last year" is a year's wages, and the comparison has to be taken out of the line before
# anything reads it as a state.
BETTER_OFF = re.compile(r"\b(?:no\s+)?better\s+off\b|\bworse\s+off\b", re.I)


# A good word the line says has been missing is not that mood. "i cant remember the last time i
# felt happy" names "happy" with no negator near enough for `denied` to see (the polarity came out
# 1), so the mood was read as happy and the happy pool answered "That's a good place to be. Enjoy
# it." to somebody saying they cannot remember being happy. What the line says is how long it has
# been, so the frame is read as the low it is: the memory denied ("cant remember the last time"),
# or the feeling said not to have been there ("havent felt happy in weeks").
GOOD_WORD_MISSING = re.compile(
    r"\b(?:cant|can\s*not|couldnt|could\s*not|dont|do\s*not|didnt|did\s*not|havent|have\s*not|"
    r"hasnt|has\s*not|hadnt|had\s*not|never|not)\b[^.?!;]{0,40}?"
    r"\b(?:remember|remembered|felt|feel|feeling|been|be|was|were)\b", re.I)


# A comparison is the other way round - "i havent felt this happy in years" and "i cant remember
# being this happy" both say they are happy now - so "this", "so", "that" or "as" in front of the
# good word keeps it.
GOOD_WORD_COMPARED = re.compile(
    r"\b(?:this|so|that|as)\s+(?:happy|glad|pleased|excited|proud|relieved|good|great|well|"
    r"content|calm|fine)\b", re.I)
