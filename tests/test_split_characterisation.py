"""Characterisation tests that make a module split checkable.

    python -m unittest tests.test_split_characterisation          # a sample, about two minutes
    PYBOT_FULL=1 python -m unittest tests.test_split_characterisation   # every recorded line

The namespace and probe checks run in an interpreter of their own, with PYTHONHASHSEED=0 and nothing
run before them, so they give the same answer however the tests are ordered.

The expected values live in tests/golden/characterisation.json and are made by
tests/support/record.py on a commit whose behaviour is the one to keep. Three things are compared:

* what the bot replies to a few hundred lines taken from its own source, alone and in runs of three
  that share a memory;
* that every name `bot/compose/fallback.py` and `bot/modules/chat.py` defined is still reachable
  from the same module, with the same signature or the same data, wherever it now lives;
* what each small function in those modules returns for a fixed set of probe lines.

A failure after a change meant to keep behaviour means the change altered a reply, lost a name, or
changed what a function returns. Re-record only when the change to the bot's answers is intended.
"""
import json
import os
import subprocess
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

    @classmethod
    def observed(cls):
        """Namespaces and probes, measured in a fresh interpreter so earlier tests cannot change them."""
        if not hasattr(cls, "_observed"):
            spec = {"namespaces": {m: sorted(v) for m, v in GOLDEN["namespaces"].items()},
                    "probes": {m: sorted(v) for m, v in GOLDEN["probes"].items()}}
            done = subprocess.run([sys.executable, os.path.join(HERE, "support", "record.py"), "observe"],
                                  input=json.dumps(spec), capture_output=True, text=True, cwd=ROOT,
                                  env=dict(os.environ, PYTHONHASHSEED=record.HASH_SEED))
            if done.returncode:
                raise RuntimeError("observe failed:\n" + done.stderr[-2000:])
            cls._observed = json.loads(done.stdout.splitlines()[-1])
        return cls._observed

    def test_1_every_defined_name_is_still_reachable_and_unchanged(self):
        got = self.observed()["namespaces"]
        for name, recorded in GOLDEN["namespaces"].items():
            for member, was in recorded.items():
                with self.subTest(module=name, member=member):
                    self.assertIn(member, got[name], "%s no longer reachable from %s" % (member, name))
                    self.assertEqual(got[name][member], was)

    def test_2_small_functions_return_what_they_did(self):
        got = self.observed()["probes"]
        for name, recorded in GOLDEN["probes"].items():
            for member, was in recorded.items():
                with self.subTest(module=name, member=member):
                    self.assertIn(member, got[name])
                    self.assertEqual(got[name][member], was)

if __name__ == "__main__":
    unittest.main()
