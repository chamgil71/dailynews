# scripts/ 파일 가이드

> 최종 업데이트: 2026-06-13  
> `scripts/` 폴더의 각 Python 파일의 역할·사용법·의존관계를 정리합니다.

---

## 디렉터리 구조 요약

```
scripts/
├── 수집·분석 진입점
│   ├── run_news.py
│   ├── run_stock.py
│   ├── run_ai_issue.py
│   └── stock_main.py
│
├── 사이트 빌드
│   ├── build_site.py
│   ├── build_stock_site.py
│   ├── build_ai_issue_site.py
│   └── build_all.py
│
├── 카드뉴스
│   ├── build_cardnews.py
│   ├── generate_cardnews_images.py
│   ├── post_cardnews.py
│   └── post_instagram.py
│
├── 발송
│   ├── send_email.py
│   └── send_telegram.py
│
├── 모니터링
│   └── notify_pipeline.py
│
├── 동기화·마이그레이션
│   ├── sync_notion.py
│   ├── migrate_subscribers.py
│   ├── migrate_json_sidecars.py
│   └── init_db.py
│
└── 유지보수·분석
    ├── reanalyze.py
    ├── update_history.py
    └── validate_ai_issue_sources.py
```

---

## 1. 수집·분석 진입점

### `run_news.py`
**역할**: 뉴스 채널 전체 파이프라인 실행 (수집→분석→저장)  
**출력**: `reports/news_YYYY-MM-DD.md` + `.json`  
**사용처**: `news.yml` GitHub Actions  
```bash
python scripts/run_news.py
```

### `run_stock.py`
**역할**: 주식 시황 전체 파이프라인 (yfinance + Naver API → LLM 분석 → MD 저장)  
**출력**: `reports/stock/stock_YYYY-MM-DD.md`  
**사용처**: Claude Code 루틴 21:25 KST, `stock_main.py`에서 호출  
```bash
python scripts/run_stock.py
```

### `run_ai_issue.py`
**역할**: 주간 AI 이슈 브리핑 파이프라인 (arXiv + 블로그 → LLM 분석 → MD + JSON 저장)  
**출력**: `reports/ai-issue/ai_issue_YYYY-MM-DD.md` + `.json`  
**사용처**: `ai_issue.yml` GitHub Actions (일 07:00 KST)  
```bash
python scripts/run_ai_issue.py
```

### `stock_main.py`
**역할**: `run_stock.py`의 GitHub Actions용 래퍼. SSL 안정화 포함.  
**사용처**: `stock_build.yml` — 루틴 미실행 시 백업 자동 실행  
```bash
python scripts/stock_main.py
```

---

## 2. 사이트 빌드

### `build_site.py`
**역할**: 뉴스 MD → HTML 변환 + `search-index.json`, `data.json`, `archive.html` 생성  
**출력**: `publish/news/`, `publish/index.html`, `publish/search-index.json`  
**주요 함수**: `build(theme_name, from_date, rebuild_all)`, `build_search_index()`  
**사용처**: `news.yml`, `stock_build.yml`(search-index 갱신용), `build_all.py`  
```bash
python scripts/build_site.py --from 2026-06-10   # 특정 날짜 이후만
python scripts/build_site.py --all               # 전체 재빌드
```

### `build_stock_site.py`
**역할**: 주식 MD → HTML 변환 + `stock/index.html`, `stock/archive.html`, `stock/data.json` 생성  
**출력**: `publish/stock/`  
**주요 함수**: `build(theme_name)`  
**사용처**: `stock_build.yml`, `build_all.py`  
```bash
python scripts/build_stock_site.py
```

### `build_ai_issue_site.py`
**역할**: AI이슈 MD → HTML 변환 + `ai-issue/index.html`, `ai-issue/archive.html`, `ai-issue/data.json` 생성  
**출력**: `publish/ai-issue/`  
**주요 함수**: `build(theme_name)`, `main()`  
**사용처**: `ai_issue.yml`, `build_all.py`  
```bash
python scripts/build_ai_issue_site.py
```

