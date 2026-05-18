// Shared news data — sample from reports/news_2026-04-19.md
// Synthesized AI summary so we can show what an actual analysis looks like

window.NEWS_DATA = {
  date: "2026-04-19",
  dateKo: "2026년 4월 19일 일요일",
  generatedAt: "2026-04-19 04:48 KST",
  issueNo: 47,

  stats: {
    total: 61,
    en: 0,
    ko: 61,
    analyzed: 40,
    dedupSkipped: 12,
    sources: 7,
  },

  // Top-level highlights extracted from the AI analysis
  highlights: [
    {
      headline: "이 대통령, 인도·베트남 국빈방문 출국",
      blurb: "에너지 공급망 협력 논의가 핵심 의제. 호르무즈 재봉쇄로 원유 수급 불확실성 확대 국면에서 미국산 원유 도입 확대 카드가 함께 거론된다.",
      category: "POLITICS",
      categoryKo: "정치·외교",
      source: "한겨레 · 연합뉴스TV",
    },
    {
      headline: "북한, 신포서 단거리 탄도미사일 140㎞ 비행",
      blurb: "국가안보실은 안보리 결의 위반 도발행위로 규정. 4·19혁명 66주년과 맞물려 안보 긴장도가 한 단계 상승.",
      category: "SECURITY",
      categoryKo: "안보",
      source: "연합뉴스TV · 한겨레",
    },
    {
      headline: "코스피, 종전 기대에 사상 최고치 재시동",
      blurb: "외국인·일본계 자금이 돌아오는 가운데 SK하이닉스 성과급 25조 화제. 반면 환율은 1,400원 후반대 박스권에서 횡보.",
      category: "MARKETS",
      categoryKo: "증권·투자",
      source: "한국경제 · 매일경제",
    },
  ],

  // Section summaries (the AI 'combined' output)
  sections: [
    {
      id: "politics",
      title: "정치·외교·안보",
      bullets: [
        "이재명 대통령이 인도·베트남 국빈방문에 나서며 첫 순방지로 인도에 향했다. 에너지 공급망 다변화와 경제안보 협력이 핵심 의제.",
        "호르무즈 해협 재봉쇄 국면이 길어지며 산업통상자원부 장관은 미국산 원유 도입 확대가 “불가피하다”고 발언.",
        "북한이 신포에서 단거리 탄도미사일을 발사해 140㎞를 비행. 국가안보실은 안보리 결의 위반 도발로 규정.",
        "4·19혁명 66주년 기념행사가 부산을 비롯한 전국에서 진행.",
      ],
    },
    {
      id: "economy",
      title: "경제·산업",
      bullets: [
        "IMF 총재가 한국 중기 재정건전성 노력을 긍정 평가. 5월 여객선 유류할증료가 최고 단계로 인상되며 운임 부담 확대.",
        "현대엘리베이터가 고층용 모듈러 공법을 세계 최초로 상용화. 동박 3사는 니켈도금 동박 선점전에 본격 진입.",
        "중기부가 ‘비정상의 정상화’ TF를 발족, 글로벌 소상공인에 최대 1억 지원 프로그램을 가동.",
      ],
    },
    {
      id: "tech",
      title: "IT·기술",
      bullets: [
        "JB금융이 전 계열사 ‘AI 에이전트화’에 착수하며 업무·시스템 동시 재편. 수출입은행도 자체 생성형 AI 플랫폼 구축에 들어감.",
        "리벨리온 AI 반도체 ‘리벨100’이 글로벌 오픈소스 추론 모델에서 성능을 입증. 테라텍-엣지AI는 국산 NPU 기반 인프라 생태계 확장 협력.",
        "젠슨 황은 미국 기술 규제를 “패배주의이자 광기”라고 직격. 구찌-구글은 2027년 AI 안경 출시 협업 발표.",
      ],
    },
    {
      id: "markets",
      title: "증권·투자",
      bullets: [
        "코스피 신기록 가능성에 시장 관심 집중. 외국인·일본계 자금 유입이 재개되며 ‘육천피도 아직 싸다’ 분석이 나옴.",
        "SK하이닉스 성과급 재원이 25조 원에 달하며 업계 전반의 성과급 기대가 커짐.",
        "‘2030 코스피’ vs ‘5060 반도체’로 연금 ETF 투자 성향이 세대별로 양분되는 양상.",
      ],
    },
  ],

  articles: [
    { cat: "politics", catKo: "정치", title: "이 대통령, 첫 순방지 인도 향발…경제안보 지평 넓힌다", source: "연합뉴스TV", url: "https://www.yonhapnewstv.co.kr/news/MYH20260419131736cSd", time: "13:17" },
    { cat: "politics", catKo: "정치", title: "호르무즈 재봉쇄…2차 종전 협상 벼랑 끝 대치", source: "연합뉴스TV", url: "#", time: "13:14" },
    { cat: "politics", catKo: "정치", title: "산업장관 \"미국산 원유 도입 확대 불가피\"", source: "연합뉴스TV", url: "#", time: "13:10" },
    { cat: "security", catKo: "안보", title: "북한, 신포서 단거리 탄도미사일 발사…140㎞ 비행", source: "연합뉴스TV", url: "#", time: "13:16" },
    { cat: "society", catKo: "사회", title: "[날씨] 휴일 '30도 육박' 초여름 더위…제주 비", source: "연합뉴스TV", url: "#", time: "13:10" },
    { cat: "politics", catKo: "정치", title: "이 대통령, 인도·베트남 국빈방문 출국…에너지 공급망 협력 논의", source: "한겨레", url: "#", time: "12:42" },
    { cat: "society", catKo: "사회", title: "'공영주차장 5부제' 참여 1694곳 뿐…수치 파악 못 해 '5분의 1' 수준", source: "한겨레", url: "#", time: "12:18" },
    { cat: "economy", catKo: "경제", title: "상장폐지 피하려 시세조종·허위거래까지…금감원, 합동 대응 착수", source: "한겨레", url: "#", time: "12:02" },
    { cat: "economy", catKo: "경제", title: "IMF 총재 \"한국 중기 재정건전성 노력, 안정적 재정운용 도움될 것\"", source: "한겨레", url: "#", time: "11:48" },
    { cat: "society", catKo: "사회", title: "'박진성 시인 성폭력 고발' 김현진씨 사망에 \"가해자 옹호 사회와 싸우다\"", source: "한겨레", url: "#", time: "11:30" },
    { cat: "security", catKo: "안보", title: "국가안보실 \"북 탄도미사일 발사, 안보리 결의 위반 도발행위\"", source: "한겨레", url: "#", time: "11:12" },
    { cat: "world", catKo: "국제", title: "룰라, 트럼프 겨냥 \"아침마다 전쟁 선언 대통령 SNS 보며 깰 순 없어\"", source: "한겨레", url: "#", time: "10:55" },
    { cat: "society", catKo: "사회", title: "4·19혁명 66주년…부산서 다양한 기념행사", source: "한겨레", url: "#", time: "10:30" },
    { cat: "economy", catKo: "경제", title: "미국·이란 중동전쟁에 발목잡혔다… 사라진 '봄철 특수'", source: "한국경제", url: "#", time: "10:12" },
    { cat: "economy", catKo: "경제", title: "한국 상륙한 英 항공사…\"혁신 서비스로 게임체인저 될 것\"", source: "한국경제", url: "#", time: "09:58" },
    { cat: "economy", catKo: "경제", title: "현대엘리베이터, 고층용 모듈러공법 세계 최초 상용화", source: "한국경제", url: "#", time: "09:30" },
    { cat: "economy", catKo: "경제", title: "항공료 이어 배값도 올랐다… 5월 여객선 유류할증료 최고 단계", source: "한국경제", url: "#", time: "09:15" },
    { cat: "economy", catKo: "경제", title: "돌아오는 외국인 '큰 손'...일본계 자금도 우르르", source: "매일경제", url: "#", time: "08:48" },
    { cat: "economy", catKo: "경제", title: "\"하이닉스 성과급 우리도\"…성과급 재원만 25조원", source: "매일경제", url: "#", time: "08:30" },
    { cat: "economy", catKo: "경제", title: "\"글로벌 소상공인 육성\"…중기부, 최대 1억 지원한다", source: "매일경제", url: "#", time: "08:12" },
    { cat: "tech", catKo: "IT·기술", title: "JB금융, 전 계열사 'AI 에이전트화' 착수…업무·시스템 동시 재편", source: "전자신문", url: "#", time: "08:00" },
    { cat: "tech", catKo: "IT·기술", title: "리벨리온 AI 반도체 '리벨100', 글로벌 오픈소스 AI 추론 모델에서 성능 입증", source: "전자신문", url: "#", time: "07:45" },
    { cat: "tech", catKo: "IT·기술", title: "에이치에너지, AI 에이전트 '헬리오스' 공개…\"에너지 소유·분배 구조 바꿀 것\"", source: "전자신문", url: "#", time: "07:30" },
    { cat: "tech", catKo: "IT·기술", title: "우주 전자파·방사선 모두 막는 초박막 '보호막' 개발", source: "전자신문", url: "#", time: "07:12" },
    { cat: "tech", catKo: "IT·기술", title: "'꿈의 배터리' 올라탄 동박 3사…니켈도금 동박 선점전 가열", source: "전자신문", url: "#", time: "06:55" },
    { cat: "tech", catKo: "IT·기술", title: "테라텍-엣지에이아이, 국산 NPU 기반 AI 인프라 생태계 확장에 '맞손'", source: "전자신문", url: "#", time: "06:40" },
    { cat: "tech", catKo: "IT·기술", title: "앤트로픽 '클로드' 인증 강화에 중국 개발자 '우회 경쟁' 격화", source: "AI타임스", url: "#", time: "06:30" },
    { cat: "tech", catKo: "IT·기술", title: "'자기학습 AI'로 설립 4개월 만에 7300억 투자 유치한 슈퍼 스타트업 등장", source: "AI타임스", url: "#", time: "06:15" },
    { cat: "tech", catKo: "IT·기술", title: "테슬라, 로보택시 서비스 댈러스·휴스턴으로 확대...\"등록 차량 1대뿐?\"", source: "AI타임스", url: "#", time: "06:00" },
    { cat: "tech", catKo: "IT·기술", title: "젠슨 황, 미국 기술 규제에 직격탄...\"패배주의이자 광기\"", source: "AI타임스", url: "#", time: "05:48" },
    { cat: "tech", catKo: "IT·기술", title: "구찌, 구글 파트너십으로 2027년 AI 안경 출시", source: "AI타임스", url: "#", time: "05:30" },
    { cat: "markets", catKo: "증권", title: "미국·이란 전쟁 협상에 '촉각'…환율 1400원 후반대 박스권 맴도나", source: "한국경제", url: "#", time: "05:15" },
    { cat: "markets", catKo: "증권", title: "\"삼전닉스 담았고 그 다음은…\" 고수들 서둘러 줍줍한 종목", source: "한국경제", url: "#", time: "05:00" },
    { cat: "markets", catKo: "증권", title: "종전 기대 고개 들자 실적에 쏠리는 눈…코스피 신기록 쓸까", source: "한국경제", url: "#", time: "04:48" },
    { cat: "markets", catKo: "증권", title: "\"사두면 오를 일만 남았다\"…개미들 빚까지 끌어서 '몰빵'", source: "한국경제", url: "#", time: "04:30" },
    { cat: "markets", catKo: "증권", title: "'2030 코스피' vs '5060 반도체'…확 갈린 '연금 ETF' 투자법", source: "한국경제", url: "#", time: "04:12" },
    { cat: "markets", catKo: "증권", title: "\"육천피 찍어도 아직 싸다\"…'역대급 저평가' 알짜 종목들", source: "한국경제", url: "#", time: "04:00" },
    { cat: "markets", catKo: "증권", title: "추격 매수 vs 쫓지 마…랠리, 쉬운 부분은 지났다?", source: "한국경제", url: "#", time: "03:48" },
  ],

  sourceDist: [
    { name: "한국경제", count: 14 },
    { name: "한겨레", count: 11 },
    { name: "전자신문", count: 9 },
    { name: "매일경제", count: 9 },
    { name: "AI타임스", count: 8 },
    { name: "연합뉴스TV", count: 6 },
    { name: "인포맥스", count: 4 },
  ],

  catDist: [
    { name: "경제", count: 19, color: "#1e6f5c" },
    { name: "IT·기술", count: 14, color: "#3b5bdb" },
    { name: "증권", count: 8, color: "#a14a07" },
    { name: "정치", count: 7, color: "#7a1f1f" },
    { name: "사회", count: 8, color: "#5a4a8a" },
    { name: "안보", count: 3, color: "#1f3a5f" },
    { name: "국제", count: 2, color: "#6b5b27" },
  ],
};
