/* global React */

// ============================================================
// VARIATION 2 — MINIMAL EDITORIAL (Substack / Bear Blog feel)
// Generous whitespace, single column, Pretendard type,
// subtle category chips, focus on the AI summary as the hero.
// ============================================================

const minimalStyles = `
  .mn-root {
    --bg: #fafaf7;
    --surface: #ffffff;
    --ink: #16181a;
    --ink-soft: #3d4248;
    --ink-mute: #8a8f95;
    --rule: #e6e2da;
    --accent: #ff5a1f;
    --chip: #f1efe8;
    font-family: 'Pretendard', 'Pretendard Variable', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    background: var(--bg);
    color: var(--ink);
    width: 100%;
    min-height: 100%;
    padding: 56px 80px 80px;
    box-sizing: border-box;
    line-height: 1.6;
    font-feature-settings: 'ss01', 'ss02';
  }
  .mn-root, .mn-root * { box-sizing: border-box; }
  .mn-wrap { max-width: 720px; margin: 0 auto; }

  /* Top bar */
  .mn-topbar {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 24px;
    margin-bottom: 56px;
    border-bottom: 1px solid var(--rule);
  }
  .mn-brand {
    display: flex; align-items: center; gap: 10px;
    font-weight: 700; letter-spacing: -0.02em;
    font-size: 15px;
  }
  .mn-brand-dot {
    width: 22px; height: 22px; border-radius: 7px;
    background: var(--ink);
    display: grid; place-items: center;
    color: var(--bg);
    font-size: 11px; font-weight: 800;
  }
  .mn-nav { display: flex; gap: 22px; }
  .mn-nav a {
    color: var(--ink-soft); text-decoration: none;
    font-size: 13px; font-weight: 500;
  }
  .mn-nav a.on { color: var(--ink); font-weight: 700; }

  /* Hero */
  .mn-hero { margin-bottom: 56px; }
  .mn-eyebrow {
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 18px;
    display: flex; align-items: center; gap: 10px;
  }
  .mn-eyebrow::before {
    content: ''; width: 24px; height: 1px; background: var(--accent);
  }
  .mn-hero h1 {
    font-size: 52px;
    line-height: 1.08;
    letter-spacing: -0.03em;
    font-weight: 800;
    margin: 0 0 22px;
    text-wrap: balance;
  }
  .mn-hero-meta {
    display: flex; gap: 16px; align-items: center;
    color: var(--ink-mute); font-size: 13px;
    padding-top: 18px;
    border-top: 1px solid var(--rule);
  }
  .mn-hero-meta strong { color: var(--ink); font-weight: 600; }
  .mn-hero-meta .dot { width: 3px; height: 3px; background: var(--ink-mute); border-radius: 50%; }

  /* Stats strip */
  .mn-stats {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0;
    margin-bottom: 56px;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 22px 0;
  }
  .mn-stat { padding: 0 4px; border-left: 1px solid var(--rule); padding-left: 18px; }
  .mn-stat:first-child { border-left: none; padding-left: 0; }
  .mn-stat .n {
    font-size: 32px; font-weight: 800; letter-spacing: -0.04em;
    line-height: 1; margin-bottom: 6px;
    font-feature-settings: 'tnum';
  }
  .mn-stat .l { font-size: 12px; color: var(--ink-mute); letter-spacing: 0.04em; }

  /* TL;DR card */
  .mn-tldr {
    background: var(--ink);
    color: var(--bg);
    border-radius: 18px;
    padding: 32px 34px;
    margin-bottom: 56px;
  }
  .mn-tldr-head {
    display: flex; align-items: center; gap: 8px;
    font-size: 12px; letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 18px;
  }
  .mn-tldr-head::before {
    content: '';
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 0 4px rgba(255,90,31,0.18);
  }
  .mn-tldr-list { display: flex; flex-direction: column; gap: 18px; }
  .mn-tldr-item {
    display: grid;
    grid-template-columns: 28px 1fr;
    gap: 14px;
    align-items: start;
  }
  .mn-tldr-num {
    font-size: 12px; font-weight: 800;
    color: rgba(255,255,255,0.45);
    font-feature-settings: 'tnum';
    padding-top: 4px;
    letter-spacing: 0.04em;
  }
  .mn-tldr-item h3 {
    font-size: 17px; line-height: 1.4;
    font-weight: 700; letter-spacing: -0.015em;
    margin: 0 0 6px;
  }
  .mn-tldr-item p {
    font-size: 14px; line-height: 1.6;
    color: rgba(255,255,255,0.7);
    margin: 0;
  }

  /* Section */
  .mn-section { margin-bottom: 52px; }
  .mn-sec-head {
    display: flex; align-items: baseline; justify-content: space-between;
    margin-bottom: 22px;
  }
  .mn-sec-head h2 {
    font-size: 26px; letter-spacing: -0.02em;
    font-weight: 800; margin: 0;
  }
  .mn-sec-head .mn-sec-count {
    font-size: 13px; color: var(--ink-mute);
    font-feature-settings: 'tnum';
  }
  .mn-sec-bullets {
    display: flex; flex-direction: column; gap: 14px;
  }
  .mn-sec-bullets p {
    font-size: 16px; line-height: 1.7;
    color: var(--ink-soft);
    margin: 0;
    padding-left: 18px;
    position: relative;
  }
  .mn-sec-bullets p::before {
    content: ''; position: absolute;
    left: 0; top: 11px;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
  }

  /* Article list */
  .mn-articles { display: flex; flex-direction: column; }
  .mn-article {
    display: grid;
    grid-template-columns: 56px 1fr auto;
    gap: 16px; align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid var(--rule);
  }
  .mn-article:last-child { border-bottom: none; }
  .mn-time {
    font-size: 12px; color: var(--ink-mute);
    font-feature-settings: 'tnum';
    letter-spacing: 0.02em;
  }
  .mn-art-title {
    font-size: 15px; line-height: 1.45;
    color: var(--ink);
    font-weight: 500;
  }
  .mn-art-meta {
    display: flex; gap: 8px; align-items: center;
    margin-top: 4px;
  }
  .mn-chip {
    display: inline-block;
    background: var(--chip);
    color: var(--ink-soft);
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.02em;
    font-weight: 500;
  }
  .mn-src {
    font-size: 12px;
    color: var(--ink-mute);
  }
  .mn-arrow {
    color: var(--ink-mute);
    font-size: 16px;
    transition: color .15s, transform .15s;
  }
  .mn-article:hover .mn-arrow { color: var(--accent); transform: translateX(3px); }

  /* Subscribe block */
  .mn-sub {
    background: var(--surface);
    border: 1px solid var(--rule);
    border-radius: 14px;
    padding: 34px;
    text-align: center;
    margin: 64px 0 32px;
  }
  .mn-sub h3 {
    font-size: 22px; letter-spacing: -0.02em;
    font-weight: 800; margin: 0 0 6px;
  }
  .mn-sub p {
    font-size: 14px; color: var(--ink-mute);
    margin: 0 0 18px;
  }
  .mn-sub-form {
    display: flex; gap: 8px;
    max-width: 420px; margin: 0 auto;
  }
  .mn-sub-form input {
    flex: 1; padding: 11px 14px;
    border: 1px solid var(--rule);
    border-radius: 8px;
    font-size: 14px;
    background: var(--bg);
    font-family: inherit;
    color: var(--ink);
    outline: none;
  }
  .mn-sub-form button {
    background: var(--ink);
    color: var(--bg);
    border: none;
    padding: 11px 18px;
    border-radius: 8px;
    font-size: 14px; font-weight: 600;
    cursor: pointer; font-family: inherit;
  }

  /* Footer */
  .mn-footer {
    border-top: 1px solid var(--rule);
    padding-top: 22px;
    color: var(--ink-mute);
    font-size: 12px;
    display: flex; justify-content: space-between;
  }
`;

