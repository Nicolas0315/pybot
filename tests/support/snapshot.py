"""Describe a module's namespace so a split can be checked against it.

`describe(module)` returns one short string per public-or-private name in the module: the kind of
thing it is, and for functions the signature, for plain data a digest of its value. Splitting a
module into several files must leave every name still reachable from the original module with the
same signature and the same data, so the description before and after must be equal.

A regular expression is described by its pattern and flags, a function by its signature and its
defaults, a class by its bases' names and its own members, anything else by a digest of `repr`.
Objects whose `repr` carries a memory address (a bare `object()`, a lambda) are described by kind
only, since the address changes from run to run.
"""
import hashlib
import inspect
import re
import types

ADDRESS = re.compile(r" at 0x[0-9a-fA-F]+")
# an int this big is a memory address (id()), not a number the bot means
ADDRESS_FLOOR = 10 ** 8
BIG_INT = re.compile(r"\b\d{9,}\b")


def _digest(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _stable_repr(value, depth=0):
    if depth > 6:
        return "..."
    if isinstance(value, re.Pattern):
        return "re(%r,%d)" % (value.pattern, value.flags)
    if isinstance(value, (str, bytes, int, float, bool, type(None))):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return type(value).__name__ + "[" + ",".join(_stable_repr(v, depth + 1) for v in value) + "]"
    if isinstance(value, (set, frozenset)):
        return type(value).__name__ + "{" + ",".join(sorted(_stable_repr(v, depth + 1) for v in value)) + "}"
    if isinstance(value, dict):
        # a dict keyed by id() has keys that change with every process; only its values are kept
        if value and all(isinstance(k, int) and not isinstance(k, bool) and k >= ADDRESS_FLOOR for k in value):
            return "idkeyed{" + ",".join(sorted(_stable_repr(v, depth + 1) for v in value.values())) + "}"
        items = sorted((_stable_repr(k, depth + 1), _stable_repr(v, depth + 1)) for k, v in value.items())
        return "{" + ",".join("%s:%s" % pair for pair in items) + "}"
    if isinstance(value, types.FunctionType):
        return "fn:" + value.__name__
    text = repr(value)
    # "<bot.x.y.Name object>": the module the class lives in is not part of what the object is
    text = re.sub(r"<(?:[A-Za-z_][\w]*\.)+([A-Za-z_]\w*) object>", r"<\1 object>", ADDRESS.sub("", text))
    return BIG_INT.sub("N", text)


def _describe_one(name, value):
    if isinstance(value, types.ModuleType):
        return "module"
    if isinstance(value, types.FunctionType):
        try:
            signature = str(inspect.signature(value))
        except (TypeError, ValueError):
            signature = "?"
        return "function %s%s" % (value.__name__, signature)
    if inspect.isclass(value):
        members = sorted(key for key in vars(value) if not key.startswith("__"))
        return "class %s(%s) %s" % (value.__name__, ",".join(b.__name__ for b in value.__bases__), ",".join(members))
    return "%s %s" % (type(value).__name__, _digest(_stable_repr(value)))


def describe(module, skip=()):
    """{name: description} for every attribute of `module`, minus dunders and `skip`."""
    out = {}
    for name in sorted(vars(module)):
        if name.startswith("__") and name.endswith("__"):
            continue
        if name in skip:
            continue
        out[name] = _describe_one(name, vars(module)[name])
    return out
