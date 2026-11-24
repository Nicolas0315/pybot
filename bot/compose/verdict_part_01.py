"""Part 1 of 7 of the module, split out of `verdict`.

Everything here is re-exported from `verdict`, so callers import it from there as before.
"""
import re




try:  # the shared reading of a line as news that went well, so a floor does not treat it as a symptom
    from .goodnews import reads_as_good_news as _reads_as_good_news
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no guard
    _reads_as_good_news = None


try:  # whether a death word in the line is about a thing that stopped, so a doubt is not a loss
    from .loss import a_thing_stopped as _a_thing_stopped
except Exception:  # noqa: BLE001 - a reading that cannot be imported just adds no guard
    _a_thing_stopped = None


# The whole line, not a prefix: "is that bad" is a question about the last thing said, while
# "is that bad for the baby" or "is my knee normal" carry their own subject and are someone
# else's to answer.
BARE = re.compile(
    r"^(?:and |so )?(?:is|was|are|were|does|do|did) (?:that|this|it|all of that|all that)"
    r"(?: (?:really|actually|very|too|that))?"
    r"(?: (?:bad|normal|serious|dangerous|ok|okay|alright|all right|acceptable|fine|safe|common|"
    r"weird|odd|strange|a problem|"
    r"something to worry about|anything to worry about|worth worrying about|"
    # "is that something i should worry about" is the same ask as "is that anything to worry
    # about", and the two words in the middle of it were the whole difference: the ruling reader
    # did not match and the worry pool did not either, so a person asking whether a knee or a
    # boiler needed a doctor got "That's beyond what I know well, sorry. Searching for it will
    # turn up better sources". The ask names nothing of its own, so the answer above it is what
    # it is about, which is exactly what this file answers.
    r"(?:something|anything|a thing) (?:i should|to|that i should|worth) worry(?:ing)? about|"
    r"something (?:i should|to) be worried about))"
    r"(?: then| though| or not)?$"
    r"|^(?:and |so )?should i (?:be )?(?:worried|worry|worrying)(?: then| though)?$"
    # "when should i worry" is the same doubt as "should i worry" about the answer just given,
    # and it is the one that names what it wants: the condition. Bare, it has no subject of its
    # own, so no reading of a subject finds it and it reached the search hedge one line after a
    # card that had written the condition out ("my mum keeps forgetting things" / "when should i
    # worry" -> "I'd rather not guess, do a search"). With a subject it stays a knowledge
    # question ("when should i worry about my knee"), so only the bare form is here.
    r"|^(?:and |so )?when (?:should|do|would) i (?:be )?(?:worried|worry|worrying)"
    r"(?: about (?:it|that|this))?(?: then| though)?$"
    r"|^(?:and |so )?when (?:should|do) i (?:start|need) (?:to )?(?:be )?worry(?:ing)?$"
    # "is that worrying" is the same ask in the other order. It is not a fact question this
    # composer may rule on with a yes or a no, though: over a child with a temperature the
    # knowledge base has the answer ("ring 111 if ..."), and a verdict pool took that turn away
    # from it. So it is here only to be read for the answer's own condition, and with no
    # condition in hand it stands aside.
    r"|^(?:and |so )?is (?:that|it|this) (?:worrying|worrisome|a worry)(?: then| though)?$"
    # "do i need to worry" and "do i need to be worried about that" are the same ask again, and
    # an unfinished sentence is how it arrives: the boiler bangs, the person says "do i need to
    # worry", and the search hedge is the one answer that helps nobody. The adverb goes in the
    # middle of it when the person is asking twice - "do i really need to worry", "do i actually
    # have to worry about it" - and the arm did not allow one, so the reinforcement that makes it
    # the doubt fell to the floor: a burnt hand answered "yes, get it looked at" was followed by
    # "do i actually need to worry" and got "that's beyond what I know well, a search should sort
    # you out", which is the search hedge over an answer that had already given it.
    r"|^(?:and |so )?(?:do|will|should|would) i (?:really |actually |honestly )?"
    r"(?:need|have) to (?:be )?worr(?:y|ied)"
    r"(?: about (?:it|that|this))?(?: then| though)?$"
    r"|^(?:and |so )?(?:is|was) (?:that|it|this)(?: (?:going to|gonna))? (?:get worse|"
    r"getting worse|spread|serious)$"
    r"|^(?:and |so )?(?:does|do|did) (?:that|this|it) matter(?: then| though)?$"
    # The copula is the word people drop or mangle when they type in a hurry: "s that ok", "iz
    # that ok", "that ok?". The ask is the same one, and the composer stood aside for it, so the
    # fallback echoed the line back - "Got it - iz that ok." - which says nothing to anybody.
    r"|^(?:and |so )?(?:iz |is |s |z )?(?:that|it|this) "
    r"(?:ok|okay|fine|alright|bad|normal|serious)(?: then| though| or not)?$"
    # "is that just age" is the doubt an older relative's answer gets more often than any
    # other phrasing: after an answer about a parent forgetting words the bot punted ("That's
    # beyond what I know well, sorry. Searching for it..."), which is the one thing a worried
    # daughter cannot use, and "is that just a phase" is the same question about a child. None of
    # the pools below can answer either - the honest answer starts "often, and the change is the
    # part to watch" - so the form has its own reading (AGE_LINES).
    r"|^(?:and |so |or )?(?:is|was) (?:that|it|this) (?:just|only) (?:old age|age|a phase|a stage|"
    r"the age|his age|her age|their age|tiredness|the tiredness)\??$"
    r"|^(?:and |so )?is (?:that|it|this) (?:a|much of a) (?:problem|worry|issue)(?: then| though)?$"
    # "is it bad for me" is the same question asked with the person in it. The subject it names
    # is the speaker, who is the one the last answer was for, so it is not "is that bad for the
    # baby" - a line about somebody else, which only the knowledge base can answer. "harmful",
    # "dangerous" and "will it hurt me" are the same ask in other words, and a person asking
    # them after "the mould on the soil" wants the verdict, not the paragraph again.
    r"|^(?:and |so )?(?:is|was|would|will|can|could) (?:that|this|it) (?:be )?"
    r"(?:bad|harmful|dangerous|unsafe|alright|ok|okay) for (?:me|us)(?: then| though)?$"
    r"|^(?:and |so )?(?:is|was|would|will|can|could) (?:that|this|it) (?:be )?"
    r"(?:harmful|dangerous|unsafe)(?: then| though)?$"
    r"|^(?:and |so )?(?:will|would|could) (?:that|this|it) hurt (?:me|us)(?: then| though)?$"
    r"|^(?:and |so )?(?:does|do|did|will) (?:that|this|it) (?:hurt|harmed|harm|make me ill"
    r"|make me sick)(?: then| though)?$"
    # A doubt about the person themselves, after a line about how they are: "am i ok", "am i
    # going mad". It names nothing at all, so no reading of a subject finds it and it used to
    # reach chat's sign-off - "Glad to hear it." to somebody who had just said they feel low.
    r"|^(?:and |so )?(?:am|was) i (?:ok|okay|alright|all right|normal|going mad|going crazy|"
    r"losing it|losing my mind)(?: then| though)?$"
    # "do i need to worry" is the doubt about the person themselves with the need in it: "am i
    # overreacting" and "should i worry" both have a shape in the composer's fallback, and this
    # one has none, so it walked past every pool below to the floor's care line - "Get it seen
    # today - you'll know either way" over an answer that had said ring 999 straight away.
    r"|^(?:and |so )?(?:do|would|will) i (?:really |actually )?(?:need|have) to (?:be )?"
    r"worr(?:y|ied)(?: about (?:it|that|this))?(?: then| though)?$"
    r"|^(?:and |so )?(?:should|do) i need to worry(?: then| though)?$"
)


