// Top-level app: handles view switching + theme tweaks.

const { useState, useEffect } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "navy"
}/*EDITMODE-END*/;

const THEME_OPTIONS = [
  { value: "navy",   label: "Navy",   sub: "Modern tech-news (default)" },
  { value: "ink",    label: "Ink",    sub: "Charcoal + newspaper red" },
  { value: "forest", label: "Forest", sub: "Deep green + mint" },
];

function App() {
  const [view, setView] = useState("latest");
  const [latestDate, setLatestDate] = useState(REPORTS[0].date);
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // Apply theme to <html> so EVERY component, including chrome, switches.
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("theme-ink", "theme-forest");
    if (tweaks.theme === "ink")    root.classList.add("theme-ink");
    if (tweaks.theme === "forest") root.classList.add("theme-forest");
  }, [tweaks.theme]);

  const navigate = (k, date) => {
    setView(k);
    if (date) setLatestDate(date);
  };

  const currentReport = REPORTS.find((r) => r.date === latestDate) || REPORTS[0];

  return (
    <React.Fragment>
      <Header activeView={view} onNav={(k) => navigate(k)} />

      {view === "latest" && <ReportView report={currentReport} />}
      {view === "app"    && <AppView />}
      {view === "archive" && (
        <ArchiveView onPickDate={(d) => navigate("latest", d)} />
      )}

      <Footer generatedAt={currentReport.generated_at} />

      <TweaksPanel title="Tweaks">
        <TweakSection label="Theme">
          <div className="theme-swatches">
            {THEME_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                className={"theme-swatch " + (tweaks.theme === opt.value ? "active" : "")}
                onClick={() => setTweak("theme", opt.value)}
                data-theme={opt.value}
              >
                <div className="theme-swatch-strip">
                  <span className="ts-chrome"></span>
                  <span className="ts-accent"></span>
                  <span className="ts-bg"></span>
                </div>
                <div className="theme-swatch-label">
                  <div className="ts-name">{opt.label}</div>
                  <div className="ts-sub">{opt.sub}</div>
                </div>
              </button>
            ))}
          </div>
        </TweakSection>
      </TweaksPanel>
    </React.Fragment>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
