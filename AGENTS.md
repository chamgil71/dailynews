# AGENTS.md — dailynews (AI News Brief)

서버리스 3채널(뉴스·주식·AI이슈) AI 브리핑 자동 수집·분석·발송 시스템 (Python + LLM + Vercel + GitHub Actions). 이 문서는 이 레포에서 AI 에이전트 작업의 **최상위 진입점(SSOT)**입니다.

- **적용 프로필**: `standard` (＋아래 아웃바운드/시크릿/비용 강화) — [`agent/profiles/standard.md`](./agent/profiles/standard.md)
- **오케스트레이션**: [`agent/orchestration.md`](./agent/orchestration.md)의 라우팅·의존성·롤백 규칙을 따릅니다.
- **거버넌스 엔진**: 구현/검증 시 [`agent/knowledge/security_and_cost_governance.md`](./agent/knowledge/security_and_cost_governance.md)와 [`agent/knowledge/resilience_and_observability.md`](./agent/knowledge/resilience_and_observability.md)를 `view_file`로 읽어 적용합니다.

## 문서 우선순위 (CLAUDE.md 공존)

- 이 레포에는 운영 규칙을 담은 [`CLAUDE.md`](./CLAUDE.md)가 이미 존재합니다.
- **세션 시작 필수**: [`CLAUDE.md`](./CLAUDE.md) 지시대로 **작업 전 `git pull origin main`** 을 먼저 실행합니다(자동 빌드 커밋과 `publish/` 충돌 방지).
- **역할 분리**: `AGENTS.md`는 거버넌스 진입점, `CLAUDE.md`는 채널 구조·운영 절차 컨텍스트. 상충 시 `CLAUDE.md` 우선.

## Facts (무엇을 만드는가)

- 사양·설계의 1차 앵커는 [`docs/spec.md`](./docs/spec.md)입니다. 채널 구조·운영 절차는 [`CLAUDE.md`](./CLAUDE.md)·[`docs/architecture.md`](./docs/architecture.md)를 우선 참조합니다.
- 세션 진행 로그는 루트 [`worklog.md`](./worklog.md)에 누적합니다.

## Project Shape

- `core/shared/` — `mailer.py`(이메일), `telegram.py`(텔레그램) 등 채널 공통 발송 로직
- `api/`, `main.py`, `config/`, `themes/`, `templates/` — 수집·분석·렌더 파이프라인
- `.github/workflows/` — `news.yml`, `stock_build.yml`, `stock_send.yml`, `ai_issue.yml` 스케줄러

## Local Rules (아웃바운드/시크릿/비용 강화)

- **실발송 드라이런 의무화**: 이메일·텔레그램·SNS 등 실제 수신자에게 나가는 발송 로직을 변경할 때는, 실제 발송 API 호출 전 반드시 드라이런/샌드박스로 검증하고 **사용자 승인 후에만** 실발송 경로를 엽니다.
- **크레덴셜 하드코딩 절대 금지**: SMTP·텔레그램 토큰·LLM API 키는 `.env`/GitHub Secrets/환경변수로만 획득합니다.
- **LLM 비용 통제**: 토큰 낭비·무한 재시도 호출을 차단하고, 프롬프트/모델 변경 시 예상 비용 영향을 명시합니다.
- 스케줄러(`*.yml`) cron·발송 시각을 임의 변경하지 않습니다.

## Verification

```bash
git pull origin main
python -m pytest tests/
python main.py --dry-run     # 실발송 없이 파이프라인 검증 (플래그는 main.py 참조)
```

실행 불가 시 정확한 사유를 보고합니다.