# The reassuring words this composer learned to read after the ones below: they say how many
# people it happens to rather than how it ends ("it is common at four", "fix it for most people
# who snore"). They are kept apart because they are the weakest reading of the ordinary - an
# answer that says both "common" and "see a GP if it is one-sided" has named the half that
# matters, and the weakest reading must not talk over it.
HOW_MANY_PEOPLE = ("common", "for most people", "for most adults", "for most children",
                   "for most babies", "usual for", "is usual")


# What a reply that already answered the question sounds like. The reassuring words are the
# ones the knowledge base uses for the ordinary cause; the care words are the ones it uses when
# the point of the answer is that somebody else should look at it. "usually" is here on purpose:
# in these answers it introduces the ordinary case ("usually air or a pump"), not a hedge.
# The half of REASSURE that denies rather than describes: "it usually means a ligament" names the
# ordinary cause, while "most of these are not serious" answers the question asked. A denial in
# the opening settles the turn even when a later sentence lists what to get checked.
DENIES = ("harmless", "nothing to worry", "not serious", "nothing serious", "no need to",
          "nothing to be")


# The answer's own word for "this cannot hurt you". It is the one reassurance a fix above it
# does not take over: "the mould is harmless" answers "is it bad for me" and "scrape it off" does
# not, so an answer that says it keeps the ordinary pool whatever else it tells the person to do.
HARMLESS = ("harmless", "not serious", "nothing serious", "nothing to worry", "nothing to be",
            "no need to", "needs nothing doing", "does not need")


# A word that calls the thing itself normal, as against one that only says what usually happens.
# "Waking in the night is normal - sleep runs in cycles ... The fix is what you do in those
# minutes" has answered the doubt in its own first clause, so the pool that takes the answer's
# word for it is the one to give ("That one is the ordinary kind, so no"); the job in its second
# half does not change that. "Banging or rumbling when the heating starts is usually air ... bleed
# the radiators" has called nothing normal - it said what usually causes it - so there the job is
# the whole verdict. Main pins the first reading (`test_a_bare_ask_with_no_condition_still_gets_
# the_old_reading`), and the second is the one snappy-net asked for.
SAYS_NORMAL = ("normal", "nothing to worry", "not serious", "nothing serious", "nothing to be",
               "no need to", "harmless")


REASSURE = ("harmless", "nothing to worry", "not serious", "nothing serious", "usually",
            "normal", "no need to", "should settle", "usually settles", "will settle",
            "goes away", "just air", "nothing to be",
            # The ordinary kind is often said as an outcome rather than as a verdict: "Most back
            # pain is muscular and settles in two to six weeks", "it usually clears up by itself".
            # A word that only ever names an ending the answer expects is the same reading, and a
            # bare "is that bad" after it was being left with no verdict at all.
            "settles", "settle down", "clears up", "clears by itself", "goes by itself",
            "gets better on its own", "heals on its own", "resolves on its own",
            "does the job on its own", "is muscular",
            # The ordinary kind is also said as how many people it happens to: "It is common at
            # four and still common at nine" ("my son is 6 and he still wets the bed" / "is it
            # normal"), "fix it for most people who snore", "most children say short sentences by
            # three". Every other word in those answers was a cause and a check, so the pooling
            # came back as the search hedge. A danger in the answer is read before this, and a
            # stop is read before it too, so "common, and call 999 if" still lands on the call.
            "is common", "common", "common in", "common at", "common for", "quite common",
            "for most people", "for most adults", "for most children", "for most babies",
            "usual for", "is usual")


CARE = ("get it checked", "get checked", "get it looked at", "get it seen", "see a doctor",
        "see your gp", "ring 111", "call 111", "999", "a&e", "get someone in",
        "get an engineer", "get a heating engineer", "call an engineer", "engineer out",
        "call out", "straight away", "as soon as you can", "urgent", "needs an engineer",
        "is an engineer's job", "stop using it", "stop and", "unplug", "turn it off",
        "switch it off", "turn the water off", "stop the cycle", "leave it off",
        # A vet is the same kind of referral as a GP, and a pet answer says it in its own words:
        # "can my dog eat grapes?" / "is that bad" was answered "Alright then - good luck with
        # it" because none of the words above appear in "Ring your vet today".
        "ring your vet", "ring the vet", "call your vet", "call the vet", "see a vet",
        "see your vet", "get to the vet", "vet today", "vet straight away", "ask your vet",
        "your vet will want", "phone the vet", "phone your vet",
        # A referral is a referral however the answer words it, and these are the ways the
        # knowledge base and the greeting line say it: "worth a GP visit whatever the age",
        # "worth a hearing test first", "ask your health visitor or GP for a referral", "your
        # health visitor or the 111 line will talk it through with you today".
        # "worth a gp" is deliberately not here: it is the declarative way of naming an
        # appointment ("Pins and needles ... is worth a GP visit"), which is a warning about
        # another symptom rather than a referral now, and it is read as one in GO_FROM where the
        # plainness of the go matters.
        "gp visit", "worth a hearing test", "a referral", "for a referral",
        "health visitor", "111 line", "worth seeing", "worth getting looked at",
        # Main's side of the same reading (#4120): the article and the possessive are both ways
        # of saying where the person is sent, and the clinic names that go with them.
        "see a gp", "see the gp", "ring the gp", "phone the gp", "see a nurse",
        "ring the surgery", "call the surgery", "phone the surgery",
        "walk-in centre", "minor injuries", "out of hours", "urgent care",
        # The same referral said as the service rather than as the call: "Your health visitor or
        # the 111 line will talk it through with you today" names who to speak to without a verb
        # in front of it, and that answer is a "yes, this wants someone" for a verdict ask.
        "111 line", "nhs 111", "111 will", "health visitor", "out of hours service",
        "urgent treatment centre", "ask your midwife", "ring your midwife",
        # ... and the same thing said as a visit: "so it is worth a GP visit whatever the age".
        "worth a gp visit", "gp visit", "gp appointment", "doctor's appointment")


# A condition in front of the care words makes them advice for later, not a verdict now:
# "if it keeps dropping, there's a leak ... get a heating engineer out".
CONDITIONAL = re.compile(r"\b(?:if|unless|once|when) \w+[^.]{0,80}$")


# The same condition said after the cue: "see a GP if the arm is weak or numb".
CONDITIONAL_AFTER = re.compile(r"\b(?:if|unless|once|when|whenever)\b")


# A thread that has already said the worst thing in it is not short of a detail, and nothing in
# it is a thing to be weighed: "my dad has cancer" then "is that bad" is somebody checking
# whether the weight of it is allowed. The doubt path used to send that to the acknowledgement
# floor - "Alright then - good luck with it." - a diagnosis heard and answered like a lunch. The
# line gives no verdict, asks for nothing and puts nothing on a scale.
HARD_NEWS_LINES = (
    "There is no verdict to give on that one - some things are just hard, and that is not a "
    "judgement on you.",
    "I would not put that on a scale. What happened is heavy enough without working out where "
    "it sits.",
    "That is not something with a good or bad answer. It is a hard thing to carry, and you are "
    "allowed to just feel it.",
)


# The worst things a person brings here, as they write them. Read on the person's own line and
# not on the bot's, because a condolence is written to say how it feels rather than what
# happened ("I'm really sorry" says nothing about a father). Only the things that make a doubt
# the wrong question: a diagnosis of coeliac disease or ADHD is a thing to learn about rather
# than a hard thing to carry, and it is answered as it was.
HARD_NEWS = re.compile(
    r"\b(?:died|dying|death|passed away|funeral|buried|cremated|hospice|"
    r"cancer|leuka?emia|lymphoma|myeloma|tumou?r|terminal|palliative|chemo|radiotherapy|"
    r"miscarriage|miscarried|stillborn|"
    r"dementia|alzheimers|motor neurone|multiple sclerosis|parkinsons|copd|"
    r"kidney failure|heart failure|liver failure|"
    r"stroke|heart attack|sepsis|"
    r"given months|not going to make it)\b", re.I)


