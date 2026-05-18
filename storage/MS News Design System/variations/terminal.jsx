/* global React */

// ============================================================
// VARIATION 3 — TERMINAL / DATA DASHBOARD
// Dark, dense, monospace-flavored Bloomberg-ish terminal.
// Information-dense, color-coded categories, sidebar metrics,
// ticker bar, status footer.
// ============================================================

const terminalStyles = `
  .tm-root {
    --bg: #0a0d12;
    --panel: #11161e;
    --panel-2: #161c25;
    --line: #1f2733;
    --line-soft: #182030;
    --ink: #e8eef5;
    --ink-soft: #a8b3c2;
    --ink-mute: #5a6675;
    --amber: #f5a524;
    --green: #2cb67d;
    --red: #e5484d;
    --blue: #4d9ff5;
    --violet: #9b7af3;
    font-family: 'JetBrains Mono', 'IBM Plex Mono', 'D2Coding', ui-monospace, monospace;
    background: var(--bg);
    color: var(--ink);
    width: 100%;
    min-height: 100%;
    font-size: 13px;
    line-height: 1.5;
    box-sizing: border-box;
    padding: 0;
  }
  .tm-root, .tm-root * { box-sizing: border-box; }

  /* Top status bar */
  .tm-topbar {
    display: flex; align-items: center;
    background: var(--panel-2);
    border-bottom: 1px solid var(--line);
    padding: 8px 16px;
    font-size: 11px;
    letter-spacing: 0.04em;
    color: var(--ink-soft);
    height: 32px;
  }
  .tm-topbar .lhs { display: flex; align-items: center; gap: 14px; }
  .tm-topbar .rhs { margin-left: auto; display: flex; align-items: center; gap: 14px; }
  .tm-logo {
    display: flex; align-items: center; gap: 8px;
    color: var(--amber); font-weight: 700; letter-spacing: 0.12em;
  }
  .tm-logo-box {
    width: 16px; height: 16px;
    border: 1px solid var(--amber);
    color: var(--amber);
    display: grid; place-items: center;
    font-size: 9px;
    font-weight: 700;
  }
  .tm-tab {
    padding: 4px 10px; color: var(--ink-mute);
    border-bottom: 2px solid transparent;
    cursor: pointer; height: 32px;
    display: flex; align-items: center;
    margin-top: -8px; margin-bottom: -8px;
  }
  .tm-tab.on {
    color: var(--amber);
    border-bottom-color: var(--amber);
    background: linear-gradient(180deg, transparent 60%, rgba(245,165,36,0.06));
  }
  .tm-live {
    display: inline-flex; gap: 6px; align-items: center;
    color: var(--green); font-weight: 600;
  }
  .tm-live::before {
    content: ''; width: 6px; height: 6px;
    background: var(--green); border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(44,182,125,0.18);
    animation: tmpulse 2s ease-in-out infinite;
  }
  @keyframes tmpulse { 50% { opacity: 0.4 } }

  /* Ticker */
  .tm-ticker {
    background: #0e1219; border-bottom: 1px solid var(--line);
    height: 28px; overflow: hidden; display: flex; align-items: center;
    font-size: 11px;
  }
  .tm-ticker-label {
    background: var(--amber); color: #0a0d12;
    padding: 0 12px; height: 100%;
    display: flex; align-items: center;
    font-weight: 700; letter-spacing: 0.1em;
  }
  .tm-ticker-track {
    display: flex; gap: 28px;
    padding: 0 18px;
    white-space: nowrap;
    animation: tmscroll 60s linear infinite;
  }
  @keyframes tmscroll { to { transform: translateX(-50%) } }
  .tm-ticker-item { display: inline-flex; gap: 8px; align-items: center; }
  .tm-ticker-item .cat { color: var(--amber); font-weight: 700; }

  /* Main grid */
  .tm-grid {
    display: grid;
    grid-template-columns: 260px 1fr 280px;
    height: calc(100% - 60px);
    min-height: 1100px;
  }

  .tm-panel { padding: 14px 16px; border-right: 1px solid var(--line); }
  .tm-panel:last-child { border-right: none; }

  /* Panel section */
  .tm-section { margin-bottom: 22px; }
  .tm-section-head {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--line);
    padding-bottom: 6px; margin-bottom: 10px;
  }
  .tm-section-head .ttl {
    color: var(--amber);
    font-size: 11px; letter-spacing: 0.14em;
    font-weight: 700;
  }
  .tm-section-head .right { color: var(--ink-mute); font-size: 10px; }

  /* Stats list */
  .tm-statline {
    display: flex; justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px dashed var(--line-soft);
    font-size: 12px;
  }
  .tm-statline:last-child { border-bottom: none; }
  .tm-statline .k { color: var(--ink-mute); }
  .tm-statline .v { color: var(--ink); font-weight: 600; }

  /* Distribution bars */
  .tm-bar { margin-bottom: 9px; }
  .tm-bar-row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
  .tm-bar-row .nm { color: var(--ink-soft); }
  .tm-bar-row .ct { color: var(--ink-mute); font-feature-settings: 'tnum'; }
  .tm-bar-track { height: 4px; background: var(--line); border-radius: 2px; overflow: hidden; }
  .tm-bar-fill { height: 100%; }

  /* Center main panel */
  .tm-main { padding: 18px 22px; overflow-y: auto; }
  .tm-main-head {
    display: flex; justify-content: space-between; align-items: flex-end;
    border-bottom: 1px solid var(--line);
    padding-bottom: 14px; margin-bottom: 18px;
  }
  .tm-main-head h1 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px; font-weight: 700;
    letter-spacing: -0.01em; margin: 0;
    color: var(--ink);
  }
  .tm-main-head .meta { font-size: 11px; color: var(--ink-mute); text-align: right; line-height: 1.7; }
  .tm-main-head h1 .gt { color: var(--amber); font-weight: 700; }

  /* AI report block */
  .tm-aiblock {
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 2px solid var(--amber);
    padding: 14px 18px;
    margin-bottom: 18px;
  }
  .tm-aiblock .head {
    display: flex; align-items: center; gap: 8px;
    font-size: 11px;
    letter-spacing: 0.15em;
    color: var(--amber); font-weight: 700;
    margin-bottom: 10px;
  }
  .tm-aiblock h3 {
    font-size: 16px; color: var(--ink);
    margin: 0 0 8px;
    font-weight: 600; letter-spacing: -0.01em;
  }
  .tm-aiblock p {
    font-size: 12.5px; color: var(--ink-soft);
    line-height: 1.65; margin: 0 0 6px;
  }
  .tm-aiblock .src {
    font-size: 10px; color: var(--ink-mute);
    letter-spacing: 0.06em; margin-top: 8px;
  }

  /* Section block */
  .tm-secblock {
    margin-bottom: 16px;
    border: 1px solid var(--line);
    background: var(--panel);
  }
  .tm-secblock-head {
    display: flex; align-items: center; gap: 10px;
    background: var(--panel-2);
    border-bottom: 1px solid var(--line);
    padding: 7px 14px;
    font-size: 11px;
    letter-spacing: 0.1em;
  }
  .tm-secblock-head .id {
    background: var(--amber); color: #0a0d12;
    padding: 1px 6px; font-weight: 700;
  }
  .tm-secblock-head .nm { color: var(--ink); font-weight: 600; }
  .tm-secblock-head .ct { margin-left: auto; color: var(--ink-mute); }
  .tm-secblock-body { padding: 12px 16px; }
  .tm-secblock-body p {
    font-size: 12px; color: var(--ink-soft);
    margin: 0 0 8px; line-height: 1.6;
    padding-left: 16px; position: relative;
  }
  .tm-secblock-body p::before {
    content: '>'; position: absolute; left: 0; top: 0;
    color: var(--amber); font-weight: 700;
  }

  /* Article table */
  .tm-table { width: 100%; border-collapse: collapse; font-size: 11.5px; }
  .tm-table thead th {
    text-align: left;
    color: var(--ink-mute);
    font-weight: 500;
    letter-spacing: 0.08em;
    padding: 6px 8px;
    border-bottom: 1px solid var(--line);
    font-size: 10px; text-transform: uppercase;
  }
  .tm-table tbody tr:nth-child(even) { background: rgba(255,255,255,0.012); }
  .tm-table tbody tr:hover { background: rgba(245,165,36,0.05); }
  .tm-table tbody td {
    padding: 6px 8px;
    border-bottom: 1px solid var(--line-soft);
    color: var(--ink);
    vertical-align: top;
  }
  .tm-table .time { color: var(--ink-mute); font-feature-settings: 'tnum'; width: 56px; }
  .tm-table .cat { width: 78px; }
  .tm-table .cattag {
    display: inline-block;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.06em;
  }
  .tm-table .src { color: var(--ink-mute); width: 90px; font-size: 11px; }
  .tm-table .title { color: var(--ink); }
  .tm-table a { color: inherit; text-decoration: none; }
  .tm-table a:hover { color: var(--amber); }

  /* Right panel — story digest */
  .tm-story {
    border-bottom: 1px solid var(--line);
    padding: 10px 0;
  }
  .tm-story:last-child { border-bottom: none; }
  .tm-story .tag {
    font-size: 10px; color: var(--amber);
    letter-spacing: 0.12em; font-weight: 700;
    margin-bottom: 4px;
  }
  .tm-story .h {
    font-size: 12.5px; color: var(--ink);
    line-height: 1.4; margin-bottom: 4px;
    font-weight: 500;
  }
  .tm-story .b {
    font-size: 11px; color: var(--ink-soft);
    line-height: 1.55;
    margin-bottom: 4px;
  }
  .tm-story .footer {
    display: flex; justify-content: space-between;
    font-size: 10px; color: var(--ink-mute);
  }

  /* Footer status */
  .tm-status {
    border-top: 1px solid var(--line);
    background: var(--panel-2);
    padding: 6px 16px;
    font-size: 10px;
    color: var(--ink-mute);
    display: flex; gap: 16px;
    height: 26px; align-items: center;
    letter-spacing: 0.06em;
  }
  .tm-status .ok { color: var(--green); }
  .tm-status .spacer { margin-left: auto; }
`;

