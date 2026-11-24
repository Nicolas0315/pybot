"""Part 3 of 6 of a large module, split out of `arbiter`.

Everything here is re-exported from `arbiter`, so callers import it from there as before.
"""
import importlib
import re

from ..compose import facts, fallback
from .arbiter_part_01 import (
    SAFETY, _places_the_figure, _priority, _repeat, WORD, MOVE_ANSWER_WORDS, MOVE_SHARE, MOVE_WHOLE,
    MOVE_WORDS, RECALL, PAUSE, WHOLE_LINE_BAND, _ack,
)
from .arbiter_part_02 import (
    _a_bare_doubt_reply, _content, ECHO_STOP, THEIR_VOICE, _the_ask_after_the_facts, POOL_MODULES,
    _hands_the_decision_back, A_SUBJECT_WORD, NOT_A_SUBJECT_WORD, _one_word,
    _declares_claims_instead, _CONDOLENCE, _THE_NAMELESS, THE_CAUSE, _PEOPLE, _composer_reading,
    _ABOUT_SOMEONE_ELSE, _A_HOW_TO, _A_PERSON_NAMED, _THE_ONE_NAMED, _a_refusal, _a_story_opened,
    _repeat_leads,
)


def _the_card_that_places_the_figure(candidates, best, text, memory):
    """A card that puts the figure against a range beats the composer's ask for a second figure.

    The operator's rule: the reply that fits the line most closely wins, and a broad "
    what are you comparing it with" is beaten by the one that says what the figure is like. The
    hand-back is still the answer when no card has a range - that is the whole point of it - so
    this only moves the turn when a candidate both names what the line is about and carries a
    figure (`_places_the_figure`).
    """
    if not _a_bare_doubt_reply(candidates[best], text, memory):
        return best
    for index in range(len(candidates)):
        if index == best or _priority(candidates[index]) >= SAFETY:
            continue
        reply = candidates[index].get("reply")
        if _places_the_figure(reply) and _names_what_they_said(reply, text, memory):
            return index
    return best


def _said_it_already(candidates, text, memory, last=""):
    """The index of the composer's said-it-already reply, when it is the only new thing here.

    Asked only when no real candidate has anything new to say (see `_choose`). The composer owns
    both halves of this - the reading of the line as a repeat and the wording - so the arbiter
    only recognises the line and lets it through; it keeps no vocabulary of its own.

    Only a repeat that has lost something counts. The whole answer said again still answers a
    narrower question ("what about tea" is in the answer about water, word for word) and STYLE.md
    would rather have it twice than a shrug; the opening of it, with the rest gone, does not.
    """
    if not last or not fallback.says_it_already(text, memory):
        return None
    real = [candidate for candidate in candidates if _priority(candidate) >= 0]
    if not real:
        return None
    first = _content(real[0].get("reply"))
    if not _echoes(first, last) or len(first.split()) >= len(last.split()) - 3:
        return None
    # ... and only when what is gone is what they asked about. "What about tea" is answered by
    # the shortened line about water, which names tea, so it still answers the question; "how do
    # i free up space" is not answered by the opening, which names the space and drops every way
    # of freeing it.
    # The words of a figure ask are the asking, not the thing asked about. "how many times a
    # week" is answered by "Three runs a week", and "times" is nothing the answer had to keep, so
    # the repeat was read as one that had lost what was asked and the person got "That is all of
    # what I know on it" instead of "Three runs a week gets most people to 5k in about eight
    # weeks". The ask is stripped with the store's own patterns (`repeat.FIGURE_ASKS`), which is
    # the reading `repeat.the_figure_asked` makes of the same line, so a figure ask added there
    # is read here too.
    subject = str(text or "")
    for figure in getattr(_repeat, "FIGURE_ASKS", ()) or ():
        try:
            _name, ask, _says = figure
        except (TypeError, ValueError):
            continue
        # Every ask that the line matches, each read against the whole line, and the shortest
        # result wins: "how many times a week" is one ask for a count ("how many") and one for a
        # rate ("how many times"), and stripping them one after the other leaves "times" behind
        # because the second no longer matches what the first left. The thing asked about is
        # what is left when as much of the asking as possible has been taken out.
        try:
            if ask.search(str(text or "")):
                shorter = ask.sub(" ", str(text or ""))
                if len(shorter) < len(subject):
                    subject = shorter
        except AttributeError:
            continue
    # A bare figure ask names no subject: "how much should i take", "how long should i leave
    # it". The words left after the ask phrase is taken out ("should", "i", "take") are the
    # asking, not the thing asked about, so a shorter answer that gives the figure has not lost
    # what they asked for. Without this the amount sentence "1 to 2 mg about an hour before bed"
    # was read as a repeat that dropped the verb "take", and the shrug took the turn.
    if _repeat is not None:
        left = [word for word in re.findall(r"[a-z']+", subject)
                if word not in getattr(_repeat, "FIGURE_WORDS", ())
                and word not in getattr(_repeat, "FIGURE_SAYING", ())]
        if not left:
            return None
    last_words = set(last.split())
    asked = [word for word in fallback.content_words(subject)
             if word in last_words or word.rstrip("s") in last_words or word + "s" in last_words]
    if not asked:
        return None
    said = set(first.split())
    missing = [word for word in asked
               if word not in said and word.rstrip("s") not in said and word + "s" not in said]
    if len(missing) * 2 < len(asked):
        return None
    for index, candidate in enumerate(candidates):
        if _priority(candidate) < 0 and fallback.is_said_it_already(candidate.get("reply")):
            return index
    return None


ACK_POOL = None


