// Self-presentation deck for one interview, in the style of the first model deck (13 Oct 2026).
// node build_deck.js specs/<spec>.json <out.pptx>
// Shared slides (about me, the projects, instruments) come from profile_deck.json next to this file
// (DECK_PROFILE overrides the path): only PROFILE.md / DEFENSIBLE_CLAIMS.md facts go there.
// The spec gives the host slides, the order of the projects, the language (en | fr) and the notes.
// Since 17 Oct 2026 the slide set and notes follow the edited model deck: no lessons slide,
// no "Three things the numbers told me" slide, no agenda notes; notes say the slide simply, then the
// result, and put over-explanation between // and // (kept for questions, not said).
// Since 18 Oct 2026 (v19) no personal content is in this file: the same code runs in every campaign.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const JSZip = require("jszip");

const SP = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = process.argv[3];
const ME = JSON.parse(fs.readFileSync(process.env.DECK_PROFILE || path.join(__dirname, "profile_deck.json"), "utf8"));
const FR = SP.lang === "fr";
const L2 = (en, fr) => (FR ? fr : en);
const LL = x => (x && typeof x === "object" && !Array.isArray(x) && "en" in x ? L2(x.en, x.fr) : x);

const INK = "1D1D1F", GRAY = "6E6E73", LIGHT = "F5F5F7", ACC = "5E5CE6", WHITE = "FFFFFF", BLACK = "000000", DIM = "A1A1A6";
const H = "Segoe UI Semibold", B = "Segoe UI", LT = "Segoe UI Light";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.author = ME.author;
pres.title = SP.title.replace(/\n/g, " ");
pres.theme = { headFontFace: H, bodyFontFace: B };

// every animated object is registered per slide, in order; eyebrow and title stay static
const plan = [];
let cur;
const slide = (dark) => { const s = pres.addSlide(); s.background = { color: dark ? BLACK : WHITE }; cur = []; plan.push(cur); return s; };
const nb = x => typeof x === "string" ? x.replace(/(\d) (µM|nm|°C|h|eV|wt%|cm|S\/cm|weeks|semaines|min|%)(?=[\s,.:;)]|$)/g, "$1 $2") : x.map(r => Object.assign({}, r, { text: nb(r.text) }));
const t = (s, text, o) => { if (o.anim !== false) cur.push(o.objectName); delete o.anim; s.addText(nb(text), Object.assign({ isTextBox: true, margin: 0, fontFace: B, color: INK, valign: "top" }, o)); };
const box = (s, kind, o) => { cur.push(o.objectName); s.addShape(kind, o); };
const eyebrow = (s, text, dark) => t(s, text, { x: 0.8, y: 0.55, w: 11.7, h: 0.35, fontSize: 13, color: dark ? DIM : GRAY, objectName: "eyebrow", anim: false });
const title = (s, text) => t(s, text, { x: 0.8, y: 0.95, w: 11.7, h: 1.2, fontSize: 38, fontFace: H, color: INK, objectName: "title", anim: false });
const RR = () => pres.shapes.ROUNDED_RECTANGLE;
const N = SP.notes || {};
const note = (s, key, base) => s.addNotes([base, N[key]].filter(Boolean).join(" "));

// ---------- 1. Title (dark)
let s = slide(true);
t(s, SP.host_line, { x: 0.8, y: 1.6, w: 8, h: 0.4, fontSize: 16, color: DIM, objectName: "t1eyebrow" });
t(s, SP.title, { x: 0.8, y: 2.15, w: 7.6, h: 2.6, fontSize: 66, fontFace: H, color: WHITE, objectName: "t1title" });
t(s, LL(ME.title_sub), { x: 0.8, y: 5.0, w: 8, h: 0.9, fontSize: 16, color: DIM, objectName: "t1sub", paraSpaceAfter: 4 });
box(s, RR(), { x: 9.0, y: 2.0, w: 3.3, h: 3.3, rectRadius: 0.5, fill: { color: "1C1C1E" }, line: { color: "1C1C1E" }, objectName: "t1block" });
box(s, pres.shapes.OVAL, { x: 9.95, y: 2.95, w: 1.4, h: 1.4, fill: { color: BLACK }, line: { color: "3A3A3C", width: 1.5 }, objectName: "t1cav" });
box(s, pres.shapes.OVAL, { x: 10.1, y: 3.1, w: 1.1, h: 1.1, fill: { color: ACC }, line: { color: ACC }, objectName: "t1mol" });
note(s, "title");