# What an answer that heard the news sounds like. The doubt only belongs to the loss when the
# answer above was about the loss: "how do i stop my phone battery dying" / "is that bad" is not
# a bereavement, and "my plant is dying" / "is that bad" is not one either - both are how-to
# answers, and neither of them says sorry.
SYMPATHY = re.compile(
    r"\b(?:i'm sorry|im sorry|so sorry|really sorry|sorry to hear|sorry for your loss|"
    r"sorry about (?:your|the)|sounds rough|that sounds rough|a real loss|how awful|that's awful|"
    r"that is awful|how sad|that's sad|that is sad|"
    # A reply that meets the news without the word "sorry" in it still met the news: "my dad had
    # a stroke" is answered "Frightening to watch, and the first day or two is tests rather than
    # answers", and "my grandad had a heart attack" with "Ugh, that's a lot to carry". Both are
    # the bot hearing a hard thing, which is what this half of the test asks.
    r"frightening|scary|a lot to carry|no wonder|that's heavy|that is heavy|"
    r"nothing about that is a fault|hardest days?)\b", re.I)


# A referral that names when to act is not waiting on a condition, and an "if" later in its own
# sentence is measuring something rather than deciding whether to go: "Ring the vet today if it
# has been more than 24 hours, and straight away for a puppy under six months" is the threshold
# that says go now. Reading that later "if" as a fence made the referral conditional twice over,
# and a dog that will not eat was answered "that one is the ordinary kind, so no" one turn after
# an answer that said ring the vet today.
# The words that turn a condition into a degree of the same errand ("and sooner if ..."): the
# answer has already said go, and this says go at once.
COMPARATIVE = re.compile(r"\b(?:sooner|earlier|quicker|faster|more so|especially|particularly|"
                         r"above all)\b", re.I)


URGENT_TIME = re.compile(r"\b(?:today|tonight|now|straight away|right away|immediately|"
                         r"as soon as|first thing|urgent(?:ly)?|within \d+)\b")


# A person's week is not a body either. "my mum is 79 and lives on her own" is answered "Do the
# inviting yourself, and make it the same thing each week ... if they seem low for weeks rather than
# lonely, ask them plainly how they are and help them see a GP", and "is that ok" came back "Yes,
# that one wants a proper look rather than watching it. Get it looked at properly" - the pools read
# the answer's fenced care for the harder case as a referral for a symptom, and offered a woman on
# her own a doctor's look for her week (#routing 77612). The verdict on a person's situation is
# about the answer's own two halves: do the simple step now, and the fenced half is when to act.
# A body in the line is the health cards' subject, not this reading's: "my baby is not feeding",
# "my son has a temperature of 39" and "my child has a rash" all keep the pools above.
A_SYMPTOM_WORD = re.compile(
    r"\b(?:skin|rash|itch|itching|eyes?|ears?|throat|chest|stomach|belly|temperature|fever|"
    r"vomit|vomiting|sick|diarrhoea|diarrhea|feeding|feeding|breath|breathing|breathless|cough|"
    r"poo|wee|blood|pain|hurts?|hurting|swelling|swollen|knee|joint|joints|mouth|teeth|tooth|"
    r"napp(?:y|ies)|nappy|wet(?:s|ting)? the bed|constipated|constipation|gums?)\b", re.I)


A_PERSON_THEY_KNOW = re.compile(
    r"\b(?:mums?|moms?|mother|father|dads?|son|daughter|kids?|child(?:ren)?|wife|husband|"
    r"partner|girlfriend|boyfriend|friend|friends|neighbours?|grans?|granny|nan|nana|"
    r"grandma|granddad|grandad|grandpa|sister|brother|aunt|uncle|cousin|bab(?:y|ies)|"
    r"in[- ]laws?|mother in law|father in law)\b", re.I)


# What makes it the person's days rather than their health: contact, company and quiet, which is
# the subject of the friendship and loneliness answers. A body in the line stands the reading down
# ("my baby is not feeding", "my son has a temperature of 39"), and so does a line about nothing
# but sleep or food - those are the health cards, and the pools above are right for them.
A_RELATION_TROUBLE = re.compile(
    r"\b(?:lonely|loneliness|company|visit|visits|visiting|ring|rings|rang|call|calls|called|"
    r"speak|speaks|spoke|spoken|talk|talks|talked|talking|quiet|withdrawn|alone|"
    r"on (?:his|her|their|its) own|lives? on (?:his|her|their) own|"
    r"arguments?|arguing|row|rows|falling out|fallen out|ignores?|ignoring|"
    r"does not listen|doesnt listen|wont listen|wont say|wont go out|does not go out|"
    r"trust|trusts|jealous|suspicious|accuses?|accusing|controlling|keeps? checking|"
    r"checking (?:my|his|her|their)|"
    r"doesnt go out|birthday|anniversary|seen (?:him|her|them)|see (?:him|her|them))\b", re.I)


PERSON_ORDINARY = (
    "There is nothing there to watch for going wrong: it is an ordinary stretch, and the answer's "
    "own first step is what moves it. Do that for a few weeks - if it is the same after that, say "
    "it to them plainly rather than sitting on it.",
    "Nothing in that is a fault on either side. The small thing in the answer, done consistently, "
    "is what changes it, and if nothing has changed after a few weeks that is the point to say "
    "something out loud.",
)


PERSON_CALL = (
    "Yes - take up the first half of what I said now, and the second half is what to act on: if it "
    "is still like that after a few weeks, do the part about talking to somebody properly.",
    "Yes, that one is worth acting on rather than watching. Start with the simple step in the "
    "answer, and if nothing has moved in a few weeks, take the next step it names.",
)


NO_LINES = (
    "Nothing in that sounded like a warning sign. What would change it is the thing itself "
    "changing — getting worse, or not settling — and then it's worth getting looked at.",
    "That one is the ordinary kind, so no. Watch it rather than worry about it: if it's still "
    "the same in a week or two, or it gets worse, get someone to look at it.",
    "No — the part you asked about is the harmless kind. What to keep an eye on is change "
    "rather than the thing itself.",
)


# An answer can do both: "It is common at four and still common at nine ... so it is worth a GP
# visit whatever the age". The ordinary word alone would have the bot say "nothing to act on
# now" against the answer's own advice, so this shape gets a line that says both halves.
BOTH_LINES = (
    "It's the common kind rather than a warning sign — and the check is still worth doing.",
    "Common enough, so no panic. Getting it looked at is worth doing all the same: that is what "
    "catches the less usual ones.",
    "Not a warning sign on its own, no. Common enough that mentioning it is enough rather than "
    "rushing — do that, and say what they tell you.",
)


DO_LINES = (
    "It's a job rather than a danger. Do it and see whether it holds — if it comes back, that's "
    "the point where it stops being a DIY thing.",
    "Not bad in itself, but not something to leave alone either. Do the job properly, and if it "
    "comes back after that, get someone in.",
    "Worth doing rather than worrying about. Sort it out; if it keeps coming back, that's when "
    "it's somebody else's job.",
)


# A follow-up asking whether the step just given is the fix: "and does that fix the pressure
# too", "will that sort it out", "does that cure it". The step is in the answer the person was
# given a turn ago, so the honest reply is whether doing it fixes the thing and how they will
# know - not the same paragraph again. The answers entry hands back a slice of its own paragraph
# word for word on this ask ("my boiler keeps losing pressure" then "and does that fix the
# pressure too"), which is the same answer twice with nothing said about the question it asked.
# The shape is what is read, never the topic: any step, any subject.
FIX_ASKED_LINES = (
    "Give it a day or two and see whether it holds. If the same thing comes back, the step was "
    "not the fix and it wants a proper look.",
    "Do it and give it a few days. Coming back after that is the sign it is not something the "
    "step sorts out on its own.",
    "Try it and watch what happens next. If it stays away, that was the whole of it; if it "
    "does not, the thing behind it needs seeing to.",
)