def _ack_lines():
    """The lines `chat` closes a conversation with, reduced the way a reply is compared."""
    global ACK_POOL
    if ACK_POOL is None:
        try:
            module = importlib.import_module(".chat", 'bot.modules')
            pools = getattr(module, "REPLIES", None) or {}
            ACK_POOL = frozenset(_content(line) for line in pools.get("ack", ()))
        except Exception:  # noqa: BLE001 - no pool means nothing is read as a stock close
            ACK_POOL = frozenset()
    return ACK_POOL


def _the_reply_is_the_report(candidate, text, memory):
    """Is this candidate the composer's own reply to a report on the advice just given?

    The reading is the composer's (`fallback.the_report_reply`), and it is the same call the
    module proposing the reply makes, so the arbiter compares two replies rather than keeping a
    second copy of the reading. It exists because a report on the advice is the composer's
    subject, and the module that proposes its reply sits under the floor: "i wiped it and now its
    worse" after the oven answer was answered by `chat`'s tired pool - the word "wiped" read as
    tiredness - over the composer's "Stop and leave it alone. Worse is the answer ...", and
    `_a_real_answer_besides` counted that pool line as an answer to the line.
    """
    reply = _content(candidate.get("reply"))
    if not reply:
        return False
    try:
        own = _content(fallback.the_report_reply(text, memory))
    except Exception:  # noqa: BLE001 - a reading that fails is not a claim
        return False
    return bool(own) and own == reply


def _real_answers_besides(candidates, last=""):
    """The candidates of modules above the floor that said something to the line.

    Being above the floor is not the same as answering: `chat` sits at 300 on every line and its
    acknowledgement pool signs the conversation off ("Alright then - good luck with it."). A hook
    that gives way to that hands the person a goodbye, which is what the whole of this rule is
    meant to stop. The pool is read from the module that owns it, so nothing here is a second copy
    of somebody's wording, and a reply that only repeats the last answer is not an answer either.
    """
    said = []
    for candidate in candidates:
        if _priority(candidate) <= 0:
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == _content(last)):
            continue
        if candidate.get("module") == "chat" and reply in _ack_lines():
            continue
        said.append(candidate)
    return said


def _only_says_the_line_back(reply, text):
    """True when a reply is made of nothing but the words the person has just used.

    The store claims a line for the fact in it and says that fact back ("Your sister is veggie."),
    which is the answer to a line that only states it and no answer at all to the question after
    it. A reply that adds no word of its own has read nothing new, so it cannot be what the person
    asked for.
    """
    words = WORD.findall(_content(reply))
    if not words or len(words) > 14:
        return False
    said = set(WORD.findall((text or "").lower()))
    said |= {THEIR_VOICE.get(word, word) for word in said}
    body = [word for word in words if word not in ECHO_STOP and len(word) > 2]
    if not body:
        return False
    return all(word in said for word in body)


def _the_candidates_that_answer_the_ask(text, candidates, pool):
    """The pool without the reply that only says the person's own line back, or None to keep it.

    None when the line asks nothing after its facts, when every candidate in the pool says
    something of its own, or when the only reply left is a floor line - a line whose one answer is
    the fact said back keeps it, because telling the person less is worse than telling them what
    they already knew.
    """
    if not _the_ask_after_the_facts(text):
        return None
    answering = [index for index in pool
                 if not _only_says_the_line_back(_content(candidates[index].get("reply")), text)]
    if not answering or len(answering) == len(pool):
        return None
    if not any(_priority(candidates[index]) >= 0 for index in answering):
        return None
    return answering


def _a_card_besides(candidates, index):
    """True when a module with a subject of its own proposed something beside this candidate.

    A report on the advice can be the only reading of a line - "i wiped it and now its worse" is
    not a question and names no subject to look up - and then the composer's reply is the answer,
    not a pool line's. Where a card is beside it ("done that" after the emails answer still has
    the next part of that answer to give), the card keeps the turn and this reading is not
    consulted.
    """
    for other, candidate in enumerate(candidates):
        if other == index:
            continue
        if candidate.get("module") in POOL_MODULES:
            continue
        if _content(candidate.get("reply")):
            return True
    return False


def _a_real_answer_besides(candidates, last=""):
    """True when some module above the floor said something to the line rather than closing it.

    Being above the floor is not the same as answering: `chat` sits at 300 on every line and its
    acknowledgement pool signs the conversation off ("Alright then - good luck with it."). A hook
    that gives way to that hands the person a goodbye, which is what the whole of this rule is
    meant to stop. The pool is read from the module that owns it, so nothing here is a second copy
    of somebody's wording, and a reply that only repeats the last answer is not an answer either.
    """
    return bool(_real_answers_besides(candidates, last))


def _only_a_hand_back_besides(candidates, last=""):
    """True when the only answer above the floor hands the decision back, else False.

    `_a_real_answer_besides` counts a hand-back as an answer, so that a hook from below the floor
    cannot take the turn off it - the same reason a stock close is not counted: a hook that gives
    way to a goodbye hands the person nothing. But a hand-back is not the answer to a judgement
    either (see `_hands_the_decision_back`), and a take from under the floor that says the one
    thing about the thing is a better reply than asking the question back. This is the test that
    tells the two cases apart: everything above the floor here is a hand-back.
    """
    found = False
    for candidate in candidates:
        if _priority(candidate) < 0:
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == _content(last)):
            continue
        if candidate.get("module") == "chat" and reply in _ack_lines():
            continue
        if not _hands_the_decision_back(candidate.get("reply") or ""):
            return False
        found = True
    return found


