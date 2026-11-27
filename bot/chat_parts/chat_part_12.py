"""Part 12 of 17 of the small-talk reply module, split out of `chat`.

Everything here is re-exported from `chat`, so callers import it from there as before.
"""
import re

from ..compose import nearly, negated, pick
from ..compose.badnews import reads_like_a_symptom
from ..compose.goodnews import reply_for_a_win_from_a_past_year
from ..understanding import breeds
from ..understanding.kinds import shortage_of
from ..compose import loss as loss_reading
from ..compose import onscreen
from ..compose import harm as harm_reading
from ..compose import urgent as urgent_reading

from ..memory import ack
from ..memory import stuck as stuck_line
from ..memory.topics import in_a_safety_thread as _safety_thread

from .chat_part_01 import (
    _a_thread_to_come_back_to,
)
from .chat_part_02 import (
    NEWS_REPLIES, AT_IT, AWAKE_SINCE, AWAY_WORDS, BID, ERRAND, HOME_AGAIN, IN_BED, LEAVING,
    LOST_ONLY, PAUSE, PRESENCE, RETURNED, STUCK_FEELING, STUCK_ON_A_FORM, STUCK_ON_A_THING,
    UNDERWAY, _HOW_LONG_AT_IT, VERDICT_POOR, VERDICT_WELL, WENT_BAD_WEATHER, WENT_TO,
    WENT_TO_COMPANY, WENT_TO_SEE, WENT_TO_SEE_COMPANY, WATCHED_DESCRIBER, WATCHED_THINGS, WENT_WELL,
    WENT_WRONG, _poor_word, BACK_FROM, BEEN_TO, NOT_A_PLACE_START, TRIP_NOT_YET, WENT_TO_ANY,
    _not_a_night_out, SAID_POOR,
)
from .chat_part_03 import (
    ANNOUNCED_ONE, ASKED_ABOUT_THE_BOT, FEELINGS, FEELING_LEAD, FEELING_SELF, FLAT_IDIOM,
    GUILT_DEED, LOW_THING, MOOD_FOR, NEWS_AFTER, NOT_HAPPY_ABOUT, NOT_LANDED, NOT_MYSELF, NOT_WORDS,
    REGRET_DEED, SELF_INSULT, SICK_DEED, SLEEP_WORD, SPENT_MONEY, TIRED_DESPITE_SLEEP,
    TIRED_PERSISTENT, _a_thing_in_front, _denies_an_earlier_word, _negated,
    _without_the_feeling_avoided, _asked_about_the_effort,
)
from .chat_part_04 import (
    REPLIES, said_loss, ABILITY_WORDS, ROUGH_DAY, WHAT_A_DAY, WORRY_EVENT, WORRY_FEELING,
    WORRY_PERSON, _a_stretch_that_drags,
)
from .chat_part_05 import (
    AHEAD, CHEER_IN_LOSS, CHEER_KINDS, NEEDS_AHEAD, _the_lost_thread_asked,
)
from .chat_part_06 import (
    FIRST_LINE_POOL, _mid_chat, _says_the_time_of_day, _thanks_that_fit, _the_part_of_day,
    EMOTION_FEELING, LOST_THE_THREAD, PANIC_NOW, PANIC_SOMEONE_ELSE, SELF_CUE, THING_OF,
    _bare_feeling, _without_skills, _worry_kind,
)
from .chat_part_07 import (
    _the_weight_said, LONELY_STEP_WORDS, NOTHING_HELPING, _nothing_helped_just_before,
    A_FACULTY_GETTING_WORSE, A_QUESTION_ABOUT_A_FIGURE, GUILT_WORDS, LEFT_BEHIND, MAD_ABOUT_THE_DAY,
    MOVED_BY, MOVED_BY_PART, MY_TEARS, NOT_WANTING_IT, OWN_MEMORY_OFF, RELIEF_SAID, STATE_WHEN,
    _a_low_word, _apart_from_people, _as_said, _bad_day, _hard_about_their_thing, _own_state,
    _says_relief, _scattered, _weeping,
)
from .chat_part_08 import (
    _a_low_just_before, _going_on, _my_own_tears, _tears_said_as_a_verb,
)
from .chat_part_10 import (
    _not_coping, _says_how_the_person_is,
)
from .chat_part_11 import (
    _confusion_names_a_thing, _note_the_pool, _the_not_knowing_has_a_subject, _place_values,
    _the_thing_this_line_names, _the_poor_describer, _tidy, _trip_place, _a_good_time_they_had,
    _the_detail_of_the_good_time,
)


def _after_a_lost_thread(clean, understood, memory):
    """The line that picks the thread up, when the one before it was the lost-thread question.

    A follow-up that names nothing of its own ("i thought i had it and now i dont") has no
    answer of its own, and the question has already been asked once, so the reply asks where it
    slipped. A line that does name something, asks something, or names a feeling keeps its own
    answer: "the morning one is white and the evening one is blue" is not this, and a hello
    after the question is still a hello.
    """
    if not isinstance(memory, dict):
        return None
    note = memory.get("lost_thread")
    if not isinstance(note, dict):
        return None
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return None
    if note.get("turn") != len(turns) - 1:
        return None
    if (not isinstance(understood, dict) or understood.get("kind") != "statement"
            or understood.get("emotion") or understood.get("asks")):
        return None
    if _confusion_names_a_thing(understood):
        return None
    words = re.findall(r"[a-z']+", str(clean or "").lower())
    # A bare "yes", "no" or "what" is an answer to the question, not the rest of the thing they
    # could not follow, and asking it again is nagging.
    if len(words) < 3 or len(words) > 14:
        return None
    return _reply("lost_thread_more", memory, None, " ".join(words))


