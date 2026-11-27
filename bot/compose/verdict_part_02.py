"""Part 2 of 7 of the module, split out of `verdict`.

Everything here is re-exported from `verdict`, so callers import it from there as before.
"""
import re

from .verdict_part_01 import (
    DO_LINES, NO_LINES, CONDITION_LINES, NOTHING_WARNED_LINES,
)


# The state, and the family of sentence that answers it. "fed" is here for "fed up", which is the
# same line said the other way round.
FEELING_FAMILY = {
    "tired": "tired", "exhausted": "tired", "drained": "tired", "wiped": "tired",
    "knackered": "tired", "shattered": "tired", "worn": "tired", "burnt": "tired",
    "burnout": "tired",
    "anxious": "anxious", "anxiety": "anxious", "worried": "anxious", "stressed": "anxious",
    "stress": "anxious",
    "crying": "crying", "cry": "crying", "tearful": "crying",
    "low": "flat", "down": "flat", "flat": "flat", "miserable": "flat", "unhappy": "flat",
    "sad": "flat", "numb": "flat", "lonely": "flat", "hopeless": "flat",
    "overwhelmed": "heavy", "struggling": "heavy", "fed": "heavy", "useless": "heavy",
    "worthless": "heavy", "pointless": "heavy",
}


FEELING_DOUBT_LINES = {
    "tired": (
        "That is what running on empty feels like, and it is not a fault in you. Sleep and food "
        "come first - tiredness from a hard stretch lifts once those are back.",
        "Nothing about it is a sign something is broken. Tired like that is what carrying a lot "
        "does to a person, and it comes back up slowly rather than all at once.",
        "Being this worn out is ordinary for the run you have had, and it is allowed to be this "
        "heavy. If a couple of weeks pass with no better days in them, that is worth saying to a "
        "GP.",
    ),
    "anxious": (
        "That is worry doing its work, and it is not a sign something is wrong with you. It eases "
        "once the thing on your mind eases; until then, sleep and eating are the two worth "
        "guarding.",
        "Nothing about it is unusual, and nothing to be ashamed of. The part worth watching is "
        "whether it is there all day every day - weeks of that is worth saying to a GP.",
    ),
    "crying": (
        "That is tiredness and grief coming out of you, and it is not a weakness. It comes in "
        "waves, and the waves get further apart - they do not keep to a timetable.",
        "Nothing about crying like that is a sign something is broken. It usually eases within a "
        "few weeks of the thing that set it off; a month of it is worth saying to a GP.",
    ),
    "flat": (
        "That is what a low stretch does to a person, and it is not a fault in you. It lifts, "
        "slowly and not in a straight line - watch the good hours rather than the bad ones.",
        "Nothing there is a sign something is broken. Feeling flat is what a heavy few months "
        "looks like from the inside, and the way back is usually small and boring: sleep, food, "
        "one person who knows.",
        "That is ordinary for the run you have had, and it is allowed to be this heavy. If a "
        "couple of weeks go by with no better hours in them, that is the point to say it to a "
        "GP.",
    ),
    "heavy": (
        "That is a lot to carry, and it is not a measure of you. If a couple of weeks pass with "
        "no better hours in them, say it to a GP - that is what they are there for.",
        "Nothing there is a weakness. What you are describing is what too much for too long feels "
        "like, and the first thing that helps is usually a shorter list rather than more effort.",
    ),
}


# Which doubt was asked. "is that bad" asks whether the thing matters, and the pools above
# answer that. "is it normal" asks something else: whether the thing is the customary one. The
# answer above is read the same way for both, so the pools above said the opposite of it over a
# normality ask - "... the causes behind it, and how to fix it for most people who snore ..."
# then "is it normal" came back "No - the part you asked about is the harmless kind", and the
# person hears that their snoring is not normal (snappy-net, #3872 review). Nothing in the
# reading changes: the pool follows the doubt that was actually asked.
ASKS_NORMAL = re.compile(
    r"\b(?:normal|abnormal|unusual|usual|typical|common|ordinary|standard)\b", re.I)


# "is that ok" asks for permission, and its answer is "yes" - the same reading, told the other way
# round. The severity pools say "no" in words ("That one is the ordinary kind, so no", "No - the
# part you asked about is the harmless kind"), which is the verdict for "is that bad" and the
# opposite of the one asked for here: over a harmless answer, "my knee clicks when i go upstairs"
# / "is that ok" was told "No - the part you asked about is the harmless kind". Nothing in the
# reading changes; the pool follows the doubt that was actually asked, as it does for the
# normality ask above.
ASKS_OK = re.compile(r"\b(?:ok|okay|alright|all\s+right|acceptable|fine|safe)\b", re.I)


OK_LINES = (
    "Nothing in that sounded like a warning sign \u2014 so yes, it is fine. What would change it "
    "is the thing itself changing: getting worse, or not settling.",
    "Yes \u2014 that one is the ordinary kind. Watch it rather than worry about it: if it is still "
    "the same in a week or two, or it gets worse, get someone to look at it.",
    "Yes \u2014 the part you asked about is the harmless kind. What to keep an eye on is change "
    "rather than the thing itself.",
)


ORDINARY_NORMAL = (
    "Yes, that is the usual thing - what to keep an eye on is change rather than the thing "
    "itself.",
    "Yes, that is normal for most people. Watch it rather than worry about it: if it is the "
    "same in a week or two, or it gets worse, get someone to look at it.",
    "Yes, that is the ordinary thing, and it stays ordinary unless it changes. Getting worse, "
    "or not settling, is what would make it worth someone's look.",
)


CARE_NORMAL = (
    "Yes - common or not, that one is worth getting looked at properly. Say what you told me "
    "here when you do.",
    "Yes. That one needs a look rather than watching, and whether it is the usual thing is "
    "exactly what the look settles. Say what you told me here when you go.",
)


# The honest answer when the bot cannot say how usual a thing is - and only then. Over a card that
# already said ("It is common at four and still common at nine") the line argues with the answer
# the person has just read, and over a card that put a time on its referral ("ring the vet today")
# it hedges about a cheap check that the card said to make now (hearty-emu, airy-moss, #3872).
CARE_NORMAL_UNKNOWABLE = (
    "I could not call that usual or not from here, and it is one to have looked at: the check "
    "is cheap and it settles the question rather than the guessing.",
)


# A card that told them when: "ring the vet today", "get it seen the same day". The doubt is
# answered by the card's own timing, so the reply says to do it rather than wondering whether the
# thing is usual.
CARE_NOW = re.compile(
    r"\b(?:today|tonight|the same day|same day|straight away|right away|now|urgent|"
    r"within (?:a|one|two|three|\d+) (?:day|days|hour|hours))\b", re.I)


# The same timed card, asked the other doubt. "Yes, that one wants a proper look" answers "should I
# be worried" and means the opposite over "is it normal": a person asking whether a thing is usual
# reads that yes as "yes, it is usual" over the answer that said to have it seen today. So the
# normal-shaped line says the timing and the look, and never answers the usual question it cannot
# answer (shiny-shrew, #3872).
CARE_NOW_NORMAL = (
    "Don't sit on that one - it is a today thing, and whether it is the usual thing is what the "
    "look settles rather than the guessing.",
    "That wants seeing today. Whether it is the ordinary version or not is exactly what the "
    "visit is for, so ring and be seen.",
)


DO_NORMAL = (
    "That is the ordinary thing to do about it, and it is a job rather than a danger: do what I "
    "said and see whether it holds.",
    "Nothing in that is out of the ordinary - it is the everyday job, so do it and see whether "
    "it holds; if it comes back after that, get someone in.",
    "That is the usual way of dealing with it, and it is worth sorting rather than worrying "
    "about - do it and see whether it holds.",
)


