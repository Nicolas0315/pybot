"""Call a module's small functions directly and keep a digest of what each returns.

The conversation corpus only reaches a function when a line happens to land on it. This reaches the
rest: every function that takes one required argument, or a line and a memory, is called with a fixed
set of probe lines and its results are folded into one digest per function. A function that raises
is described by the exception's type, so a change from an answer to an error is seen too.
"""
import copy
import hashlib
import inspect
import re
import types

# an int this long is a memory address (id()) when a result shows one; it differs in every process
BIG_INT = re.compile(r"\b\d{9,}\b")
HEX_ADDRESS = re.compile(r" at 0x[0-9a-fA-F]+")

EDGE = ["", " ", "what", "hello", "x" * 400, "my sister has arrived", "i lost my job today",
        "can you help me with my dog", "what is the weather like in paris", "no", "it is not that",
        "i am scared about the results", "thanks so much", "tell me more about it"]


def _digest(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _outcome(call):
    try:
        return BIG_INT.sub("N", HEX_ADDRESS.sub("", repr(call())))
    except BaseException as error:  # a probe line may legitimately raise; the type is the record
        return "!" + type(error).__name__


def probe(module, lines, memory_for, only=None):
    """{function name: digest} for every one- or two-argument function defined in `module`.

    "Defined in" is read from the function's `__module__` (the module itself or a `<module>_...` part)
    when `only` is None, as when recording. After a split the functions live elsewhere, so a check
    passes the names it recorded in `only` and those are looked up on the module whatever their origin.
    """
    out = {}
    for name, value in sorted(vars(module).items()):
        if not isinstance(value, types.FunctionType):
            continue
        if only is not None:
            if name not in only:
                continue
        elif value.__module__ != module.__name__ and not value.__module__.startswith(module.__name__ + "_"):
            continue
        try:
            parameters = [p for p in inspect.signature(value).parameters.values()
                          if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        except (TypeError, ValueError):
            continue
        if len(parameters) == 1:
            results = [_outcome(lambda s=s: value(s)) for s in lines]
        elif len(parameters) == 2 and parameters[1].name in ("memory", "mem"):
            results = [_outcome(lambda s=s: value(s, copy.deepcopy(memory_for(s)))) for s in lines]
        else:
            continue
        out[name] = _digest("\n".join(results))
    return out


def lines_for_probe(sampled):
    return EDGE + list(sampled)