def _reply(kind, memory, name=None, seed=""):
    # One check for every pool: a line that talks about the conversation is not a reply to its
    # first line. It is made before the pool is read, so every kind that has such a line is
    # covered without a guard in each branch (`bot/compose/onscreen.py` says what counts as
    # talking about the conversation, and why it is read once).
    if not _mid_chat(memory):
        kind = FIRST_LINE_POOL.get(kind, kind)
    # A hello two turns into a conversation is a check-in, not a new morning: the cheerful
    # first-line pool would be bright two lines after bad news.
    if kind == "greeting" and _mid_chat(memory) and not _says_the_time_of_day(memory):
        if name:
            return pick([o.format(name=name) for o in REPLIES["check_in_name"]], memory, seed)
        return pick(list(REPLIES["check_in"]), memory, seed)
    if kind == "howareyou" and _mid_chat(memory):
        if said_loss(memory):
            # A loss is already on the table: answer the question gently, and do not send a
            # bereaved person off to "What's next?".
            return pick(list(REPLIES["howareyou_loss"]), memory, seed)
        return pick(list(REPLIES["howareyou_mid"]), memory, seed)
    part = _the_part_of_day(memory)
    if kind == "greeting" and part:
        return pick(list(REPLIES["greeting_" + part]), memory, seed)
    # Every reply taken from a pool passes here, so this is the one place that knows which pool
    # the person's answer came from: it is where a heavy one is noted for the turn after it, and
    # where the lost-thread question is noted so the line after it can pick the thread up.
    _the_weight_said(memory, kind)
    _the_lost_thread_asked(memory, kind)
    options = REPLIES[kind]
    if not _mid_chat(memory):
        # A pool with one line about the conversation in it ("Where were we?") keeps its other
        # lines for a first line; a pool where every line is like that is left as it is, because
        # a reply has to be given, and the pools that are all like that are mapped above.
        fresh = [o for o in options if not onscreen.talks_about_the_conversation(o)]
        options = fresh or options
    if kind == "thanks":
        options = _thanks_that_fit(options, memory)
    if name and kind == "greeting":
        options = REPLIES["greeting_name"]
    if kind in CHEER_KINDS and _a_death_just_said(memory):
        # A death in the thread stands the celebration down before anything else picks a line:
        # "my mum died last night" / "great" is not a line to be glad about. The window is the
        # turn or two after the death, not the whole chat: a bereaved thread still has a good
        # thing happen in it three days later.
        options = CHEER_IN_LOSS
    elif kind in ("happy", "anxious"):
        # The line that names what is coming up is the one that fits a line saying what is coming
        # up, so it is chosen there and taken out everywhere else.
        fits = [o for o in options if o in NEEDS_AHEAD]
        if AHEAD.search(str(seed)):
            options = fits or options
        else:
            options = [o for o in options if o not in NEEDS_AHEAD] or options
    # The person's own line seeds the choice where the caller has it: two different lines
    # answered from one pool should not get the same sentence just because both are turn one.
    text = pick([option.format(name=name) for option in options], memory, seed)
    return text


def _after_lonely(clean, memory):
    """The step asked for straight after a lonely reply, if that is what this line is."""
    if not isinstance(memory, dict):
        return None
    note = memory.get("heavy_reply")
    if not isinstance(note, dict) or note.get("feeling") not in ("lonely", "lonely_apart"):
        return None
    turns = memory.get("turns")
    if not isinstance(turns, list) or not turns:
        return None
    if note.get("turn") != len(turns) - 1:
        return None
    words = re.findall(r"[a-z']+", " ".join(str(clean or "").lower().split()))
    if not words or len(words) > 7:
        return None
    if any(word not in LONELY_STEP_WORDS for word in words):
        return None
    if not ({"what", "how"} & set(words)) or "do" not in words:
        return None
    return _reply("lonely_step", memory, None, " ".join(words))


def _nothing_helps(clean, memory):
    """The answer to "nothing helps" straight after a low the person has just described."""
    if not NOTHING_HELPING.search(clean):
        return None
    if not (_a_low_just_before(memory) and len(clean.split()) <= 8
            or _nothing_helped_just_before(memory, clean)):
        return None
    return _reply("nothing_helps", memory, None, clean)


