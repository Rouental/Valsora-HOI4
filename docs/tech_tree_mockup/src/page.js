"use strict";
/* Valsora 2036 tech tree mockup: renders tree.json (inlined above) as the game's research screen would show it. */
const DATA = JSON.parse(document.getElementById("tree-data").textContent);
const TECH = new Map(DATA.techs.map(t => [t.id, t]));
const FOLD = new Map(DATA.folders.map(f => [f.key, f]));
const RANK = { feudal: 0, developing: 1, modern: 2, super: 3 };
const ERAS = DATA.meta.eras;
const ERA = Object.fromEntries(ERAS.map(e => [e.key, e]));
const TIERS = DATA.meta.tiers;
const TIERSHORT = { super: "Superpower", modern: "Modern", developing: "Developing", feudal: "Feudal" };
const STEP = { 1965: "Cold War I", 1985: "Cold War II", 2005: "Modern I", 2025: "Modern II", 2036: "Game start" };
const MAIN = ["infantry", "support", "artillery", "armour", "naval", "naval_support", "air", "electronics", "industry", "projects"];
const DOCS = ["doc_land", "doc_naval", "doc_air", "doc_sf"];
const CLASSIC = { armour: "armour_classic", naval: "naval_classic", air: "air_classic" };
const SHORT = { infantry: "Infantry", support: "Support", artillery: "Artillery", armour: "Armour", naval: "Naval",
  naval_support: "Naval Systems", air: "Air", electronics: "Electronics", industry: "Industry", projects: "Projects",
  doc_land: "Land", doc_naval: "Naval", doc_air: "Air", doc_sf: "Special Forces", armour_classic: "Armour",
  naval_classic: "Naval", air_classic: "Air" };
const KIDS = new Map();
for (const t of DATA.techs) for (const r of t.req || []) { if (!KIDS.has(r)) KIDS.set(r, []); KIDS.get(r).push(t.id); }
const DOC = new Map();       // doctrine entries by id, for search and details
for (const f of DATA.folders.filter(f => f.kind === "doctrines")) {
  for (const g of f.extra.grands) DOC.set(f.key + ":" + g.id, { kind: "grand", folder: f.key, ...g });
  for (const tr of f.extra.tracks) for (const s of tr.subs) DOC.set(f.key + ":" + s.id, { kind: "sub", folder: f.key, track: tr.name, ...s });
}

