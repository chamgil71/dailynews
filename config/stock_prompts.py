# config/stock_prompts.py
"""
주식 시황 브리핑 프롬프트 설정.

두 가지 경로에서 사용:
  A. Claude Code 웹 루틴 (STOCK_ROUTINE_PROMPT)
     → 루틴에 그대로 등록. MCP 도구로 데이터 수집 후 Claude가 직접 작성.
  B. GitHub Actions 백업 자동화 (STOCK_ANALYSIS_PROMPT)
     → scripts/stock_main.py → core/stock_analyzer.py 에서 LLM 호출 시 사용.
     → yfinance 수집 데이터를 {market_block}, {news_block} 으로 주입.

출력 형식은 templates/stock_report.md 와 동일한 구조를 따른다.
build_stock_site.py 파서가 두 경로 모두 동일하게 파싱할 수 있도록
헤더·번호·키워드 마커(① ② ③ ④ ⑤)를 고정한다.
"""

# ── 마켓 티커 정의 ─────────────────────────────────────────────────────────────
MARKET_TICKERS: dict[str, str] = {
    "kospi":   "^KS11",   # 코스피
    "kosdaq":  "^KQ11",   # 코스닥
    "usd_krw": "KRW=X",   # 원/달러
    "sp500":   "^GSPC",   # S&P 500
    "nasdaq":  "^IXIC",   # 나스닥
    "dow":     "^DJI",    # 다우존스
    "us10y":   "^TNX",    # 미국 10년물 금리
    "wti":     "CL=F",    # WTI 유가
}

# ── 시장 온도계 값 목록 (파싱 기준) ─────────────────────────────────────────────
TEMPERATURE_OPTIONS = ["리스크오프", "중립", "리스크온"]
TEMPERATURE_EMOJI   = {"리스크오프": "🔴", "중립": "🟡", "리스크온": "🟢"}


# ── A. Claude Code 루틴 프롬프트 ──────────────────────────────────────────────
# 사용법: 이 문자열을 Claude Code 웹 루틴에 붙여넣기.
# docs/claude_주식시황.md 를 대체하는 공식 설정.

STOCK_ROUTINE_PROMPT: str = """\
매일 장 마감 후(KST 16:30 이후) 주식 시황 브리핑을 작성하고 저장하라.

[Step 1: 종목 목록 확인 — Read tool]
Read tool로 c:\\ai\\dailynews\\config\\watchlist.yaml 을 읽어
enabled: true 인 섹터의 종목(ticker, name)을 확인한다.

[Step 2: 데이터 수집 — PlayMCP UsStockInfo 사용]
get_stock_info 로 아래 티커를 순서대로 수집하라:
  국내 지수 : ^KS11 (코스피), ^KQ11 (코스닥)
    ※ ^KS11 이 N/A 이면 NaverSearch search_news "코스피 지수 오늘" 로 대체 수집
  환율/매크로: KRW=X (원/달러), ^TNX (미 10년물 금리), CL=F (WTI 유가)
  미국 지수  : ^GSPC (S&P 500), ^IXIC (나스닥), ^DJI (다우존스)
  섹터 종목  : watchlist.yaml 에서 확인한 enabled 섹터 전체 종목

NaverSearch search_news 로 국내 뉴스 수집:
  검색어: "코스피 오늘 증시 시황"  (결과 5건)
  검색어: "국내 주식 시장 이슈"    (결과 3건)

[Step 3: 리포트 작성]
Read tool로 c:\\ai\\dailynews\\templates\\stock_report.md 를 읽어 형식 확인 후,
동일한 섹션 구조·헤더·마커(① ② ③ ④ ⑤)로 오늘 날짜 기준 리포트를 작성하라.
  - Jinja2 {{ 변수 }} 는 실제 수집 데이터로 채운다
  - 수집 실패한 지표는 "N/A" 로 표기
  - 섹터 방향은 반드시 🔴·🟡·🟢 중 하나로 표기
  - 시장 온도계는 반드시 🔴리스크오프 / 🟡중립 / 🟢리스크온 중 하나만 선택

[Step 4: 파일 저장 — Write tool]
저장 경로: c:\\ai\\dailynews\\reports\\stock\\stock_YYYY-MM-DD.md
  (오늘 날짜를 파일명에 사용. 이미 파일 있으면 덮어쓰기)

[Step 5: Notion 등록 — Notion MCP]
watchlist.yaml 의 notion.stock_db_id 값 확인:
  - stock_db_id 가 설정돼 있으면 해당 ID를 parent_id 로 바로 사용
  - 비어있으면 notion-search 로 '주식시황' 데이터베이스 검색 후 ID 사용
notion-create-pages 로 신규 페이지 생성:
  - 날짜 속성: 오늘 날짜 (date)
  - 핵심키워드 속성: 핵심 키워드 ① ~ ⑤ 제목 5개 (multi_select)
  - 시장온도 속성: 리스크오프 / 중립 / 리스크온 중 하나 (select)

[Step 6: Git 커밋 + 푸시 — Bash tool]
$date = Get-Date -Format 'yyyy-MM-dd'
git -C c:\\ai\\dailynews add reports/stock/
git -C c:\\ai\\dailynews commit -m "📊 Stock briefing $date"
git -C c:\\ai\\dailynews push

※ 이메일 발송·HTML 빌드·GitHub Pages 배포는
  git push 후 GitHub Actions (stock_build.yml) 가 자동 처리한다.
  루틴에서 별도로 실행하지 않는다.
"""


