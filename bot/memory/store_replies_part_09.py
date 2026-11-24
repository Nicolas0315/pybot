"""Part 9 of 13 of the module, split out of `store_replies`.

Everything here is re-exported from `store_replies`, so callers import it from there as before.
"""
import re
from ..compose import pick
from ..memory import (
    content, current, last_user, others, plan_line, plan_sentence, stem, thread, user,
)
from ..memory import ack
from ..memory.filler import without_filler
from ..memory import plans
from ..memory.taste import ASKS_ABOUT_A_TASTE, TASTE_ASKED_ABOUT
from ..memory import facts as extract
from ..memory import history
from ..memory import recall
from ..memory.topics import STOPWORDS
from ..memory import topics as _topics
from ..memory.topics import subject as topic_subject
from ..memory.thread import about as _about_the_chat
from ..understanding import understand
from ..memory.store_lines import CHILD, NOTHING_STARTED, LENGTH
from ..memory.relations import _called
from bot.memory.corrected import ANY_NUMBER, _asks
from .store_replies_part_01 import (
    STOPWORDS,
)
from .store_replies_part_03 import (
    _is_are, _place_phrase,
)
from .store_replies_part_04 import (
    ASK_FILLER, NO_THING, OWN_ASK, A_CLAIM_OF_TELLING, SUMMARY_FILLER, SMALL_TALK_ONLY,
)
from .store_replies_part_05 import (
    _a_diet_predicate, _diet_how, _job_phrase,
)
from .store_replies_part_07 import (
    _vary, _a_pet,
)
from .store_replies_part_08 import (
    AN_ATTITUDE, CHANGE_WORD, NEGATIVE_LINE, _shape, SAY_BACK_CORRECTION, SAY_BACK_VAGUE,
    SAY_BACK_VAGUE_TAIL, _lines_that_moved, _reads_as_a_correction, _safety_lines,
    _the_summary_already_says, _with_the_name,
)


def _about_what_they_said(text, memory):
    """A yes-or-no ask the store has no fact for, answered from their own earlier line.

    "do i drive" after "i dont drive" used to answer "I don't know enough to answer that
    honestly", which is not true: they said it one line ago. The words the question names have
    to be in a line they said, all of them, so a question about something they never mentioned
    is left to the ordinary reply rather than answered with a guess.

    Every line they said is read, not the last few. A fact about them does not expire because
    the chat moved on: "i dont drive" ... four turns about a boiler ... "do i drive" answered
    "I'd rather not guess" about something they had told the bot, and a chat that long is an
    ordinary chat. The containment is what keeps it honest, so the newest line that names the
    thing wins: "i passed my driving test" is read after "i dont drive" rather than instead.
    """
    low = " ".join(str(text or "").lower().split()).strip(" ?!.,")
    if not OWN_ASK.match(low) or len(low.split()) > 9:
        return None
    words = {stem(word) for word in re.findall(r"[a-z']+", low)}
    words = {word for word in words
             if len(word) > 3 and word not in ASK_FILLER and word not in NO_THING}
    # A thing named in three letters is still the thing: "car", "job", "dog", "gas".
    words |= {word for word in re.findall(r"\b[a-z]{3}\b", low) if word not in NO_THING
              and word not in ASK_FILLER}
    if not words:
        return None
    said_before = [str(turn.get("user") or "") for turn in (memory.get("turns") or [])
                   if isinstance(turn, dict)]
    newest = " ".join((said_before[-1] if said_before else "").lower().split()).strip(" ?!.,")
    for line in reversed(said_before):
        said = {stem(word) for word in re.findall(r"[a-z']+", str(line or "").lower())}
        if not words <= said:
            continue
        # The newest line about the thing is the one read, and going back past a line that names
        # the thing is still not done ("what can i cook" is not about the thing, so the line about
        # it stands). When the line read is not the last thing they said, something may have
        # changed since: "i dont drive" then "i passed my driving test last week" - the test is
        # one word away from "drive" but "driving" is not "drive", so the older line is the one
        # that matches. It goes back to them as what they said earlier, with the door open, rather
        # than being asserted as true now.
        phrase = _told_phrase(line)
        if phrase:
            # The restater writes contractions out, which leaves "you can not swim": the one place
            # that reads badly is put back the way people say it.
            phrase = phrase.replace("can not", "cannot")
            flat = " ".join(str(line or "").lower().split()).strip(" ?!.,")
            if flat != newest:
                return pick(["Earlier you said " + phrase + " - still the case?",
                             "You said " + phrase + ", earlier in this chat - still the case?"],
                            memory)
            return pick(["You told me " + phrase + ".", "You said " + phrase + "."], memory)
        return None
    return None


def _first_bot_reply(memory):
    """The first thing the bot said, for "what was the first thing you said?"."""
    first = _first_sentence(history.first_bot_line(memory))
    if not first:
        return "I haven't said anything yet — you go first."
    return _vary(["I opened with: \"" + first + "\"",
                  "My first line was: \"" + first + "\"",
                  "I started with: \"" + first + "\""], memory)


def _last_told(memory):
    """What they last told you, in their own words, or "" when the line was a question or small talk.

    A line that leaves no fact behind is still something they told you: "my parents evening went
    well" keeps nothing to recall, and a summary that skips it answers "you haven't told me about
    yourself" to someone who just did.
    """
    record = current(memory)
    # The topic is often the question itself ("what do you know about me"), so the lines before it
    # are tried in turn and the first one that said something is the one said back.
    candidates = [str((record or {}).get("text") or "")]
    candidates += [str(line or "") for line in reversed(last_user(memory, 3))]
    for text in candidates:
        if recall.ask(text) == "me":
            # A question about what the bot holds is not something they told it: "anything
            # you've learned about me" was said back as "you said anything you have learned
            # about you" in the summary of a chat that had three real facts in it.
            continue
        phrase = _told_phrase(text)
        if phrase:
            return phrase
    return ""