CONDITION_NORMAL = (
    "Ordinary on its own, yes - and it stops being usual if {when}. That is the point to act on.",
    "That is the usual case on its own, and it becomes something else if {when}.",
    "Usual up to a point: what would make it something to act on is if {when}.",
)


NOTHING_WARNED_NORMAL = (
    "Yes, that is how it is normally handled. What would matter is a change in it.",
    "Yes, that is the ordinary job, and what would send you to someone is a change in it.",
    "Yes, ordinary - that is the everyday fix for it, and the thing to watch is it getting "
    "worse or not shifting.",
)


YES_LINES = (
    # "the check itself" opened this pool until a person's own chats showed what it did: the pool
    # is picked for any yes, and only an answer that named a test or a scan makes a check the thing
    # to act on. After "ring 111 now" for a baby who has stopped feeding, and after "ring a dentist
    # the same day" for a tooth, it told a worried person the part worth acting on was a check
    # nobody had offered. Acting is what every one of those answers asked for, so that is what the
    # line says, and it no longer names a test, a scan or an examination.
    "Yes — it is worth acting on rather than sitting on. Asking costs very little and it stops "
    "the guessing.",
    "Yes, that one wants a proper look rather than watching it. Get it looked at properly, and "
    "say what you told me here when you do.",
    "Yes. Get it seen to — not an emergency, but not something to sit on either.",
)


# A thing the person owns is not a body, and the pools above talk like one: "watch it rather than
# worry about it: if it's still the same in a week or two", "get it looked at properly". Over a
# knocking boiler that tells a person to leave it alone, and offers them a doctor for a machine
# (modern-cap, #routing 77551). The verdict on a thing is about the job and who does it: the
# everyday reading is "do the job, and if it is still doing it, that is the call", and a call is
# somebody with the trade rather than somebody with a stethoscope.
A_THING_THEY_OWN = re.compile(
    r"\b(?:boilers?|radiators?|central heating|thermostat|washing machine|washer dryer|"
    r"tumble dryer|dishwashers?|fridge|freezer|fridge freezer|ovens?|hob|cooker|microwave|"
    r"kettles?|toaster|hoover|vacuum|lawnmower|mower|strimmer|pressure washer|shower tray|"
    r"showers?|taps?|toilets?|sinks?|drains?|plughole|gutters?|roof|fencing|fence|decking|"
    r"doors?|windows?|locks?|sockets?|fuse board|consumer unit|lights?|"
    r"cars?|vans?|bikes?|bicycles?|motorbike|scooter|tyres?|brakes?|clutch|exhaust|engine|"
    r"laptops?|computers?|pcs?|printers?|phones?|tablets?|monitors?)\b", re.I)


# The same noun can be the person's own body ("my back", "my skin"), and then the pools above are
# the right ones whichever word sits beside it: "my sink" is a drain, "i feel sick" is not.
A_BODY_WORD = re.compile(
    r"\b(?:skin|rash|itch|itching|eyes?|ears?|throat|chest|stomach|belly|knee|knees|joint|"
    r"joints|hips?|shoulders?|neck|foot|feet|hands?|arms?|legs?|tooth|teeth|gums?|breath|"
    # A "back door", a "back garden" and a "back wall" are not the person's back.
    r"back(?! (?:door|doors|garden|gate|wall|bed|room|bit|passage))|"
    r"breathing|breathless|cough|poo|wee|blood|fever|temperature|hearing|sight|head|"
    r"headaches?|migraine)\b", re.I)


THING_ORDINARY = (
    "It is the everyday thing rather than a fault, and the job I described is what settles it. If "
    "it is still doing it after that, or it comes back, that is when it wants somebody who does "
    "this for a living.",
    "Nothing in that is a fault on its own: it is the ordinary thing with a job attached. Do the "
    "job, and if the noise or the mark is still there afterwards, get somebody in.",
    "That is the usual reason for it, and the fix I gave is the check. Do that first - if it "
    "holds, it was the everyday thing, and if it does not, that is a call to somebody with the "
    "trade.",
)


THING_CALL = (
    "Yes - that one is for somebody who does this for a living rather than a watch-and-see. "
    "Describe it as you did here when you book them in, and hold off using it until they have "
    "looked.",
    "Yes, get that looked at properly. It is a call to a trade rather than something to sit on, "
    "and the sooner they see it the less it usually costs.",
    "Yes. That is a job for somebody with the right tools, not a wait-and-see.",
)


# A safety answer has already said what to do, so the verdict question after it has one answer:
# yes. "my cat is having trouble breathing" / "is that serious" was the search hedge, because the
# verdict reading only ever reads a knowledge answer and a safety line is not one. The lines point
# back at the call without quoting it, because the call is whatever the answer named - a vet, 111,
# a crisis line - and they stay true for all of them.
# The last thing the bot said was not an answer from the knowledge base but a warm line about the
# person's own day, and the bare verdict ask arrives on top of it: "i cant be bothered to leave
# the house" / "is that bad" was answered "Alright then - good luck with it". There is no answer
# to read a verdict out of, so this is a floor rather than a reading: it says the honest thing
# about a habit or a mood - not a fault, worth looking at - and asks the question a friend asks.
# True whatever the subject was, because the composer does not know what it was.
BACKSTOP_LINES = (
    "Not bad, no. What would make it matter is how long it has been going on and what it is "
    "costing you — how do those two look?",
    "I wouldn't call it bad. It is worth a proper look rather than a shrug, though: what does it "
    "take out of your week?",
    "Not a fault, and nothing to be ashamed of. The question worth asking is whether it has a "
    "hold on your days rather than whether it is bad.",
)


# The care words that name somebody who looks at a person rather than a thing. "get someone in"
# is a trade coming to the house, so an answer whose opening names one of these is a referral and
# not a job: the boiler answer's Gas Safe engineer keeps the job pool, and a child referred to a
# speech therapist does not.
PEOPLE_CARE = ("gp", "doctor", "nurse", "midwife", "health visitor", "physio", "therapist",
               "pharmacist", "optician", "dentist", "vet", "111", "referral", "hospital",
               "a&e", "urgent care", "out of hours", "specialist", "clinic")


# The same floor when the line above ruled on nothing: "I'm listening - say more if it helps"
# is not an answer, and a floor that says "I wouldn't call it bad" over it rules on a subject it
# has not read. These ask the question a friend asks and claim nothing about the thing.
FLOOR_LINES = (
    "How long has it been going on, and what does it cost you day to day?",
    "How long has it been like that, and is it getting in the way of your week?",
    "What would you like to do about it, and how long has it been like that?",
)


# And the floor for a line that is about something the person has rather than does ("i have a
# cough", "i have a lump in my breast", "i have blood in my poo"). It may not carry the severity
# of the two pools above - what somebody has can be a lump or a dog - so it asks and promises a
# hearing, which is more than "Alright then - good luck with it" without ruling on a subject the
# composer has not read.
NEUTRAL_ASK_LINES = (
    "Say a bit more: how long has it been like that, and what does it cost you day to day?",
    "How long has it been going on, and what would you like to do about it?",
    "Tell me more and I will help you think it through: how long, and how is it affecting you?",
)


