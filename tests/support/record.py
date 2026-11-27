"""Record the golden file the split-characterisation tests compare against.

    python tests/support/record.py            # writes tests/golden/characterisation.json

Run it on a commit whose behaviour is the one to keep, never after a change meant to alter the
bot's answers unless the new answers are the intended ones. It records three things:

* replies: a digest of the bot's reply to each corpus line, alone and in runs of three that share a
  memory, so lines that read the earlier turns are covered;
* namespaces: for each module named in MODULES, what every name the module's own source defines
  looks like (signature, or a digest of the data), so a split must leave them reachable;
* probes: a digest of what each small function in those modules returns for a fixed set of lines.
"""
import ast
import hashlib
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import clock  # noqa: E402
import corpus  # noqa: E402
import probe  # noqa: E402
import snapshot  # noqa: E402

MODULES = ["bot.compose.fallback", "bot.modules.chat",
           "bot.memory.store_replies", "bot.modules.answers", "bot.knowledge.home_craft", "bot.memory.facts",
           "bot.memory.topics", "bot.knowledge.lookup", "bot.understanding.normalize", "bot.memory.ack",
           "bot.compose.verdict", "bot.memory.repeat", "bot.knowledge.maths", "bot.modules.arbiter",
           "bot.compose.fallback_chain", "bot.knowledge.cooking", "bot.modules.memory_store",
           "bot.understanding.kinds"]
SINGLES = 800
TRIPLES = 300
PROBE_LINES = 40
GOLDEN = os.path.join(ROOT, "tests", "golden", "characterisation.json")
# Filled in on first use, so what they hold depends on which line the bot has already read.
LAZY = {"_VENUE_RE", "_A_MY_PERSON", "_ACK_PATTERN", "_ANY_FOOD_TEXT", "_BAKE_ALIASES", "_FOODS_SAID",
        "_PANTRY_AS_WORDS", "_ASK_FRAME_FORMS", "_FRAME_PRONOUN_FORMS", "_FRAME_STARTS", "_TAIL_ASK_WORDS",
        "_TAKE_OFF", "_PEOPLE", "_CARD_OPENINGS", "_NAME_WORDS", "ACK_POOL", "_FRAME", "_SOUND_CUES",
        "_A_WORD_THE_BOT_WRITES"}
# Sets and the patterns built from them come out in a different order in every process unless the
# hash seed is fixed, so the namespace and probe records are made and checked with this seed.
HASH_SEED = "0"


def digest(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def said(runtime_reply, line, memory):
    return digest(" ".join(str(runtime_reply(line, memory)).split()))


def defined_names(module):
    """Names the module's own source binds at top level (defs, classes, assignments)."""
    with open(module.__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for sub in ast.walk(target):
                    if isinstance(sub, ast.Name):
                        names.add(sub.id)
    return sorted(names)


def observe(spec):
    """What the namespace and probe checks compare, measured in this process.

    `spec` is {"namespaces": {module: [names]}, "probes": {module: [names]}}. The order is the one the
    record is made in: every namespace first, while nothing has run and the lazily filled caches are
    empty, then every probe. Run it in a process of its own (`record.py observe`, spec on stdin), so what
    ran earlier in a test run cannot change the answer.
    """
    clock.freeze()
    from bot.runtime import reply
    probe_lines = probe.lines_for_probe(corpus.sample(PROBE_LINES, seed=7))
    memory_for = memory_factory(reply)
    modules = {name: importlib.import_module(name) for name in dict.fromkeys(list(spec["namespaces"]) + list(spec["probes"]))}
    namespaces = {}
    for name in spec["namespaces"]:
        wanted = set(spec["namespaces"][name])
        namespaces[name] = {n: d for n, d in snapshot.describe(modules[name], skip=LAZY).items() if n in wanted}
    probes = {name: probe.probe(modules[name], probe_lines, memory_for, only=set(spec["probes"][name]))
              for name in spec["probes"]}
    return {"namespaces": namespaces, "probes": probes}


def memory_factory(runtime_reply):
    cache = {}

    def memory_for(line):
        if line not in cache:
            memory = {}
            runtime_reply(line, memory)
            cache[line] = memory
        return cache[line]
    return memory_for


def record(only=None, modules=None):
    """Write the golden file. `only` is a set of {"replies", "namespaces"} to refresh in an existing file."""
    if os.environ.get("PYTHONHASHSEED") != HASH_SEED:
        raise SystemExit("run with PYTHONHASHSEED=%s so sets and the patterns built from them keep one order" % HASH_SEED)
    clock.freeze()
    from bot.runtime import reply
    if only and os.path.exists(GOLDEN):
        with open(GOLDEN, encoding="utf-8") as handle:
            golden = json.load(handle)
    else:
        only = None
        golden = {"seed": 20261124, "singles": [], "triples": [], "namespaces": {}, "probes": {}}
    # One order for recording and for checking: every namespace first, while nothing has run and the
    # lazily filled caches are still empty, then every probe, then the replies.
    probe_lines = probe.lines_for_probe(corpus.sample(PROBE_LINES, seed=7))
    memory_for = memory_factory(reply)
    chosen = modules or MODULES
    imported = [importlib.import_module(name) for name in chosen]
    for name, module in zip(chosen, imported):
        names = defined_names(module)
        described = snapshot.describe(module)
        golden["namespaces"][name] = {n: described[n] for n in names if n in described and n not in LAZY}
    for name, module in zip(chosen, imported):
        golden["probes"][name] = probe.probe(module, probe_lines, memory_for)
    if only is None or "replies" in only:
        lines = corpus.sample(SINGLES + TRIPLES * 3)
        golden["singles"] = [said(reply, line, {}) for line in lines[:SINGLES]]
        golden["triples"] = []
        rest = lines[SINGLES:]
        for index in range(0, len(rest), 3):
            memory = {}
            golden["triples"].append([said(reply, line, memory) for line in rest[index:index + 3]])
    os.makedirs(os.path.dirname(GOLDEN), exist_ok=True)
    with open(GOLDEN, "w", encoding="utf-8") as handle:
        json.dump(golden, handle, sort_keys=True, indent=0)
        handle.write("\n")
    return golden


if __name__ == "__main__" and sys.argv[1:] == ["observe"]:
    print(json.dumps(observe(json.load(sys.stdin))))
elif __name__ == "__main__":
    only_modules = None
    args = []
    for a in sys.argv[1:]:
        if a.startswith("modules="):
            only_modules = a.split("=", 1)[1].split(",")
        else:
            args.append(a)
    result = record(set(args) or None, only_modules)
    print("singles", len(result["singles"]), "triples", len(result["triples"]),
          {k: len(v) for k, v in result["namespaces"].items()},
          {k: len(v) for k, v in result["probes"].items()})