# ...and the same question about a step whose answer arrives at once. A blocked bath trap is
# answered by running the tap: "do it and give it a few days" is wrong advice for it, because the
# person knows in a minute. So the wait is read off the step the answer gave, and a step that names
# no wait gets the verdict now. The test in the line is the one the person already used to decide
# the thing was broken.
FIX_ASKED_NOW_LINES = (
    "Do it now and check it the way you checked before. If nothing has changed at all, that step "
    "was not the fix and the next thing to look at is further in.",
    "Try it straight away. If it does what it should, that was the fix; if it behaves the same, "
    "the step was not the answer and something else is doing it.",
    "Do it and look again straight after. Unchanged means the step was not the fix, rather than "
    "that it needs longer.",
)


# The wait a step can name for itself: "leave it overnight", "check after a week", "within a few
# days". Minutes are not a wait - "you will know in a minute" is the step answering at once.
A_WAIT_IN_THE_STEP = re.compile(
    r"\b(?:after|within|for|over|in|another)\s+(?:a|an|the|two|three|four|five|six|few|couple|"
    r"several|\d+)\s+(?:day|days|week|weeks|night|nights|month|months)\b"
    r"|\bovernight\b|\bnext day\b|\bthe following (?:day|week)\b"
    r"|\bleave it (?:to|for)\b", re.I)


# The ask itself: a modal or an "is/does", a pointing word, and a word for fixing. Kept short,
# because a long line brings its own subject and is a new question rather than a question about
# the answer just given.
_ASKS_ABOUT_A_STEP = re.compile(
    r"\b(?:does|do|will|would|should|can|could|is|was)\b(?:\s+\w+){0,3}\s+(?:that|this|it)\b", re.I)


# The asks that want the step itself rather than a word on whether one will work: "how do i fix
# it", "what should i do about it". They are the same words as the follow-up and the opposite
# question, which is why they are read first.
_ASKS_FOR_THE_STEP = re.compile(r"^\s*(?:how|what|where|when|which|who|why)\b", re.I)


_A_FIX_WORD = re.compile(
    r"\b(?:fix|fixes|fixed|sort|sorts|sorted|solve|solves|cure|cures|work|works|help|enough|"
    r"stop|stops|clear|clears|do the trick|make a difference)\b", re.I)


# Answers that are not a job the person tries and watches for a few days: a body, a pregnancy, a
# baby, an animal, or somebody to ring. "my baby is not feeding" is answered with "a baby under
# three months who stops feeding needs looking at today", and "does that fix it" was told to
# "give it a few days", which is the one thing that answer must never say. The knowledge base
# already says which module an answer came from (`last_answer["domain"]`), so the reading is the
# module and not a phrase: a boiler in a chat about a baby is still a boiler, because the boiler
# answer came from `home`. The words are the fallback for an answer with no module behind it, and
# they are kept to the ones no DIY or cooking answer uses - "bleed" is a radiator here.
NOT_A_STEP_TO_WATCH = frozenset((
    "health", "pregnancy", "babyfood", "body", "caring", "complaints", "crisis_replies",
    "pharmacy", "pets", "animals", "family", "friends", "sleep",
))


NOT_A_STEP_TO_WATCH_WORDS = re.compile(
    r"\b(?:baby|babies|infant|newborn|toddler|pregnan\w*|napp(?:y|ies)|rash|fever|"
    r"vomit\w*|diarr\w*|breathless|symptom\w*|seizure|dehydrat\w*|allerg\w*|asthma|"
    r"inhaler|epipen|insulin|diabet\w*|medicin\w*|medication|antibiotic\w*|paracetamol|"
    r"ibuprofen|painkiller\w*|gp|gps|doctor|doctors|nurse|midwife|pharmac\w*|hospital|"
    r"a&e|ambulance|111|999|911|dentist|vet)\b", re.I)


# An answer whose care is fenced by an "if" is not a warning about the thing itself: "my arm
# aches after gardening" ends "See a GP if the arm is weak or numb", and a bare "is that bad"
# asks about the ache. The honest verdict is the answer's own line: this is ordinary on its own,
# and the condition it named is the thing to act on.
CONDITION_LINES = (
    "Not the thing itself, no. It would stop being ordinary if {when} — that is the point to "
    "act on.",
    "Ordinary on its own, yes. It stops being ordinary if {when}, so that is what to watch.",
    "Nothing in that is a warning by itself. It becomes one if {when}: that is when it wants "
    "someone.",
)


# And when the condition the answer named is the thing the person just described, there is no
# fence left to quote: "my baby is not feeding" / "is that bad" was told "Ordinary on its own,
# yes. It stops being ordinary if it stops feeding" by an answer that had just said to ring 111
# now. The answer's own threshold is met, so the verdict is the answer's next step, not a
# reassurance about a condition the person has already met.
# The floor under a death, when the line the ask follows is a condolence rather than an answer.
# It claims nothing about what the person is carrying, and it does not ask them to describe it.
GRIEF_FLOOR_LINES = (
    "Not something to be graded bad or not - it is a loss, and it deserves the room it takes. Be "
    "gentle with yourself, and let whoever is around you know how you are.",
    "That is not a thing to call bad, and not a thing to carry on your own. Take the help that is "
    "offered, and tell someone close how today actually went.",
    "Nothing about that is a fault in you. Give it the time it takes, and lean on the person who "
    "asks how you are.",
)


MET_CONDITION_LINES = (
    "Then you are already at the point it named, so that is the bit to act on rather than the bit "
    "to watch. Get it looked at, and say what you told me here when you do.",
    "That is the thing that answer said to act on, and it is what you are describing. Get it seen "
    "to rather than sitting with it.",
    "So it is past the watching stage: the answer's own next step is the one for now. Get that "
    "started today.",
)


# The two arms of BARE that are this ask, kept here as well so the pool below can be chosen for
# them and for nothing else (an "is that bad" still gets its verdict).
WHEN_ASK = re.compile(
    r"^(?:and |so )?when (?:should|do|would) i (?:be )?(?:worried|worry|worrying)"
    r"(?: about (?:it|that|this))?(?: then| though)?$"
    r"|^(?:and |so )?when (?:should|do) i (?:start|need) (?:to )?(?:be )?worry(?:ing)?$")


# The same ask the other way round. It is read for the answer's own condition and nothing else:
# a bare "is that worrying" over a card with no condition in it is the knowledge base's (a child
# with a temperature has a line about 111, and a verdict pool has none).
WORRYING_ASK = re.compile(
    r"^(?:and |so )?is (?:that|it|this) (?:worrying|worrisome|a worry)(?: then| though)?$")


# "when should i worry" is not a yes/no doubt: it asks for the condition, so the answer is the
# condition the card just wrote out, not a verdict on the thing. Over "my mum keeps forgetting
# things" the yes/no pools said "Yes, that one wants a proper look rather than watching it",
# which answers a question nobody asked, while the card had already listed what counts.
WHEN_LINES = (
    "This is the line: {when}. Short of that it is the ordinary kind, and worth watching rather "
    "than acting on.",
    "What makes it somebody else's job: {when}. Until then it is a watch-and-see.",
    "The point to act on is this: {when}. Before that it is the ordinary thing, so keep an eye on "
    "it rather than acting on it.",
)


# The same ask over a card that named its call and its reason in the other order: "See a GP the
# same day for spreading redness or pus; a red streak running up the arm or leg, a fever, or
# feeling shivery and ill is 111 today". The {when} already carries each sign's own call, so
# these lines only have to say where the waiting stops.
WHEN_CALL_LINES = (
    "The line to act on: {when}. Short of that it is the watching stage, and the answer's own "
    "steps are the plan.",
    "This is where it stops being a wait-and-see: {when}. Before that, do what the answer said "
    "and keep an eye on it.",
    "What sends you to someone: {when}. Under that line the answer's steps are the whole of it.",
)