# A bare doubt after a plan, a choice or a wish the person brought is not a nod and not a symptom,
# and neither pool above fits it: "im going to rome" / "is that ok", "i want to book a holiday" /
# "is that ok", "should i accept a counter offer" / "is that ok" and "we're thinking of getting a
# rescue greyhound" / "is that ok" were all answered "Alright then - good luck with it." The doubt
# path had nothing to rule on, so it stood aside, and the ack pool read "ok" as a nod. There is
# still nothing to rule on - the plan is theirs - but a shrug says the conversation is over, and
# what the person is checking is that wanting it is allowed. So these name the thing as a thing
# they want and ask for the part that is being weighed.
A_PLAN_DOUBT_LINES = (
    "Nothing in that sounds wrong: it is a plan rather than a fault to check. Which part of it are "
    "you unsure about?",
    "Say which part you are unsure about and we can weigh it up together.",
    "That is yours to decide rather than something to worry about. What is the bit you keep going "
    "over?",
)


# "i tried that and it helped" / "is that bad" is not a symptom: the thing worked, and the next
# thing to say is to keep it up. A floor over it invented a worry ("That is worth a proper look").
# A named professional who is not an emergency: a dentist, an optician, a physio, a vet, a
# pharmacist. The answer named who, so the verdict is "yes, get it seen", not "ring tonight".
SOON_LINES = (
    "Yes, that wants looking at - the answer named who, so book it rather than wait for it to "
    "settle.",
    "It is worth having it seen to, and that answer already said by whom. Get that booked, and "
    "say how long it has been going on when you do.",
    "Not an emergency by the sound of it, but not something to leave either: the person named in "
    "that answer is the one to see.",
)


HELPED_LINES = (
    "Then it is doing its job - keep it up and give it a few more days before you judge it.",
    "Good: that is the thing that worked, so stay with it. The point to get someone to look is if "
    "it stops helping.",
    "That is the answer then. Keep doing it, and tell me if it stops working.",
)


# The asks the knowledge base's own hedge answers better than this file can: "should i be
# worried" is not a verdict about the bot's last line, it is a request for the health hedge
# ("a GP, a pharmacist or 111 will tell you"), and the floor took that turn away from it.
WORRIED_ASK = re.compile(
    r"^(?:and |so )?should i (?:be )?(?:worried|worry|worrying|concerned|see someone|see a doctor"
    r"|do anything|do something|get it checked|be checked|call someone|ring someone)(?: then"
    r"| though)?$")


# A thing that helped, in the person's own words, before the doubt ask.
HELPED = re.compile(
    r"\b(?:(?:that|it|this) (?:has )?(?:helped|worked|did the trick|did help|is helping"
    r"|is working)|both worked|they worked|it worked out|(?:much )?better (?:now|today)"
    r"|(?:its|it is) (?:helping|working)|on the mend)\b")


YES_SAID_LINES = (
    "Yes - that is why the call is the thing to do now rather than something to wait on. Do that "
    "first, and tell me what they say.",
    "Yes it is, and that is what the call is for. Make it now rather than tomorrow, and we can go "
    "through the rest once you have.",
    "Yes - ringing is not an overreaction here, it is the whole point of it. Do that first and "
    "come back to me after.",
    "Yes. Somebody needs to hear this today rather than next week, so make the call and then tell "
    "me what they say.",
)


# An answer that tells the person to stop doing something is standing in for a warning, wherever
# in the answer it comes: the "yes, this wants a proper look" line is the verdict for it, and
# "that one is the ordinary kind, so no" is never it.
# An answer that opens by telling the person to get rid of the thing is the strongest verdict in
# the knowledge base: "bin it, I'm afraid: cooked chicken left out for more than 2 hours isn't
# safe to eat". A bare "is that bad" on top of it was answered "Alright then - good luck with it"
# - the bot handing back the door on the one answer where a person is asking to be talked out of
# a risk. The yes is the answer's own instruction said back, so the pool cannot disagree with it,
# and the action is quoted from the line rather than named by the pool.
THROW_AWAY = re.compile(
    r"\b(?:bin\s+(?:it|them|that)|throw\s+(?:it|them|that)\s+(?:away|out)|"
    r"chuck\s+(?:it|them|that)(?!\s+(?:\w+\s+){0,2}(?:in|on|into|with|to)\b)|"
    r"(?:get|getting)\s+rid\s+of\s+(?:it|them|that))\b", re.I)


# The throw-away is not the instruction when the answer says *not* to do it - "don't flush them
# and don't bin them" over old medicines read back as "Bin them" - and it is not the instruction
# either when it is one option in a list: "sell, donate or bin it now".
NOT_TOLD_TO = re.compile(r"(?:\bdon'?t|\bdo not|\bnever|\bnot|\brather than|\binstead of|\bbefore you)\s*$", re.I)


ONE_OPTION = re.compile(r"\b(?:or|and|rather than|instead of)\s*$", re.I)


# The sentence opens by naming a test rather than a state of the thing, so the answer has not
# said the person's milk is off - only what to do if it ever is.
TESTING = re.compile(r"^[\s\"'(\u2018\u201c]*(?:if|unless|once|whenever|when|any ?time|should|whether)\b", re.I)


THROW_AWAY_LINES = (
    "{Action} \u2014 it is not worth the risk, and it is not a close call.",
    "Yes, really. {Action}. This is the one where guessing costs the most.",
    "{Action}, and do not talk yourself out of it: nothing you can see or smell makes it safe.",
)


# The same answer written as a test - "if milk smells or tastes sour, bin it". The person has not
# said the milk is off, so the answer is not a verdict on their milk; it is the test that settles
# it, and the doubt on top of it is "is it bad if I get that far". The action stays, said as the
# outcome of the test rather than as a ruling on today's carton.
TEST_LINES = (
    "{Action} once it has turned - that is the whole test, and I would not taste it to check.",
    "You do not need me to judge it. {Action} once it has turned, and that is the whole test.",
    "{Action} if it has actually turned. The test is the answer, and the thing itself is the judge.",
)


# An answer that says outright that the thing itself is not safe has given the verdict in the
# sentence, and none of the readings below can see it: they read a referral, a job to do, a
# danger word or an ordinary word, and "There is no safe number of drinks before driving" is none
# of those. So `im gonna drive home after a few pints` / `is that ok` fell all the way through to
# the acknowledgement floor and answered "Alright then - good luck with it." over a straight no.
# The negative half is read here, before the care words, because an answer can hold both a no and
# a referral and it is the no that was asked about.
STATED_NO = re.compile(
    r"\bthere (?:is|are) no safe (?:number|amount|level|dose|limit|quantity|way)\b"
    r"|\bno amount of .{1,40} (?:is|was) safe\b"
    r"|\bnothing about .{1,40} (?:is|makes it) safe\b"
    r"|\bis not safe to (?:eat|drink|drive|take|use|give|leave|keep)\b"
    r"|\bare not safe to (?:eat|drink|take|use|give)\b"
    r"|\bnone of (?:it|them|these) is safe\b"
    r"|\byou cannot make .{1,40} safe\b",
    re.I)


NO_STATED_LINES = (
    "No \u2014 that is the answer's own line: {no} There is nothing in it for you to weigh up.",
    "That one is a no, and the answer said it plainly: {no} What to do instead is in the rest of "
    "what I said.",
    "No. {no} That is the whole of it, so it is not a thing for you to judge.",
    "No, and not a close call. {no}",
)


# The other half of the same reading: an answer that says the amount is enough. "is that enough"
# asks about a quantity and not about how bad a thing is, so none of the pools below can read it,
# and the acknowledgement floor took the turn. The answer's own sentence is handed back.
ENOUGH_ASK = re.compile(
    r"^(?:and |so )?(?:is|was|are|were) (?:that|this|it|all of that|all that)"
    r"(?: (?:really|actually|about|roughly))? enough(?: then| though)?$", re.I)


