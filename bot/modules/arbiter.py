"""Chooses each turn's reply among the modules' candidates. The routing lane owns this file.

The seed rule stays the floor: candidates arrive highest PRIORITY first, and a fallback
(PRIORITY below 0) answers only when nothing else does. Two general rules on top of it
(README.md, "Routing"; STYLE.md):

* the specialist beats the generalist: a module that declares `ANSWERS` (the topics it is
  good at, e.g. `ANSWERS = ("cooking", "food")`) is preferred when this line was read as
  being about one of them, and the candidate in front of it is not about them. A reply about
  the topic asked beats a fluent one about something else. Two specialists go to the one that
  matches the line better (more of its topics, a topic id before a single word), and only
  then to PRIORITY. The understanding engine's topic ids (memory["understood"]["topics"] and
  ["topic"]) are the strong signal; the line's own words are the weaker one, so a module still
  works while a topic reader is missing. A follow-up ("and how long?") has no topic of its
  own, so the line the conversation is on (memory["topic"]) is read with the same reader and
  stands in for it.
* a line about the conversation is the recall band's: a line that names no topic of its own
  ("what am i doing this week" after "im writing up my thesis") was read as a topic only by
  inheritance, and the memory store's answer to it ("You're writing up your thesis.") is the
  answer to what was asked, while a topic entry that fits only by inheritance answers a question
  nobody asked. So the specialist rule does not lift a module over a PRIORITY 7000 candidate on
  a line whose own reading names no topic; the line's own phrase or word can still lift it (see
  `_fit`).
* never say the same thing twice in a row: a candidate whose reply only repeats the bot's
  last turn is passed over while another candidate says something different. Nor a whole answer
  said to this person earlier in the conversation: a reply that is word for word something the
  bot already said, several turns back, is passed over while another real candidate has something
  new. The same question asked twice in a row is the case for the repeat, and there every real
  candidate is that answer again, so nothing is dropped.
* an emergency stays an emergency: for a line that is still inside a safety thread, the
  composer's careful continuation beats a light module that would answer it as ordinary talk.
* a sudden loss is answered as a loss: a pregnancy that has ended or someone who took their own
  life gets the composer's own line for it, even when a module below has a general "sorry to
  hear it" for bad news ("we lost the baby" was answered "give it a day, then look at what you
  can control", which is advice for a setback).
* a bare "where do i start" gets the step out of the answer in hand: a line that names nothing and
  asks for the next move is answered by the shortest candidate built from the answer's own words,
  even when a topic entry answers the same line by reading the whole answer out again in its other
  wording (see `_the_move_in_hand`).
* a module can say that one of its proposals is to be answered as it comes, without raising its
  PRIORITY: it declares `TAKES_AS_IT_COMES(text, memory)` and the arbiter asks it on the line
  the proposal is for (see `_as_it_comes`). A band says "everything this module proposes"; a
  hook says "this line, because I read it whole", which is what a module needs when only part
  of what it proposes deserves the turn.
* a reply does not offer the food the line refused: "im trying to eat better but i hate veg" was
  answered by the balanced-meal card ("Half the plate vegetables..."), the one thing the person
  had just ruled out. The kitchen already reads the refusal, so a candidate whose first sentence
  offers that food is passed over while one that respects it is on the table. The safety band is
  never passed over, and neither is a reply that names the food to leave it out ("No onion then:
  ...", "nut-free"), which is still the answer to the refusal.

* a rule-out keeps the turn when the answer beside it offers back what was ruled out: "what
  should i cook tonight" / "not curry, something else" was answered "Quick: chickpea curry in 25,
  or a sweet potato curry" - the thing refused, twice - while the rule-out's own line ("That one
  never mentions curry at all, so nothing changes. ...") was in the list under the floor. A reply
  that hands back what the person has just ruled out has not read the line, so it is not an answer
  a claim gives way to, by PRIORITY or to a declaring specialist (see `_every_real_answer_offers`).

A candidate at PRIORITY >= 9000 (the safety band) is never passed over this way: a real
emergency is answered by the module that recognised it. Anything unexpected falls back to the
seed rule, so a turn is never lost and the arbiter never crashes a reply.

The implementation lives in the `arbiter_part_NN` parts (in bot/module_parts); this module keeps the header
imports and re-exports every name the parts bind, so `arbiter.<name>` is what it was.
"""
import importlib
import re