const catColorMap = {
  politics: '#7a1f1f',
  security: '#1f3a5f',
  economy: '#1e6f5c',
  society: '#5a4a8a',
  world:   '#6b5b27',
  tech:    '#3b5bdb',
  markets: '#a14a07',
};
const catColorAccent = {
  politics: '#e87171',
  security: '#7fb4ff',
  economy: '#4dd2a8',
  society: '#b39ce8',
  world:   '#e5c66a',
  tech:    '#7fa9ff',
  markets: '#f5a524',
};

function Terminal({ data }) {
  return (
    <div className="tm-root">
      <style>{terminalStyles}</style>

      {/* Top bar */}
      <div className="tm-topbar">
        <div className="lhs">
          <div className="tm-logo">
            <span className="tm-logo-box">N</span>
            <span>DAILY/NEWS TERMINAL</span>
          </div>
          <span className="tm-tab on">BRIEF</span>
          <span className="tm-tab">ARCHIVE</span>
          <span className="tm-tab">SOURCES</span>
          <span className="tm-tab">KEYWORDS</span>
        </div>
        <div className="rhs">
          <span className="tm-live">LIVE</span>
          <span>KST 04:48</span>
          <span>{data.date}</span>
        </div>
      </div>

      {/* Ticker */}
      <div className="tm-ticker">
        <div className="tm-ticker-label">▸ AI BRIEF</div>
        <div className="tm-ticker-track">
          {[...data.articles.slice(0, 12), ...data.articles.slice(0, 12)].map((a, i) => (
            <span className="tm-ticker-item" key={i}>
              <span className="cat">{a.catKo.toUpperCase()}</span>
              <span style={{color:'var(--ink-soft)'}}>{a.title}</span>
              <span style={{color:'var(--ink-mute)'}}>· {a.source}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Main grid */}
      <div className="tm-grid">

        {/* LEFT PANEL */}
        <div className="tm-panel">
          <div className="tm-section">
            <div className="tm-section-head">
              <span className="ttl">▸ RUN STATUS</span>
              <span className="right">OK</span>
            </div>
            <div className="tm-statline"><span className="k">date</span><span className="v">{data.date}</span></div>
            <div className="tm-statline"><span className="k">generated</span><span className="v">04:48 KST</span></div>
            <div className="tm-statline"><span className="k">analyzer</span><span className="v">gemini-flash</span></div>
            <div className="tm-statline"><span className="k">issue</span><span className="v">#{data.issueNo}</span></div>
            <div className="tm-statline"><span className="k">runtime</span><span className="v">24.1s</span></div>
          </div>

          <div className="tm-section">
            <div className="tm-section-head">
              <span className="ttl">▸ COLLECTION</span>
              <span className="right">{data.stats.total} ITEMS</span>
            </div>
            <div className="tm-statline"><span className="k">total</span><span className="v">{data.stats.total}</span></div>
            <div className="tm-statline"><span className="k">korean</span><span className="v">{data.stats.ko}</span></div>
            <div className="tm-statline"><span className="k">english</span><span className="v">{data.stats.en}</span></div>
            <div className="tm-statline"><span className="k">ai analyzed</span><span className="v" style={{color:'var(--green)'}}>{data.stats.analyzed}</span></div>
            <div className="tm-statline"><span className="k">dedup skipped</span><span className="v" style={{color:'var(--red)'}}>{data.stats.dedupSkipped}</span></div>
          </div>

          <div className="tm-section">
            <div className="tm-section-head">
              <span className="ttl">▸ BY CATEGORY</span>
              <span className="right">DIST</span>
            </div>
            {data.catDist.map((c, i) => {
              const max = Math.max(...data.catDist.map(x => x.count));
              const pct = (c.count / max) * 100;
              return (
                <div className="tm-bar" key={i}>
                  <div className="tm-bar-row">
                    <span className="nm">{c.name}</span>
                    <span className="ct">{c.count}</span>
                  </div>
                  <div className="tm-bar-track">
                    <div className="tm-bar-fill" style={{width: pct + '%', background: c.color}} />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="tm-section">
            <div className="tm-section-head">
              <span className="ttl">▸ BY SOURCE</span>
              <span className="right">TOP 7</span>
            </div>
            {data.sourceDist.map((s, i) => (
              <div className="tm-statline" key={i}>
                <span className="k">{s.name}</span>
                <span className="v" style={{color:'var(--amber)'}}>{String(s.count).padStart(2,'0')}</span>
              </div>
            ))}
          </div>
        </div>

        {/* CENTER PANEL */}
        <div className="tm-main">
          <div className="tm-main-head">
            <h1><span className="gt">&gt;</span> daily_brief.md // {data.date}</h1>
            <div className="meta">
              {data.dateKo}<br/>
              Generated {data.generatedAt}<br/>
              <span style={{color:'var(--green)'}}>● status=success</span>
            </div>
          </div>

          {/* AI executive summary */}
          <div className="tm-aiblock">
            <div className="head">▸ EXECUTIVE SUMMARY · AI</div>
            <p>
              대통령 인도·베트남 국빈방문이 막을 올린 가운데, 호르무즈 해협 재봉쇄로 에너지 공급망이
              다시 외교의 1순위 의제로 부상했다. 산업부는 미국산 원유 도입 확대가 “불가피하다”고 못박았다.
            </p>
            <p>
              안보 측면에서는 북한이 신포에서 단거리 탄도미사일을 발사, 140㎞를 비행하며
              4·19혁명 66주년에 맞춰 긴장 수위를 높였다. 국가안보실은 안보리 결의 위반으로 규정.
            </p>
            <p>
              시장에서는 종전 기대감과 외국인 자금 유입으로 코스피 신기록 가능성이 거론되며,
              SK하이닉스의 25조 원 성과급 화제가 업계 전반의 보너스 기대를 키우고 있다.
            </p>
            <div className="src">SOURCE: 한겨레 · 연합뉴스TV · 한국경제 · 매일경제 · 전자신문 · AI타임스</div>
          </div>

          {/* Section blocks */}
          {data.sections.map((sec, i) => {
            const count = data.articles.filter(a => tmSecMatch(a.cat, sec.id)).length;
            return (
              <div className="tm-secblock" key={sec.id}>
                <div className="tm-secblock-head">
                  <span className="id">{String(i + 1).padStart(2, '0')}</span>
                  <span className="nm">{sec.title.toUpperCase()}</span>
                  <span className="ct">{count} ITEMS</span>
                </div>
                <div className="tm-secblock-body">
                  {sec.bullets.map((b, j) => <p key={j}>{b}</p>)}
                </div>
              </div>
            );
          })}

          {/* Article table */}
          <div className="tm-secblock">
            <div className="tm-secblock-head">
              <span className="id">FT</span>
              <span className="nm">FULL FEED · {data.articles.length} ITEMS</span>
              <span className="ct">SORT: TIME ↓</span>
            </div>
            <table className="tm-table">
              <thead>
                <tr>
                  <th>TIME</th>
                  <th>CAT</th>
                  <th>HEADLINE</th>
                  <th>SOURCE</th>
                </tr>
              </thead>
              <tbody>
                {data.articles.slice(0, 28).map((a, i) => (
                  <tr key={i}>
                    <td className="time">{a.time}</td>
                    <td className="cat">
                      <span className="cattag" style={{
                        background: catColorMap[a.cat] || '#333',
                        color: catColorAccent[a.cat] || '#fff'
                      }}>{a.catKo}</span>
                    </td>
                    <td className="title"><a href={a.url}>{a.title}</a></td>
                    <td className="src">{a.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="tm-panel">
          <div className="tm-section">
            <div className="tm-section-head">
              <span className="ttl">▸ TOP STORIES</span>
              <span className="right">AI · {data.highlights.length}</span>
            </div>
            {data.highlights.map((h, i) => (
              <div className="tm-story" key={i}>
                <div className="tag">#{String(i + 1).padStart(2, '0')} · {h.category}</div>
                <div className="h">{h.headline}</div>
                <div className="b">{h.blurb}</div>
                <div className="footer">
                  <span>{h.source}</span>
                  <span>{h.categoryKo}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="tm-section">
            <div className="tm-section-head">
              <span className="ttl">▸ KEYWORDS</span>
              <span className="right">WATCH</span>
            </div>
            <div style={{display:'flex', flexWrap:'wrap', gap:6}}>
              {['반도체', 'AI', '원유', '환율', '코스피', '북한', '미사일', '성과급', '연금', 'NPU', '구글', '로보택시', '동박', '엘리베이터'].map((k, i) => (
                <span key={i} style={{
                  fontSize: 10,
                  padding: '3px 8px',
                  border: '1px solid var(--line)',
                  background: 'var(--panel)',
                  color: 'var(--ink-soft)',
                  letterSpacing: '0.04em',
                }}>{k}</span>
              ))}
            </div>
          </div>

          <div className="tm-section">
            <div className="tm-section-head">
              <span className="ttl">▸ NEXT RUN</span>
              <span className="right">SCHED</span>
            </div>
            <div className="tm-statline"><span className="k">trigger</span><span className="v">cron</span></div>
            <div className="tm-statline"><span className="k">at</span><span className="v">{data.date.slice(0,-1)}{Number(data.date.slice(-1))+1} 08:00</span></div>
            <div className="tm-statline"><span className="k">in</span><span className="v" style={{color:'var(--amber)'}}>27h 12m</span></div>
            <div className="tm-statline"><span className="k">delivery</span><span className="v">resend + git</span></div>
          </div>
        </div>
      </div>

      {/* Footer status */}
      <div className="tm-status">
        <span className="ok">● OK</span>
        <span>gemini-2.0-flash</span>
        <span>resend: 1/100</span>
        <span>cache: 23h ttl</span>
        <span className="spacer">chamgil71/dailynews · gh-actions</span>
        <span>v3.2.1</span>
      </div>
    </div>
  );
}

function tmSecMatch(cat, secId) {
  if (secId === 'politics') return cat === 'politics' || cat === 'security' || cat === 'world';
  if (secId === 'economy') return cat === 'economy' || cat === 'society';
  if (secId === 'tech') return cat === 'tech';
  if (secId === 'markets') return cat === 'markets';
  return false;
}

window.Terminal = Terminal;