def _out_of_date_lines(memory):
    """The lines a later line changed, without the store having a key to record it under.

    "im single" / "im married now" leaves no fact behind - there is no key for it - so the log
    says nothing and both lines would be walked back, the old state beside the new one. A line
    that left a fact behind is left to the store's own value, so "im allergic to nuts" keeps its
    line even after "im vegetarian now".
    """
    lines = [" ".join(str(line or "").lower().split()) for line in last_user(memory, 8)]
    logged = {" ".join(str(entry.get("text") or "").lower().split())
              for entry in (memory.get("facts_log") or []) if isinstance(entry, dict)}
    out = set()
    for index, line in enumerate(lines):
        if not CHANGE_WORD.search(line):
            continue
        changed = {word for word in re.findall(r"[a-z0-9']+", line)
                   if len(word) > 2 and word not in STOPWORDS
                   and not CHANGE_WORD.fullmatch(word)}
        for older in lines[:index]:
            if older in logged:
                continue
            knew = {word for word in re.findall(r"[a-z0-9']+", older)
                    if len(word) > 2 and word not in STOPWORDS}
            if changed & knew or _shape(older) == _shape(line):
                out.add(older)
    # A negative line and a later line where they do the thing: the same thing compared on its
    # stem, so "drive" and "driving" are one word. Only a statement of theirs counts - a question
    # ("do you like fish?") takes nothing back - and an attitude is not a thing they can undo.
    for index, older in enumerate(lines):
        if not NEGATIVE_LINE.search(older) or AN_ATTITUDE.search(older):
            continue
        knew = [_root(word) for word in re.findall(r"[a-z']+", older)
                if len(word) > 2 and word not in STOPWORDS]
        for later in lines[index + 1:]:
            if (not re.match(r"^(?:i|ive|i've|im|i'm|we|weve) ", later)
                    or NEGATIVE_LINE.search(later) or later.endswith("?")):
                continue
            there = [_root(word) for word in re.findall(r"[a-z']+", later)
                     if len(word) > 2 and word not in STOPWORDS]
            if any(_one_word(a, b) for a in knew for b in there):
                out.add(older)
                break
    return out