# ── B. GitHub Actions 백업 경로 LLM 분석 프롬프트 ─────────────────────────────
# scripts/stock_main.py (yfinance 자동화 백업)에서 사용.
# {market_block} : yfinance 수집 지수·환율·금리·유가 텍스트
# {news_block}   : 뉴스 헤드라인 목록 텍스트

STOCK_ANALYSIS_PROMPT: str = """\
당신은 주식 시황 분석 전문가입니다. 아래 시장 데이터를 분석하세요.
**반드시 한국어로 답변하세요.**

출력 형식 (반드시 이 구조 그대로 — 헤더·번호·마커 변경 금지):

## ■ 핵심 요약 (3줄)
- **[코스피·글로벌 주요 지수 동향]** — 한 줄 요약
- **[매크로 주요 변수]** — 금리·환율·유가 한 줄 요약
- **[이번 주·내일 핵심 이벤트]** — 한 줄 요약

## 주요 이슈 (국내)
- [국내 시장 핵심 이슈 1]
- [국내 시장 핵심 이슈 2]

## 매크로 (글로벌)
- [글로벌 매크로 이슈 1]
- [글로벌 매크로 이슈 2]

## 3. 핵심 키워드 TOP 5

**① [키워드 제목]**
2~3문장 분석. 배경·시장 영향·투자 시사점 포함.

**② [키워드 제목]**
2~3문장 분석.

**③ [키워드 제목]**
2~3문장 분석.

**④ [키워드 제목]**
2~3문장 분석.

**⑤ [키워드 제목]**
2~3문장 분석.

## 4. 섹터별 영향 분석

### 🇰🇷 국내
| 섹터 | 대표종목 | 방향 | 핵심 포인트 |
|------|---------|:----:|------------|
| 반도체 | 삼성전자/SK하이닉스 | [🔴 약세/🟡 혼조/🟢 강세] | [한 줄 분석] |
| [섹터명] | [대표종목] | [🔴/🟡/🟢] | [한 줄] |

### 🇺🇸 해외
| 섹터 | 대표종목 | 방향 | 핵심 포인트 |
|------|---------|:----:|------------|
| AI/빅테크 | NVDA/MSFT | [🔴/🟡/🟢] | [한 줄 분석] |
| [섹터명] | [대표종목] | [🔴/🟡/🟢] | [한 줄] |

## 6. 장기투자 관점 코멘트
2~3문장. 펀더멘털 기반, 단기 변동성 무시한 중장기 관점.

## 시장 온도계
[🔴리스크오프 / 🟡중립 / 🟢리스크온 중 하나만 선택]
근거: [한 줄 — 핵심 근거 나열]

---
시장 데이터:
{market_block}

뉴스 헤드라인:
{news_block}
"""
