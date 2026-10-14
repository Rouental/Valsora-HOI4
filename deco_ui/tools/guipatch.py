"""Small, assertive patch helpers for Clausewitz .gui files.

Elements are addressed by name, or by a path of names ("parent/child/name") when a name is not
unique in the file. Every lookup asserts it found exactly one element, so a renamed or removed vanilla
element stops the build instead of silently producing a broken file.
"""
import re

TYPES = (r"(?:containerWindowType|iconType|buttonType|instantTextBoxType|instantTextboxType|textBoxType|"
         r"checkboxType|gridBoxType|gridboxtype|positionType|smoothListboxType|listboxType|editBoxType|"
         r"OverlappingElementsBoxType|overlappingElementsBoxType|extendedScrollbarType|windowType)")


def _block_end(text, start):
    depth = 0
    for j in range(text.index("{", start), len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    raise ValueError("unbalanced braces")


def _strip_comments(text):
    """Same length as text, with comments blanked (so offsets stay valid)."""
    return re.sub(r"#[^\n]*", lambda m: " " * len(m.group(0)), text)


def find_block(text, path, lo=0, hi=None):
    """(start, end) of the element addressed by `path`, searched within text[lo:hi].

    Path segments are element names joined by "/" (any descendant) or ">" (direct child only),
    e.g. "countrypoliticsview>pol_view_bg" or "manage_subjects_window/close_button".
    """
    hi = len(text) if hi is None else hi
    clean = _strip_comments(text)
    segs = re.split(r"([/>])", path)
    names_, seps = segs[0::2], [None] + segs[1::2]
    parent = None
    for i, (name, sep) in enumerate(zip(names_, seps)):
        pat = re.compile(r'\bname\s*=\s*"?' + re.escape(name) + r'"?(?=\s)')
        hits = []
        for m in pat.finditer(clean, lo, hi):
            heads = list(re.finditer(TYPES + r"\s*=\s*\{", clean[lo:m.start()], re.I))
            if not heads:
                continue
            s = lo + heads[-1].start()
            e = _block_end(clean, s)
            inner = clean[clean.index("{", s) + 1:m.start()]
            if inner.count("{") != inner.count("}"):
                continue                     # name belongs to a background or other sub-block
            if sep == ">" and parent is not None:
                between = clean[clean.index("{", parent[0]) + 1:s]
                if between.count("{") != between.count("}"):
                    continue                 # not a direct child
            hits.append((s, e))
        assert len(hits) == 1, (path, name, len(hits))
        parent = hits[0]
        lo, hi = hits[0]
    return parent


def own_region(block):
    """Split a block into (its own attributes, the rest: children + closing brace)."""
    clean = _strip_comments(block)
    body0 = block.index("{") + 1
    m = re.search(TYPES + r"\s*=\s*\{|background\s*=\s*\{", clean[body0:], re.I)
    if m:
        cut = body0 + m.start()
        cut = block.rindex("\n", 0, cut) + 1
    else:
        cut = block.rindex("}")
        cut = block.rindex("\n", 0, cut) + 1 if "\n" in block[:cut] else cut
    return block[:cut], block[cut:]


QUOTED = ("font", "sprite", "Orientation", "text", "spriteType", "quadTextureSprite", "buttonFont")


def fmt_value(key, val):
    if key in ("position", "show_position"):
        return "{ x = %d y = %d }" % val
    if key == "size":
        return "{ width = %s height = %s }" % val
    if key in ("slotsize",):
        return "{ width = %s height = %s }" % val
    if key == "max_slots":
        return "{ x = %s y = %s }" % val
    if isinstance(val, str) and key in QUOTED:
        return '"%s"' % val
    return str(val)


def set_attrs(src, path, **attrs):
    """Set (or add) attributes on the element at `path`. `src` is the whole file (named so that an element
    attribute called `text` can be passed as a keyword)."""
    text = src
    s, e = find_block(text, path)
    block = text[s:e]
    head, rest = own_region(block)
    indent = re.search(r"\n(\s*)name", head).group(1)
    for key, val in attrs.items():
        key_re = {"sprite": r"(?:spriteType|quadTextureSprite)"}.get(key, re.escape(key))
        val_s = fmt_value(key, val)
        line_re = re.compile(r"(\n\s*)(" + key_re + r")(\s*=\s*)(\{[^}]*\}|\"[^\"]*\"|[^\s#]+)", re.IGNORECASE)
        m = line_re.search(_strip_comments(head))
        if m:
            head = head[:m.start()] + m.group(1) + m.group(2) + " = " + val_s + head[m.end():]
        else:
            k = "spriteType" if key == "sprite" else key
            head = head.rstrip() + "\n" + indent + k + " = " + val_s + "\n"
    return text[:s] + head + rest + text[e:]


def remove_attr(text, path, key):
    s, e = find_block(text, path)
    block = text[s:e]
    head, rest = own_region(block)
    head = re.sub(r"\n[ \t]*" + re.escape(key) + r"\s*=\s*(\{[^}]*\}|\"[^\"]*\"|[^\s#]+)[^\n]*", "", head, flags=re.I)
    return text[:s] + head + rest + text[e:]


def set_background(text, path, sprite):
    s, e = find_block(text, path)
    block = text[s:e]
    new, n = re.subn(r'(background\s*=\s*\{[^}]*?(?:quadTextureSprite|spriteType)\s*=\s*)"?[A-Za-z0-9_]+"?',
                     r'\1"%s"' % sprite, block, count=1)
    assert n == 1, path
    return text[:s] + new + text[e:]


def insert_after(text, path, snippet):
    """Insert raw .gui text right after the element addressed by path (same parent)."""
    s, e = find_block(text, path)
    return text[:e] + snippet + text[e:]


def insert_child(text, path, snippet, first=True):
    """Insert raw .gui text as a child of the element addressed by path (first or last child)."""
    s, e = find_block(text, path)
    block = text[s:e]
    head, rest = own_region(block)
    if first:
        return text[:s] + head + snippet + rest + text[e:]
    return text[:e - 1].rstrip() + snippet + "\n" + text[e - 1:]


def check(text):
    clean = _strip_comments(text)
    assert clean.count("{") == clean.count("}"), (clean.count("{"), clean.count("}"))
    return text


def names(text):
    return re.findall(r'\bname\s*=\s*"?([A-Za-z0-9_\-]+)"?', _strip_comments(text))