def _root(word):
    """The same word with its ending taken off: drive and driving are one thing."""
    word = str(word or "").lower().strip("'")
    for suffix in ("ing", "ers", "er", "ed", "es", "s", "ly"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[:-len(suffix)]
            break
    if len(word) > 3 and word[-1] == word[-2] and word[-1] not in "aeiou":
        word = word[:-1]  # swimming, stopped: the doubling is the ending, not the word
    if len(word) > 3 and word.endswith("e"):
        word = word[:-1]
    return word


def _one_word(first, second):
    """Whether two words are the same thing said with a different ending: drive, driving."""
    return first == second or (_root(first) == _root(second) and len(_root(first)) >= 3)


SELF_JUDGEMENT = re.compile(
    r"^\W*(?:(?:and|but|so|oh|also|well|yeah|yep|ok|okay|right|honestly|tbh)\W+)*"
    r"(?:i'?m|i\s+am|im|i\s+feel(?:\s+like)?|i\s+was(?:\s+being)?)\b"
    # "im such an idiot", "i am a complete muppet", "i feel like a rubbish mum"
    r"(?:\s+(?:being|such|a|an|the|complete|total|absolute|right|proper|bit\s+of\s+a))*\s+"
    r"(?:idiot|muppet|moron|fool|clown|disaster|loser|failure|letdown|let\s?down|"
    r"embarrassment|disappointment|waste\s+of\s+space|useless|worthless|hopeless|"
    r"no\s+good|not\s+good\s+enough|"
    r"(?:rubbish|bad|terrible|awful|useless|hopeless)\s+(?:mum|mom|mother|dad|father|parent|"
    r"husband|wife|partner|friend|person|son|daughter))"
    # "useless at everything i try" judges the whole person; "useless at maths" rates a skill
    r"(?:\s+(?:at|with|in)\s+(?:everything|anything|life|myself|all\s+of\s+it|this|that)\b"
    r"(?:\s+\w+){0,4})?"
    r"\s*[.!]*$"
    # "what an idiot i am": the same judgement said the other way round
    r"|^\W*what\s+an?\s+(?:idiot|muppet|moron|fool|disaster)\s+i\s+(?:am|was|have\s+been)\b"
    # "i hate myself" is the same judgement, and only the whole line is it
    r"|^\W*i\s+hate\s+myself\b"
    # what they say they always do: "i always mess things up", "i keep ruining everything". An
    # object of their own ("i keep messing up the recipe") is a thing that happened, not a
    # verdict on the person, so only the whole of it with no thing named is caught here.
    r"|^\W*i\s+(?:always|constantly|just|keep|keeps)\s+"
    r"(?:mess(?:es|ing)?\s+(?:things|it|everything)?\s*up"
    r"|ruin(?:s|ing)?\s+(?:things|it|everything)"
    r"|screw(?:s|ing)?\s+(?:things|it|everything)\s+up)\s*[.!]*$", re.I)


SELF_WORST = re.compile(
    r"^\W*(?:(?:and|but|so|oh|also|well|yeah|yep|ok|okay|right|honestly)\W+)*"
    r"(?:i'?m|i\s+am|im)\s+(?:the\s+|literally\s+|such\s+|an?\s+)*(?:worst|worse)\s*"
    r"[.!]*$", re.I)


def _judging_themselves(line):
    """Whether the line is the person rating themselves rather than telling the bot a fact."""
    said = " ".join(str(line or "").lower().split())
    return bool(said) and bool(SELF_JUDGEMENT.match(said) or SELF_WORST.match(said))


def _recent_told(memory, limit=3):
    """The last few things they told you, newest first, in their own words.

    The store keeps the facts it has a key for, and the rest is only what they said: "i dont
    drive" leaves no fact behind, so the line is the whole of it. Walking back over the lines
    they typed keeps those for more than one turn.
    """
    out, seen = [], set()
    newest = ""
    # A chat the bot has answered with care gets no inventory: the summary of a crisis is not a
    # list of what the bot has on file.
    if _topics.in_a_safety_thread(memory):
        return out
    moved = _lines_that_moved(memory)
    care = _safety_lines(memory)
    record = current(memory)
    # The lines they typed, newest first. The record the chat is on is the line it opened with, so
    # it is only the whole history when nothing else is kept.
    lines = [str(line or "") for line in reversed(last_user(memory, 8))]
    if not lines:
        lines = [str((record or {}).get("text") or "")]
    newest = " ".join(lines[0].lower().split())
    for index, line in enumerate(lines):
        flat = " ".join(str(line or "").lower().split())
        # A line whose fact the store now holds a different value for is not said: after
        # "im 34" / "no i mean 43" the summary has the 43, and saying the 34 beside it is the
        # bot repeating a mistake the person already put right.
        if flat in moved or flat in _out_of_date_lines(memory):
            continue
        # A line the bot answered with care is not a fact about the person: "you said you keep
        # thinking about ending it" is the worst thing they said, quoted back in a list. A line
        # where they are hard on themselves is the same: the recap is no place to hand back "you
        # are such an idiot" in the bot's own voice.
        if flat in care or _judging_themselves(flat):
            continue
        # A correction takes back what came before it, so the walk stops there: everything older
        # is what they put right, and the store holds whatever the correction left. A figure put
        # up for something the store has no fact for puts nothing right - "the table is booked for
        # 10" then "actually just 8" left the store empty - so that line takes nothing back, and
        # stopping on it made the recap deny the whole chat ("Not much yet - you haven't told me
        # about yourself") one turn after they had told the bot about the table.
        if _reads_as_a_correction(line):
            if not _a_figure_the_store_could_not_keep(line, memory):
                break
            continue
        # Half of the question they just asked is not something they told us: "whats the capital
        # of australia" then "and the weather there in june" has no verb and nobody in it, and
        # the summary that listed it reported a fact they never gave.
        if ack.the_rest_of_a_question(
                line, lines[index + 1] if index + 1 < len(lines) else ""):
            continue
        if A_CLAIM_OF_TELLING.match(flat) and not extract.extract(line):
            # "i told you already" is about the telling, not a fact about the person: said back in
            # a summary it reported "you said you told you already" as something they had told.
            continue
        if recall.ask(flat) == "me":
            # A question about what the bot holds is not something they told it: "anything
            # you've learned about me" came back as "you said anything you have learned about
            # you" in the summary of a chat whose facts were all asked back.
            continue
        if _the_summary_already_says(memory, flat):
            continue
        phrase = " ".join(_told_phrase(extract.no_tone(line)).split())
        while phrase and phrase.split()[-1].lower() in SAY_BACK_VAGUE_TAIL:
            phrase = " ".join(phrase.split()[:-1])
        # "can not swim" reads like a translation; the contraction is how a person writes it.
        phrase = phrase.replace("can not", "cannot")
        words = {w for w in _summary_words(phrase)}
        if not words or words <= SAY_BACK_VAGUE or SAY_BACK_CORRECTION.search(phrase):
            continue
        key = phrase.lower()
        if key in seen:
            continue
        seen.add(key)
        # The line the chat is on is said only if it is what the facts above are about; an older
        # line is a different thing they told the bot, and the topic guard does not apply to it.
        out.append((phrase, flat == newest))
        if len(out) >= limit:
            break
    return out


AGREEMENT_ONLY = frozenset("""
know knew knows knowing agree agreed guess suppose supposed admit honestly seriously swear trust
believe promise really truly sure right true yes yeah no nah mean means meant said say saying
tell told think thought feel felt do did does done that this it everything anything much
""".split())


def _all_about_the_bot(memory):
    """Whether every line they typed was a question about the bot itself.

    "so youre claude" / "what do you know about me" has no subject of its own to name, and the
    reading that names one said "so far it's been the claude" - the bot's own name offered as
    the thing the person is into. The composer already has one reading of "this is about you",
    so it is asked rather than a second list of words kept here.
    """
    from ..compose.fallback import about_the_bot
    lines = [str(line or "").strip() for line in last_user(memory, 8)]
    lines = [line for line in lines if line]
    if not lines:
        return False
    return all(about_the_bot(" ".join(line.lower().split())) for line in lines)


def _a_figure_the_store_could_not_keep(line, memory):
    """True when the line is only a new figure for something, and no fact moved for it.

    The store records what a correction moved under `memory["correction"]`, so no key there means
    nothing was put right: "the table is booked for 10" then "actually just 8" named a thing the
    store keeps no fact for, and the line before it is still true. Only a figure counts, and only
    when the line is nothing but one with a correction word in front, so a denial ("i dont
    drive") is still the take-back it was.
    """
    if (memory.get("correction") or {}).get("key"):
        return False
    found = extract.extract(line).get("correction") or {}
    value = " ".join(str(found.get("to") or "").split())
    return bool(value) and bool(ANY_NUMBER.fullmatch(value))


def _the_thing_the_chat_is_on(memory):
    """The phrase to name in place of facts, or "" when the chat holds nothing of the person's.

    Only when the line it comes from is a question or something about them ("how do i clean the
    oven", "whats the capital of australia"): a chat whose only line is about the bot itself has
    no subject of theirs to name, and naming one said "so far it's been the claude".
    """
    if _all_about_the_bot(memory):
        return ""
    record = current(memory) or {}
    text = " ".join(str(record.get("text") or "").split()).lower()
    if not text:
        return ""
    theirs = re.search(r"\b(?:i|im|i'm|my|we|our|me|us|mine)\b", text)
    # A question put to the bot is not a subject of theirs either: "are you a real person" is
    # about the bot, and naming it said "so far it's been the real person".
    to_the_bot = re.search(r"\b(?:you|your|youre|you're|u)\b", text)
    if not (theirs or (_asks(text) and not to_the_bot)):
        return ""
    return " ".join(str(_about_the_chat(memory) or "").split())


def _a_fact_of_its_own(clause):
    """Whether a clause beside a judgement says something, rather than agreeing with the verdict."""
    words = {word.strip(".,!?;:'\"") for word in str(clause).lower().split()} - SUMMARY_FILLER
    return bool(words) and not words <= AGREEMENT_ONLY


def _told_phrase(text):
    """One line said back inside a sentence, or "" when it is not something they told you."""
    if not text:
        return ""
    reading = understand(text, {})
    # A question or an ask is not something they told you: "any tips for my parents evening" is
    # a request, and "you said any tips for your parents evening" is not a sentence.
    if (reading.get("kind") in ("question", "greeting", "thanks")
            or reading.get("intent") in ("question", "request", "greeting", "thanks")
            # A feeling is how they are, not a fact they told us. It slipped through on the
            # lines whose feeling is carried by a thing acting on the speaker - "work is
            # stressing me out" has no "i" in it, so the whole line was read back as news:
            # "Got it - your job is stressing you out." The engine now reads those as feelings
            # (kinds.py, ACTS_ON_THE_SPEAKER), and this is the store honouring the reading.
            or reading.get("intent") == "feeling"
            or reading.get("asks")):
        return ""

    if reading.get("about_bot"):
        return ""
    if extract.is_a_judgement(text):
        # A judgement about themselves is how they feel, not something they told us: "you said
        # you are a bad mum" is the store agreeing with them. A line can carry a fact beside the
        # judgement though - "im a terrible cook, i burned the roast again" - so the clause that
        # is not a judgement is the one said back, and a line that is all judgement keeps nothing.
        rest = [part.strip() for part in re.split(r"\s*(?:[,;.]|\bbut\b|\band\b)\s*", text)
                if part and part.strip()]
        text = next((part for part in rest
                     if not extract.is_a_judgement(part) and _a_fact_of_its_own(part)), "")
        if not text:
            return ""
    said = _with_the_name(thread.restate(without_filler(text)) or "", text)
    words = [word for word in said.split() if word.strip(".,!?;:")]
    body = {word.strip(".,!?;:").lower() for word in words} - SUMMARY_FILLER
    if not body or body <= SMALL_TALK_ONLY or len(words) > 14:
        return ""
    return " ".join(words)


def _expanded(text):
    """A line with its contractions written out: "you're veg" and "you are veg" are the same line."""
    text = str(text).lower().replace("\u2019", "'")
    for pattern, word in ((r"n't\b", " not"), (r"'re\b", " are"), (r"'ve\b", " have"),
                          (r"'ll\b", " will"), (r"'d\b", " would"),
                          (r"\bi'm\b", "i am"), (r"\bim\b", "i am"),
                          (r"\bive\b", "i have"), (r"\byoure\b", "you are"),
                          (r"\bdont\b", "do not"), (r"\bdoesnt\b", "does not"),
                          (r"\bim\b", "i am")):
        text = re.sub(pattern, word, text)
    return text


NUMBER_AS_A_WORD = dict(zip(
    "1 2 3 4 5 6 7 8 9 10 11 12 20 30 40 50 100".split(),
    "one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty "
    "hundred".split()))


def _a_judgement_was_said(memory):
    """Whether a line they said in this chat judged themselves rather than stating a fact.

    It is read from the history the runtime keeps (memory["turns"]) rather than from a flag of
    its own, so there is no second copy of the fact to keep in step with the store: a judgement
    is never filed, and the line they typed is still there.
    """
    for turn in (memory.get("turns") or []):
        if not isinstance(turn, dict):
            continue
        line = turn.get("user")
        if isinstance(line, str) and extract.is_a_judgement(line):
            return True
    return False


FACT_FRAME_WORDS = frozenset("""i im ive the a an my our at with for to of in on and
got get gotten job jobs start started starting new began""".split())


def _plain_words(text):
    """The words of a line as they are, without the length rule the summary meaning applies."""
    return set(re.findall(r"[a-z0-9']+", str(text or "").lower().replace("-", " ")))


def _says_nothing_new(phrase, told_words, body_words):
    """Whether the line is the fact above, in the person's own words, and nothing more."""
    body = _summary_words(body_words)
    if told_words <= body:
        return True
    # The short words a summary drops are sometimes the whole of the thing shared: "co-op" in the
    # fact and "co op" in the line are the same place, and both halves are two letters long, so the
    # place is compared on the words as they are.
    rest = _plain_words(phrase) - FACT_FRAME_WORDS
    if not rest:
        return False
    return rest <= _plain_words(body_words)


def _summary_words(text):
    """The words that carry the meaning of a line, for telling a repeat from a new thing."""
    words = set()
    for word in _expanded(text).replace(";", " ").replace(",", " ").split():
        word = stem(word.strip(".,!?;:'"))
        word = NUMBER_AS_A_WORD.get(word, word)
        # A figure is a fact in its own right ("im 41", "my son is 8"), so it is kept whatever
        # its length: the words around it are what the length rule is for.
        if not word.isdigit():
            # The store keeps the plain word, so the slang has to fold the same way here: "veggie"
            # in the line and "vegetarian" in the fact above are the same fact, said twice.
            word = stem(extract.DIET_NAMES.get(word, word))
        if word and (word.isdigit() or len(word) > 2) and word not in SUMMARY_FILLER \
                and word not in SMALL_TALK_ONLY:
            words.add(word)
    return words


def _already_said(words, said):
    """Whether the facts above already say this: "allergy" and "allergic" are the same word here."""
    said = _summary_words(said)
    if not said:
        return False  # nothing above says anything, so this is new
    if not words:
        return True
    for word in words:
        same = [other for other in said
                if other == word or (len(word) >= 4 and len(other) >= 4
                                     and other[:4] == word[:4])]
        said.difference_update(same)
    return len(said) < max(1, len(words) // 2)


TASTE_ASK = ASKS_ABOUT_A_TASTE


_TASTE_LEFT = TASTE_ASKED_ABOUT


def _taste_reply(memory, low):
    """The taste they have already said, said back as the answer to "do i like fish?".

    Returns None when the store has no taste about that thing, so a question about something
    they have never mentioned is left to whoever can answer it.
    """
    left = _TASTE_LEFT.split(str(low or ""), maxsplit=1)
    asked = left[-1] if len(left) > 1 else ""
    asked = re.sub(r"\b(?:again|still|actually|really|now|any ?more)\b", "", asked).strip(" ?!.,")
    if not asked:
        return None
    wanted = [stem(word) for word in content(asked)]
    if not wanted:
        return None
    for taste in reversed(user(memory).get("tastes") or []):
        thing = str(taste.get("thing") or "").lower()
        bare = thing[5:] if thing.startswith("your ") else thing
        said = [stem(word) for word in content(bare)]
        if not said:
            continue
        if sum(1 for word in wanted if word in said) < max(1, len(wanted) - 1):
            continue
        how = str(taste.get("how") or "yes")
        # Said back with the possessive it was kept in: "do i like my job?" is "you like your
        # job", not "you like job".
        named = bare if not thing[5:].strip() or not thing.lower().startswith("your ") else thing
        if how == "no":
            return "You don't, you told me you're not keen on " + named + "."
        if how == "unsure":
            return "You weren't sure about " + named + ", that's all you've said."
        return "You do, you told me you like " + named + "."
    return None


def _tastes_said(memory):
    """"what do i like?" as the short list of tastes, not the whole summary of what is known.

    Only the tastes are asked for, so only the tastes are said. A store with none answers
    nothing at all and the question goes to whoever can answer it, rather than to a summary that
    would read as a dodge.
    """
    liked, other = [], []
    for taste in user(memory).get("tastes") or []:
        thing = str((taste or {}).get("thing") or "").strip()
        if not thing:
            continue
        how = str(taste.get("how") or "yes")
        if how == "no":
            other.append("You're not keen on " + thing + ".")
        elif how == "unsure":
            other.append("You're not sure about " + thing + ".")
        else:
            liked.append(thing)
    said = []
    if liked:
        joined = liked[0] if len(liked) == 1 else ", ".join(liked[:-1]) + " and " + liked[-1]
        said.append("You like " + joined + ".")
    said.extend(other)
    return " ".join(said) if said else None


AGE_SAID_IN_WORDS = re.compile(
    r"\b(?:(?:i(?:'m| am)|im|you(?:'re| are)|youre|we(?:'re| are)|were|they(?:'re| are)))\s+"
    r"(?:\d{1,3}|a hundred|one|two|three|four|five|six|seven|eight|nine|"
    r"ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
    r"thirty|forty|fifty|sixty|seventy|eighty|ninety)\b", re.I)


def _without_the_age(line):
    """The line with the age taken out of it: "you're 41 and you're training" -> "you're training"."""
    without = AGE_SAID_IN_WORDS.sub("", str(line or ""), count=1).strip(" .,;:!?-")
    return re.sub(r"^(?:and|also|plus)\s+", "", without, flags=re.I).strip()


def _the_words_of_a_fact(value):
    """The words a stored fact is made of, whatever shape the store keeps it in."""
    if isinstance(value, bool):
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_the_words_of_a_fact(part) for part in value.values())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_the_words_of_a_fact(part) for part in value)
    return ""


