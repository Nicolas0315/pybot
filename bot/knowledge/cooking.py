"""Cooking and food: everyday how-tos, timings, fixes and food safety.

The answers lane owns this domain. Everything here is data plus a few small functions:
one Entry per thing people ask about, keyed by the words that identify it (a dish, an
ingredient, a kitchen problem), and phrased the way a good cook would explain it. The
matcher in bot/knowledge/lookup.py finds the entry; bot/modules/answers.py answers.

Timings are for a home oven and say so; fan ovens run about 20C cooler in Celsius
terms, so the entries give both where it matters.

Two kinds of entry sit side by side: a technique ("how long do I boil potatoes") and a dish
("what can I make with potatoes and cheese"). The dish entries are keyed by the thing in the
fridge, so "half a cabbage", "a tin of chickpeas" and "bananas going brown" each reach a
recipe; the general "what shall I cook" entry keeps out of any line that names a food, because
the food's own entry answers it better.

The implementation lives in the `cooking_part_NN` parts (in bot/knowledge_parts); this module keeps the header
imports and re-exports every name the parts bind, so `cooking.<name>` is what it was.
"""
import re

from ..understanding import line_as_read
from ..knowledge.dishes import KEEP_QUALITY_WORDS, PLAN_NAMES
from ..knowledge.keeping_cooked import COOKED_KEEP_ASK, COOKED_KEEP_AVOID, COOKED_KEEPS
from ..knowledge.lookup import (entry, find, kinds_entries, says_it_has_gone_off as _says_it_has_gone_off,
                     TOOTH_OR_GUM)
from ..knowledge.meals import NOT_MINE_ENTRY as _NOT_MINE, says_a_diet as _says_a_diet
# The bake-fault dispatcher and its tables live in their own file: this one is on the
# uploader's size ceiling, and the entry below still reaches the same code.
from ..knowledge.bake_faults import (_BAKE_FAULT, _BAKE_FAULT_FAMILIES, _BAKE_THING,  # noqa: F401
                          _bake_always, _bake_fault)  # noqa: F401
from ..knowledge.prices import a_price_is_judged
from ..knowledge.units import BIRD_GRAMS, people_in_groups
from ..knowledge.cooking_tables import (NOT_WANTED, MEAL_IDEAS, SIDES, SEASONINGS, DIET_VARIANTS, FREEZE_FACTS, FOOD_CALORIES, FOOD_NUTRIENTS, FOOD_CALORIE_MEALS, BAKES, KEEPS, PANTRY, DISHES, RECIPES)  # noqa: F401  (the tables, so the rows below can read them)