### `build_all.py`
**역할**: 3채널 빌드 오케스트레이터. `build_site`, `build_stock_site`, `build_ai_issue_site`를 순차 실행 후 `search-index.json` 통합 갱신.  
**사용처**: 로컬 전체 재빌드 시 (CI에서는 채널별 개별 스크립트 사용)  
```bash
python scripts/build_all.py --all            # 전체 재빌드
python scripts/build_all.py --type stock     # 주식만
python scripts/build_all.py --from 2026-06-10
```

---

## 3. 카드뉴스

### `build_cardnews.py`
**역할**: 카드뉴스 HTML 생성 (채널별 PNG 렌더링용 슬라이드 HTML)  
**출력**: `publish/cardnews/{news|ai-issue|stock}/YYYY-MM-DD.html` + `data.json`  
**설정 파일**: `config/cardnews_themes.json` (채널별 accent/topbar/label), `templates/cardnews_card.css`  
**사용처**: `cardnews.yml`, `generate_cardnews_images.py` 전 단계  
```bash
python scripts/build_cardnews.py --type news
python scripts/build_cardnews.py --type all --all   # 전체 날짜 재빌드
```

### `generate_cardnews_images.py`
**역할**: Playwright(헤드리스 Chromium)로 카드뉴스 HTML → 1080×1080 PNG 변환. Pillow 폴백 지원.  
**출력**: `publish/cardnews/{channel}/YYYY-MM-DD-{N}.png`  
**의존성**: `playwright`, `Pillow`, 한국어 폰트(Noto Sans KR)  
**사용처**: `cardnews.yml`  
```bash
python scripts/generate_cardnews_images.py --type news --date 2026-06-10
```

### `post_cardnews.py`
**역할**: 카드뉴스 PNG를 멀티 플랫폼 SNS에 발송. 플랫폼별 분기 처리.  
**지원 플랫폼**: `instagram` (카루셀), `threads` (카루셀), `facebook` (멀티 사진), `telegram` (미디어 그룹), `twitter` (이미지 스레드)  
**텔레그램 채널 분기**: `stock` → `TELEGRAM_CHAT_ID_STOCK`, 그 외 → `TELEGRAM_CHAT_ID`  
**사용처**: `cardnews.yml`  
```bash
python scripts/post_cardnews.py --type news --platform instagram,threads,telegram
python scripts/post_cardnews.py --type stock --platform telegram --date 2026-06-09
```

### `post_instagram.py`
**역할**: Instagram 카루셀 전용 발송 스크립트. `post_cardnews.py`에서 내부적으로 import하여 사용.  
**API**: Meta Graph API v21.0 (`/media`, `/media_publish`)  
**직접 실행도 가능:**
```bash
python scripts/post_instagram.py --type news --date 2026-06-10
```

---

## 4. 발송

### `send_email.py`
**역할**: 3채널 이메일 발송 통합 스크립트. `--type`으로 채널 선택.  
**채널별 동작**:
- `news`: MD → Jinja2 템플릿 렌더링 → Gmail 발송
- `stock`: MD → 주식 전용 템플릿 → Gmail 발송 (report_date 기준 날짜 표시)
- `ai-issue`: JSON → HTML 빌드 → Gmail 발송  
**수신자 조회**: Supabase `subscribers` 테이블 (미설정 시 `RECIPIENT_EMAILS` 폴백)  
**사용처**: `news.yml`, `stock_send.yml`, `ai_issue.yml`  
```bash
python scripts/send_email.py --type stock --date 2026-06-09
python scripts/send_email.py --type news --force   # AI 분석 실패 플래그 무시
```

### `send_telegram.py`
**역할**: 3채널 텔레그램 발송 통합 스크립트.  
**채널별 동작**:
- `news`: 텍스트 요약 메시지 → `TELEGRAM_CHAT_ID`
- `stock`: 시황 요약 메시지 → `TELEGRAM_CHAT_ID_STOCK`
- `ai-issue`: 주간 이슈 요약 → `TELEGRAM_CHAT_ID`  
**사용처**: `news.yml`, `stock_send.yml`, `ai_issue.yml`  
```bash
python scripts/send_telegram.py --type stock --date 2026-06-09
```

---

## 5. 모니터링

