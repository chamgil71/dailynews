# worklog — dailynews

> AI 에이전트 세션 누적 작업 로그. 기존 이력을 삭제·덮어쓰지 않고 날짜·세션별로 **아래로 누적**합니다.
> 형식: 날짜 / 수행 성과 / 테스트·검증 결과 / 다음 계획.

---

## 2026-07-02 — 거버넌스 스캐폴드 이식
- `AGENTS.md`(SSOT 진입점) 및 `agent/` 거버넌스 엔진(orchestration·prompts·knowledge·profiles·templates) 이식.
- 적용 프로필: 레포 성격에 맞게 AGENTS.md에 선언.
- 다음 계획: 실제 개발 세션에서 프로필·오케스트레이션 규칙 적용 개시.

## 2026-07-02 — 세션 2: docs/spec.md 앵커 전개 + 실제 값 채움
- SPEC_TEMPLATE 기반 `docs/spec.md` 신규 생성, `AGENTS.md` Facts를 spec.md 1차 앵커로 연결.
- 코드 정밀 분석으로 요구사항·스키마 TODO를 **실제 값**으로 채움(파이프라인 단계·산출물·JSON 스키마·config/env).
- 남은 TODO: 성능/품질 목표치(baseline) — 사용자 결정 대기.
- 커밋·푸시 완료(origin main).

## 2026-09-29 — 세션 27: 카드뉴스 이미지 생성 중단 + SNS 텍스트 전용 발송 + 플랫폼별 실패 알림
- **원인 확인(gh 로그)**: 9/26~9/28 cardnews 실행 4회 모두 Instagram·Facebook·Telegram 성공, Threads만 토큰 만료(OAuth 190, 2026-08-10 만료). 한 플랫폼 실패로 스텝 전체 failure → 원인 없는 "파이프라인 실패" 알림 반복.
- **변경**:
  - `cardnews.yml`: job env `CARDNEWS_MODE: text` 스위치 신설 → 폰트/Playwright/카드 HTML·PNG 빌드/카드 커밋/CDN 대기 skip. 재개 시 `image`로 변경만 하면 됨. 알림 스텝에 플랫폼별 detail 전달(env 경유).
  - `scripts/post_cardnews.py`: `--mode text|image`, 핸들러별 텍스트 경로(Threads 텍스트, Facebook feed+link, Telegram 메시지, Twitter 무미디어), Instagram은 text 모드에서 skip. `run()` 분리, 기본 플랫폼은 config.
  - `core/shared/sns_source.py`(신규): 원본 발행 데이터 기반 캡션·최신 날짜. `build_cardnews.py` 중복 추출 로직 위임.
  - `core/shared/sns_report.py`(신규): 플랫폼별 결과 집계·사유 분류·GITHUB_OUTPUT 기록.
  - `scripts/notify_pipeline.py`: `--detail` 인자 + Markdown 이스케이프.
  - `config/cardnews_themes.json`: `sns.default_platforms` (text: threads,facebook / image: 기존 4개).
- **테스트·검증**: `pytest tests/test_sns_text_mode.py` 15 passed, `tests/test_stock_v6.py` 83건 통과, py_compile·YAML 파싱 OK, 3채널 캡션 dry-run(실발송 없음), 카드 data.json extra 필드 동일성 112/16/81건 불일치 0.
- **다음 계획**: Threads 토큰 재발급(전까지 매 실행 실패 알림), `post_cardnews.py` 658줄 → 플랫폼별 모듈 분리, 다음 자동 실행에서 Facebook 텍스트 게시·알림 형식 확인.

## 2026-09-29 — 세션 27(2): 주식 발송 중복 제거 + 주간 일요일 1회 + 카드뉴스 발송일 한정 + "(주간)" 표기
- **원인 확인(gh 로그)**: 주간 시황 일·월 2회 발송(9/13·14, 9/20·21, 9/27·28), 추석 연휴 9/23 리포트 3회 발송(9/24~26). `stock_send.yml` 매일 실행 + "3일 내 최신 리포트"를 보냈는지 확인 없이 선택. AI이슈는 일요일 1회로 정상.
- **변경**:
  - `scripts/select_stock_send_target.py`(신규): 일=주간/화~토=일일/월=없음, 기준일 이전만, 3일 초과 제외, 최초 커밋 시각 < 직전 정기 실행 시각이면 중복으로 건너뜀(기록 커밋 불필요). 직전 실행 미상 시 어제 날짜만.
  - `stock_send.yml`: cron `0 23 * * 1-6`(KST 화~일), actions:write, fetch-depth 0(blob:none), 발송한 경우에만 `cardnews.yml` workflow_dispatch 호출.
  - `cardnews.yml`: `Stock Briefing Send`·`Weekly Stock Build` workflow_run 트리거 제거.
  - "YYYY-MM-DD (주간)" 표기: `report_date.weekly_label()` → 주식 아카이브·주간 페이지 제목·이메일 제목·SNS 캡션, SPA `weeklyLabel()`(app.html·index.html).
  - 문서: `docs/weekly_routine_v1.md` 현행화, `docs/scripts_guide.md`, `CLAUDE.md`(흐름도·패턴 15).
