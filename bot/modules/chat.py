"""Small talk: greetings, thanks, short replies, goodbyes and simple feelings.

Reads the line the way a friend would. A short reply ("ok", "lol", "nah") answers the bot's
last turn, so it is read in that light and answered in kind. A feeling ("I'm knackered",
"long day") gets a warm, concrete line back — never a therapist's question. Everything else is
left to the modules that know about it: this one passes unless the whole line is small talk.

The implementation lives in the `chat_part_NN` parts (in bot/chat_parts); this module keeps the header
imports and re-exports every name the parts bind, so `chat.<name>` is what it was.
"""
import copy
import re

from ..compose import (LINGERED_LINE, badnews, circumstance, doubted, fallback, greet_with,
                       nearly, negated, pick, says_it_has_lingered, step_when_low)
from ..compose import leaving as leaving_reading
from ..compose import limit as limit_line
from ..compose.badnews import reads_as_bad_news, reads_like_a_symptom
from ..compose.goodnews import (a_detail_of_the_news, asks_for_news,
                                MORE_OF_THE_NEWS, MORE_OF_THE_NEWS_ARRIVAL,
                                MORE_OF_THE_NEWS_SCORE, reads_as_a_pass,
                                reads_as_a_win_nobody_noticed,
                                reads_as_a_prize_in_a_message, reads_as_good_news,
                                reply_for_a_win_from_a_past_year)
from ..memory import hope, matters, obstacle, plan as plan_steps
from ..memory.when import asks_what_today_is
from ..memory import size as another_size
from ..memory.cause import NO_REASON as _NO_REASON
from ..knowledge.lookup import the_body_is_short_of_sleep
from ..understanding import breeds, topics
from ..understanding.kinds import (ADDRESSED, EMOTION_WORDS, THANKS_NOISE,
                                   ANSWERING_A_QUOTED_ASK, cue_about_person,
                                   the_manners_question, verdicts_a_thing, shortage_of)
from ..compose import loss as loss_reading
from ..compose import onscreen
from ..compose import unseen as unseen_reading
from ..compose import harm as harm_reading
from ..compose import saidby as saidby_reading
from ..compose import reaction as answer_reaction
from ..compose import repair
from ..compose import said_about_me
from ..compose.repair import (DEEDS_WITH_A_CARD, amends_to, deed_of, owns_the_deed,
                              with_the_feeling_named)
from ..compose import reading as reading_reply
from ..compose import urgent as urgent_reading
from ..compose import stepwords
from ..compose import verdict as verdict_reply
from ..compose import doubt as doubt_reply
from ..compose import occasionplan
from ..memory import PERSON_TROUBLE as SOMEONE_TROUBLE
from ..memory import WHO_SAID, about, about as about_the_person, current, person, person_named, trouble, user, you

from ..memory import ack, current, last_user as _last_said, user, you
from ..memory import remedy
from ..memory import stuck as stuck_line
from ..memory import thread
from ..memory.facts import JUDGEMENT_AFTER, JUDGEMENT_NOUNS
from ..memory.topics import in_a_safety_thread as _safety_thread
from ..memory.topics import names_nothing
from ..memory.topics import keywords as _content_words

from ..memory import again as _same_again  # the answer under a repeat's lead-in
from ..memory import carried_on as step_after
from ..memory import passing_the_time
from ..memory import the_years
from ..memory import warmth as talked_to
from ..memory import limits, portions
from ..memory import facts, hours as hours_after, limit, meant, pile, repeat, tried, more, returned
from ..memory import topics as topic_memory
from ..memory.ack import A_MOVE, a_person_getting_better, nobody_around
from ..knowledge import lookup
from ..knowledge import travel as travel_kb
from ..understanding import lexicon
from ..understanding import understand as understanding
from ..understanding.topics import PLACES as KNOWN_PLACES

