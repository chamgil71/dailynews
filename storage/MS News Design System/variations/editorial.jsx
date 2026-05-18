/* global React */

// ============================================================
// VARIATION 1 — EDITORIAL / NEWSPAPER
// Korean newspaper-inspired masthead, serif headlines,
// multi-column flow, ruled lines, condensed metadata.
// ============================================================

const editorialStyles = `
  .ed-root {
    --ink: #1a1612;
    --ink-soft: #4a4036;
    --ink-mute: #8a7e6f;
    --paper: #f4ede0;
    --paper-2: #ece2cf;
    --rule: #2b231a;
    --rule-soft: #c8bda7;
    --accent: #8b2a1f;
    font-family: 'Noto Serif KR', 'Source Serif Pro', Georgia, serif;
    background: var(--paper);
    color: var(--ink);
    width: 100%;
    min-height: 100%;
    padding: 36px 44px 56px;
    line-height: 1.55;
    box-sizing: border-box;
  }
  .ed-root, .ed-root * { box-sizing: border-box; }

  /* Masthead */
  .ed-masthead {
    border-top: 6px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 14px 0 10px;
    margin-bottom: 18px;
  }
  .ed-masthead-top {
    display: flex; justify-content: space-between; align-items: baseline;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; letter-spacing: 0.12em;
    color: var(--ink-soft);
    text-transform: uppercase;
    border-bottom: 1px solid var(--rule-soft);
    padding-bottom: 8px;
    margin-bottom: 14px;
  }
  .ed-title {
    font-family: 'Noto Serif KR', serif;
    font-weight: 900;
    font-size: 88px;
    letter-spacing: -0.04em;
    line-height: 0.92;
    text-align: center;
    margin: 6px 0 2px;
    font-style: italic;
  }
  .ed-title em { color: var(--accent); font-style: italic; }
  .ed-tagline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.3em;
    text-align: center;
    color: var(--ink-soft);
    text-transform: uppercase;
    padding-top: 6px;
    border-top: 1px solid var(--rule-soft);
    margin-top: 10px;
  }

  /* Briefing row */
  .ed-briefing {
    display: grid;
    grid-template-columns: 220px 1fr 180px;
    gap: 0;
    border-bottom: 1px solid var(--rule);
    padding: 16px 0 18px;
    margin-bottom: 28px;
  }
  .ed-briefing-left { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--ink-soft); }
  .ed-briefing-left .lbl { color: var(--ink); font-weight: 600; display: block; margin-bottom: 4px; letter-spacing: 0.08em; }
  .ed-briefing-stat { display: flex; gap: 14px; align-items: baseline; margin-top: 8px; }
  .ed-briefing-stat .num { font-family: 'Noto Serif KR', serif; font-size: 26px; font-weight: 700; font-style: italic; }
  .ed-briefing-stat .lab { font-size: 10px; letter-spacing: 0.15em; color: var(--ink-mute); text-transform: uppercase; }
  .ed-kicker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 6px;
    border-left: 3px solid var(--accent);
    padding-left: 12px;
  }
  .ed-lede {
    font-family: 'Noto Serif KR', serif;
    font-size: 26px; line-height: 1.35;
    font-weight: 500;
    padding: 0 14px;
    text-wrap: balance;
  }
  .ed-byline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--ink-mute);
    text-align: right;
    line-height: 1.7;
    border-left: 1px solid var(--rule-soft);
    padding-left: 14px;
  }

  /* Highlights cards row */
  .ed-headlines {
    display: grid;
    grid-template-columns: 1.4fr 1fr 1fr;
    gap: 0;
    border-bottom: 3px double var(--rule);
    padding-bottom: 26px;
    margin-bottom: 30px;
  }
  .ed-hl {
    padding: 6px 22px;
    border-left: 1px solid var(--rule-soft);
  }
  .ed-hl:first-child { padding-left: 0; border-left: none; }
  .ed-hl-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; letter-spacing: 0.18em;
    color: var(--accent); margin-bottom: 8px;
    text-transform: uppercase;
  }
  .ed-hl h2 {
    font-family: 'Noto Serif KR', serif;
    font-size: 22px; line-height: 1.25;
    font-weight: 800;
    margin: 0 0 10px;
    text-wrap: balance;
  }
  .ed-hl:first-child h2 { font-size: 30px; line-height: 1.2; }
  .ed-hl p {
    font-size: 14px; color: var(--ink-soft);
    line-height: 1.6; margin: 0 0 8px;
  }
  .ed-hl-src { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--ink-mute); letter-spacing: 0.08em; }

  /* Section block */
  .ed-section { margin-bottom: 32px; }
  .ed-section-head {
    display: flex; align-items: baseline; gap: 14px;
    border-bottom: 2px solid var(--rule);
    padding-bottom: 8px; margin-bottom: 16px;
  }
  .ed-section-head h3 {
    font-family: 'Noto Serif KR', serif;
    font-size: 24px; font-weight: 800; margin: 0;
    letter-spacing: -0.02em;
  }
  .ed-section-head .ed-section-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: var(--ink-mute);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-left: auto;
  }

  .ed-summary {
    columns: 2;
    column-gap: 32px;
    column-rule: 1px solid var(--rule-soft);
    font-size: 15px; line-height: 1.7;
    margin-bottom: 18px;
  }
  .ed-summary p {
    margin: 0 0 12px;
    break-inside: avoid;
    text-indent: 1.2em;
  }
  .ed-summary p:first-child { text-indent: 0; }
  .ed-summary p:first-child::first-letter {
    font-family: 'Noto Serif KR', serif;
    font-size: 56px; font-weight: 800;
    float: left; line-height: 0.9;
    padding: 4px 8px 0 0; color: var(--accent);
  }

  /* Article list */
  .ed-list {
    columns: 2; column-gap: 32px; column-rule: 1px solid var(--rule-soft);
    border-top: 1px solid var(--rule-soft);
    padding-top: 14px;
  }
  .ed-list-item {
    break-inside: avoid;
    display: grid; grid-template-columns: 44px 1fr;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px dotted var(--rule-soft);
  }
  .ed-list-item .ed-li-time {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: var(--ink-mute);
    padding-top: 3px;
  }
  .ed-list-item .ed-li-title {
    font-size: 14px; line-height: 1.45;
    color: var(--ink);
  }
  .ed-list-item .ed-li-src {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: var(--ink-mute);
    letter-spacing: 0.06em;
    margin-top: 2px;
  }
  .ed-li-cat {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-transform: uppercase;
    margin-right: 6px;
    vertical-align: 1px;
  }

  /* Section header for big "TODAY'S BRIEF" hero */
  .ed-eyebrow {
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; letter-spacing: 0.4em;
    color: var(--ink-soft); text-transform: uppercase;
    margin: 0 0 10px;
  }

  /* Footer */
  .ed-footer {
    border-top: 6px solid var(--rule);
    margin-top: 30px; padding-top: 14px;
    display: flex; justify-content: space-between; align-items: baseline;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: var(--ink-mute);
    letter-spacing: 0.12em; text-transform: uppercase;
  }
`;