def _feeling(clean, understood=None, bare=None, kept=False):
    """The feeling the line names, if it is about how the person feels.

    `kept` says the line is shaped "i keep <feeling>" (KEEPS_HOW_THEY_ARE), which is a cue the
    mood is the speaker's in its own right: "i keep crying", "i keep getting upset".
    """
    # The worry matchers tell a person from an event by the little word in front of it, so a line
    # typed at speed has to be read with its slips undone: "im worried bout my mum" has no
    # "about" in the words as typed, so the person read as nothing at all and the line got the
    # nerves-before-something-big reply, cold on a line about a mother. `plain` is the line with
    # only the words that were wrong repaired, and it is what the README says a matcher reads.
    clean = _as_said(clean, understood)
    clean = _without_the_feeling_avoided(clean, understood)
    if harm_reading.reads_as_hurting_someone(clean):
        # A mood word in front of a doing is the frame the wish came in, not the feeling to
        # answer: "im scared im going to shake the baby" got "That sounds unsettling. Is there
        # one thing you can check or ask about that would settle it?" while the harm card for
        # exactly that line was one module away. The harm reading answers it, so this stands down.
        return None
    if isinstance(understood, dict) and understood.get("a_load_carried"):
        # The reading says the person is the one holding it all up for everybody else, and a line
        # like that has no feeling word in it to key a pool: "im always the one who organises
        # everything" was answered with a shrug. It is kept apart from the pools until the
        # knowledge base has been asked, because a card can say something a pool cannot ("i feel
        # like i do everything at home" wants one named job on one named day) and that card must
        # keep the turn.
        return "carrying"
    if ack.a_limit_on_the_plan(clean):
        # A limit on the plan denies nothing about how the person is: "nothing too tiring" and
        # "no long walks" reach the negation rules below as a denied feeling and were answered
        # "Fair enough - what's going on, then?". They are the ack's line, not a mood.
        return None
    if A_QUESTION_ABOUT_A_FIGURE.search(_as_said(clean, understood)):
        # "is that too low" asks about a figure the answer above gave - a boiler pressure, a tyre,
        # a reading - and "low" there is the number, not how the person feels. The sad pool
        # answered it ("That's a heavy feeling, and it's fair to have it. Be kind to yourself
        # today.") to somebody asking whether 1 bar is low enough, and the same to "my tyre is a
        # bit soft / is that too low". The words without the question are still a mood ("im low",
        # "i feel low"), which is why the guard is the question and not the word.
        return None
    clean = STATE_WHEN.sub(" ", clean)
    if (isinstance(understood, dict) and understood.get("state_owner") not in (None, "self")
            and not FEELING_SELF.search(clean)):
        # The state is somebody else's or a thing's, not the speaker's: "she was just exausted"
        # and "my laptop is knackered" are about the person or the thing, not about how the
        # speaker feels. A mood line speaks for the speaker, so it stands down and the
        # knowledge row answers. A line that says the state in the first person ("she was
        # exausted and i am too") still carries a feeling of the speaker's, so `FEELING_SELF`
        # keeps it.
        return None
    if bare is None:
        bare = _bare_feeling(clean)
    if LOW_THING.search(clean):
        clean = LOW_THING.sub(" ", clean)
    if ((isinstance(understood, dict) and understood.get("shortage"))
            or shortage_of(clean)):
        # The line names a thing that has run out ("im low on milk", "ive run out of tea bags"),
        # so it is the cupboard and not how the person is: the surface cue is still "im low", and
        # the condolence for a low day was going to the person whose milk had run out. Every
        # shortage the reading keeps as a mood ("low on energy", "low on confidence") names one
        # of their own reserves, so it never reaches this line. The words are read again here
        # because a retried line comes back with no reading on it (`as_said=False`).
        return None
    clean = _without_skills(clean)
    if FLAT_IDIOM.search(clean):
        clean = FLAT_IDIOM.sub(" ", clean)
    if ANNOUNCED_ONE.search(clean):
        rest = ANNOUNCED_ONE.sub(" ", clean)
        if NEWS_AFTER.search(rest):
            # The opener carries a word of mood of its own and `bare` was read before it came
            # out, so the mood word has to be read again from what is left of the line.
            clean = rest
            bare = _bare_feeling(clean)
    if MOOD_FOR.search(clean):
        clean = MOOD_FOR.sub(" ", clean)
    if ((MOVED_BY.search(clean)
         or (MY_TEARS.search(clean) and MOVED_BY_PART.search(clean)))
            and not _a_low_word(clean)):
        # The tears are the person's own and something built to move them did it, so the answer
        # is about the thing they were moved by rather than about a low or a film to watch.
        # A line that names its own bad day too ("i feel awful and i keep crying at films") is
        # the low, and the pools below answer it.
        if (_my_own_tears(clean) and not NOT_WANTING_IT.search(clean)
                and not _bad_day(clean) and not ROUGH_DAY.search(clean)):
            return "moved"
        return None
    tears = _tears_said_as_a_verb(clean)
    if tears:
        return tears
    if _weeping(clean):
        # Not the sad pool: its lines are written for a low that has been there a while, and the
        # one a person landed on was a suggestion to go for a walk.
        #
        # Tears that come every day are not today's tears. "i want to cry every day", "all the
        # time", "most days", "constantly" were answered below with "that long is worth a proper
        # look ... book the GP", and the tears pool took that away. The line is still read as the
        # low it is, so the weeks-of-it pool gets it: `_going_on` is that pool's own reading, and
        # it already refuses a mood that belongs to somebody else ("my husband is angry all the
        # time" is his line, not hers).
        return "sad" if _going_on(clean) else "tears"
    if NOT_WANTING_IT.search(clean) and not _a_low_word(clean):
        # "im trying not to cry" is a fight against it, not a grief, and the condolence line
        # reads as if they had said the opposite. It wants the gentle listening line instead.
        # A line that also names a mood of its own ("i feel awful and i dont want to cry")
        # keeps that mood and is answered as one.
        return None
    asked = ASKED_ABOUT_THE_BOT.search(clean)
    mine = FEELING_SELF.search(clean)
    if asked and (mine is None or asked.start() < mine.start()):
        return None
    if SELF_INSULT.search(clean) and FEELING_SELF.search(clean):
        return "sad"
    if _not_coping(clean):
        # Not the sad pool: it is written for a named mood, and "be kind to yourself today"
        # is thinner than what a person who says they are not coping has just told us.
        return "not_coping"
    if _bad_day(clean):
        return "bad_day"
    if _apart_from_people(clean):
        # Contact lost is loneliness said without the word, and the lonely pool's "a weekly club
        # is the quickest way to see the same faces" presumes a stranger they have not met yet.
        return "lonely_apart"
    if _a_stretch_that_drags(clean):
        # A week that will not move is not a bad day: the rough-day pool's shower and early night
        # answers a day that went wrong, and these lines have had nothing go wrong in them.
        return "long_stretch"
    if ROUGH_DAY.search(clean) or WHAT_A_DAY.search(clean):
        return "rough_day"
    if _scattered(clean):
        # A mind that will not settle is not a day that went badly: the practical reply is about
        # closing loops, not about an early night. It is read before `bare` because "im scattered"
        # is exactly a bare feeling, and no pool below has a line for it.
        return "scattered"
    if bare and not PANIC_NOW.search(clean):
        # "bored tbh" is a feeling with no subject but the speaker. A panic attack is a feeling
        # word too, but the anxious pool it would land in presumes something big is coming up.
        return bare
    # "i havent felt myself" is the low day even though no mood adjective follows a "feel".
    if NOT_MYSELF.search(clean):
        return "sad"
    if (PANIC_NOW.search(clean) and not PANIC_SOMEONE_ELSE.search(clean)
            and not negated(clean, "panic")):
        # "im having a panic attack" is not the anxious pool: that one presumes something big is
        # coming up, and a person mid-attack has a body to settle first.
        return "panic"
    read = None
    if isinstance(understood, dict) and (SELF_CUE.search(clean) or LOST_THE_THREAD.search(clean)
                                         or understood.get("state_owner") == "self"):
        # The reading names a mood of the speaker's own, whether the line spells it "im" or
        # through a part of them: "my heart is broken" is the same state as "im heartbroken",
        # and it was answered "I'm listening - say more if it helps" because this gate only
        # looked for the "im" frame in the words; "could be better" is a low with no word of
        # mood in it at all. The engine says whose state it is, so the shape of the sentence
        # is not what decides.
        read = EMOTION_FEELING.get(understood.get("emotion"))
        if read and (A_FACULTY_GETTING_WORSE.search(clean) or OWN_MEMORY_OFF.search(clean)) \
                and _answers_knows(clean, {"turns": []}):
            # The state word is about a part of them, not about them: "my memory is getting
            # worse" is a card, not a rough day, and "should i be worried about my memory" is a
            # question about the memory rather than a worry with no end date on it. Whichever
            # pool the reading fell into, the card that answers the part has the turn. Only when
            # a card actually answers it, because a pool line is warmer than the listening line
            # for a body part nothing covers yet.
            read = None
        if read == "confused" and _confusion_names_a_thing(understood):
            # The line names a thing of its own, so the thing is the answer: "im confused why my
            # boiler won't light" wants the boiler and "im confused about my medication" wants
            # the medication row, and a pool line that asks them to explain the confusing bit
            # takes that away. Read on the words the line names rather than on the topic,
            # because a feeling word takes the topic ("im confused about my medication" is read
            # as feelings) while the thing named is still there and still answerable.
            read = None
        if read and understood.get("state_owner") not in (None, "self"):
            # The mood is a thing's or somebody else's, not the speaker's: "i have a houseplant
            # that looks sad" wants the answer about the plant, and "i dont understand why shes
            # angry" wants the line about her, not "Annoying. Walk it off for ten minutes before
            # you reply to her", which tells the wrong person to cool off. A pool line speaks
            # for the speaker, so it stands down unless the reading says the state is theirs.
            # The reading says whose state the word is (bot/understanding/kinds.py), so the line
            # is not read again here.
            read = None
        if read and nearly(clean, read):
            # "im almost happy" is not a happy line, the same way "i nearly finished it" is not
            # a thing to congratulate: the reading names the feeling and the cue undoes it.
            read = None
        if read == "anxious" and THING_OF.search(clean):
            read = _worry_kind(clean)
        if read == "happy" and _says_relief(clean):
            # "im relieved hes gone" is the relief and not the celebration: the emotion is happy
            # in the engine's lexicon and the cue reader found no feeling word of its own in the
            # line, so the happy pool answered a death with "anything nice planned".
            read = "relieved"
        elif read == "happy" and RELIEF_SAID.search(clean) and negated(clean, "relieved"):
            # "im not relieved" names the weight and says it has not come off yet, so the line is
            # a low and not a good feeling. The denial was read by the happy group in FEELINGS
            # ("denying a good feeling is a low one"); relief has its own reading now, and the
            # emotion reader reaches the happy pool with no denial on it, which said "that's a
            # good feeling to carry into the rest of the day" to a person still waiting.
            read = "sad"
        if read == "annoyed" and MAD_ABOUT_THE_DAY.search(clean):
            # The engine reads "mad" as the speaker's anger, and a day being mad is how busy it
            # was: "work was mad today" came back "Annoying. Walk it off for ten minutes before
            # you reply to anyone", which puts a second person in a line that has none. The
            # reading stands down here and the busy pool asks what is taking most of it - the
            # same trade the loop below makes for the same word, because a line can reach the
            # annoyed pool through the engine's emotion as well as through the words.
            read = "busy"
    if not (FEELING_SELF.search(clean) or FEELING_LEAD.search(clean) or read
            or _own_state(clean) or kept or _hard_about_their_thing(clean)
            or REGRET_DEED.search(clean)):
        return None
    # A denied guilt is not guilt: "im not feeling guilty about cancelling" is a line about it
    # not sitting heavy, so the denial is read on the guilt family's own words before the deed.
    if not any(_negated(clean, word) for word in GUILT_WORDS):
        if GUILT_DEED.search(clean) or SICK_DEED.search(clean):
            return "guilty"
    # "i dont regret what i said" is a denial of the guilt, and the regret pool would read it as
    # the confession: the verb is negated, so the deed after it is not one they are sorry for.
    if REGRET_DEED.search(clean) and not _negated(clean, "regret"):
        return "guilty"
    denied = False
    denied_names = set()
    for name, words in FEELINGS:
        for word in words:
            match = re.search(r"\b" + re.escape(word) + r"\b", clean)
            if (match and not _a_thing_in_front(clean, word)
                    and _says_how_the_person_is(clean, word, match)):
                if word.split()[0] in NOT_WORDS:
                    # The cue is already the denial itself ("not ok", "not fine"), so a negator
                    # further back denies the denial, not the feeling: "no really im not fine" is
                    # emphatically not fine. Read as a denial of a low it got "Noted, and good.",
                    # the one reply that line must never get.
                    return name
                if _negated(clean, word):
                    if name == "happy":
                        # "im not happy" and "i dont feel great" are not a denial of a problem,
                        # they are the problem: denying a good feeling is a low one. Aimed at a
                        # thing ("not happy about the service") it is a complaint, not a mood.
                        return "annoyed" if NOT_HAPPY_ABOUT.search(clean) else "sad"
                    denied = True  # "im not tired" says the opposite: read the next feeling
                    denied_names.add(name)
                    continue
                if word in ABILITY_WORDS and re.search(
                        r"\b" + re.escape(word) + r"\s+(?:at|with)\b", clean):
                    continue
                if name == "anxious" and WORRY_FEELING.search(clean):
                    kind = _worry_kind(clean)
                    # A worry said about the body is about the body: "my throat hurts and i keep
                    # losing my voice, should i worry" is a symptom question, and the nerves
                    # pool's line ("nerves before something big are normal") reads as if the
                    # throat had not been mentioned at all. The body pools answer it (badnews
                    # reads the symptom), so this reading stands down.
                    if reads_like_a_symptom(clean):
                        continue
                    # A worry the person says is their own, with no event in it ("my worry is i
                    # wont finish in time"), is not nerves before something big: the reply that
                    # presumes a date reads as if they had not been listened to.
                    if kind == "anxious" and _own_state(clean) and not WORRY_EVENT.search(clean):
                        kind = "worry"
                    return kind
                # "i'm stressed about my mum" is the same worry as "worried about my mum", and
                # "write it all down and do the smallest item" answers the wrong thing. The same
                # goes for every fear word in the group: "im terrified of my husband" was an
                # answer about the husband until "terrified" joined "anxious", and the "what if"
                # list then read as if the person had not been named at all. A person in the line
                # outranks the group the fear was filed under.
                if name in ("anxious", "stressed") and WORRY_PERSON.search(clean):
                    return "worry_person"
                if (name == "annoyed" and word == "mad"
                        and MAD_ABOUT_THE_DAY.search(clean)):
                    # A day being mad is how busy it was, not anger at somebody: the reading
                    # stands down and the line is left to the busy pool, which asks what is
                    # taking most of it instead of telling them to cool off before replying.
                    continue
                if word in ("tired", "bored", "done") and re.search(
                        r"\b" + re.escape(word) + r"\s+(of|with)\b", clean):
                    # "tired of everything" is low mood about the whole thing, not annoyance
                    # at one person or one job, so it gets the heavier reply.
                    if re.search(r"\b" + re.escape(word) +
                                 r"\s+(of|with)\s+(everything|anything|it all|life|the lot|"
                                 r"the world|myself)\b", clean):
                        return "sad"
                    return "annoyed" if word != "bored" else "bored"
                # A tiredness with a "when" or a "why" in it is the knowledge entry's line.
                if name == "tired" and (TIRED_PERSISTENT.search(clean) or (
                        TIRED_DESPITE_SLEEP.search(clean) and SLEEP_WORD.search(clean))):
                    return None
                # "im spent up this month" is money, and main noted it as the fact it is: the
                # advice about an early night is for the other sense of the word.
                if word == "spent" and SPENT_MONEY.search(clean):
                    continue
                # "im not feeling great" is not a happy line, and neither is "im not happy".
                # A negator in front of a good feeling word turns it into a bad one; the
                # sad pool is the mild one, so it fits "not great" without being heavy.
                if name == "happy" and negated(clean, word):
                    return "sad"
                if negated(clean, word) and not _denies_an_earlier_word(clean, word):
                    denied = True
                    denied_names.add(name)
                    continue
                # "im almost happy" is not a happy line, and "i nearly cried" is not the sad one.
                if nearly(clean, word):
                    continue
                if name == "happy" and NOT_LANDED.search(clean):
                    # "im happy but i dont feel it" is a mood that did not land, whatever is
                    # behind it, so the sad reading wins over the news one.
                    return "sad"
                if name == "happy" and ack.has_news(clean) and not LEFT_BEHIND.search(clean):
                    # "im in a good mood because i got the job" is a job as well as a mood, and
                    # the news it carries is what the person wants answered: the happy pool
                    # answers a mood with nothing behind it. The ack module stands aside on the
                    # same test (bot/memory/ack.py), and the news reader below answers the line.
                    #
                    # Except a ward they have left: "im glad, my mum is out of hospital" is an
                    # event, and standing aside handed the word "hospital" to the worry reader,
                    # which said "That is a worrying place for your mum to be" about a woman who
                    # had just come home. The mood reply it had is better than that.
                    return None
                return name
    if denied and not (read and read not in denied_names):
        # A denial is only the whole line when nothing else in it names how they are. "im not
        # hungover just tired" corrects the bot about one feeling and gives it another, and the
        # reading already has that other one: the pool for it is the answer, not the flat
        # acknowledgement a pure "im not tired" wants.
        return "not_feeling"
    return read