from ..knowledge_parts.cooking_part_01 import (  # noqa: F401
    ANSWERS, BREAD_TIP, BAKED_GOODS, BAKED_GOODS_WORDS, CONTAINER_FOODS, CONTAINER_MONTHS,
    _container_keep, _stuck_jar, _baked_keep, KEEP_ASK, OPEN_ASK, _FOOD, _A_FAULT_SAID, _A_TASTE,
    _corn, BASICS, NOT_A_METHOD, KNOWS_READY, STAPLE_ASK, _BODY_TOO_THICK, _BODY_TOO_THIN,
    _TOO_THICK_SAID, _REST_BODY, _REST_CUT, _REST_CUT_PHRASE, _resting_a_body_part, _rest_the_meat,
    CHILD_WORDS, _about_a_child, KIDS_VEG, ADULT_VEG, _the_veg_card_was_just_said, _kids_veg,
    _harvest_crops, _done_words, _AN_APPLIANCE, _an_appliance_has_the_line, _pancakes,
    _pancake_batch, _sweet_potato, PET_LINE_WORDS, _thighs, _weight_words, _legs, _legs_method,
    _tenders_method, _bird_weight, _hours_words, _in_words, _chicken_time, _A_RUB, _a_seasoning,
    _ONES, _TEENS, _TENS, _spelled_counts, _CROWD_PHRASES, _OCCASIONS, _NOT_A_TABLE, _people_after,
    _TABLE_PHRASES, _CROWD_VERBS, _CROWD_FOOD, _CROWD_QUANTITY,
)
from ..knowledge_parts.cooking_part_02 import (  # noqa: F401
    _CROWD_NOT_A_MEAL, _occasion, plan_side, side_for, _table_side, _plan_side, ANY_MEAL,
    DIABETIC_PLATE, DIABETES_WORDS, _says_diabetes, PLAN_WEEK, PLAN_CHEAP, PLAN_BATCH, TIME_PHRASES,
    TIME_WORDS, TIME_TWENTY, TIME_SOON, TIME_MIDDLING, _minutes_named, CHEAP_DISHES, CHEAP_TAIL,
    CHEAP_TAIL_MEATFREE, PROTEIN_SOURCES, PROTEIN_COMPLETE, _protein, BAKED_APPLES, BAKED_FRUIT,
    STEWED_FRUIT, MICROWAVED_FRUIT, _the_baked_fruit, _bake_fruit, JACKET_BAKE, JACKET_FILL,
    _jacket, JAM_RECIPE, CHUTNEY_RECIPE, _jam_make, POACH_FISH, _poach_fish, MUSHROOM_WASH,
    MUSHROOM_PEEL, _mushroom_wash, _same, _BAKED_GOODS, _CAKE_NAMES, _BAKE_KEEPING, _BAKED,
    _BAKE_NAMES, _the_bake_named, _BAKE_DISH, _RICE_DISH, _DIP_DISH, _SAUCE_DISH, _asks_why, _dry,
    _bread, COMING_APART, _FISH_NAMES, _COMING_APART_ON_PURPOSE, _MUSHY_OWN_ROW, _falls_apart,
    _DOUGH_WET, _DOUGH_DRY, _DOUGH_NOT, _dough, _MASH_DISH, _CHICKPEA_WET, _GREEN_DIP_WET,
    _OLIVE_DIP_WET, _DIP_DISH_WET, _AVOCADO_WET, _PASTRY_WET, _PASTRY_DOUGH_WET, _DUMPLING_WET,
    _RICE_WET, _RISOTTO_WET, _COUSCOUS_WET, _WET_FOOD, _BAKE_WET, _FRY_MIX_WET, _BREAD_DOUGH_WET,
    _BATTER_WET, _PORRIDGE_WET, _WET_CUSTARD, _WET_ICING, _WET_DRINK, _WET_YOGHURT, _WET_DIP_WORDS,
    _WET_DAL, _WET_SLAW, _PLANT_MILK, _PLANT_MILK_DISH, _watery, _lumpy,
)
from ..knowledge_parts.cooking_part_03 import (  # noqa: F401
    _FREEZE_AVOID, _CHEAP_AVOID, _MEAL_ASK_AVOID, WANT_SOMETHING_ELSE, _CLUMP_WORDS, _EGG_STORE,
    _EGG_STORE_TEXT, _EGG_TEST_TEXT, _eggs, _pasta_cook, _popcorn_make, _popcorn_keep,
    _STEWED_FRUIT, _STEWED_WHY, _stewed_fruit, _tough, _BAKE, _salty, _scramble, _EGG_DISH,
    _EGG_FAULT, _EGG_PAN, _EGG_FRITTATA, _EGG_QUICHE, _EGG_FRIED, _EGG_SAUCE, _egg_fault, _cookies,
    _chocolate, _GRAIN_FOOD, _GRAIN_WORD, _grainy, _SUGAR_MAKING, _SUGAR_TROUBLE, _soup, _flat,
    _FROM_FROZEN, _FROZEN_TIME, _FROZEN_WHAT, _FROZEN_ASK, _FROZEN_CUTS, _FROZEN_WHOLE, _FROZEN_ONE,
    _FROZEN_MANY, _frozen_from_the_bag, _turkey, _cut_time, _turkey_cut, _hummus, JOINT_BEEF,
    JOINT_PORK, GOING_OFF_ASK, KEEPING_VERB, IN_THE_OVEN, _roast_joint, KEEPING_SENSE,
    _MINCE_GRAIN_DISH, _MINCE_GRAIN_WORD, _BOLOGNESE_WORDS, _mince, FOOD, _said_so_far,
    _PEOPLE_AFTER, _COUNT_WORD_SHAPES, _COUNT_VALUE, MEATLESS_ROAST, _head_count, _roast_shopping,
    _LACTOSE_WORDS, _NOT_LACTOSE_WORDS, _a_lactose_intolerance, _record_says_lactose,
    _their_diet_is_a_lactose_intolerance, _list_words, FISH_SPLIT, _the_guest,
    NOT_SETTLED_BY_THE_RECIPE,
)
from ..knowledge_parts.cooking_part_04 import (  # noqa: F401
    LACTOSE_LOW, LACTOSE_HIGH, _LACTOSE_SAYS, _bans, GLUTEN_WORDS, SWAP_WINDOW, _first_sentence,
    _lentils, PET_ANIMALS, _PET_OWNED, _PET_EATING, _ORDER_NOT_A_MEAL, _MILK_IN_TEA_NOT_A_MEAL,
    _a_brew_not_a_dinner, _an_order_not_a_dinner, _PLANT_NOT_A_DINNER, _PLANT_GARDEN_VERB,
    _PLANT_COOK_ASK, _PLANT_KITCHEN_PLANT, _PLANT_BEARS, _PLANT_DO_WITH, _the_garden_has_this_plant,
    _PLANT_WOODY, _PLANT_PURCHASE, _a_plant_from_the_shop, _FEEDING_ANIMALS, FEEDING_NOT_FOOD,
    _pet_not_dinner, PET_MEAT_ANIMALS, PET_NOT_FOOD, PET_CARE, PET_COOKING_ASK, ANY_BREAKFAST,
    BREAKFAST_TAIL, ANY_LUNCH, FREEZER_KEEP, FREEZE_ANY, HONEY_BABY, HONEY_OLDER, _honey_age,
    _FREEZE_WORD_FORMS, _FREEZE_POINTS_AT, _points_at_something, _freeze_units, _a_freeze_fact,
    _names_one_food, _the_dish_the_chat_names, ALSO_OUT, _HAVE_NONE, _OUT_ASK, _VEGAN_ASK,
    _asks_vegan, SUBSTITUTE_PHRASES, KEEPING, COOK_VERBS, STORAGE, NUTRIENT_COLUMNS,
    NUTRIENT_CONTEXT, _MINERALS, _NUTRIENT_WORDS, _NUTRIENT_DISH, _NUTRIENT_JOIN, _COUNT_WORDS,
    _plurals, _portion_count, _squashed, _one_letter_apart, _the_food_named_by_a_slip,
    _a_food_word_misspelt, _nutrient_food, _nutrient_asked, _PROTEIN_SHARES, _grams, _WEIGHT_WORDS,
    _portion_size, _weight_in_the_line, _figure, _CALORIE_PLURAL, _CALORIE_NOT_A_DISH, CALORIE_ASKS,
    _CALORIE_OWN, _CALORIE_DISH, _CALORIE_JOIN, _names_a_food, GLUTEN_FREE_ASKS, GLUTEN_FREE_DISHES,
    _GLUTEN_FREE_SKIP, _GLUTEN_MAKING, _gluten_free, GLUTEN_FACT_DIET, GLUTEN_FACT_NAMED_SWAP,
    GLUTEN_FACT_NOT_PLAIN, LACKS, REQUIRES, LACK_HEADS, LACK_NOUNS, LACK_ATTACHED, _says_gone,
    _line, TURNS_DOWN, DECIDING, _sentences, NO_OVEN, NO_HOB, NO_BAKING, _GRIDDLE_DOUGH,
    _GRIDDLE_BATTER, _GRIDDLE_WARM, _GRIDDLE_TAIL, NO_OVEN_BREAD, NO_KETTLE,
)
from ..knowledge_parts.cooking_part_05 import (  # noqa: F401
    _sugar_work, NO_OVEN_ONLY, NO_MICROWAVE, LISTING, COOKING_ASKS, PUDDING_IDEAS, ONLY_ONE,
    HAVE_ONE, available, _herbs_keep, COOK_WORDS, WORD_SUBJECT, NOT_A_COOKING_LINE,
    DEFINITION_WORDS, _names_a_subject, _cook_word_hit, _MASH_NOT_THIS, _NO_MEAT, _TIMING_ASKS,
    _ALREADY_BAKED_PHRASES, _NONSTICK_CLEAN, _NONSTICK_KEEP, _non_stick_pan, TEA_METHOD_TEXT,
    TEA_POT_TEXT, TEA_ICED_TEXT, TEA_CLOUDY_TEXT, TEA_FAULT_TEXT, TEA_GREEN_TEXT, TEA_TWICE_TEXT,
    _rice_time, _NO_YEAST, _bread_rise_answer, _COFFEE_BITTER, _COFFEE_SOUR, _COFFEE_BURNT,
    _coffee_fault, LEAFY, LEAFY_AVOID, _PAN_DISH, _PAN_CLEAN, _BURNT_PAN_REPLY, _PAN_WORDS,
    _REMOVAL_FROM_A_PAN, _BURNT_ON_A_PAN, _burnt_on_the_pan, _BURNT_DISH_REPLY, _BURNT_MEAT,
    _BURNT_MEAT_REPLY, _BURNT_VEG, _BURNT_VEG_REPLY, _BURNT_BATTER, _BURNT_BATTER_REPLY,
    _BURNT_EATING_ASK, _BURNT_EATING_REPLY, _ROAST_PARTS, _ROAST_PART_REPLY, _BAKE_NOUNS,
    _GRIME_WORDS, _TIN_OR_OVEN, _BURNT_ON, _words_and_text, _says, _burnt_pan, _BAKED_BURNT,
    _TIN_SIZE, _TIN_FILL, _TIN_LINE, _TIN_GREASE, _TIN_FRUIT, _TIN_GREASE_WORDS, _TIN_LINE_WORDS,
    _TIN_FRUIT_WORDS, _tin_answer, _CAKE_FAULT_WORDS, _cake_fault, _PASTRY_SHRINK_WORDS,
    _pastry_fault, _BAKE_PREVENTION, _BAKE_BURNT, _BAKE_BOTTOM_REPLY, _burnt, _FRIED_GREASY,
    _POT_GREASY, _MEAT_GREASY, _PASTRY_GREASY, _greasy, _CUSTARD_NAMES, _split, _UNDER_BAKE,
    _UNDER_BREAD, _UNDER_STARCH, _UNDER_VEG, _undercooked, _DIP_FIXES,
)
from ..knowledge_parts.cooking_part_06 import (  # noqa: F401
    _DIP_PLAIN, OIL_SMOKE_POINTS, _ONTO_A_PERSON, _a_dish_with_a_heat,
    _SOMETHING_IS_WRONG_WITH_THE_PAN, _dip_fault, _SOGGY_BREAD, _SOGGY_LEAF, _BAKE_FOLLOW_SHAPES,
    _NEXT_SHAPES, _USE_SHAPES, _BAKE_KEEP_SHAPES, _bake_keep_sentence, _bake_keep, _bake_follow,
    _BREAD_WORDS, _GUMMY_CAKE, _GUMMY_BREAD, _gummy, KEEP_DATE_WORDS, MOULD_WORDS, _SPOILT_WORDS,
    LEFTOVER_IDEAS, LEFTOVER_SOUP, NOT_THIS_FOOD, PLANT_MILKS, LEFT_POINTER, LEFTOVER_PHRASES,
    MEAL_WANTS, MEAL_PHRASES, BOUGHT_PHRASES, MEAL_ASK_PHRASES, USE_UP_ASKS, RESTRICTED_EATING,
    ACTIVITY_PHRASES, MAKING_IT_YOURSELF_PHRASES, ILLNESS_PHRASES, FOOD_SAFETY_RULES,
    PROBLEM_PHRASES, EMPTY_PHRASES, EMPTY_ASK_PHRASES, EMPTY_KITCHEN, OUT_ASKS, OUT_OF_FRESH,
    OUT_OF_FORM, FORM_ADVICE, FROZEN_MEAT, FROZEN_FRUIT, FORM_FOODS, RULING_OUT_PHRASES,
    REFUSAL_REACH, FOOD_CLASSES, DIETS, NEGATION_REACH, COOKED_REACH, _READ_FOR_INGREDIENTS,
    _READ_FOR_INGREDIENTS_KEEP, MEAT_SWAPS, _VEG_PHRASES, _VEG_DINNER, _VEG_DINNER_CHEAP,
    _plain_words, _recent_user_turns, AND_NO, SHORTAGE_WORDS, _STAND_IN_ASK, _reads_as_news,
    _CHOICE_WORDS, _COOKING_MEDIUM, _NUMBER_WORD, COOKED_KEEPING, _this_line_only, _RECIPE_ANSWERS,
    _USE_UP_WORDS, POINT_BACK, PAIRING_WORDS, SECOND_IDEA, POINT_BACK_STOP, recent_replies,
    _words_of, _PLANNED_FOOD, SCALE_DOWN, SCALE_UP, SCALE_UP_WORDS,
)
from ..knowledge_parts.cooking_part_07 import (  # noqa: F401
    _STAPLE_NAMES, _learn_to_cook, DISH_BEFORE, DISH_AFTER, _body, _more_veg, _A_HEAT_OR_TIME,
    _A_HOW_MUCH, _A_SIDE_SAID, _not_a_portion_ask, _staple, _a_guard_said, TENDER_ADJECTIVE_BEFORE,
    _tenders_are_a_piece, SEASONING_ASKS, SIDE_ASKS, _CROWD_NUMBERS, _CROWD_SPELLED, _CROWD_FOR,
    _CROWD_WITHIN, _crowd, _NAMED_TABLE, _named_table, _table_text, _crowd_ask, _CROWD_WORDS,
    _trays, _crowd_meal, _crowd_or_any, A_TIME_OR_HEAT_ASK, _sides, MONTHS_SAID, GOING_SAID,
    EATING_WORDS, PLAN_WORDS, CHEAP_PLAN_WORDS, TONIGHT_WORDS, _time_budget, _SOFT_FRUIT,
    _SOFT_FRUIT_WANTS_THE_OVEN, _a_soft_fruit_is_still_a_cooking_question, _meal_plan,
    _NO_SPREAD_RISE, _NO_CAKE_RISE, _NO_LOAF_RISE, _FROZEN_CUT_WORDS, _frozen_cook_reply,
    _meat_defrost, _MINCE_PIE_PHRASE, _mince_grainy, VAGUE, _VAGUE_KEYS, MEAT, FISH, DAIRY, CHEESES,
    EGGS, NUTS, GLUTEN, SHELLFISH, FAMILIES, NO_MEAT_DIET, CONDITION_BANS, NOT_THIS, AVOIDED,
    FREEFROM, TROUBLE, _DIET_ASKED, _DIET_ASK_NOT_A_FOOD, _ask_about_the_food, _excluded,
    LIST_JOINERS, LIST_FOODS, _families_of, _foods_in_list, _denied_at, EAT_ASK, FANCY_ASK,
    EAT_ASK_THEM, MADE_OF, _names, _families, _name, FAMILY_SAY, SELF_SAY, EAT_ASK_BARE, EAT_ASK_IF,
    EAT_ANY, EAT_ANY_WORDS, MAY_HAVE, BAN_SAY, ANY_FAMILY, _food_named, _foods_named, SINGULAR_IN_S,
    _is_plural, _named_as, _bans_for, THIRD_PERSON, _mine_only, _bans_from_store, _bans_of,
    _named_families, _bans_said, BAN_SAY_NAME, FREE_OF, _food_may, _not_for_them, _POINTING,
    _LEAVE_IT_OUT, _foods_a_line_points_at, pointed_at_a_food, _free_of, _bans_it,
    _LACTOSE_FREE_ASK, _lactose_answer, _one_food_answer, _no_meat_also_means_fish, MEAT_SAYS,
    FISH_SAYS, DAIRY_SAYS, EGG_SAYS, NUT_SAYS, SHELLFISH_SAYS, DAIRY_SWAPS, NUT_SWAPS, GLUTEN_SWAPS,
    NOT_THE_DAIRY, CAUTION_SAID, PLANT_SAID, SWAP_BEFORE, SWAP_AFTER, avoids, _family_of,
    avoids_for_the_one_talked_about, SWAP_CLAUSE, SAYS_THE_FOOD_IS_OUT, GLUTEN_FREE_ALREADY,
    SUBSTITUTE_ASK, _any_meal, _NOT_A_DISH, _cauliflower_rice, _leftover, _PULSES_HARD,
    _PULSES_NO_SOAK, _PULSES_TIN, _PULSES_FRESH, _PULSES_DRIED, _PULSES_APPLIANCE, _PULSES_KIDNEY,
    _pulses, _PLAN_ASK, _keeps_its_own_name, _PLANT_SOURCE, _a_plant_not_a_dinner, FEEDING_EATS,
    FEEDING_GIVEN, FEEDING_SAFE_FOR, _feeding_ask, PET_HOME, _reads_as_a_pet, _pet_or_meat,
    _meal_ideas, _pantry_idea, _porridge, BREAKFAST_CHOICES, SHORT_OF_ASK, _short_of_food, _rushed,
    _breakfast_ideas, _lunch_ideas, _NOT_A_FREEZER, _freeze_food, SOYA, _nut_free, _vegan_bake,
    _SWAP_ASK, _NUTRIENT_ASK_WORDS, _AMOUNT_ASKED, _nutrients, _calories, GLUTEN_FACT_ASKS,
    GLUTEN_FACT_FOODS, GLUTEN_FACT_SWAPS, GLUTEN_FACT_OPENING, GLUTEN_FACT_MAKING,
    asks_a_gluten_fact, _free_of_gluten_fact, _SWAP_VERDICTS, LACK_SAID, missing, GRIDDLE_BAKES,
    GRIDDLE_DOUGH, GRIDDLE_BATTER, _griddle_answer, SWEET_ASK, CROWD, BREAD, CAKEISH,
    _asks_for_sweet, _no_baking, _pudding_ideas, without, NEEDS_DEFINITION, _cook_word,
    _BAKE_ALIASES, _bake_aliases, _PANTRY_AS_WORDS, _pantry_words, _bake_hits, _names_a_bake,
    _ALREADY_BAKED_WORDS, _already_baked, _bake, _ASKS_WHAT_TO_HAVE, _FOR_A_MEAL, _tea_reply,
    _burnt_dish, _VESSEL_PHRASES, _BAKE_BOTTOM, _BAKE_STOP, _BAKE_DONE, _bake_burning, _BODY_PART,
    _fat_has_landed_on_a_person, _oil_smoking, _soggy_lunch, _LISTED_ENTRIES, _NO_SUGAR, ENTRIES,
    _KINDS, _offered, _replaced, _verdict, FREEZER_WORDS, STILL_FROZEN_WORDS, COOKING_VERBS,
    _already_cooked_is_the_question, KEEP_WORDS, COOKED_WORDS, USE_UP_WORDS, COOKING_WORDS, STORING,
    KEEP_EXTRA_WORDS, KEEP_STAND_DOWN, METHOD_WORDS, DONENESS, GREEN_SAFETY_WORDS, BAKED_LINE_WORDS,
    _COOKED_KEEPING, _KEEPING_ASK, _row, _A_BLANK_FILLER, _a_food_and_not_a_blank, _OFF_ASK,
    _OFF_THE_THING, KEEP_AHEAD_OF_THE_GENERAL, _reply, _avoid, _key, _bias, KEEPS_COOKED,
    KEEPS_COOKED_WORDS, _NAMED_FOODS, _FOODS_SAID, _foods_said, _leftover_meal_reply,
    LEFTOVER_WORDS, JOINERS, _words_just_before, MEAL_CUES, FOOD_CUES, NOT_MEAL_ASKS,
    SUBSTITUTE_WORDS, PROBLEM_WORDS, SICK_PHRASES, SICK_EAT_WORDS, PREVENTION_ASK, AWAY_FROM_HOME,
    _SICK_FROM_FOOD, _eat_when_ill, MEAL_WORDS, PET_WORDS, _INGREDIENT_WORDS, _fold,
    _fold_meal_ideas, _aliases, _idea, _alias, _ALIASES_BY_LENGTH, _ALIAS_TEXT, FORMS, FRUIT_WORDS,
    _form_word, _form_swap, _FORM_FOOD_WORDS, FORM_SWAP_WORDS, NEGATIONS, CLAUSE_BREAK,
    _refused_before, FILLER, _DIET_WORDS, SOFTENED, EVENT_HEADS, _renamed_by_an_event,
    _named_ingredients, _work_out_ingredients, REFUSAL_JOINERS, _on_a_list_already_ruled_out,
    diet_exclusions, WITHOUT, _is_food_list, ingredients, negated_ingredients, _mentions,
    cooked_ingredients, _VEG_WORDS, _VEG_GUESTS, _VEG_ELSEWHERE, _SELF_VEG, _veg_dinner, _diet,
    _diet_from_turns, _BARE_NO_CUES, SHORTAGE_AFTER, _refused_foods, DINNER_ASK_WORDS,
    NOT_A_DINNER_LIMIT, DINNER_NAMED, LUNCH_AND_BREAKFAST, _STAND_IN_USE, _REFUSAL_CUES,
    _REFUSAL_JOINERS, _REFUSAL_FILLER, _dishes_without, _best_dish, SENTENCE, _served_without,
    _without_the_trimmings, dish, _WHAT_IS_IT, _ANY_FOOD_TEXT, _any_food_text, _a_choice_of_foods,
    meal, _meal_texts, _MEAL_TEXTS, _MEAL_METHODS, _TIMING, _BACK_REFERENCE, _WORD, _KEEP_WORDS,
    _KEEP_TIME, _KEEP_TIME_ASK, _COOKING_SENSE, _SPEAKS_OF_KEEPING, _TOTAL_TIME, _RECIPE_STEP,
    _RECIPE_ASK, _RECIPE_ASK_WORDS, _DISH_ON_ITS_OWN_FILLER, _names_nothing_but_the_dish,
    _WANT_PHRASES, _WANT_ACTION, _WANT_TO_COOK, _WANT_TO_LEARN_COOK, _wants_the_dish,
    _RECIPE_NOT_THIS, _recipe_only_when_asked_for_this, _RECIPE_KEEPING, _RECIPE_COOKING,
    _RECIPE_GROWING_WORDS, ANNOUNCED_DISH, _A_POT_ALREADY_MADE, _a_made_pot_is_not_its_recipe,
    _RECIPE_FAULT_WORDS, _alone, _PANTRY_FOODS, names_a_dish, POINT_BACK_BARE, THE_FOOD_OR_THE_MEAL,
    POINT_BACK_OBJECT, _ideas_are_for_something_else, _food_before, pointed, _scaling_reply,
    _TAIL_ENTRIES, asks_a_food_fact, first_plan, follow_up, plan_recent, remembered, wants, _clean,
    _said_words,
)
from ..knowledge_parts.cooking_part_08 import (  # noqa: F401
    _cheap_dinners, _someones_else_can_eat, suits_them, considered, _food_they_avoid,
    _a_swap_not_a_dish, _says_a_food, _the_banned_words, _rewritten_outside_swaps, _uncautioned,
    _nut_swapped, _a_nut_swap_is_safe, fitted_for_the_one_talked_about, names_a_banned_food,
    fits_the_diet, _the_card_without_that_sentence, _recipe_for_unknown_dish, pantry_idea, unusable,
    refused_foods, asks_for_a_stand_in, a_dinner_without, _is_meal_answer, speaks_of_keeping,
    keeping_ask, _the_answer_names_a_food, keeping_followup, timing_followup,
)
