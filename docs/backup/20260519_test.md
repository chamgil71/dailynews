✻ Cooked for 23m 30s

❯ 그런데 기존 app? index?  초기 화면이 왼편에 통계 내용이 나왔었는데 왜 사라졌지? 그리고 상단에 탭이 아니라 주식시황이 데일리뉴스 상단에 표기되는 건 이상하다.  디자인도 변경안됐고. &                       'c:\ai\dailynews\storage\AI News Daily.html' c:\ai\dailynews\storage\Snipaste_2026-05-18_17-36-40.png                                                                                                    
  
● 스크린샷과 원본 HTML을 확인하겠습니다.

  Read 2 files (ctrl+o to expand)

● 원본 HTML 파일도 확인합니다.

  Read 1 file (ctrl+o to expand)

● 원본 디자인을 이해했습니다. 현재 문제:                                                                                                                                                                   
  1. 사이드바 사라짐 - 원본은 왼쪽에 검색+통계+날짜 목록이 있는 2컬럼 레이아웃
  2. 주식 브리핑 허브 카드 - 뉴스 페이지 상단에 hub_sections_html()이 크게 표시됨 (제거해야 함)

  build_site.py와 현재 index.html을 확인합니다.

  Read 2 files (ctrl+o to expand)

● build_site.py의 실제 import 구조를 확인합니다:

  Searched for 1 pattern, read 2 files (ctrl+o to expand)

● index.html이 어떤 빌드 시스템으로 생성됐는지 확인합니다:

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● PowerShell(git diff HEAD~1 -- scripts/build_site.py | Select-Object -First 50)
  ⎿  (No output)

● PowerShell(git log --oneline -5 scripts/build_site.py)
  ⎿  646116b batch mailing + token unsubscribe + subscribe card
     60e0e7f refactor: docs → publish, 프롬프트/키워드 config 분리, RSS 소스 정비
     a852816 26-04-27 TG
     … +2 lines (ctrl+o to expand)