STATED_ENOUGH = re.compile(
    r"\bis (?:definitely |probably |easily |more than |plenty )?enough\b"
    r"|\bis plenty\b|\bmore than enough\b|\bthat will do\b|\bthat does it\b", re.I)


ENOUGH_STATED_LINES = (
    "Yes \u2014 {yes} That is the amount, and the rest of what I said is what makes it work.",
    "Yes: {yes} Nothing in the answer asks for more than that.",
    "It covers it as it stands. {yes}",
    "Yes, on the answer's own figures. {yes}",
)


STOP_DOING = ("stop driving", "don't drive", "dont drive", "don't eat", "dont eat", "don't use it",
              "dont use it", "don't touch", "dont touch", "don't drink", "dont drink",
              "leave the building", "get everyone away", "stop if it is safe")


# An answer that names the harm is a warning, wherever in it the "usually" sits. "can i give my
# cat ibuprofen" is answered "Never give a dog or cat human painkillers ... a cat can die from a
# single paracetamol ... ring them and they will usually ...", and the only cue the reading above
# found was that last "usually", so the verdict was "that one is the ordinary kind, so no" about
# a cat that can die: an answer this plain cannot be read as reassurance.
DANGER = ("dangerous", "toxic", "poisonous", "poisoning", "can die", "could die", "may die",
          "can kill", "could kill", "fatal", "harmful", "not safe", "unsafe", "an emergency",
          "never give", "never use", "never take", "never leave")


# "not dangerous", "harmless and not toxic" and "isn't poisonous" are the reassuring half of a
# danger word, so the word in front of it decides which one this is.
NEGATED = re.compile(r"(?:\bnot|\bno|n't|\bnever|\bnon)[ -]\w*[ -]?$")


# Said back when the same question comes twice: the second ask wants the answer again, plainly,
# not a fresh sentence that sounds like a different verdict.
AGAIN = (
    "Same answer as a moment ago: nothing in what I said was a warning sign. It's the change "
    "to watch for, not the thing itself.",
    "Still no. If it would help, tell me what's actually worrying you about it and I'll be "
    "straight with you.",
)


# The same reading, for the two things a person asks *after* a yes/no verdict, and just as
# often after the answer itself: "what should i do", and "should i see someone". Both are
# answered from the advice already given, because the knowledge answer that prompted them
# carries the steps and the condition in its own words.
# A filler word in front of the ask is not a subject of its own: "honestly what do i do" after
# the drain answer is the same request for the first step as "what do i do", and it was read as
# a line naming its own thing, so the person got the bare offer ("say a bit about what is in
# front of you") one turn after being told what to do. `topics.STOPWORDS` keeps these words out
# of the subject, so the lead only has to stop hiding the ask behind them; the ask itself has to
# be exactly the ask, so "actually the boiler is losing pressure" is not a step request.
# People put the filler where it falls in the sentence, not only at the front: "what can i
# *actually* do about it" and "what should i *really* do" are the same ask, and the reader below
# matched from the first word, so with the filler inside the ask neither was its line at all -
# the person got the answer above handed back with "Same as before:" in front of it, which reads
# like a restatement of the problem rather than a first move. So the filler is allowed wherever
# it lands, and what is left when it is taken out still has to be exactly the ask.
_FILLER = (r"(?:(?:and|so|ok|okay|but|well|right|honestly|actually|basically|literally|simply|"
           r"truly|really|just) )")


_LEAD_FILLER = _FILLER + r"*"


_FILL = _FILLER + r"?"


STEP = re.compile(
    r"^(?:" + _LEAD_FILLER + r")"
    r"(?:(?:what|which) " + _FILL + r"(?:should|do|can) " + _FILL
    + r"i " + _FILL + r"do(?: now| next| first| about it)?"
    r"(?: then)?$"
    r"|what " + _FILL + r"now$"
    r"|what " + _FILL + r"(?:do|should) " + _FILL + r"i " + _FILL
    + r"(?:try|do) " + _FILL + r"(?:first|next)$"
    r"|how " + _FILL + r"do " + _FILL + r"i " + _FILL
    + r"(?:fix|sort|deal with) " + _FILL + r"(?:it|that|this)$"
    r"|what " + _FILL + r"(?:should|do|can|could) " + _FILL + r"i " + _FILL
    + r"(?:put|use|apply|try) " + _FILL + r"(?:on|to|for) " + _FILL
    + r"(?:it|that|this)(?: then)?$)"
)


# The same ask when it is about speaking up: "should i say something", "shall i mention it",
# "do you think i should bring it up" want the step the last answer already gave - "Claim it in
# the room, lightly and factually ..." - not a shrug about what is the person's call. Only the
# verbs of saying something to somebody, so "should i give up" is left where it was.
SPEAK_VERBS = (r"(?:say|mention|bring (?:it|that|this|them) up|raise|tell|ask|text|call|"
               r"ring|email|write|speak|talk)")


SPEAK_UP = re.compile(
    r"^(?:and |so )?(?:(?:do you think|do you reckon|d'you reckon) )?"
    r"(?:should|shall|ought) i " + SPEAK_VERBS + r"\b"
    r"|^(?:and |so )?(?:do you think|do you reckon|d'you reckon) i should " + SPEAK_VERBS + r"\b")


# An answer that tells them to ring the emergency services is not advice to quote a step out of.
# "Ring now rather than waiting to be sure: 999 or 911, say where you are and what has happened"
# read as a step is "Ring now rather than waiting to be sure" - the colon took the number and the
# sentence about what to say with it - and the step line then put it back with an order on the
# end of it ("before you do anything else I mentioned") to somebody who has just been told to
# ring for an ambulance. The number is the instruction, so an answer that *opens* on one keeps the
# turn itself; a step ask after it is answered by whatever reads an emergency, not by a fragment.
# Only an opening: an ordinary answer that ends "and ring 999 straight away if the breathlessness
# comes on suddenly" has its own first move ("rest it, ice it") and that step is still its to give.
EMERGENCY_CALL = re.compile(
    r"\b(?:ring|call|dial|phone|contact)\b[^.!?]{0,60}?\b(?:999|911|112)\b", re.I)


SEE = re.compile(
    r"^(?:and |so )?(?:should|do) i (?:need to )?(?:see|call|ring|go to) (?:a |the |my )?"
    r"(?:someone|somebody|doctor|gp|vet|dentist|engineer|plumber|doctor about it)(?: then)?$"
    r"|^(?:and |so )?do i need (?:to see )?(?:someone|a doctor|the doctor|the vet)(?: then)?$"
    r"|^(?:and |so )?is it worth (?:seeing|going to|ringing) (?:someone|a doctor|the vet)"
    r"(?: then)?$"
)


# A how-to ask about the thing in hand names the doing and no object: "how do i prepare", "how do
# i get ready for it", "how should i practise". The thing being prepared for, practised or started
# is the one in the answer above, so the answer already holds the move and the step out of it is
# the reply. Typed on main `eae7434d`:
#
#     im nervous about a presentation
#       Rehearse the first sixty seconds out loud until you could say it half asleep ...
#     its on friday
#       Nothing separate for friday - it is the same advice: Rehearse the first sixty seconds ...
#     how do i prepare
#       I'm not sure about that one, sorry - I'd rather not guess. A quick search online will ...
#
# The person has been told how to prepare twice and asked what more there is to it; a search hedge
# is the bot saying it never had an answer. The doing takes no object, which is what separates it
# from a how-to question for the base: "how do i cook rice" names the rice, and the knowledge base
# answers that one, while "how do i cook" with the dinner in hand is this ask.
HOW_TO = re.compile(
    r"^(?:and |so |ok |okay |well )?how (?:do|should|can|would|might|will) i "
    r"(?P<doing>[a-z]+)"
    r"(?P<obj>(?: (?:[a-z]+ ){0,2}(?:it|that|this|them)"
    r"(?: (?:on (?:friday|monday|tuesday|wednesday|thursday|saturday|sunday)|then|now|first|"
    r"out|off|down|up|again|properly|safely))?)?)$")


