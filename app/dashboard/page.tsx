"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";

/* ──────────────────────────── tokens ──────────────────────────── */

const C = {
  bg: "#0B0D0A", card: "#12150F", card2: "#171B14", line: "#232819",
  text: "#EDEFE8", dim: "#8A9382", faint: "#5A6152",
  yellow: "#F8CB46", green: "#4FBF5E", lime: "#D6E85A",
  blue: "#6AA6FF", red: "#E5614F", violet: "#B08CE8",
};

const GROUP_C: Record<string, string> = {
  DISCOVERABILITY: C.blue, TRUST: C.green, EXPERIENCE: C.violet, UNCLASSIFIED: "#4A5142",
};
const GROUP_LABEL: Record<string, string> = {
  DISCOVERABILITY: "Discoverability", TRUST: "Trust", EXPERIENCE: "Experience", UNCLASSIFIED: "Unclassified",
};
const SENT_C: Record<string, string> = {
  positive: C.green, neutral: "#8A9382", negative: C.red, mixed: C.yellow, unknown: "#4A5142",
};
const BARRIER_ROW_C: Record<string, string> = {
  awareness: C.blue, assortment: C.blue, trust: C.green, other: "#4A5142",
};

const LBL = (s: string) => String(s).replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());

const THEME_LABEL: Record<string, string> = {
  discovery_awareness: "Awareness", assortment_gap: "Assortment gap", search_findability: "Findability",
  trust_quality: "Trust & quality", quality_trust: "Trust & quality", returns_support: "Returns & support",
  delivery_ops: "Delivery", app_ux: "App experience", price_value: "Price & value",
  habit_convenience: "Habit & convenience", other: "Unclassified",
};

const TABS = ["Overview", "Discovery", "Conversations", "Competitive", "Methodology"] as const;
type Tab = typeof TABS[number];

type Row = {
  uid: string; platform: string; source: string; rating: number; text: string; date: string;
  sentiment: string; theme: string; secondary: string; group: string; categories: string[];
  discovery: boolean; barrier_label: string; segment: string; jtbd: string; quote: string; reasoning: string;
};

/* ──────────────────────────── page ──────────────────────────── */

export default function Page() {
  const [d, setD] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("Overview");
  const [q, setQ] = useState("");
  const [open, setOpen] = useState<Row | null>(null);

  useEffect(() => {
    fetch("/data.json")
      .then((r) => { if (!r.ok) throw new Error(); return r.json(); })
      .then(setD)
      .catch(() => setErr("Couldn't read /data.json. Confirm it sits in the public folder."));
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text }}>
      <Styles />
      <TopBar tab={tab} setTab={setTab} q={q} setQ={setQ} meta={d?.meta} />
      <div className="wrap">
        {err && <Empty title="Data not found" body={err} />}
        {!d && !err && <Empty title="Loading" body="Reading the classified conversation set." />}
        {d && (
          <>
            <KpiRow d={d} />
            <BarrierRail d={d} />
            {tab === "Overview" && <Overview d={d} />}
            {tab === "Discovery" && <Discovery d={d} onOpen={setOpen} />}
            {tab === "Conversations" && <Conversations d={d} q={q} onOpen={setOpen} />}
            {tab === "Competitive" && <Competitive d={d} />}
            {tab === "Methodology" && <Methodology d={d} />}
            <Footer meta={d.meta} />
          </>
        )}
      </div>
      {open && <Drawer r={open} close={() => setOpen(null)} />}
    </div>
  );
}

/* ──────────────────────────── chrome ──────────────────────────── */

function TopBar({ tab, setTab, q, setQ, meta }: any) {
  return (
    <header className="topbar">
      <div className="wrap tbInner">
        <div className="brand">
          <span className="mark">blink<span style={{ color: C.green }}>it</span></span>
          <span className="sub">flash · discovery analytics</span>
        </div>
        <nav className="tabs">
          {TABS.map((t) => (
            <button key={t} onClick={() => setTab(t)} className={"tab" + (tab === t ? " on" : "")}>{t}</button>
          ))}
        </nav>
        <input className="search" placeholder="Search conversations…" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {meta && (
        <div className="wrap ribbon">
          <span>Play Store · App Store · YouTube</span><span className="dot" />
          <span>Blinkit, Zepto, BigBasket</span><span className="dot" />
          <span>{meta.retrieved.toLocaleString()} retrieved · {meta.retrieval_pct}% retrieval rate</span>
        </div>
      )}
    </header>
  );
}

function KpiRow({ d }: any) {
  const m = d.meta;
  const neg = d.sentiment.find((s: any) => s.name === "negative")?.value ?? 0;
  const items = [
    { label: "Collected", value: m.corpus.toLocaleString(), note: "public conversations" },
    { label: "Retrieved", value: m.retrieved.toLocaleString(), note: `${m.retrieval_pct}% retrieval rate`, accent: C.violet },
    { label: "Discovery-relevant", value: m.discovery, note: `${m.discovery_pct_of_corpus}% of full corpus`, accent: C.yellow },
    { label: "Negative share", value: `${Math.round((neg / m.retrieved) * 100)}%`, note: `avg rating ${m.avg_rating}`, accent: C.red },
  ];
  return (
    <div className="kpis">
      {items.map((k) => (
        <div key={k.label} className="kpi">
          <div className="kpiLabel">{k.label}</div>
          <div className="kpiValue" style={{ color: k.accent ?? C.text }}>{k.value}</div>
          <div className="kpiNote">{k.note}</div>
        </div>
      ))}
    </div>
  );
}