def _a_fact_the_recap_does_not_say(memory, phrase, body_words):
    """True when this line filed a fact the recap above does not say.

    The topic guard in `_summary_reply` drops the newest line when the word the conversation is on
    appears anywhere in the facts. That is a guess from the topic, so a fact outranks it: a line
    that put something in the store which no part of the summary says is said back, and only the
    lines that add nothing are dropped. The line is matched to its `facts_log` entries the way
    `_recent_told` builds the phrase it says, so the match is the same line and not a lookalike.
    """
    said = _summary_words(body_words)
    for entry in memory.get("facts_log") or []:
        if not isinstance(entry, dict) or not entry.get("key"):
            continue
        text = " ".join(str(entry.get("text") or "").lower().split())
        if " ".join(_told_phrase(extract.no_tone(text)).split()) != phrase:
            continue
        words = _summary_words(_the_words_of_a_fact(user(memory).get(entry["key"])))
        if words - said:
            return True
    return False


def _kids_told(memory):
    """How many children the person said they have, or 0.

    The count is kept on the person (`user.kids`) when they say it ("i've got two kids", "we have
    three children", "i have 2 kids"), so the summary reads the record rather than the line.
    """
    told = user(memory).get("kids")
    if isinstance(told, bool):
        return 0
    if isinstance(told, int):
        return told if told > 0 else 0
    if isinstance(told, str) and told.strip().isdigit():
        return int(told.strip())
    return 0


