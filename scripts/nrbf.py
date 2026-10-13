"""Read the .NET BinaryFormatter (MS-NRBF) object graph inside a paint.net .pdn.

Only what paint.net documents use. parse() returns every record with its byte span, so
writepdn.py can patch a field or copy a record. A record is (kind, start, end, info):
    "class"     a class with its member names and types (info: object id, class name,
                metadata id, member values), or "classid" (the same, reusing a class
                defined earlier); a member value is ("prim", bytes, offset) when stored
                inline, else ("rec", record index)
    "string"    (object id, text)        "ref"   object id
    "null"/"nulls"  how many             "objarray"  (object id, length, record indices)
    "binarray"  (object id, lengths, element type, record indices)
plus "header", "library", "primarray", "primtyped" and "end".
"""
import struct

PRIM_SIZE = {1: 1, 2: 1, 6: 8, 7: 2, 8: 4, 9: 8, 10: 1, 11: 4, 12: 8, 13: 8, 14: 2, 15: 4, 16: 8}


class Graph:
    def __init__(self, buf, start):
        """buf: the file's bytes; start: where the NRBF stream begins (after paint.net's
        two-byte marker that follows the XML header)."""
        self.b, self.p = buf, start
        self.meta = {}      # metadata id -> (class name, member names, types, extra type info)
        self.records = []
        self.objects = {}   # object id -> record index
        while self.records == [] or self.records[-1][0] != "end":
            self.record()

    # ------------------------------------------------------------------ primitives
    def u8(self):
        v = self.b[self.p]
        self.p += 1
        return v

    def i32(self):
        v = struct.unpack_from("<i", self.b, self.p)[0]
        self.p += 4
        return v

    def lps(self):  # length-prefixed string, 7-bit encoded length
        n, shift = 0, 0
        while True:
            c = self.u8()
            n |= (c & 0x7F) << shift
            shift += 7
            if not c & 0x80:
                break
        s = self.b[self.p:self.p + n].decode("utf-8")
        self.p += n
        return s

    def prim(self, t):
        if t in PRIM_SIZE:
            raw = self.b[self.p:self.p + PRIM_SIZE[t]]
            self.p += PRIM_SIZE[t]
            return raw
        if t == 18:
            return self.lps()
        if t == 3:  # a char: one UTF-8 character
            c = self.b[self.p]
            n = 1 if c < 0x80 else 2 if c < 0xE0 else 3 if c < 0xF0 else 4
            raw = self.b[self.p:self.p + n]
            self.p += n
            return raw
        raise ValueError(f"primitive type {t}")

    def typeinfo(self, types):
        extra = []
        for t in types:
            if t in (0, 7):
                extra.append(self.u8())
            elif t == 3:
                extra.append(self.lps())
            elif t == 4:
                extra.append((self.lps(), self.i32()))
            else:
                extra.append(None)
        return extra

    # ------------------------------------------------------------------ records
    def add(self, kind, start, info):
        self.records.append((kind, start, self.p, info))
        return len(self.records) - 1

    def members(self, mid):
        vals = []
        for t, x in zip(self.meta[mid][2], self.meta[mid][3]):
            if t == 0:
                at = self.p
                vals.append(("prim", self.prim(x), at))
            else:
                vals.append(("rec", self.record()))
        return vals

    def elements(self, n):
        items, got = [], 0
        while got < n:
            j = self.record()
            kind, _, _, info = self.records[j]
            items.append(j)
            got += info if kind == "nulls" else 1
        return items

    def record(self):
        s = self.p
        k = self.u8()
        if k == 0x00:
            self.p += 16
            return self.add("header", s, None)
        if k == 0x0C:
            lid = self.i32()
            return self.add("library", s, (lid, self.lps()))
        if k in (0x04, 0x05):  # (System)ClassWithMembersAndTypes
            oid, name = self.i32(), self.lps()
            mn = [self.lps() for _ in range(self.i32())]
            types = [self.u8() for _ in mn]
            extra = self.typeinfo(types)
            if k == 0x05:
                self.i32()  # library id
            self.meta[oid] = (name, mn, types, extra)
            i = self.add("class", s, None)
            vals = self.members(oid)
            self.records[i] = ("class", s, self.p, (oid, name, oid, vals))
            self.objects[oid] = i
            return i
        if k == 0x01:  # ClassWithId
            oid, mid = self.i32(), self.i32()
            i = self.add("classid", s, None)
            vals = self.members(mid)
            self.records[i] = ("classid", s, self.p, (oid, self.meta[mid][0], mid, vals))
            self.objects[oid] = i
            return i
        if k == 0x06:
            oid = self.i32()
            i = self.add("string", s, (oid, self.lps()))
            self.objects[oid] = i
            return i
        if k == 0x09:
            return self.add("ref", s, self.i32())
        if k == 0x0A:
            return self.add("null", s, 1)
        if k == 0x0D:
            return self.add("nulls", s, self.u8())
        if k == 0x0E:
            return self.add("nulls", s, self.i32())
        if k == 0x08:
            t = self.u8()
            return self.add("primtyped", s, (t, self.prim(t)))
        if k == 0x0F:
            oid, n, t = self.i32(), self.i32(), self.u8()
            self.p += n * PRIM_SIZE[t]
            i = self.add("primarray", s, (oid, n, t))
            self.objects[oid] = i
            return i
        if k in (0x10, 0x11):  # ArraySingleObject / ArraySingleString
            oid, n = self.i32(), self.i32()
            i = self.add("objarray", s, None)
            self.records[i] = ("objarray", s, None, (oid, n, self.elements(n)))
            self.records[i] = ("objarray", s, self.p, self.records[i][3])
            self.objects[oid] = i
            return i
        if k == 0x07:  # BinaryArray
            oid, at, rank = self.i32(), self.u8(), self.i32()
            lens = [self.i32() for _ in range(rank)]
            if at in (3, 4, 5):
                [self.i32() for _ in range(rank)]
            t = self.u8()
            x = self.typeinfo([t])[0]
            total = 1
            for v in lens:
                total *= v
            i = self.add("binarray", s, None)
            items = []
            if t == 0:
                for _ in range(total):
                    self.prim(x)
            else:
                items = self.elements(total)
            self.records[i] = ("binarray", s, self.p, (oid, lens, t, items))
            self.objects[oid] = i
            return i
        if k == 0x0B:
            return self.add("end", s, None)
        raise ValueError(f"unknown record type {k:#x} at byte {s}")

    def meta_id(self, name):
        return next(m for m, v in self.meta.items() if v[0] == name)
