# AI News & Stock Briefing 프로젝트 개선 계획서 (Project Improvement Plan v2.2)

> **최종 수정일**: 2026-05-22  
> **상태**: 사용자 피드백 반영 및 보안성 강화 완료 (Approved-Ready)  
> **대상 프로젝트**: AI Daily News + 주식시황 브리핑 자동화 시스템 (`chamgil71/dailynews`)  
> **목적**: 기존 프로젝트의 구조를 분석하여 전체 워크플로우와 서비스 연계도를 도출하고, 사용자 피드백을 기반으로 동적 중복 필터링 고도화, 노션 API 연동, Vercel 404 해소, 테마 로직 일원화, 그리고 동적 JSON 설정 기반의 다중 카드뉴스 가이드 및 활용 방안을 수립합니다. (중요 보안 검증을 통과하여 일체의 API 실물 Key는 환경변수로 격리 조치되었습니다.)

---

## 1. 프로젝트 구조 및 서비스 연계도 (Workflow & Integration Map)

본 시스템은 **정기 수집(RSS, Stock API) → AI 분석(Gemini 3.1) → DB 누적 및 동기화 → 사이트 빌드 → 다채널 배포(Vercel, Notion, SMTP Email)**의 전체 과정을 유기적으로 자동화하는 고급 파이프라인을 구축하고 있습니다.

### 1-1. 전체 데이터 흐름 및 서비스 연계 아키텍처

```mermaid
graph TD
    %% 실행 트리거
    Trigger["⏱️ GitHub Actions (정기 실행)"] --> Collector["📥 collector.py (RSS 수집)"]
    
    %% 중복 필터링 및 DB 파이프라인
    Collector --> CacheLoad["🔍 news_db.json 로드 (기존 링크 필터링)"]
    CacheLoad --> Filter["✨ 중복 제거된 신규 기사 추출"]
    
    %% 저장 및 동기화 파이프라인
    Filter --> JSONSave["💾 news_db.json 업데이트"]
    JSONSave --> XLSXSave["📊 news_db.xlsx 업데이트"]
    XLSXSave --> NotionSync["📝 Notion API 연동 (노션 DB 업데이트)"]
    
    %% Notion 관련 Credentials
    subgraph Notion Integration
        NotionSync --> NotionDB["Notion Database"]
        NotionToken["🔑 Notion Integration Token (환경변수 관리)"] -.->|API 인증| NotionSync
    end

    %% AI 분석 및 리포트 빌드
    Filter --> AI_Analyzer["🧠 Gemini 3.1 LLM (카테고리별 분석)"]
    AI_Analyzer --> ReportGen["✍️ report.py (reports/news_YYYY-MM-DD.md 생성)"]
    
    %% 사이트 빌드 & 호스팅
    ReportGen --> SiteBuilder["🏗️ build_site.py (HTML & JSON 빌드)"]
    SiteBuilder --> ThemeSystem["🎨 테마 시스템 (theme_config.py)"]
    
    subgraph 테마 운영 방식 (디자인 유지)
        ThemeSystem --> StyleA["Style A (Standard Jinja2)<br>classic, forest, ink"]
        ThemeSystem --> StyleB["Style B (Custom Python)<br>editorial, terminal, minimal"]
    end
    
    SiteBuilder --> Deploy["🚀 Vercel 정적 호스팅 배포"]
    SiteBuilder --> Email["✉️ mailer.py (Gmail SMTP 이메일 발송)"]
    
    %% Vercel 404 Rewrite / .gitignore 개선
    subgraph Vercel Routing
        Deploy --> VercelJson["vercel.json Routing (SPA Rewrite)"]
        Deploy --> GitIgnore["Git Tracked HTML (.gitignore 수정)"]
    end
```

---

## 2. 핵심 개선 영역 상세 계획 (Action Items)

### 2-1. [안정성] `news_db.json` 필터링 및 Notion API 연동 파이프라인

기존 엑셀 파일 직접 로드 방식 대신 데이터 구조화와 기동성이 뛰어난 `news_db.json`을 중복 필터링의 "단일 진실 원천(Single Source of Truth)"으로 삼습니다. 수집 프로세스 후 엑셀 데이터 보완과 Notion 동기화를 연쇄적으로 수행합니다.