/* Signature element — mirrors the deck's own barrier-mix chart exactly. */
function BarrierRail({ d }: any) {
  const rows = d.barrier_mix;
  const total = rows.reduce((a: number, r: any) => a + r.value, 0);
  const copy: Record<string, string> = {
    awareness: `"I didn't know Blinkit sold this."`,
    assortment: `"I wish they stocked this specific item."`,
    trust: `"I don't trust this category enough to buy here."`,
    other: "Mixed or too sparse to classify further",
  };
  return (
    <section className="rail">
      <div className="railHead">
        <span className="eyebrow">Where discovery breaks — barrier mix</span>
        <span className="railNote">
          Among the {total} discovery-relevant conversations found inside the {d.meta.retrieved.toLocaleString()} retrieved candidates
        </span>
      </div>
      <div className="railBars">
        {rows.map((r: any) => {
          const pct = total ? (r.value / total) * 100 : 0;
          return (
            <div key={r.name} className="railCell" style={{ flex: Math.max(pct, 10) }}>
              <div className="railFill" style={{ background: BARRIER_ROW_C[r.name] }} />
              <div className="railStage" style={{ color: BARRIER_ROW_C[r.name] }}>{r.label}</div>
              <div className="railNum">{r.value} <span>· {pct.toFixed(0)}%</span></div>
              <div className="railCopy">{copy[r.name]}</div>
            </div>
          );
        })}
      </div>
      <p className="railFoot">
        CONSIDER — whether Blinkit ever comes to mind for the purchase — barely registers here. That's not a gap in
        the method: nobody reviews a platform they never opened. Public data can see Awareness and Trust; the
        consideration gap is structurally invisible, which is why it became the priority question for primary interviews.
        Retrieval recall on this signal is {d.meta.recall_known}/{d.meta.recall_total} against an independent full-corpus
        check — the remaining gap is mostly noise (a bare URL, off-topic comments) rather than missed signal; see Methodology.
      </p>
    </section>
  );
}

/* ──────────────────────────── overview ──────────────────────────── */

