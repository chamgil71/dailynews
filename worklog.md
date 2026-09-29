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