# The doings that mean "the thing in hand" and take no object of their own. A verb of making or
# getting takes one ("how do i cook", "how do i fix"), and those belong to the knowledge base.
DOING_WITH_NO_OBJECT = frozenset("""prepare practise practice rehearse revise study train
warm stretch""".split())


# A doing with a pronoun after it names no thing of its own - "it" can only be the thing in the
# answer above - so the verb does not have to be on any list: "how do i clean it" after "my oven is
# filthy", "how do i unblock it" after "my sink is blocked", "how do i get rid of it", "how do i
# descale it". The verb list only decides the case with no object at all ("how do i cook"), where
# nothing on the line says what is in hand. (tan-needle, #routing 114695.)
KNOWING_DOING = frozenset("""know tell check spot find see say guess recognise recognize""".split())


# A bare plea for tips after the bot has already answered is the same ask as "what should i do":
# "i cant sleep" / "any tips" was answered "Happy to help - tell me what you've got so far and I'll
# add what I can", which asks the person to repeat what the bot had just told them. The subject is
# in the answer above, so the reply is the step out of it, exactly as for "what next". The plea
# comes in several words besides "tips": "any tricks" after the veg answer was still the stock
# "Sure. What have you tried so far? That tells me where to start".
#
# "Ideas" is the same plea and was not in the list: after the answer about a child who will not eat
# vegetables, "any ideas" was answered "That's most of what I know on it - say which part is still
# unclear", which is the bot saying it has nothing while the first thing to do was in the answer a
# line above ("Keep serving one small piece of veg next to something they already like").
# "Suggestions" and "thoughts" are asked in the same breath. A plea that names its own thing ("any
# ideas for dinner") keeps it, so it is still the knowledge base's question.
TIPS_AGAIN = re.compile(
    r"^(?:and |so |ok |okay |well )?(?:(?:any|some|got any|got some|need some|need any|"
    r"want some|more|any more|another|a few|any other)\s+)?"
    r"(?:tips?|advice|pointers?|tricks?|hints?|ideas?|suggestions?|thoughts?)"
    r"(?: (?:at all|then|please|too|now|really|anyway))*$"
)


# The same plea said as one move: "just one thing to start", "where do i start", "what is the
# first thing to do". A person who has just been told the long version and asks for the one thing
# is asking the same question as "any tips", and the answer above holds it. It is a separate
# pattern because the words are a plan, not a plea: "one thing to start" reads as a thing to do,
# so it was acknowledged back ("i need to save money" / "just one thing to start" came back
# "Got it - just one thing to start") instead of being answered from the answer.
# The ask usually comes with a word of feeling in front of the verb - "where do i even start",
# "how do i actually begin" - and the pattern only knew an adverb after it, so the line fell
# through to the one that says the answer over again ("Same as before: ..."), which is the
# repeat STYLE.md forbids. Any of these words in that place is the same ask, and none of them
# changes what is being asked for. (@keen-jasmine's list, from #routing 54143.)
ONE_THING_ADVERB = ("even", "actually", "really", "just", "possibly", "maybe", "instead",
                    "honestly", "normally")


_ONE_THING_ADVERB = r"(?:(?:%s) )?" % "|".join(ONE_THING_ADVERB)


# A follow-up that asks how to do the thing in hand, in the words people use for it: "whats the
# safest way", "whats the best way to fix it", "which is the quickest method". Like a plea for
# tips, it names no subject of its own - the subject is the answer above - so it is a step ask.
# One that does name its own thing ("whats the best way to defrost chicken") is the knowledge
# base's, and the "to <verb> it" tail is only accepted for a verb that takes a pronoun.
# "Cheapest" is deliberately not here: "what is the cheapest way to do it" after an answer about
# tyres wanted prices, and the base gave them ("a budget tyre fitted is about 55 to 80 a corner"),
# while the step handed back was "read the size off the sidewall". A price ask is answered with
# prices; the method asks above are the ones the base could not answer at all.
A_HOW_ASK = re.compile(
    r"^(?:and |so |ok |okay |well )?(?:what|whats|what is|which is|whichs) the "
    r"(?:safest|best|quickest|fastest|easiest|simplest|surest|most reliable|right|"
    r"proper|correct) (?:way|method|bet|option|approach|route)"
    r"(?: (?:to (?:do|fix|sort|handle|treat|clean|stop|get rid of|deal with|go about) "
    r"(?:it|that|this)|to (?:start|begin|try|go about)(?: (?:it|that|this))?"
    r"|of doing (?:it|that|this)|of getting rid of (?:it|that|this)"
    r"|for (?:it|that|this)|here|then|now|at all|please))?$")


ONE_THING = re.compile(
    r"^(?:and |so |ok |okay |well |but )?(?:"
    r"just (?:one|the one|the first|1) (?:thing|step|move|bit)(?: to (?:start|begin|try|do)"
    r"(?: with)?(?: first)?)?"
    r"|(?:one|the one|the first) (?:thing|step|move) (?:to (?:start|begin|try|do)(?: with)?"
    r"(?: first)?|first)"
    r"|(?:what|which) (?:is|would be|should be) the (?:one|first) thing(?: to do)?"
    r"|(?:where|how) (?:do|should) i " + _ONE_THING_ADVERB + r"(?:start|begin)"
    r"(?: with it| with that| here| off)?"
    r"|(?:what|where) do i " + _ONE_THING_ADVERB + r"(?:start|begin)(?: with it| with that)?"
    r")(?: (?:then|please|though|now|really))*$"
)


# The advice is whatever the answer put after its colon or dash, and the condition is the
# "if ..." it fenced the referral with. Neither is invented: both are the answer's own words.
AFTER = re.compile("[:;] | - | — | – ")


# The same breaks with the break kept, for the one place that has to know which one it was: a
# colon is the answer explaining its own instruction, and a dash is a new thought.
SPLIT = re.compile("([:;] | - | — | – )")


# The answer's own opening word when it leads with the second half of a thought it never wrote.
THEN_OPEN = re.compile(r"^(?:and\s+)?then[,]?\s+", re.I)


