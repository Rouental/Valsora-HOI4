"""A small reader for Paradox script (the `key = value` / `key = { ... }` files of HOI4).

parse(text) returns a list of (key, op, value) entries, where value is a string or, for a
block, another such list. Comments are dropped; quoted strings keep their quotes stripped
but are marked by `Quoted` so callers can tell them apart. Used by scripts/vanilla_sync.py
to read vanilla's files.
"""
import re

TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}]|[<>!?]?=|[<>]|[^\s{}=<>"#?]+|#[^\n]*')


class Quoted(str):
    """A value that was written in quotes."""


def tokens(text):
    for m in TOKEN.finditer(text):
        t = m.group(0)
        if t.startswith("#"):
            continue
        if t.startswith('"'):
            yield Quoted(t[1:-1])
        else:
            yield t


def parse(text):
    toks = list(tokens(text.lstrip("﻿")))
    pos = 0

    def block():
        nonlocal pos
        out = []
        while pos < len(toks):
            t = toks[pos]
            if t == "}":
                pos += 1
                return out
            if pos + 1 < len(toks) and toks[pos + 1] in ("=", "<", ">", "<=", ">=", "!=", "?="):
                key, op = t, toks[pos + 1]
                pos += 2
                if pos < len(toks) and toks[pos] == "{":
                    pos += 1
                    out.append((key, op, block()))
                elif pos < len(toks):
                    out.append((key, op, toks[pos]))
                    pos += 1
            elif t == "{":                       # an anonymous block (lists of blocks)
                pos += 1
                out.append((None, None, block()))
            else:                                # a bare value (lists like `{ 1 2 3 }`)
                out.append((None, None, t))
                pos += 1
        return out

    return block()


def walk(entries, path=()):
    """Every (path, key, op, value) in the tree, depth first; path is the keys above."""
    for key, op, value in entries:
        yield path, key, op, value
        if isinstance(value, list):
            yield from walk(value, path + (key,))


def read(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return parse(f.read())