# Many cards write the condition as a list with a call at the end of it rather than as an "if":
# "A leg he won't put weight on, a swelling, or a limp that is no better after two days needs the
# vet", "asking the same question within minutes, getting lost on a familiar route, or forgetting
# something they have always done are not, and want a GP appointment". A "when should i worry"
# asks for exactly that list, and every reader above looks for a fence, so it found nothing and
# the answer was a flat "yes, get it looked at" over a card that had written the line out.
NEEDS_A_CALL = re.compile(
    r"(?P<list>[^.;:]*?)\s*(?:,\s*and\s+|\s+and\s+)?(?:needs?|wants?|want|means)\s+"
    r"(?:the\s+|your\s+|a\s+)?"
    r"(?:vet|gp|doctor|dentist|optician|pharmacist|physio|111|a&e|engineer|plumber|electrician)\b",
    re.I)


# The "are not, and" that joins the list to its call is the card's grammar, not part of the list.
_LIST_JOIN = re.compile(r"\b(?:are|is|was|were)\s+not\s*,?\s*(?:and)?\s*$", re.I)


def _the_list_before_the_call(said):
    """"A leg he won't put weight on, a swelling, or ..." - the answer's own list of signs."""
    best = ""
    for m in NEEDS_A_CALL.finditer(str(said or "")):
        part = _LIST_JOIN.sub("", m.group("list").strip(" ,;:-"))
        part = part.strip(" ,;:-")
        words = part.split()
        if 3 <= len(words) <= 24 and len(part) > len(best):
            best = part
    # "A leg he won't put weight on, a swelling" is quoted mid-sentence after a colon, so the
    # card's own capital goes with the full stop it was written behind.
    if best and best.split()[0] in ("A", "An", "The"):
        best = best[0].lower() + best[1:]
    return best


# The other order again: the call first and what it is for after it. "Ring 111 if you cannot
# breathe" is the shape every reader above knows, but "See a GP the same day for spreading
# redness or pus" is not an "if" at all, and it is how a cut and a cough write their line. Over
# both, a person asking "when should i worry" was told nothing about the answer in hand: "my cut
# looks infected what should i do" / "when should i worry" went to the search hedge, over a card
# that had named a GP, 111 and the signs for each.
CALLS_FOR = re.compile(
    r"\b(?:see|ring|call|contact|speak to|go to|get)\s+(?:a |your |the )?"
    r"(?P<who>gp|doctor|practice nurse|nurse|111|999|a&e|vet|dentist|optician|pharmacist|"
    r"surgery|midwife|physio(?:therapist)?|urgent care|out of hours)"
    r"(?P<quick>\s+(?:the same day|today|straight away|now|first thing|as soon as you can|"
    r"within \w+ hours))?\s+for\s+(?P<list>[^.;:]+)",
    re.I)


# The same line with the sign in front and a number behind it: "a red streak running up the arm
# or leg, a fever, or feeling shivery and ill is 111 today".
IS_A_NUMBER = re.compile(
    r"(?P<when>[^.;:]+?)\s+(?:is|are)\s+(?P<who>111|999|a&e)\b"
    r"(?P<quick>\s+(?:today|now|the same day|that day|straight away))?",
    re.I)


# The pool above says where the waiting stops, which is the wrong thing to say to somebody already
# past it: "there is a red streak up my arm / when should i worry" and "my cut has pus coming out
# of it / when should i worry" were told "Before that, do what the answer said and keep an eye on
# it", which puts them back under a line their own line has crossed. When the sign about to be
# quoted is worded in the person's own line, the reading that already exists for these chats (a
# proper look, the call is the thing to do now) is the one that answers.
_NOT_A_SIGN_WORD = frozenset((
    "about", "after", "again", "been", "before", "could", "doesnt", "from", "have", "into",
    "just", "like", "more", "much", "only", "over", "same", "should", "some", "than", "that",
    "their", "them", "then", "there", "these", "they", "thing", "this", "very", "want", "what",
    "when", "will", "with", "worried", "worry"))


def _the_sign_words(call):
    """The content words of the signs in the quoted call, without the calls themselves."""
    signs = re.sub(r"\([^)]*\)", " ", str(call or ""))
    return {w for w in re.findall(r"[a-z']+", signs.lower())
            if len(w) >= 3 and w not in _NOT_A_SIGN_WORD}


def _the_person_for(who, quick):
    """"See a GP the same day" -> "a GP the same day"; "111 today" keeps its number."""
    trade = (who or "").strip().lower()
    if not trade:
        return ""
    # The card writes "a GP" and "A&E" and so does the line: a lowercase "gp" reads as a typo.
    trade = {"gp": "GP", "a&e": "A&E", "nhs": "NHS"}.get(trade, trade)
    if trade[0].isdigit() or trade in ("A&E", "NHS"):
        piece = trade
    elif trade in ("GP", "doctor", "practice nurse", "nurse", "surgery", "vet", "dentist",
                   "optician", "midwife", "physio", "physiotherapist"):
        piece = "your " + trade
    else:
        piece = "a " + trade
    hurry = re.sub(r"\s+", " ", str(quick or "")).strip(" ,")
    return (piece + " " + hurry).strip() if hurry else piece


# An answer that is a fix and no warning at all: "damp in the corner of my bedroom" gets the
# extractor fan and the window, and "is that bad" arrives. The answer never said "harmless" and
# never named anyone to ring, so the two pools above do not apply - but it also never said
# anything was dangerous, and that is a reading of the bot's own words rather than a claim about
# the world: nothing in the answer was a warning, and the answer's fix is the thing to do.
# The doubt path is for a person checking a thing that is wrong: "damp in the corner of my
# bedroom" then "is that bad". A plan and a how-to are not things that can be wrong - "im going
# to rome" then "is that ok" asked about the trip, "how do i cook rice" then "is that ok" asked
# about the method - and both were told "Everything in that answer is the ordinary job": a
# verdict on a fault nobody had raised. So the line has to report something, not announce one
# or ask for one.
# A plan is the person's own, so its subject is them in the first person. Without that the arm
# read a prediction about a fault as a plan: "the damp in my bedroom is going to get worse" then
# "is that bad" got "Alright then - good luck with it", and so did "my back is going to give out"
# and "my tooth is going to fall out", when the answer above each of them was the one that says
# what to watch.
A_PLAN = re.compile(
    r"\b(?:i'm|im|i am|we're|were|we are)\s+(?:going|off|flying|driving|sailing|heading|"
    r"travelling|traveling|moving|booking|booked|selling|buying|renting)\b"
    r"|\b(?:i|we)\s+(?:want|wanna|hope|plan|intend|need|'d like|would like)\s+to\b"
    r"|\b(?:i'm|im|i am|we're|were|we are)\s+(?:about to|planning to|thinking (?:of|about)|going to)\b")


# The other line that is not a fault: one that asks how to do something. Its "is that ok" is
# about the method, and the method in the answer is the bot's own, so the verdict is that it is
# the way the bot would do it - not "that is how it is normally handled", which answers a
# question about danger.
A_HOW_TO_ASK = re.compile(
    r"\b(?:how|where|when)\s+(?:do|should|can|could|would|shall)\s+(?:i|we)\b"
    r"|\bhow\s+(?:do|can|would)\s+(?:i|we)\s+(?:stop|get|fix|clean|keep|make|put|sort|"
    r"deal|go|use|set|apply)\b")


# "What should I cook tonight" then "is that ok" is asking whether the suggestion is fine, and
# the fault pools answer a different question ("Not on its own, no. That is how it is normally
# handled..."). A suggestion is the bot's own, so the warm acknowledgement is the honest reply.
A_DECISION_ASK = re.compile(
    r"\b(?:what|which)\s+(?:should|shall|do|would)\s+(?:i|we)\b"
    # "should i" on its own is a yes/no question about one thing, not a choice between two:
    # "should i get my mole checked" / "is that bad" was read as a choice and handed back
    # "Alright then - good luck with it", when the answer above was a referral and the doubt
    # has one answer. Only a line that names a second option is the choice this stands aside
    # for ("should i ring the shop or the maker first", "what should i cook tonight").
    r"|\b(?:should|shall)\s+(?:i|we)\b")