function Overview({ d }: any) {
  const themes = d.theme;
  const maxT = Math.max(...themes.map((t: any) => t.value), 1);
  const sent = d.sentiment;
  const total = sent.reduce((a: number, s: any) => a + s.value, 0);

  return (
    <>
      <div className="grid2">
        <Card title="What customers talk about" hint="Primary theme across the retrieved population. Unclassified excluded.">
          <div className="hbars">
            {themes.map((t: any) => {
              const group =
                ["discovery_awareness", "assortment_gap", "search_findability"].includes(t.name) ? "DISCOVERABILITY" :
                ["trust_quality", "quality_trust", "returns_support"].includes(t.name) ? "TRUST" : "EXPERIENCE";
              return (
                <div key={t.name} className="hbar">
                  <div className="hbarLabel">{THEME_LABEL[t.name] ?? LBL(t.name)}</div>
                  <div className="hbarTrack">
                    <div className="hbarFill" style={{ width: `${(t.value / maxT) * 100}%`, background: GROUP_C[group] }} />
                  </div>
                  <div className="hbarVal">{t.value}</div>
                </div>
              );
            })}
          </div>
          <Legend2 items={[["Discoverability", C.blue], ["Trust", C.green], ["Experience friction", C.violet]]} />
        </Card>

        <Card title="Sentiment across the full corpus" hint="Classified per conversation, not derived from star rating. Scoped to the retrieved population.">
          <div className="donutRow">
            <div className="donutBox">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={sent} dataKey="value" innerRadius={58} outerRadius={88} paddingAngle={2} stroke="none">
                    {sent.map((s: any) => <Cell key={s.name} fill={SENT_C[s.name]} />)}
                  </Pie>
                  <Tooltip content={<Tip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="donutCenter">
                <div className="donutNum">{total.toLocaleString()}</div>
                <div className="donutCap">conversations</div>
              </div>
            </div>
            <div className="legendCol">
              {sent.map((s: any) => (
                <div key={s.name} className="legendRow">
                  <span className="swatch" style={{ background: SENT_C[s.name] }} />
                  <span className="legendName">{s.name}</span>
                  <span className="legendPct">{Math.round((s.value / total) * 100)}%</span>
                  <span className="legendVal">{s.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      <Card title="Categories customers raise outside groceries" hint="Category tags among retrieved conversations, excluding grocery staples and snacks.">
        <div style={{ height: 260 }}>
          <ResponsiveContainer>
            <BarChart data={d.categories.map((c: any) => ({ ...c, label: LBL(c.name) }))} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
              <CartesianGrid stroke={C.line} vertical={false} />
              <XAxis dataKey="label" tick={{ fill: C.faint, fontSize: 11 }} axisLine={false} tickLine={false} interval={0} angle={-18} textAnchor="end" height={56} />
              <YAxis tick={{ fill: C.faint, fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<Tip />} cursor={{ fill: "#ffffff08" }} />
              <Bar dataKey="value" fill={C.yellow} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </>
  );
}

/* ──────────────────────────── discovery ──────────────────────────── */

function Discovery({ d, onOpen }: any) {
  const rows: Row[] = d.rows.filter((r: Row) => r.discovery);
  const cats = d.disc_categories.slice(0, 6);
  const maxC = Math.max(...cats.map((c: any) => c.value), 1);
  return (
    <>
      <Card
        title="The discovery frontier"
        hint={`Only ${d.meta.discovery_pct}% of ${d.meta.corpus.toLocaleString()} conversations touch category discovery at all — but the signal is consistent, and it names the categories customers are surprised Blinkit carries.`}
      >
        <div className="hbars">
          {cats.map((c: any) => (
            <div key={c.name} className="hbar">
              <div className="hbarLabel">{LBL(c.name)}</div>
              <div className="hbarTrack">
                <div className="hbarFill" style={{ width: `${(c.value / maxC) * 100}%`, background: C.lime }} />
              </div>
              <div className="hbarVal">{c.value}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Read every discovery-relevant conversation" hint="All 47. Click any card for the full classification and the model's stated reasoning.">
        <div className="cards">
          {rows.map((r) => (
            <button key={r.uid} className="gcard" onClick={() => onOpen(r)}>
              <div className="gTop">
                <span className="chip">{r.platform}</span>
                {r.barrier_label !== "none" && (
                  <span className="pill" style={{ color: C.yellow, borderColor: C.yellow + "55" }}>{LBL(r.barrier_label)}</span>
                )}
                <span className="pill" style={{ color: SENT_C[r.sentiment], borderColor: SENT_C[r.sentiment] + "55" }}>{r.sentiment}</span>
              </div>
              <div className="gQuote">{r.quote || r.text.slice(0, 150)}</div>
              <div className="gMeta">
                <span>{THEME_LABEL[r.theme] ?? LBL(r.theme)}</span>
                {r.categories[0] && <><span className="dot" /><span>{LBL(r.categories[0])}</span></>}
              </div>
            </button>
          ))}
        </div>
      </Card>
    </>
  );
}

/* ──────────────────────────── conversations ──────────────────────────── */

const PAGE = 12;

function Conversations({ d, q, onOpen }: any) {
  const [f, setF] = useState({ platform: "All", group: "All", sentiment: "All", theme: "All", source: "All", onlyDiscovery: false });
  const [page, setPage] = useState(0);
  useEffect(() => { setPage(0); }, [f, q]);

  const rows: Row[] = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return d.rows.filter((r: Row) =>
      (f.platform === "All" || r.platform === f.platform) &&
      (f.group === "All" || r.group === f.group) &&
      (f.sentiment === "All" || r.sentiment === f.sentiment) &&
      (f.theme === "All" || r.theme === f.theme) &&
      (f.source === "All" || r.source === f.source) &&
      (!f.onlyDiscovery || r.discovery) &&
      (!ql || r.text.toLowerCase().includes(ql))
    );
  }, [d.rows, f, q]);

  return (
    <Card
      title="Every conversation"
      hint="All {d.meta.retrieved.toLocaleString()} retrieved conversations, classified. Click any row for the labelling rationale."
      right={
        <div className="filters">
          <Sel label="Platform" v={f.platform} set={(v: string) => setF({ ...f, platform: v })} opts={["All", ...d.platform.map((p: any) => p.name)]} />
          <Sel label="Group" v={f.group} set={(v: string) => setF({ ...f, group: v })} opts={["All", "DISCOVERABILITY", "TRUST", "EXPERIENCE", "UNCLASSIFIED"]} />
          <Sel label="Theme" v={f.theme} set={(v: string) => setF({ ...f, theme: v })} opts={["All", ...d.theme.map((t: any) => t.name)]} />
          <Sel label="Sentiment" v={f.sentiment} set={(v: string) => setF({ ...f, sentiment: v })} opts={["All", "positive", "neutral", "negative", "mixed"]} />
          <Sel label="Source" v={f.source} set={(v: string) => setF({ ...f, source: v })} opts={["All", ...d.source.map((s: any) => s.name)]} />
          <button
            className={"toggle" + (f.onlyDiscovery ? " on" : "")}
            onClick={() => setF({ ...f, onlyDiscovery: !f.onlyDiscovery })}
          >
            Discovery only
          </button>
          <button className="reset" onClick={() => setF({ platform: "All", group: "All", sentiment: "All", theme: "All", source: "All", onlyDiscovery: false })}>Reset</button>
        </div>
      }
    >
      <Table rows={rows} page={page} setPage={setPage} onOpen={onOpen} />
    </Card>
  );
}

function Table({ rows, page, setPage, onOpen }: any) {
  const pages = Math.max(1, Math.ceil(rows.length / PAGE));
  const slice = rows.slice(page * PAGE, page * PAGE + PAGE);
  if (!rows.length) return <Empty title="Nothing matches" body="Loosen a filter or clear the search." />;
  return (
    <>
      <div className="tableWrap">
        <table className="tbl">
          <thead>
            <tr>
              <th style={{ width: 88 }}>Platform</th>
              <th>Conversation</th>
              <th style={{ width: 132 }}>Theme</th>
              <th style={{ width: 118 }}>Group</th>
              <th style={{ width: 92 }}>Sentiment</th>
            </tr>
          </thead>
          <tbody>
            {slice.map((r: Row) => (
              <tr key={r.uid} onClick={() => onOpen(r)} className="clickable">
                <td>
                  <span className="chip">{r.platform}</span>
                  <div className="srcSm">{r.source}</div>
                </td>
                <td className="cell">
                  {r.text}
                  {(r.categories.length > 0 || r.discovery) && (
                    <div className="tags">
                      {r.discovery && <span className="tag hot">discovery signal</span>}
                      {r.categories.map((c) => <span key={c} className="tag">{LBL(c)}</span>)}
                    </div>
                  )}
                </td>
                <td className="muted">{THEME_LABEL[r.theme] ?? LBL(r.theme)}</td>
                <td><span className="pill" style={{ color: GROUP_C[r.group], borderColor: GROUP_C[r.group] + "55" }}>{GROUP_LABEL[r.group]}</span></td>
                <td><span className="pill" style={{ color: SENT_C[r.sentiment], borderColor: SENT_C[r.sentiment] + "55" }}>{r.sentiment}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="pager">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>← Previous</button>
        <span>Page {page + 1} of {pages} · {rows.length.toLocaleString()} conversations</span>
        <button disabled={page >= pages - 1} onClick={() => setPage(page + 1)}>Next →</button>
      </div>
    </>
  );
}

/* ──────────────────────────── competitive ──────────────────────────── */

function Competitive({ d }: any) {
  const m = d.matrix;
  const maxTrust = Math.max(...m.map((x: any) => x.trust_pct), 1);
  return (
    <>
      <Card title="Trust is the tax on expansion" hint="Share of each platform's conversations whose primary theme is trust or product quality.">
        <div className="hbars">
          {m.map((p: any) => (
            <div key={p.platform} className="hbar">
              <div className="hbarLabel" style={{ textTransform: "capitalize" }}>{p.platform}</div>
              <div className="hbarTrack">
                <div className="hbarFill" style={{ width: `${(p.trust_pct / maxTrust) * 100}%`, background: p.platform === "blinkit" ? C.yellow : "#3E4636" }} />
              </div>
              <div className="hbarVal">{p.trust_pct}%</div>
            </div>
          ))}
        </div>
        <p className="prose" style={{ marginTop: 18 }}>
          The platform pushing hardest into new categories carries the heaviest trust complaints. Expansion without
          trust scaffolding backfires — the case for building on trust Blinkit has already earned rather than
          spending to buy attention for aisles it hasn't.
        </p>
      </Card>

      <Card title="Friction mix by platform" hint="Same classification, applied across all three apps.">
        <div className="matrix">
          <div className="mRow mHead">
            <div>Platform</div><div>Conversations</div><div>Discoverability</div><div>Trust</div><div>Experience</div><div>Discovery signal</div><div>Negative</div>
          </div>
          {m.map((p: any) => (
            <div className="mRow" key={p.platform}>
              <div style={{ textTransform: "capitalize", color: p.platform === "blinkit" ? C.yellow : C.text }}>{p.platform}</div>
              <div className="num">{p.total.toLocaleString()}</div>
              <div className="num" style={{ color: C.blue }}>{p.DISCOVERABILITY}</div>
              <div className="num" style={{ color: C.green }}>{p.TRUST}</div>
              <div className="num" style={{ color: C.violet }}>{p.EXPERIENCE}</div>
              <div className="num" style={{ color: C.yellow }}>{p.discovery}</div>
              <div className="num" style={{ color: C.red }}>{p.neg_pct}%</div>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}

/* ──────────────────────────── methodology ──────────────────────────── */

function Methodology({ d }: any) {
  const m = d.meta;
  return (
    <>
      <Card title="How this was built" hint="Three steps. Retrieval narrows the corpus to candidates; classification runs only on what's retrieved.">
        <div className="funnel">
          <div className="fRow">
            <div className="fLabel">Collected</div>
            <div className="fTrack"><div className="fFill" style={{ width: "100%", background: C.dim }} /></div>
            <div className="fNum">{m.corpus.toLocaleString()}</div>
            <div className="fNote">Play Store, App Store, YouTube — Blinkit, Zepto, BigBasket</div>
          </div>
          <div className="fRow">
            <div className="fLabel">Retrieved</div>
            <div className="fTrack"><div className="fFill" style={{ width: `${m.retrieval_pct * 4.5}%`, background: C.violet }} /></div>
            <div className="fNum">{m.retrieved.toLocaleString()}</div>
            <div className="fNote">{m.retrieval_pct}% — matched a KNOW/CONSIDER/CONFIDENCE/CATEGORY/EXPLORE signal family</div>
          </div>
          <div className="fRow">
            <div className="fLabel">Discovery-relevant</div>
            <div className="fTrack"><div className="fFill" style={{ width: `${m.discovery_pct_of_retrieved * 8}%`, background: C.yellow }} /></div>
            <div className="fNum">{m.discovery}</div>
            <div className="fNote">{m.discovery_pct_of_retrieved}% of retrieved · {m.discovery_pct_of_corpus}% of the full corpus</div>
          </div>
        </div>
      </Card>

      <Card
        title="Retrieval recall — the honest number"
        hint="How much of the true discovery signal the keyword filter actually catches, checked against an independent full-corpus classification pass."
      >
        <div className="recallRow">
          <div className="recallBox">
            <div className="recallNum">{m.recall_known}<span>/{m.recall_total}</span></div>
            <div className="recallLbl">known discovery-relevant conversations retrieved</div>
          </div>
          <div className="recallBox">
            <div className="recallNum" style={{ color: C.green }}>{Math.round(100 * m.recall_known / m.recall_total)}%</div>
            <div className="recallLbl">recall, up from 43% before the filter was widened</div>
          </div>
        </div>
        <p className="prose" style={{ marginTop: 16 }}>
          The first version of the retrieval filter missed 27 of 47 known discovery-relevant conversations — mostly
          Hinglish and Devanagari phrasing ("<em>Jo kahi nahi milta wo Blinkit pe milta hai</em>" — "what you can't
          find anywhere, you find on Blinkit") and imperative YouTube-comment recommendations ("gotta try...",
          "u should try...") that the English-only keyword patterns couldn't see. Widening the filter for these
          patterns brought recall from 43% to 81% without materially inflating the candidate pool (674 → 711,
          17.8% → 18.8%).
        </p>
        <p className="prose" style={{ marginTop: 12 }}>
          The remaining 9 are a mix of likely classifier noise (a bare YouTube Shorts URL, "2nd and 3rd dress are
          beautiful," an unrelated gym-app comment) and one genuine miss — a product-quality complaint ("already
          used, mud stains, worn out") with no keyword a retrieval filter could safely match without also pulling in
          every generic damaged-delivery complaint. Chasing full coverage on that one would cost far more false
          positives than it's worth.
        </p>
      </Card>

      <Card title="What this data can and can't tell you" hint="Read this before quoting any number on a slide.">
        <div className="windows">
          {d.windows.map((w: any) => (
            <div key={w.source} className="win">
              <div className="winSrc">{w.source}</div>
              <div className="winN">{w.n.toLocaleString()} conversations</div>
              <div className="winRange">{w.start} → {w.end}</div>
              <div className="winDays">{w.days} day window</div>
            </div>
          ))}
        </div>
        <p className="prose" style={{ marginTop: 18 }}>
          The three sources return very different history — Play Store only its most recent few days, App Store
          about six weeks, YouTube over two years. Volume-over-time would measure the scraper, not customer
          behaviour, so it isn't shown here and shouldn't go on a slide. What holds up is the <em>mix</em> question —
          of the conversations that touch discovery, which barrier they land on — because that comparison is
          within-corpus, not across time.
        </p>
      </Card>
    </>
  );
}

/* ──────────────────────────── drawer ──────────────────────────── */

function Drawer({ r, close }: { r: Row; close: () => void }) {
  return (
    <div className="scrim" onClick={close}>
      <aside className="drawer" onClick={(e) => e.stopPropagation()}>
        <div className="dHead">
          <div>
            <div className="eyebrow">{r.platform} · {r.source} · {r.rating}★</div>
            <h3>{THEME_LABEL[r.theme] ?? LBL(r.theme)}</h3>
          </div>
          <button className="close" onClick={close}>Close</button>
        </div>
        <blockquote>{r.text}</blockquote>
        <dl className="kv">
          <Kv k="Friction group" v={GROUP_LABEL[r.group] ?? r.group} />
          <Kv k="Secondary theme" v={THEME_LABEL[r.secondary] ?? LBL(r.secondary)} />
          <Kv k="Discovery relevant" v={r.discovery ? "Yes" : "No"} />
          <Kv k="New-category barrier" v={LBL(r.barrier_label)} />
          <Kv k="Categories" v={r.categories.map(LBL).join(", ")} />
          <Kv k="Segment signal" v={LBL(r.segment)} />
        </dl>
        {r.jtbd && r.jtbd !== "none" && r.jtbd !== "unknown" && (
          <div className="block"><span className="eyebrow">Job to be done</span><p>{r.jtbd}</p></div>
        )}
        {r.reasoning && <div className="block"><span className="eyebrow">Why it was labelled this way</span><p>{r.reasoning}</p></div>}
      </aside>
    </div>
  );
}

const Kv = ({ k, v }: { k: string; v: string }) => (<><dt>{k}</dt><dd>{v || "—"}</dd></>);

/* ──────────────────────────── primitives ──────────────────────────── */

function Card({ title, hint, right, children }: any) {
  return (
    <section className="card">
      <div className="cardHead">
        <div><h2>{title}</h2>{hint && <p className="hint">{hint}</p>}</div>
        {right}
      </div>
      {children}
    </section>
  );
}

function Sel({ label, v, set, opts }: any) {
  return (
    <label className="sel">
      <span>{label}</span>
      <select value={v} onChange={(e) => set(e.target.value)}>
        {opts.map((o: string) => <option key={o} value={o}>{o === "All" ? "All" : LBL(o)}</option>)}
      </select>
    </label>
  );
}

function Legend2({ items }: { items: [string, string][] }) {
  return <div className="legend2">{items.map(([n, c]) => <span key={n}><i style={{ background: c }} />{n}</span>)}</div>;
}

function Tip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="tip">
      {label && <div className="tipLabel">{label}</div>}
      {payload.map((p: any) => (
        <div key={p.name} className="tipRow">
          <i style={{ background: p.color || p.payload?.fill }} />
          <span>{p.name}</span><b>{Number(p.value).toLocaleString()}</b>
        </div>
      ))}
    </div>
  );
}

const Empty = ({ title, body }: any) => (<div className="empty"><h3>{title}</h3><p>{body}</p></div>);

const Footer = ({ meta }: any) => (
  <footer className="foot">
    <span>{meta.corpus.toLocaleString()} collected · {meta.retrieved.toLocaleString()} retrieved ({meta.retrieval_pct}%) · {meta.discovery} discovery-relevant</span>
    <span>Retrieval finds candidates; classification confirms. Recall on the discovery signal: {meta.recall_known}/{meta.recall_total} against an independent check.</span>
  </footer>
);

/* ──────────────────────────── styles ──────────────────────────── */

function Styles() {
  return <style dangerouslySetInnerHTML={{ __html: CSS_TEXT }} />;
}

const CSS_TEXT = `
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:${C.bg};-webkit-font-smoothing:antialiased}
.wrap{max-width:1360px;margin:0 auto;padding:0 28px}
h1,h2,h3{margin:0;font-weight:620;letter-spacing:-.015em}
.num,.kpiValue,.hbarVal,.legendVal,.legendPct,.fNum,.railNum,.winN{font-variant-numeric:tabular-nums}

.topbar{position:sticky;top:0;z-index:40;background:${C.bg}f2;backdrop-filter:blur(10px);border-bottom:1px solid ${C.line}}
.tbInner{display:flex;align-items:center;gap:28px;height:64px}
.brand{display:flex;align-items:baseline;gap:12px;flex-shrink:0}
.mark{font-size:19px;font-weight:800;letter-spacing:-.04em;background:${C.yellow};color:#12150F;padding:3px 9px;border-radius:6px}
.sub{font-size:12px;color:${C.dim};letter-spacing:.02em}
.tabs{display:flex;gap:4px;flex:1}
.tab{background:none;border:0;color:${C.dim};font-size:13.5px;padding:8px 13px;border-radius:7px;cursor:pointer;font-family:inherit;transition:.15s}
.tab:hover{color:${C.text};background:#ffffff08}
.tab.on{color:${C.bg};background:${C.lime};font-weight:600}
.search{width:210px;background:${C.card};border:1px solid ${C.line};border-radius:8px;padding:8px 12px;color:${C.text};font-size:13px;font-family:inherit}
.search::placeholder{color:${C.faint}}
.search:focus{outline:2px solid ${C.lime}55;border-color:${C.lime}}
.ribbon{display:flex;align-items:center;gap:10px;padding-bottom:10px;font-size:11.5px;color:${C.faint};letter-spacing:.03em}
.dot{width:3px;height:3px;border-radius:50%;background:${C.faint};display:inline-block}

.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0 14px}
.kpi{background:${C.card};border:1px solid ${C.line};border-radius:12px;padding:18px 20px}
.kpiLabel{font-size:11.5px;color:${C.dim};text-transform:uppercase;letter-spacing:.07em}
.kpiValue{font-size:32px;font-weight:680;letter-spacing:-.03em;margin:8px 0 3px;line-height:1}
.kpiNote{font-size:12px;color:${C.faint}}

.rail{background:${C.card};border:1px solid ${C.line};border-radius:12px;padding:20px;margin-bottom:14px}
.railHead{display:flex;align-items:baseline;gap:14px;margin-bottom:16px;flex-wrap:wrap}
.eyebrow{font-size:10.5px;text-transform:uppercase;letter-spacing:.12em;color:${C.lime};font-weight:600}
.railNote{font-size:12.5px;color:${C.dim}}
.railBars{display:flex;gap:10px}
.railCell{min-width:0}
.railFill{height:5px;border-radius:3px;margin-bottom:12px}
.railStage{font-size:12.5px;font-weight:700;letter-spacing:.03em}
.railNum{font-size:22px;font-weight:640;letter-spacing:-.02em;margin:2px 0 4px}
.railNum span{font-size:13px;color:${C.faint};font-weight:400}
.railCopy{font-size:12.5px;color:${C.dim};line-height:1.45}
.railFoot{margin:18px 0 0;padding-top:16px;border-top:1px solid ${C.line};font-size:12.5px;color:${C.dim};line-height:1.6;max-width:92ch}

.card{background:${C.card};border:1px solid ${C.line};border-radius:12px;padding:22px;margin-bottom:14px}
.cardHead{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:20px;flex-wrap:wrap}
.card h2{font-size:16px}
.hint{margin:5px 0 0;font-size:12.5px;color:${C.dim};max-width:70ch;line-height:1.5}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.prose{font-size:13.5px;line-height:1.65;color:${C.dim};max-width:88ch;margin:0}

.hbars{display:flex;flex-direction:column;gap:11px}
.hbar{display:grid;grid-template-columns:132px 1fr 42px;align-items:center;gap:13px}
.hbarLabel{font-size:12.5px;color:${C.dim};text-align:right}
.hbarTrack{height:20px;background:#ffffff06;border-radius:4px;overflow:hidden}
.hbarFill{height:100%;border-radius:4px;transition:width .5s cubic-bezier(.4,0,.2,1)}
.hbarVal{font-size:13px;color:${C.text};font-weight:600}
.legend2{display:flex;gap:16px;margin-top:18px;font-size:11.5px;color:${C.dim};letter-spacing:.05em}
.legend2 span{display:flex;align-items:center;gap:6px}
.legend2 i{width:9px;height:9px;border-radius:2px}

.donutRow{display:flex;align-items:center;gap:22px}
.donutBox{width:190px;height:190px;position:relative;flex-shrink:0}
.donutCenter{position:absolute;inset:0;display:grid;place-content:center;text-align:center;pointer-events:none}
.donutNum{font-size:23px;font-weight:660;letter-spacing:-.02em}
.donutCap{font-size:10.5px;color:${C.faint};text-transform:uppercase;letter-spacing:.08em}
.legendCol{display:flex;flex-direction:column;gap:12px;flex:1}
.legendRow{display:grid;grid-template-columns:12px 1fr auto auto;align-items:center;gap:11px;font-size:13px}
.swatch{width:10px;height:10px;border-radius:3px}
.legendName{color:${C.dim};text-transform:capitalize}
.legendPct{color:${C.text};font-weight:600}
.legendVal{color:${C.faint};min-width:46px;text-align:right}

.funnel{display:flex;flex-direction:column;gap:14px}
.fRow{display:grid;grid-template-columns:150px 1fr 70px 1.4fr;align-items:center;gap:16px}
.fLabel{font-size:13px;color:${C.text};font-weight:600}
.fTrack{height:24px;background:#ffffff06;border-radius:5px;overflow:hidden}
.fFill{height:100%;border-radius:5px;transition:width .6s cubic-bezier(.4,0,.2,1)}
.fNum{font-size:15px;font-weight:660;text-align:right}
.fNote{font-size:12px;color:${C.faint}}

.recallRow{display:flex;gap:14px}
.recallBox{background:${C.card2};border:1px solid ${C.line};border-radius:10px;padding:16px 22px;flex:1}
.recallNum{font-size:30px;font-weight:680;letter-spacing:-.02em;color:${C.text}}
.recallNum span{font-size:16px;color:${C.faint};font-weight:400}
.recallLbl{font-size:12px;color:${C.dim};margin-top:6px;line-height:1.4}
.windows{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.win{background:${C.card2};border:1px solid ${C.line};border-radius:10px;padding:15px}
.winSrc{font-size:12.5px;color:${C.yellow};text-transform:capitalize;font-weight:600;margin-bottom:8px}
.winN{font-size:17px;font-weight:640}
.winRange{font-size:11.5px;color:${C.dim};margin-top:5px}
.winDays{font-size:11.5px;color:${C.faint};margin-top:2px}

.filters{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.sel{display:flex;align-items:center;gap:7px;background:${C.card2};border:1px solid ${C.line};border-radius:8px;padding:6px 10px}
.sel span{font-size:11px;color:${C.faint};text-transform:uppercase;letter-spacing:.06em}
.sel select{background:none;border:0;color:${C.text};font-size:12.5px;font-family:inherit;cursor:pointer;outline:none}
.sel select option{background:${C.card2}}
.reset{background:none;border:1px solid ${C.line};color:${C.dim};font-size:12.5px;padding:7px 13px;border-radius:8px;cursor:pointer;font-family:inherit}
.reset:hover{color:${C.text};border-color:${C.faint}}
.toggle{background:none;border:1px solid ${C.line};color:${C.dim};font-size:12.5px;padding:7px 13px;border-radius:8px;cursor:pointer;font-family:inherit}
.toggle.on{background:${C.yellow}22;border-color:${C.yellow};color:${C.yellow}}

.tableWrap{overflow-x:auto;margin:0 -22px;padding:0 22px}
.tbl{width:100%;border-collapse:collapse;font-size:13px}
.tbl th{text-align:left;font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:${C.faint};font-weight:600;padding:0 12px 11px 0;border-bottom:1px solid ${C.line}}
.tbl td{padding:14px 12px 14px 0;border-bottom:1px solid ${C.line};vertical-align:top}
.clickable{cursor:pointer}
.clickable:hover td{background:#ffffff06}
.cell{color:${C.text};line-height:1.55;max-width:620px}
.muted{color:${C.dim};font-size:12.5px}
.srcSm{font-size:10.5px;color:${C.faint};margin-top:5px}
.chip{display:inline-block;background:#ffffff0d;color:${C.dim};font-size:11px;padding:3px 8px;border-radius:5px;text-transform:capitalize}
.pill{display:inline-block;border:1px solid;font-size:10.5px;padding:2px 8px;border-radius:20px;letter-spacing:.04em;white-space:nowrap}
.tags{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.tag{font-size:10.5px;color:${C.lime};background:${C.lime}14;padding:2px 7px;border-radius:4px}
.tag.hot{color:${C.yellow};background:${C.yellow}18}
.pager{display:flex;justify-content:space-between;align-items:center;margin-top:18px;font-size:12.5px;color:${C.dim}}
.pager button{background:${C.card2};border:1px solid ${C.line};color:${C.text};font-size:12.5px;padding:7px 14px;border-radius:8px;cursor:pointer;font-family:inherit}
.pager button:disabled{opacity:.35;cursor:not-allowed}
.pager button:not(:disabled):hover{border-color:${C.lime}}

.matrix{font-size:13px}
.mRow{display:grid;grid-template-columns:1fr .9fr .9fr .7fr .8fr .9fr .7fr;gap:10px;padding:13px 0;border-bottom:1px solid ${C.line}}
.mHead{font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:${C.faint};font-weight:600}
.mRow>div:not(:first-child){text-align:right}

.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.gcard{background:${C.card2};border:1px solid ${C.line};border-radius:10px;padding:16px;text-align:left;cursor:pointer;font-family:inherit;transition:.15s}
.gcard:hover{border-color:${C.lime}66;transform:translateY(-1px)}
.gTop{display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap}
.gQuote{font-size:13px;color:${C.text};line-height:1.55;margin-bottom:11px}
.gMeta{display:flex;align-items:center;gap:8px;font-size:11.5px;color:${C.faint}}

.scrim{position:fixed;inset:0;background:#000000aa;z-index:60;display:flex;justify-content:flex-end}
.drawer{width:min(540px,100%);height:100%;background:${C.card};border-left:1px solid ${C.line};padding:26px;overflow-y:auto}
.dHead{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:18px}
.dHead h3{font-size:17px;margin-top:6px}
.close{background:none;border:1px solid ${C.line};color:${C.dim};font-size:12.5px;padding:6px 12px;border-radius:8px;cursor:pointer;font-family:inherit}
.drawer blockquote{margin:0 0 22px;padding:15px 17px;background:#ffffff06;border-left:2px solid ${C.yellow};border-radius:0 8px 8px 0;font-size:13.5px;line-height:1.6;color:${C.text}}
.kv{display:grid;grid-template-columns:auto 1fr;gap:9px 18px;margin:0 0 22px;font-size:13px}
.kv dt{color:${C.faint};font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;padding-top:2px}
.kv dd{margin:0;color:${C.text}}
.block{margin-bottom:20px}
.block p{margin:7px 0 0;font-size:13px;line-height:1.6;color:${C.dim}}

.tip{background:${C.card2};border:1px solid ${C.line};border-radius:8px;padding:10px 12px;font-size:12px;box-shadow:0 8px 24px #0008}
.tipLabel{color:${C.dim};margin-bottom:6px;font-size:11px}
.tipRow{display:flex;align-items:center;gap:8px;padding:2px 0}
.tipRow i{width:8px;height:8px;border-radius:2px}
.tipRow b{margin-left:auto;font-variant-numeric:tabular-nums}

.empty{text-align:center;padding:64px 20px;color:${C.dim}}
.empty h3{font-size:15px;color:${C.text};margin-bottom:7px}
.empty p{font-size:13px;margin:0}
.foot{display:flex;justify-content:space-between;gap:20px;padding:26px 0 40px;font-size:11.5px;color:${C.faint};flex-wrap:wrap}

@media(max-width:1000px){
 .kpis{grid-template-columns:repeat(2,1fr)}
 .grid2,.windows{grid-template-columns:1fr}
 .railBars{flex-direction:column}
 .fRow{grid-template-columns:110px 1fr 56px}
 .fNote{display:none}
 .donutRow{flex-direction:column;align-items:flex-start}
 .tbInner{height:auto;padding:12px 0;flex-wrap:wrap}
 .search{width:100%;order:3}
 .mRow{grid-template-columns:1fr 1fr 1fr;font-size:12px}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
`;