// ---------- 2. About me
s = slide();
eyebrow(s, L2("About me", "Qui je suis"));
title(s, LL(ME.about.title));
LL(ME.about.stats).forEach(([n, l], i) => {
  const x = 0.8 + i * 4.05;
  box(s, RR(), { x, y: 2.75, w: 3.7, h: 3.2, rectRadius: 0.25, fill: { color: LIGHT }, line: { color: LIGHT }, objectName: `st${i}` });
  t(s, n, { x: x + 0.4, y: 3.0, w: 3.0, h: 1.4, fontSize: 72, fontFace: LT, color: i === 0 ? ACC : INK, objectName: `stn${i}` });
  t(s, l, { x: x + 0.4, y: 4.55, w: 3.0, h: 1.1, fontSize: 17, color: GRAY, objectName: `stl${i}` });
});
t(s, LL(ME.about.foot), { x: 0.8, y: 6.35, w: 11.7, h: 0.4, fontSize: 14, color: GRAY, objectName: "aboutfoot" });
note(s, "about", LL(ME.about.notes));

// ---------- 3. Agenda
s = slide();
eyebrow(s, L2("Today", "Aujourd'hui"));
title(s, SP.agenda_title);
SP.agenda.forEach((a, i) => {
  const y = 2.55 + i * 1.0;
  t(s, `0${i + 1}`, { x: 0.8, y, w: 1.0, h: 0.7, fontSize: 30, fontFace: LT, color: ACC, objectName: `agn${i}` });
  t(s, a, { x: 1.9, y: y + 0.06, w: 9.5, h: 0.7, fontSize: 26, color: INK, objectName: `aga${i}` });
});
// the agenda slide has no notes (17 Oct 2026)

// ---------- the projects, in the order the spec asks (spec "order" = keys of profile_deck.json "projects")
const num = k => `0${SP.order.indexOf(k) + 1}`;