# An answer that opened by giving the yes it was asked for, with its condition on it ("Yes, if
# they want heat within about 20C of each other: put the hotter dish in first", "Yes, as long as
# the pan is deep enough"). The method is confirmed in the answer itself, so a bare "is that ok"
# on the next turn is the person checking that method and not asking for a verdict on a fault:
# read through the fault pools it was told "That answer is the usual handling of it rather than a
# warning about it", which is an answer to a question nobody asked (sleek-heather, #routing 75213).
SAID_YES = re.compile(
    r"\A\W*(?:yes|yep|yeah|yup|it does|that does|they can|it can|you can|both do)\b",
    re.IGNORECASE)


# "will that work" after a how-to is a doubt about the step, not a decision to weigh. The pool
# that judges a choice ("would that work" after "im thinking of getting a cat") was reading it
# too, and told a person who had just been given the way to bleed a radiator "Not a call I can
# make for you" - a refusal of a question the bot's own answer had answered.
METHOD_DOUBT = re.compile(
    r"^(?:and |so |but |ok |okay |well )*(?:will|would|does|do|did|can|could) "
    r"(?:that|this|it) (?:actually |really |even |still )?"
    r"(?:work|help|be enough|do the job|do it)(?: then| though)?$")


# "will that work" after a how-to is a doubt about the step, not a decision to weigh. The pool
# that judges a choice ("would that work" after "im thinking of getting a cat") was reading it
# too, and told a person who had just been given the way to bleed a radiator "Not a call I can
# make for you" - a refusal of a question the bot's own answer had answered.
METHOD_DOUBT = re.compile(
    r"^(?:and |so |but |ok |okay |well )*(?:will|would|does|do|did|can|could) "
    r"(?:that|this|it) (?:actually |really |even |still )?"
    r"(?:work|help|be enough|do the job|do it)(?: then| though)?$")


# The whole family, not five phrasings of it: the same check is asked as "would that be worth
# it", "does that actually work", "is that the right thing to do" and "shall i try that", and
# each of those was left to the card it was checking, which said itself again.
A_CHECK_ASK = re.compile(
    r"^(?:and |so |but |ok(?:ay)?[, ]+)?(?:do you think\s+)?"
    r"(?:will|would|does|do|did|should|shall|could|can|is|was)\s+(?:that|this|it|they|those)\s+"
    r"(?:actually |really |even )?(?:be\s+)?"
    r"(?:work|works|help|helps|fix it|fix that|do it|do the trick|do any good|"
    r"make a difference|sort it|be enough|enough|ok|okay|fine|right|worth it|worth doing|"
    r"worth a go|worth the money|the right thing|the right thing to do|the right way|"
    r"the done thing|the usual way)"
    r"(?: then| though| at all| for me| for us| for them| really)?\s*$"
    # the same check with the person as the subject: "shall i try that", "should i give it a go",
    # "do i do it that way"
    r"|^(?:and |so )?(?:shall|should|could|can|do)\s+i\s+(?:try|do|use|go with|give)\s+"
    r"(?:(?:that|this|it)\s+)?(?:a\s+)?(?:go|try|shot)"
    r"|^(?:and |so )?(?:shall|should|could|can|do)\s+i\s+(?:try|do|use|go with)\s+"
    r"(?:that|this|it)(?:\s+then)?\s*$"
    # the plain form, subject first: "that will work", "do you think that is enough"
    r"|^(?:and |so )?(?:do you think\s+)?(?:that|this|it)\s+(?:will|would|does|is|'s)?\s*"
    r"(?:be enough|enough|work|help|be worth it|be ok|be fine)\s*$"
    # and the version that names the question rather than the effect
    r"|^(?:and |so )?(?:is|was)\s+(?:that|this|it)\s+the\s+"
    r"(?:right|best|proper|usual|sensible|standard)\s+"
    r"(?:thing|way|way to do it|order|approach|method|call)(?:\s+to\s+do)?\s*$")


# The ask about whether the method does anything, rather than about whether it is the right one:
# "will that work" / "will that help" / "would that fix it" / "is that enough" / "do you think
# that is enough". Kept apart from BARE because the thing being checked is the answer's effect,
# not the fault in the thing, and apart from A_HOW_TO_ASK because the how-to ask comes before it.
# A line that says the person is still weighing a thing up rather than asking how to do it: the
# answer to it is the bot's view of the choice, and a check on that answer is not a check on a
# method.
A_THINKING_ABOUT = re.compile(r"\bthinking (?:about|of)\b|\bwondering\b|\bconsidering\b|"
                              r"\bnot sure (?:if|whether)\b")


# Said back to a person checking the method they have just been given.
# The lines do not answer "is that bad" with a yes in front of them, because the same pool answers
# "is that ok" and "is that bad": "It is, yes" after "is that bad" reads as a verdict that the
# thing is bad, and the method is the only thing either ask is about.
METHOD_OK_LINES = (
    "Nothing there is a problem - that is how I would do it too.",
    "That is how I would go about it, and there is nothing in it to worry about.",
    "Done that way, it needs no one else: that is the method I would use.",
)


# A check on the effect of the method just given: "will that work", "will that help", "is that
# enough". It is the same ask as "is that ok" about a method, said about whether the method does
# anything, and the answer above is the bot's own method, so the reading is the answer's own: it
# is the standard thing to try, and what the person does next is watch it. Told instead "Not a
# call I can make for you. Say what you would lose either way" - the line for a choice the bot
# has no view on - a person asking about advice the bot had just given was handed the question
# back, and told "Alright then - good luck with it" the conversation was closed on them.
# The two pools are split by whether the answer named something to watch for, for the same reason
# the method pool is: "will that help" over the back-pain answer must not drop the line about
# getting it looked at if it is no better.
CHECK_WORKS_LINES = (
    "It is the right thing to try first, and it works for most people. Give it a week or two and "
    "tell me how it goes.",
    "Yes - that is the standard way, so it is the one I would count on to start with. What changes "
    "after you have tried it is what tells us the next step.",
    "That is the usual way to go at it and it tends to do the job. If nothing has moved in a "
    "week, say so and we will go a step further.",
    "That is what I would do myself, so yes - it is worth a run. A fortnight of it is usually "
    "enough to know.",
)


# The check after a method with no length to it: "how do i cook rice" / "will that work". Rice is
# cooked tonight, so "if nothing has moved in a week" is not true of it - the same sentence would
# land on a stain, a blocked drain or a flat tyre. This pool answers the check and says nothing
# about how long the thing is meant to take, because the answer above gave it no time at all.
CHECK_ONCE_LINES = (
    "That is the standard way of doing it and it works - tell me how it goes and we will take it "
    "from there.",
    "Yes, that is how it is done. Do it that way and tell me how you get on.",
    "That way of doing it is the right one, so go ahead - tell me if it does not do the trick.",
)


# The answer above says how long the thing takes to show ("give it a week", "two to six weeks",
# "if it has gone on for weeks"), so a check on it can talk about that length. A method with no
# length in it is a one-off job, and the pool above is the one for it.
# Only a length a week of trying it can be measured against counts: days, a few weeks, a
# fortnight. "Ten weeks" was a length too, and the check over it said "give it a week or two and
# tell me how it goes" about a passport application (snappy-net, #8488) - the length was read out
# of the answer and then a different one was invented over it. A month or a year is the same
# fault, so the numbers stop at four and the long units are out: the answer with ten weeks in it
# is a one-off job as far as this pool is concerned, and the pool with no time in it answers.
A_LENGTH_IN_THE_ANSWER = re.compile(
    r"(?<![a-z])(?:a|one|two|three|four)(?: or (?:more|so))? "
    r"(?:day|days|week|weeks|night|nights|hour|hours|fortnight|fortnights)(?![a-z])"
    r"|(?<![a-z])a few (?:days|weeks|nights)(?![a-z])|(?<![a-z])fortnight(?![a-z])")


CHECK_WATCH_LINES = (
    "That is the thing to try first, and most people do well on it. If it is no better in a week "
    "or two, that is when it wants someone to look rather than more of the same.",
    "Yes, that is worth doing first. If it stops helping, or it goes the wrong way, that is the "
    "point to get it looked at rather than wait.",
)