● PowerShell((Get-Content C:\ai\dailynews\scripts\build_site.py | Measure-Object -Line).Lines; (Get-Content C:\ai\dailynews\scripts\build_site.py)[0..15] -join "`n")
  ⎿  312
     # scripts/build_site.py
     """
     … +14 lines (ctrl+o to expand)
  ⎿  You've hit your limit · resets 7:30pm (Asia/Seoul)
     /upgrade to increase your usage limit.                                                                                                                                                                

✻ Worked for 2m 51s                                                                                                                                                                                          
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────❯  
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ⏵⏵ accept edits on (shift+tab to cycle)




지금 시스템을 폴더 구조를 개편 (아래는 구분의 예시이며 일반적인 개발방법에서 사용하는 분리구조로 정확히 맵핑 )
기본설정 - 스크립트 - 테마적용 - 웹서비스 로 구성되고 (추가로 노션, xlsx 저장등 부가)
제공 컨텐츠는 현재는 두가지 콘텐츠방식(뉴스데일리, 주식시황 )이 있고 카드뉴스는 예정되어 있다. 
전체는 유기적으로 동작해야하지만 독립적으로도 사용가능해야한다. 
테마역시 현재 4개 테마를 적용하지만 전체테마에서 색상스타일만 변경해서 뉴스, 시황을 구분하는 것도 필요하다.
(오히려 전체테마는 한개로 정하고, 뉴스, 시황을 색상스타일을 변경하는게 맞을지도 모른다.)
해당 내용 검토해 주고. 현재 프로젝트 폴더가 임의로 생성삭제된 내용이 많으니 정리해줘.
필요없어진 스크립트 등은 storage/ 폴더로 이동하고 개발프로젝트에 적합한 폴더구조로 재편해줘. 
마지막으로 정리된 내용은 readme, guide, worklog에 업데이트 해주고(마찬가지로 내용을 덮어쓰지말고 backup폴더로 복사한후 진행한다)
이 프로젝트는 총 3가지를 실험한다. 
- 뉴스, 주식 정보의 클리핑과 저장
- 저장된 내용을 테마시스템을 통한 디자인 변경
- 변경디자인과 컨텐츠를 다른 서비스와 연동

---

## 작업방향 (2026-05-19)

### 1. 폴더 구조 재편

**현재 문제**
- `core/`에 뉴스·주식 모듈이 혼재 (collector, analyzer, report, stock_*)
- `scripts/`에 빌드·실행·유틸리티가 뒤섞임
- 루트에 `integration_plan_mywiki.md`, `changes.patch` 등 관리 안 된 파일 산재
- `config/` 하위에 `sources/` 중첩 패키지

**목표 구조** (콘텐츠 타입 × 레이어 분리)

```
config/               # 기본설정 레이어
  settings.py         # 공통 환경변수
  theme_config.py     # 테마·푸터 설정
  watchlist.yaml      # 주식 종목 설정
  keywords.py / rss_sources.py / prompts.py / stock_prompts.py

core/                 # 핵심 로직 레이어 (콘텐츠 타입별 분리)
  news/
    collector.py      # ← core/collector.py
    analyzer.py       # ← core/analyzer.py
    report.py         # ← core/report.py
  stock/
    collector.py      # ← core/stock_collector.py
    analyzer.py       # ← core/stock_analyzer.py
    report.py         # ← core/stock_report.py
  shared/
    mailer.py         # ← core/mailer.py
    db.py             # ← core/db.py

scripts/              # 실행 진입점 (CLI 스크립트)
  run_news.py         # 뉴스 수집·분석·저장 (← main.py 역할)
  run_stock.py        # 주식 수집·분석·저장 (← scripts/stock_main.py)
  build_news.py       # 뉴스 사이트 빌드 (← scripts/build_site.py)
  build_stock.py      # 주식 사이트 빌드 (← scripts/build_stock_site.py)
  send_email.py       # 메일 발송 (← scripts/send_stock_email.py)
  init_db.py          # DB 초기화

themes/               # 테마 레이어
  base.py             # 공통 헬퍼 (split, news_list_section 등)
  classic.py / editorial.py / terminal.py / minimal.py / ink.py / forest.py
  __init__.py         # load_theme()

api/                  # 외부 서비스 API 엔드포인트 (Vercel)
  unsubscribe.py

publish/              # 웹서비스 빌드 산출물 (GitHub Pages) — 구조 유지
  index.html / app.html / archive.html
  stock/ (주식 HTML)
  reports-data.json / stock-data.json

reports/              # 클리핑 저장소
  news_YYYY-MM-DD.md
  stock/

templates/            # MD 리포트 템플릿
docs/                 # 문서
  backup/             # 기존 문서 백업본
storage/              # 보관·레거시 (더 이상 사용하지 않는 파일)
```

**정리 대상** (storage/ 이동 또는 삭제)
- `integration_plan_mywiki.md` → `docs/backup/`
- `changes.patch` → `storage/`
- `requirements.txt.backup` → `storage/`
- `main.py` → `scripts/run_news.py`로 역할 이전 후 루트에서 제거

---

### 2. 테마 시스템 방향

**현재**: 6개 완전 독립 테마 (classic / minimal / ink / forest / editorial / terminal)  
stock·email은 실제로는 모두 classic base에 위임 → 구조 불일치

**두 가지 선택지**

| | 다중 완전 테마 (현재) | 단일 마스터 + 색상 토큰 |
|---|---|---|
| 장점 | 레이아웃까지 극적으로 다름, 디자인 실험에 유리 | 유지보수 단순, 뉴스·주식·메일 색상 독립 적용 쉬움 |
| 단점 | 코드 중복, 새 테마 추가 공수 큼 | 레이아웃 차이 없음 |

**권장: 혼합 방식**
- 레이아웃 테마 3개만 유지: `classic` (일반 뉴스), `editorial` (신문), `terminal` (다크·금융)
- `ink`·`forest`·`minimal` → 색상 토큰(CSS variables)만 교체하는 color-variant로 전환
- `config/theme_config.py`의 `SECTION_THEMES`로 뉴스·주식·메일 각각 레이아웃 선택
- `--color-only` 플래그로 레이아웃 유지 색상만 교체 지원 (이미 CLI 문서에 정의됨)

---

### 3. 3개 실험 트랙 정의

**Track 1 — 클리핑 & 저장**
```
RSS / API → core/news|stock → reports/*.md → DB(SQLite)
```
- 수집·분석·저장이 독립 실행 가능 (`scripts/run_news.py`, `scripts/run_stock.py`)
- DB 스키마: `articles(id, date, lang, label, title, url, summary, sent_to_ai)`
- 카드뉴스 추가 시 `core/cardnews/` 레이어 추가만으로 확장

**Track 2 — 테마 디자인**
```
reports/*.md + themes/*.py → scripts/build_*.py → publish/*.html
```
- 빌드는 뉴스·주식 독립 실행 + 전체 일괄 빌드 모두 지원
- 테마 선택: `THEME_NEWS=editorial python scripts/build_news.py --from`
- 색상만 변경: `python scripts/build_news.py --color-only`

**Track 3 — 서비스 연동**
```
publish/*.html → GitHub Pages (웹)
reports/*.md   → Notion / Google Drive
email_html     → Gmail / TG
```
- 현재 구현: TG, Gmail 발송, GitHub Actions 자동화, Vercel 구독해제 API
- 예정: Notion 페이지 동기화, xlsx 저장, 카카오톡 MCP

---

### 4. 즉시 실행 순서

1. **백업** — `docs/*.md` → `docs/backup/YYYYMMDD_*.md` 복사
2. **정리** — 루트 stray 파일 → `storage/` 이동, `__pycache__` .gitignore 확인
3. **구조 재편** — `core/` 하위 뉴스·주식·shared 분리, `scripts/` 역할 재배치
4. **테마 정리** — ink·forest·minimal color-variant 전환, 레이아웃 테마 3개 고정
5. **문서 업데이트** — `news_readme.md`, `stock_readme.md`, `worklog.md` 반영



