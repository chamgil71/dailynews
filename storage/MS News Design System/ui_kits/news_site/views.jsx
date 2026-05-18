// Views — three modes matching publish/index.html, publish/app.html, publish/archive.html.

const { useState, useMemo } = React;

/* ── ReportBody: shared analysis renderer ──────────────────────────────── */
function ReportBody({ report, lang = "all", query = "" }) {
  const showEn = lang === "all" || lang === "en";
  const showKo = lang === "all" || lang === "ko";

  const renderAnalysis = (a) => a && (
    <React.Fragment>
      <h2>{a.title}</h2>
      <p>{a.lead}</p>
      <h2>핵심 이슈 TOP 3</h2>
      <ol>
        {a.issues.map((it, i) => (
          <li key={i}>
            <strong>{it.title}</strong> — {it.body}
          </li>
        ))}
      </ol>
      <h2>주목할 트렌드</h2>
      <ul>
        {a.trends.map((t, i) => (
          <li key={i}><strong>{t.k}</strong> {t.v}</li>
        ))}
      </ul>
    </React.Fragment>
  );

  const newsEn = useMemo(
    () => query
      ? report.news_en.filter((n) => n.title.toLowerCase().includes(query.toLowerCase()))
      : report.news_en,
    [report, query]
  );
  const newsKo = useMemo(
    () => query
      ? report.news_ko.filter((n) => n.title.toLowerCase().includes(query.toLowerCase()))
      : report.news_ko,
    [report, query]
  );

  return (
    <React.Fragment>
      {showEn && renderAnalysis(report.analysis_en)}
      {showEn && showKo && <hr />}
      {showKo && renderAnalysis(report.analysis_ko)}

      {report.matched && report.matched.length > 0 && (
        <React.Fragment>
          <hr />
          <h2>🔍 키워드 매칭 기사 ({report.matched.length}건)</h2>
          <ul>
            {report.matched.map((m, i) => (
              <li key={i} style={{ marginBottom: 14 }}>
                <strong>[{m.label}]</strong>{" "}
                <a href={m.link} onClick={(e) => e.preventDefault()}>{m.title}</a>
                {m.quote && <Quote>{m.quote}</Quote>}
              </li>
            ))}
          </ul>
        </React.Fragment>
      )}

      <hr />
      <h2>📋 수집 기사 전체 목록</h2>
      {showEn && <NewsList items={newsEn} lang="en" date={report.date} query={query} />}
      {showKo && <NewsList items={newsKo} lang="ko" date={report.date} query={query} />}

      {query && !newsEn.length && !newsKo.length && (
        <EmptyState icon="🔍" message={`"${query}" 검색 결과 없음`} />
      )}
    </React.Fragment>
  );
}

/* ── ReportView: matches publish/index.html ───────────────────────────── */
function ReportView({ report }) {
  return (
    <div className="container">
      <Card>
        <h1>📰 Daily News Brief</h1>
        <div className="meta">
          <Badge>📅 {report.displayDate}</Badge>
          <Badge>🤖 AI 자동 분석</Badge>
          <Badge>🌐 EN + KO</Badge>
        </div>
        <Quote>
          📅 생성일시: {report.generated_at}<br />
          📊 수집: 총 {report.stats.total}건 (EN: {report.stats.en} / KO: {report.stats.ko}) | AI 분석: {report.stats.sent_to_ai}건 | 키워드 매칭: {report.stats.matched}건
        </Quote>
        <ReportBody report={report} lang="all" query="" />
      </Card>

      <Card style={{ marginTop: 24, textAlign: "center" }}>
        <h3 style={{ marginTop: 0 }}>📬 뉴스레터 구독</h3>
        <p style={{ color: "var(--color-muted)", margin: ".5em 0 1.2em" }}>
          매일 오전 AI가 정리한 글로벌 뉴스 브리핑을 이메일로 받아보세요.
        </p>
        <a
          href="#"
          onClick={(e) => e.preventDefault()}
          className="btn-primary"
        >
          구독 신청하기
        </a>
        <p style={{ fontSize: ".8rem", color: "var(--color-muted)", margin: ".8em 0 0" }}>
          구독 취소는 수신된 메일 하단 링크를 클릭하세요.
        </p>
      </Card>
    </div>
  );
}

/* ── AppView: matches publish/app.html ────────────────────────────────── */
function AppView() {
  const [activeDate, setActiveDate] = useState(REPORTS[0].date);
  const [lang, setLang] = useState("all");
  const [query, setQuery] = useState("");

  const report = useMemo(
    () => REPORTS.find((r) => r.date === activeDate) || REPORTS[0],
    [activeDate]
  );

  const stats = useMemo(() => {
    const total = REPORTS.length;
    const news = REPORTS.reduce((s, r) => s + r.stats.total, 0);
    const en   = REPORTS.reduce((s, r) => s + r.stats.en, 0);
    const ko   = REPORTS.reduce((s, r) => s + r.stats.ko, 0);
    return { total, news, en, ko };
  }, []);

  return (
    <div className="ms-layout">
      <Sidebar
        query={query}
        onQuery={setQuery}
        stats={stats}
        dates={REPORTS.map((r) => ({ date: r.date }))}
        activeDate={activeDate}
        onPickDate={setActiveDate}
      />
      <main className="main-area">
        <div className="controls">
          <h2>{report.date.replace(/-/g, ".")} 브리핑</h2>
          <Tabs value={lang} onChange={setLang} />
        </div>
        <Card style={{ animation: "fadeIn .3s ease" }}>
          <div className="report-header">
            <div className="report-date">📰 {report.displayDate} 브리핑</div>
            <div className="badges">
              <Badge tone="blue">EN {report.stats.en}건</Badge>
              <Badge tone="green">KO {report.stats.ko}건</Badge>
              <Badge tone="orange">AI 분석 {report.stats.sent_to_ai}건</Badge>
            </div>
          </div>
          <div className="analysis">
            <ReportBody report={report} lang={lang} query={query} />
          </div>
        </Card>
      </main>
    </div>
  );
}

/* ── ArchiveView: matches publish/archive.html ────────────────────────── */
function ArchiveView({ onPickDate }) {
  return (
    <div className="container">
      <Card>
        <h1>📚 전체 리포트 목록</h1>
        <p style={{ color: "var(--color-muted)", margin: ".5em 0 1.5em" }}>
          총 {ARCHIVE_ENTRIES.length}개 리포트
        </p>
        <ul className="archive-list">
          {ARCHIVE_ENTRIES.map((d) => {
            const wd = new Date(d.date).toLocaleDateString("en-US", { weekday: "short" });
            const isOpenable = REPORTS.some((r) => r.date === d.date);
            return (
              <li key={d.date}>
                <a
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    if (isOpenable) onPickDate(d.date);
                  }}
                  style={{ opacity: isOpenable ? 1 : 0.5 }}
                >
                  📄 {d.displayDate} ({wd}) 리포트
                </a>
                <div className="archive-date">{d.date}</div>
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
}

Object.assign(window, { ReportView, AppView, ArchiveView });