def _names_what_they_said(reply, text, memory):
    """True when the reply says a word from what the person has told the bot, else False.

    A take from under the floor may beat a hand-back, but only where it is about the same thing:
    the composer's pool for "is that a good idea" after "im thinking of getting a cat" says the cat
    back ("getting a cat is worth doing"), and the pool it reaches on another line said "Honestly
    I can't tell you what it's like there. What matters most to you about the trip?" after "im
    thinking of going vegetarian" - a sentence about a trip nobody mentioned, which only surfaced
    once the hand-back stopped outranking it. What separates them is the subject, so the reply has
    to share a word with the thread that is not one every sentence holds.
    """
    said = set(A_SUBJECT_WORD.findall(_content(text)))
    for turn in reversed((memory or {}).get("turns") or []):
        if isinstance(turn, dict):
            said.update(A_SUBJECT_WORD.findall(_content(turn.get("user"))))
        if len(said) > 80:
            break
    # The form of a word is not the word: the card that answers "im going to walk to work" says
    # "Walking counts, and brisk walking for 30 minutes most days does most of it", and "walk" and
    # "walking" were not the same word, so the one sentence about the line was passed over and the
    # composer's pool from under the floor took the turn ("Yes - wanting to walk to work is worth
    # doing. The one thing to have ready is an answer for what if it goes wrong."). The ending on
    # a word is not a different word, so the two are compared by their stem (see `_one_word`).
    said -= NOT_A_SUBJECT_WORD
    words = set(A_SUBJECT_WORD.findall(_content(reply))) - NOT_A_SUBJECT_WORD
    if said & words:
        return True
    return any(_one_word(one, other) for one in said for other in words)


def _claims_instead(text, memory, candidates, last="", above=None):
    """The index of a real candidate whose module says it answers a line another module claims.

    "how do i unblock my sink" is answered with the plunger and the trap, and the line after it -
    "i tried that and it didn't work" - is read by the composer as a report on that advice, so it
    claims the turn as it comes. What the composer then says is about the attempt ("say what you
    did and that it hasn't shifted"); the module that knows who does the job once a home fix has
    run out ("a plumber, with the plunger and the trap already ruled out") has the answer, and the
    claim takes the turn from it. That is a routing fault, and it cannot be fixed by looking for
    the advice's words in the candidates' replies: word overlap let a wrong answer line through on
    a phone-battery thread and turned "my knee is sore when i run / its not helping" into the
    fallback's shrug.

    So the claim is given up only to a module that says so itself: it declares
    `CLAIMS_INSTEAD(text, memory) -> bool` and says yes only on the lines where its own proposal
    is the answer to the claimed line, never to win turns. PRIORITY still settles the rest - a
    claim from a module above the declaring one keeps the turn, so the memory store's reading of
    "places to eat near the old town" is not displaced by a general answer - and the safety band
    was read before this. A reply that only says the bot's last line again is not an answer, so
    it does not displace anything.
    """
    for index, candidate in enumerate(candidates):
        if _priority(candidate) < 0:
            continue
        if above is not None and _priority(candidate) <= above:
            continue
        name = candidate.get("module")
        if not _declares_claims_instead(name, text, memory):
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == last):
            continue
        return index
    return None


def _the_move_in_hand(candidates, real, text, last):
    """The index of the step out of the answer just given, on a line that asks for it, else None.

    "where do i start" after an answer names nothing to look up: it asks which part of the answer
    in hand to do first. The composer reads that and hands the step back ("The thing to do first:
    Keep them short and filed."), and the entry that wrote the answer is asked by the same line and
    writes the same answer again at full length, in its second wording - so the never-repeat rule
    does not see a repeat either, and the specialist rule then gives the turn to the paragraph the
    person has just read ("i want to stop biting my nails" / "where do i start" came back as the
    nail-biting paragraph a second time).

    What makes a reply a form of the answer is its words: nearly every one of them is a word the
    answer used, or it runs to the answer's own length and is the answer again in other words. A
    step is the shortest of them and one clause long; a paragraph is not. And the
    paragraph has to be the answer again, not a part of it: a reply that runs to three quarters of
    the answer's own length re-tells it, while an entry that has already taken a step out of the
    answer ("The first thing I would change: Ease off running ...") says a third of it, and that
    is answering the same way the composer does, so this rule leaves it alone. Nothing here reads
    the topic, so a step that is genuinely about something else cannot be taken for the answer's
    own (`names_nothing` and `MOVE_ASK` are the memory lane's readings, not a word list here).
    """
    if not last or _repeat is None:
        return None
    try:
        if not _repeat.names_nothing(text) or not _repeat.MOVE_ASK.search(str(text or "")):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return None
    if len(real) < 2:
        return None
    said = last.split()
    seen = set(said)
    forms = []
    whole = False
    for index in real:
        words = _content(candidates[index].get("reply")).split()
        if not words:
            continue
        share = sum(1 for word in words if word in seen) / len(words)
        of_the_answer = share >= MOVE_SHARE
        re_tells = len(said) >= MOVE_ANSWER_WORDS and len(words) >= len(said) * MOVE_WHOLE
        if re_tells:
            # A reply as long as the answer is the answer again, whatever words it picks: main's
            # entries are rewritten between commits, and the paragraph that came back for "i want
            # to stop biting my nails" / "where do i start" was another entry's wording of it,
            # sharing too few words to be caught by the share alone.
            whole = True
        if of_the_answer or re_tells:
            forms.append((len(words), index, of_the_answer))
    if not whole:
        return None
    # The step has to be made of the answer's own words, whatever else is on offer: a re-tell may
    # share almost none of them (it is the entry's second wording) but a *step* that shares none
    # is not a part of this answer at all - it is a hedge ("Nothing to do on my side, honestly")
    # or a line pointing at a list from another turn ("the rest in the order I gave them"), and
    # both of those are shorter than the step that should have won.
    sharing = [form for form in forms if form[2]]
    if len(forms) < 2 or not sharing:
        return None
    shortest, index, _ = min(sharing)
    longest = max(length for length, _, _ in forms)
    if shortest > MOVE_WORDS or shortest * 3 > longest * 2:
        return None  # nothing here is a step, or the step is not clearly shorter than the re-tell
    return index


