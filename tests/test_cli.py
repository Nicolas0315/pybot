"""Tests for the command line in pybot.py. Run from the repository root:

    python -m unittest discover -s tests

They check the command line only, not what PyBot says: the bot's own tests live in the swarm's
repository.
"""
import argparse
import contextlib
import io
import os
import subprocess
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pybot  # noqa: E402


def run(args, stdin=None):
    return subprocess.run([sys.executable, "-m", "pybot"] + args, input=stdin, capture_output=True,
                          text=True, cwd=ROOT, timeout=600)


def chat(typed, **options):
    """Run the interactive chat on these typed lines; return (the prompts shown, the lines printed)."""
    args = argparse.Namespace(prompt=None, interactive=False, seed=None, verbose=False)
    for name, value in options.items():
        setattr(args, name, value)
    typed = iter(typed)
    prompts = []

    def typing(prompt=""):
        prompts.append(prompt)
        try:
            return next(typed)
        except StopIteration:
            raise EOFError

    out = io.StringIO()
    with mock.patch("builtins.input", typing), contextlib.redirect_stdout(out):
        pybot.chat(pybot.load_bot(), args)
    return prompts, out.getvalue().splitlines()


class ChatOpening(unittest.TestCase):
    def test_the_chat_opens_with_one_line_saying_what_pybot_is(self):
        _, lines = chat(["/exit"])
        self.assertEqual(lines[0], "PyBot: a chatbot written in plain Python. No weights, no training, just rules.")
        self.assertIn("/reset", lines[1])


class ChatTurnsAreLabelled(unittest.TestCase):
    def test_the_prompt_is_user_and_every_reply_starts_with_pybot(self):
        prompts, lines = chat(["hello", "how do i descale a kettle", "/exit"])
        self.assertEqual(prompts, ["user: "] * 3)
        replies = [line for line in lines if line.startswith("pybot: ")]
        self.assertEqual(len(replies), 2)
        for reply in replies:
            self.assertGreater(len(reply), len("pybot: "))

    def test_a_first_message_given_with_p_is_shown_as_the_users_turn(self):
        prompts, lines = chat(["/exit"], prompt="hello", interactive=True)
        self.assertIn("user: hello", lines)
        self.assertEqual(sum(line.startswith("pybot: ") for line in lines), 1)
        self.assertEqual(prompts, ["user: "])

    def test_commands_and_empty_lines_get_no_reply(self):
        prompts, lines = chat(["", "/help", "/reset", "/exit"])
        self.assertEqual(len(prompts), 4)
        self.assertFalse(any(line.startswith("pybot: ") for line in lines))
        self.assertIn("New conversation.", lines)

    def test_the_chat_ends_when_input_ends(self):
        prompts, lines = chat(["hello"])
        self.assertEqual(sum(line.startswith("pybot: ") for line in lines), 1)

    def test_verbose_names_the_module_under_the_reply(self):
        _, lines = chat(["hello", "/exit"], verbose=True)
        index = next(i for i, line in enumerate(lines) if line.startswith("pybot: "))
        self.assertRegex(lines[index + 1], r"^\[module: \S+ \| \d+ ms\]$")


class OneShotAndPipeStayPlain(unittest.TestCase):
    def test_p_prints_the_reply_alone(self):
        result = run(["-p", "hello"])
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 1)
        self.assertFalse(lines[0].startswith("pybot: "))

    def test_piped_input_matches_the_bots_own_loop(self):
        typed = "hello\nhow do i descale a kettle\nhow long does that take\n\nthanks\n"
        mine = run(["-s", "0"], stdin=typed)
        theirs = subprocess.run(
            [sys.executable, "-c", "import random; random.seed(0); from bot.__main__ import main; main()"],
            input=typed, capture_output=True, text=True, cwd=ROOT, timeout=600)
        self.assertEqual(mine.returncode, 0)
        self.assertEqual(mine.stdout, theirs.stdout)
        self.assertEqual(len(mine.stdout.splitlines()), 5)


if __name__ == "__main__":
    unittest.main()
