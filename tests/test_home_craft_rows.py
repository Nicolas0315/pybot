"""Pin the rows `bot/knowledge/home_craft.entries()` returns, so the list can be cut into parts.

    python -m unittest tests.test_home_craft_rows
    PYTHONHASHSEED=0 python tests/test_home_craft_rows.py record   # rewrite the golden file

`home_craft.entries()` is one expression that builds about 11,000 lines of `entry(...)` rows. The
characterisation tests already pin the names the module defines and what the bot replies, but a row
that went missing or moved down the list would only show if a corpus line happened to reach it. This
test compares every row, in order, with the rows recorded before the list was cut: for each row a
digest of all its fields, with functions represented by their source syntax and captured values.
Source positions and interpreter bytecode do not enter the digest.

The golden file is tests/golden/home_craft_rows.json. Record it against the rows to preserve.
"""
import ast
import hashlib
import json
import os
import sys
import types
import unittest
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(HERE, "support"))

import snapshot  # noqa: E402

GOLDEN = os.path.join(HERE, "golden", "home_craft_rows.json")


def _digest(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _syntax(value):
    if isinstance(value, ast.AST):
        # New Python versions can add fields for syntax that this node does not use.
        fields = tuple((name, _syntax(item)) for name, item in ast.iter_fields(value)
                       if item is not None and item != [] and (name, item) != ("is_lazy", 0))
        return type(value).__name__, fields
    if isinstance(value, list):
        return [_syntax(item) for item in value]
    return value


@lru_cache(maxsize=None)
def _function_nodes(filename):
    with open(filename, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=filename)
    nodes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Lambda):
            key = node.lineno, "<lambda>"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.decorator_list[0] if node.decorator_list else node
            key = first.lineno, node.name
        else:
            continue
        nodes.setdefault(key, []).append(node)
    return nodes


def _value(value):
    if isinstance(value, types.FunctionType):
        code = value.__code__
        node, = _function_nodes(code.co_filename)[code.co_firstlineno, value.__name__]
        captured = tuple(cell.cell_contents for cell in value.__closure__ or ())
        return "fn(%r|%s|%s|%s)" % (_syntax(node), _value(value.__defaults__),
                                    _value(value.__kwdefaults__), _value(captured))
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
        self.assertEqual(row_digests(home.ENTRIES[:len(rows)]), row_digests(rows))


if __name__ == "__main__":
    if sys.argv[1:] == ["record"]:
        if os.environ.get("PYTHONHASHSEED") != "0":
            raise SystemExit("run with PYTHONHASHSEED=0")
        with open(GOLDEN, "w", encoding="utf-8") as handle:
            json.dump(observed(), handle, indent=0)
            handle.write("\n")
    else:
        unittest.main()