def _made_of_the_answer(reply, seen):
    """True when the reply is the answer's own words and next to nothing else, else False."""
    words = _content(reply).split()
    return bool(words) and sum(1 for word in words if word in seen) / len(words) >= MOVE_SHARE


def _a_condolence(reply):
    """Whether *reply* opens as comfort for a loss rather than as an answer about a thing."""
    said = _content(reply).lower()
    return bool(said) and bool(_CONDOLENCE.match(said))


def _says_the_subject(reply, line):
    """Whether *reply* says a word of *line* that names something (four letters or more)."""
    said = {word for word in WORD.findall(_content(reply).lower()) if len(word) >= 4}
    if not said:
        return False
    for word in WORD.findall(line):
        if len(word) < 4 or word in _THE_NAMELESS:
            continue
        for other in said:
            if other.startswith(word) or word.startswith(other):
                return True
    return False


def _the_cause_asked_for(candidates, real, text, best):
    """The entry's answer to "why is this thing failing" beats the composer's condolence.

    "why are my fish dying" was answered "I'm so sorry to hear that. It's a hard thing to carry -
    I'm here if you want to talk about it, or if anything practical would help": the loss composer
    read a pet going under as a bereavement, and the water entry's answer ("A fish sitting on the
    bottom, or hanging at the surface gulping, is reacting to the water rather than to you, and
    ammonia is the usual cause ...") was in the turn and lost, because it is an ordinary entry
    under a module that reads the whole line. A condolence answers a loss somebody has had; a
    question about why a living thing is failing asks for the cause, and the entry that names the
    thing is the one that has it.
    """
    if not _a_condolence(candidates[best].get("reply")):
        return None
    line = _content(text).lower()
    if not THE_CAUSE.search(line):
        return None
    if _says_the_subject(candidates[best].get("reply"), line):
        # A condolence that names the thing ("I'm so sorry about your fish") is about it, so the
        # person is being answered about what they asked about, and it keeps the turn.
        return None
    if set(WORD.findall(line)) & _PEOPLE:
        return None
    for index in real:
        if index == best:
            continue
        if _says_the_subject(candidates[index].get("reply"), line):
            return index
    return None


def _the_date_fact(candidates, real, text):
    """The store's date is the answer to a "when is it" ask, and a card about the subject is not.

    "when do we fly" after "no in july" was answered with the airport check-in card, and "when is
    my dentist appointment" after "im at the dentist on tuesday" with "ring practices near you and
    ask whether they take new NHS patients" - the subject matched and the date did not, so the
    specialist rule handed the turn to the card. A line that asks when something is wants the fact
    back, and the store is the only module that has it (see bot/compose/facts.py).
    """
    if not facts.asks_for_a_when(_content(text)):
        return None
    store = None
    for index in real:
        candidate = candidates[index]
        if candidate.get("module") != "memory_store":
            continue
        if _priority(candidate) < RECALL:
            continue
        if facts.the_fact_asked_for(_content(text), _content(candidate.get("reply"))):
            store = index
            break
    if store is None:
        return None
    # A reply that names the same date needs no help: the store's bare fact is not better than a
    # card that carries it and goes on to say something useful. "what time is my flight" after "my
    # flight is at 6am" / "no, 8" is answered "You told me your flight is at 8am, so be at the
    # airport by 6am ...", and "At 8am." alone would trade that away.
    said = _content(candidates[store].get("reply"))
    for index in real:
        if index == store:
            continue
        if facts.the_same_date(_content(candidates[index].get("reply")), said):
            return None
    return store


def _the_next_part(candidates, text, last):
    """The index of the next part of the answer in hand, on a line that asks for more, else None.

    "what else" after "The thing to do first: Keep them short and filed" asks for the part after
    the step, and the entry that wrote the answer reads the line as the same question and hands
    back the whole paragraph - the answer a third time, at the length it was the first time. The
    memory lane walks the answer in order and hands back the part that comes next
    (`bot/memory/repeat.py`: `NEXT_ASK`, `_another_part`), and this rule keeps the turn for it.

    The line is picked out the way the step is: by the memory lane's own readings
    (`asks_for_more`, `NEXT_LEADS`, `ALSO_LEADS` in bot/memory/repeat.py), so this rule keeps no
    vocabulary of its own. Only the ask the memory lane reads as this one comes here, so nothing
    else moves.
    """
    if not last or _repeat is None:
        return None
    try:
        if not _repeat.asks_for_more(text):
            return None
        leads = tuple(getattr(_repeat, "NEXT_LEADS", ())) + tuple(getattr(_repeat, "ALSO_LEADS", ()))
    except Exception:  # noqa: BLE001 - a reading that fails claims no turn
        return None
    return _a_lead_line(candidates, leads, last)


def _a_lead_line(candidates, leads, last):
    """The index of the memory lane's own short form of the answer in hand, else None.

    Every line the memory lane hands back out of an answer opens with one of its leads ("The
    thing to do first:", "After that:"), and the leads are that lane's constants, so recognising
    the line costs the arbiter no vocabulary of its own. The lead alone does not pick between two
    of them: an entry that takes a step out of its own answer says the same thing as the
    composer's cut of it, and the one that says more is the better reply, so the longest wins.
    The reply just given is no answer, and never answers itself.
    """
    openers = tuple(str(lead).split("{")[0].strip().lower() for lead in leads if str(lead))
    if not openers:
        return None
    found = []
    for index, candidate in enumerate(candidates):
        reply = str(candidate.get("reply") or "").strip()
        if not reply or not reply.lower().startswith(openers):
            continue
        if last and _content(reply) == last:
            continue
        found.append((len(_content(reply).split()), index))
    if not found:
        return None
    found.sort()
    return found[-1][1]