#### 💡 고도화된 수집 & 적재 워크플로우
1. **링크 수집 (Link Collection)**: 지정된 RSS 피드 및 주식 정보에서 최신 뉴스를 1차 크롤링합니다.
2. **기존 JSON 필터링**: `storage/news_db.json`에 저장된 URL 목록을 대조하여 이미 수집 완료된 중복 기사를 완벽하게 제거합니다.
3. **JSON 업데이트**: 새로 수집된 기사를 `news_db.json` 파일에 고속으로 축적하고 저장합니다.
4. **Excel 업데이트**: 기존 `storage/news_db.xlsx` 엑셀 파일에도 데이터를 업데이트하여 로컬 데이터 백업 무결성을 보장합니다.
5. **Notion 업데이트**: 연동용 Notion API를 활용하여 노션 데이터베이스/페이지에 기사를 실시간 동기화합니다.

#### 📝 Notion API 연동 명세 (용도별 데이터베이스 이중화)
* **데이터베이스 혼선 방지 설계**: 뉴스 리스트 적재용 DB와 주식 시황 브리핑용 DB를 엄격히 분리하여 꼬이지 않게 통제합니다.
  * **`NOTION_DATABASE_ID_NEWS`**: 신규 수집된 데일리 뉴스 기사 저장용 데이터베이스 ID
  * **`NOTION_DATABASE_ID_STOCK`**: 주식 시황 및 마켓 온도계 분석 저장용 데이터베이스 ID
* **안전한 API Key 관리**: API 실물 토큰은 Git 추적 대상인 문서에 노출되지 않도록 **GitHub Secrets 및 로컬 `.env` 환경변수(`NOTION_API_KEY`)**로만 철저히 격리 관리합니다.
* **연동 모듈 설계 (`core/shared/notion.py` 추가 제안)**:
  ```python
  import requests
  import os
  import logging

  logger = logging.getLogger(__name__)

  NOTION_KEY = os.getenv("NOTION_API_KEY")
  NOTION_DB_NEWS = os.getenv("NOTION_DATABASE_ID_NEWS")
  NOTION_DB_STOCK = os.getenv("NOTION_DATABASE_ID_STOCK")

  def sync_news_to_notion(news_items: list, date_str: str):
      """수집 완료된 신규 뉴스 기사를 Notion 뉴스 데이터베이스에 Page 형태로 삽입"""
      if not NOTION_KEY or not NOTION_DB_NEWS:
          logger.warning("[Notion 뉴스] API 설정(NOTION_API_KEY, NOTION_DATABASE_ID_NEWS)이 환경변수에 누락되었습니다.")
          return
      
      headers = {
          "Authorization": f"Bearer {NOTION_KEY}",
          "Content-Type": "application/json",
          "Notion-Version": "2022-06-28"
      }
      
      for item in news_items:
          payload = {
              "parent": {"database_id": NOTION_DB_NEWS},
              "properties": {
                  "제목": {"title": [{"text": {"content": item["title"]}}]},
                  "날짜": {"date": {"start": date_str}},
                  "카테고리": {"select": {"name": item["category"]}},
                  "출처": {"select": {"name": item["label"]}},
                  "링크": {"url": item["link"]},
                  "요약": {"rich_text": [{"text": {"content": item["summary"]}}]}
              }
          }
          response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
          if response.status_code != 200:
              logger.warning(f"[Notion 뉴스 동기화 실패] {response.text}")

  def sync_stock_to_notion(stock_summary: dict, date_str: str):
      """분석된 주식 시황 및 지표 정보를 Notion 주식시황 데이터베이스에 Page 형태로 삽입"""
      if not NOTION_KEY or not NOTION_DB_STOCK:
          logger.warning("[Notion 주식] API 설정(NOTION_API_KEY, NOTION_DATABASE_ID_STOCK)이 환경변수에 누락되었습니다.")
          return
      # 주식 시황 용도의 동기화 로직도 독립적으로 여기에 구현 (뉴스 DB와 완전히 물리적 분리 보장)
  ```

---

### 2-2. [일관성] Vercel 404 오류 해결 및 SPA 라우팅 최적화

현재 날짜별 정적 HTML 파일이 `.gitignore`에 등록되어 배포 컨테이너 내에 존재하지 않음으로 인해 발생하는 Vercel 호스팅 404 문제를 해결합니다.

#### 💡 실행 계획 (동시 반영)
1. **`.gitignore` 파일의 수정**:
   날짜별 정적 HTML 생성 파일을 주석 처리하여 Git이 해당 파일을 추적할 수 있도록 변경합니다.
   ```diff
   # .gitignore
   # 날짜별 자동 생성 HTML 배포 추적 대상화
   - publish/20??-??-??.html
   - publish/stock/20??-??-??.html
   + # publish/20??-??-??.html
   + # publish/stock/20??-??-??.html
   ```