/* ---------------- icons: line art on a 24 grid, in the Deco UI's style ---------------- */
const ICONS = {
  rifle: '<path d="M2 11h12l1.5-1.5H21v3h-4l-1 1.5H9.5L8 17H5.5l1-3.5H2z"/><path d="M12 14l.6 2.6"/>',
  mg: '<path d="M3 9h13l2-1h3v2.5h-3l-1 1H8"/><path d="M9 11.5L5.5 19M9 11.5l3.5 7.5M9 11.5V19"/>',
  helmet: '<path d="M4 16v-1.5a8 8 0 0 1 16 0V16h-4.5l-1.6-2.6H10L8.4 16z"/><path d="M7 10.5h10M12 6.5v4"/>',
  optics: '<path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6z"/><circle cx="12" cy="12" r="3"/><path d="M12 7.5v1.2M12 15.3v1.2"/>',
  shield: '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
  exo: '<circle cx="12" cy="4.5" r="1.8"/><path d="M12 7v6M7.5 9h9M8.5 9l-1.5 5M15.5 9l1.5 5M12 13l-3 7M12 13l3 7M8.5 16.5h7"/>',
  network: '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><circle cx="12" cy="13" r="1.6"/><path d="M12 7v4.4M10.7 14.1l-4.1 2.7M13.3 14.1l4.1 2.7M7 18h10"/>',
  atgm: '<path d="M3 15.5l13.5-6 1.2 1.6-13.6 6z"/><path d="M17 9.6l4-1.6M17.8 11l3.6-.2"/><path d="M7.5 15.2l1.3 4.3M11.5 13.4l1.3 4.3"/>',
  truck: '<path d="M2.5 6.5h11v9.5h-11zM13.5 10h3.8l3.2 3.2V16h-7z"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
  ifv: '<path d="M3 13h18l-2 3.5H5z"/><path d="M6 13l1.5-3h7l1.5 3"/><path d="M11 10V8.5h4M15 9.2h6"/><circle cx="7" cy="18" r="1.2"/><circle cx="12" cy="18" r="1.2"/><circle cx="17" cy="18" r="1.2"/>',
  armcar: '<path d="M3 14l2-4h12l3 4v2H3z"/><path d="M9 10V8h4v2M13 9h6"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="12" cy="17.5" r="1.8"/><circle cx="17.5" cy="17.5" r="1.8"/>',
  amphib: '<path d="M4.5 12l2-3h10l3 3z"/><path d="M10.5 9V7.5h3.5"/><path d="M2 15.5c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5M2 19c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/>',
  marine: '<circle cx="12" cy="5" r="2"/><path d="M12 7v13M8 10.5h8M5 14a7 7 0 0 0 14 0"/>',
  mountain: '<path d="M2 19l6.5-11 4 6.5 2.5-4L22 19z"/><path d="M6.6 11.3l1.9 1.2 1.6-1.1"/>',
  para: '<path d="M3 11a9 7 0 0 1 18 0"/><path d="M3 11c1.5-1 3-1 4.5 0 1.5-1 3-1 4.5 0 1.5-1 3-1 4.5 0 1.5-1 3-1 4.5 0"/><path d="M3 11l9 7.5 9-7.5M7.5 11l4.5 7.5 4.5-7.5"/><circle cx="12" cy="20" r="1.3"/>',
  ranger: '<circle cx="12" cy="12" r="8.5"/><path d="M12 5l2 7-2 7-2-7z"/><path d="M5 12h3M16 12h3"/>',
  dagger: '<path d="M12 2.5l2 3v9h-4v-9z"/><path d="M7.5 14.5h9M12 14.5V21M10.5 21h3"/>',
  engineer: '<path d="M12 3v11M10 3h4"/><path d="M8.5 14h7l-1 4.5c-.4 1.5-1.5 2.5-2.5 2.5s-2.1-1-2.5-2.5z"/>',
  crate: '<path d="M3.5 8L12 4l8.5 4v8.5L12 20.5 3.5 16.5z"/><path d="M3.5 8L12 12l8.5-4M12 12v8.5M7.7 6l8.5 4"/>',
  drone: '<circle cx="5.5" cy="6" r="2.5"/><circle cx="18.5" cy="6" r="2.5"/><circle cx="5.5" cy="18" r="2.5"/><circle cx="18.5" cy="18" r="2.5"/><path d="M7.5 7.5l3 3M16.5 7.5l-3 3M7.5 16.5l3-3M16.5 16.5l-3-3"/><rect x="10" y="10" width="4" height="4" rx="1"/>',
  fpv: '<circle cx="6" cy="6" r="2.4"/><circle cx="18" cy="6" r="2.4"/><path d="M8 7.6l2.2 2M16 7.6l-2.2 2"/><path d="M10 9.5h4v4h-4z"/><path d="M12 13.5v6M9.5 17l2.5 3 2.5-3"/>',
  heli: '<path d="M3 4.5h14M10 4.5v3"/><path d="M4 12a5 4.5 0 0 1 5-4.5h3a4.5 4.5 0 0 1 0 9H8a4 4 0 0 1-4-4.5z"/><path d="M15.8 10.5H21l1-2.5"/><path d="M6 19.5h9M8 16.5v3M13 16.5v3"/>',
  police: '<path d="M12 3l2.2 4.6 5 .7-3.6 3.5.9 5L12 14.5l-4.5 2.3.9-5-3.6-3.5 5-.7z"/><path d="M5 20.5h14"/>',
  wrench: '<path d="M14.7 3.8a5 5 0 0 0-5 6.6L3.5 16.6a2 2 0 0 0 2.9 2.9l6.2-6.2a5 5 0 0 0 6.6-5l-3 3-2.6-.5-.5-2.6z"/>',
  medic: '<circle cx="12" cy="12" r="9"/><path d="M10 7h4v3h3v4h-3v3h-4v-3H7v-4h3z"/>',
  signal: '<path d="M12 10v11M9 21h6M10 10l2-5 2 5"/><path d="M7.5 5.5a6 6 0 0 0 0 8M16.5 5.5a6 6 0 0 1 0 8M5 3.5a9.5 9.5 0 0 0 0 12M19 3.5a9.5 9.5 0 0 1 0 12"/>',
  jam: '<path d="M13 2L6 13h5l-1 9 7-11h-5z"/>',
  cyber: '<rect x="5" y="10" width="14" height="10" rx="1.5"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
  aa: '<path d="M4 20h16M7.5 20l2.5-5h6l2 5"/><path d="M11 15l5.5-10 1.6.9-5.5 10"/><path d="M16.5 5l1.4-2.6 1 3.4"/>',
  laser: '<path d="M3 20h7M5 20v-4h3v4"/><path d="M8.5 15.5L19 6"/><path d="M19 6l2.2-2.2M19 6l2.8.6M19 6l-.6-2.8"/>',
  rail: '<rect x="6" y="3.5" width="12" height="12" rx="2"/><path d="M6 10h12M9 18.5L7 21M15 18.5l2 2.5M5 21h14"/><circle cx="9" cy="13" r=".8"/><circle cx="15" cy="13" r=".8"/>',
  missile: '<path d="M4 20l2.5-5.5L16 5l3-1-1 3-9.5 9.5z"/><path d="M6.5 14.5l3 3M4 16.5l-1 4.5 4.5-1"/>',
  howitzer: '<path d="M3 14l14-7 1 1.8-14 7z"/><circle cx="8" cy="17" r="3"/><path d="M10.5 18.5l5 2h5"/>',
  radar: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><path d="M12 12l6.4-6.4"/><circle cx="15.5" cy="9.5" r="1"/>',
  mlrs: '<path d="M2.5 15h19v2.5h-19z"/><path d="M6 15l9-7h4l-7 7"/><path d="M10 11.5l7.5-5.5"/><circle cx="6" cy="19.5" r="1.4"/><circle cx="12" cy="19.5" r="1.4"/><circle cx="18" cy="19.5" r="1.4"/>',
  tank: '<path d="M3 14h18l-2 3.5H5z"/><path d="M6.5 14l1.5-3.5h7l1.5 3.5"/><path d="M15 11.5h7"/><circle cx="7.5" cy="16" r=".6"/><circle cx="12" cy="16" r=".6"/><circle cx="16.5" cy="16" r=".6"/>',
  tank_l: '<path d="M5 14h14l-1.7 3H6.7z"/><path d="M8 14l1-2.5h5.5l1 2.5"/><path d="M14 12.3h5.5"/>',
  tank_h: '<path d="M2.5 13h19l-1.5 4.5H4z"/><path d="M5.5 13V9.5h10V13"/><path d="M15.5 10.5H22M8 9.5V8h4v1.5"/>',
  ugv: '<path d="M4 14h16l-1.5 3h-13z"/><path d="M8 14v-3h8v3"/><path d="M12 11V6M10 6h4"/><circle cx="12" cy="4.2" r="1"/>',
  engine: '<path d="M3 9h12l4-2v10l-4-2H3z"/><path d="M7 9v6M11 9v6M19 12h2"/>',
  flame: '<path d="M12 21c-4 0-6.5-2.8-6.5-6 0-4 3-5.5 4-9 2.5 1.5 3 3.5 3 5 1-1 1.5-2 1.5-3.5 2.5 2 4.5 4.5 4.5 7.5 0 3.2-2.5 6-6.5 6z"/>',
  mech: '<path d="M8.5 3.5h7l1.5 4h-10z"/><path d="M6.5 7.5h11V12h-11z"/><path d="M17.5 9h4"/><path d="M9 12l-2 4 1.5 4.5M15 12l2 4-1.5 4.5M6 20.5h4M14 20.5h4"/>',
  chip: '<rect x="7" y="7" width="10" height="10" rx="1"/><rect x="10" y="10" width="4" height="4"/><path d="M9.5 3v4M14.5 3v4M9.5 17v4M14.5 17v4M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4"/>',
  frigate: '<path d="M2 15h20l-2.5 4h-15z"/><path d="M5 15v-3h5V9h3v3h5v3"/><path d="M11.5 9V4M10 6h3"/>',
  torpedo: '<path d="M5 9.5h11l3 2.5-3 2.5H5a2.5 2.5 0 0 1 0-5z"/><path d="M19 12h2.5M21.5 9.5v5"/>',
  sonar: '<path d="M3 12h2"/><path d="M7 8a6 6 0 0 1 0 8M10.5 5a10 10 0 0 1 0 14M14 2.5a13 13 0 0 1 0 19"/>',
  usv: '<path d="M3 14h15l3-3v3l-2 4H5z"/><path d="M8 14v-2.5h5V14M10.5 11.5V8.5"/><path d="M14 6a4 4 0 0 1 0 5M16.5 4.5a6.5 6.5 0 0 1 0 8"/>',
  cruiser: '<path d="M1.5 15h21l-2.5 4h-16z"/><path d="M4 15v-2.5h4V10h7v2.5h4V15"/><path d="M11.5 10V5M10 7h3"/>',
  battleship: '<path d="M1.5 15h21l-3 4h-15z"/><path d="M5 15v-2h3v-2h7v2h3v2"/><path d="M11.5 11V6.5M3 13.5h3.5M17.5 13.5H21"/>',
  carrier: '<path d="M1.5 12h21l-3 6h-15z"/><path d="M15 12V8h3v4"/><path d="M4 12l1-2h4"/>',
  sub: '<path d="M2 14a3 3 0 0 1 3-3h13a4 4 0 0 1 4 3 4 4 0 0 1-4 3H5a3 3 0 0 1-3-3z"/><path d="M9 11V7.5h4l1 3.5M11 7.5V5"/>',
  gun: '<path d="M4 18h14v-4a3 3 0 0 0-3-3H8a4 4 0 0 0-4 4z"/><path d="M13 12l8-4M14 14.5l8-4"/><path d="M2 18h20"/>',
  cargo: '<path d="M2 15h20l-2 4H4z"/><path d="M5 15V9h12v6M5 12h12M9 9v6M13 9v6"/>',
  mine: '<circle cx="12" cy="12" r="5"/><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.9 2.9M15.5 15.5l2.9 2.9M5.6 18.4l2.9-2.9M15.5 8.5l2.9-2.9"/>',
  jet: '<path d="M12 2.5l1.6 5 6.9 7.5v1.5l-6.5-2-.5 4 2.5 2v1h-8v-1l2.5-2-.5-4-6.5 2V15l6.9-7.5z"/>',
  drone_l: '<path d="M12 4v15M2.5 10.5h19M9 19l3-1.5 3 1.5"/><path d="M10.6 4.5h2.8l.6 7h-4z"/>',
  jet_m: '<path d="M12 2.5l1.3 4.5 8 6.5v1.5l-8-2.5v5l2.5 2v1h-7.6v-1l2.5-2v-5l-8 2.5v-1.5l8-6.5z"/><path d="M11 6h2"/>',
  bomber: '<path d="M12 6l10 8-3 1.5-2.5-1.5L14 16l-2-1.5-2 1.5-2.5-1.5L5 15.5 2 14z"/>',
  cargo_air: '<path d="M12 2.5v17M3 9.5h18M8 19.5h8"/><path d="M10.5 3.5h3v12h-3zM6 9.5v2M18 9.5v2"/>',
  bomb: '<path d="M8.5 13.5a3.5 3.5 0 0 0 7 0v-6a3.5 3.5 0 0 0-7 0z"/><path d="M8.5 16.5L6.5 20h11l-2-3.5M12 4V2"/>',
  aam: '<path d="M5 10h11l3 2-3 2H5z"/><path d="M5 10L3 7.5M5 14l-2 2.5M12 10l-1.5-2M12 14l-1.5 2M19 12h2.5"/>',
  gun_air: '<path d="M3 9h14M3 12h16M3 15h14M17 8v8M6 8v8M19 12h2"/>',
  satellite: '<rect x="9.5" y="9.5" width="5" height="5" transform="rotate(45 12 12)"/><path d="M8.5 8.5L5.5 5.5M15.5 15.5l3 3"/><path d="M2 7l5-5 3 3-5 5zM14 19l5-5 3 3-5 5z"/>',
  ai: '<circle cx="12" cy="12" r="3.5"/><path d="M12 4v4.5M12 15.5V20M4 12h4.5M15.5 12H20M6.3 6.3l3.2 3.2M14.5 14.5l3.2 3.2M6.3 17.7l3.2-3.2M14.5 9.5l3.2-3.2"/><circle cx="12" cy="3" r="1"/><circle cx="12" cy="21" r="1"/><circle cx="3" cy="12" r="1"/><circle cx="21" cy="12" r="1"/>',
  quantum: '<circle cx="12" cy="12" r="1.6"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(120 12 12)"/>',
  code: '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
  fort: '<path d="M3 19.5h18M5 19.5v-6a7 7 0 0 1 14 0v6"/><path d="M8.5 14h7M3 19.5l2-2M21 19.5l-2-2"/>',
  nuke: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.5"/><path d="M12 10.5L9 5.6a7 7 0 0 1 6 0zM13.3 12.8l5.7.1a7 7 0 0 1-3 5.2zM10.7 12.8L8 18.1a7 7 0 0 1-3-5.2z"/>',
  factory: '<path d="M3 20.5V11l5 3v-3l5 3v-3l5 3V4.5h3v16z"/>',
  gear: '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="6.5"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
  crane: '<path d="M6.5 21V3.5M3.5 21h6M6.5 4.5h14M6.5 8.5l4-4M18 4.5V10M16.5 10h3v2.5h-3z"/>',
  pick: '<path d="M5 20l8.5-8.5"/><path d="M6 6.5c4-3.5 9.5-3.5 13 0-3-.8-6-.3-8.3 1.4L13.5 10l-2.2 2.2-1.8-1.8L11.7 8C10 6.8 8 6.3 6 6.5z"/>',
  fuel: '<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M6 8h12M6 16h12"/><path d="M12 10.5c1.4 1.6 2 2.4 2 3.2a2 2 0 0 1-4 0c0-.8.6-1.6 2-3.2z"/>',
  oil: '<path d="M12 3c3.5 4.5 6 7.5 6 11a6 6 0 0 1-12 0c0-3.5 2.5-6.5 6-11z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
  tyre: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M12 3v5M12 16v5M3 12h5M16 12h5"/>',
  rod: '<path d="M4 4l3 3"/><rect x="2.5" y="2.5" width="3" height="3" transform="rotate(45 4 4)"/><path d="M9 9l8 8"/><path d="M17 17l2.5 2.5M14.5 21H21v-6.5"/><path d="M5 12a7 7 0 0 0 7 7"/>',
  atom: '<circle cx="12" cy="12" r="1.6"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(120 12 12)"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18M5 7h14M5 17h14"/>',
  gov: '<path d="M3 9.5L12 4l9 5.5z"/><path d="M5.5 10v8M9.5 10v8M14.5 10v8M18.5 10v8M3 20.5h18"/>',
  flask: '<path d="M9 3h6M10 3v6l-5.2 9.2A1.9 1.9 0 0 0 6.5 21h11a1.9 1.9 0 0 0 1.7-2.8L14 9V3"/><path d="M7.5 15h9"/>',
  mail: '<rect x="3" y="6" width="18" height="12.5"/><path d="M3 6l9 7 9-7"/>',
  scale: '<path d="M12 4v16M7.5 20.5h9M5 7h14"/><path d="M5 7l-2.5 6a2.5 2.5 0 0 0 5 0zM19 7l-2.5 6a2.5 2.5 0 0 0 5 0z"/>',
  flag: '<path d="M6 21V3M6 4h12l-2.4 3.5L18 11H6"/>',
  people: '<circle cx="9" cy="8" r="2.8"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><circle cx="16.5" cy="9" r="2.2"/><path d="M15 14.2a4.5 4.5 0 0 1 6 4.3"/>',
  doc: '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 12h7M9 16h7"/>',
  x: '<path d="M5 5l14 14M19 5L5 19"/>',
  star: '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6l-5.4 2.9 1.2-6-4.5-4.2 6.1-.7z"/>',
};
(function sprite() {
  const s = document.getElementById("sprite");
  s.innerHTML = Object.entries(ICONS).map(([k, v]) =>
    `<symbol id="i-${k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${v}</symbol>`).join("");
})();
const ico = (k, cls = "") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-${ICONS[k] ? k : "chip"}"></use></svg>`;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* ---------------- state ---------------- */
const state = { tab: "overview", tier: "modern", dlc: true, markNew: true, q: "", sel: null };
try { const t = localStorage.getItem("valsora-tt-tier"); if (t && RANK[t] !== undefined) state.tier = t; } catch (e) { /* no storage */ }