# The pools above are about a remedy - "most people do well on it", "give it a week or two" - and
# that is only true of a body or a habit. A job that is not a remedy is a price, a form, a wait or
# a quote, and the remedy wording is about nothing there: "what does a dentist cost" / "will that
# help" got "most people do well on it" over an answer whose job was to ask which band the
# treatment falls in, "how long does a passport take" / "will that work" was told to give it a
# week or two over an answer that says ten weeks, and "my car is 12 years old" / "will that help"
# was told it tends to do the job over "get an insurance quote before you buy". This pool answers
# the check and claims nothing about how long the job takes or how it usually goes, because the
# answer said neither (snappy-net, #8488).
# The words that make a remedy pool's claims true: a body part or a symptom. Only these, and not
# the clinician words - "what does a dentist cost" names a dentist and asks about money, and the
# answer to it has no body in it at all (snappy-net, #8488).
try:  # the body and symptom words the composer already knows
    from .fallback_data import BODY_PARTS as _BODY_PARTS, SYMPTOM_WORDS as _SYMPTOM_WORDS
except Exception:  # noqa: BLE001 - a reading that cannot be imported just leaves the neutral pool
    _BODY_PARTS = _SYMPTOM_WORDS = frozenset()


_A_BODY_WORD = frozenset(_BODY_PARTS) | frozenset(_SYMPTOM_WORDS) | frozenset((
    # the words the order of a sentence hides: "my back is killing me", "i feel sick"
    "sick", "unwell", "ill", "nauseous", "sore", "soreness", "swollen", "swelling"))


def _about_a_body(*texts):
    """True when one of these lines names a body part or a symptom.

    Callers pass the line the person typed, not the answer: an answer says "back the files up",
    and read as a body that made the laptop answer a remedy ("give it a week or two" over "leave
    it two days"). The line the person typed is what the check is about.
    """
    for text in texts:
        words = re.findall(r"[a-z'-]+", str(text or "").lower())
        if any(word in _A_BODY_WORD for word in words):
            return True
    return False


CHECK_JOB_LINES = (
    "That is how I would go about it, and it is the right thing to do first. Tell me how you get "
    "on and I will pick it up from there.",
    "Yes, do it that way - it is the sensible order to do it in. Say how it goes.",
    "That is the right first move, and what comes back from it decides the next step.",
)


# A choice the answer made for them ("what should i cook tonight" -> three dinners, "should i get a
# dog" -> the test to apply) and its "is that ok?" is a question about the suggestion, not about a
# fault. Standing aside for it left the acknowledgement floor's "Alright then - good luck with
# it.", which answers nothing, so the pool says the one thing that is true and useful: it is a good
# call, and nothing in it needs second-guessing. It works for a dinner and for a dog because it
# judges the choice rather than the thing chosen.
ASKS_FINE = re.compile(
    r"\b(?:ok|okay|alright|all right|fine|sensible|a good idea|worth it)\b", re.I)


ASKS_WRONG = re.compile(r"\b(?:bad|wrong|worrying|worry|a problem|dangerous|stupid)\b", re.I)


CHOICE_OK_LINES = (
    "Yes - that is a good call, and there is nothing in it I would change.",
    "Yes, go with it. It is a sensible thing to do and nothing in it is a problem.",
    "That one is fine as it stands. Nothing in it needs second-guessing.",
    "Nothing wrong with that choice. If it is the one that suits you, take it.",
    "Yes, I would. That is the pick I would make from where you are standing.",
)


# The lines talk about the thing, not about the conversation: "there was no warning in what I
# told you" reads as a system message about itself, and a person asking whether something is bad
# wants to hear that it is ordinary on its own and what would change that.
NOTHING_WARNED_LINES = (
    "Nothing there is a warning sign - it is the ordinary thing to do. What would change it is "
    "the thing itself getting worse, or not settling.",
    "There is no warning in it: that is the everyday fix. What would matter is it getting worse "
    "or not shifting, so watch for that.",
    "Nobody needs to be called over it yet - it is the standard way to handle it. The point to "
    "get someone is if it does not settle.",
    "It is the usual handling of a thing like that rather than a warning about it. What would "
    "matter is it getting worse or not shifting.",
    # No line here rules on how bad the thing is. Three months of a landlord's damp gets this pool,
    # and "On its own, no" about that decided something the answer never decided: the fix in it
    # says the thing wants putting right, not that it is nothing.
    "It is a job to do rather than a sign of how bad it is. Do that, and the thing to watch is it "
    "getting worse or not settling.",
)


# A doubt asked over money is not a doubt about a symptom, and the "fix with no warning" pool
# above answers it as one: "i cant pay the rent this month" / "is that bad" was told "It is the
# usual handling of a thing like that rather than a warning about it. What would matter is it
# getting worse or not shifting", which is a thing that might settle rather than a month with a
# hole in it. The rent, a card, a fine and a bill all get that same sentence, and none of them is
# something the person can watch for a week.
#
# What is true of all of them: the number is the problem rather than a fault in the person or the
# thing, and the date on the next letter is what makes it urgent. Nothing here says how it ends or
# what they can afford, and nothing here calls it their fault.
MONEY_TROUBLE_LINES = (
    "Nothing here is broken - it is the money that does not stretch, and that is a thing letters "
    "and calls fix faster than waiting does. What is the first date you have to meet?",
    "It matters, and it is the sort of thing that shrinks as soon as somebody official is told "
    "about it. Ring the one the answer named before the next payment date, not after.",
    "That is a real hole in the month rather than a fault in you. Start with the one the answer "
    "named, and tell me what they say.",
    "It is a squeeze, not a sign that you have done something wrong, and it is the kind that gets "
    "smaller once it is written down. What is the number you cannot meet?",
)


# The words a money line is made of. A noun alone is not a trouble ("i got a pay rise" has wages
# in it), so the line needs one of these and a word that says something is not being met.
MONEY_NOUN_WORDS = frozenset((
    "rent", "money", "bill", "bills", "debt", "debts", "owe", "owed", "arrears", "overdue",
    "loan", "loans", "credit", "card", "cards", "mortgage", "council", "tax", "fine", "fines",
    "energy", "electric", "electricity", "gas", "heating", "water", "payment", "payments",
    "payday", "wages", "pay", "savings", "overdraft", "afford"))


MONEY_NOT_MET = re.compile(
    r"\b(?:cant|can'?t|couldnt|couldn'?t|no|not|nothing|never|behind|missed|miss|late|overdue"
    r"|short|stuck|struggling|struggle|afford|owe|owed|debt|debts|arrears|skint|going down"
    # A fine or an arrears letter is the trouble itself, so it needs no other word: "i got a
    # parking fine for 120 quid" is a month that has just got worse, not a fault to be watched.
    r"|cut|reduced|behind on|fine|fines|fined|penalty|penalties|repossession|evicted|eviction"
    # A card turned down at the till is the money failing in public, and it was told to watch it.
    r"|bailiffs|declined|decline|refused|bounced|overdrawn|overdraft)\b")


# "pay" is in the noun list because "i cant pay my mate back" is money, and the one verb it belongs
# to that is not money is "pay attention": that line was answered "That is a real hole in the month
# rather than a fault in you", which is a sentence about a person's bank balance.
NOT_MONEY_PAY = re.compile(r"\bpay(?:s|ing|ed)?\s+(?:attention|heed|respects?|tribute|homage|"
                           r"lip\s+service|a\s+visit|a\s+call|compliments)\b", re.I)


# Somebody else's money is theirs: "my son has run up a bill" is still a money doubt, so this is
# only used to keep a doubt about somebody's health off the money pool.
A_BODY_IN_THE_LINE = re.compile(
    r"\b(?:pain|ache|hurts?|hurting|sore|swollen|rash|bleeding|lump|cough|fever|temperature|"
    r"vomiting|sick|dizzy|breathless|doctor|gp|hospital|ambulance)\b", re.I)