def _a_child_is_described(memory):
    """True when the store can say a child of theirs by name or age, which says the same thing."""
    for entry in others(memory):
        who = str(entry.get("who") or "").rstrip("s")
        if who and who in CHILD and (entry.get("name") or entry.get("age") or entry.get("ages")):
            return True
    return False


def _a_few_children(count):
    """Two kids, one child, four children - the count the way a person says it."""
    if count == 1:
        return "one child"
    in_words = {number: word for word, number in extract.KID_NUMBERS.items()}
    return in_words.get(count, str(count)) + " kids"


# The chat summed up as a whole, said the way people say it: "whats our plan", "what have we
# decided", "what do we know so far", "tell me what we've agreed", "walk me through what we
# decided", "so whats the state of play", "how far have we got". Every one of them asks for the
# list the chat holds, not for the newest line ("where were we" is `_summary_ask`, and it is the
# newest line) and not for one thing its words name. It has to be the whole line: "what have we
# got for dinner" and "whats the plan for dinner" name a thing and are answered about it, so the
# whole-line match is the fence, and the wrapper words in front ("ok", "so", "and right") and the
# ones that only say when ("so far", "then") come off first.
SUMMED_UP = re.compile(
    r"^(?:ok |okay |right |so |and |but |also |well |quick |just )*(?:"
    r"what (?:have|did) we (?:got|get|have|decided|decide|settled|settle|agreed|agree|know)|"
    r"what do we (?:know|have|got)|"
    r"what(?:'s|\u2019s|s)? (?:our|the) plan|what is (?:our|the) plan|"
    r"tell me what we(?:'ve|\u2019ve|ve)? (?:agreed|decided|settled)|"
    r"walk me through what we (?:decided|agreed|settled)|"
    r"what(?:'s|\u2019s|s)? (?:the )?state of play|what is (?:the )?state of play|"
    r"how far (?:have|did) we (?:got|get)|"
    r"what(?:'s|\u2019s|s)? decided|what is decided"
    r")(?: so far| then| now| again| already| on)*\s*[?.!]*$")


def _summed_up(low):
    """True for a line that asks for the whole chat summed up, rather than for one line of it."""
    return bool(SUMMED_UP.match(str(low or "").strip()))