const has = (t, tier = state.tier) => !!t && t.start != null && RANK[tier] >= RANK[t.start];
const avail = (t, tier = state.tier) => !has(t, tier) && (!(t.req && t.req.length) || t.req.some(r => has(TECH.get(r), tier)));
const folderName = k => (FOLD.get(k) || {}).name || k;
function startText(t) {
  if (t.start == null) return t.folder === "projects" ? "Nobody has it done at the start" : "Nobody at the start: researched in play";
  if (t.folder === "projects") return `Done at the start by: ${TIERS.filter(x => x.rank >= RANK[t.start]).map(x => TIERSHORT[x.key]).join(", ")}`;
  if (t.start === "super") return "The superpowers start with it";
  return `${TIERSHORT[t.start]} nations and above start with it`;
}

/* ---------------- tabs and controls ---------------- */
function visibleTabs() {
  const main = MAIN.filter(k => state.dlc || k !== "naval_support").map(k => (!state.dlc && CLASSIC[k]) ? CLASSIC[k] : k);
  return { main, docs: DOCS };
}
function renderTabs() {
  const { main, docs } = visibleTabs();
  const one = (k, label, icon) => `<button class="tab" role="tab" type="button" data-tab="${k}" aria-selected="${state.tab === k}">${ico(icon)}${esc(label)}</button>`;
  document.getElementById("tabs").innerHTML =
    one("overview", "Overview", "star") +
    main.map(k => one(k, SHORT[k], FOLD.get(k).icon)).join("") +
    `<span class="grp lbl">Doctrines</span>` + docs.map(k => one(k, SHORT[k], FOLD.get(k).icon)).join("");
  document.getElementById("tiers").innerHTML = ["super", "modern", "developing", "feudal"].map(k =>
    `<button type="button" data-tier="${k}" aria-pressed="${state.tier === k}">${TIERSHORT[k]}</button>`).join("");
  for (const b of document.querySelectorAll("#dlc button")) b.setAttribute("aria-pressed", String((b.dataset.dlc === "1") === state.dlc));
}

/* ---------------- tree geometry ---------------- */
const GA = { COLW: 150, ROWH: 64, SECT: 26, TOP: 66, LEFT: 20, BW: 140, BH: 56, SH: 48 };
const GD = { COLW: 170, ROWH: 64, TOP: 50, LEFT: 96, GAP: 14, BW: 160, BH: 56, SH: 48 };
function layout(f) {
  const ts = DATA.techs.filter(t => t.folder === f.key);
  const yi = new Map(f.years.map((y, i) => [y, i]));
  const starts = f.sections.map(s => s.lane);
  const nsec = l => starts.filter(s => s <= l).length;
  const pos = new Map();
  let W, H, laneA = [];
  if (f.orient === "across") {
    const G = GA;
    for (let l = 0; l < f.lanes; l++) laneA[l] = G.TOP + l * G.ROWH + G.SECT * nsec(l);
    W = G.LEFT + f.years.length * G.COLW + 24;
    H = laneA[f.lanes - 1] + G.ROWH + 18;
    for (const t of ts) {
      const h = t.size === "big" ? G.BH : G.SH;
      pos.set(t.id, { x: G.LEFT + yi.get(t.year) * G.COLW + (G.COLW - G.BW) / 2, y: laneA[t.lane] + (G.ROWH - h) / 2, w: G.BW, h,
        c: yi.get(t.year), l: t.lane });
    }
  } else {
    const G = GD;
    for (let l = 0; l < f.lanes; l++) laneA[l] = G.LEFT + l * G.COLW + G.GAP * (nsec(l) - 1);
    W = laneA[f.lanes - 1] + G.COLW + 20;
    H = G.TOP + f.years.length * G.ROWH + 18;
    for (const t of ts) {
      const h = t.size === "big" ? G.BH : G.SH;
      pos.set(t.id, { x: laneA[t.lane] + (G.COLW - G.BW) / 2, y: G.TOP + yi.get(t.year) * G.ROWH + (G.ROWH - h) / 2, w: G.BW, h,
        c: yi.get(t.year), l: t.lane });
    }
  }
  return { f, ts, yi, pos, W, H, laneA };
}
function route(L, s, t) {
  const f = L.f;
  if (f.orient === "across") {
    const G = GA, colB = i => G.LEFT + i * G.COLW;
    const sx = s.x + s.w, sy = s.y + s.h / 2, tx = t.x, ty = t.y + t.h / 2;
    if (t.c > s.c) {
      const g1 = colB(s.c + 1), g2 = colB(t.c);
      if (t.c === s.c + 1) return s.l === t.l ? `M${sx} ${sy}H${tx}` : `M${sx} ${sy}H${g1}V${ty}H${tx}`;
      const yc = t.l > s.l ? L.laneA[s.l] + G.ROWH : L.laneA[s.l];
      return `M${sx} ${sy}H${g1}V${yc}H${g2}V${ty}H${tx}`;
    }
    const g1 = colB(s.c + 1);
    return `M${sx} ${sy}H${g1}V${ty}H${t.x + t.w}`;
  }
  const G = GD, rowB = i => G.TOP + i * G.ROWH;
  const sx = s.x + s.w / 2, sy = s.y + s.h, tx = t.x + t.w / 2, ty = t.y;
  if (t.c > s.c) {
    const g1 = rowB(s.c + 1), g2 = rowB(t.c);
    if (t.c === s.c + 1) return s.l === t.l ? `M${sx} ${sy}V${ty}` : `M${sx} ${sy}V${g1}H${tx}V${ty}`;
    const xc = t.l > s.l ? L.laneA[s.l] + G.COLW : L.laneA[s.l];
    return `M${sx} ${sy}V${g1}H${xc}V${g2}H${tx}V${ty}`;
  }
  const g1 = rowB(s.c + 1);
  return `M${sx} ${sy}V${g1}H${tx}V${t.y + t.h}`;
}
function eraSpans(years) {
  const out = [];
  years.forEach((y, i) => {
    const e = eraOf(y);
    if (out.length && out[out.length - 1].e === e) out[out.length - 1].b = i; else out.push({ e, a: i, b: i });
  });
  return out;
}
function eraOf(y) { for (const e of ERAS) if (y >= e.from && y <= e.to) return e.key; return "next"; }