// slide layouts for project slides; each one draws from a profile_deck.json slide entry (P)
const LAYOUT = {
  // two coloured circles (before / after), three numbered facts on the right, a caption
  two_states(s, P) {
    P.states.forEach((st, i) => {
      const x = [0.9, 4.6][i];
      box(s, pres.shapes.OVAL, { x, y: 2.75, w: 2.4, h: 2.4, fill: { color: st.color }, line: { color: st.color }, objectName: st.name });
      if (i === 0) t(s, "→", { x: 3.45, y: 3.45, w: 1.0, h: 1.0, fontSize: 44, fontFace: LT, color: GRAY, align: "center", objectName: "arr" });
    });
    P.states.forEach((st, i) => t(s, LL(st.label), { x: [0.9, 4.6][i], y: 5.35, w: 2.4, h: 0.8, fontSize: 15, color: GRAY, align: "center", objectName: st.name + "l" }));
    LL(P.facts).forEach(([n, l], i) => {
      const y = 2.55 + i * 1.3;
      t(s, n, { x: 8.0, y, w: 1.9, h: 0.8, fontSize: 30, fontFace: LT, color: ACC, objectName: `f4n${i}` });
      t(s, l, { x: 9.95, y: y + 0.05, w: 3.0, h: 1.0, fontSize: 14, color: INK, objectName: `f4l${i}` });
    });
    t(s, LL(P.caption), { x: 0.8, y: 6.45, w: 11.7, h: 0.6, fontSize: 12, color: GRAY, objectName: "c4" });
  },
  // horizontal bar chart of candidate signals, two big numbers on the right, a caption
  signal_chart(s, P) {
    s.addChart(pres.charts.BAR, [{ name: P.chart.name, labels: LL(P.chart.labels), values: P.chart.values }], {
      x: 0.6, y: 2.3, w: 7.4, h: 4.3, barDir: "bar", catAxisOrientation: "maxMin", valAxisMinVal: P.chart.min, valAxisMaxVal: P.chart.max, valAxisMajorUnit: 0.1,
      chartColors: [ACC].concat(P.chart.values.slice(1).map(() => "C7C7CC")), barGapWidthPct: 45,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: P.chart.format, dataLabelFontFace: B, dataLabelFontSize: 12, dataLabelColor: INK,
      catAxisLabelFontFace: B, catAxisLabelFontSize: 13, catAxisLabelColor: INK, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      catAxisLineShow: false, showLegend: false, showTitle: false, objectName: "chart5",
    });
    cur.push("chart5");
    P.big.forEach((b, i) => {
      t(s, LL(b.value), { x: 8.6, y: [2.45, 4.2][i], w: 4.2, h: 1.0, fontSize: 48, fontFace: LT, color: i === 0 ? ACC : INK, objectName: `lod${i + 1}` });
      t(s, LL(b.label), { x: 8.6, y: [3.45, 5.2][i], w: 4.2, h: [0.5, 0.8][i], fontSize: 14, color: GRAY, objectName: `lod${i + 1}l` });
    });
    t(s, LL(P.caption), { x: 0.8, y: 6.65, w: 11.7, h: 0.5, fontSize: 12, color: GRAY, objectName: "c5" });
  },
  // five process steps (one highlighted), three key results, a caption
  process(s, P) {
    LL(P.steps).forEach(([a, b], i) => {
      const x = 0.8 + i * 2.38, hi = i === P.highlight;
      box(s, RR(), { x, y: 2.5, w: 2.1, h: 2.1, rectRadius: 0.25, fill: { color: hi ? ACC : LIGHT }, line: { color: hi ? ACC : LIGHT }, objectName: `p7b${i}` });
      t(s, a, { x: x + 0.25, y: 2.75, w: 1.7, h: 0.5, fontSize: 20, fontFace: H, color: hi ? WHITE : INK, objectName: `p7a${i}` });
      t(s, b, { x: x + 0.25, y: 3.4, w: 1.75, h: 1.0, fontSize: 13, color: hi ? WHITE : GRAY, objectName: `p7c${i}` });
    });
    LL(P.results).forEach(([n, l], i) => {
      const x = 0.8 + i * 4.0;
      t(s, n, { x, y: 5.0, w: 3.8, h: 0.6, fontSize: 24, fontFace: LT, color: INK, objectName: `p7n${i}` });
      t(s, l, { x, y: 5.6, w: 3.7, h: 0.5, fontSize: 13, color: GRAY, objectName: `p7l${i}` });
    });
    t(s, LL(P.caption), { x: 0.8, y: 6.55, w: 11.7, h: 0.5, fontSize: 12, color: GRAY, objectName: "c7" });
  },
  // three big numbers with a unit and a line each, then the spec's take-away line
  three_numbers(s, P) {
    LL(P.numbers).forEach(([n, u, l], i) => {
      const x = 0.8 + i * 4.0;
      t(s, [{ text: n, options: { fontSize: 60, fontFace: LT, color: i === 0 ? ACC : INK } }, { text: " " + u, options: { fontSize: 18, color: GRAY } }], { x, y: 2.6, w: 3.8, h: 1.2, objectName: `f8n${i}` });
      t(s, l, { x, y: 3.95, w: 3.5, h: 1.6, fontSize: 15, color: INK, objectName: `f8l${i}` });
    });
    t(s, SP[P.take_key], { x: 0.8, y: 6.1, w: 11.7, h: 0.8, fontSize: 17, fontFace: H, color: INK, objectName: "f8take" });
  },
};

function project(key) {
  const PR = ME.projects[key];
  if (!PR) throw new Error(`spec order names "${key}", not a project in profile_deck.json`);
  PR.slides.forEach((P, k) => {
    const s = slide();
    eyebrow(s, k === 0 ? `${num(key)}  ·  ${SP[key + "_label"]}  ·  ${LL(P.eyebrow)}` : `${num(key)}  ·  ${LL(P.eyebrow)}`);
    title(s, LL(P.title));
    LAYOUT[P.layout](s, P);
    note(s, P.note_key, LL(P.notes));
  });
  // optional deeper slides, when the host asked for a presentation of this work (spec "<key>_extra")
  (SP[key + "_extra"] || []).forEach((x, k) => {
    const s = slide();
    eyebrow(s, `${num(key)}  ·  ${x.eyebrow}`);
    title(s, x.title);
    x.rows.forEach(([a, b], i) => {
      const y = 2.35 + i * 1.3;
      box(s, RR(), { x: 0.8, y, w: 11.7, h: 1.1, rectRadius: 0.2, fill: { color: LIGHT }, line: { color: LIGHT }, objectName: `px${k}b${i}` });
      t(s, a, { x: 1.15, y: y + 0.27, w: 3.4, h: 0.6, fontSize: 22, fontFace: H, color: i === 0 ? ACC : INK, objectName: `px${k}a${i}` });
      t(s, b, { x: 4.7, y: y + 0.15, w: 7.5, h: 0.85, fontSize: 15, color: INK, valign: "middle", objectName: `px${k}v${i}` });
    });
    if (x.take) t(s, x.take, { x: 0.8, y: 6.3, w: 11.7, h: 0.7, fontSize: 15, fontFace: H, color: INK, objectName: `px${k}take` });
    note(s, `${key}_extra${k}`);
  });
}

