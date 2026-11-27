"""Build the prompt corpus for the characterisation tests.

The bot's source is full of short lowercase phrases: the words and idioms its modules listen for.
Lifted out as lines, they exercise far more branches than a hand-written list. The corpus is the
same on every run (sorted, then sampled with a fixed seed), so a recorded answer can be compared
with the one given later.
"""
import ast
import os
import random
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LINE = re.compile(r"^[a-z][a-z' ?]{5,60}$")


def harvest(root=ROOT):
    found = set()
    for folder, _dirs, files in os.walk(os.path.join(root, "bot")):
        for name in files:
            if not name.endswith(".py"):
                continue
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                tree = ast.parse(handle.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    text = " ".join(node.value.split())
                    if LINE.match(text) and 2 <= len(text.split()) <= 9:
                        found.add(text)
    return sorted(found)


def sample(count, seed=20261124, root=ROOT):
    lines = harvest(root)
    random.Random(seed).shuffle(lines)
    return lines[:count]
