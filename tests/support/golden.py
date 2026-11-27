"""Read the pre-refactor characterisation data for this Python version."""

import json
import os
import sys


def load(path):
    with open(path, encoding="utf-8") as handle:
        golden = json.load(handle)

    if sys.version_info >= (3, 11):
        return golden

    stem, suffix = os.path.splitext(path)
    with open(stem + "-py38-310" + suffix, encoding="utf-8") as handle:
        legacy = json.load(handle)

    recordings = [legacy]
    if sys.version_info < (3, 9):
        recordings.append(legacy.get("py38", {}))
    for differences in recordings:
        for section in ("singles", "triples"):
            for index, expected in differences.get(section, {}).items():
                golden[section][int(index)] = expected
        for section in ("namespaces", "probes"):
            for module, members in differences.get(section, {}).items():
                golden[section][module].update(members)
    return golden