2. **`vercel.json` 라우팅 리라이트 룰 보완**:
   Vercel에 직접적인 날짜 경로(`/2026-05-22` 등) 요청이 왔을 때 404 에러를 뿜지 않고 `publish/app.html` SPA로 자연스럽게 Rewrite되어, 브라우저 스크립트가 `reports-data.json`에서 해당 데이터를 비동기적으로 로딩하고 화면을 즉석 렌더링하도록 일관된 라우팅 체계를 확립합니다.
   ```json
   {
     "src": "/(\\d{4}-\\d{2}-\\d{2})",
     "dest": "/publish/app.html"
   }
   ```

---

### 2-3. [일관성] 테마 획득 로직 정상화 및 기존 디자인 유지

현재 테마 폴더에 공존하는 두 가지 서로 다른 디자인 운영 방식을 철저히 파악하고, **기존 디자인의 훌륭한 비주얼 및 코드는 그대로 유지하면서** 제어의 일관성을 높입니다.

#### 🎨 테마 운영 방식의 두 종류 분석 (기존 코드 유지 보장)
* **Style A (Standard Jinja2)**: `classic.py`, `forest.py`, `ink.py` 테마.
  * `base.py` 및 `templates/web_news.html`, `web_stock.html` 템플릿 파일을 경유하여 빌드됩니다.
  * 레이아웃의 수정은 HTML 템플릿에서 수행하며, 폰트 및 색상 정보만 `TOKENS`를 통해 dynamic CSS 변수로 제어됩니다.
* **Style B (Custom Python Layout)**: `editorial.py`, `terminal.py`, `minimal.py` 테마.
  * Jinja2 템플릿 파일을 배제하고, Python 스크립트 내부에서 직접 HTML/CSS 문자열을 f-string과 도구 함수로 만들어 반환합니다.
  * 매우 높은 가독성과 미려하고 독창적인 타이포그래피 레이아웃(예: 신문 스타일의 다단 구성, 모노스페이스 다크 터미널 등)을 완벽히 유지합니다.

#### 💡 개선 방안: 제어 구조 정규화
1. **`build_stock_site.py` 로직 일원화**:
   특정 테마 환경변수가 누락되었을 때의 Fallback 로직을 `SECTION_THEMES.get("stock", SITE_THEME)` 방식으로 확실하게 정상화합니다.
2. **워크플로우 하드코딩 제거**:
   GitHub Actions YAML 파일들 내부에 하드코딩되어 있던 특정 테마 지정 변수(`THEME_NEWS: editorial` 등)를 전부 소거하고, 오직 `theme_config.py` 파일의 딕셔너리 구조 혹은 GitHub Secret 단 한 곳에서만 전체 테마를 통제하도록 중앙 일원 관리 구조를 완성합니다.

---

### 2-4. [확장성] Phase 2: 카드뉴스 생성 자동화 및 설정 동적화

`reports-data.json`에 추출되어 정제되어 있는 고해상도 요약 데이터와 핵심 이슈들을 기반으로, 모바일 및 SNS 환경에 최적화된 비주얼 프리미엄 카드뉴스 템플릿을 자동으로 렌더링하고 배포하는 설계를 고도화합니다.

#### 🎨 카드뉴스 디자인 테마의 JSON 관리 (하드코딩 방지)
카드뉴스의 디자인 요소(배경 그라데이션, 카드 투명도, 테두리, 폰트 색상 등)를 소스 코드 내에 하드코딩하지 않고, **`config/cardnews_themes.json`** 이라는 설정 파일에서 종합 관리합니다. 여러 디자인 샘플을 등록한 후 테마 키워드 하나로 즉각 교체 가능하게 유연성을 보장합니다.