SP.order.forEach(project);

// ---------- Instruments (last card: what I have not done yet, for this host)
s = slide();
eyebrow(s, `${num(SP.order[1])}  ·  ${L2("Instruments", "Instruments")}`);
title(s, LL(ME.instruments.title));
LL(ME.instruments.cards).concat([SP.not_yet]).forEach(([a, b], i) => {
  const x = 0.8 + (i % 4) * 2.98, y = 2.45 + Math.floor(i / 4) * 2.05, last = i === 7;
  box(s, RR(), { x, y, w: 2.75, h: 1.8, rectRadius: 0.22, fill: { color: last ? WHITE : LIGHT }, line: { color: last ? ACC : LIGHT, width: 1.5, dashType: last ? "dash" : "solid" }, objectName: `i9b${i}` });
  t(s, a, { x: x + 0.25, y: y + 0.3, w: 2.3, h: 0.6, fontSize: 18, fontFace: H, color: last ? ACC : INK, objectName: `i9a${i}` });
  t(s, b, { x: x + 0.25, y: y + 0.95, w: 2.35, h: 0.7, fontSize: 13, color: GRAY, objectName: `i9c${i}` });
});
note(s, "instruments", LL(ME.instruments.notes));

// ---------- How I understand your research: three steps
s = slide();
eyebrow(s, `03  ·  ${L2("How I understand your research", "Ce que je comprends de vos recherches")}`);
title(s, SP.understand.title);
SP.understand.steps.forEach(([a, b], i) => {
  const x = 0.8 + i * 4.0;
  box(s, RR(), { x, y: 2.5, w: 3.6, h: 3.3, rectRadius: 0.25, fill: { color: i === 2 ? ACC : LIGHT }, line: { color: i === 2 ? ACC : LIGHT }, objectName: `u10b${i}` });
  t(s, `0${i + 1}`, { x: x + 0.3, y: 2.75, w: 1.0, h: 0.6, fontSize: 26, fontFace: LT, color: i === 2 ? WHITE : ACC, objectName: `u10n${i}` });
  t(s, a, { x: x + 0.3, y: 3.45, w: 3.0, h: 0.8, fontSize: 20, fontFace: H, color: i === 2 ? WHITE : INK, objectName: `u10a${i}` });
  t(s, b, { x: x + 0.3, y: 4.3, w: 3.0, h: 1.4, fontSize: 14, color: i === 2 ? WHITE : GRAY, objectName: `u10c${i}` });
  if (i < 2) t(s, "→", { x: x + 3.6, y: 3.7, w: 0.4, h: 0.6, fontSize: 26, fontFace: LT, color: GRAY, align: "center", objectName: `u10x${i}` });
});
t(s, SP.understand.caption, { x: 0.8, y: 6.35, w: 11.7, h: 0.6, fontSize: 14, color: GRAY, objectName: "u10cap" });
note(s, "understand");

// ---------- What I read about your group
s = slide();
eyebrow(s, `03  ·  ${L2("What I read about your group", "Ce que j'ai lu sur votre équipe")}`);
title(s, SP.group.title);
SP.group.cards.forEach((c, i) => {
  const x = 0.8 + (i % 2) * 6.0, y = 2.4 + Math.floor(i / 2) * 2.15;
  box(s, RR(), { x, y, w: 5.7, h: 1.9, rectRadius: 0.22, fill: { color: LIGHT }, line: { color: LIGHT }, objectName: `g11b${i}` });
  t(s, c.head, { x: x + 0.3, y: y + 0.25, w: 5.1, h: 0.5, fontSize: 18, fontFace: H, color: INK, objectName: `g11h${i}` });
  t(s, c.body, { x: x + 0.3, y: y + 0.8, w: 5.1, h: 0.95, fontSize: 13, color: GRAY, objectName: `g11t${i}` });
});
note(s, "group");