def _say(kind, memory, **values):
    """One wording of a reply kind, rotating and never repeating the last few replies."""
    if not _mid_chat(memory):
        # The same one check as `_reply`, for this pool as well: `returned` is "back again, where
        # were we", which is a greeting when nothing has been said yet, and a line of any other
        # pool that refers to something said before is passed over in favour of one that does not.
        opening = FIRST_LINE_POOL.get(kind)
        if opening:
            return _reply(opening, memory)
        fresh = [o for o in NEWS_REPLIES[kind]
                 if not onscreen.talks_about_the_conversation(o)]
        if fresh and len(fresh) < len(NEWS_REPLIES[kind]):
            return pick([o.format(**values) for o in fresh], memory)
    if kind in CHEER_KINDS and _a_death_just_said(memory):
        # "my nan passed away in june" then "i got the job" got "That's brilliant. Nice one!"
        return pick(list(CHEER_IN_LOSS), memory)
    options = [option.format(**values) for option in NEWS_REPLIES[kind]]
    if kind == "good_news":
        _note_the_pool(memory, kind)
    return pick(options, memory)


def _cheer_or_the_question(flat, memory):
    """The cheer for a win, or the question a win from a past year deserves instead.

    The congratulations pool greets news as if it had just arrived, so a line that puts its win in
    1998 was congratulated on something twenty years old. It is read here rather than below
    because this is where the pool is chosen: a module lower down can replace a line, but not one
    that was never its to give.
    """
    years_back = reply_for_a_win_from_a_past_year(flat)
    if years_back:
        _note_the_pool(memory, "good_news_gone_by")
        return years_back
    return _say("good_news", memory)