def _verdict_lines():
    """The composer's own lines for a verdict on the news (bot/compose/fallback.py)."""
    lines = set()
    for name in ("VERDICT_ANNOY", "VERDICT_LUCK", "VERDICT_SHAME", "VERDICT_ROUGH",
                 "VERDICT_HEAVY", "VERDICT_NUMB"):
        try:
            lines.update(getattr(fallback, name, ()))
        except Exception:  # noqa: BLE001 - a pool that cannot be read claims nothing
            continue
    # The same reduction the other matchers in this file use (`CALLED_BACK`, `leaving.lines()`):
    # a pool line carries its own punctuation and capital letters, and a reply that came back
    # through `_choose` is the same words, so comparing the raw text against the reduced one
    # never matched and the rule below never fired.
    return frozenset(_content(line) for line in lines)


def _the_verdict_turn(candidates, lines):
    """The index of the candidate whose reply IS the composer's verdict line, else None.

    Matching the line rather than skipping the ones that are wrong is what makes the rule hold:
    "im being evicted next week" then "thats a nightmare" was answered by the sleep entry
    ("Nightmares usually follow stress, late food, alcohol or a heavy film before bed"), and
    "my landlord wont fix the boiler" then "what a headache" by the headache entry, because any
    card that happens to own the noun won the topic rule. A verdict has no subject of its own, so
    the composer's line for it takes the turn and the cards that own the word stand down.
    """
    for index, candidate in enumerate(candidates):
        if _content(candidate.get("reply")) in lines:
            return index
    return None


def _pause_reply(candidates, pool, text, memory, last=""):
    """The index of the composer's line for an apology about the chat pausing, or None.

    "sorry for not replying" is an apology for the gap and nothing else, and a topic entry can
    still take it on a word of it: the answers module read "reply" and "message" as a request
    to draft an email, so a person who had just said sorry for being away was told to "say the
    ask in the first line". The reading and the wording are the composer's
    (`fallback.reads_as_pause`, `fallback.CAME_BACK`); the arbiter only keeps the turn where it
    belongs, the way it does for a goodbye.

    Not at the expense of a module that read the whole line itself: the loss and grief bands sit
    above `WHOLE_LINE_BAND` and their turn stands, and a safety thread was answered before this
    (`_composer_reading` returns THREAD for it, so there is no pause to keep).
    """
    try:
        # The composer's own reading decides, including where it does not apply: a condolence
        # thread or a live crisis has its own voice, so it returns no pause there.
        if _composer_reading(text, memory)[0] != PAUSE:
            return None
        said = {_content(line) for line in fallback.CAME_BACK}
        # A line that only points back at the conversation is the same kind for the arbiter's
        # purpose - no topic entry may take it back on a word of it - so its pool is read here
        # too. The version that asks about the thing named after the phrase ("as i was saying
        # about the car") is that pool with the thing filled in, so the thing is what the reply
        # has to be built from.
        said |= {_content(line) for line in fallback.RETURNED_TO_IT}
        named = fallback.reads_as_a_return(text)
        if named:
            said |= {_content(line.format(thing=named))
                    for line in fallback.RETURNED_TO_A_THING}
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    kept = None
    for index in pool:
        if _priority(candidates[index]) >= WHOLE_LINE_BAND:
            return None  # a module that read the whole line has the better claim
    for index, candidate in enumerate(candidates):
        said_back = _content(candidate.get("reply"))
        if said_back not in said:
            continue
        if not last or said_back != last:
            return index
        kept = index if kept is None else kept
    return kept


def _the_store_revises_the_answer(candidates, pool, memory, text, last=""):
    """The store's reply on the turn the person says one thing in it is out, else None.

    A suggestion is often a list, and the line after it takes one thing off the list: after "what
    can i add to chicken salad" the reply names celery, red onion, apple and walnuts, and "and i
    hate celery" is answered by giving the list back without the celery. Only the store can do
    that. It read the dislike, and its reply is the answer the person already has with the food
    they will not eat taken out.

    The knowledge base cannot know it: the line has the word "celery" in it, so the five-a-day
    entry answers "a portion is a handful - about 80g" and the person who said what they do not
    eat is told about fruit and vegetables instead. The store's reply scores nothing on the
    conversation's topic and the entry scores on it, so the last rule in `_choose` has to pick
    the entry unless this one takes the turn first.

    Narrow on purpose, and each gate is a test:

    - the line has to say the thing the store holds as their dislike (the store's own reading, not
      a second reader here), so a line about something else never qualifies;
    - the store has to have proposed on this line, which it only does when it read the line as the
      revision;
    - its reply has to carry five words in a row of the last answer, which is what makes it the
      answer in hand rather than a new one, and keeps a store reply that shares nothing with the
      answer (`"Celery - got it, that is out of anything I suggest"`) under the ordinary rules.
    """
    if not last or not isinstance(memory, dict):
        return None
    # Their own dislikes and their guests': "she doesnt eat meat" then "and she hates mushrooms" is
    # the same turn as "and i hate celery", and the store holds the suggestion both times.
    held = [memory.get("user")]
    others = memory.get("others")
    if isinstance(others, list):
        held.extend(others)
    dislikes = [str(thing).lower()
                for person in held if isinstance(person, dict)
                for thing in (person.get("dislikes") or []) if thing]
    if not dislikes:
        return None
    said = set(_content(text).split())
    if not said & set(dislikes):
        return None  # the line did not name the thing they do not eat
    previous = last.split()
    for index in pool:
        if candidates[index].get("module") != "memory_store":
            continue
        reply = candidates[index].get("reply") or ""
        if _a_clause_was_cut_in_half(reply):
            continue
        words = _content(reply).split()
        for start in range(0, max(0, len(words) - 4)):
            run = words[start:start + 5]
            if len(run) == 5 and _a_run_of(previous, run):
                return index
    return None