// ---------- Where I could contribute
s = slide();
eyebrow(s, `04  ·  ${L2("Where I could contribute", "Où je pourrais contribuer")}`);
title(s, SP.contribute.title);
SP.contribute.items.forEach(([a, b], i) => {
  const x = 0.8 + i * 4.0;
  t(s, `0${i + 1}`, { x, y: 2.5, w: 1.0, h: 0.6, fontSize: 26, fontFace: LT, color: ACC, objectName: `c12n${i}` });
  t(s, a, { x, y: 3.15, w: 3.6, h: 0.55, fontSize: 21, fontFace: H, color: INK, objectName: `c12a${i}` });
  t(s, b, { x, y: 3.8, w: 3.55, h: 1.9, fontSize: 15, color: GRAY, objectName: `c12b${i}` });
});
t(s, SP.contribute.take, { x: 0.8, y: 6.15, w: 11.7, h: 0.7, fontSize: 16, fontFace: H, color: INK, objectName: "c12take" });
note(s, "contribute");

// ---------- Practical + close (dark)
s = slide(true);
t(s, L2("Thank you.", "Merci."), { x: 0.8, y: 1.5, w: 11.7, h: 1.4, fontSize: 66, fontFace: H, color: WHITE, objectName: "end" });
(SP.practical || LL(ME.practical)).forEach(([a, b], i) => {
  const x = 0.8 + i * 4.0;
  t(s, a, { x, y: 3.9, w: 3.8, h: 0.6, fontSize: 21, fontFace: H, color: WHITE, objectName: `e13a${i}` });
  t(s, b, { x, y: 4.5, w: 3.7, h: 0.6, fontSize: 15, color: DIM, objectName: `e13b${i}` });
});
t(s, ME.contact_line, { x: 0.8, y: 6.4, w: 11.7, h: 0.4, fontSize: 13, color: DIM, objectName: "e13c" });
note(s, "end");

// ---------- builds: fade transition, objects fade in one after another on slide start (as the first model deck)
function timing(spids) {
  let n = 3;
  const eff = spids.map((sp, i) =>
    `<p:par><p:cTn id="${++n}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" nodeType="${i ? "withEffect" : "afterEffect"}">` +
    `<p:stCondLst><p:cond delay="${i * 280}"/></p:stCondLst><p:childTnLst>` +
    `<p:set><p:cBhvr><p:cTn id="${++n}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>` +
    `<p:tgtEl><p:spTgt spid="${sp}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>` +
    `<p:to><p:strVal val="visible"/></p:to></p:set>` +
    `<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="${++n}" dur="550"/>` +
    `<p:tgtEl><p:spTgt spid="${sp}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>`).join("");
  return '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>' +
    '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>' +
    '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>' +
    `<p:par><p:cTn id="${++n}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>` + eff +
    '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>' +
    '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>' +
    '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>' +
    '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>';
}

pres.write({ outputType: "nodebuffer" }).then(async buf => {
  const zip = await JSZip.loadAsync(buf);
  for (let i = 0; i < plan.length; i++) {
    const f = `ppt/slides/slide${i + 1}.xml`;
    let xml = await zip.file(f).async("string");
    const ids = {};
    for (const m of xml.matchAll(/<p:cNvPr id="(\d+)" name="([^"]*)"/g)) ids[m[2]] = m[1];
    const missing = plan[i].filter(a => !ids[a]);
    if (missing.length) throw new Error(`slide ${i + 1}: no shape named ${missing}`);
    if (!xml.includes("</p:clrMapOvr>")) xml = xml.replace("</p:cSld>", "</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>");
    xml = xml.replace("</p:clrMapOvr>", '</p:clrMapOvr><p:transition spd="med"><p:fade/></p:transition>' + timing(plan[i].map(a => ids[a])));
    zip.file(f, xml);
  }
  fs.writeFileSync(out, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  console.log("wrote", out, plan.length, "slides");
});
