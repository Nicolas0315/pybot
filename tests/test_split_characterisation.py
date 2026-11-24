"""Characterisation tests that make a module split checkable.

    PYTHONHASHSEED=0 python -m unittest tests.test_split_characterisation          # a sample, about a minute
    PYTHONHASHSEED=0 PYBOT_FULL=1 python -m unittest tests.test_split_characterisation   # every recorded line

Without PYTHONHASHSEED=0 the namespace and probe checks are skipped (the reply checks still run).

The expected values live in tests/golden/characterisation.json and are made by
tests/support/record.py on a commit whose behaviour is the one to keep. Three things are compared:

* what the bot replies to a few hundred lines taken from its own source, alone and in runs of three
  that share a memory;
* that every name `bot/compose/fallback.py` and `bot/modules/chat.py` defined is still reachable
  from the same module, with the same signature or the same data, wherever it now lives;
* what each small function in those modules returns for a fixed set of probe lines.

The tests are numbered because the order matters: the namespace check must run before anything has
warmed the lazily filled caches, then the probes, then the replies, the same order the record is made in.

A failure after a change meant to keep behaviour means the change altered a reply, lost a name, or
changed what a function returns. Re-record only when the change to the bot's answers is intended.
"""
import importlib
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(HERE, "support"))

import clock  # noqa: E402
import corpus  # noqa: E402
import probe  # noqa: E402
import record  # noqa: E402
import snapshot  # noqa: E402
clock.freeze()  # the bot says the date and the time; the recorded replies were made at this moment
from bot.runtime import reply  # noqa: E402

FULL = bool(os.environ.get("PYBOT_FULL"))
SEEDED = os.environ.get("PYTHONHASHSEED") == record.HASH_SEED
NEEDS_SEED = unittest.skipUnless(SEEDED, "set PYTHONHASHSEED=%s: sets and the patterns built from them vary otherwise" % record.HASH_SEED)
SAMPLE_SINGLES = 150
SAMPLE_TRIPLES = 50

with open(record.GOLDEN, encoding="utf-8") as handle:
    GOLDEN = json.load(handle)


class SplitCharacterisation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        total = record.SINGLES + record.TRIPLES * 3
        cls.lines = corpus.sample(total, seed=GOLDEN["seed"])

    def test_corpus_is_the_one_recorded(self):
        self.assertEqual(len(GOLDEN["singles"]), record.SINGLES)
        self.assertEqual(len(GOLDEN["triples"]), record.TRIPLES)

    def test_4_single_lines_get_the_recorded_reply(self):
        count = record.SINGLES if FULL else SAMPLE_SINGLES
        for line, expected in list(zip(self.lines, GOLDEN["singles"]))[:count]:
            with self.subTest(line=line):
                self.assertEqual(record.said(reply, line, {}), expected)

    def test_3_runs_of_three_get_the_recorded_replies(self):
        rest = self.lines[record.SINGLES:]
        count = record.TRIPLES if FULL else SAMPLE_TRIPLES
        for index in range(count):
            asked = rest[index * 3:index * 3 + 3]
            memory = {}
            with self.subTest(first=asked[0]):
                got = [record.said(reply, line, memory) for line in asked]
                self.assertEqual(got, GOLDEN["triples"][index])

    @NEEDS_SEED
    def test_1_every_defined_name_is_still_reachable_and_unchanged(self):
        for name, recorded in GOLDEN["namespaces"].items():
            module = importlib.import_module(name)
            described = snapshot.describe(module, skip=record.LAZY)
            for member, was in recorded.items():
                with self.subTest(module=name, member=member):
                    self.assertIn(member, described, "%s no longer reachable from %s" % (member, name))
                    self.assertEqual(described[member], was)

    @NEEDS_SEED
    def test_2_small_functions_return_what_they_did(self):
        lines = probe.lines_for_probe(corpus.sample(record.PROBE_LINES, seed=7))
        memory_for = record.memory_factory(reply)
        for name, recorded in GOLDEN["probes"].items():
            module = importlib.import_module(name)
            got = probe.probe(module, lines, memory_for, only=set(recorded))
            for member, was in recorded.items():
                with self.subTest(module=name, member=member):
                    self.assertIn(member, got)
                    self.assertEqual(got[member], was)


if __name__ == "__main__":
    unittest.main()