def _conversation(clean, tokens, memory):
    """Presence checks, a pause, coming back, a bid for attention, leaving and getting home."""
    if len(tokens) > 8:
        return None
    flat = clean.replace("'", "").strip(" .,!;:")
    if _safety_thread(memory):
        return None
    # The thing they are stuck on is read before the not-knowing: a form and a cv are not the
    # not-knowing, they are one part of a job that will not move, and the reply names the part.
    if STUCK_ON_A_FORM.match(flat):
        return _say("on_a_form", memory)
    if STUCK_ON_A_THING.match(flat):
        return _say("on_the_thing", memory)
    if STUCK_FEELING.match(flat):
        return _say("a_stuck_feeling", memory)
    if AT_IT.match(flat):
        return _say("at_it", memory)
    if _HOW_LONG_AT_IT.match(flat) and _asked_about_the_effort(memory):
        return _say("the_long_haul", memory)
    if LOST_ONLY.match(flat) and not _the_not_knowing_has_a_subject(memory) \
            and not stuck_line._the_answer_gave_a_step(memory):
        # Unless there is already a subject on the table. "i lost my job on friday", then "i dont
        # know what to do", is a person asking what to do about the job, and main answers it from
        # the job ("Money has dates, so start there: what the last pay and any notice money come
        # to"). Asking "what's the situation?" instead throws that answer away and makes them say
        # again what they have just said. The same goes once the answer has named a first step:
        # "i want to sort my sleep out", then "i dont know where to start", wants that step back.
        # A line that is only the not-knowing is the first line of the conversation, or the line
        # after a nod, and there the question is the one thing a friend can say.
        return _say("lost", memory)
    if PRESENCE.search(flat):
        # "still there" one turn after an answer is the thing again - "i have a headache" then
        # "still there" is the headache - and the store reads it as the report it is.
        from ..memory import tried as not_moved
        if not not_moved.still_going_on(clean, memory):
            return _say("presence", memory)
    if PAUSE.search(flat):
        return _say("pause", memory)
    if RETURNED.search(flat) and not AWAY_WORDS.search(flat) \
            and _a_thread_to_come_back_to(memory):
        return _say("returned", memory)
    if BID.search(flat):
        return _say("bid", memory)
    if HOME_AGAIN.search(flat) and not AWAY_WORDS.search(flat):
        return _say("home_again", memory)
    if LEAVING.search(flat):
        # Going to bed is not going out: "have a good one, what's on today?" fits a shift, not
        # someone saying goodnight.
        if re.search(r"\b(?:bed|sleep|sleeping|kip|nap)\b", flat):
            return _say("leaving_bed", memory)
        return _say("leaving", memory)
    if UNDERWAY.search(flat):
        return _say("underway", memory)
    if IN_BED.search(flat):
        return _say("in_bed", memory)
    awake = AWAKE_SINCE.search(flat)
    if awake:
        return _say("awake", memory, when=awake.group("when").strip())
    chore = ERRAND.search(flat)
    if chore:
        return _say("chore", memory, what=chore.group("what").strip())
    return None


def _about_the_night_out(clean, tokens, memory):
    """A verdict on the place they mentioned last turn ("it was lovely", "it was quiet"), or None."""
    seen = memory.get("night_out") if isinstance(memory, dict) else None
    if not isinstance(seen, dict) or not seen.get("place"):
        return None
    # Only the turn right after my question: a verdict three turns later is about something else.
    if len(memory.get("turns") or []) != seen.get("turn", -9) + 1:
        return None
    if clean.endswith("?") or not 1 <= len(tokens) <= 8:
        return None
    # A line that says where they went or what they watched names a night of its own, so it is
    # not a verdict on the one before it: "we went to a terrible gig last night" after a film
    # would otherwise come back "Shame about a film", a thing the person did not just say.
    if (WENT_TO_SEE.search(clean) or WENT_TO_SEE_COMPANY.search(clean)
            or WENT_TO.search(clean) or WENT_TO_COMPANY.search(clean)):
        return None
    # "the match was terrible" is about the match, whatever the last turn named: a verdict on a
    # thing they say for themselves is answered about that thing.
    own_thing = _the_thing_this_line_names(clean)
    named = "the " + own_thing if own_thing else seen["place"]
    values = _place_values(named)
    if VERDICT_WELL.search(clean):
        return _say("night_out_well", memory, **values)
    # The weather the trip got comes before a general verdict, because "it was freezing" is about
    # the weather there and the pool for it can answer about the place.
    if WENT_BAD_WEATHER.search(clean):
        return _say("night_out_weather", memory, **values)
    if VERDICT_POOR.search(clean):
        return _say("night_out_poor", memory, **values)
    return None


def _saw_something(flat, memory):
    """A film, a match or a gig they went to and came back from, or None.

    The thing they watched is read back to them, so "we went to see a film last night" gets a
    question about the film instead of "Thanks for telling me". A line that already says how it
    went is left to the pool that answers that.
    """
    match = WENT_TO_SEE.search(flat) or WENT_TO_SEE_COMPANY.search(flat)
    if not match:
        return None
    thing = " ".join(match.group(1).split()).strip(" .,!;:")
    words = [w for w in thing.split() if w not in {"the", "a", "an"}]
    # "a good film" and "a really good film" are the thing behind the describer, and a line that
    # says how they felt in the middle of it ("i watched a boring film last night") still names
    # the thing: the verdict word is answered by WENT_WRONG/WENT_WELL below, not here.
    said_how = 0
    while len(words) > 1 and words[0] in WATCHED_DESCRIBER:
        words = words[1:]
        said_how += 1
    if not words or words[0] not in WATCHED_THINGS:
        return None
    if said_how:
        # They have said how they found it already, so the thing is asked about by name only:
        # "A really good film - any good?" is a reply to something they did not say.
        named = _tidy(" ".join(w for w in thing.split() if w not in WATCHED_DESCRIBER))
        if isinstance(memory, dict):
            memory["night_out"] = {"place": named, "turn": len(memory.get("turns") or [])}
        poor_describer = _the_poor_describer(thing)
        if poor_describer:
            # "i watched a rubbish film last night" already says how it went, so "what was it?"
            # is a question they have half answered.
            return _say("saw_it_poor", memory, p=poor_describer,
                        X=named, x=named[:1].lower() + named[1:])
        return _say("saw_it_told", memory, X=named, x=named[:1].lower() + named[1:])
    named = _tidy(thing)
    poor = _poor_word(flat)
    if poor:
        # "we watched the match last night and it was dead boring": the thing and the word they
        # used for it are answered, the same way the verdict after my question is.
        return _say("night_out_poor_said", memory, p=poor, P=poor[:1].upper() + poor[1:],
                    X=named, x=named[:1].lower() + named[1:])
    if WENT_WRONG.search(flat) or WENT_WELL.search(flat):
        return None
    if isinstance(memory, dict):
        memory["night_out"] = {"place": named, "turn": len(memory.get("turns") or [])}
    return _say("saw_it", memory, X=named, x=named[:1].lower() + named[1:])