def _summary_reply(memory):
    known = user(memory)
    parts = []
    if known.get("name"):
        parts.append("you're " + known["name"])
    # Their age is a fact they gave, so it is in the summary: "im 41" then "what do you know about
    # me" answered "not much yet", which reads as the bot not listening. It hangs off the name
    # when there is one ("you're Sam, 41") rather than saying "you're" twice.
    if known.get("age"):
        age = str(known["age"])
        if parts and parts[0].startswith("you're ") and "," not in parts[0]:
            parts[0] += ", " + age
        else:
            parts.append("you're " + age)
    if known.get("job"):
        # The summary says the job the way the job reply does, from its frame: a shift told as
        # "i work nights" is "you work nights" here too, never "a nights".
        said = _job_phrase(known)
        if known.get("city"):
            said += " in " + known["city"]
        parts.append(said)
    elif known.get("city"):
        parts.append("you live in " + known["city"])
    shift = str(known.get("shift") or "").strip()
    if shift:
        # "you work nights", the way the line itself said it, never "a nights".
        parts.append("you work " + shift)
    place = str(known.get("workplace") or "").strip()
    if place:
        # Where they work is kept beside the role: "you're a teacher, and you work in a school".
        parts.append("you work " + _place_phrase(place))
    origin = known.get("from")
    if origin and str(origin).lower() != str(known.get("city") or "").lower():
        parts.append("you're from " + origin)
    said_things = set()
    for pet in known.get("pets") or []:
        parts.append("you've got " + _a_pet(pet))
        said_things.update(str(pet.get(k) or "").lower().rstrip("s") for k in ("animal", "name"))
    # A taste is a thing they told the bot about themselves, so the summary that answers "what do
    # you know about me?" has to carry it: a hedge stays a hedge ("not sure about curry"), and
    # only a plain dislike is said as one (`bot/memory/taste.py`).
    for taste in known.get("tastes") or []:
        thing = str(taste.get("thing") or "").strip()
        if not thing:
            continue
        # A taste about a thing the summary has already named is said once, in the fuller line:
        # "we love our dog" is "you've got a dog, and you like it", not the dog twice over.
        bare = thing.lower()
        bare = bare[5:] if bare.startswith("your ") else bare
        if bare in said_things or bare.rstrip("s") in said_things:
            continue
        how = str(taste.get("how") or "yes")
        if how == "no":
            parts.append("you're not keen on " + thing)
        elif how == "unsure":
            parts.append("you're not sure about " + thing)
        else:
            parts.append("you like " + thing)
    if known.get("allergies"):
        parts.append("you're allergic to " + ", ".join(known["allergies"]))
    named = set()
    for entry in others(memory):
        who = entry.get("who")
        p_allergic = entry.get("allergies") or []
        if who and p_allergic:
            parts.append("your " + who + _is_are(who) + "allergic to " + ", ".join(p_allergic))
            named.add(who)
        # A person they named, or told the age of, is a fact of theirs like the allergy is, and
        # the summary says it the way the recall would: "your mum is called Janet".
        p_name = str(entry.get("name") or "")
        p_age = str(entry.get("age") or "")
        # The ages a group of children was given are one fact, and the summary says them the way
        # the recall does: the verb agrees with the people ("your kids are", never "your kids
        # is"), and every child is in the line.
        p_ages = [age for age in entry.get("ages") or [] if isinstance(age, int)]
        p_diet = str(entry.get("diet") or "")
        if who and p_name and who.rstrip("s") in CHILD and p_age:
            # A child given with a name and an age is said as the child, not as the group they
            # came in: "Ada is 7", because "your kids is called Ada and is 7" is one child too
            # many and the wrong word for them.
            parts.append(_called(p_name) + " is " + p_age)
            named.add(who)
        elif who and p_name:
            said = "your " + who + " is called " + _called(p_name)
            if p_age:
                said += " and is " + p_age
            parts.append(said)
            named.add(who)
        elif who and p_ages:
            said_ages = (", ".join(str(age) for age in p_ages[:-1]) + " and " + str(p_ages[-1])
                         if len(p_ages) > 1 else str(p_ages[0]))
            parts.append("your " + who + _is_are(who) + said_ages)
            named.add(who)
        elif who and p_age and who.rstrip("s") in CHILD:
            # One child, given as an age rather than a count ("i have a 4 year old"): said the
            # way they said it, because "your kids is 4" is not a sentence and does not agree
            # with the word in front of it.
            parts.append("you've got a " + p_age + " year old")
            named.add(who)
        elif who and p_age:
            parts.append("your " + who + " is " + p_age)
            named.add(who)
        if who and p_diet:
            parts.append("your " + who + " " + _a_diet_predicate(who, p_diet))
            named.add(who)
    # A count of children is a fact they gave, and the summary could not say it: the count only
    # ever came back as the line quoted ("you said you have got two kids"), so a chat that had
    # said how many children it had answered "what do you know about me" with everything except
    # them. A child the store can name or age is said as that child, and the count beside it would
    # be the same fact twice.
    told_kids = _kids_told(memory)
    if told_kids and not _a_child_is_described(memory):
        # "you've got a dog and two kids" reads as one line; two "you've got"s in a row reads
        # like a list of records, so a part that already says "you've got" takes the count on.
        if parts and parts[-1].startswith("you've got "):
            parts[-1] += " and " + _a_few_children(told_kids)
        else:
            parts.append("you've got " + _a_few_children(told_kids))
    if known.get("diet"):
        diet = str(known["diet"])
        parts.append("you don't " + _diet_how(diet) + " " + diet[3:] if diet.startswith("no ")
                     else "you're " + diet)
    if known.get("condition"):
        parts.append("you're " + ", ".join(str(c) for c in known["condition"]))
    if known.get("budget"):
        parts.append("your budget is " + str(known["budget"]))
    plans = list(known.get("plans") or [])
    # A correction puts the plan itself under `user["plan"]` (`corrected.py`), and the summary read
    # only the list, so a plan that had been put right was one the recap could not say at all.
    if known.get("plan") and known["plan"] not in plans:
        plans.append(known["plan"])
    last_plan = str(plans[-1]) if plans else ""
    # A plan often names what another part would say: "a picnic for my daughter" makes
    # "you mentioned your daughter" a repeat, so say it once, in the fuller line.
    # The line said back at the end often names the person too ("you said your sister had a baby
    # girl"), so the person is not named twice.
    told = _last_told(memory)
    # A taste already names the thing ("you like your sister's dog"), so a person in it is not
    # named again in the line about them.
    in_tastes = " ".join(str(t.get("thing") or "").lower() for t in known.get("tastes") or [])
    people = [p for p in (known.get("people") or [])
              if p not in named and str(p).lower() not in last_plan.lower()
              and str(p).lower() not in told.lower()
              and str(p).lower() not in in_tastes]
    if people:
        parts.append("you mentioned your " + ", ".join(people[:3]))
    if plans:
        # The plan is said in the shape it was given: a plan they stated ("im going away for 2
        # weeks in june") is a sentence and comes back as one, and a plan that is only the thing
        # itself ("the gym tomorrow") needs a verb in front of it. Saying a sentence after "on
        # about" reads like a machine: "you were on about lose five kilos before summer".
        plan = plan_sentence(plans[-1], plan_line(memory, plans[-1]))
        plan = plan[:1].lower() + plan[1:]
        if known.get("age") and AGE_SAID_IN_WORDS.search(plan):
            # "i'm 41 and i'm training for a marathon" keeps the whole line as its plan, and the
            # age is already said first in the summary: it is said once.
            plan = _without_the_age(plan)
        # The plan often names the person the line above just named ("a picnic for my daughter"
        # makes "you mentioned your daughter" a repeat), so it is said once, in the fuller line.
        if plan and plan.lower() not in " ".join(parts).lower():
            parts.append(plan)
    # The chat itself, said back in their words. It goes last because it is the loosest thing the
    # store knows, and it is left out when a fact above already says it.
    body_words = "; ".join(parts)
    subject = topic_subject(memory).lower()
    # A fact above that already names the thing ("you've got a kitten" for "thinking of getting a
    # kitten", "your daughter is allergic to nuts" for "her nut allergy") says it better than the
    # line itself, so the line is not said again.
    head = subject.split()[-1] if subject else ""
    # The lines themselves, said back in their words, newest first. A fact with no key to live
    # under ("i dont drive", "i work from home") is only the line, and a summary that says the
    # last one alone forgets it as soon as another line goes by. Two is the most that reads like a
    # friend rather than a log.
    facts_body = "; ".join(parts)
    # The newest line is the one the facts above are about, so it is the one the topic guard
    # applies to; an older line is a different thing they told you.
    said_back = 0
    for phrase, from_current in _recent_told(memory, limit=4):
        body_words = "; ".join(parts)
        # Every word of the line is already in the facts above ("im veg" -> "you're veg"), so the
        # line itself would say nothing new: the facts are the same words, said better.
        told_words = _summary_words(phrase)
        covered = bool(told_words) and _says_nothing_new(phrase, told_words, body_words)
        if not covered and told.startswith("you work ") and "you work " in body_words:
            # Where they work is already in the summary, said from the store ("you work in a
            # bakery" after "you work in a school"). The older line said back beside it reads as
            # two answers to the same question: "you work in a bakery; you said you work in a
            # school".
            covered = True
        # "you grew up in Bolton" adds nothing to "you're from Bolton": the thing it names is
        # already in the summary.
        anchor_word = ""
        for word in phrase.split():
            if len(word) > 3 and word.lower() not in SAY_BACK_VAGUE:
                anchor_word = word.lower()
        # The topic guard: the last word of the subject the chat is on, found anywhere in the
        # facts above, means the line is about something already said. It is a guess from the
        # topic, so it gives way to a fact: a line that filed something the recap does not say is
        # never dropped for the topic's sake. Without that, "i live in bristol" set the topic to
        # "live bristol" and the next line, "i've got two kids", was dropped because "bristol" was
        # in the facts above - the count of children was in no reply at all:
        #
        #     i live in bristol        -> Bristol - what's it like there?
        #     i've got two kids        -> Two kids - good to know. How old are they?
        #     what do you know about me-> So far I know you live in Bristol.
        on_topic = (from_current and head and head in facts_body.lower()
                    and not _a_fact_the_recap_does_not_say(memory, phrase, body_words))
        if (covered or _already_said(told_words, body_words)
                or (anchor_word and _summary_words(anchor_word) & _summary_words(body_words))
                or on_topic):
            continue
        # One "you said" and then the facts on their own: "you said X; you said Y" repeats the
        # verb twice in a sentence, which reads like a log rather than a friend.
        parts.append(("you said " if not said_back else "") + phrase)
        said_back += 1
        if said_back >= 2:
            break
    if people and said_back:
        # "you mentioned your dad" is the store's vague mention; once a line says what happened
        # to him, the fuller line is the one to keep.
        said_lines = " ".join(part for part in parts
                              if not part.startswith("you mentioned your ")).lower()
        parts = [part for part in parts
                 if not (part.startswith("you mentioned your ")
                         and any(word in said_lines for word in part.split()[3:]))]
    if not parts:
        if _a_judgement_was_said(memory):
            # A judgement about themselves is never filed as a fact (facts.is_a_judgement), so a
            # chat whose only line about them was one has nothing to recap. "Not much yet - you
            # haven't told me about yourself" one turn after "im a bad mum" is the store telling
            # them it did not hear them, which is the one thing a chat that remembers cannot say:
            # the line is held, it is just not a fact to quote back.
            return pick(["I've got that you're being hard on yourself, and no facts about you yet. "
                         "What should I know?",
                         "I have that you're being hard on yourself - and nothing about your life "
                         "yet that I can say back.",
                         "You've told me how you're feeling about yourself, and nothing about your "
                         "life yet. What should I know?"], memory)
        # Nothing to quote is not the same as having heard nothing. "how do i clean the oven" /
        # "and the grill" / "what do you know about me" denied the whole chat ("you haven't told
        # me about yourself") when what it holds is the two questions, so the reply names the
        # thing the chat has been on. A chat with no subject at all keeps the plain line.
        about = _the_thing_the_chat_is_on(memory)
        if about:
            return pick([
                "Nothing about you yet — so far it's been " + about + ". What should I know?",
                "I've got no facts about you yet; we've been on " + about + ". What should I "
                "know?",
                "No notes about you so far — you've had me on " + about + ". What should I know?"],
                memory)
        return "Not much yet — you haven't told me about yourself. What should I know?"
    body = "; ".join(parts)
    # The same summary twice in a row reads like a machine: the lead-in moves instead.
    return pick(["So far I know " + body + ".",
                 "Here's what you've told me: " + body + ".",
                 "You've told me " + body + "."], memory)


