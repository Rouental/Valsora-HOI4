"""Reading the Gazetteer's site directly (scripts/gazetteer_fetch.py, 2026-10-18, the author: "In the future you need a
way to read the website directly"), against a stand-in for Google: a token endpoint that checks the service account's
signed request with the public half of a key made for the test, and a Firestore REST endpoint with two nations (one
nation's folder in two pages, as Firestore pages long listings). The file it writes must be the one the page's Owner
tools › Save every nation as a file writes for the same atlas.

    python3 tests/gazetteer/fetch.py        # PROBLEMS: none
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gazetteer_fetch as F  # noqa: E402

problems = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        problems.append(what)


def fs(v):
    """plain JSON -> a Firestore REST value"""
    if isinstance(v, bool):
        return {"booleanValue": v}
    if isinstance(v, int):
        return {"integerValue": str(v)}
    if isinstance(v, float):
        return {"doubleValue": v}
    if isinstance(v, str):
        return {"stringValue": v}
    if v is None:
        return {"nullValue": None}
    if isinstance(v, list):
        return {"arrayValue": {"values": [fs(x) for x in v]}}
    return {"mapValue": {"fields": {k: fs(x) for k, x in v.items()}}}


# the atlas: two nations with passwords, the second with nothing entered yet
KEYS = {"TST": "Brass Lantern 42", "EMP": "quiet-harbour-17"}
FOLDERS = {
    F.key_for("TST", KEYS["TST"]): [
        ("states", {"names": {"10,20": "Northmarch"}, "drawn": [], "empty": None}),
        ("politics", {"ruler": {"name": "Ada Test", "traits": ["popular_figure"]}, "gov": "neutrality"}),
        ("meta", {"status": "draft", "notes": "first pass", "updatedAt": 1760760000000,
                  "editors": {"u1": {"at": 1760760000000}}, "updatedBy": "u1"}),
        ("req_a1", {"t": "req", "text": "A new trait, please", "at": 1760760000001}),
        ("suggest", {"s1": {"type": "province", "label": "Split it", "pts": [[1, 2], [3, 4]]}}),
        ("img_abc", {"t": "img", "data": "data:image/png;base64,AAAA", "w": 82, "h": 52, "name": "flag.png",
                     "extra": "dropped"}),
    ],
    F.key_for("EMP", KEYS["EMP"]): [],
}
DOCS = {"owner/keys": KEYS, "planned/list": {"NEW": {"name": "Newland", "continent": None, "added": 1}}}


def serve(pub):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def reply(self, code, body):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            form = urllib.parse.parse_qs(self.rfile.read(int(self.headers["Content-Length"])).decode())
            head, claims, sig = form["assertion"][0].split(".")
            pad = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))  # noqa: E731
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(pad(sig))
            ok = subprocess.run(["openssl", "dgst", "-sha256", "-verify", pub, "-signature", f.name],
                                input=f"{head}.{claims}".encode(), capture_output=True).returncode == 0
            os.unlink(f.name)
            c = json.loads(pad(claims))
            if ok and c["iss"] == "reader@test.iam" and c["scope"] == F.SCOPE:
                self.reply(200, {"access_token": "tok-123"})
            else:
                self.reply(401, {"error": "bad assertion"})

        def do_GET(self):
            if self.headers.get("Authorization") != "Bearer tok-123":
                return self.reply(403, {"error": "no token"})
            u = urllib.parse.urlparse(self.path)
            path = urllib.parse.unquote(u.path).split("/documents/", 1)[1]
            if path in DOCS:
                return self.reply(200, {"name": path, "fields": fs(DOCS[path])["mapValue"]["fields"]})
            parts = path.split("/")
            if len(parts) == 3 and parts[0] == "n" and parts[2] in FOLDERS:
                docs = FOLDERS[parts[2]]
                q = urllib.parse.parse_qs(u.query)
                start = int(q.get("pageToken", ["0"])[0])
                page = docs[start:start + 4]          # four to a page: the first nation's folder takes two
                body = {"documents": [{"name": f"projects/p/databases/(default)/documents/{path}/{i}",
                                       "fields": fs(v)["mapValue"]["fields"]} for i, v in page]}
                if start + 4 < len(docs):
                    body["nextPageToken"] = str(start + 4)
                return self.reply(200, body if page else {})
            return self.reply(404, {"error": "not found"})

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    with tempfile.TemporaryDirectory() as tmp:
        key, pub = Path(tmp) / "key.pem", Path(tmp) / "pub.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key)],
                       check=True, capture_output=True)
        subprocess.run(["openssl", "pkey", "-in", str(key), "-pubout", "-out", str(pub)], check=True, capture_output=True)
        srv = serve(str(pub))
        base = f"http://127.0.0.1:{srv.server_port}"
        sa = {"type": "service_account", "client_email": "reader@test.iam", "private_key": key.read_text(),
              "token_uri": f"{base}/token"}
        out = Path(tmp) / "all.json"
        env = dict(os.environ, GAZETTEER_SERVICE_ACCOUNT=json.dumps(sa), GAZETTEER_FIRESTORE_URL=f"{base}/v1")
        env.pop("GAZETTEER_SERVICE_ACCOUNT_FILE", None)
        r = subprocess.run([sys.executable, "scripts/gazetteer_fetch.py", str(out)], cwd=ROOT, env=env,
                           capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        check(r.returncode == 0, "the fetch runs")
        if r.returncode:
            sys.exit(1)
        d = json.loads(out.read_text(encoding="utf-8"))
        check(set(d) == {"gazetteer", "saved", "planned", "unlock", "nations"} and d["gazetteer"] == 2,
              "the file has the page's top level (gazetteer 2, saved, planned, unlock, nations)")
        check(d["planned"] == DOCS["planned/list"] and d["unlock"] == {}, "planned/list read, a missing planned/unlock is {}")
        check(sorted(d["nations"]) == ["EMP", "TST"], "every nation with a password, through its own folder")
        t = d["nations"]["TST"]
        check(set(t["facts"]) == {"states", "politics", "suggest"}, "facts: the page's kinds only (meta, requests and "
              "pictures apart)")
        check(t["facts"]["states"] == {"names": {"10,20": "Northmarch"}, "drawn": []},
              "facts compacted as the page does (no nulls), empty lists kept")
        check(t["facts"]["suggest"]["s1"]["pts"] == [[1, 2], [3, 4]], "suggestions read whole, past the first page")
        check(t["meta"] == {"status": "draft", "notes": "first pass", "updatedAt": 1760760000000,
                            "editors": {"u1": {"at": 1760760000000}}}, "meta: status, notes, updatedAt, editors only")
        check(t["requests"] == [{"t": "req", "text": "A new trait, please", "at": 1760760000001, "id": "req_a1"}],
              "requests with their ids")
        check(t["images"] == {"abc": {"data": "data:image/png;base64,AAAA", "w": 82, "h": 52, "name": "flag.png"}},
              "pictures by id without img_, four fields")
        check(d["nations"]["EMP"] == {"facts": {}, "meta": {}, "requests": [], "images": {}}, "an empty nation")
        check("tok-123" not in out.read_text() and "PRIVATE KEY" not in out.read_text(),
              "neither the token nor the key in the file")
        bad = dict(sa, client_email="someone@else.iam")
        r = subprocess.run([sys.executable, "scripts/gazetteer_fetch.py", str(Path(tmp) / "no.json")], cwd=ROOT,
                           env=dict(env, GAZETTEER_SERVICE_ACCOUNT=json.dumps(bad)), capture_output=True, text=True)
        check(r.returncode != 0 and not (Path(tmp) / "no.json").exists(), "a refused key writes nothing")
        r = subprocess.run([sys.executable, "scripts/gazetteer_fetch.py"], cwd=ROOT,
                           env={k: v for k, v in env.items() if k != "GAZETTEER_SERVICE_ACCOUNT"},
                           capture_output=True, text=True)
        check(r.returncode != 0 and "GAZETTEER_SERVICE_ACCOUNT" in (r.stderr + r.stdout),
              "without a key it says how to set one")
        srv.shutdown()
    print("PROBLEMS: " + ("; ".join(problems) if problems else "none"))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