def _a_clause_was_cut_in_half(reply):
    """True when a reply splices a describing clause onto a list, so it reads as two halves.

    The store builds a revision by keeping the list of things from the answer and dropping the
    one that is out. Where the answer put a clause beside the list ("a chickpea and vegetable
    traybake, made in the largest dish you own, which feeds eight from one oven") the same
    keeping word by word gives "a chickpea and vegetable traybake, made in the largest dish you
    own or which feeds eight from one oven all still work" - the list and the clause stitched at
    the wrong place. That is a fault in the store's own wording, and until it builds the list
    without the clause the ordinary answer is the one to give, so the relative pronoun says the
    revision was cut in half.
    """
    words = _content(reply).split()
    return any(word in ("which", "whose") for word in words)


def _store_correcting(candidates, pool, memory, text, last=""):
    """The store's reply on the turn the person corrects what they just said, else None.

    A correction is a line that only replaces something said a moment ago ("my budget is 500"
    then "make it 900"). The understanding engine finds no topic in it, but a knowledge entry
    keyed on its words can: "make it 900" reached the budget-split entry, so the person got a
    lecture about splitting their income instead of "900 - got it". Only the store knows the line
    is a correction of the turn before (the shared `memory["correction"]` says which line it
    was), and no entry can, so on that turn the store's reply is the one they are owed.

    Nothing here reads a reply's wording: the store has to have proposed on this line (its own
    reader decides that) and the never-repeat rule still holds.
    """
    fixed = memory.get("correction") if isinstance(memory, dict) else None
    if not isinstance(fixed, dict) or not fixed.get("value"):
        return None
    if str(fixed.get("said") or "") != " ".join(str(text or "").lower().split()):
        return None  # this is not the line that made the correction
    for index in pool:
        if candidates[index].get("module") != "memory_store":
            continue
        if last and _content(candidates[index].get("reply")) == last:
            return None  # the reply just given is no answer to a correction
        return index


def _draft_index(candidates, last, clean=""):
    """The composer's promised draft, or its offer to write it, or None.

    A line asking for help with a message is answered, honestly, by asking for the two things a
    message needs: who it is for and what it should say. The next line is that detail ("saying im
    off sick tomorrow"), and on main it was echoed back or met with a topic entry that took it on
    a word ("my car broke down" got the hard-shoulder advice instead of the note the person was
    told to hand over). An offer the bot then drops is worse than never offering.

    This is the one place a composer reply is chosen ahead of every other candidate, before
    `_instead`: it is safe only because the composer drafts on its own gates (the offer in the
    bot's last turn, and a line that is not news, a symptom, a mood or a fragment). Any widening
    of the draft has to keep those gates, or this turns routing into a priority raise.

    The composer already writes the draft, so the routing decision is only to give the turn to
    the module the composer answers through - `fallback.FALLBACK_MODULE`, the one module whose
    whole reply is the composer's - when that reply is the drafted message. The module is matched
    rather than the text, because the composer draws its pool twice (see `_thread_index`), and the
    draft is recognised by its own lead-in, so a composer reply that is a statement or a
    continuation never claims the turn this way.

    The offer half is read the same way and only on a line that asks for the words: "can you help
    me write a text to my landlord" got the tenancy entry, which answers about housing and not
    about the message, and its example text was about a rota for a different person entirely. A
    card can be right about the topic and still be the wrong answer to "write me the words", so
    the offer takes the turn and the next line is the message. Both readings live in
    bot/compose/draft.py, and the composer only offers when it has nothing to draft from.

    What the offer may not displace is another answer that hands the words over: the writing card
    answers the same line with the shape to aim at and "tell me who it is for and what you need
    and I will write yours", and a card can answer it with the note itself in quotation marks.
    Both are the offer plus something, so the turn is only taken when no other candidate promises
    to write the message or already hands one over, and the cards keep the lines they were
    written for.
    """
    for index, candidate in enumerate(candidates):
        if candidate.get("module") != fallback.FALLBACK_MODULE:
            continue
        reply = candidate.get("reply")
        if not _content(reply) or _content(reply) == last:
            return None
        if fallback.draft.names_a_draft(reply):
            return index
        if (clean and fallback.draft.offers_a_draft(reply)
                and fallback.draft.reads_as_a_writing_ask(clean)
                and not any(fallback.draft.offers_a_draft(other.get("reply"))
                            or fallback.draft.hands_over_words(other.get("reply"))
                            or fallback.draft.hands_over_the_shape(other.get("reply"))
                            for other in candidates if other is not candidate)):
            return index
        return None
    return None


def _the_words_for_the_child(candidates, clean, memory, last=""):
    """The index of the composer's words for a child, after a condolence.

    `_the_ask_about_a_child` above is the same ask in one line with the death, and it hands the
    turn to the entry. A turn later there is no death in the line at all - just "how do i tell a
    4 year old" - so the entry reads it as a general how-to and the card on screen time takes it,
    or the condolence's own drafter answers with a message for the bereaved. The composer reads
    the thread (`childwords.asks_the_words_for_a_child`) and has the words; this is only the
    routing decision, and it stands aside the moment that reading says no.
    """
    from ..compose import childwords
    try:
        if not clean or not childwords.asks_the_words_for_a_child(clean, memory):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    for index, candidate in enumerate(candidates):
        if candidate.get("module") != fallback.FALLBACK_MODULE:
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == last):
            continue
        if reply in _the_words_for_a_child_pool():
            return index
    return None


def _the_words_for_a_child_pool():
    """The composer's pool for a child's words, reduced the way the candidates are.

    `_content` drops punctuation and case, so a pool line has to be reduced the same way before
    the two can be compared (the em dash alone makes them unequal).
    """
    from ..compose import childwords
    return tuple(_content(line) for line in childwords.THE_WORDS_FOR_A_CHILD)