# "Ask a GP" is the same referral as "see a GP" and the knowledge base writes it that way in
# places: "i cant sleep" ends "If you're worn out all day too, or it has gone on for weeks, ask a
# GP", and the word missing here meant that answer was read as carrying no referral at all, so
# "is that bad" after it got "Alright then — good luck with it". "Ask" is left out of the
# "someone" line on purpose: "ask a friend to help you lift it" is not a referral.
REFER = re.compile(
    r"\b(?:see|ring|call|contact) (?:a |your |the )?(?:gp|doctor|vet|dentist|nurse|someone|"
    r"surgery|physio|physiotherapist|pharmacist|optician|midwife|111|999|engineer|plumber)"
    # A referral is often worded as something to have done, not someone to ring: the pet skin
    # card ends "Have the vet look before the skin is broken", and with no other referral words
    # in it a bare "should i be worried" found no verdict at all and fell to the carry. The same
    # shape covers "get a doctor to look", "have your GP check it".
    r"|\b(?:have|get) (?:a |your |the )?(?:gp|doctor|vet|dentist|nurse|physio|physiotherapist|"
    r"pharmacist|optician|midwife)\s+(?:to\s+)?(?:look|check|see|take a look)\b"
    r"|\bask (?:a |your |the )?(?:gp|doctor|vet|dentist|nurse|physio|physiotherapist|"
    r"pharmacist|optician|midwife)\b"
    # The trade is often named with the qualifier in front of it: "call a Gas Safe engineer",
    # "get a heating engineer out". Without the gap those answers named nobody at all, and the
    # "if it locks out twice" that belongs with the call was left off the verdict. A joining
    # word is not a qualifier, though: "a reason to ring the surgery or 111" names the trade on
    # the far side of an "or", and reading that as the call the answer is about turned a fix
    # with no warning in it into nothing at all ("i have a cough" / "is that bad" went back to
    # "Alright then - good luck with it").
    r"|\b(?:see|ring|call|contact) (?:a |your |the )?(?:(?!and\b|or\b|to\b|for\b|of\b|in\b|on\b"
    r"|at\b|from\b|with\b|that\b|if\b|when\b|it\b)[a-z-]+ ){0,3}(?:gp|doctor|vet|dentist|"
    r"nurse|someone|physio|physiotherapist|pharmacist|optician|midwife|111|999|engineer|plumber)"
    r"|get (?:it|that|this|him|her|them|someone|somebody)? ?(?:looked at|checked|seen)"
    r"|a&e|urgent care|out of hours"
    r"|\b(?:vet|doctor|gp|dentist) (?:visit|job|matter|appointment)\b"
    # The knowledge base also sends someone by taking the thing to a clinician: "If you get them
    # most days, ... take it to a pharmacist or GP" is the referral in the ordinary-headache
    # answer, and read as neither a care cue nor a call it left a frequency ask with the shrug.
    r"|\btake (?:it|this|that|them) (?:to|along to|back to|in to) (?:a |your |the )?"
    r"(?:gp|doctor|pharmacist|nurse|dentist|vet|physio|physiotherapist|optician|midwife)\b"
    r"|\bnot a wait-and-see\b|worth getting (?:it |them )?checked",
    re.I,
)


# An answer that names a clinician has a call in it however it is put: "a week of home readings,
# sitting still, is what a GP wants" sends the person to the same place as "see your GP", and the
# method answer ("there is nothing in it to worry about") must not stand over either. Kept apart
# from REFER because REFER reads the imperative forms a verdict is argued from, and this one only
# asks whether a person to see is named anywhere.
NAMES_A_CLINICIAN = re.compile(
    r"\b(?:gps?|doctors?|nurse|practice nurse|midwife|health visitor|pharmacist|vets?|"
    r"dentist|a&e|minor injuries|walk-in (?:centre|clinic)|urgent care|out of hours|111|999|nhs)\b",
    re.I,
)


# The shape of a referral that only names the appointment, without telling anyone to go.
DECLARATIVE_REFERRAL = re.compile(
    r"\b(?:vet|doctor|gp|dentist) (?:visit|job|matter|appointment)\b|\bnot a wait-and-see\b"
    # "A new lump in the breast should be checked by a GP within a week or two" tells nobody to
    # go: it states the appointment as the answer's judgement, and read as neither an instruction
    # nor a care word the composer called a breast lump "the ordinary kind, so no".
    r"|\b(?:checked|looked at|assessed|seen) by (?:a |your |the )?(?:gp|doctor|nurse|practice"
    r" nurse|physio|physiotherapist|dentist|vet|pharmacist|optician|midwife)\b"
    r"|\bneeds? (?:a |your |the )?(?:gp|doctor|nurse|vet|dentist|physio|pharmacist|optician)\b"
    r"|\bneeds? (?:to be )?(?:seen|checked|looked at)\b"
    # The shapes a care cue is named in without a verb: "worth a GP visit", "a GP appointment",
    # "the 111 line". They are the answer's judgement rather than an instruction, so the same
    # rule applies - in the opening it is the verdict, later it is a warning about that symptom.
    # Read as an instruction, "Pins and needles in the fingers that wake you is worth a GP visit"
    # answered a wrist that is "usually an overused tendon" with "yes, that one wants a proper
    # look".
    r"|\bworth (?:a |an |your |the )?(?:gp|doctor|doctor's|vet|dentist|optician|pharmacist"
    r"|physio\w*|nurse|midwife|health visitor)\b"
    r"|\b(?:gp|doctor's|doctor|vet|dentist|optician|physio\w*|midwife|health visitor)"
    r" appointment\b"
    r"|\b(?:nhs 111|111 line|out of hours service|urgent treatment centre|health visitor)\b",
    re.I,
)


# A step cut off on one of these is half a sentence, and telling someone to do half a sentence
# is worse than saying nothing ("compare the reading on the bill with").
WHEN = frozenset("""about around roughly per couple once twice three four five six seven two
a an every each daily nightly
morning afternoon evening night day week month year hour minute second time times""".split())


HANGING = frozenset((
    "with", "in", "of", "to", "on", "for", "at", "and", "or", "the", "a", "an", "my", "your",
    "its", "it's", "from", "by", "as", "than", "but", "if", "so", "into", "about",
    "between", "among", "through", "under", "over", "without", "within", "against", "across",
    "behind", "beyond", "towards", "toward", "upon", "except", "despite", "unless", "until",
    "whether", "onto", "than",
))


