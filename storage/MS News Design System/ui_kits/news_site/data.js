// Sample data lifted from the real AI News Daily reports.
// 3 dates so date-list + archive interactions are meaningful.

window.REPORTS = [
  {
    date: "2026-05-14",
    displayDate: "2026년 05월 14일",
    stats: { total: 166, en: 94, ko: 70, sent_to_ai: 40, matched: 2 },
    generated_at: "2026-05-14 05:44 KST",
    analysis_en: {
      title: "🌐 Global News Analysis",
      lead: "뉴스 분석 전문가로서 제공해주신 기술 및 AI 산업 동향을 분석한 결과입니다.",
      issues: [
        {
          title: "AI 에이전트의 실무 도입 가속화 및 생태계 확장",
          body:
            "Anthropic의 'Cowork', Notion의 AI 에이전트 플랫폼, Salesforce의 Slackbot 개편 등 단순 챗봇을 넘어 업무를 직접 수행하는 '에이전트' 중심의 서비스가 주류로 자리 잡고 있습니다. 이는 AI가 단순 정보 제공을 넘어 파일 관리, 코드 작성, 워크플로우 자동화 등 실질적인 생산성 도구로 진화하고 있음을 보여줍니다.",
        },
        {
          title: "OpenAI vs. 일론 머스크 법적 공방과 AI 거버넌스 논란",
          body:
            "일론 머스크와 OpenAI 간의 소송이 장기화되면서 AI의 안전성, 기업의 책임, 기술 독점 및 윤리적 책임에 대한 사회적 논의가 격화되고 있습니다. 특히 AI 모델의 개발 방식과 기업 간의 기술 탈취 의혹 등이 법정에서 다뤄지며, 향후 AI 산업의 규제 방향성에 큰 변곡점이 될 것으로 보입니다.",
        },
        {
          title: "AI 인프라 수요 급증과 에너지·클라우드 시장의 재편",
          body:
            "AI 모델 학습 및 운영을 위한 데이터센터 수요가 폭발하면서 지열 에너지(Fervo Energy)와 같은 친환경 에너지 투자와 고성능 클라우드 인프라(Railway 등)에 대한 대규모 자금 유입이 이어지고 있습니다. 이는 AI 기술이 물리적 인프라와 에너지 산업 전반의 구조적 변화를 강제하고 있음을 시사합니다.",
        },
      ],
      trends: [
        { k: "에이전트화(Agentic AI):", v: "단순 질의응답을 넘어 사용자의 의도를 파악하고 외부 툴과 연동하여 능동적으로 업무를 처리하는 '프로액티브' AI로의 전환이 뚜렷합니다." },
        { k: "AI 인프라의 물리적 한계와 대응:", v: "데이터센터의 전력 문제(xAI 사례), 모델 학습 비용의 지속 가능성, 그리고 AI 모델의 보안 취약점이 주요 해결 과제로 부상했습니다." },
        { k: "산업별 특화 AI 적용:", v: "법률(Clio), 의료(NHS), 금융 등 특정 도메인에 최적화된 AI 솔루션이 도입되며, 이를 뒷받침하기 위한 데이터 거버넌스가 핵심 경쟁력이 되고 있습니다." },
      ],
    },
    analysis_ko: {
      title: "🇰🇷 국내 뉴스 분석",
      lead: "뉴스 분석 전문가로서 제공해주신 뉴스 목록을 바탕으로 국내 IT·기술 산업 및 경제 동향을 분석한 결과입니다.",
      issues: [
        {
          title: "삼성전자 노조 갈등과 경제 리스크 부각",
          body:
            "삼성전자 노조가 성과급 상한 폐지 등 제도 개선을 요구하며 사측과의 대화에 강경한 입장을 고수하고 있습니다. 경제 수장들은 삼성전자의 파업이 수출, 성장률, 금융 시장 전반에 상당한 리스크를 초래할 수 있다고 경고하며 원칙 있는 협상을 촉구하고 있습니다.",
        },
        {
          title: "AI 인프라 및 기술 생태계의 급격한 확장",
          body:
            "반도체 장비업체 어플라이드 머티어리얼즈와 마이크론 등 글로벌 기업들이 AI 인프라 수요를 확인하며 시장 전망을 상향하고 있습니다. 국내에서도 메가존클라우드, 워크데이 등이 AI 거버넌스 및 오케스트레이터 전략을 내세우며 기업용 AI 도입의 효율성과 안전성을 강조하는 추세입니다.",
        },
        {
          title: "정부 주도의 원전 수출 체계 개편 및 산업 지원",
          body:
            "한국전력과 한수원으로 이원화되어 있던 원전 수출 체계가 정부 주도의 통합 관리 체제로 개편되었습니다. 이는 글로벌 원전 시장의 G2G(정부 간 거래) 성격에 대응하고 공기업 간 불필요한 경쟁을 방지하여 국가적 차원의 수주 경쟁력을 높이려는 전략입니다.",
        },
      ],
      trends: [
        { k: "AI의 실무·공공 영역 침투:", v: "AI 기술이 단순 연구 단계를 넘어 재정 통합 시스템, 침수 계측, 어린이보호구역 관리 등 지자체 행정까지 광범위하게 적용되고 있습니다." },
        { k: "AI 풀스택(Full-stack) 구축 경쟁:", v: "하드웨어(반도체, 부품)부터 소프트웨어(AI 모델, 거버넌스)까지 아우르는 AI 풀스택 역량이 국가 및 기업의 핵심 경쟁력으로 부상하고 있습니다." },
        { k: "리스크 관리와 안전 문화 확산:", v: "바이오 산업의 안전 문화, AI 거버넌스 플랫폼, 불법 조업 담보금 상향 등 산업 현장의 안전과 보안을 강화하려는 움직임이 뚜렷합니다." },
      ],
    },
    matched: [
      { label: "국내 IT·기술", title: "AI가 국가 R&D 예산심의 돕는다…'예산심의 특화 AI' 본격 도입", link: "#", quote: "정부가 국가 연구개발(R&D) 예산 심사에 인공지능(AI)을 본격 도입한다. 방대한 사업계획서 검토와 유사·중복 사업 분석, 회의록 작성 등을 AI가 지원하면서 국가 R&D 예산심의 체계를 데이터 기반으로 전환한다는 구상이다." },
      { label: "국내 IT·기술", title: "세명소프트, 국산 NPU 기반 'AI 모델 허브 플랫폼' 구축한다", link: "#", quote: "세명소프트(대표 황바울)는 과학기술정보통신부 및 정보통신기획평가원이 추진하는 'AI 반도체 특화 클라우드 네이티브 SW 스택 및 모델 허브 기술 개발' 과제에 선정됐다고 14일 밝혔다." },
    ],
    news_en: [
      { label: "글로벌 기술", title: "Solar drone with jumbo jet wingspan broke a flight record—then it crashed", link: "#" },
      { label: "글로벌 기술", title: "Microsoft's Edge Copilot update uses AI to pull information from across your tabs", link: "#" },
      { label: "글로벌 기술", title: "YouTube is courting creators — and sponsors — with streaming shows", link: "#" },
      { label: "글로벌 기술", title: "AMD's best CPU tech for gamers is coming to workstations too", link: "#" },
      { label: "AI·ML", title: "Anthropic launches Cowork, a Claude Desktop agent that works in your files — no coding required", link: "#" },
      { label: "AI·ML", title: "Notion just turned its workspace into a hub for AI agents", link: "#" },
      { label: "AI·ML", title: "Clio's $500M milestone arrives just as Anthropic ups the ante", link: "#" },
      { label: "AI·ML", title: "Musk's xAI is running nearly 50 gas turbines unchecked at its Mississippi data center", link: "#" },
      { label: "AI·ML", title: "Geothermal startup Fervo Energy pops 33% in IPO debut fueled by AI data center demand", link: "#" },
      { label: "AI·ML", title: "Salesforce rolls out new Slackbot AI agent as it battles Microsoft and Google", link: "#" },
      { label: "AI·ML", title: "Railway secures $100 million to challenge AWS with AI-native cloud infrastructure", link: "#" },
      { label: "AI·ML", title: "World Models: 10 Things That Matter in AI Right Now", link: "#" },
    ],
    news_ko: [
      { label: "국내 경제", title: "경주 방폐장 2단계 가동···표층처분시설, 1년 만에 운영 시작", link: "#" },
      { label: "국내 경제", title: "외국 어선 불법 조업하다 걸리면 패가망신…담보금 5억→15억 '껑충'", link: "#" },
      { label: "국내 경제", title: "삼성전자 노조, 중노위 '대화 재개' 제안에도 \"제도화 먼저\"", link: "#" },
      { label: "국내 경제", title: "어플라이드 머티어리얼즈, 실적 발표…\"AI 인프라 수요 확인\"", link: "#" },
      { label: "국내 경제", title: "BofA, 마이크론 반도체 장기 호황 덕 목표가 950달러로 상향", link: "#" },
      { label: "국내 IT·기술", title: "나눠졌던 원전 수출, 정부가 주도한다…한전·한수원 국가 분담제 폐지", link: "#" },
      { label: "국내 IT·기술", title: "워크데이 \"AI 거버넌스 플랫폼 전환…통제 가능한 AI 구현\"", link: "#" },
      { label: "국내 IT·기술", title: "메가존클라우드, AI 오케스트레이터 전략 본격화…\"AI 도입 혼란 해결\"", link: "#" },
      { label: "국내 IT·기술", title: "MS, 오픈AI 누적 투자 비용 첫 공개…\"인프라 포함 150조 넘어\"", link: "#" },
      { label: "국내 IT·기술", title: "\"급여 관리부터 마케팅까지\"...앤트로픽, 소상공인 전용 AI 패키지 출시", link: "#" },
    ],
  },
  {
    date: "2026-05-13",
    displayDate: "2026년 05월 13일",
    stats: { total: 152, en: 88, ko: 64, sent_to_ai: 35, matched: 3 },
    generated_at: "2026-05-13 05:42 KST",
    analysis_en: {
      title: "🌐 Global News Analysis",
      lead: "오늘의 글로벌 기술·AI 동향 핵심 분석입니다.",
      issues: [
        { title: "Anthropic Claude 4 출시 임박", body: "차세대 멀티모달 모델의 베타 테스트가 시작되며 코딩 벤치마크에서 새로운 SOTA를 기록한 것으로 알려졌습니다. 엔터프라이즈 도입 가속화가 예상됩니다." },
        { title: "EU AI Act 단계적 시행", body: "5월부터 고위험 AI 시스템에 대한 첫 번째 의무 조항이 발효되며, 글로벌 기업들의 컴플라이언스 대응이 본격화됐습니다." },
        { title: "엔비디아 H200 공급 정상화", body: "지난 분기 병목이었던 H200 GPU 공급이 정상화되며 클라우드 사업자들의 인프라 확장이 재개되고 있습니다." },
      ],
      trends: [
        { k: "오픈소스 모델 경쟁:", v: "Meta, Mistral, DeepSeek 등이 잇따라 신모델을 공개하며 폐쇄형 모델과의 격차를 좁히고 있습니다." },
        { k: "AI 거버넌스 표준화:", v: "ISO/IEC 42001 AI 경영시스템 표준 도입이 글로벌 기업들 사이에서 빠르게 확산되고 있습니다." },
      ],
    },
    analysis_ko: {
      title: "🇰🇷 국내 뉴스 분석",
      lead: "국내 IT·경제 시장 주요 동향을 분석했습니다.",
      issues: [
        { title: "SK하이닉스 HBM4 양산 돌입", body: "차세대 고대역폭 메모리 HBM4 양산 라인이 본격 가동되며, 엔비디아·AMD향 공급 계약이 확정됐습니다." },
        { title: "네이버·카카오 AI 사업 재편", body: "두 회사 모두 AI 사업부를 별도 법인화하는 방안을 검토 중이며, 이는 글로벌 투자 유치와 의사결정 속도 제고를 위한 조치입니다." },
      ],
      trends: [
        { k: "K-반도체 호황 지속:", v: "메모리 수요 강세와 환율 효과로 1분기 실적이 시장 전망을 상회했습니다." },
      ],
    },
    matched: [
      { label: "국내 IT·기술", title: "SK하이닉스 HBM4 양산 본격화…엔비디아향 첫 출하", link: "#", quote: "SK하이닉스가 차세대 고대역폭 메모리 HBM4 양산을 본격적으로 시작했다. 첫 출하분은 엔비디아의 차세대 AI 가속기에 탑재될 예정이다." },
    ],
    news_en: [
      { label: "AI·ML", title: "Anthropic teases Claude 4 with breakthrough coding benchmark", link: "#" },
      { label: "AI·ML", title: "EU AI Act enters first compliance phase as enterprises scramble", link: "#" },
      { label: "글로벌 기술", title: "Nvidia H200 supply finally catches up to insatiable demand", link: "#" },
      { label: "글로벌 기술", title: "Meta releases Llama 4 with native multimodal capabilities", link: "#" },
    ],
    news_ko: [
      { label: "국내 IT·기술", title: "SK하이닉스 HBM4 양산 본격화…엔비디아향 첫 출하", link: "#" },
      { label: "국내 경제", title: "네이버·카카오, AI 사업부 별도 법인화 검토", link: "#" },
      { label: "국내 경제", title: "한은, 5월 금통위서 기준금리 동결 유력", link: "#" },
    ],
  },
  {
    date: "2026-05-12",
    displayDate: "2026년 05월 12일",
    stats: { total: 138, en: 79, ko: 59, sent_to_ai: 30, matched: 1 },
    generated_at: "2026-05-12 05:51 KST",
    analysis_en: {
      title: "🌐 Global News Analysis",
      lead: "월요일 뉴스의 주요 흐름을 정리했습니다.",
      issues: [
        { title: "오픈AI 신규 추론 모델 발표", body: "GPT-5의 추론 강화 버전이 공개됐으며, 복잡한 수학·과학 문제 해결 능력이 크게 개선됐습니다." },
        { title: "Apple WWDC 2026 사전 분석", body: "다음 달 WWDC에서 발표될 Apple Intelligence 2세대에 대한 기대가 높아지고 있습니다." },
      ],
      trends: [
        { k: "AI 에이전트 표준화:", v: "MCP(Model Context Protocol)가 사실상의 표준으로 자리잡으며 도구 통합이 가속화되고 있습니다." },
      ],
    },
    analysis_ko: {
      title: "🇰🇷 국내 뉴스 분석",
      lead: "월요일 국내 시장 주요 이슈입니다.",
      issues: [
        { title: "현대차 전기차 시장 점유율 회복", body: "유럽 시장에서 신형 아이오닉 라인업이 호평을 받으며 점유율이 회복세를 보이고 있습니다." },
      ],
      trends: [
        { k: "K-콘텐츠 글로벌 확장:", v: "넷플릭스·디즈니플러스 한국 오리지널 라인업이 동시에 강세를 보이고 있습니다." },
      ],
    },
    matched: [],
    news_en: [
      { label: "AI·ML", title: "OpenAI unveils GPT-5 Reasoning with breakthrough math performance", link: "#" },
      { label: "글로벌 기술", title: "Apple WWDC 2026 preview: what to expect from Apple Intelligence 2.0", link: "#" },
    ],
    news_ko: [
      { label: "국내 IT·기술", title: "현대차, 유럽 전기차 시장 점유율 회복세", link: "#" },
      { label: "국내 경제", title: "삼성SDI, 차세대 전고체 배터리 시범생산 돌입", link: "#" },
    ],
  },
];

// Older archive entries (just date stubs)
window.ARCHIVE_ENTRIES = [
  ...window.REPORTS.map((r) => ({ date: r.date, displayDate: r.displayDate })),
  ...["2026-05-11", "2026-05-10", "2026-05-09", "2026-05-08", "2026-05-07",
      "2026-05-06", "2026-05-05", "2026-05-04", "2026-05-03", "2026-05-02"]
    .map((d) => ({
      date: d,
      displayDate: `2026년 ${d.slice(5, 7)}월 ${d.slice(8, 10)}일`,
    })),
];
