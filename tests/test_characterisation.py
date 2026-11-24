"""Characterisation tests: pin what the bot says today so refactors can be checked against it.

Run from the repository root:

    python -m unittest discover -s tests

`test_every_module_imports` imports each module under `bot/`; `test_conversation_is_unchanged` replays one
conversation through `bot.runtime.reply` with a shared memory and compares each reply with the text
recorded before the unused-import cleanup. A failure here after a change meant to keep behaviour means
the change altered what the bot says, or broke an import. Re-record the expected lines only when a
change to the bot's answers is intended.
"""
import importlib
import os
import pkgutil
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bot  # noqa: E402
from bot.runtime import reply  # noqa: E402

CONVERSATION = [
    ('hello',
     'Hi there — what do you need?'),
    ('hi there',
     "I haven't got anything for that to point at yet — give me the thing in a few words and I'll answer for it."),
    ('what is your name',
     "No name of my own — call me whatever you like, I'll answer to it. What can I help with?"),
    ('i am vegetarian',
     "I'd do chickpea curry (25 minutes): fry an onion with curry powder, add a tin of chickpeas and a tin of tomatoes and simmer for 15 minutes. Something else that works is a lentil dhal."),
    ('what can i cook',
     "I'd do tomato pasta (20 minutes): fry sliced garlic in olive oil for a minute, add a tin of tomatoes and simmer 10 minutes while the pasta cooks. Something else that works is macaroni cheese."),
    ('i changed my diet',
     "You were vegetarian, so I'll drop that - what does a normal day look like now?"),
    ('my name is sam',
     'Hello Sam! What are we doing today?'),
    ('what is my name',
     'Sam — you told me.'),
    ('tell me a joke',
     "I only know 25 letters of the alphabet. I don't know y."),
    ('how do i boil an egg',
     'Lower eggs into already boiling water: 6 minutes for a runny yolk, 7 for jammy, 9 to 10 for hard boiled. Cool them in cold water for a minute before peeling so the shell comes away cleanly.'),
    ('i feel sad',
     "That sounds rough. If it's been hanging around for a while, talking to someone you trust is worth it."),
    ('thanks',
     'No problem at all.'),
    ('bye',
     'Bye for now!'),
    ("what's the capital of france",
     'Paris.'),
    ('i want to lose weight',
     'Change a few things you can keep doing rather than going on a diet: fill half the plate with vegetables, put protein in every meal so you are not hungry an hour later, swap sugary drinks for water or squash, and walk for half an hour a day. Losing about 0.5 to 1kg a week is the rate that stays off, and the plan that works is the one you would still follow in a year. If you are hungry all the time, or the weight is going on without trying, see a GP.'),
    ('how far is the moon',
     'About 384,400 km (238,900 miles) away on average, which is roughly 30 Earths side by side, and light takes 1.3 seconds to reach us from it. It is drifting about 4cm further away each year.'),
    ('i have a dog',
     "A dog — good to know. What's its name?"),
    ('what should i feed him',
     'As a rough guide, an adult dog eats about 2% of his body weight a day: 400g of food for a 20kg dog, split into two meals. Use the bag or tin as a starting point, then go by condition: you should feel ribs easily but not see them, and see a waist from above. Puppies need more, and a vet can weigh him and give you an exact amount.'),
    ('plan a trip to paris',
     'Paris wants about four full days. Book the first two nights and the last night only, keep one day free in the middle, and sleep near the airport on the way home.'),
    ('help',
     'Work out how many nights you have first, then give each place at least three of them: a base with day trips beats a list of cities, because every move costs you half a day. Book the first two nights and the last night only, keep one day free in the middle, and sleep near the airport on the way home.'),
]


class Characterisation(unittest.TestCase):
    def test_every_module_imports(self):
        for module in pkgutil.walk_packages(bot.__path__, "bot."):
            with self.subTest(module=module.name):
                importlib.import_module(module.name)

    def test_conversation_is_unchanged(self):
        memory = {}
        for asked, expected in CONVERSATION:
            with self.subTest(asked=asked):
                self.assertEqual(" ".join(str(reply(asked, memory)).split()), expected)


if __name__ == "__main__":
    unittest.main()