def _the_ask_about_a_child(candidates, clean, last=""):
    """The index of the knowledge entry that answers "how do I tell the child", else None.

    The person is not asking what to say to themselves about a death; they are asking for the
    words for a child, and the entry that has them (`explaining-death-to-a-child`) is the only
    reply that answers the question. `loss` answers bad news well and declares `ANSWERS_INSTEAD`,
    so without this the ask got advice for talking to a grown-up ("use the person's name, don't
    rush to fill the silence") on the lines the entry now reads: a niece, a grandson, "my girls".
    Read before that declaration, because the question is not the loss.

    Strict, and only on the lines the composer read whole: the reading says no to a death named
    as today and to the child who is the one who died, so a bereaved parent keeps the condolence.
    """
    try:
        if not fallback.asks_what_to_tell_a_child(clean):
            return None
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    for index, candidate in enumerate(candidates):
        if candidate.get("module") != "answers" or _priority(candidate) < 0:
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == last):
            continue
        return index
    return None


def _about_the_person_the_line_names(candidates, pool, clean, last=""):
    """The index of a reply about the person a how-to line names, when the front one is not.

    The card in front answers the speaker's own life; the entry below it answers the question
    about the other person. Read only on a how-to line that names someone ("how do i stop my
    teenager staying up all night"), so a line about the speaker is untouched. The person the
    how-to is about is the first person the line names, so "how do i console a friend whos just
    lost their dad" is about the friend and their grief, not a cue to answer about a dad. And a
    reply that says it cannot answer is never taken over the card in front, which can.
    """
    if not clean or not _A_HOW_TO.match(clean):
        return None
    named = _THE_ONE_NAMED.search(clean)
    if named is None:
        return None
    first = _A_PERSON_NAMED.search(clean)
    if first is None or first.start() != named.start():
        # the line names somebody else first ("how do i console a friend who lost their dad")
        return None
    word = named.group(0).split()[-1].lower()
    if _priority(candidates[pool[0]]) >= RECALL:
        return None  # the recall band and the safety band are answered as they come
    front = _content(candidates[pool[0]].get("reply"))
    if not front:
        return None
    if re.search(r"\b%ss?\b" % re.escape(word.rstrip("s")), front, re.I) or \
            _ABOUT_SOMEONE_ELSE.search(front):
        return None  # the reply in front already says something about them
    for index in pool[1:]:
        candidate = candidates[index]
        if _priority(candidate) >= RECALL or candidate.get("module") != "answers":
            continue
        reply = _content(candidate.get("reply"))
        if not reply or (last and reply == last):
            continue
        if fallback.is_a_hedge(reply):
            continue  # "I don't know enough to answer that" is not an improvement on the card
        if re.search(r"\b%ss?\b" % re.escape(word.rstrip("s")), reply, re.I) or \
                _ABOUT_SOMEONE_ELSE.search(reply):
            return index
    return None


def _story_goes_on_reply(text, memory, candidates, last=""):
    """The index of the composer's listening line for the next line of a hard story, or None.

    The reading lives in bot/memory/ack.py (`carries_the_story_on`: bad news in the last two
    turns, and this line about someone else doing something) and the wording next to it, so this
    is only the routing decision - the same shape as `_sudden_loss_reply` above, for the turn
    after bad news rather than the bad news itself.

    The one thread the listening reply does not keep is a thread that began with news that has a
    name in it: a condition on somebody they love, a court letter, an award stopped, the roof going
    (`badnews.NEWS_WITH_A_NAME`). Those lines are answered gently and then the person asks about
    the thing itself - "my dad has parkinsons" then "he keeps falling" is the falls card's turn,
    and "she keeps asking for her mum" after a diagnosis is the question the dementia answer is
    for. The listening line is for the thread a death, a break-up or a refusal began, where the
    next line is more of the same story - `_a_story_opened` reads the two, and `_a_refusal` keeps
    "she wont eat" after a diagnosis with the listening line rather than the feeding card.
    """
    if _ack is None:
        return None
    try:
        if not _ack.carries_the_story_on(text, memory):
            return None
        if (not _a_story_opened(memory) and not _a_refusal(text)
                and any(_priority(candidate) >= 0 for candidate in candidates)):
            # Named news - a condition on somebody, a stay in hospital - is news the next line
            # asks a question about ("my mum has cancer" / "she keeps falling" is the falls card),
            # so the module that answered it keeps the turn. After a death there is nothing to
            # answer and the listening line holds: "my nan died last week" / "he took the car" is
            # the story going on, and the motorway advice under it read as a shrug.
            return None
        pools = (_ack.THE_STORY_GOES_ON,)
        for index, candidate in enumerate(candidates):
            if int(candidate.get("priority") or 0) >= SAFETY:
                continue  # a real emergency is never passed over for a listening line
            reply = str(candidate.get("reply") or "").strip()
            if not reply or (last and _content(reply) == last):
                continue
            if any(reply in wanted for wanted in pools):
                return index
    except Exception:  # noqa: BLE001 - a reading that fails just adds no rule
        return None
    return None