def _told_a_trip(flat, memory):
    """A trip they told me about by name, answered about the place, or None.

    "we went to lisbon", "i've been to japan", "we got back from spain on friday". The place is
    kept the way the night out is kept, so the next line about how it went is answered about the
    trip rather than read back to them.
    """
    if TRIP_NOT_YET.search(flat):
        return None
    for pattern, kind in ((BACK_FROM, "back_from"), (BEEN_TO, "been_to"),
                          (WENT_TO_ANY, "day_out")):
        match = pattern.search(flat)
        if not match:
            continue
        place = _trip_place(match.group(1), memory)
        if not place:
            continue
        # The same places the night-out answer refuses: a hospital, a court date and a shift at
        # work are lines about something that happened, not somewhere to ask "what was it like"
        # about. "i went to work in 2019" was answered "Work - what was it like?".
        if _not_a_night_out(place):
            continue
        bare = " ".join(w for w in place.lower().split() if w not in {"the", "a", "an"})
        if bare.split()[0] in NOT_A_PLACE_START:
            continue
        named = _tidy(place)
        if isinstance(memory, dict):
            memory["night_out"] = {"place": named, "turn": len(memory.get("turns") or [])}
        return _say(kind, memory, **_place_values(named))
    return None


def _night_out(flat, memory):
    """A warm, specific reply to somewhere they went and came back from, or None.

    The place is read out of their own words and put back in front of them, so the reply is
    about the pub they mentioned rather than a line that would fit any message.
    """
    detail = _the_detail_of_the_good_time(flat, flat, flat.split(), memory)
    if detail:
        return detail
    good_time = _a_good_time_they_had(flat, memory)
    if good_time:
        return good_time
    detail = _the_detail_of_the_good_time(flat, flat, flat.split(), memory)
    if detail:
        return detail
    good_time = _a_good_time_they_had(flat, memory)
    if good_time:
        return good_time
    seen = _saw_something(flat, memory)
    if seen:
        return seen
    match = WENT_TO.search(flat) or WENT_TO_COMPANY.search(flat)
    if not match:
        return None
    place = " ".join(match.group(1).split()).strip(" .,!;:")
    words = place.split()
    if not place or words[0] in {"my", "our", "his", "her", "their"}:
        return None
    if _not_a_night_out(place):
        return None
    bare = " ".join(w for w in words if w not in {"the", "a", "an"})
    if bare.split()[0] in NOT_A_PLACE_START:
        return None
    named = _tidy(place)
    values = {"X": named, "x": named[:1].lower() + named[1:]}
    poor_describer = _the_poor_describer(place)
    if poor_describer and not _poor_word(flat):
        # "we went to a terrible gig last night": the complaint is in front of the place, so the
        # place is named back without its word and the word is taken as said.
        bare_place = _tidy(" ".join(w for w in words if w not in SAID_POOR))
        if bare_place:
            if isinstance(memory, dict):
                memory["night_out"] = {"place": bare_place,
                                       "turn": len(memory.get("turns") or [])}
            return _say("day_out_poor", memory, p=poor_describer,
                        **_place_values(bare_place))
    poor = _poor_word(flat)
    if poor:
        # They already said how it went: "we went to the pub last night but it was dead" is not
        # a question for me, and it is not a line that would fit any message either. The word
        # they used comes back to them, as it does in the verdict after my question.
        return _say("night_out_poor_said", memory, p=poor, P=poor[:1].upper() + poor[1:],
                    **values)
    if WENT_WRONG.search(flat):
        # Somebody who was there was the trouble ("we went to the pub with my mum and she was
        # awful"), so the place is left alone.
        return None
    if isinstance(memory, dict):
        # Kept so the answer they give to my question has something to be about: "The pub —
        # what was it like?" / "it was lovely". Only this module's memory is kept when this
        # reply is the one chosen, so the note is only there if the question was really asked.
        memory["night_out"] = {"place": named, "turn": len(memory.get("turns") or [])}
    if WENT_WELL.search(flat):
        return _say("day_out_well", memory, **values)
    return _say("day_out", memory, **values)


# A filler hanging off the end of the thing is not part of it: "i fancy a cup of tea actually" is
# about a cup of tea, and "i want a dog too" is about a dog. Read as the thing's last word, the
# reply asked "What kind of actually do you usually go for?" and "What kind of too do you
# usually go for?" - a question nobody could answer.
FILLER_TAIL = frozenset("""
actually really honestly truly genuinely tbh though although anyway anyhow too also instead
already then please maybe probably perhaps possibly just now here there ok okay yeah right eh
""".split())


# Two-word fillers, the ones people hang on a thing as a phrase: "i want a garden as well", "a
# shed this year". Read as the thing, the last of the phrase is a question nobody can answer
# ("What kind of well do you usually go for?").
FILLER_TAIL_PHRASES = tuple(phrase.split() for phrase in """
as well|for now|this year|next year|right now|at the moment|i think|i guess|i suppose|of course
for sure|to be honest|if possible|at least|so far|in the end|as usual
""".replace("\n", "|").split("|") if phrase.strip())


# The tail of a correction: "im thinking of a kitchen, no, a bathroom". There the second half is
# the thing they are settling on and the first is the one they have just withdrawn, so the tail
# is kept and the head dropped - the opposite of the case above.
CORRECTION_TAIL = re.compile(
    r"^\s*(?:no|sorry|i mean|i meant|rather|make that|instead|actually)\b[\s,:-]*(?P<t>\S.*)$",
    re.I)


# A tail that rules something else out is not a correction: "i want a dog, not a cat" is about the
# dog, and reading "not a cat" as the thing they are settling on asks which kind of cat they want.
NEGATED_TAIL = re.compile(
    r"^\s*(?:and |but |honestly |definitely |really |just |probably )*"
    r"(?:not|rather than|instead of|anything but|other than)\b", re.I)