function cardHTML(t, p, tier, q) {
  const cls = ["tc", t.size === "small" ? "small" : "big", has(t, tier) ? "have" : avail(t, tier) ? "avail" : "lock"];
  if (state.sel === t.id) cls.push("sel");
  if (q && matches(t, q)) cls.push("hit");
  const isNew = t.replaces === "new";
  const sp = t.dlc && /special project/i.test(t.dlc) ? `<svg class="sp" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-atom"></use></svg>` : "";
  const label = `${t.name}, ${t.year}${isNew ? ", new" : ""}; ${has(t, tier) ? "researched at the start" : avail(t, tier) ? "available" : "locked"}`;
  return `<button type="button" class="${cls.join(" ")}" data-id="${t.id}" aria-label="${esc(label)}" style="left:${p.x}px;top:${p.y}px;width:${p.w}px;height:${p.h}px">` +
    `<span class="ic"><span>${ico(t.icon)}</span></span><span class="tn">${isNew && state.markNew ? '<i class="nbs"></i>' : ""}${esc(t.name)}</span><span class="ty">${t.year}</span>` +
    (isNew && state.markNew ? `<span class="nb">NEW</span>` : "") + sp + `</button>`;
}
function treeHTML(f, tier, q = "") {
  const L = layout(f);
  const parts = [];
  const spans = eraSpans(f.years);
  if (f.orient === "across") {
    const G = GA;
    for (const s of spans) {
      const x = G.LEFT + s.a * G.COLW, w = (s.b - s.a + 1) * G.COLW;
      parts.push(`<div class="era-band ${s.e}" style="left:${x}px;top:0;width:${w}px;height:${L.H}px"></div>`);
      parts.push(`<div class="era-lab ${s.e}" style="left:${x + 10}px;top:9px">${esc(ERA[s.e].name)}</div>`);
    }
    f.years.forEach((y, i) => parts.push(`<div class="yr" style="left:${G.LEFT + i * G.COLW + 10}px;top:26px">${y}${STEP[y] ? `<small>${STEP[y]}</small>` : ""}</div>`));
    for (const s of f.sections) parts.push(`<div class="sec" style="left:${G.LEFT + 4}px;top:${L.laneA[s.lane] - G.SECT + 6}px;width:${Math.min(L.W - 60, 700)}px">${esc(s.name)}</div>`);
    if (L.yi.has(2036)) {
      const x = G.LEFT + L.yi.get(2036) * G.COLW;
      parts.push(`<div class="startmark v" style="left:${x - 1}px;top:56px;height:${L.H - 56}px"><span style="left:4px;top:${L.H - 80}px">Start · 1 Jan 2036</span></div>`);
    }
  } else {
    const G = GD;
    for (const s of spans) {
      const y = G.TOP + s.a * G.ROWH, h = (s.b - s.a + 1) * G.ROWH;
      parts.push(`<div class="era-band ${s.e}" style="left:0;top:${y}px;width:${L.W}px;height:${h}px"></div>`);
      parts.push(`<div class="era-lab ${s.e}" style="left:10px;top:${y + 7}px">${esc(ERA[s.e].short || ERA[s.e].name)}</div>`);
    }
    f.years.forEach((y, i) => parts.push(`<div class="yr" style="left:12px;top:${G.TOP + i * G.ROWH + (STEP[y] ? 22 : 26)}px">${y}${STEP[y] ? `<small>${STEP[y]}</small>` : ""}</div>`));
    for (let k = 0; k < f.sections.length; k++) {
      const s = f.sections[k], nx = k + 1 < f.sections.length ? f.sections[k + 1].lane : f.lanes;
      const x = L.laneA[s.lane] + 6, w = L.laneA[nx - 1] + G.COLW - L.laneA[s.lane] - 12;
      parts.push(`<div class="sec wrapok" style="left:${x}px;top:${w < 200 && s.name.length > 12 ? 4 : 18}px;width:${w}px">${esc(s.name)}</div>`);
    }
    if (L.yi.has(2036)) {
      const y = G.TOP + L.yi.get(2036) * G.ROWH;
      parts.push(`<div class="startmark h" style="left:0;top:${y - 1}px;width:${L.W}px"><span style="right:8px;top:-17px">Start · 1 Jan 2036</span></div>`);
    }
  }
  // lines
  const paths = [];
  const marks = [];
  for (const t of L.ts) {
    const tp = L.pos.get(t.id);
    for (const r of t.req || []) {
      const sp = L.pos.get(r);
      if (!sp) continue;
      const rt = TECH.get(r);
      const cl = has(rt, tier) && has(t, tier) ? "l2" : has(rt, tier) ? "l1" : "l0";
      paths.push(`<path class="${cl}" d="${route(L, sp, tp)}"/>`);
    }
    for (const x of t.excl || []) {
      if (x < t.id) continue;
      const op = L.pos.get(x);
      if (!op) continue;
      const a = { x: tp.x + tp.w / 2, y: tp.y + tp.h / 2 }, b = { x: op.x + op.w / 2, y: op.y + op.h / 2 };
      paths.push(`<path class="lx" d="M${a.x} ${a.y}L${b.x} ${b.y}"/>`);
      let mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      if (f.orient === "down" && Math.abs(a.y - b.y) < 2) mx = Math.max(tp.x, op.x) - (GD.COLW - GD.BW) / 2;
      if (f.orient === "across" && Math.abs(a.x - b.x) < 2) my = Math.max(tp.y, op.y) - (GA.ROWH - GA.BH) / 2;
      marks.push(`<div class="xm" style="left:${mx}px;top:${my}px">${ico("x")}</div>`);
    }
  }
  const cards = L.ts.map(t => cardHTML(t, L.pos.get(t.id), tier, q)).join("");
  const html = `<div class="canvas${q ? " dimall" : ""}" style="width:${L.W}px;height:${L.H}px">` +
    `<svg class="wm" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-${f.icon}"></use></svg>` + parts.join("") +
    `<svg class="lines" width="${L.W}" height="${L.H}" viewBox="0 0 ${L.W} ${L.H}" aria-hidden="true">${paths.join("")}</svg>` +
    cards + marks.join("") + `</div>`;
  return { html, W: L.W, H: L.H };
}