### `notify_pipeline.py`
**역할**: 뉴스·주식·AI이슈 파이프라인 성공/실패 결과를 텔레그램 모니터링 채널에 알림 발송.  
**성공 시**: 채널별 핵심 지표 포함 (뉴스: 기사 수·AI 분석 건수·TOP3 이슈 / 주식: 온도계·핵심 요약 3줄 / AI이슈: period·TOP3·카테고리 통계)  
**실패 시**: 채널명 + 날짜시각 + GitHub Actions 링크  
**사용처**: 모든 워크플로우 마지막 스텝 (`if: always()`)  
**환경변수**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID_MONITOR` — 미설정 시 `sys.exit(0)` (워크플로우 영향 없음)  
```bash
python scripts/notify_pipeline.py --type news --status success --date 2026-06-13
python scripts/notify_pipeline.py --type stock --status failure
```

---

## 6. 동기화·마이그레이션

### `sync_notion.py`
**역할**: 리포트를 Notion 데이터베이스에 동기화.  
**사용처**: `news.yml`, `stock_send.yml`, `ai_issue.yml` (별도 스텝)  
```bash
python scripts/sync_notion.py --type stock --date 2026-06-09
```

### `migrate_subscribers.py`
**역할**: 기존 `RECIPIENT_EMAILS` 환경변수 이메일 목록을 Supabase `subscribers` 테이블로 일괄 삽입. **1회성 마이그레이션 스크립트**.  
```bash
python scripts/migrate_subscribers.py
```

### `migrate_json_sidecars.py`
**역할**: 구버전 `news_*.md` 파일에서 누락된 JSON 사이드카 파일을 자동 생성. **1회성 유지보수 스크립트**.  
```bash
python scripts/migrate_json_sidecars.py
```

### `init_db.py`
**역할**: `reports/*.md` → `storage/news_db.xlsx` 초기 DB 생성. **레거시 1회성 스크립트**.

---

## 7. 유지보수·분석

### `reanalyze.py`
**역할**: 기존 MD 파일 재분석. `--mode smart`(AI 분석 실패 항목만) 또는 `--mode full`(전체).  
**주의**: 이메일/텔레그램 발송 없음 (분석·저장만 수행)  
```bash
python scripts/reanalyze.py --mode smart
python scripts/reanalyze.py --mode full --from 2026-06-01
```

### `update_history.py`
**역할**: `reports/history/{ticker}.md` 파일에 일별 종가 이력 누적. 신규 종목 초기화 및 레거시 마이그레이션 자동 처리.  
**사용처**: `run_stock.py` 내부에서 자동 호출

### `validate_ai_issue_sources.py`
**역할**: AI 이슈 RSS 피드 소스 URL 유효성 검증. SSL 안정화 포함.  
**사용처**: 유지보수 시 수동 실행  
```bash
python scripts/validate_ai_issue_sources.py
```

---

## 워크플로우 → 스크립트 매핑

| GitHub Actions 워크플로우 | 실행 스크립트 |
|------------------------|------------|
| `news.yml` | `run_news.py` → `build_site.py` → `send_email.py` → `send_telegram.py` → `notify_pipeline.py` |
| `stock_build.yml` | `stock_main.py` → `build_stock_site.py` → `build_site.py` → `notify_pipeline.py` |
| `stock_send.yml` | `send_email.py --type stock` → `sync_notion.py` → `send_telegram.py --type stock` |
| `ai_issue.yml` | `run_ai_issue.py` → `build_ai_issue_site.py` → `build_site.py` → `send_email.py` → `send_telegram.py` → `notify_pipeline.py` |
| `cardnews.yml` | `build_cardnews.py` → `generate_cardnews_images.py` → `post_cardnews.py` |

---

## 로컬 실행 시 주의사항

1. **가상환경 활성화** 후 실행: `& C:\ai\.venv\Scripts\Activate.ps1`
2. **`.env` 로드**: 스크립트 내부에서 `dotenv.load_dotenv()` 자동 호출
3. **작업 디렉터리**: 반드시 `C:\ai\dailynews` 루트에서 실행
4. **Playwright**: `generate_cardnews_images.py` 실행 전 `playwright install chromium` 필요