* **`config/cardnews_themes.json` 설계 명세**:
  ```json
  {
    "active_card_theme": "glass_dark",
    "themes": {
      "glass_dark": {
        "name": "Glassmorphism Dark",
        "bg_gradient": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        "card_bg": "rgba(255, 255, 255, 0.05)",
        "card_border": "rgba(255, 255, 255, 0.1)",
        "card_blur": "16px",
        "text_primary": "#f8fafc",
        "text_muted": "#94a3b8",
        "accent_color": "#38bdf8",
        "shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
      },
      "neon_cyber": {
        "name": "Neon Cyberpunk",
        "bg_gradient": "linear-gradient(135deg, #0b0f19 0%, #111827 100%)",
        "card_bg": "rgba(17, 24, 39, 0.7)",
        "card_border": "rgba(139, 92, 246, 0.3)",
        "card_blur": "12px",
        "text_primary": "#ffffff",
        "text_muted": "#9ca3af",
        "accent_color": "#a78bfa",
        "shadow": "0 0 15px rgba(139, 92, 246, 0.4)"
      },
      "minimal_light": {
        "name": "Minimalist Light",
        "bg_gradient": "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
        "card_bg": "rgba(255, 255, 255, 0.85)",
        "card_border": "rgba(226, 232, 240, 1)",
        "card_blur": "0px",
        "text_primary": "#0f172a",
        "text_muted": "#475569",
        "accent_color": "#ea580c",
        "shadow": "0 10px 25px rgba(148, 163, 184, 0.1)"
      }
    }
  }
  ```

#### ❓ 다중 카드뉴스 활용 방안 및 동작 원리 가이드 (User Guide)

"카드뉴스를 어떻게 실제로 잘 사용(써먹을)할 수 있는지"에 대한 대표적 시나리오와 다중 카드 전개 시의 대응 방향입니다.

* **💡 실질적 비즈니스/서비스 활용 시나리오**
  1. **모바일 SNS(인스타그램, 스레드, 블로그 등) 원클릭 이미지 내보내기**:
     - 빌드된 카드뉴스 페이지 하단에 **"인스타그램 이미지로 저장"** 버튼을 제공합니다.
     - 클라이언트 브라우저 표준 라이브러리인 `html2canvas`를 CDN으로 가볍게 연동하여, 사용자가 버튼을 클릭하면 각 뉴스 카드 슬라이드가 1:1 정방형(1080x1080px) 고품질 PNG 파일로 기기에 바로 다운로드됩니다.
     - 이를 인스타그램 슬라이드(피드)나 스레드에 그대로 업로드하여 채널 유입 및 SNS 브랜딩 콘텐츠로 200% 활용합니다.
  2. **뉴스 브리핑 웹사이트 최상단 Shorts 배너**:
     - 바쁜 아침, 기사 리포트 전체 텍스트를 읽기 부담스러운 독자들을 위해 사이트 진입 시 최상단 비주얼 요약 영역에 카드를 노출시킵니다.
     - 15초 만에 핵심 기사 3건을 스와이프로 가볍게 훑어보고(Shorts-form), 관심 있는 카드 클릭 시 상세 기사 분석 위치로 스무스 스크롤 이동을 지원합니다.
  3. **이메일 본문 유기적 세로 나열 결합**:
     - 아침 메일 본문 상단 영역에 미려한 수직 카드 레이아웃으로 핵심 뉴스 3건을 먼저 인상 깊게 노출시켜 메일 구독자 클릭율(CTR)을 높이고, 카드 하단의 "전체 카드뉴스 가로 스냅으로 보기" CTA를 통해 정적 웹사이트로의 트래픽 전환을 유도합니다.

* **💡 옆으로 넘기는(가로 스와이프) 다중 카드 기술적 대응 명세**
  1. **Pure CSS Scroll Snap을 활용한 초경량 모바일 스와이프**:
     - SwiperJS와 같이 100KB가 넘어가는 무거운 외부 JavaScript 라이브러리를 일절 배제하여 빠른 로딩 속도를 확보합니다.
     - CSS의 `scroll-snap-type: x mandatory;`와 `scroll-snap-align: center;`를 적극 활용하여, 모바일에선 스마트폰 기본 앨범 앱처럼 손가락으로 슥 넘겼을 때 자석처럼 찰칵찰칵 걸리며 부드럽게 스와이프되는 모바일 네이티브 감각을 완벽 구현합니다.
  2. **PC 마우스 환경을 위한 인디케이터 및 네비게이션 바인딩**:
     - 데스크톱 사용자의 마우스 휠 및 클릭 경험을 위해 카드 좌우측에 반투명한 블러 화살표 버튼(` < `, ` > `)을 탑재합니다.
     - 버튼 클릭 시 바닐라 JS의 `element.scrollTo({ left: ..., behavior: 'smooth' })` API를 호출해 부드럽게 이동하게 제어하고, 하단에 점(Indicator Dot) 표시를 연동해 현재 몇 번째 카드를 읽고 있는지 한눈에 인지하도록 돕습니다.

#### 📱 Premium Card News UI 디자인 템플릿 구상 시안

