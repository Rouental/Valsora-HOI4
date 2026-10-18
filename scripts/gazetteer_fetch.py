"""Read the Gazetteer's atlas straight from its Firestore (the author, 2026-10-18: "In the future you need a way to read
the website directly"), into the same file as Owner tools > Save every nation as a file, for `gazetteer.py import`.

It reads as a Google service account of the author's Firebase project (valsora-hoi4) with the Cloud Datastore Viewer
role: it can read everything and change nothing, and the site's rules, which keep each nation behind its password,
don't apply to it, so it reads owner/keys and through the passwords every nation's folder (n/<TAG>/<key>/..., the key
as the page makes it: keyFor in gazetteer.html). Its key, the JSON file Google gives for it, is the environment's
secret GAZETTEER_SERVICE_ACCOUNT (the JSON itself) or a file named by GAZETTEER_SERVICE_ACCOUNT_FILE; it never goes
into the repository or into work/ (the token is signed by openssl from a temporary file, deleted at once).

    python3 scripts/gazetteer_fetch.py [OUT]      # default work/gazetteer_in/valsora-gazetteer-all-<UTC time>.json
    python3 scripts/gazetteer.py import OUT

GAZETTEER_FIRESTORE_URL points it at another server (tests/gazetteer/fetch.py runs it against a stand-in).
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT = json.loads(Path("source/gazetteer_site/firebase-config.json").read_text())["projectId"]
FIRESTORE = os.environ.get("GAZETTEER_FIRESTORE_URL", "https://firestore.googleapis.com/v1")
SCOPE = "https://www.googleapis.com/auth/datastore"
# the page's KINDS (gazetteer.html): a nation's facts, one document each
KINDS = ("states", "provinces", "cities", "rivers", "rails", "politics", "flags", "people", "about", "suggest",
         "releasables")


def service_account():
    raw = os.environ.get("GAZETTEER_SERVICE_ACCOUNT")
    if not raw and os.environ.get("GAZETTEER_SERVICE_ACCOUNT_FILE"):
        raw = Path(os.environ["GAZETTEER_SERVICE_ACCOUNT_FILE"]).read_text()
    if not raw:
        sys.exit("no service account: set GAZETTEER_SERVICE_ACCOUNT (the key's JSON) or GAZETTEER_SERVICE_ACCOUNT_FILE "
                 "(docs/GAZETTEER_INTERNALS.md, 'Reading the site directly')")
    sa = json.loads(raw)
    for k in ("client_email", "private_key", "token_uri"):
        if k not in sa:
            sys.exit(f"the service account's key has no {k}")
    return sa


def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def sign(private_key, data):
    """RS256 with openssl (the cryptography package isn't usable everywhere this runs)"""
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as f:
        os.chmod(f.name, 0o600)
        f.write(private_key)
    try:
        return subprocess.run(["openssl", "dgst", "-sha256", "-sign", f.name], input=data, capture_output=True,
                              check=True).stdout
    finally:
        os.unlink(f.name)


def token(sa):
    now = int(time.time())
    head = b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = b64(json.dumps({"iss": sa["client_email"], "scope": SCOPE, "aud": sa["token_uri"], "iat": now,
                             "exp": now + 3600}).encode())
    jwt = f"{head}.{claims}"
    jwt += "." + b64(sign(sa["private_key"], jwt.encode()))
    body = urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                                   "assertion": jwt}).encode()
    with urllib.request.urlopen(urllib.request.Request(sa["token_uri"], data=body), timeout=30) as r:
        return json.load(r)["access_token"]


def value(v):
    """a Firestore REST value as plain JSON"""
    if "mapValue" in v:
        return {k: value(x) for k, x in (v["mapValue"].get("fields") or {}).items()}
    if "arrayValue" in v:
        return [value(x) for x in v["arrayValue"].get("values") or []]
    if "integerValue" in v:
        return int(v["integerValue"])
    if "doubleValue" in v:
        return float(v["doubleValue"])
    if "booleanValue" in v:
        return v["booleanValue"]
    if "nullValue" in v:
        return None
    for k in ("stringValue", "timestampValue", "referenceValue", "bytesValue"):
        if k in v:
            return v[k]
    if "geoPointValue" in v:
        return v["geoPointValue"]
    raise ValueError(f"a Firestore value of an unknown kind: {list(v)}")


class Store:
    def __init__(self, bearer):
        self.bearer = bearer
        self.base = f"{FIRESTORE}/projects/{PROJECT}/databases/(default)/documents"

    def get(self, url):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.bearer}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise SystemExit(f"Firestore answered {e.code} for {url.split('/documents/')[-1]}: {e.read()[:300]!r}")

    def doc(self, path):
        d = self.get(f"{self.base}/{urllib.parse.quote(path)}")
        return {k: value(v) for k, v in (d or {}).get("fields", {}).items()} if d else None

    def folder(self, path):
        """{document id: fields} of a collection, every page"""
        out, page = {}, None
        while True:
            q = {"pageSize": 300, **({"pageToken": page} if page else {})}
            d = self.get(f"{self.base}/{urllib.parse.quote(path)}?{urllib.parse.urlencode(q)}") or {}
            for doc in d.get("documents", []):
                out[doc["name"].rsplit("/", 1)[1]] = {k: value(v) for k, v in doc.get("fields", {}).items()}
            page = d.get("nextPageToken")
            if not page:
                return out


def norm_pw(s):  # the page's normPw
    s = re.sub(r"-+", "-", re.sub(r"[\s_.,]+", "-", str(s or "").lower()))
    return s.strip("-")


def key_for(tag, pw):  # the page's keyFor
    return hashlib.sha256(f"valsora-gazetteer|{tag}|{norm_pw(pw)}".encode()).hexdigest()[:32]


def compact(o):  # the page's compact: no nulls, no empty objects
    if not isinstance(o, dict):
        return o
    out = {}
    for k, v in o.items():
        if v is None:
            continue
        c = compact(v)
        if isinstance(c, dict) and not c:
            continue
        out[k] = c
    return out


def fetch(store):
    keys = store.doc("owner/keys") or {}
    nations = {}
    for tag in sorted(keys):
        docs = store.folder(f"n/{tag}/{key_for(tag, keys[tag])}")
        facts, meta, requests, images = {}, {}, [], {}
        for did, v in docs.items():  # as the page's saveAllFile sorts them
            if did in KINDS:
                facts[did] = compact(v)
            elif did == "meta":
                meta = compact({k: v.get(k) for k in ("status", "notes", "updatedAt", "editors")})
            elif v.get("t") == "req":
                requests.append({**v, "id": did})
            elif v.get("t") == "img":
                images[did[4:]] = {k: v.get(k) for k in ("data", "w", "h", "name")}
        nations[tag] = {"facts": facts, "meta": meta, "requests": requests, "images": images}
    return {"gazetteer": 2, "saved": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "planned": store.doc("planned/list") or {}, "unlock": store.doc("planned/unlock") or {}, "nations": nations}


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(f"work/gazetteer_in/valsora-gazetteer-all-{datetime.now(timezone.utc):%Y%m%d-%H%M}.json")
    store = Store(token(service_account()))
    data = fetch(store)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    n = data["nations"]
    sug = sum(len([1 for v in (f["facts"].get("suggest") or {}).values() if v]) for f in n.values())
    print(f"wrote {out}: {len(n)} nations with a password, {sum(1 for f in n.values() if f['facts'])} with facts, "
          f"{sug} suggestions, {sum(len(f['requests']) for f in n.values())} requests")


if __name__ == "__main__":
    main()