def _quote(text, limit=90):
    """The user's own words, without the full stop before the closing quote.

    A quote that stops in the middle of a word reads like a mistake, so a cut quote gives back
    the part word: "my daughter's 7th bi..." is the one people notice.
    """
    text = " ".join(str(text).split())
    if len(text) > limit:
        cut = text[:limit - 1]
        if not cut.endswith(" ") and " " in cut:
            cut = cut[:cut.rfind(" ")]
        text = cut.rstrip(" ,;:-") + "…"
    return "\"" + text.rstrip(" .!?") + "\""


HEAVY_TOPIC = re.compile(
    r"\b(?:died|dying|death|funeral|passed away|buried|cremation|"
    r"kill myself|killing myself|killed myself|suicide|suicidal|end it all|take my own life|"
    r"hurt myself|hurting myself|self harm|self-harm|cut myself|overdose|"
    r"miscarriage|stillborn|terminal|diagnosed with cancer|beat me|beats me|abuses?d? me|"
    r"bullied|bullying|hit me|hits me|assaulted)\b",
    re.I)


def _heavy(line):
    """True when the line is about a death, a crisis or someone being hurt."""
    return bool(HEAVY_TOPIC.search(" ".join(str(line or "").split())))


def _topics_reply(memory):
    """The subjects the conversation has been on, most recent last."""
    lines = history.topic_lines(memory)
    light = [line for line in lines if not _heavy(line)]
    if not lines:
        return pick(NOTHING_STARTED, memory)
    if not light:
        return pick(["We've been on something heavy, and I won't read it back to you. It is "
                     "still here if you want to talk about it.",
                     "What we've been on is heavy, so I'd rather not put it in quotation marks. "
                     "Say more about it whenever you want."], memory)
    said = "; ".join(_quote(line, 60) for line in light)
    if len(light) < len(lines):
        return pick(["We've been on " + said + ", and on something heavy I won't read back.",
                     "Mostly " + said + ". There was something heavier too, and I have not "
                     "forgotten it."], memory)
    return pick(["We've been on " + said + ".",
                 "Mostly " + said + ".",
                 "Covered so far: " + said + "."], memory)