> [!NOTE]
> 모바일 기기 화면을 고려하여 다크 테마 기반의 매혹적인 **글래스모피즘(Glassmorphism)**과 가로 스크롤 스와이프 인터페이스, 가독성이 뛰어난 산세리프 폰트를 결합한 비주얼 디자인 시안입니다.

![Premium Card News UI Mockup](file:///C:/Users/nipa/.gemini/antigravity/brain/453071cc-386e-4aac-afa7-2f755d0060ab/card_news_mockup_1779425483113.png)

---

### 2-5. [확장성] 텔레그램(Telegram) 실시간 알림 파이프라인 연동

자동 생성된 핵심 카드뉴스와 에디션 요약을 사용자님의 **텔레그램(Telegram) 개인 대화방 또는 공개 채널**로 즉시 실시간 전송하는 파이프라인을 구축합니다. 이 역시 철저한 환경변수 보안 격리 모델을 따릅니다.

#### 🛠️ 사용자 준비 사항 (Telegram Credentials 획득)
1. **봇 생성 및 API 토큰 획득 (`TELEGRAM_BOT_TOKEN`)**:
   * 텔레그램에서 **`@BotFather`** 검색 후 대화방 진입 ➔ `/newbot` 입력.
   * 봇 이름 및 아이디(반드시 `_bot`으로 종결) 설정 후 발급되는 **HTTP API 토큰**(예: `123456789:ABCde...`)을 메모해 둡니다.
2. **대상 수신방 ID 획득 (`TELEGRAM_CHAT_ID`)**:
   * **개인 톡방 수신 시**: 생성된 봇 링크를 누르고 들어가 `/start`를 보냅니다. 이후 텔레그램의 **`@GetMyChatID_Bot`** 등을 통해 본인의 숫자형 Chat ID(예: `987654321`)를 획득합니다.
   * **채널/그룹방 수신 시**: 텔레그램 채널을 생성하고 생성한 봇을 **관리자(Administrator)**로 등록합니다. 채널의 주소 ID(예: `@my_news_channel`)를 획득합니다.
3. **자격 증명 등록**: 획득한 값들을 로컬 `.env` 및 GitHub Secrets에 각각 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`로 등록해 주시면 준비 완료됩니다.

#### 📝 텔레그램 전송 모듈 설계 (`core/shared/telegram.py` 신규 제안)
* **메시지 전송 스펙**: HTML 마크다운 태그를 바인딩하여 깔끔한 비주얼 텍스트 형태로 전송하고, 웹사이트 원문 카드뉴스로 갈 수 있는 CTA 버튼을 결합합니다.
  ```python
  import requests
  import os
  import logging

  logger = logging.getLogger(__name__)

  BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
  CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

  def send_telegram_briefing(issues: list, date_str: str, web_url: str):
      """오늘의 핵심 이슈 3개를 정돈하여 텔레그램 봇으로 전송"""
      if not BOT_TOKEN or not CHAT_ID:
          logger.warning("[Telegram] API 설정(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)이 환경변수에 누락되었습니다.")
          return False
      
      # 텍스트 포맷 구성
      text = f"📢 <b>{date_str} 오늘의 AI News Briefing</b>\n\n"
      for i, issue in enumerate(issues[:3], start=1):
          text += f"🔥 <b>이슈 {i}. {issue['title']}</b>\n"
          text += f"➔ {issue['body'][:120]}...\n"
          if issue.get("url"):
              text += f"🔗 <a href='{issue['url']}'>원문 링크</a>\n"
          text += "\n"
      
      text += f"🃏 <a href='{web_url}'>모바일에서 가로 스크롤 카드뉴스로 읽기</a>"
      
      url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
      payload = {
          "chat_id": CHAT_ID,
          "text": text,
          "parse_mode": "HTML",
          "disable_web_page_preview": False
      }
      
       try:
          response = requests.post(url, json=payload, timeout=10)
          if response.status_code == 200:
              logger.info("[Telegram] 데일리 브리핑 알림 전송 완료!")
              return True
          else:
              logger.warning(f"[Telegram] 알림 전송 실패: {response.text}")
      except Exception as e:
          logger.error(f"[Telegram] 전송 에러 발생: {e}")
      return False
  ```

### 2-6. [사용성] 검색 시스템 UI 고도화 (좌측 검색 - 우측 결과 통합 연동)

현재 `app.html` 웹 앱에서 제공되는 검색창은 선택된 당일 리포트 내의 기사를 필터링하고 키워드를 하이라이팅하는 구조입니다. 이를 한층 업그레이드하여, **좌측 검색창에서 검색어를 입력하면 우측 영역에 해당하는 모든 과거 기사 목록(날짜 정보 포함)이 카드 및 리스트 형태로 즉시 취합되어 나타나는 지능형 검색 환경**을 계획합니다.

#### 💡 UI 및 기능적 설계 방안
1. **검색 전용 결과 뷰(Search View) 도입**:
   - 사용자가 좌측 검색창에 단어를 입력하기 시작하면, 현재 활성화된 뉴스/주식 브리핑 상세 뷰에서 **'검색 결과 리스트 뷰'로 우측 메인 영역이 부드럽게 전환**됩니다.
   - 검색창을 지우면(`value === ""`), 기존에 보고 있던 날짜의 상세 브리핑 뷰로 원복됩니다.
2. **과거 데이터 전수 검색 (Global Search)**:
   - `reports-data.json`은 뉴스 목록(`news_en`/`news_ko`)을 제거하여 경량화되어 있으므로, 전체 기간에 대한 고속 검색을 위해 다음 2가지 방안을 검토합니다.
     - **방안 A (경량 로컬 캐시)**: 사용자가 검색을 개시하면 백그라운드에서 아직 로드되지 않은 최근 N일간의 `publish/news/YYYY-MM-DD.json` 파일들을 비동기 패치하여 브라우저 메모리 캐시에 적재 후 고속 필터링을 수행합니다.
     - **방안 B (검색 인덱스 활용)**: 빌드 시점(`build_site.py`)에 전체 기사의 제목과 링크, 날짜, 카테고리를 결합한 컴팩트한 검색 전용 인덱스 파일(`publish/search-index.json`, 약 100~200KB)을 별도 빌드하여 서빙하고, 클라이언트가 이를 한 번만 받아 로컬에서 0.1초 만에 완전 검색을 수행하도록 구현합니다.
3. **사용자 경험(UX) 개선**:
   - 우측 검색 결과 화면에 표시된 기사 항목을 클릭하면 새 탭으로 원문 기사가 열릴 뿐만 아니라, **"이 기사가 속한 날짜의 브리핑 전체 보기"** 링크를 제공하여 유기적인 콘텐츠 탐색이 가능하도록 구성합니다.
   - 키워드가 매칭된 영역을 노란색 `<mark>` 태그로 하이라이팅 처리하여 시인성을 높입니다.

---

## 3. 향후 계획 (Future Roadmap): 클라우드 DB 서비스 전환 설계

로컬 sqlite3의 한계(Stateless 환경에서의 데이터 무결성 보존의 복잡함, 깃허브 원격 푸시 의존성 등)를 극복하기 위해, **가볍고 관리가 필요 없는 클라우드 서버리스 데이터베이스(Cloud Serverless Database)**로의 연동 방안을 향후 계획으로 분리하여 정립합니다.

```
                  ┌──────────────────────────────┐
                  │   GitHub Actions Workflow    │
                  └──────────────┬───────────────┘
                                 │
                                 ▼ (수집 및 AI 가공 데이터)
                  ┌──────────────────────────────┐
                  │      Notion API / JSON       │
                  └──────────────┬───────────────┘
                                 │
                                 ▼ (실시간 동기화)
┌──────────────────────────────────────────────────────────────────┐
│             ☁️ Cloud Serverless Database Service                  │
│                                                                  │
│  - Supabase / Neon PostgreSQL (서버리스 트랜잭션 및 REST API 제공)  │
│  - 실시간 대시보드 및 다중 쓰기 세션 완벽 분리                          │
└──────────────────────────────────────────────────────────────────┘
```

### 3-1. 클라우드 DB 연동 아키텍처 개요
* **Supabase / Neon (Serverless PostgreSQL) 활용**:
  * 로컬 DB 파일 보관 방식을 과감히 벗어나 외부 클라우드 DB 인스턴스에 직접 커넥션을 생성하여 데이터를 안전하게 보존합니다.
  * SQL 표준 구문은 물론 RESTful API를 기본 지원하여 복잡한 라이브러리 설치 없이 데이터 입출력이 가능합니다.
* **마이그레이션 및 연동 단계**:
  1. 클라우드 포털에서 무료 티어 PostgreSQL(Supabase, Neon 중 택1) 데이터베이스 개설.
  2. 기 구축된 엑셀 데이터의 일괄 클라우드 이관 스크립트(`scripts/migrate_to_cloud.py`) 실행.
  3. `core/shared/db.py` 내부의 쿼리 인터페이스를 클라우드 API 호출 구조로 대체.
