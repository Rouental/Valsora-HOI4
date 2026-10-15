// A stand-in for the claude.ai runtime, keeping the platform's rules that the page relies on:
// path grammar, data/users/<id>/ private to its viewer, `planned` written by the owner only,
// collection queries over direct children with where/limit, assets for uploads.
// Configure before it runs: window.__me = {id, name, isOwner}; window.__seed = {path: data};
// window.__readonly (writes refused), window.__nodb (no db), window.__noassets.
(() => {
  const ME = Object.assign({ id: "u_owner", name: "The Author", isOwner: true }, window.__me || {});
  if (window.__notOwner) Object.assign(ME, { id: "u_friend", name: "A Friend", isOwner: false });
  const store = new Map(Object.entries(window.__seed || {}).map(([k, v]) => [k, JSON.parse(JSON.stringify(v))]));
  const docL = new Map();
  const colL = [];
  const SEG = /^[A-Za-z0-9_\-.~:@+]+$/;
  const segs = p => {
    const s = String(p).split("/");
    for (const x of s) if (!SEG.test(x) || x === "." || x === ".." || x.length > 200) throw new TypeError("bad path segment in " + p);
    return s;
  };
  const isObj = v => v !== null && typeof v === "object" && !Array.isArray(v);
  const deep = (a, b) => { const o = isObj(a) ? { ...a } : {}; for (const k in b) o[k] = isObj(b[k]) ? deep(o[k], b[k]) : b[k]; return o; };
  const parent = p => p.split("/").slice(0, -1).join("/");
  const privOther = p => { const m = /^data\/users\/([^/]+)\//.exec(p); return !!(m && m[1] !== ME.id); };
  const canWrite = p => !window.__readonly && !privOther(p) && !(p.startsWith("planned/") && !ME.isOwner);
  const refuse = () => Promise.reject({ code: "invalid_argument", message: "refused" });
  const visible = p => store.has(p) && !privOther(p);
  const snap = p => { const ok = visible(p), d = ok ? store.get(p) : undefined;
    return { id: p.split("/").pop(), ref: docRef(p), exists: ok, data: () => (ok ? JSON.parse(JSON.stringify(d)) : undefined), metadata: { fromCache: false, hasPendingWrites: false } }; };
  const match = (d, filters) => filters.every(([f, op, v]) => {
    const x = d[f];
    if (op === "==") return x === v;
    if (op === "!=") return x !== v;
    if (op === "in") return v.includes(x);
    if (op === "not-in") return !v.includes(x);
    throw new Error("mock: op " + op);
  });
  const colSnap = (c, filters, n) => {
    const docs = [...store.keys()].filter(p => parent(p) === c && visible(p) && match(store.get(p), filters)).sort().slice(0, n).map(snap);
    return { docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata: { fromCache: false, hasPendingWrites: false } };
  };
  const notify = p => {
    (docL.get(p) || new Set()).forEach(cb => setTimeout(() => cb(snap(p)), 3));
    colL.filter(l => l.c === parent(p)).forEach(l => setTimeout(() => l.cb(colSnap(l.c, l.f, l.n)), 3));
  };
  const size = d => JSON.stringify(d).length;
  function docRef(p) {
    if (segs(p).length % 2) throw new TypeError("odd segments for a doc: " + p);
    return {
      id: p.split("/").pop(), path: p,
      get: async () => snap(p),
      set: async d => { if (!canWrite(p)) return refuse(); if (size(d) > 262144) throw { code: "invalid_argument", message: "too big" };
        window.__writes.push(["set", p, d]); store.set(p, JSON.parse(JSON.stringify(d))); notify(p); },
      update: async d => { if (!canWrite(p)) return refuse(); window.__writes.push(["update", p, d]);
        if (!store.has(p)) throw { code: "not_found", message: "missing" }; store.set(p, deep(store.get(p), JSON.parse(JSON.stringify(d)))); notify(p); },
      delete: async () => { if (!canWrite(p)) return refuse(); window.__writes.push(["delete", p]); store.delete(p); notify(p); },
      onSnapshot: (cb, err) => { if (!docL.has(p)) docL.set(p, new Set()); docL.get(p).add(cb); setTimeout(() => cb(snap(p)), 3); return () => docL.get(p).delete(cb); },
      collection: c => colRef(p + "/" + c),
    };
  }
  function query(c, f, n) {
    return {
      path: c,
      where: (field, op, v) => query(c, [...f, [field, op, v]], n),
      limit: k => query(c, f, k),
      orderBy: () => query(c, f, n),
      get: async () => colSnap(c, f, n),
      onSnapshot: cb => { const l = { c, f, n, cb }; colL.push(l); setTimeout(() => cb(colSnap(c, f, n)), 3); return () => { const i = colL.indexOf(l); if (i >= 0) colL.splice(i, 1); }; },
    };
  }
  function colRef(c) {
    if (!(segs(c).length % 2)) throw new TypeError("even segments for a collection: " + c);
    return Object.assign(query(c, [], 1000), {
      doc: id => docRef(c + "/" + (id || Math.random().toString(36).slice(2))),
      add: async d => { const r = docRef(c + "/" + Math.random().toString(36).slice(2)); await r.set(d); return r; },
    });
  }
  const db = { doc: docRef, collection: colRef };
  window.__writes = []; window.__store = store; window.__assets = new Map();
  const av = "data:image/svg+xml," + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><circle cx="12" cy="12" r="12" fill="#6a7"/></svg>');
  const me = { id: ME.id, name: ME.name, avatarUrl: av, color: "#6a7", email: null, isOwner: ME.isOwner, canEdit: true };
  const user = {
    me: async () => me, can: async () => (window.__readonly ? false : true), id: async () => me.id, isOwner: async () => me.isOwner, canEdit: async () => true,
    profiles: async ids => Object.fromEntries([].concat(ids).map(i => [i, { id: i, name: { u_owner: "The Author", u_friend: "A Friend" }[i] || "Merlo", avatarUrl: av, color: "#888", email: null, isMe: i === me.id, guest: false }])),
  };
  const downloads = { save: async ({ filename, data }) => { window.__saved = { filename, data: String(data) }; return { status: "saved" }; } };
  const assets = {
    upload: async blob => { const id = [...crypto.getRandomValues(new Uint8Array(16))].map(b => b.toString(16).padStart(2, "0")).join("");
      // the test serves /_blob/<id> for every browser: hand it the bytes
      const b64 = await new Promise(r => { const f = new FileReader(); f.onload = () => r(String(f.result).split(",")[1]); f.readAsDataURL(blob); });
      if (window.__putBlob) await window.__putBlob(id, b64, blob.type);
      window.__assets.set(id, { size: blob.size, type: blob.type }); return { id, url: "/_blob/" + id, sizeBytes: blob.size, contentType: blob.type }; },
    list: async () => ({ assets: [...window.__assets.entries()].map(([id, a]) => ({ id, ...a })), usage: {} }),
    delete: async id => { window.__assets.delete(id); },
  };
  window.claude = { use: async n => {
    if (n === "db") return window.__nodb ? null : db;
    if (n === "assets") return window.__noassets || window.__readonly ? null : assets;
    return { user, downloads }[n] || null;
  } };
})();