# A sentence the answer opens with a verb is the answer's first instruction.
IMPERATIVES = frozenset((
    "keep", "ease", "ice", "rest", "bleed", "put", "take", "stop", "swap", "use", "ring",
    "call", "check", "top", "wear", "cut", "leave", "unplug", "turn", "sit", "drink", "wrap",
    "raise", "prop", "wash", "rinse", "soak", "cover", "avoid", "try", "start", "do", "give",
    "pick", "choose", "compare", "buy", "order", "fill", "print", "ask", "tell", "move", "set",
    "open", "close", "save", "read", "write", "clean", "clear", "make", "budget", "shop",
    "cool", "reheat", "freeze", "drain", "store", "boil", "bake", "chill",
    "go", "get", "book", "phone", "add", "apply", "hold", "heat", "cook", "remove", "dig",
    "plant", "water", "measure", "log", "email", "text", "fill", "mix", "line", "air",
    # The rest of the verbs an answer opens its first instruction on. The list above grew one
    # answer at a time and stopped at the ones that turned up in the first few domains, so "bathe
    # it with cool water and dry it" (a cut paw) and "rub it with an oil-based cleanser" (ink on
    # the skin) were not read as the answer's first move: the step reader walked on to a later
    # sentence and pointed at the wrong thing, or found nothing and left "what should i do
    # first" unanswered. These are the verbs the knowledge base itself uses to open an
    # instruction, so the list is the base's own vocabulary and not a guess.
    # "sleep" was tried and taken out again: it opens a sentence as a noun as readily as a verb,
    # and the noun sentences are reachable - "Sleep and repetition file it away" (memory), "Sleep,
    # water and an antihistamine" (dark circles), "Sleep is when the brain files the day's
    # memories" - and each was handed back as the first thing to do. A word whose noun is as
    # common as its verb is not a tell. It costs two small steps ("sleep with your head raised",
    # "sleep with the wrist straight"), which is the cheaper side of that trade.
    # "say" and "name" are deliberately absent: those are the verbs of the bot asking the person
    # for a subject ("I'm listening - say more if it helps"), and a greeting is readable here, so
    # reading them as instructions handed that request back as the first thing to do.
    "bathe", "blot", "dab", "sponge", "rub", "wipe", "dry", "pull", "empty", "hang", "lay",
    "press", "find", "look", "run", "work", "change", "split", "pat", "stir", "track",
    "iron", "serve", "roll", "fix", "follow", "build", "replace", "send", "stand", "draw",
    # An answer about something a person is getting ready for opens on one of these, and without
    # them the step out of it was nothing: "Rehearse the first sixty seconds out loud until you
    # could say it half asleep" (a presentation) had no first move to hand back, so "how do i
    # prepare" after it was a search hedge.
    "rehearse", "practise", "practice", "recite",
    "tighten", "blend", "stretch", "skip", "practise", "watch", "learn", "offer", "report",
    "stay", "seal", "trim", "prime", "screw", "weigh", "scrape", "simmer", "roast",
    "grill", "shred", "mash", "chop", "begin", "feed", "place", "switch", "fit", "test",
    "brush", "scrub", "pour", "grate", "slice", "spray", "prune", "repot", "balance", "let",
    "be", "eat",
    # Cleaning, cooking and bedtime, where the word is a verb and not a noun: the mattress
    # answer's step is "Scrape up what you can" and the sleep answer's is "Walk them back every
    # time with the same short line", and with the verb unread the composer walked past the
    # instruction and quoted what came after it instead ("heat sets both the colour and the
    # smell" as the first thing to do), or found no step at all and answered a plea for tips with
    # "that's most of what I know on it". Only words whose noun is rare go in: "sand", "press" and
    # "carry" are also things, and read as an instruction they turn a list of kit into one.
    "scour", "flush", "vacuum", "hoover", "peel", "fold", "loosen",
    # Bedtime again, where the verb is the whole answer. "rock" and "wind" are left out on the
    # same test as "carry": each opens a sentence as a noun ("Wind chill makes it feel colder").
    "walk", "tuck", "settle", "swaddle",
    # The verbs the base opens an instruction on that were still missing. Each one is a sentence
    # the knowledge base itself starts with, so "Pay the debts that keep a roof over your head
    # first" (money), "Pack what you use least first" (moving flat), "Treat how they seem, not the
    # number" (a fever) is read as the step it is. Without them the step reader walked past the
    # instruction to a later
    # sentence, which is how "where do i even start" after the moving answer came back as "do one
    # room an evening" - the last thing in the answer, not the first.
    "treat", "pack", "pay", "photograph", "aim", "melt", "halve", "agree", "shut",
    "sort", "repair", "label", "install", "cancel", "plug", "restart", "reset", "scan", "reply",
    "spend", "bin", "tidy", "sell", "throw", "push", "answer", "mend", "rent",
    # "bring" opens an instruction as often as "put" does ("Bring a pan of water to a bare simmer
    # with a splash of vinegar, stir it into a gentle whirlpool and slide the egg in from a cup"),
    # and with it unread the poached-egg answer had no step at all: "where do i even start" was
    # answered "Everything I know on that one is in the answer above, and none of it is one job to
    # start with" to somebody whose answer opened on the job.
    "bring",
    # "Separate them first and deal with it when everyone is calm" is the children-fighting
    # answer's opening instruction, and with it unread "what do i do" after that answer reached
    # no step at all, so the greeting's ask-back answered: "Tell me what has gone on, even
    # roughly" to the person who had just said what had gone on. Found by reading the knowledge
    # base's own first sentences for the verbs this list does not have; the fifteen others the
    # same scan turned up (sow, brown, lift, complain, whisk, talk, allow, soften, beat, defrost,
    # fry, decide, count, mark) are a wash on the deck's 296 step-ask chats - 2 better, 1 wash,
    # 2 slightly worse - so they are not here.
    "separate",
))


# The step said back with what the answer said next. The lines used to promise a list ("then
# work down the list I gave you") whenever the answer gave more than one thing to do, but there
# was never a list on screen - one answer is not a list, and pointing at one that is not there
# reads as a bot that has lost the thread. The step is the whole of what a friend says next, so
# the line says that and stops.
# An answer can also give its move as a list without writing one as an instruction ("The things
# that work: same wake-up time every day, no caffeine after early afternoon"), and then the item
# is quoted as it was written, so the line around it must read without a verb in the step.
LIST_STEP_LINES = (
    "Start with the first thing on that list: {step}.",
    "The first one on that list: {step}.",
)


# The step and nothing else. Each of these used to end by pointing at the rest of the answer
# ("the rest of what I said follows from that", "the rest in the order I gave them"), which tells
# somebody who asked what to do first that there is more without giving it: the rest is on the
# screen a line above, and a friend answering "where do i start" says the step and stops.
STEP_LINES = (
    "{Step} first.",
    "{Step} - that is the first move.",
    "{Step}, before anything else.",
)


# The answer explained its own step after a colon ("Turn it off and keep it off: do not charge
# it"), and that explanation is the part a friend would say, so it is quoted whole and the line
# only introduces it. A template that ends on "first" cannot take it: the colon has already put
# the instruction first.
STEP_DETAIL_LINES = (
    "{Step}. That is the first move.",
    "{Step}. Start there.",
    "{Step}. Do that before anything else.",
)


# A step that already puts itself first does not want another "first" bolted on: the sink answer
# opens "Start with a plunger over the plughole with a little water in the bowl", and the line
# above made it ".. in the bowl first, then work down the list", which reads as a second first.
FIRST_ITSELF = re.compile(r"\b(?:start|begin|first)\b", re.I)


STEP_ALREADY_FIRST_LINES = (
    "{Step}. Nothing else before it.",
    "{Step}, and only that to begin with.",
    "{Step}, in that order.",
)


# A sentence that opens on a subject pronoun and runs on is the answer explaining something, not
# giving a step. "They take oxygen out of the water instead of the air: water goes in at the mouth,
# passes over the gills and the gills pull the oxygen out" describes how a fish breathes, and the
# piece after its colon, read on its own, is the instruction "Water goes in at the mouth" - which
# is what a person asking what to do about a goldfish on the bottom of the tank was told to do.
# The tell is the subject in front of the verb: an instruction has no subject, so a verb-shaped
# word that has one is the sentence's subject and not an order ("water" is what you do to a
# plant). A short piece in front of a colon is still a heading ("That's the one: split your time
# in three"), so only a piece too long to be one makes the sentence an explanation.
SUBJECT_OPEN = re.compile(r"^(?:they|it|it's|its|he|he's|she|she's|this|that|that's|these|those"
                          r"|there|there's|we|we're)\b", re.I)


EXPLANATION_WORDS = 5


def _is_an_explanation(sentence):
    """True for a sentence that says how something is, and so holds no step of its own."""
    text = sentence.strip()
    if not SUBJECT_OPEN.match(text):
        return False
    head = re.split(r":|,|;| - | \u2014 ", text, 1)[0]
    return len(head.split()) > EXPLANATION_WORDS


# The same answer, when it gave one thing to do and nothing after it: "work down the list I gave
# you" points at a list that is not there, and the person is owed the one step plainly.
STEP_ONE_LINES = (
    "{Step}, and take it from there.",
    "{Step}. That is the one to do today; the rest is waiting to see whether it shifts.",
    "{Step} - start with that, and tell me how it goes.",
)


# The step asked for a second time, when the answer above is where it already was given. Quoting
# it back says the same sentence twice, one turn apart: "Keep it plain and separate: one new food
# next to one they already eat" was the answer, and the next ask got the same words again with
# "That is the first move" on the end, which is the one thing STYLE.md forbids outright. What is
# left to say honestly is that the step has not changed - so the line says that and adds nothing.
STEP_KEPT_LINES = (
    "Still the same move, and nothing to add to it: it is small, and it is the one that counts today.",
    "That step stands - it is a thing to keep doing rather than a second thing to start.",
    "Nothing new from me on it. Do the first thing as I said it, and tell me how it goes.",
)