from ..compose import aboutness, badnews, facts, fallback, fit, leaving, onscreen
from ..compose import outlook as _outlook
from ..compose import limit as _limit
from ..memory import narrow as _narrow
from ..compose.goodnews import reads_as_a_detail_of_the_news, reads_as_the_detail_line

from ..module_parts.arbiter_part_01 import (  # noqa: F401
    _ack, _recall, _repeat, _loss, _dream, _already, _harm, _there_is_a_chat, _lineback, _naming,
    THREAD, CARE_THREAD, PAUSE, _STEP_WHEN_LOW, _cooking, _ruledout, _history, _reading,
    DECLARED_TOPICS, CHOICE, DECLARED_INSTEAD, DECLARED_DEFERS, DECLARED_AS_IT_COMES,
    DECLARED_CLAIMS_INSTEAD, DECLARED_ABOUT_THE_CHAT, OWN_ABOUT_THE_CHAT, SAFETY, CHATTER, RECALL,
    MOVE_WORDS, MOVE_SHARE, MOVE_WHOLE, MOVE_ANSWER_WORDS, WHOLE_LINE_BAND, WORD, LABEL_KEYS, READ,
    _a_past_that_is_not_there, _SAID_BEFORE_WORDS, MEMORY_MODULES, _a_recall_from_an_earlier_turn,
    _the_kind_line_they_gave, _seed, _priority, _REFUSAL_UNDONE, _ALLERGY_LIFTED,
    _the_food_the_line_refused, _offers_the_food, _offers_what_the_line_ruled_out,
    _the_thing_the_line_ruled_out, _every_real_answer_offers, A_CEILING, GENERIC,
    _the_cut_the_line_asked_for, A_FIGURE, A_WORKED_OUT, A_SUM_TO_WORK_OUT, _the_figures_they_gave,
    _says_back_one_of, _AN_AMENDMENT, _MONTHS, _amends_a_detail,
    _the_candidates_that_hand_the_detail_back, _asks_it_back, DOING_WANTS,
    _the_line_asks_for_a_doing, SAID_BACK, _says_what_they_already_said, _NUMBER_WORDS, _FIGURES,
    _the_numbers_in, _explains_the_method, _the_figure_they_asked_back, A_MY_OWN_REPORT,
    A_REPORT_ASKS, A_DEFINITION, A_REPORT_NOD, A_CONTENT_WORD, REPORT_STOP,
    _the_words_the_report_names, _a_report_and_no_ask, _is_advice_about, _how_much_it_names,
    _the_advice_over_a_definition, LONG_ENOUGH, _places_the_figure, LETTERS, _says_only_the_line,
    FIRST_VERB, CARRIES_NO_SUBJECT, _the_same_plain_word, INFLECTED_ENDS, DOUBT_WORDS,
    _reads_the_doubt, POINTS_BACK, REPEAT_FRAME, _FRAME, THE_ANSWER_BANDS,
    _an_answer_behind_the_ask, _asks_for_the_answer_again, _the_repeat_frame,
    _the_store_reads_a_repeat, _the_store_reads_an_explain_again_ask,
)
from ..module_parts.arbiter_part_02 import (  # noqa: F401
    _a_bare_doubt_reply, _about_the_line, _names_the_thing, _a_repeat_to_hold,
    _a_shorter_said_again, _asks_a_question, _asks_for_a_judgement, _hands_the_decision_back,
    POOL_MODULES, THE_ASK_OPENS, ECHO_STOP, THEIR_VOICE, _the_ask_after_the_facts, A_SUBJECT_WORD,
    A_SUBJECT_PHRASE, WORD_ENDINGS, _one_word, A_MEASURE_ASKED, _names_a_figure, NOT_A_SUBJECT,
    _a_question_about_the_bot, _declares_claims_instead, _declares_as_it_comes,
    _asks_about_the_chat, WHOLE_MOVE_WORDS, CUT_MARKS, TOKEN, _the_line_is_news,
    _announces_a_repeat, _repeat_leads, _carries_on, _run_in_the_answer, THE_CAUSE, _PEOPLE,
    _CONDOLENCE, _THE_NAMELESS, _my_workings, _reads_as_a_verdict, _in_a_careful_thread,
    KEEPS_ITS_OWN_ANSWER, ANSWERS_THE_NEWS, A_VERDICT_BACK, NOT_A_SUBJECT_WORD, _subject_words,
    _about_the_news, _says_the_same_thing_again, _the_subject_was_answered, ASK_CLAUSE_SPLIT,
    ASKS_FOR_A_THING, _the_ask_clause, _defers_to, _asks, _a_sign_off, _a_leaving_said_plain,
    _sudden_loss_reply, _a_whole_line_module_spoke, _A_HOW_TO, _THE_ONE_NAMED, _A_PERSON_NAMED,
    _ABOUT_SOMEONE_ELSE, _the_name_they_gave, _a_knowledge_entry_has_it, _hurting_reply,
    _a_story_opened, REFUSAL, _a_refusal, _is_loss_reply_in, _composer_reading, _carries_the_answer,
    _a_check_on_the_answer, _opens_on_a_job, _is_a_generic_step, CHITCHAT, _answers_this_line,
    _content,
)
from ..module_parts.arbiter_part_03 import (  # noqa: F401
    _the_card_that_places_the_figure, _said_it_already, ACK_POOL, _ack_lines,
    _the_reply_is_the_report, _real_answers_besides, _only_says_the_line_back,
    _the_candidates_that_answer_the_ask, _a_card_besides, _a_real_answer_besides,
    _only_a_hand_back_besides, _names_what_they_said, _claims_instead, _the_move_in_hand,
    _made_of_the_answer, _a_condolence, _says_the_subject, _the_cause_asked_for, _the_date_fact,
    _the_next_part, _a_lead_line, _verdict_lines, _the_verdict_turn, _pause_reply,
    _the_store_revises_the_answer, _a_clause_was_cut_in_half, _store_correcting, _draft_index,
    _the_words_for_the_child, _the_words_for_a_child_pool, _the_ask_about_a_child,
    _about_the_person_the_line_names, _story_goes_on_reply, _echoes, AGAIN_FIRST_WORDS,
    AGAIN_TAIL_WORDS, _the_answer_again_with_a_tail, _the_quoted_repeat, A_POINTS_BACK,
    _points_back, _a_run_of,
)
from ..module_parts.arbiter_part_04 import (  # noqa: F401
    _an_answer_it_already_gave, _names_the_answers_figure, _names_the_subject, _a_bare_yes_no,
    _carried_words, _fit, _line_topics, _a_choice_the_answer_did_not_make, _the_answer_handed_back,
    _a_declaring_specialist_besides, _a_fresh_answer_besides, _the_whole_move, _only_acknowledges,
    _a_presence_check, _about_the_bot, _the_venue_hours_turn, _the_bots_own_taste, _declares_topics,
    _the_verdict_back, _verdict_reply, _instead, _the_entry_that_answers_the_ask, _defers,
    _declares_instead, _declared, _named_topics, _thread_index, _the_answer_written_out,
    _last_reply, _said_before, _about, _strings, _label, _labels, _stored, _read_topic, _answered,
    _match,
)
from ..module_parts.arbiter_part_05 import (  # noqa: F401
    _the_candidates_with_a_figure, _the_candidates_that_give_the_shape, _the_same_word, _choose,
    _as_it_comes, _leaving_reply, _the_subject_words, _the_lines_own_words, _the_forms_of,
    _names_a_word_of, _a_card_names_the_line, _a_detail_added_to_the_news, _shares_a_stem,
    NOT_A_NEW_WORD, _the_word_the_line_added, _says_nothing_new, _names_the_word,
    _the_answer_that_names_what_the_line_added, _a_card_that_names_the_line, A_PLAINER_ASK,
    PLAIN_ASK_FILLER, _a_line_asking_for_plainer_words, _says_the_answer_again,
    _a_plainer_reading_of_the_same_answer,
)
from ..module_parts.arbiter_part_06 import (  # noqa: F401
    choose,
)