/* ---------------- boards ---------------- */
const CX = ["small", "medium", "large", "insane"];
function pips(level, vanilla) {
  const n = CX.indexOf(level) + 1, v = CX.indexOf(vanilla) + 1;
  return `<span class="pips" title="Complexity: ${level}${vanilla && vanilla !== level ? ` (the game's: ${vanilla})` : ""}">` +
    [1, 2, 3, 4].map(i => `<i class="${i <= n ? "on" : ""}${v && v !== n && i === v ? " v" : ""}"></i>`).join("") + `</span>`;
}
function projectsHTML(f, tier, q = "") {
  const specs = f.extra.specs;
  return `<div class="board pj${q ? " dimall" : ""}">` + specs.map((s, i) => {
    const ts = DATA.techs.filter(t => t.folder === f.key && t.spec === s.key);
    const lines = [...new Set(ts.map(t => t.line))];
    return `<section class="col"><i class="ck tl"></i><i class="ck tr"></i><h3>${esc(s.name)}<small>${esc(s.game)} · ${ts.length} projects</small></h3>` +
      lines.map(ln => `<div class="line-h">${esc(ln)}</div><div class="pgrid">` + ts.filter(t => t.line === ln).map(t => {
        const cls = ["pc", has(t, tier) ? "have" : "", q && matches(t, q) ? "hit" : "", state.sel === t.id ? "sel" : ""].join(" ");
        return `<button type="button" class="${cls}" data-id="${t.id}"><span class="ic2">${ico(t.icon)}</span><span class="pn">${esc(t.name)}</span>` +
          `<span class="pm">${pips(t.complexity, t.vanilla && t.vanilla.complexity)}<span>${t.complexity} · ${t.year}</span></span>` +
          (t.replaces === "new" && state.markNew ? `<span class="nb">NEW</span>` : "") + `</button>`;
      }).join("") + `</div>`).join("") + `</section>`;
  }).join("") + `</div>`;
}
function doctrineHTML(f, q = "") {
  const e = f.extra;
  const grands = e.grands.map((g, i) => (i ? `<span class="gx" aria-hidden="true"><i></i></span>` : "") +
    `<button type="button" class="gd${q && dmatch(g, q) ? " hit" : ""}" data-doc="${f.key}:${g.id}"><span class="med"><span>${ico(f.icon)}</span></span><b>${esc(g.name)}</b>` +
    `<small>${g.replaces === "new" ? "new" : "the game's " + esc(g.vanilla_name || g.id)}</small></button>`).join("");
  const tracks = e.tracks.map(tr => `<section class="col"><i class="ck tl"></i><i class="ck tr"></i><h3>${esc(tr.name)}<small>${tr.vanilla_name ? "the game's " + esc(tr.vanilla_name) + " track · " : ""}${tr.subs.length} subdoctrines</small></h3>` +
    tr.subs.map(s => `<button type="button" class="sd${q && dmatch(s, q) ? " hit" : ""}" data-doc="${f.key}:${s.id}"><span class="sn">${esc(s.name)}</span>` +
      `<span class="sv">${s.replaces === "new" ? "New subdoctrine" : "The game's " + esc(s.vanilla_name || s.id)}${s.dlc ? " · " + esc(s.dlc.split(" (")[0]) : ""}</span>` +
      `<span class="rw" title="Five mastery rewards">${"<i></i>".repeat(5)}</span>${s.replaces === "new" && state.markNew ? `<span class="nb">NEW</span>` : ""}</button>`).join("") +
    `<div style="height:6px"></div></section>`).join("");
  return `<div class="board dc${q ? " dimall" : ""}"><div class="lbl" style="text-align:center">Grand doctrines · choose one</div><div class="grands">${grands}</div>` +
    `<div class="tracks">${tracks}</div>${e.note ? `<p class="dnote">${esc(e.note)}</p>` : ""}</div>`;
}

/* ---------------- search ---------------- */
function hay(t) {
  return [t.name, t.id, t.replaces, t.vanilla && t.vanilla.name, t.desc, ...(t.unlocks || []), t.section, t.line].join(" ").toLowerCase();
}
const HAY = new Map(DATA.techs.map(t => [t.id, hay(t)]));
const DHAY = new Map([...DOC].map(([k, d]) => [k, [d.name, d.id, d.vanilla_name, d.desc, ...(d.unl || [])].join(" ").toLowerCase()]));
const matches = (t, q) => q.split(/\s+/).every(w => HAY.get(t.id).includes(w));
const dmatch = (d, q) => q.split(/\s+/).every(w => [d.name, d.id, d.vanilla_name, d.desc].join(" ").toLowerCase().includes(w));
function searchAll(q) {
  const out = [];
  const ws = q.split(/\s+/);
  for (const t of DATA.techs) {
    const h = HAY.get(t.id);
    if (ws.every(w => h.includes(w))) out.push({ kind: "t", id: t.id, name: t.name, icon: t.icon, where: `${folderName(t.folder)} · ${t.year}`,
      score: (t.name.toLowerCase().includes(q) ? 0 : 1) + (FOLD.get(t.folder).variant_of ? 0.5 : 0) });
  }
  for (const [k, d] of DOC) {
    if (ws.every(w => DHAY.get(k).includes(w))) out.push({ kind: "d", id: k, name: d.name, icon: FOLD.get(d.folder).icon,
      where: `${folderName(d.folder)} · ${d.kind === "grand" ? "grand doctrine" : d.track}`, score: d.name.toLowerCase().includes(q) ? 0.2 : 1.2 });
  }
  return out.sort((a, b) => a.score - b.score || a.name.localeCompare(b.name));
}
function renderResults() {
  const box = document.getElementById("results");
  const q = state.q;
  if (q.length < 2) { box.hidden = true; return; }
  const r = searchAll(q);
  box.innerHTML = r.length ? r.slice(0, 40).map((x, i) => `<button type="button" data-${x.kind === "t" ? "id" : "doc"}="${x.id}" class="${i ? "" : "on"}">${ico(x.icon)}<span>${esc(x.name)}</span><small>${esc(x.where)}</small></button>`).join("") +
    (r.length > 40 ? `<div class="none">${r.length - 40} more: type more of the name</div>` : "") : `<div class="none">Nothing matches "${esc(q)}".</div>`;
  box.hidden = false;
}

/* ---------------- views ---------------- */
function folderCounts(key) {
  const ts = DATA.techs.filter(t => t.folder === key);
  const e = { cw: 0, modern: 0, y2036: 0, next: 0 };
  ts.forEach(t => e[t.era]++);
  return { n: ts.length, nw: ts.filter(t => t.replaces === "new").length, e, had: ts.filter(t => has(t)).length };
}
function folderView(key) {
  const f = FOLD.get(key);
  const q = state.q.length >= 2 ? state.q : "";
  let body, chips = [];
  chips.push(`<span class="chip code">${esc(f.game)}</span>`);
  if (f.dlc) chips.push(`<span class="chip dlc">${esc(f.dlc)}</span>`);
  let start = "";
  if (f.kind === "doctrines") {
    const subs = f.extra.tracks.reduce((a, t) => a + t.subs.length, 0);
    const nw = f.extra.tracks.reduce((a, t) => a + t.subs.filter(s => s.replaces === "new").length, 0);
    const ntr = f.extra.tracks_in_game || f.extra.tracks.length;
    chips.push(`<span class="chip"><b>${f.extra.grands.length}</b> grand doctrines</span><span class="chip"><b>${ntr}</b> tracks</span><span class="chip"><b>${subs}</b> subdoctrines</span><span class="chip"><b>${nw}</b> new</span>`);
    start = `<div class="startline"><span class="lbl">Doctrines</span><span>are chosen with experience, not researched by year: every nation starts with none and picks its own.</span></div>`;
    body = doctrineHTML(f, q);
  } else {
    const c = folderCounts(key);
    chips.push(`<span class="chip"><b>${c.n}</b> ${f.kind === "projects" ? "projects" : "technologies"}</span><span class="chip"><b>${c.nw}</b> new</span><span class="chip"><b>${c.n - c.nw}</b> renamed</span>`);
    const tierObj = TIERS.find(x => x.key === state.tier);
    start = f.kind === "projects"
      ? `<div class="startline"><span class="lbl">${esc(tierObj.name)}</span><span>${c.had ? `has <b>${c.had}</b> of these done at the start (gold).` : "has none of these done at the start."} Complexity: ◆ small to ◆◆◆◆ insane; a green ring marks the game's own level where it differs.</span></div>`
      : `<div class="startline"><span class="lbl">${esc(tierObj.name)}</span><span>starts with <b>${c.had}</b> of ${c.n} here (gold): ${esc(tierObj.desc)}</span></div>`;
    if (f.kind === "projects") body = projectsHTML(f, state.tier, q);
    else { const t = treeHTML(f, state.tier, q); body = `<div class="treebox" style="--h:${t.H + 2}px">${t.html}</div>`; }
  }
  const legend = f.kind === "tree" ? `<div class="legend"><span><i class="sw have"></i>Researched at the start</span><span><i class="sw avail"></i>Can be researched</span><span><i class="sw lock"></i>Later</span><span><i class="sw new"></i>New technology</span><span><i class="sw ex"></i>Mutually exclusive</span><span>${ico("atom", "")} Needs a special project</span></div>` : "";
  return `<div class="fhead"><div><h2 class="gilt-text">${esc(f.name)}</h2><p>${esc(f.blurb)}</p><div class="fmeta">${chips.join("")}</div></div></div><div class="under">${start}${legend}</div>${body}`;
}

function overviewView() {
  const rows = [], tree = [...MAIN, "armour_classic", "naval_classic", "air_classic"];
  let tot = { n: 0, nw: 0, e: { cw: 0, modern: 0, y2036: 0, next: 0 } };
  for (const k of tree) {
    const f = FOLD.get(k), c = folderCounts(k);
    const isMain = !f.variant_of;
    if (isMain) { tot.n += c.n; tot.nw += c.nw; for (const e in c.e) tot.e[e] += c.e[e]; }
    rows.push(`<tr><td><button type="button" class="lnk" data-tab="${k}">${esc(f.name)}</button><br><small class="lbl" style="letter-spacing:.06em;text-transform:none">${esc(f.game)}</small></td>` +
      ["cw", "modern", "y2036", "next"].map(e => `<td class="n">${c.e[e]}</td>`).join("") +
      `<td class="n"><b>${c.n}</b></td><td class="n">${c.nw}</td><td class="n">${c.n - c.nw}</td><td><div class="ebar" aria-hidden="true">${["cw", "modern", "y2036", "next"].map(e => `<i class="${e}" style="width:${100 * c.e[e] / c.n}%"></i>`).join("")}</div></td></tr>`);
    if (k === "projects") rows.push(`<tr class="sum"><td>Designer folders and projects</td>${["cw", "modern", "y2036", "next"].map(e => `<td class="n">${tot.e[e]}</td>`).join("")}<td class="n">${tot.n}</td><td class="n">${tot.nw}</td><td class="n">${tot.n - tot.nw}</td><td></td></tr><tr><td colspan="9" class="lbl" style="padding-top:14px">Without the designer DLCs, these replace Armour, Naval, Naval Systems and Air</td></tr>`);
  }
  const drows = DOCS.map(k => {
    const f = FOLD.get(k), subs = f.extra.tracks.reduce((a, t) => a + t.subs.length, 0), nw = f.extra.tracks.reduce((a, t) => a + t.subs.filter(s => s.replaces === "new").length, 0);
    return `<tr><td><button type="button" class="lnk" data-tab="${k}">${esc(f.name)}</button></td><td class="n">${f.extra.grands.length}</td><td class="n">${f.extra.tracks_in_game || f.extra.tracks.length}</td><td class="n">${subs}</td><td class="n">${nw}</td><td class="n">${subs - nw}</td></tr>`;
  });
  const dsum = DOCS.reduce((a, k) => { const f = FOLD.get(k); a.g += f.extra.grands.length; a.s += f.extra.tracks.reduce((x, t) => x + t.subs.length, 0); a.n += f.extra.tracks.reduce((x, t) => x + t.subs.filter(s => s.replaces === "new").length, 0); return a; }, { g: 0, s: 0, n: 0 });
  const mainTree = DATA.techs.filter(t => MAIN.includes(t.folder) && t.folder !== "projects");
  const proj = DATA.techs.filter(t => t.folder === "projects");
  const tierRows = ["super", "modern", "developing", "feudal"].map(k => {
    const ti = TIERS.find(x => x.key === k);
    const n = mainTree.filter(t => has(t, k)).length, p = proj.filter(t => has(t, k)).length;
    return `<div class="tier"><b>${esc(ti.name)}</b><span>${esc(ti.desc)}</span><em title="technologies researched at the start, of ${mainTree.length}">${n}<small class="lbl" style="display:block;margin-top:4px;font-size:9px">of ${mainTree.length}${p ? ` · ${p} projects` : ""}</small></em></div>`;
  }).join("");
  const eraRows = ERAS.map(e => `<tr><td><span class="eradot ${e.key}"></span><b>${esc(e.name)}</b></td><td>${e.from}–${e.to}</td><td>${esc(e.desc)}</td></tr>`).join("");
  return `<div class="ov">
  <section><p class="lead">Valsora's research begins where the base game's ends: the floor is the Cold War, today's kit sits in the middle, and the game's thirteen years run from 2036 into the next generation.</p>
  <div class="figs">
   <div class="fig"><b>${MAIN.length - 1}</b><span class="lbl">Research folders</span></div>
   <div class="fig"><b>${mainTree.length}</b><span class="lbl">Technologies</span></div>
   <div class="fig"><b>${mainTree.filter(t => t.replaces === "new").length}</b><span class="lbl">Of them new</span></div>
   <div class="fig"><b>${proj.length}</b><span class="lbl">Special projects</span></div>
   <div class="fig"><b>${dsum.s}</b><span class="lbl">Subdoctrines</span></div>
   <div class="fig"><b>${DATA.techs.filter(t => FOLD.get(t.folder).variant_of).length}</b><span class="lbl">Without-DLC fallbacks</span></div>
  </div></section>
  <section><h2>The calendar</h2><p><b>The base game's 1936 is Valsora's 2036.</b> Every line keeps the game's own steps in their order. Its first steps are today's kit (what the base game gives its minor nations), its 1936 steps are 2036's (what its majors start with: here, the superpowers), and its steps after 1936 are the game's thirteen years, with the base game's rhythm of a big step every three years. New steps added below them are the Cold War kit the poorer nations start with, and a few added at the end keep the frontier open. Pick a start above to see each tier's frontier in gold.</p>
   <div class="scroll-x"><table><thead><tr><th>Era</th><th>Years</th><th>What it holds</th></tr></thead><tbody>${eraRows}</tbody></table></div></section>
  <section><h2>Who starts with what</h2><p>The four great powers, one for every ideology but the Theocratic, are the superpowers: ${DATA.meta.superpowers.map(s => `${esc(s.name)} (${s.tag}, ${s.ideology})`).join(", ")}. Nuclear weapons exist in small numbers, theirs alone at the start. The figure is the technologies each tier has researched on 1 January 2036 in the designer folders.</p><div class="tiers">${tierRows}</div></section>
  <section><h2>Counts by folder and era</h2>
   <div class="scroll-x"><table><thead><tr><th>Folder</th><th class="n"><span class="eradot cw"></span>Cold War</th><th class="n"><span class="eradot modern"></span>Modern</th><th class="n"><span class="eradot y2036"></span>2036</th><th class="n"><span class="eradot next"></span>Next gen.</th><th class="n">Total</th><th class="n">New</th><th class="n">Renamed</th><th>By era</th></tr></thead><tbody>${rows.join("")}</tbody></table></div></section>
  <section><h2>Doctrines</h2><p>The game's 1.19 doctrines: a grand doctrine per folder (they exclude each other), then one subdoctrine per track, each with five mastery rewards. Renamed for 2036, with a few new ones for drones, mechs, arsenal ships and electronic warfare.</p>
   <div class="scroll-x"><table><thead><tr><th>Folder</th><th class="n">Grand</th><th class="n">Tracks</th><th class="n">Subdoctrines</th><th class="n">New</th><th class="n">Renamed</th></tr></thead><tbody>${drows.join("")}<tr class="sum"><td>All four</td><td class="n">${dsum.g}</td><td class="n">14</td><td class="n">${dsum.s}</td><td class="n">${dsum.n}</td><td class="n">${dsum.s - dsum.n}</td></tr></tbody></table></div></section>
  <section class="two"><div><h2>How to read a folder</h2><p>Each folder is laid out as the game lays it: Infantry, Support and the naval folders run their years across the top, the others down the left side. The eras are the coloured bands; the dashed line is the game's start. Cards are gold where the chosen tier has researched them on day one, framed in green where it can research them next, plain where they come later. Large cards unlock equipment or units, small ones are upgrades. Click any card for its file: what it replaces in the base game, what it unlocks, who has it.</p></div>
   <div><h2>The in-game view</h2><p>The button at the top shows any folder as a 1920 × 1080 screen in the Valsora Deco UI, under the top bar and the research screen's notched header, the way the author would see it in the game. The pictures in <code>screens/</code> were taken from it.</p><p><button type="button" class="btn" data-game="infantry">Open the Infantry folder in game</button></p></div></section>
  </div>`;
}

/* ---------------- details ---------------- */
function chipsFor(ids) {
  return `<div class="links">${ids.map(id => { const t = TECH.get(id); if (!t) return `<span class="id">${esc(id)}</span>`;
    return `<button type="button" data-id="${id}">${esc(t.name)}<small>${t.year}${t.folder !== state.tab ? " · " + esc(SHORT[t.folder] || t.folder) : ""}</small></button>`; }).join("")}</div>`;
}
function detailTech(t) {
  const v = t.vanilla;
  const f = FOLD.get(t.folder);
  let rep;
  if (t.replaces === "new") rep = `<p><span class="tag-new">NEW</span> <span style="margin-left:6px">A new ${t.folder === "projects" ? "project" : "technology"}: not in the base game.</span></p>`;
  else rep = `<dl class="rep"><dt>Replaces</dt><dd><code>${esc(t.replaces)}</code>${v && v.name ? ` · ${esc(v.name)}` : ""}${v && v.year ? ` (${v.year})` : ""}</dd>` +
    (v && v.complexity ? `<dt>Game's</dt><dd>complexity ${esc(v.complexity)}, prototype ${esc(v.prototype)}, ${esc(v.specialization)}</dd>` : "") +
    (v && v.requires && v.requires.length ? `<dt>Game's path</dt><dd>after <code>${v.requires.map(esc).join("</code>, <code>")}</code></dd>` : "") +
    (v && v.also ? `<dt>Also</dt><dd>${v.also.map(a => `<code>${esc(a.id)}</code>${a.dlc ? ` (${esc(a.dlc)})` : ""}`).join(", ")}</dd>` : "") +
    (v && v.cost ? `<dt>Cost</dt><dd>${v.cost} × the base cost, as in the game</dd>` : "") + `</dl>`;
  const meta = [t.year, ERA[t.era].name, f.name, t.section || t.line, t.size === "big" && t.folder !== "projects" ? "equipment or unit" : t.folder !== "projects" ? "upgrade" : t.complexity + " complexity"].filter(Boolean).join(" · ");
  const kids = KIDS.get(t.id) || [];
  return `<h3 class="gilt-text">${esc(t.name)}</h3><div class="meta">${esc(meta)}</div>` +
    `<p class="desc">${esc(t.desc)}</p><div class="rule"></div>${rep}` +
    `<h4>At the start</h4><p style="margin:0;font-size:13.5px">${esc(startText(t))}</p>` +
    (t.unlocks && t.unlocks.length ? `<h4>${t.folder === "projects" ? "Output" : "Unlocks in the game"}</h4><ul>${t.unlocks.map(u => `<li><span>${esc(u).replace(/\b([a-z]+_[a-z0-9_]+)\b/g, "<code>$1</code>")}</span></li>`).join("")}</ul>` : "") +
    (t.req && t.req.length ? `<h4>Needs ${t.req.length > 1 ? "one of" : ""}</h4>${chipsFor(t.req)}` : "") +
    (kids.length ? `<h4>Leads to</h4>${chipsFor(kids)}` : "") +
    (t.excl && t.excl.length ? `<h4>Excludes</h4>${chipsFor(t.excl)}` : "") +
    (t.same ? `<h4>With the designer DLCs</h4>${chipsFor([t.same])}` : "") +
    (t.dlc ? `<div class="note"><b>DLC:</b> ${esc(t.dlc)}</div>` : "") +
    (t.note ? `<div class="note">${esc(t.note)}</div>` : "") +
    (t.tags ? `<h4>Project tags</h4><p style="margin:0" class="id">${t.tags.map(esc).join(", ")}</p>` : "");
}
function detailDoc(d) {
  const f = FOLD.get(d.folder);
  return `<h3 class="gilt-text">${esc(d.name)}</h3><div class="meta">${esc(f.name)} · ${d.kind === "grand" ? "grand doctrine" : esc(d.track) + " track"}</div>` +
    `<p class="desc">${esc(d.desc)}</p><div class="rule"></div>` +
    (d.replaces === "new" ? `<p><span class="tag-new">NEW</span> <span style="margin-left:6px">A new ${d.kind === "grand" ? "grand doctrine" : "subdoctrine"}.</span></p>`
      : `<dl class="rep"><dt>Replaces</dt><dd><code>${esc(d.id)}</code> · ${esc(d.vanilla_name || "")}</dd>${d.also && d.also.length ? `<dt>Also</dt><dd><code>${d.also.map(esc).join("</code>, <code>")}</code></dd>` : ""}</dl>`) +
    (d.kind === "sub" ? `<h4>Mastery</h4><p style="margin:0;font-size:13.5px">Five rewards as the track's mastery grows: the game's, renamed in a later step.</p>` : `<h4>Excludes</h4><p style="margin:0;font-size:13.5px">The folder's other grand doctrines.</p>`) +
    (d.unl && d.unl.length ? `<h4>Effects</h4><ul>${d.unl.map(u => `<li><span>${esc(u)}</span></li>`).join("")}</ul>` : "") +
    (d.dlc ? `<div class="note"><b>DLC:</b> ${esc(d.dlc)}</div>` : "");
}
function openDetail(html) {
  const el = document.getElementById("detail");
  el.innerHTML = `<i class="ck tl"></i><i class="ck tr"></i><i class="ck bl"></i><i class="ck br"></i><button type="button" class="x" aria-label="Close">${ico("x")}</button>` + html;
  el.hidden = false;
  el.scrollTop = 0;
}
function closeDetail() { document.getElementById("detail").hidden = true; state.sel = null; for (const c of document.querySelectorAll(".tc.sel,.pc.sel")) c.classList.remove("sel"); }

function select(id, scroll) {
  const t = TECH.get(id);
  if (!t) return;
  const f = FOLD.get(t.folder);
  if (f.variant_of && state.dlc) state.dlc = false;
  if (!f.variant_of && CLASSIC[t.folder] && !state.dlc) state.dlc = true;
  if (t.folder === "naval_support" && !state.dlc) state.dlc = true;
  state.sel = id;
  if (state.tab !== t.folder) { state.tab = t.folder; render(); }
  else for (const c of document.querySelectorAll(".tc,.pc")) c.classList.toggle("sel", c.dataset.id === id);
  openDetail(detailTech(t));
  if (scroll) {
    const el = document.querySelector(`[data-id="${CSS.escape(id)}"].tc, [data-id="${CSS.escape(id)}"].pc`);
    if (el) { el.scrollIntoView({ block: "center", inline: "center", behavior: "auto" }); el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash"); }
  }
}
function selectDoc(key, scroll) {
  const d = DOC.get(key);
  if (!d) return;
  if (state.tab !== d.folder) { state.tab = d.folder; render(); }
  openDetail(detailDoc(d));
  if (scroll) { const el = document.querySelector(`[data-doc="${CSS.escape(key)}"]`); if (el) { el.scrollIntoView({ block: "center" }); el.classList.add("flash"); } }
}

/* ---------------- render ---------------- */
function render() {
  renderTabs();
  const main = document.getElementById("main");
  main.innerHTML = state.tab === "overview" ? overviewView() : folderView(state.tab);
  try { if (location.hash.slice(1) !== state.tab) history.replaceState(null, "", "#" + state.tab); } catch (e) { /* sandboxed */ }
  const sel = document.querySelector('.tab[aria-selected="true"]');
  if (sel) sel.scrollIntoView({ block: "nearest", inline: "nearest" });
}

/* ---------------- in-game view ---------------- */
function stageHTML(key, tier) {
  const f = FOLD.get(key);
  const { main, docs } = visibleTabs();
  const tabsArr = (f.kind === "doctrines" ? docs : main);
  const tabs = tabsArr.map((k, i) => `<span class="g-tab${k === key ? " on" : ""}${f.kind !== "doctrines" && k === "projects" ? " sep" : ""}" title="${esc(SHORT[k])}"><span>${ico(FOLD.get(k).icon)}</span></span>`).join("");
  const crowns = ["gov", "flask", "mail", "scale", "crane", "factory", "people", "truck", "optics", "doc"].map((k, i) => `<span class="g-ib${i === 1 ? " on" : ""}"><span>${ico(k)}</span></span>`).join("");
  const rd = (icon, l, v) => `<div class="g-vd"></div><div class="g-rd">${ico(icon)}<div><div class="g-rl">${l}</div><div class="g-rv">${v}</div></div></div>`;
  const sp = { super: ["SUPERPOWER", "214", "71%", "48%", "8.62M", "◆ 412  ◆ 288  ◆ 64"], modern: ["MODERN NATION", "96", "62%", "35%", "1.24M", "◆ 46  ◆ 28  ◆ 6"],
    developing: ["DEVELOPING", "61", "51%", "28%", "820.4K", "◆ 18  ◆ 9  ◆ 1"], feudal: ["LEVY STATE", "38", "44%", "40%", "215.0K", "◆ 7  ◆ 3  ◆ 0"] }[tier];
  const kindWord = f.kind === "doctrines" ? "DOCTRINE" : f.kind === "projects" ? "SPECIAL PROJECTS" : "RESEARCH";
  const sub = f.kind === "doctrines" ? `${f.name} · grand doctrines and their tracks`
    : f.kind === "projects" ? `Special project facilities · ${TIERS.find(x => x.key === tier).name} on 1 January 2036`
      : `${f.name}${f.variant_of ? " (without the designer DLC)" : ""} · Cold War to the next generation · ${TIERS.find(x => x.key === tier).name} on 1 January 2036`;
  const legend = f.kind === "tree" ? `<div class="g-legend"><span><i class="sw have"></i>Researched</span><span><i class="sw avail"></i>Available</span><span><i class="sw lock"></i>Later</span><span><i class="sw new"></i>New</span><span><i class="sw ex"></i>Exclusive</span></div>`
    : f.kind === "projects" ? `<div class="g-legend"><span><i class="sw have"></i>Done at the start</span><span><span class="pips"><i class="on"></i><i class="on"></i><i></i><i></i></span>Complexity</span><span><i class="sw new"></i>New</span></div>` : "";
  return `<div class="g-map"></div>
   <div class="g-top"><div class="g-btns">${crowns}</div>
    <div class="g-reads">${rd("star", "Political power", `${sp[1]}<span class="pos">+2.10</span>`)}${rd("gov", "Stability", sp[2])}${rd("flag", "War support", sp[3])}${rd("people", "Manpower", sp[4])}${rd("factory", "Factories", sp[5])}<div class="g-vd"></div></div>
    <div class="g-date"><div><span class="g-play"></span><div class="d">1 JANUARY 2036<small>PAUSED</small></div><span style="color:#F1DC9C;font:700 15px/1 var(--f-body)">›››</span></div></div></div>
   <div class="g-med"><div><span class="g-flag"><span>${ico("globe")}</span></span><span class="nm gilt-text">${sp[0]}</span><span class="seal">${ico("doc")}</span></div></div>
   <div class="g-panel"><div class="g-head"><div class="g-title gilt-text">${kindWord}</div><div class="g-sub">${esc(sub)}</div><div class="g-tabs">${tabs}</div>
     ${f.kind === "tree" ? `<div class="g-slots"><div class="g-rl">Research slots</div><div class="g-rv">${{ super: 6, modern: 4, developing: 3, feudal: 2 }[tier]} · ${f.years[0]} to ${f.years[f.years.length - 1]}</div></div>` : ""}
     <span class="g-close">${ico("x")}</span></div>
    <div class="g-tree" id="g-tree"><div class="inner" id="g-inner"></div><i class="ck tl"></i><i class="ck tr"></i><i class="ck bl"></i><i class="ck br"></i>${legend}<div class="g-scale" id="g-scale"></div></div></div>`;
}
function showGame(key, tier = state.tier, shot = false) {
  const f = FOLD.get(key) || FOLD.get("infantry");
  const st = document.getElementById("stage"), scr = document.getElementById("scr");
  st.hidden = false; st.classList.toggle("shot", shot);
  document.getElementById("app").hidden = true; document.getElementById("detail").hidden = true;
  scr.innerHTML = stageHTML(f.key, tier);
  const inner = document.getElementById("g-inner"), area = document.getElementById("g-tree");
  const AW = 1900, AH = 888;
  let W, H;
  if (f.kind === "tree") { const t = treeHTML(f, tier); inner.innerHTML = t.html; W = t.W; H = t.H; }
  else {
    inner.style.width = AW + "px";
    inner.innerHTML = f.kind === "projects" ? projectsHTML(f, tier) : doctrineHTML(f);
    W = AW; H = inner.scrollHeight;
  }
  const s = Math.min(1, (AW - 4) / W, (AH - 64) / H);
  inner.style.transform = `scale(${s})`;
  inner.style.left = Math.max(0, (AW - W * s) / 2) + "px";
  inner.style.top = (f.kind === "tree" ? 0 : 6) + "px";
  document.getElementById("g-scale").textContent = s < 0.999 ? `Whole folder shown at ${Math.round(s * 100)} % (the game scrolls it)` : "Shown at the game's size";
  fitStage();
  return s;
}
function fitStage() {
  const scr = document.getElementById("scr");
  const s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
  scr.style.transform = `scale(${s})`;
  scr.style.left = Math.max(0, (window.innerWidth - 1920 * s) / 2) + "px";
  scr.style.top = Math.max(0, (window.innerHeight - 1080 * s) / 2) + "px";
}
function hideGame() { document.getElementById("stage").hidden = true; document.getElementById("app").hidden = false; render(); }
window.addEventListener("resize", () => { if (!document.getElementById("stage").hidden) fitStage(); });

/* ---------------- events ---------------- */
document.addEventListener("click", e => {
  const tab = e.target.closest("[data-tab]");
  if (tab) { state.tab = tab.dataset.tab; state.sel = null; document.getElementById("detail").hidden = true; render(); window.scrollTo({ top: 0 }); return; }
  const tier = e.target.closest("[data-tier]");
  if (tier) { state.tier = tier.dataset.tier; try { localStorage.setItem("valsora-tt-tier", state.tier); } catch (err) { /* none */ } const keep = state.sel; render(); if (keep) select(keep, false); return; }
  const dl = e.target.closest("[data-dlc]");
  if (dl) { state.dlc = dl.dataset.dlc === "1"; const map = state.dlc ? Object.fromEntries(Object.entries(CLASSIC).map(([a, b]) => [b, a])) : CLASSIC;
    if (map[state.tab]) state.tab = map[state.tab]; if (!state.dlc && state.tab === "naval_support") state.tab = "naval_classic"; render(); return; }
  const g = e.target.closest("[data-game]");
  if (g) { showGame(g.dataset.game); return; }
  if (e.target.closest("#to-game")) { showGame(state.tab === "overview" ? "infantry" : state.tab); return; }
  if (e.target.closest("#exit-game")) { hideGame(); return; }
  if (e.target.closest(".detail .x")) { closeDetail(); return; }
  const r = e.target.closest("#results [data-id], #results [data-doc]");
  if (r) { document.getElementById("results").hidden = true; r.dataset.id ? select(r.dataset.id, true) : selectDoc(r.dataset.doc, true); return; }
  const card = e.target.closest("[data-id]");
  if (card) { select(card.dataset.id, !card.matches(".tc,.pc")); return; }
  const dc = e.target.closest("[data-doc]");
  if (dc) { selectDoc(dc.dataset.doc, false); return; }
  if (!e.target.closest(".search")) document.getElementById("results").hidden = true;
});
document.getElementById("q").addEventListener("input", e => {
  state.q = e.target.value.trim().toLowerCase();
  renderResults();
  if (state.tab !== "overview") { const y = window.scrollY; const box = document.querySelector(".treebox"); const sx = box && box.scrollLeft, sy = box && box.scrollTop;
    document.getElementById("main").innerHTML = folderView(state.tab); const nb = document.querySelector(".treebox"); if (nb && box) { nb.scrollLeft = sx; nb.scrollTop = sy; } window.scrollTo(0, y); }
});
document.getElementById("q").addEventListener("keydown", e => {
  if (e.key === "Enter") { const b = document.querySelector("#results button"); if (b) b.click(); }
  if (e.key === "Escape") { e.target.value = ""; state.q = ""; renderResults(); render(); }
});
document.getElementById("marknew").addEventListener("change", e => { state.markNew = e.target.checked; render(); });
document.addEventListener("keydown", e => {
  if (e.key === "Escape") { if (!document.getElementById("stage").hidden) hideGame(); else closeDetail(); }
});
document.addEventListener("mouseover", e => {
  const c = e.target.closest(".tc");
  if (c && !c.title) { const t = TECH.get(c.dataset.id); c.title = `${t.name} · ${t.year}${t.replaces === "new" ? " · new" : " · the game's " + (t.vanilla && t.vanilla.name ? t.vanilla.name : t.replaces)}`; }
});

/* ---------------- start ---------------- */
(function start() {
  const h = (location.hash || "").slice(1);
  if (h.startsWith("game-") && FOLD.get(h.slice(5))) { state.tab = h.slice(5); render(); showGame(h.slice(5)); return; }
  if (h && (h === "overview" || FOLD.get(h))) { state.tab = h; if (FOLD.get(h) && FOLD.get(h).variant_of) state.dlc = false; }
  render();
})();
window.tt = { showGame, hideGame, render, state, select, layout };