def _echoes(reply, last, announced=False):
    """True when a reply is only words the bot said in its last answer.

    Two shapes. The first is the last answer said again with a nod in front: a bare follow-up
    ("why is that", "what should i do") is answered "Same as before: <the opening of the last
    answer>", which is not a second answer, because the person read those words a turn ago and is
    asking about them. The never-repeat rule compared whole replies, so a reply with three words
    in front of the last one read as a fresh candidate.

    The second is a slice of the answer with nothing in front of it: after "my washing machines
    making a bang on the spin", "is it worth fixing or shall i just get a new one" got the
    sentence about the transport bolts, which is the branch of that answer the person had not read
    - words already on the screen, dressed as a reply to a question they never answered.

    The shape stays narrow on purpose, so nothing that adds anything can be taken for a repeat: at
    most six words of lead-in, then twelve words or more of the last answer word for word, in one
    run to the end of the reply. Anything the candidate says of its own after the run is new, and
    a reply shorter than twelve words is a sentence a friend might choose to say again.
    """
    words = _content(reply).split()
    previous = _content(last).split()
    if len(previous) < 12 or len(words) < 12:
        return False
    for lead in range(0, min(6, len(words) - 12) + 1):
        run = words[lead:]
        if len(run) >= 12 and _a_run_of(previous, run):
            return True
    # A lead that names itself as a repeat is longer than the six words allowed above, so it is
    # read only where the never-repeat rule must decide a claim, and only when asked for: "Same as
    # before: <the whole answer>" would otherwise count as a repeat in `_choose`, where the answer
    # said again is the only thing on the table and the fallback's question ("tell me what it is
    # for") would take the turn off it - "what do i bring" after the meeting-the-parents answer
    # lost "Take something small for the house" that way in a blind sample.
    if announced:
        handed = _the_quoted_repeat(reply)
        if handed:
            run = handed.split()
            if len(run) >= 8 and _a_run_of(previous, run):
                return True
    return False


# A claim that reads the answer back is not a claim: how much of the last answer has to come
# first, and how much the reply may add after it, to say the reply is the answer again with a
# comment on the end rather than a second answer.
AGAIN_FIRST_WORDS = 16


AGAIN_TAIL_WORDS = 12


def _the_answer_again_with_a_tail(reply, last):
    """True when the reply opens on the last answer and then adds a short remark of its own.

    `_echoes` reads two shapes of repeat, and both of them end in the answer: a lead and then the
    answer, or a slice of it with nothing after. This is the third shape, and the one a claim uses
    to keep a line it should have given up: the whole answer, word for word from its first word,
    and then a sentence of its own on the end.

    "im knackered all the time" / "i only get about five hours sleep" is the case. The memory
    store answers as it comes, and what it handed back was the tiredness answer from the top -
    every word of it - with "Five hours is more than enough for all of that" added. The
    knowledge entry beside it had the answer the line asked for ("Five hours is on the short side:
    most adults need seven to nine"), and the store's tail was not only a repeat, it was the
    opposite of what the card says. The tail is new, so `_echoes` leaves the whole reply alone;
    this reading says the reply is the answer again, and settling a claim on it hands the person
    the paragraph they read a turn ago.

    Narrow on purpose: the answer has to be sixteen words or more, the reply has to open on it
    from the first word, and what comes after may be no more than twelve. A store that quotes a
    line and adds the one thing that matters most is doing its job, so that is not this shape.
    """
    words = _content(reply).split()
    previous = _content(last).split()
    if len(previous) < AGAIN_FIRST_WORDS:
        return False
    same = 0
    while same < len(words) and same < len(previous) and words[same] == previous[same]:
        same += 1
    return same >= AGAIN_FIRST_WORDS and len(words) - same <= AGAIN_TAIL_WORDS


def _the_quoted_repeat(reply):
    """The part of the last answer a lead says it is handing back, or None.

    A lead that names itself as a repeat ("It's what I said a moment ago: ...", "Same answer:
    ...") is longer than the six words `_echoes` allows in front of a quote, so a reply wearing
    one was read as a new answer when it was the paragraph again. The lead has to be one the
    other lanes write themselves (`_repeat_leads`, the same list `_announces_a_repeat` reads),
    and the words after it have to be the answer's, because a lead that says it is handing on the
    *next* part of the answer ("There was a second bit to that answer: ...") is the answer the
    person has not read yet and must not be taken for a repeat.

    Not called `_announces_a_repeat`: that is the rule that settles a turn where every candidate
    is the answer over again, and it answers yes or no. A second function of that name read every
    reply as the quiet one and turned "what do i bring" from the answer in hand into a question.
    """
    text = _content(reply)
    if not text:
        return None
    heads = [_content(lead) for lead in _repeat_leads()]
    # The memory lane's own leads are the long ones ("It's what I said a moment ago: {said}",
    # "From just now: {said}"), which is why this reading exists at all.
    try:
        heads.extend(_content(str(frame).split("{")[0]) for frame in getattr(_repeat, "LEADS", ()))
    except Exception:  # noqa: BLE001 - a lane that cannot be read adds no lead
        pass
    for head in heads:
        if head and text.startswith(head):
            return text[len(head):].strip()
    return None


# A reply that answers by pointing at the answer already on the screen, rather than saying
# anything: the knowledge entry found the follow-up again and came back with a short form of the
# answer it just gave, so the turn says where the answer is instead of reading it out a second
# time (bot/modules/answers.py, SAID_ABOVE and NOTHING_SEPARATE). The words are new, and that is
# the whole trouble: the never-repeat rule compares wording, so a line that adds nothing at all
# read as the one fresh candidate on the table and took the turn off a real answer.
A_POINTS_BACK = re.compile(
    r"\bis in what I said above\b|\bis in the answer above\b|\bis covered by the answer above\b"
    r"|\bwhat I said above is the whole of it\b|\bthan what I said above\b"
    r"|\bis the whole of what I have on it\b"
    r"|\bnothing separate on\b|\bnothing more on\b|\bno separate answer for\b",
    re.IGNORECASE)


def _points_back(reply):
    """True when the reply only says the answer above covers the thing, adding nothing."""
    return bool(A_POINTS_BACK.search(str(reply or "")))


def _a_run_of(previous, run):
    """True when `run` is a continuous run of words inside `previous`, the last reply."""
    size = len(run)
    return any(previous[start:start + size] == run
               for start in range(0, len(previous) - size + 1))