# Any number at all, for the gate that hands a money line with a figure in it to the comparison.
_A_NUMBER = re.compile(r"\d")


# The answer put a timescale on watching it, and the person has already been living with it longer
# than that. "i wake up soaked in sweat every night for months" / "is that bad" was told "Not the
# thing itself, no. What would change it is you wake drenched for weeks" by the same answer that
# named the weeks, which is a ruling contradicted by its own condition.
MET_LINES = (
    "That answer put a timescale on watching it, and you are already past it. That is the point it "
    "meant, so get it looked at rather than sitting on it.",
    "The answer's own line on this is the timescale, and yours has been going on longer. That is "
    "the bit to act on, and it sounds like it is now.",
    "It said to watch it, and gave the timescale for doing that. You are past the timescale, so it "
    "is past watching - get it seen to.",
)


# An amount of money is not a condition, so nothing here is "ordinary". "i owe 300 on my gas bill" /
# "is that bad" was answered "That one is the ordinary kind, so no. Watch it rather than worry about
# it: if it's still the same in a week or two..." - a ruling about a symptom given to a question
# about a bill, off the "usually" the money answer spends on tariffs rather than on the fault. The
# question the person is really asking is whether the number is too big, and the answer's own
# comparison is the only thing that settles that, so the line hands them the comparison.
# Whether a figure is a lot is not a fault and not a symptom, and it is the one doubt the body
# readings below answer worst: "im looking at a gym near work" / "its 45 a month" / "is that a lot"
# was told "Sounds good.", and "my electricity is 180 a month" / "is that a lot" was told "Alright
# then - good luck with it". Both are the bot agreeing with a price it never weighed.
#
# Nothing here knows what a gym or a unit of electricity costs, so nothing here says a number is
# high or low. What it can say is what the number comes to over a year, which is the figure that
# actually gets weighed against what the money would otherwise do, and that whether it is a lot
# depends on that comparison rather than on the number alone.
FIGURE_LINES = (
    "Same money every month adds up to a yearly figure, and that is the one to weigh: if a year of "
    "it still feels worth what you would otherwise do with the money, it is not too much.",
    "It is only ever a lot next to something. Put the year's total beside what else that money "
    "would do for you, and the answer usually picks itself.",
    "A monthly figure hides its size. Work out the year, then ask what you get for the year - to "
    "one budget it is loose change and to another it is the whole of the saving.",
)


# The ask for a judgement on a figure. Read before the bare doubts, so a price question keeps the
# money reading: as a bare doubt ("is that a lot" is not in BARE) it fell to the chat floor.
A_FIGURE_ASK = re.compile(
    r"^(?:and |so )?is (?:that|this|it) "
    r"(?:a lot|a lot of money|too much|too much money|too expensive|expensive|cheap|good value|"
    r"about right|a fair price|that much|really that much)"
    r"(?: then| though| or not)?$", re.I)


MONEY_LINES = (
    "That is a figure to compare rather than a fault: the answer above gives the usual one, so put "
    "yours beside it, and if yours is the big one, that is what to change.",
    "Not bad so much as a number to check. The answer above quotes what is usual, and the gap "
    "between that and yours is the bit worth acting on.",
    "Nothing is broken there - it is your figure against the usual one the answer gave. If yours is "
    "the higher of the two, that is the thing to do something about.",
)


# The words a line about an amount of money is made of. Nothing about a body is in here: a body word
# in the line keeps the verdict, because "my back went and the bill was 300" is about the back.
MONEY_WORD = frozenset((
    "bill", "bills", "invoice", "invoices", "rent", "owe", "owed", "owes", "owing", "debt",
    "debts", "tariff", "tariffs", "refund", "refunds", "fare", "fares", "price", "prices",
    "charge", "charges", "charged", "payment", "payments", "paying", "paid", "pay", "cost",
    "costs", "mortgage", "loan", "loans", "overdraft", "insurance", "premium", "premiums",
    "subscription", "subscriptions", "council", "tax", "vat", "fine", "fined", "money",
    "pennies", "quid", "pounds", "dollars", "euros", "pension", "salary", "wage", "wages",
    "budget", "savings", "saving",
))


# A currency amount, with a symbol or a word, which is a figure however the line words it.
A_FIGURE = re.compile(
    r"[\u00a3$\u20ac]\s?\d|"
    # "200 a month", "90 per week": a bare number with the period it is paid over is a figure too,
    # and it is how most people say a bill.
    r"\b\d+(?:\.\d+)?\s*(?:p|quid|pounds?|dollars?|euros?|grand|k)\b|"
    r"\b\d[\d,.]*\s*(?:a|per|each)\s+(?:month|week|year|fortnight|day)\b",
    re.IGNORECASE)


A_COMPARISON = ("usual", "usually", "typical", "typically", "compare", "compares", "average",
                "on average", "benchmark")


# "is that just age" asks the one thing the answer above did not say: whether what the person
# is seeing is ordinary. The referral pool cannot say it ("Yes, that one wants a proper look") and
# the ordinary pool cannot either, because the honest reply starts "often it is, and the change is
# the part to watch". So the form has its own lines.
JUST_AGE = re.compile(
    r"\b(?:just|only)\b[^.!?]{0,24}\b(?:age|a phase|a stage|tiredness|the tiredness)\b",
    re.I)


AGE_LINES = (
    "Often it is age, and the thing that is not ordinary is a change: slower than before is usual, "
    "new or getting worse is the part to get looked at.",
    "Some of that is ordinary at that age. What is worth a word with the GP is a change - something "
    "that came on recently, or that keeps getting worse.",
    "Mostly age, as a rule, and it is the change that settles it rather than the thing itself: "
    "suddenly different, or worse each month, is the point to ask someone about it.",
)


def _a_figure_owed(line):
    """Whether the person's line is an amount of money rather than a condition of a body."""
    if not line:
        return False
    words = [w.replace("'", "").lower() for w in re.findall(r"[A-Za-z\u00a3$\u20ac']+", line)]
    if any(word in BODY_WORD for word in words):
        return False
    if any(word in MONEY_WORD for word in words):
        return True
    return A_FIGURE.search(line) is not None


# A state the person named themselves, when nothing in their line is a body: "i feel really low",
# "im so tired", "i cant stop crying", "ive been feeling flat all week". The answer above one of
# these is a warm chat line rather than a knowledge answer, so the fault readings below have
# nothing to read and the turn fell to the sign-off floor - "Glad to hear it." after "i feel
# really low", "Alright then - good luck with it." after "is that bad" - or to the search hedge.
#
# A mood is not a fault to be diagnosed and not a thing to look up. It is what a hard stretch does
# to a person, it lifts slowly, and the one thing worth naming is the sign that says ask for a
# hand. Nothing here says what the cause is and nothing here promises a date. The state the person
# named picks the family, because the sentence that is true after "im so tired" is not the one that
# is true after "i cant stop crying", and one pool for all of them gave five different weeks one
# identical line.
BODY_WORD = frozenset((
    "pain", "ache", "aches", "aching", "sick", "ill", "nauseous", "nausea", "dizzy", "headache",
    "temperature", "fever", "breathless", "throat", "chest", "stomach", "arm", "leg", "legs",
    "back", "knee", "hand", "foot", "feet", "head", "tooth", "toothache", "cough", "cold", "flu",
    "rash", "lump", "bleeding", "bleed", "blood", "itch", "itching", "swollen", "cramp",
    "period", "surgery", "pill", "pills", "tablet", "tablets", "dose",
))


# Somebody else in the line means the state is theirs, and "my son is worn out" is not a doubt
# about the person asking.
SOMEONE_ELSE = frozenset((
    "son", "daughter", "child", "children", "kid", "kids", "baby", "mum", "mom", "dad", "mother",
    "father", "wife", "husband", "partner", "boyfriend", "girlfriend", "sister", "brother",
    "friend", "gran", "grandad", "grandma", "grandpa", "nan", "colleague", "boss", "dog", "cat",
))
