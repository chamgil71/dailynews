# dailynews (AI News Brief) 사양서 (spec.md)

> [!IMPORTANT]
> 본 사양서는 개발 요구사항 및 설계의 **닻(anchor)**입니다.
> 에이전트 단독으로 수정할 수 없으며, 변경 시 반드시 사용자의 사전 승인을 받아야 합니다.
> 운영·채널 구조 컨텍스트는 [`../CLAUDE.md`](../CLAUDE.md)와 [`architecture.md`](./architecture.md)를 우선 참조합니다.
> 아래 `TODO` 표시 구간은 초기 골격이며, 실제 값은 사용자 확정 후 채웁니다.

## 1. 개요 및 목적
- **비즈니스 배경**: 뉴스·주식·AI이슈 정보를 매일 수집·요약해 여러 채널로 발행하는 작업을 자동화하고자 한다.
- **해결하려는 문제**: RSS 수집 → LLM 분석 → 웹/이메일/텔레그램/SNS 발행을 서버리스(비용 $0/월 지향)로 완전 자동화한다.
- **최종 목표**: 3채널(뉴스·주식·AI이슈)을 GitHub Actions 스케줄로 무인 수집·빌드·발송하며, 크레덴셜·비용·발송 안전을 통제한다.

## 2. 세부 요구사항 및 범위
- **기능 요구사항** (README 기준 시드 — 상세화 TODO):
  - F-1: 뉴스 채널 수집·분석·발행(`news.yml`, KST 03:15)
  - F-2: 주식 채널 빌드/발송(`stock_build.yml` / `stock_send.yml`)
  - F-3: AI이슈 주간 브리핑(`ai_issue.yml`)
  - F-4: 채널 공통 발송(`core/shared/mailer.py`, `telegram.py`) + 웹 대시보드/카드뉴스
  - F-5: _TODO — 추가 기능 요구사항_
- **비기능 요구사항 (강화)**:
  - 보안: SMTP·텔레그램 토큰·LLM 키는 `.env`/GitHub Secrets로만 획득(하드코딩 금지)
  - 발송 안전: 실발송 로직 변경 시 드라이런/샌드박스 검증 후 사용자 승인 하에만 실발송
  - 비용: LLM 토큰 낭비·무한 재시도 차단, 모델/프롬프트 변경 시 비용 영향 명시
  - 관측성: 발송 성공/실패 로깅 및 실패 복구

## 3. 시스템 아키텍처 및 설계
- **데이터 흐름**: `RSS 수집` → `LLM 분석(Gemini/Claude)` → `렌더(templates/themes)` → `publish/ 배포(Vercel/Pages)` → `mailer/telegram 발송`
- **스케줄러**: `.github/workflows/*.yml` cron 기반 (임의 변경 금지)
- **환경변수 명세**: [`env_spec.md`](./env_spec.md) 참조 / 링크맵 [`link_map.md`](./link_map.md)

## 4. 검증 계획
- **테스트 시나리오**: 드라이런으로 수집·분석·렌더 파이프라인 무결성 확인(실발송 없이)
- **검증 명령**:
  ```bash
  git pull origin main
  python -m pytest tests/
  python main.py --dry-run     # 플래그는 main.py 참조
  ```
- **기대 성공 지표**: pytest 통과 + 드라이런 무오류, 실발송 0건. 합격선 _TODO_.
