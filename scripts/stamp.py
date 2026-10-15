"""Skip a build step whose inputs haven't changed (2026-10-15, the author: "find ways to improve and speed up the
modding process without decreasing quality").

    python3 scripts/stamp.py fresh read_layers    exit 0 if read_layers' inputs are as when it last ran, and its
                                                  outputs are there; 1 otherwise
    python3 scripts/stamp.py save read_layers     after it ran: remember its inputs

run_all.sh uses it for read_layers.py, a minute of a build, whose inputs (the decoded .pdn layers, the names and the
Gazetteer's facts) change only when the map does. The stamp is generous on purpose: the step's script and every module
of scripts/ it imports (followed through their imports), any file directly in source/, in source/palettes/ or in the
Gazetteer's folder (source/gazetteer/, or GAZETTEER_DIR's); the decoded layers count by size and time (they are
gigabytes). FORCE=1 in the environment always reruns.
"""
import hashlib
import os
import sys
from pathlib import Path


def imports(script):
    """the script and every module of scripts/ it imports, followed through their own imports"""
    import re
    seen, todo = set(), [Path("scripts") / script]
    while todo:
        f = todo.pop()
        if f in seen or not f.exists():
            continue
        seen.add(f)
        for m in re.finditer(r"^\s*(?:from\s+([A-Za-z_]\w*)\s+import|import\s+([A-Za-z_][\w ,]*))", f.read_text(encoding="utf-8"), re.M):
            for name in (m.group(1) or m.group(2)).replace(" as ", " ").replace(",", " ").split():
                todo.append(Path("scripts") / f"{name}.py")
    return sorted(seen)


STEPS = {
    "read_layers": dict(
        inputs=lambda: imports("read_layers.py") + [Path("scripts/stamp.py")]
        + sorted(p for p in Path("source").glob("*") if p.is_file()) + sorted(Path("source/palettes").glob("*"))
        + sorted(Path(os.environ.get("GAZETTEER_DIR", "source/gazetteer")).glob("*.json")),
        stat=lambda: sorted(Path("work/pdn_game").glob("*")),
        outputs=["work/provinces.npz", "work/regions.npz", "work/regions.json", "work/world.npz"]),
}


def digest(step):
    s = STEPS[step]
    h = hashlib.sha256(os.environ.get("GAZETTEER_DIR", "").encode())
    for p in s["inputs"]():
        h.update(str(p).encode())
        h.update(p.read_bytes())
    for p in s["stat"]():
        st = p.stat()
        h.update(f"{p}|{st.st_size}|{st.st_mtime_ns}".encode())
    return h.hexdigest()


def main():
    cmd, step = sys.argv[1], sys.argv[2]
    f = Path(f"work/.stamp_{step}")
    if cmd == "fresh":
        ok = (not os.environ.get("FORCE") and f.exists() and all(Path(o).exists() for o in STEPS[step]["outputs"])
              and f.read_text() == digest(step))
        sys.exit(0 if ok else 1)
    if cmd == "save":
        f.write_text(digest(step))


if __name__ == "__main__":
    main()
