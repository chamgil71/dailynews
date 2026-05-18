// Small primitives + chrome for the MS News kit.

const { useState } = React;

/* ── Header ─────────────────────────────────────────────────────────────── */
function Header({ activeView, onNav }) {
  const item = (k, label) => (
    <a
      href="#"
      onClick={(e) => { e.preventDefault(); onNav(k); }}
      className={activeView === k ? "active" : ""}
    >
      {label}
    </a>
  );
  return (
    <header className="ms-header">
      <div className="logo">📰 AI <span>News</span> Daily</div>
      <nav>
        {item("latest", "최신 리포트")}
        {item("app", "검색")}
        {item("archive", "전체 목록")}
      </nav>
    </header>
  );
}

/* ── Footer ─────────────────────────────────────────────────────────────── */
function Footer({ generatedAt }) {
  return (
    <footer className="ms-footer">
      Powered by GitHub Actions · OpenAI GPT · RSS Feeds<br />
      매일 자동 업데이트{generatedAt ? ` · 생성: ${generatedAt}` : ""}
    </footer>
  );
}

/* ── Badge ──────────────────────────────────────────────────────────────── */
function Badge({ tone = "blue", children }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

/* ── Card ───────────────────────────────────────────────────────────────── */
function Card({ children, style }) {
  return <div className="card" style={style}>{children}</div>;
}

/* ── Blockquote ─────────────────────────────────────────────────────────── */
function Quote({ children }) {
  return <blockquote className="ms-quote">{children}</blockquote>;
}

/* ── News item + list ───────────────────────────────────────────────────── */
function NewsItem({ item, query }) {
  const re = query
    ? new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi")
    : null;
  const parts = re
    ? item.title.split(re).map((p, i) =>
        re.test(p) ? <mark key={i}>{p}</mark> : <React.Fragment key={i}>{p}</React.Fragment>
      )
    : item.title;
  return (
    <div className="news-item">
      <span className="cat">{item.label}</span>
      <a href={item.link || "#"} onClick={(e) => e.preventDefault()}>{parts}</a>
    </div>
  );
}

function NewsList({ items, lang, date, query }) {
  const [open, setOpen] = useState(false);
  if (!items || !items.length) return null;
  const flag = lang === "en" ? "🌐" : "🇰🇷";
  const label = lang === "en" ? "영어 뉴스" : "한국어 뉴스";
  return (
    <div className="news-block">
      <button className="news-toggle" onClick={() => setOpen((o) => !o)}>
        <span>{flag} {label} {items.length}건 보기</span>
        <span>{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="news-list">
          {items.map((n, i) => <NewsItem key={i} item={n} query={query} />)}
        </div>
      )}
    </div>
  );
}

/* ── Sidebar (search + stats + date list) ──────────────────────────────── */
function Sidebar({ query, onQuery, stats, dates, activeDate, onPickDate }) {
  return (
    <aside className="ms-sidebar">
      <div className="sidebar-card">
        <h3>🔍 검색</h3>
        <div className="search-wrap">
          <input
            type="text"
            placeholder="키워드 검색..."
            value={query}
            onChange={(e) => onQuery(e.target.value)}
          />
          <span className="icon">🔍</span>
        </div>
      </div>

      <div className="sidebar-card">
        <h3>📊 통계</h3>
        <div className="stat-grid">
          <div className="stat-item"><div className="num">{stats.total}</div><div className="lbl">총 리포트</div></div>
          <div className="stat-item"><div className="num">{stats.news}</div><div className="lbl">총 기사 수</div></div>
          <div className="stat-item"><div className="num">{stats.en}</div><div className="lbl">영어</div></div>
          <div className="stat-item"><div className="num">{stats.ko}</div><div className="lbl">한국어</div></div>
        </div>
      </div>

      <div className="sidebar-card">
        <h3>📅 리포트 날짜</h3>
        <ul className="date-list">
          {dates.map((d) => (
            <li key={d.date}>
              <a
                href="#"
                onClick={(e) => { e.preventDefault(); onPickDate(d.date); }}
                className={d.date === activeDate ? "active" : ""}
              >
                📄 {d.date.replace(/-/g, ".")}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}

/* ── Tabs (language filter) ─────────────────────────────────────────────── */
function Tabs({ value, onChange }) {
  const t = (k, label) => (
    <button
      className={"tab " + (value === k ? "active" : "")}
      onClick={() => onChange(k)}
    >
      {label}
    </button>
  );
  return (
    <div className="filter-tabs">
      {t("all", "전체")}
      {t("en", "🌐 영어")}
      {t("ko", "🇰🇷 한국어")}
    </div>
  );
}

/* ── Empty / loading states ────────────────────────────────────────────── */
function EmptyState({ icon, message }) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <div className="empty-msg">{message}</div>
    </div>
  );
}

Object.assign(window, {
  Header, Footer, Badge, Card, Quote,
  NewsItem, NewsList, Sidebar, Tabs, EmptyState,
});