def _first_sentence(text, limit=70):
    """The first sentence of `text`, cut to `limit`: what the bot opened with, not the whole
    paragraph. A cake-timing answer quoted in full is a wall of text in a one-line reply."""
    text = " ".join(str(text).split())
    end = len(text)
    for mark in (". ", "? ", "! "):
        at = text.find(mark)
        if 0 < at < end:
            end = at + 1
    text = text[:end].strip()
    if len(text) > limit:
        cut = text[:limit - 1]
        if " " in cut:
            cut = cut[:cut.rfind(" ")]
        text = cut.rstrip(" ,;:-") + "…"
    return text.rstrip(" .!?")


CALL_ASK = re.compile(
    r"^\W*(?:and\s+|so\s+|but\s+)?(?:should|shall)\s+(?:i|we)\b"
    r"|^\W*(?:and\s+|so\s+|but\s+)?(?:is|would)\s+(?:it|that)\s+"
    r"(?:safe|ok|okay|alright|fine|worth|sensible|wise|a good idea|a bad idea|too (?:late|soon))\b"
    r"|^\W*(?:and\s+|so\s+|but\s+)?(?:do|must)\s+(?:i|we)\s+(?:need to|have to|really need to)\b"
    r"|^\W*(?:and\s+|so\s+|but\s+)?(?:can|could)\s+(?:i|we)\s+(?:still|keep|go)\b")


CARRY_ON = re.compile(
    r"\b(?:keep|keeps|keep on|carry on|carrying on|go on|going|continue|continuing|"
    r"start|starting|start again|go back|back to|train|training|run|running|walk|walking|"
    r"drive|driving|ride|riding|cycle|cycling|swim|swimming|lift|lifting|play|playing|"
    r"work out|exercise|"
    r"push on|push through|try|it|that)\b", re.I)


STOP_IT = re.compile(
    r"\b(?:stop|stopping|quit|quitting|give up|giving up|lay off|rest|resting|take a break)\b",
    re.I)


STOP_CONDITION = re.compile(
    r"^(?:and\s+)?(?:see|ask|call|ring|go to|get|speak to|talk to|tell|stop|if)\b", re.I)


CLAUSE_SPLIT = re.compile(r":\s+|(?<=[.!?])\s+|,\s+(?:and|but|so)\s+")


SEE_SOMEONE = re.compile(
    r"\b(?:see|sees|seeing|call|calling|ring|ringing|go to|going to|get|getting|book|booked|"
    r"visit|visiting|speak to|speaking to|talk to|talking to|check|checked|checked out)\s+"
    r"(?:\w+\s+){0,2}(?:someone|somebody|anyone|a doctor|the doctor|my doctor|doctor|gp|physio|"
    r"nurse|hospital|a&e|ae|surgery|specialist|professional|it checked|this checked|that checked)\b",
    re.I)


HALF_AN_HOUR = re.compile(r"\bhalf\s+an\s+hour\b", re.I)


TIME_LENGTH = re.compile(
    r"\b(?P<count>\d+|an?|a\s+couple\s+of|a\s+few|"
    r"one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|"
    r"thirty|forty|forty-five|fifty|sixty|ninety)\s*-?\s*"
    r"(?P<unit>minutes?|mins?|hours?|hrs?)\b", re.I)


LENGTH_FILLER = frozenset(
    "a an the about roughly around give take or and plus maybe depending on it takes that this is "
    "of to for at least more less just only or so too up each per in all altogether total tops "
    "time".split())


LEAD_LABEL = re.compile(r"^[A-Za-z][A-Za-z' -]{0,14}:\s*")


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


SPLIT_MOVES = re.compile(r";\s+|\s+-\s+|\s+\u2014\s+|,\s+or\s+|;\s*or\s+")


BUDGET = re.compile(
    r"^\W*(?:(?:and|but|so|oh|also|well|yeah|yep|ok|okay|right|alright)\W+)*"
    r"(?:i|we|ive|i\'ve|weve|we\'ve)\s+"
    r"(?:(?:really|only|just|literally|maybe|probably|actually)\s+)*"
    r"(?:get|got|have|had|make|leave|take|need|needs|fancy)\s+"
    r"(?:(?:only|just|maybe|about|altogether|in total|tops|roughly)\s+)*"
    r"(?P<length>" + LENGTH + r")\b", re.I)


A_HORIZON = re.compile(
    r"\b(?:for|after|over|in|within)\s+(?:the\s+)?(?:first\s+|next\s+|following\s+)?"
    r"(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|few|couple(?:\s+of)?)"
    r"\s+(?:days?|weeks?|months?)\b", re.I)


def _sentences(answer):
    """The sentences of an answer, in the order given."""
    return [part.strip() for part in SENTENCE_SPLIT.split(" ".join(str(answer or "").split())) if part.strip()]


def _halves(sentence):
    """A sentence cut where a semicolon, a dash or an "or" joins two moves."""
    parts = []
    for part in SPLIT_MOVES.split(sentence):
        part = LEAD_LABEL.sub("", part.strip(" .;,"))
        if part:
            parts.append(part)
    return parts
