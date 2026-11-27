"""Pin the rows `bot/knowledge/home_craft.entries()` returns, so the list can be cut into parts.

    python -m unittest tests.test_home_craft_rows
    PYTHONHASHSEED=0 python tests/test_home_craft_rows.py record   # rewrite the golden file

`home_craft.entries()` is one expression that builds about 11,000 lines of `entry(...)` rows. The
characterisation tests already pin the names the module defines and what the bot replies, but a row
that went missing or moved down the list would only show if a corpus line happened to reach it. This
test compares every row, in order, with the rows recorded before the list was cut: for each row a
digest of all its fields, where a function (a `guard`, a lambda) counts by its bytecode, constants and
names, not by where it lives or what it is called.

The golden file is tests/golden/home_craft_rows.json.
"""
import hashlib
import json
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(HERE, "support"))

import snapshot  # noqa: E402

GOLDEN = os.path.join(HERE, "golden", "home_craft_rows.json")


def _digest(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _const(c):
    if isinstance(c, types.CodeType):
        return _code(c)
    if isinstance(c, (set, frozenset)):  # iteration order of strings changes with PYTHONHASHSEED
        return type(c).__name__ + "{" + ",".join(sorted(_const(v) for v in c)) + "}"
    if isinstance(c, tuple):
        return "(" + ",".join(_const(v) for v in c) + ")"
    return repr(c)


def _code(code):
    consts = [_const(c) for c in code.co_consts]
    return "code(%s|%s|%s|%s|%s)" % (code.co_code.hex(), code.co_names, code.co_varnames, consts,
                                    code.co_argcount)


def _value(value):
    if isinstance(value, types.FunctionType):
        defaults = [_value(d) for d in (value.__defaults__ or ())]
        return "fn(%s|%s)" % (_code(value.__code__), defaults)
    if isinstance(value, (list, tuple)):
        return type(value).__name__ + "[" + ",".join(_value(v) for v in value) + "]"
    return snapshot._stable_repr(value)


def row_digests(rows):
    """One digest per row: every slot of the Entry, in order."""
    out = []
    for row in rows:
        fields = [(slot, _value(getattr(row, slot, None))) for slot in type(row).__slots__]
        out.append([row.id, _digest(repr(fields))])
    return out


def observed():
    from bot.knowledge import home_craft
    import bot.knowledge.home  # noqa: F401  (home.py is what calls entries(), at its end)

    rows = home_craft.entries()
    return {"count": len(rows), "rows": row_digests(rows)}


class HomeCraftRows(unittest.TestCase):
    def test_every_row_is_the_one_recorded_in_the_same_place(self):
        with open(GOLDEN, encoding="utf-8") as handle:
            golden = json.load(handle)
        now = observed()
        self.assertEqual(now["count"], golden["count"])
        moved = [(i, a, b) for i, (a, b) in enumerate(zip(now["rows"], golden["rows"])) if a != b]
        self.assertEqual(moved, [], "rows that differ from the recorded ones, by position")

    def test_home_still_gets_the_same_rows_in_front_of_its_own(self):
        import bot.knowledge.home as home
        from bot.knowledge import home_craft

        rows = home_craft.entries()
        self.assertEqual([r.id for r in home.ENTRIES[:len(rows)]], [r.id for r in rows])


if __name__ == "__main__":
    if sys.argv[1:] == ["record"]:
        if os.environ.get("PYTHONHASHSEED") != "0":
            raise SystemExit("run with PYTHONHASHSEED=0")
        with open(GOLDEN, "w", encoding="utf-8") as handle:
            json.dump(observed(), handle, indent=0)
            handle.write("\n")
    else:
        unittest.main()