def _without_a_filler_tail(thing):
    """The thing with a filler, or anything after a comma, taken off the end of it.

    "a new kitchen, maybe in the spring" is about the kitchen and "a cup of tea actually" about
    the cup of tea. Only a filler is dropped from the end, so a thing said with its purpose
    ("a tent for two") is left alone, and a single word is never dropped: "i want more" is not
    a thing with "more" bolted on. A tail that opens with a correction is the other way round:
    "a kitchen, no, a bathroom" is about the bathroom.
    """
    said = " ".join(str(thing or "").split())
    head, _, tail = said.partition(",")
    head = head.strip(" ,;:")
    if tail:
        fixed = CORRECTION_TAIL.match(tail)
        if NEGATED_TAIL.match(tail):
            # The tail is the one they do not want, so the head is still the thing.
            said = head or (fixed.group("t") if fixed else said)
        elif fixed:
            said = fixed.group("t")
        elif head:
            said = head
    words = said.split()
    changed = True
    while changed and len(words) > 1:
        changed = False
        for phrase in FILLER_TAIL_PHRASES:
            if len(words) > len(phrase) and all(
                    word.lower().strip(".!?") == want
                    for word, want in zip(words[-len(phrase):], phrase)):
                words = words[:-len(phrase)]
                changed = True
                break
    while len(words) > 1 and words[-1].lower().strip(".!?") in FILLER_TAIL:
        words.pop()
    return " ".join(words)


INDEFINITE = frozenset("something anything stuff things some".split())


# A body part with something wrong with it is a symptom even when the word for the feeling is
# not there: "i need something for a stomach ache" and "something for my back" name the place
# and want help, and the ask-which-kind reply is a suggestion frame, not help.
PAIN_PART = re.compile(
    r"\b(?:stomach|tummy|belly|back|neck|shoulder|knee|elbow|wrist|ankle|foot|feet|toe|hand|"
    r"thumb|finger|hip|leg|arm|mouth|tooth|teeth|gum|gums|ear|ears|eye|eyes|throat|chest|nose|"
    r"skin|head|hip|shin|calf|heel|skin|burn|blister|bite|sting|rash|itch|cramp)\b")


INDEFINITE_SKIP = frozenset("to for that which like of".split())


ASK_KIND = (
    "What sort of {adj} are you after? Name one you liked and I'll go from there.",
    "{x}? Tell me what you've enjoyed before and I'll suggest something.",
)


# The "smallest version of it" advice only fits starting an activity ("start running"), never a
# decision or a job that carries a date of its own ("move in together", "sort out the pickup").
DOING = frozenset("""
start starting begin beginbegin learn learning try trying eat eating get getting go going do doing
take taking up cut cutting quit quitting stop stopping save saving write writing sort sorting
clear clearing tidy tidying build building train training practise practice run running walk
walking swim swimming cook cooking read reading study studying""".split())


ALWAYS = re.compile(r"\b(?:i'm|im|i am|we're|we are)\s+always\s+(.+)$")


# A thing you pursue over time ("learn to swim", "get fit", "cook more") is worth a plan. A
# one-off action is done, not built up ("cancel my gym membership", "book a table", "quit"), and
# a state is not a thing to start work on at all ("i want to be left alone" is a request for
# space). Both are handed back to the ordinary reply rather than offered a smallest version.
ONE_OFF = frozenset("""
cancel quit resign book rebook order buy pay sell file send phone call ring unsubscribe
subscribe delete close return renew sign switch claim report transfer drop
""".split())


# A change of situation is neither pursued over time nor done once: "move in together", "get
# married", "retire at 55". "Doable. Tell me the bit that feels hardest" presumes a task, so
# these go back to the neutral reply.
DECISION = re.compile(
    r"\b(?:move|moving|moved)\s+(?:in|out|abroad|away|back)\b"
    r"|\bget(?:ting)?\s+(?:married|divorced|engaged)\b"
    r"|\b(?:buy|buying|sell|selling)\s+(?:a|the|our|my)\s+(?:house|flat|home|car)\b"
    r"|\bretir(?:e|ing|ement)\b|\bemigrat\w*\b|\bhave a baby\b|\bstart a family\b"
    r"|\bgo(?:ing)?\s+back\s+to\s+(?:college|university|school|work)\b", re.I)


TASK_ONLY = ("smallest version", "hardest")


STATE = re.compile(
    r"\b(?:be|being|stay|feel)\s+(?:left alone|alone|left|out of it|free|done|rid of \w+|there)\b"
    r"|\bleft alone\b", re.I)


# "i want to keep going though" answers the question the bot just asked; it is not a new thing
# to plan. A bare continuation has nothing in it to take a first step on.
CONTINUING = frozenset(("keep going", "carry on", "keep at it", "keep it up", "keep trying"))


# A want with nothing after it but the feeling itself is a disclosure, not a thing to plan:
# "i want to disappear" and "i want to give up" get the line for a person running on empty.
# "give up smoking" names something and is not here.
BARE_FEELING = frozenset(("disappear", "vanish", "give up", "give in", "hurt", "cry", "sob",
                          "die"))


# "a sofa that fits in a small room" describes a task; the last word before the purpose is not
# the thing at all ("what kind of fits do you usually go for?").
RELATIVE = re.compile(r"\b(?:that|which|who|whose|where)\b", re.I)


# Time away from work or school ("i need time off work", "can i have the day off tomorrow") is a
# question the answers module already answers: it is not a thing to plan or pick a kind of.
LEAVE = re.compile(r"\b(?:time|day|days|week|weeks|evening|afternoon|morning|night|weekend"
                   r"|fortnight|month)\s+off\b"
                   r"|\b(?:annual leave|sick leave|sick day|parental leave|compassionate leave"
                   r"|unpaid leave|holiday entitlement|leave of absence|paid leave)\b", re.I)


# "Do i need the police" asks whether a thing is needed at all, not which sort of it they
# pick: a burgled line with that on the end read the want branch and was asked "What kind of
# police do you usually go for?". The answer to a need is the answer to the need - the 101
# card, the insurer, the GP - so the kind question stands down for it.
_A_NEED_ASK = re.compile(
    r"\bdo\s+(?:i|we|you)\s+(?:really\s+|even\s+|still\s+)?need\b", re.I)


# A person who does a job is called, not chosen between by kind: "what kind of plumber do you
# usually go for?" is not a sentence anyone says.
PERSON_WORK = re.compile(
    r"(?:er|or|ian|ist|man|woman|guy|person|smith)$", re.I)


# Not everything comes in kinds to pick between. A shop sells kinds of kettle, sofa, bike and
# holiday; it does not sell kinds of baby, divorce or mortgage. "What kind of divorce do you
# usually go for?" is not a sentence anyone says, and "i want a baby" / "i need a divorce" are
# ordinary lines, so these heads go on to the ordinary reply that names the thing instead.
NOT_A_GOOD = frozenset("""
baby child kid toddler son daughter boy girl partner husband wife fiance fiancee boyfriend
girlfriend friend mate person people family mum dad mother father brother sister gran nan
grandma grandad grandmother grandfather aunt uncle cousin relative neighbour colleague boss
nanny babysitter carer plumber doctor dentist nurse midwife
break rest sleep time chance money advice help support idea hug kiss cry favour favor lift ride
hand hands
pay rise rise promotion job refund rebate visa passport mortgage loan debt lawsuit claim
night evening morning afternoon weekend day out
complaint apology resignation divorce wedding funeral party appointment ceremony christening
interview operation surgery birthday anniversary degree exam test
tattoo house flat home cottage dog cat puppy kitten pet""".split())