from ..chat_parts.chat_part_01 import (  # noqa: F401
    PRIORITY, ANSWERS, TOKEN, GREET_CORE, GREET_FILLER, THANKS_CORE, THANKS_LOOSE, HELP_ONLY,
    THANKS_FILLER, ACK_WORDS, LAUGH_WORDS, LAUGHTER, SAYS_TOO_MUCH, NO_WORDS, NO_REFUSAL_CONTENT,
    NOT_A_REFUSAL, _only_a_refusal, A_MOOD_SAID_PLAINLY, A_VERDICT_WORD, A_VERDICT_WITH_A_ROLE,
    NOT_A_BARE_VERDICT, A_VERDICT_SAID_ALONE, A_VERDICT_ON_ITS_OWN, OWN_WORTH, OWN_TRAIT,
    SOCIAL_TRAIT_SETTING, EVERYTHING_WRONG, OWN_HARSH, LET_SOMEONE_DOWN, KEEPS_FAILING,
    NOT_THE_PERSONS_OWN, SELF_SUBJECT, _keeps_failing_theirs, _letting_someone_down,
    ROLE_YOU_CAN_FAIL, NOT_FAIR, NOT_GREAT, ASKS_A_QUESTION, SELF_WORDS, _about_themselves,
    FIRST_COPULA, LEAD_IN_JUDGEMENT, NOT_FAIR_WORDS, OTHER_SUBJECT, _themselves_unfair,
    REACTION_WORDS, REACTION_WHAT_A, REACTION_LEAD, REACTION_TAIL, REACTION_SUBJECT,
    REACTION_COPULA, REACTION_HOW, REACTION_SIGH, REACTION_SIGH_WORD, REACTION_BARE_GOOD,
    REACTION_BARE_FUNNY, _a_thread_to_come_back_to, _news_before, _nobody_would_call_it_nice,
    REACTION_CHEERFUL, AGREEMENT_ONLY, GRUMBLE, WEATHER, _the_agreement_pool, GOOD_NEWS_TURN,
    OWN_WIN, OWN_SETBACK, _turns_on_news, ASKED_AFTER, _asks_after, JUDGEMENT_TIME, SELF_COPULA,
    _when_not_why, HARSH_WORDS, _judged_a_role, DONT_KNOW_WORDS, BYE_CORE, BYE_FILLER, BYE_TIME,
    BYE_VERB, SMILES, JOKE_ASK, JOKE_ASKED, RUNTIME_LIMIT, JOKE_ADVICE, PICK_WORDS, WANTS_A_THING,
    ASKS_ALOUD, JOKES, SHORT_JOKES, ROLE_STOP, COMPARED_ROLE, ROLE_TO_PEOPLE, ROLE, ROLE_WORK,
    NOT_A_ROLE_AFTER_ARTICLE, AGE_BEFORE_A_ROLE, PLAIN_TAIL, OUT_OF_WORK, RETIRED, RETIRED_ASKING,
    PLACE, PLACE_TAIL, PLACE_MOST, PLACE_LAST, PLACE_IDIOM, PLACE_SPAN, PLACE_NONE, PLACE_POINTS,
    GROWN_IN, PLACE_POSITION,
)
from ..chat_parts.chat_part_02 import (  # noqa: F401
    PLACE_NOBODY, AWAY_WORDS, MOVING, PLACE_THING_OPENS, PLACE_TIME, PLACE_TIME_OPENS, TRIP,
    PET_ANIMALS, PET, PET_ANY, GOOD_NEWS, LOST_JOB, _a_job_that_went, JOB_STEP_ASK,
    _the_ask_after_a_job_that_went, LOST_WEIGHT, BAD_NEWS, TIME_COUNT, WHEN_DONE, WITH_COMPANY,
    WENT_TO, WENT_TO_COMPANY, WENT_TO_SEE, WENT_TO_SEE_COMPANY, WATCHED_THINGS, WATCHED_DESCRIBER,
    SAID_POOR, NOT_A_NIGHT_OUT, _not_a_night_out, NOT_A_PLACE_START, WENT_WRONG, WENT_WELL,
    POOR_THING, _poor_word, VERDICT_WELL, VERDICT_POOR, WENT_BAD_WEATHER, STATUS, JUST_DONE,
    JUST_STARTED, CAME_BACK, BACK_FROM, BEEN_TO, WENT_TO_ANY, TRIP_NOT_YET, SOME_WHEN,
    TRIP_TIME_TAIL, TRIP_SHORT_COUNTRIES, PRESENCE, PAUSE, _LOST_TAIL, LOST_ONLY, _AT_IT_TAIL,
    AT_IT, _HOW_LONG_AT_IT, _A_FORM, _A_THING_TO_MAKE, STUCK_FEELING, _STUCK_ON, _STUCK_TAIL,
    STUCK_ON_A_FORM, STUCK_ON_A_THING, RETURNED, BID, LEAVING, HOME_AGAIN, UNDERWAY, IN_BED,
    AWAKE_SINCE, ERRAND, WISH_LUCK, NEWS_REPLIES,
)
from ..chat_parts.chat_part_03 import (  # noqa: F401
    _asked_about_the_effort, _as_a_pattern, HANDS_IT_BACK, hands_it_back, POSITIVE, FEELINGS,
    FLAT_IDIOM, NOT_LANDED, GOOD_NEWS_SAID, ANY_WORLD_NEWS_ON, NOT_GLAD_WORDS, ANNOUNCED_ONE,
    NEWS_AFTER, ASKED_ABOUT_THE_BOT, SELF_INSULT, MOOD_FOR, NOT_MYSELF, THING_WORDS,
    _a_thing_in_front, SPENT_MONEY, LOW_THING, TIRED_PERSISTENT, TIRED_DESPITE_SLEEP, SLEEP_WORD,
    ACT_GERUND, IRREGULAR_DEED, DEED_TAIL, GUILT_WORD, GUILT_DEED, REGRET_DEED, SICK_DEED,
    BODY_FEELING_SHAPE, BODY_PART_FEELING, BODY_AT_THOUGHT, BODY_BEFORE_AN_EVENT, THOUGHT_UNNAMED,
    SYMPTOM_IN_LINE, ASKS_IF_NORMAL, BUG_NAMED, BODY_FEELING_WORDS, _line_as_read, _a_limit, _SAY,
    _THING, _TAIL, _HOW_I_READ_IT, _A_LIFE, _A_LOOSE_VERDICT, _THEIR_OWN_LIFE, _NOT_A_VERDICT_YET,
    _their_own_call, AVOIDED_FEELING, _without_the_feeling_avoided, FEELING_LEAD, FEELING_SELF,
    NOT_WORDS, NOT_FILLERS, _negated, CORRECTION_MARKERS, _denies_an_earlier_word, NOT_HAPPY_ABOUT,
    INTENSIFIERS, INTENSIFIER_PAIRS, DETERMINERS, STATE_NOUNS, OWN_STATES, COPULA, FUNCTION_WORDS,
    STILL_ON_THEM, FOND_OF_ME, NOT_FOND, FOND_REPLIES, _fond_of_the_bot, MISS_ME, MISS_YOU_REPLIES,
    KIND_TO_ME, PRAISED_ANSWER, BARE_PRAISE, DOUBT_FRAME, BEFORE_PRAISE, THANKS_AFTER,
    _praised_the_answer, KIND_REPLIES, ILL_SELF, COLD_NAMED, COMPLAINT_ONLY, COLD_SORE,
    COLD_SORE_FEELING, COLD_SYMPTOM, SAME_COLD,
)
from ..chat_parts.chat_part_04 import (  # noqa: F401
    _the_kind_of_worry, NO_NOSE_WORDS, _the_same_cold_again, ABILITY_WORDS, ROUGH_DAY, WHAT_A_DAY,
    A_STRETCH, A_STRETCH_THAT_DRAGS, _a_stretch_that_drags, VENTED, WORRY_FEELING, WORRY_EVENT,
    WORRY_PERSON, WORRY_ABOUT_THING, WORRY_WHEN, CANT, NOT_THE_SUBJECT, INABILITY, CANT_OPENING,
    SPAN_TAIL, ITS_BEEN, LONG_SPAN, STUCK, STUCK_SAFETY, NEG, STUCK_IDIOM, STUCK_OBJECT, STUCK_SELF,
    STUCK_DOES_SOMETHING, STUCK_A_DEGREE_OR_A_TIME, STUCK_AN_OBJECT, _doing_something_to_a_thing,
    STUCK_REASON, STUCK_FIXABLE, STUCK_LOSS, said_loss, REPLIES, OPINIONS, CONTEXT_CHAT, _BOT_DAY,
    _EVENING, PLANS_ASK, PLANS_REPLIES, PLANS_FILLER, _asks_about_plans, BOT_ABOUT,
    BOT_NOT_A_FEELING, BOT_FEELING_WORDS, BOT_FREQUENCY, BOT_HOW_MUCH_OR_WHEN, BOT_FEELING_ASK,
    FEELING_NAMES, BOT_MOOD_ASK, _a_feeling_named, BOT_FEELING_REPLIES, BOT_FEELING_NAMED,
    BOT_FEELING_NAME_OF, _a_feeling_about_me, SELF_ABOUT, SELF_AFTER, BOT_LIFE, BOT_LIFE_AREA,
    _about_bot_life, _as_meant,
)
from ..chat_parts.chat_part_05 import (  # noqa: F401
    BOT_DOINGS, BOT_WHEREABOUTS, BOT_DOINGS_AHEAD, AHEAD_TIME, BEHIND_TIME, BOT_NEVER,
    BOT_DOINGS_BARE, BEEN_UP_TO_SPAN, _a_shape_no_list_knows, _doings_pool, _a_sign_off_with_a_time,
    _about_bot_doings, _about_bot, WHAT_ARE_YOU_CAN_DO, _self_only, _opinion, _context_follow_up,
    A_LABEL_ON_THE_PERSON, AE, BUSY_RE, BUSY_WORK, LOAD_THING, LOAD_WORD, LOAD_TOOK_ON, OVERLOAD,
    LOAD_ASK, LOAD_TURNED, LOAD_SOMEONE_ELSE, LOAD_FEELS, PLAN_RE, PLAN_STOP, PLAN_TROUBLE,
    PLAN_WORRY, SORRY_TALK, SAY_SOMETHING, ASK_WHETHER_TO_SPEAK, GO_AWAY, VAGUE_WORDS, SOFTEN,
    INTENT_RE, NEXT_REST, NEXT_ACT, NEXT_UP, MY_NIGHT, NOT_MY_NIGHT, NEED_FOR, NEED_RE,
    QUESTION_STARTERS, DOUBT, INTENT_CONDITION, EVENT_RE, INTENT_STOP, WANTED, FEELING_WANT,
    FEELING_THING, LEAVE_SOMEONE, STOPS_TOGETHER, SAYS_NOTHING, EVENT_OUTING, EVENT_TIRED,
    EVENT_STATE, _a_trip, _answers_it, _as_typed, _ON_THE_JOB, _THE_RUN_OF_IT, _a_detail_on_the_job,
    A_RATE_OF_MONEY, A_JUDGEMENT_ON_A_FIGURE, _overloaded, JUDGED, _CONSIDERING, _CONSIDERING_TO,
    _judged, _STATEMENT, _BARE_DOING, _judged_thing, AGAIN_ONLY, NOT_AGAIN, HOW_TO_ASKED,
    THE_STEPS_AGAIN, LOOKING_FORWARD, _the_steps_again, _a_care_turn, _a_forecast, FEELING_POOLS,
    FEELING_SAID, _tokens, _name, _the_lost_thread_asked, AHEAD, NEEDS_AHEAD, NOT_PROUD,
    PROUD_OF_MYSELF, PROUD_OF_ANOTHER, CHEER_IN_LOSS, CHEER_KINDS, _NOTHING_MUCH_FILLER,
    _NOTHING_MUCH_BETWEEN,
)
from ..chat_parts.chat_part_06 import (  # noqa: F401
    _body_is_a_feeling, _NOTHING_MUCH_DO, _NOTHING_MUCH_AFTER, _NOTHING_MUCH_TAIL,
    _nothing_much_span, _the_line_on_the_screen, _thanks_that_fit, FIRST_LINE_POOL,
    _the_part_of_day, _says_the_time_of_day, _mid_chat, _just_met, PLAN_CLAUSE_OPENS,
    PLAN_THINGS_OPEN, PLAN_VERB_OPENS, _ing, _plan_clause, _is_greeting, THANKS_FOR,
    HOW_THEY_ARE_LINE, ANSWERS_HOW_ARE_YOU, NOT_GOOD, HEDGE_LEAD, HEDGE_TAIL, ASKED_HOW_ARE_YOU,
    _a_hedge_answering_the_question, HEDGED_OK_LINE, HEDGED_LOW_LINE, DENIAL_FILLER,
    _denies_a_good_word, _is_thanks, A_NOD_BEFORE, A_FIRM_NO, _without_the_at_all, _without_the_nod,
    HOW_ARE_YOU, HOW_ARE_YOU_CONTENT, _is_howareyou, THE_MAKE, _asks_about_the_make, _is_bye,
    LEAVES_ONLY, LEAVING_WORDS, DESCRIBES_THE_DAY, _leaves, NIGHT_SIGNOFF, _bye_kind, _ending_bye,
    EARLY_NIGHTS, OTHER_AWAKE, LOSS, OTHER_SLEPT, SPEAKER_LOST, SORE_NIGHTS, SYMPTOM, END_OF_ROPE,
    WORRY, FREQUENCY_ONLY, NIGHT_FREQUENCY, NIGHT_FREQUENCY_KEPT, BODY_FREQUENCY,
    BODY_FREQUENCY_KEPT, _A_CHILD_OR_THEM, _answers_has_the_frequency, _worry_kind, SKILL,
    _without_skills, EMOTION_FEELING, PANIC_NOW, PANIC_SOMEONE_ELSE, SELF_CUE, LOST_THE_THREAD,
    THING_OF, BARE_FILLER, A_THANK_YOU_AT_THE_END, PLAIN_GOOD_WORDS, PLAIN_GOOD_ASKED,
    PLAIN_GOOD_FRAME, PLAIN_GOOD_FILLERS, PLAIN_GOOD_TAIL, _the_bot_just_asked_them, GOOD_POOLS,
    _a_thank_you_taken_off, _a_plain_good_answer, MEANT_LEADS, _bare_feeling,
)
from ..chat_parts.chat_part_07 import (  # noqa: F401
    _the_weight_said, PERSON_WORDS, CONTRACTIONS, CAUSES_THE_FEELING, HABIT_VERBS, RELIEF_SAID,
    _says_relief, CLAUSE_JOIN, CLAUSE_SUBJECT, _starts_a_clause, _in_its_clause, _owned_by_a_thing,
    OWN_BEEN, _own_state, _carries_on, _owner, HARD_ON_THE_PERSON, LIFE_THING_HARD,
    _hard_about_their_thing, _OTHER_SUBJECT, WEARS_OTHER_PEOPLE_OUT, GUILT_WORDS, STATE_WHEN,
    WANT_TO_WEEP, WEEPING_WITH_JOY, WHY_THE_TEARS, SOMEBODY_ELSE, NOT_THEIR_TEARS, NOT_WANTING_IT,
    MOVED_BY, MOVED_BY_PART, MY_TEARS, CANT_STOP_IT, SOMEONE_IN_THEIR_OWN_TEARS, _WEEP_WORDS,
    _a_low_word, _good_news, KEEPS_HOW_THEY_ARE, KEEPS_HOW_I_AM, A_NAMED_LOW, _weeping, NOT_COPING,
    NOT_COPING_SHAPES, NOT_COPING_FEEL, NOT_COPING_ANYWHERE, GUILT_ABOUT, GOING_MAD,
    MAD_ABOUT_THE_DAY, STRUGGLING_ABOUT_A_THING, HOW_I_GET_THROUGH, ASKS_WHY, A_NIGHT_NOT_SLEPT,
    FIRST_PERSON_BEFORE, IDIOM_PLACE, FEAR_BEFORE, _bad_day, SCATTERED_MIND, _scattered, APART_WHO,
    APART_FROM_PEOPLE, APART_SOMEONE_ELSE, BARE_ACKS, BARE_CARRY_ON, _a_bare_acknowledgement,
    SORRY_KINDS, SORRY_NEWS_KINDS, SORRY_LINES, SORRY_MET, HEAVY_MODULES, _the_heavy_line,
    _apart_from_people, LONELY_STEP_WORDS, NOTHING_HELPING, _idk_kind, _offered_a_choice,
    NOTHING_CONTINUED, _nothing_helped_just_before, _as_said, MIGHT_BE, A_VERDICT_ASKED,
    A_QUESTION_ABOUT_A_FIGURE, LEFT_BEHIND, GOING_ON, GOING_ON_LONG, AT_MYSELF, KICK_MYSELF,
    AT_MYSELF_REPLIES, A_FACULTY_GETTING_WORSE, OWN_MEMORY_OFF, MOOD_KINDS, HEAVY_FEELINGS,
)
from ..chat_parts.chat_part_08 import (  # noqa: F401
    _the_answer_met_it_as_news, _a_loss_before, _reaction, _reaction_pool, _my_own_tears,
    _tears_said_as_a_verb, _a_low_just_before, NEWS_MET, NEWS_MODULES, NOT_A_NOD, ASKED_HOW_IT_WENT,
    _asked_how_it_went, A_JUDGEMENT_ASKED, JUDGEMENT_POOLS, A_SUBJECT_ALREADY_ASKED,
    _a_judgement_asked, _is_a_nod, _the_nod, SOMEONE_ELSE, FIRST_PERSON, AN_AGE_SAID,
    WORK_IN_THE_THREAD, AGE_IN_A_WORK_THREAD, A_DOUBT_ABOUT_WORK, A_TOO_OLD, TAKEN_ON_REPLIES,
    TOO_OLD_REPLIES, _a_doubt_about_being_taken_on, _in_a_work_thread, _the_age_in_a_work_thread,
    _going_on, FEEL_LIKE, FEEL_LIKE_WANT, FEEL_LIKE_NOT_HEARD, OTHER_FEELS_LIKE,
    FEEL_LIKE_NOT_ENOUGH, FEEL_LIKE_WORTH, FEEL_LIKE_ROLE, FEEL_LIKE_COPE, FEEL_LIKE_AT_HOME,
    FEEL_LIKE_LOAD, FEEL_LIKE_HOME_LOAD, FEEL_LIKE_GOOD, ARRIVAL_WORDS, FEEL_LIKE_MAIN_ANSWERS,
    FEEL_LIKE_OVERLOAD, FEEL_LIKE_ADRIFT, LIFE_ADRIFT, IDEATION, EVENT_DONE, FEEL_LIKE_EVERYTHING,
    FEEL_LIKE_PHYSICAL, FEEL_LIKE_ILLNESS, FEEL_LIKE_LEFT, FEEL_LIKE_JUDGEMENT,
    _a_journey_not_progress, GOOD_TAIL_LEADS, _STATE_OF_THEIRS, _said_about_themselves, _feel_like,
    AGAINST_ME, AGAINST_ME_SELF, AGAINST_ME_ITS_SCOPE, AGAINST_ME_THE_WEEK, JUST_A_CONTINUATION,
    _a_feeling_riding_on_the_thread, _against_me,
)
from ..chat_parts.chat_part_09 import (  # noqa: F401
    LOW_MOOD, MOOD_NIGHTS, WORRY_SOMEONE, CARE, NIGHT_SAID, WORRY_SOMEONE_NIGHT, WORRY_PRONOUN,
    WORRY_SOMEONE_DAY, _worry_someone, _loss_recent, _low_mood_recent, MAYBE_SOMEONE,
    SOMEONE_TROUBLE_ANY, SERIOUS_DIAGNOSIS, THING_BEFORE_CANNOT, _a_thing_cannot, SOMEONE_REPLY,
    SOMEONE_IS_IT_NORMAL, SOMEONE_AGES_IT, SOMEONE_MORE, SOMEONE_NEXT_STEP, SOMEONE_NORMAL_ANY,
    SOMEONE_BRING_SOMEONE, SOMEONE_NORMAL, SOMEONE_AGAIN, SOMEONE_NEXT, YOUNG, FEAR, SOMEONE_ASK,
    _checks_the_fact, ROW_SIZE, A_ROW, A_ROW_CLOSE, ROW_HER, ROW_HIM, ROW_ASK, FALLING_OUT,
    ROW_REPLY, _close_nouns, _names_the_person, A_ROW_NOT_CLOSE, _a_row_person, _keep_the_row,
    observe, ROW_EVENT_ID, ROW_FELL_OUT, WANTS_AN_APOLOGY, ASKS_FOR_WORDS, _the_base_has_an_answer,
    ROW_ABOUT, ROW_ABOUT_A_PERSON, _the_row_names_its_subject, _the_base_answers_the_row,
    _ASKS_AFTER, _a_row, ROW_CONTACT, ROW_CONTACT_ASK, ROW_NEXT, ROW_SPACE, ROW_SAID_SPACE, ROW_HOW,
    ROW_HOW_REPLY, ROW_SPACE_REPLY, A_QUIET_AT_ME, A_A_CHILD, A_TEN_OR_OVER, A_WHAT_HAPPENED,
    A_BARE_MOVE_ASK, _a_teen_has_gone_quiet, _a_quarrel_since, _the_ask_in_the_line, _a_row_next,
    ROW_ENDING, ROW_ENDING_REPLY, ROW_HUNG_UP, ROW_ENDING_REPLY_HUNG_UP, _a_row_ending,
    _row_pronoun, _their_of, _they_of, _row_subject, _the_deed_before, _a_repair_is_open, LIMIT,
    PLAN_ASK, _after_a_plan,
)
from ..chat_parts.chat_part_10 import (  # noqa: F401
    _judged_as_a_noun, _judgement, _intent, _says_nothing_much, _frequency_of_the_last_trouble,
    _frequency_is_the_turn, after, _early_start, _said_of_the_person, _a_person_who_wears_you_out,
    _says_how_the_person_is, _not_coping, _speaker_going_mad, _grieving, _better_answer_exists,
    _still_about_me, _about_the_person, _my_night, _stuck, OTHER_PERSON, OTHER_PRONOUN, CRY_WOLF,
    OTHER_FEELING_VERB, PLURAL_WORDS, SHE_WORDS, HE_WORDS, OTHER_STOP, OTHER_QUESTION,
    _A_HELP_ASK_AT_END, OTHER_ADVERB, OTHER_VERB, A_KIND_OF_THING, HOW_MUCH_OF_IT,
    _names_a_kind_of_thing, OTHER_NEG, GENERIC_OTHER_REPLIES, OTHER_REPLIES, ABOUT_REPLIES,
    FEDUP_LEAD, FEDUP_REPLIES, FEDUP_GERUND_SAFE, FED_UP_WHOLE_OF_IT, _recent_plural, _pronouns,
    OTHER_BAD_NIGHT, _other_feeling, _the_thing, JOINED_PERSON, THING_THAT_STAYS, _thing_that_stays,
    FED_UP_THING, FED_UP_STOPS, FED_UP_BARE,
)
from ..chat_parts.chat_part_11 import (  # noqa: F401
    FED_UP_THIN, NOT_A_THING, NOT_A_THING_FIRST, FEELING_WORD, NOTHING_NAMED,
    _confusion_names_a_thing, CONFUSION_IDIOM_WORDS, SECOND_PERSON, SECOND_PERSON_RE, FED_UP_DENIED,
    FED_UP_ABOUT_THE_BOT, FED_UP_WITH_A_PERSON, FED_UP_FILLER, FEDUP_SAID_PHRASE, _fedup_phrase,
    _fed_up_with, OTHER_REPLIES_SMALL_CHILD, _the_small_child, _someone_reply, _last_was_joke,
    _drop_tail, _place_of, COUNTRY_CAPS, ARTICLE_PLACES, _tidy, _numbers, _place_values,
    _note_the_pool, _just_named, _name_said, _pet_name, _question_coming, NOT_A_SUBJECT,
    A_FEELING_SAID, _the_not_knowing_has_a_subject, PLACE_OF_CARE, BACK_FROM_CARE, WENT_TO_CARE,
    WAS_IN_CARE, THIS_WEEK, _the_visit_was_this_week, PUT_ON, _A_DRESSING, TAKEN_OUT,
    HAD_A_THING_DONE, RESULT_CLEAR, DOCTOR_SAID, NIGHT, LONG_AGO, PART_FINE, RESTED, REST_WORD,
    GOT_RESULTS, NOT_A_DIAGNOSIS, INITIALISMS, _a_thing_of_care, _ends_plural, _keep_the_letters,
    WEARER, A_BODY, _wearer_is_themselves, _names_a_person, VERDICT_THING, _head_word,
    _the_poor_describer, _the_thing_this_line_names, _trip_place, GOOD_TIME_WORDS, GOOD_TIME_THINGS,
    GOOD_TIME, GOOD_TIME_LINES, _a_good_time_they_had, DETAIL_LINES, _the_detail_of_the_good_time,
    _the_thread_is_heavy_here, _a_pick_is_in_hand, INTENTION, WANT, QUESTION, THING_SKIP, KEEPS,
    KEEP_ABOUT_SOMEONE, KEEP_INTENT, KEEP_A_BELIEF, A_THOUGHT_THAT_IS_NOT_A_THING, A_DOUBT_ABOUT_IT,
    A_THOUGHT_ABOUT_OTHERS, A_HOPELESS_THOUGHT, ASK_TAIL, NEED_NOW, MEDICINE, KEEPS_SYMPTOM,
    TIME_TAIL,
)
from ..chat_parts.chat_part_12 import (  # noqa: F401
    _after_a_lost_thread, _reply, _after_lonely, _nothing_helps, _feeling, _say,
    _cheer_or_the_question, _conversation, _about_the_night_out, _saw_something, _told_a_trip,
    _night_out, FILLER_TAIL, FILLER_TAIL_PHRASES, CORRECTION_TAIL, NEGATED_TAIL,
    _without_a_filler_tail, INDEFINITE, PAIN_PART, INDEFINITE_SKIP, ASK_KIND, DOING, ALWAYS,
    ONE_OFF, DECISION, TASK_ONLY, STATE, CONTINUING, BARE_FEELING, RELATIVE, LEAVE, _A_NEED_ASK,
    PERSON_WORK, NOT_A_GOOD, NOT_THE_THING, _A_PERSON_ALREADY_IN_THE_LINE, NOT_A_THING_WITH_KINDS,
    _kindless, KINDLESS, _PERSON_IN_THE_TAIL, A_BREAK_FROM_SOMEONE, CHOOSING, THING_REPLIES,
    _a_death_just_said, _in_loss, _answers_knows,
)
from ..chat_parts.chat_part_13 import (  # noqa: F401
    _short_talk, _without_the_might, _asks_for_a_joke, GENERIC_THING_WORDS, _VERB_ENDINGS,
    _verb_stem, _answers_is_about_the_thing, _HOW_STOP, _answers_has_the_how,
    _fallback_has_its_own_pool, _the_words_they_meant, _their_thing, SELF_JOKE, _NOT_A_SUBJECT,
    REPORTS_A_JOKE, _asks_outright, _joined_read, _joke, _normalised_line, STANDING_LINE,
    STANDING_WHAT_REPLIES, STANDING_REPLIES, A_THING_THAT_BREAKS, STANDING_THING_REPLIES,
    STANDING_FEELING_REPLIES, ASKED_HOW_LONG, TIRED_SAID, _a_constant_tiredness, _standing,
    _repaired_line, DONT_KNOW, DONT_KNOW_FILLER, _says_dont_know, CHAT_SCATTER, CHAT_SCATTER_ASKS,
    CHAT_SCATTER_CTX, CHAT_SCATTER_NOT, CHAT_SCATTER_LEFTOVER, _only_the_apology,
    CHAT_SCATTER_REPLIES, CHAT_SCATTER_ALONE, CHAT_ASKING_REPLIES, CHAT_ASKING_ALONE, _chat_scatter,
)
from ..chat_parts.chat_part_14 import (  # noqa: F401
    _a_follow_up_about_their_person, TAKES_AS_IT_COMES, _after_a_repair, _about_someone,
    _own_medical_news, claims_instead, CLAIMS_INSTEAD, SAID_WRONG_DEED, SAID_WRONG, SAID_WRONG_NOT,
    SAID_WRONG_LOST, SAID_WRONG_TO_AN_ANIMAL, SAID_WRONG_TO_A_PROFESSIONAL,
    SAID_WRONG_AT_THEMSELVES, SAID_WRONG_NEXT, ASKS_FOR_THE_WORDS, ASKS_WHAT_TO_DO,
    SAID_WRONG_REPLIES, DEED_REPLIES, LEFT_IT_TOO_LONG_REPLIES, FORGOT_DATE_REPLIES, DEED_WORDS,
    FORGOT_DATE_WORDS, AMENDS_REPLIES, FORGOT_DATE_NEXT, _the_deed_pool, _the_words_pool,
    THEY_ARE_NOT_TALKING, NOT_TALKING_AFTER_A_REPAIR, DEED_NEXT, SAID_UNKINDLY, FEELING_CLAUSE,
    SAID_UNKINDLY_REPLIES, SAID_UNKINDLY_FAMILY, FAMILY_NAMED, _an_entry_answers_the_deed,
    _said_wrong, I_SAID, CLAUSE_BOUNDARY, _own_deed, FIRST_PERSON_DEED, _said_unkindly,
    _a_part_of_the_answer_they_have, _the_newest_line_started_the_topic, A_VERDICT,
    A_VERDICT_FILLER, A_DOES_SOMETHING, A_STATE_WORD, A_REASSURES, A_NEW_CONDITION, A_ASKS_WHERE,
    A_WHEN_TO_GET_HELP, ASKS_A_PRICE, A_REPEAT_FRAME, A_STATE_ASK, ASKS_A_FIGURE,
    _a_topic_still_in_this_exchange, DISTRESS, _reads_as_distress,
)
from ..chat_parts.chat_part_15 import (  # noqa: F401
    _news, _a_mood_pool_line, _the_verdict_in, HEARD_NOTHING, _nothing_was_heard, TIME_ASK,
    _asks_what_they_said, TOPIC_WORD, _the_entrys_own_name, _about_the_topic, NOT_AN_ANSWER,
    _says_nothing_about_the_ask, QUESTION_OPEN, YES_NO_OPEN, EVERY_YES_NO_OPEN, YES_NO_WORDS,
    OFFERING, OWN_THING, LOOKING_FOR, FOUND_THING, AN_ARTICLE, ASKS_ABOUT_A_THING,
    ASKS_WHAT_TO_DO_WITH, A_CONTAINER, _names_its_own_thing, _bare_ask, _words_only, A_SHORT_LINE,
    A_REPEAT_LEAD, _the_same_answer_again, _said_before, _says_the_kind, WORK_PERSON, WORK_FAULT,
    WORK_ASK, WORK_UNSEEN, WORK_CONTEXT, WORK_RELATIVE, WORK_GRUMBLE, WORK_UNSEEN_REPLY,
    _work_grumble, LAUGH_REPORT, LAUGH_TOGETHER, LAUGH_TOGETHER_NOT, LAUGH_MINE, LAUGH_AT_ME,
    LAUGH_NOT_A_PERSON, LAUGH_BAD_SETTING, _laughing_at, _the_condolence_is_the_last_thing,
    LAUGH_CARRIED_ON, LAUGH_CARRIED_ON_NOT, LAUGH_CARRIED_ON_REPLY, _laughing_still,
    SOMEBODY_THINKS, EVERYONE_THINKS, THEIR_OPINION_IS_A_HEALTH_MATTER, THINKS_REPLIES,
    _somebody_thinks_i_should,
)
from ..chat_parts.chat_part_16 import (  # noqa: F401
    _thinks_pool, A_REPORT_A_THING, A_HEARD_A_THING, A_PRAISING_VERB, A_ASKED_NOT_TOLD,
    A_PRAISE_OF_A_THING, A_RECOMMENDATION_IS_NOT, SECONDHAND_PRAISE_REPLIES,
    _somebody_recommended_a_thing, _respond,
)
from ..chat_parts.chat_part_17 import (  # noqa: F401
    respond, _follow_up_reading, _never_twice,
)