function Editorial({ data }) {
  return (
    <div className="ed-root">
      <style>{editorialStyles}</style>

      {/* Masthead */}
      <div className="ed-masthead">
        <div className="ed-masthead-top">
          <span>VOL. III · NO. {data.issueNo}</span>
          <span>{data.dateKo}</span>
          <span>AI-CURATED · KST 08:00</span>
        </div>
        <h1 className="ed-title">The Daily <em>Brief</em></h1>
        <div className="ed-tagline">RSS · AI 분석 · 매일 아침 한 부</div>
      </div>

      {/* Briefing row */}
      <div className="ed-briefing">
        <div className="ed-briefing-left">
          <span className="lbl">오늘의 통계</span>
          <div className="ed-briefing-stat">
            <span className="num">{data.stats.total}</span>
            <span className="lab">건 수집</span>
          </div>
          <div className="ed-briefing-stat">
            <span className="num">{data.stats.analyzed}</span>
            <span className="lab">AI 분석</span>
          </div>
          <div className="ed-briefing-stat">
            <span className="num">{data.stats.sources}</span>
            <span className="lab">언론사</span>
          </div>
        </div>
        <div>
          <div className="ed-kicker">에디터 노트 · TODAY'S LEDE</div>
          <p className="ed-lede">
            대통령 인도 순방·호르무즈 재봉쇄가 맞물리며 에너지 공급망이 다시 도마에 올랐다.
            북한의 단거리 미사일 발사와 코스피 신기록 기대가 한날의 헤드라인을 양분한다.
          </p>
        </div>
        <div className="ed-byline">
          AI Editor<br/>
          Gemini 2.0 Flash<br/>
          ─<br/>
          {data.generatedAt}
        </div>
      </div>

      {/* Top stories */}
      <div className="ed-headlines">
        {data.highlights.map((h, i) => (
          <div className="ed-hl" key={i}>
            <div className="ed-hl-tag">{h.category}</div>
            <h2>{h.headline}</h2>
            <p>{h.blurb}</p>
            <div className="ed-hl-src">— {h.source}</div>
          </div>
        ))}
      </div>

      {/* Section summaries */}
      <div className="ed-eyebrow">─ AI 종합 분석 ─</div>

      {data.sections.map((sec, i) => (
        <div className="ed-section" key={sec.id}>
          <div className="ed-section-head">
            <h3>{sec.title}</h3>
            <span className="ed-section-meta">
              SECTION {String(i + 1).padStart(2, '0')} · {data.articles.filter(a => secMatch(a.cat, sec.id)).length}건
            </span>
          </div>
          <div className="ed-summary">
            {sec.bullets.map((b, j) => <p key={j}>{b}</p>)}
          </div>
        </div>
      ))}

      {/* Article ledger */}
      <div className="ed-section">
        <div className="ed-section-head">
          <h3>전체 기사 색인</h3>
          <span className="ed-section-meta">LEDGER · {data.articles.length}건</span>
        </div>
        <div className="ed-list">
          {data.articles.map((a, i) => (
            <div className="ed-list-item" key={i}>
              <div className="ed-li-time">{a.time}</div>
              <div>
                <div className="ed-li-title">
                  <span className="ed-li-cat">{a.catKo}</span>
                  {a.title}
                </div>
                <div className="ed-li-src">{a.source}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="ed-footer">
        <span>The Daily Brief · Issue #{data.issueNo}</span>
        <span>Powered by Gemini · GitHub Actions · Resend</span>
        <span>chamgil71/dailynews</span>
      </div>
    </div>
  );
}

function secMatch(cat, secId) {
  if (secId === 'politics') return cat === 'politics' || cat === 'security' || cat === 'world';
  if (secId === 'economy') return cat === 'economy' || cat === 'society';
  if (secId === 'tech') return cat === 'tech';
  if (secId === 'markets') return cat === 'markets';
  return false;
}

window.Editorial = Editorial;