# A plea for tips is the one ask where the answer above still has something in it the person has
# not been handed: the step is the sentence they have just read, and the sentence after it is the
# part a friend picks out ("Roasting carrots or broccoli in a little oil makes them sweeter, and a
# dip to dunk turns it into a game"). Handing that over is news; handing the step back is the
# opening of the answer said a turn later.
ALSO_LINES = (
    "There is more in what I said: {other}",
    "One more from that answer: {other}",
    "The other half of it: {other}",
)


# A sentence of the answer that asks the person something is not the tip of the answer: "Tell me
# what is in the fridge and I will pick properly" is the bot's own question, and quoting it under
# "any tips" asks the person to answer what they have just been asked.
ASKS_THEM = re.compile(r"\b(?:tell me|let me know|say which|what have you|how ready)\b", re.I)


# The ask narrowed to one move on purpose ("just one thing to start", "where do i start"): the
# person already has the long answer and wants the one thing out of it, so the line hands that one
# thing over instead of pointing at the rest, and it reads the same whether the step is short or a
# whole sentence - which is why it is chosen before the pools that read the step's own shape.
ONE_TURN_LINES = (
    "Just this: {Step}.",
    "The one thing: {Step}.",
    "Start with this: {Step}.",
    "Just the one, then: {Step}.",
)


# The same ask when the step already orders itself ("Start with run-walk: one minute of easy
# jogging") or carries its own explanation after a colon: a line that opens "Just this:" in front
# of either puts two starts on the same sentence, so these hand the step over as it stands.
ONE_TURN_PLAIN_LINES = (
    "{Step}. That is the one I would start with.",
    "{Step}. Just that one, and the rest can wait.",
    "{Step} - the one to do today, and the rest will keep.",
)


# The one thing was asked for and the answer above wrote no move at all, so there is nothing to
# hand over and no list to point at: the answer was the whole of it, and the reply says so rather
# than reading the ask back as a fact it has noted.
ALL_OF_IT_LINES = (
    "That answer is the whole of what I have on it, and there is no single first move in it: tell "
    "me which bit you want and I will take that one further.",
    "Everything I know on that one is in the answer above, and none of it is one job to start "
    "with. Say which part matters most and I will come at it from there.",
)


# The bot's last line was its own question, and the person answered it with a bare ask instead.
# Quoting that question as a step is what this composer used to do ("Do you want to tell me what
# has made it like that?, and take it from there"), and there is no instruction in it to quote,
# so what is left is to hand the question back kindly: the offer it made still stands.
QUESTION_BACK_LINES = (
    "Nothing to do on my side, honestly - whatever comes to mind about it first is the useful bit.",
    "No steps from me yet. Take the question in your own time, and start with whatever is loudest.",
    "There is nothing to do about it until we have looked at it - so start there, in your own time.",
)


# The question the bot asked is itself the thing to do, when it was about the thing: "my career is
# stuck" / "what should i do" came back with "Nothing to do on my side", a shrug under a bot line
# that had just asked what it was like. A friend would say which of the two to answer, and the
# answer's own question is the one concrete thing on the table.
#
# Said as an offer, not as a turn to be taken. The pool used to open "Your turn on the one thing I
# asked" - a line about the mechanics of the conversation, which no friend says, and which
# STYLE.md rules out twice over ("no lectures", and a reply that would fit any message is a
# failure) - and nine of the deck's bare "what should i do" turns got a line from it. The
# question asked back is worth keeping, because it is the one thing on the table that earns a step:
# these lines keep it and say what answering it buys, which is the same content without the telling
# off.
ASKED_FIRST_LINES = (
    "I can be specific if you tell me this much: {q}? Even a line is enough.",
    "One thing and I can be concrete: {q}?",
    "Tell me this and I can say something useful: {q}?",
)


# The same, when the bot's question was only an offer to help ("Is there anything you'd like a
# hand with?"): the offered hand is taken, and the person is asked for the one thing itself.
OFFER_TAKEN_LINES = (
    "Yes - the one thing that is bothering you most, in your own words, and I will start there.",
    "Then give me the thing itself. One sentence is enough, and I will pick the first step from it.",
    "Go on then: name the one part that is worst, and we will take it from there.",
)


SEE_NOW_LINES = (
    "See someone if {when}. Before that, what I said above is the plan.",
    "Not yet, unless {when}. If that happens, get it looked at rather than waiting.",
    "The point where it wants a person is if {when}. Until then, what I said above is the plan.",
)


SEE_ANYWAY_LINES = (
    "That one is a visit rather than a wait, so yes - get it looked at.",
    "Yes. Ring them rather than waiting on it, and say what you have noticed so far.",
    "Nothing to sit on there: that is one to get looked at.",
)


# The answer set the threshold as a thing rather than as a clause ("Blood in it, breathlessness or
# three weeks of it is a reason to ring the surgery"), so it cannot be read after an "if": "See
# someone if blood in it". These name the thing itself as what would change the answer.
SEE_STATED_LINES = (
    "Nothing there needs anyone today. That changes with {when}.",
    "Not yet. The point where it wants a person: {when}. Short of that, what I said above is the "
    "plan.",
    "What would change that: {when}. Until then, what I said above is the plan.",
)


# The answer told them to do nothing, and named the change that would matter. Saying "nothing to
# do" is only honest with that condition in the same breath.
NOTHING_LINES = (
    "Nothing you need to do yet - it matters if {when}.",
    "Nothing to do for now. That changes if {when}.",
    "No steps to take: what I said only changes if {when}.",
)


SEE_NONE_LINES = (
    "Nothing in what I said needs anyone today. If it has not settled in a week or so, that "
    "changes.",
    "Not yet. Give what I described a few days; if it is no better, that is when to ask.",
)


POOLS = (NO_LINES, DO_LINES, YES_LINES)


# Every line this composer can say. They are all kept in one place so a second follow-up
# question can look past them to the answer underneath.
# The pools this composer answers "is that bad" and "what should I do" from are all in here,
# including the ones it says without naming a step or a condition: "Nothing there is a warning on
# its own, that is the everyday fix for it. What would matter is a change in it" is this
# composer's own line, and reading it back as the person's answer turned their second "is that
# bad" into a fresh verdict in its own words rather than the same answer again.
OWN_LINES = tuple(
    line for pool in (NO_LINES, DO_LINES, YES_LINES, STEP_LINES, STEP_DETAIL_LINES,
                      STEP_ONE_LINES, STEP_ALREADY_FIRST_LINES, STEP_KEPT_LINES, SEE_NOW_LINES,
                      SEE_ANYWAY_LINES, SEE_STATED_LINES, SEE_NONE_LINES, NOTHING_LINES,
                      CONDITION_LINES, NOTHING_WARNED_LINES, ORDINARY_NORMAL, CARE_NORMAL,
                      CARE_NORMAL_UNKNOWABLE, CARE_NOW_NORMAL, DO_NORMAL,
                      NOTHING_WARNED_NORMAL)
    for line in pool
)


def _own_pattern(line):
    """A line of this composer as a pattern, with the step or the cause in it left open.

    They are templates, so "Keep it plain, and take it from there." does not contain "{Step}",
    and matching the template as it is written never finds the sentence the composer said. A
    second follow-up would then read the composer's own line back as if it were the answer
    behind it, and answer the answer.
    """
    parts = re.split(r"\{[A-Za-z]+\}", line)
    return ".+?".join(re.escape(part) for part in parts)
