"""Regression coverage for shared state read by split modules."""

import unittest

from bot.memory import meant
from bot.runtime import turn


class SplitRuntime(unittest.TestCase):
    def test_a_repeat_frame_does_not_get_a_second_frame(self):
        memory = {"turns": [{
            "user": "what should i do first",
            "bot": "The thing to do first: measure the board.",
            "module": "chat",
        }]}

        result = turn("i dont follow", memory)

        chat = next(candidate for candidate in result["candidates"] if candidate["module"] == "chat")
        self.assertIn(chat["reply"], meant.SAID_TWICE)

    def test_extended_staples_reach_their_own_recipe(self):
        cases = (
            ("how do i cook beef brisket", "Brisket is a long cook"),
            ("how do i cook lamb kofta", "Kofta is minced lamb"),
        )
        for prompt, opening in cases:
            with self.subTest(prompt=prompt):
                self.assertTrue(turn(prompt, {})["reply"].startswith(opening))