function Minimal({ data }) {
  const visibleArticles = data.articles.slice(0, 16);
  return (
    <div className="mn-root">
      <style>{minimalStyles}</style>
      <div className="mn-wrap">

        {/* Top bar */}
        <div className="mn-topbar">
          <div className="mn-brand">
            <div className="mn-brand-dot">N</div>
            <span>Daily News</span>
          </div>
          <div className="mn-nav">
            <a href="#" className="on">오늘</a>
            <a href="#">아카이브</a>
            <a href="#">소스</a>
            <a href="#">구독</a>
          </div>
        </div>

        {/* Hero */}
        <div className="mn-hero">
          <div className="mn-eyebrow">{data.dateKo} · ISSUE #{data.issueNo}</div>
          <h1>대통령 인도 순방, 호르무즈 재봉쇄, 코스피 신기록 기대 — 오늘의 한국.</h1>
          <div className="mn-hero-meta">
            <span><strong>AI 분석</strong></span>
            <span className="dot" />
            <span>{data.stats.analyzed}건 요약</span>
            <span className="dot" />
            <span>{data.stats.sources}개 언론사</span>
            <span className="dot" />
            <span>읽는 시간 약 6분</span>
          </div>
        </div>

        {/* Stats */}
        <div className="mn-stats">
          <div className="mn-stat"><div className="n">{data.stats.total}</div><div className="l">수집 기사</div></div>
          <div className="mn-stat"><div className="n">{data.stats.analyzed}</div><div className="l">AI 분석</div></div>
          <div className="mn-stat"><div className="n">{data.stats.dedupSkipped}</div><div className="l">중복 제외</div></div>
          <div className="mn-stat"><div className="n">{data.stats.sources}</div><div className="l">소스</div></div>
        </div>

        {/* TL;DR — top 3 highlights */}
        <div className="mn-tldr">
          <div className="mn-tldr-head">TL;DR · 오늘의 큰 그림</div>
          <div className="mn-tldr-list">
            {data.highlights.map((h, i) => (
              <div className="mn-tldr-item" key={i}>
                <div className="mn-tldr-num">0{i + 1}</div>
                <div>
                  <h3>{h.headline}</h3>
                  <p>{h.blurb}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section summaries */}
        {data.sections.map((sec) => {
          const count = data.articles.filter(a => minSecMatch(a.cat, sec.id)).length;
          return (
            <div className="mn-section" key={sec.id}>
              <div className="mn-sec-head">
                <h2>{sec.title}</h2>
                <span className="mn-sec-count">{count}건 분석</span>
              </div>
              <div className="mn-sec-bullets">
                {sec.bullets.map((b, j) => <p key={j}>{b}</p>)}
              </div>
            </div>
          );
        })}

        {/* Article list */}
        <div className="mn-section">
          <div className="mn-sec-head">
            <h2>전체 기사</h2>
            <span className="mn-sec-count">{data.articles.length}건 · 최신순</span>
          </div>
          <div className="mn-articles">
            {visibleArticles.map((a, i) => (
              <a className="mn-article" key={i} href={a.url}>
                <div className="mn-time">{a.time}</div>
                <div>
                  <div className="mn-art-title">{a.title}</div>
                  <div className="mn-art-meta">
                    <span className="mn-chip">{a.catKo}</span>
                    <span className="mn-src">{a.source}</span>
                  </div>
                </div>
                <div className="mn-arrow">→</div>
              </a>
            ))}
          </div>
        </div>

        {/* Subscribe */}
        <div className="mn-sub">
          <h3>매일 아침 8시, 받은편지함으로.</h3>
          <p>AI가 정리한 한국 뉴스 브리핑. 광고 없음. 언제든 해지.</p>
          <div className="mn-sub-form">
            <input placeholder="you@example.com" />
            <button>구독</button>
          </div>
        </div>

        <div className="mn-footer">
          <span>© 2026 Daily News</span>
          <span>chamgil71/dailynews · Powered by Gemini</span>
        </div>
      </div>
    </div>
  );
}

function minSecMatch(cat, secId) {
  if (secId === 'politics') return cat === 'politics' || cat === 'security' || cat === 'world';
  if (secId === 'economy') return cat === 'economy' || cat === 'society';
  if (secId === 'tech') return cat === 'tech';
  if (secId === 'markets') return cat === 'markets';
  return false;
}

window.Minimal = Minimal;