# Some last words are not the thing at all: "i want my money back" ends on "back", "i want a
# small one" ends on "one", and "what kind of back do you usually go for?" is not a sentence
# anyone says. A tail like this leaves the thing to be picked between unnamed.
NOT_THE_THING = frozenset("""
back too again instead please now then anyway though later one ones it them those these
something anything nothing sort kind bit
him her me us you they he she we them mine yours ours theirs
up down off out away along around round through over apart forward forwards backwards
in on at by""".split())


_A_PERSON_ALREADY_IN_THE_LINE = frozenset(
    "him her them me us you they he she we mine yours ours".split())


# A day or a date is a deadline, never a thing that comes in kinds. "i need my dress taken up
# before saturday" read the day as the thing and asked "What kind of saturday do you usually go
# for?", which is not a sentence anyone says: the job is the thing and the day only says when.
# Asked for a kind of any of these the question is unanswerable, so the thing is named back
# instead, which is a sentence a person can answer.
NOT_A_THING_WITH_KINDS = frozenset("""
monday tuesday wednesday thursday friday saturday sunday weekday weekend week month year day
today tonight tomorrow yesterday morning afternoon evening night noon midnight
january february march april may june july august september october november december
spring summer autumn winter christmas easter birthday anniversary date
""".split())


def _kindless(word):
    """True when this word is not a thing that comes in kinds somebody picks between."""
    w = word.lower().strip(" .,!?;:'\u2019\"()")
    if w in NOT_A_THING_WITH_KINDS:
        return True
    if w in NOT_A_GOOD or w in NOT_THE_THING:
        return True
    # The verb and the particle of "my dress taken up" are the job, not a thing with kinds:
    # asked for the kind of "washed" a person has nothing to answer (`particles`).
    from ..modules.particles import a_job_word
    if a_job_word(w):
        return True
    if w.endswith("ies") and w[:-3] + "y" in NOT_A_GOOD:
        return True
    for tail in ("es", "s"):
        if w.endswith(tail) and w[:-len(tail)] in NOT_A_GOOD:
            return True
    # A breed is the animal it is, and the animal's own word is already in the list: "i want a
    # labrador" got the echo ("Got it. Is there anything you'd like a hand with?") while "i want
    # a dog" was named back ("A dog? Where are you up to with it?"), and "i want a spaniel" fell
    # into the pool that asks which sort. Nobody picks a kind of dog, so the breed is kindless.
    return bool(breeds.the_kind_of(w))


# A thing that comes in no kinds to pick between takes a reply that names it and asks for the
# situation, never a question about which sort: "what kind of divorce do you usually go for?"
# is not a sentence anyone says, and "i want a baby" is an ordinary line.
KINDLESS = (
    "{X} — tell me a bit more and I'll help you think it through.",
    "{X}? Where are you up to with it?",
    "Say more about {x} and I'll help you work out the next step.",
)


# A thing wanted *from* somebody is not a thing to pick a kind of either: "what kind of him",
# "what kind of space do you usually go for?" for "i want my own space from them". A pronoun after
# one of these prepositions is a person the line is about, so the reply is about them.
_PERSON_IN_THE_TAIL = re.compile(
    r"\b(?:from|about|with|around)\s+(?P<who>him|her|them|me|us|you)\b")


A_BREAK_FROM_SOMEONE = (
    "{X}? Tell me what's going on with {them} — that's usually where the answer is.",
    "{X} — fair enough. What is it about {them} that's wearing you down?",
    "{X} is a fair thing to want. What would time away from {them} give you that you are "
    "not getting now?",
)


CHOOSING = (
    "{X} — what kind are you after?",
    "What kind of {head} do you usually go for?",
    "{X}: tell me what you want from it and I'll help you narrow it down.",
)


THING_REPLIES = {
    # The thing is dropped into these as a label ("Learm the guitar \u2014 fair enough"), never
    # into a verb slot, because a captured phrase can be a gerund or a bare verb.
    "intention": (
        "{X}? Good thing to want. What's the bit you're least sure about?",
        "Worth planning rather than rushing into: what would have to go right for you?",
        "I'd say do it if the practical side works out. Want to work through what it would take?",
    ),
    "want": (
        "{X} \u2014 fair enough. What's stopped it happening so far?",
        "Then start with the smallest version of it, not the whole thing. What would the first "
        "step be?",
        "Doable. Tell me the bit that feels hardest and we'll start there.",
    ),
    "keeps": (
        "{X} keeps happening \u2014 that's usually the routine rather than you. "
        "What have you tried?",
        "Annoying. Is it the same every time, or does it vary?",
        "Worth fixing once rather than every week. What's the moment it goes wrong?",
    ),
    # The same thing done to somebody: "i keep saying sorry to my wife", "i keep letting people
    # down". Nothing about that annoys them - they are minding it themselves - so the reply talks
    # about the pattern instead of calling it annoying.
    "keeps_someone": (
        "{X} keeps happening \u2014 that's usually the routine rather than you. "
        "What have you tried?",
        "That would wear anyone down. How long has it been like that?",
        "Worth fixing once rather than every week. What's the moment it goes wrong?",
    ),
    "always": (
        "Always {x}? That's a routine thing more than a character thing.",
        "{X} every time \u2014 what's the usual trigger?",
        "Always {x}? Then there's a pattern in it somewhere. When did it start?",
    ),
}


def _a_death_just_said(memory):
    """True when one of the last two turns said that a person or a pet died, and it is news.

    A cheer is out of place in the turn or two after a death, and nowhere else. The wider read
    (`_in_loss`, six turns) is right for the pools that answer a bereavement; for a celebration it
    went on muting a chat long after the room had moved on: "my dad died in march / thanks im ok /
    work has been busy honestly / i got the job" is a new job and good news.

    A death dated as a story is not news either, and the dating is read where it is already read -
    "my dad died when i was 12" is a fact about a childhood, so a job after it is still good news.
    """
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    for turn in turns[-2:]:
        said = turn.get("user") if isinstance(turn, dict) else None
        if not isinstance(said, str) or not said.strip():
            continue
        if not loss_reading.reads_as_loss(said):
            continue
        if urgent_reading.reads_as_a_story(loss_reading._spoken(said)):
            continue
        return True
    return False


def _in_loss(memory):
    """True when someone in this conversation has said that a person or a pet died."""
    turns = memory.get("turns") if isinstance(memory, dict) else None
    if not isinstance(turns, list):
        return False
    return any(isinstance(turn, dict) and loss_reading.reads_as_loss(turn.get("user") or "")
               for turn in turns[-6:])


def _answers_knows(text, memory):
    """True when the knowledge base has a real answer for this line.

    "i need a side for the barbecue" and "i need a copy of my birth certificate" are not
    shopping choices: something knows what they are, and this module must not take the turn
    from it with a question about which kind they want.
    """
    from ..modules import answers
    try:
        return bool((answers.respond(text, memory) or "").strip())
    except Exception:  # noqa: BLE001 - a knowledge miss must not stop the chat module
        return False