- **테스트·검증**: `pytest tests/` 33 passed. 실제 9/13~9/29 이력 재현 — 일요일 주간 1회·월 없음·9/25·9/26 중복 차단. 표기 렌더링·SPA 스크립트 파싱·YAML 파싱 OK.
- **다음 계획**: 다음 stock_send 실행 로그로 직전 실행 조회·cardnews 호출 확인. 9/5 주간 리포트 누락 원인(루틴) 확인. 주간 루틴 실제 실행 시각(문서 09:00 vs 실제 15:20) 루틴 설정 확인.

## 2026-09-29 — 세션 27(3): 결정적 빌드 출력 (생성 시각 = 리포트 생성 시각)
- **문제**: 주식·AI이슈 전체 재생성 빌드가 페이지 하단 생성 시각에 빌드 시각을 넣어, 내용이 같아도 매 빌드 약 100개(주식)·20개(AI이슈) 파일이 바뀌어 커밋됨.
- **변경**: `report_date.report_generated_at()` 신설(MD 머리말 `생성일시:`/`생성:` 추출), 주식·AI이슈·뉴스 페이지/아카이브 ctx `now`와 AI이슈 data.json `updated` 적용.
- **테스트·검증**: `pytest tests/` 40 passed. 주식 99·AI이슈 18 페이지 2회 렌더 동일, 주식 커밋본 대비 차이는 생성줄·(주간) 표기뿐.
- **다음 계획**: 다음 빌드 1회 전체 커밋 후 파일 변경 수 감소 확인. MD 머리말(프론트매터) 형식 통일은 별도 작업으로 검토.

## 2026-09-29 — 세션 27(4): AI이슈 옵시디언/mywiki 연동 검토 (코드 변경 없음) + 세션 마감
- **확인**: obsi(`chamgil71/obsi`) main push → obsi `publish.yml`이 `publish: true` 노트를 mywiki에 동기화 → mywiki GitHub Pages 배포. 따라서 obsi `msshin/10-Projects/AI이슈/`에 노트만 넣으면 위키까지 자동.
- 기존 주간 노트 = 원본 MD + 프론트매터(본문 diff 0줄). 수동 등록은 07-26까지 → 08-02~09-27 9주 누락. 월간(05~07)은 Claude 재구성 보고서라 단순 합본 불가.
- **제안(결정 대기)**: ai_issue.yml에서 주간 노트 자동 push(기존 파일 덮어쓰기 금지, 실패 알림) + 9주 백필. 월간은 수동/자동 종합/초안 중 선택. 사용자 PAT(`OBSI_PUSH_TOKEN`) 등록 필요.
- **오늘 세션 전체 요약**: 카드뉴스 이미지 중단·SNS 텍스트 전환·플랫폼별 실패 알림(`2a18370c`) / 주식 발송 중복 제거·주간 일요일 1회·카드뉴스 발송일 한정·(주간) 표기(`9a6f57d6`) / 결정적 빌드 출력(`0d4e64ee`) / 머리말 통일 보류 TODO(`ba3dc52f`).
- **다음 계획**: 9/30 stock_send 로그 확인(직전 실행 조회·cardnews 호출), 10/4(일) 주간 1회·10/5(월) 미발송 확인, 옵시디언 연동 결정 후 구현, Threads 토큰 재발급.

## 2026-09-30 — 세션 28: 미완료 작업 점검 + AI이슈 옵시디언 자동 등록
- **점검(로그 확인)**: 9/30 stock_send — 직전 실행 조회 정상, 9/29 리포트 1회 발송, cardnews `workflow_dispatch` 호출 확인. text 모드 Facebook 성공·Threads 토큰 만료 알림 정상. 23:00 주식 빌드는 `reports/history/*`만 변경(결정적 빌드 확인). Facebook 토큰 유효 확인.
- **사용자 결정**: 조치 필요 항목(Threads 토큰·Vercel Supabase 키·AdSense 슬롯·Twitter/레거시 Secrets)은 기록만. 옵시디언 — 주간 자동 등록 + 누락분 백필, 월간 수동 유지, 토큰은 기존 PAT(`GH_CONTENTS_TOKEN`) 우선 사용.
- **변경**: `.github/workflows/ai_issue_obsi.yml`(AI이슈 성공 시 workflow_run + dispatch), `core/ai_issue/obsidian_export.py`, `scripts/export_obsidian_notes.py`(없는 노트만 생성·덮어쓰기 금지), `notify_pipeline.py --type obsidian`.
- **테스트·검증**: `PYTHONUTF8=1 pytest tests/` 44 passed(신규 4). 생성 노트가 수동 등록분(07-12·07-26)과 바이트 동일. 로컬 dry-run 대상 9건(08-02~09-27).
- **다음 계획**: main push 후 dispatch로 백필 실행(토큰 권한 확인). 실패하면 새 PAT를 `OBSI_PUSH_TOKEN`으로 등록 후 재실행. 10/4 자동 연동 확인.
