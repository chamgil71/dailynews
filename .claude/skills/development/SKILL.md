---
description: 실제 코드 구현 단계, 특히 하드코딩 배제, API 타입 동기화, LLM 연동 파이프라인(RAG/프롬프트/가드) 개발에 사용한다. "구현해줘", "RAG 붙여줘", "프롬프트 가드 만들어줘" 같은 요청, 또는 아키텍처가 확정되고 코딩을 시작하는 단계에 반응한다.
---

# 코드 구현 (Development)

코드 구현 표준 수립, 하드코딩 배제, LLM 연동 파이프라인(RAG, Prompt, Guard) 개발을 담당한다. 가독성과 안정성이 뛰어난 클린 코드를 작성하고, API Key 등 보안값을 철저히 격리하며, 비결정적인 LLM 입출력을 제어하는 하네스 가드 코드를 구현한다.

---

## 담당 작업 범위

```text
✅ 자율 실행 가능
  - spec.md 및 아키텍처에 정의된 레이어 격리를 준수하는 비즈니스 코드 및 DB 레포지토리 구현
  - RAG 데이터 인덱싱, 청킹(Chunking) 및 임베딩 로직 작성
  - 시스템 프롬프트 조립 모듈 및 입/출력 가드 규칙 구현

⚠️ 사용자 승인 필요
  - 외부 라이브러리/패키지 추가 (requirements.txt, package.json 수정)
  - 출력 가드 최대 재시도 횟수(3회 초과) 또는 폴백(Fallback) 응답 규칙 변경
  - 보안 임계치 규정 완화 (비밀 키 검사, 프롬프트 인젝션 방어 예외 처리)
```

---

## 하드코딩 탐지 정적 검사 (Credentials 스캐닝)
* **비밀 값 격리**: API Key, 비밀번호, 호스트 정보는 `.env`에 기록하고 `os.environ` 또는 Pydantic Settings로 로드한다.
* **정적 검사**: 코드를 커밋/제출하기 전 아래로 하드코딩된 비밀 값을 스캔한다.
```bash
grep -rn "api_key\|password\|secret_key\|jwt_secret" --include="*.py" --include="*.ts" .
```
검색 결과 중 하드코딩된 문자열 상수 할당이 발견되면 즉시 환경변수로 대체한다.

## 프론트-백엔드 타입 자동 동기화 및 스키마 추출 샌드박싱
API 사양 변경 시 타입을 자동 공유하되, 빌드 시 DB 커넥션 등 인프라 로드 에러로 스펙 추출이 크래시하지 않도록 샌드박싱한다.
```bash
# 1. DB 환경변수 더미 우회 후 스키마 JSON 추출
SENTRY_DSN="dummy" DATABASE_URL="sqlite:///:memory:" python -c "import json; from src.main import app; print(json.dumps(app.openapi()))" > openapi.json

# 2. openapi-typescript로 타입 생성
npx openapi-typescript openapi.json --output src/frontend/types/api.d.ts
```

## LLM 파이프라인 개발 표준 참조
Pydantic v2 유효성 검증, 프롬프트 YAML 조립 로더, 입/출력 가드(프롬프트 인젝션 방어, PII 마스킹, 성능 사양 Fail-Safe 재시도/폴백)의 구체 코드는 [`llm-pipeline` 스킬](../llm-pipeline/SKILL.md)에 있다 — 코드 작성 전에 먼저 읽는다.

## Harness RAG 및 프롬프트 엔진 구현 표준
* **청크 크기**: 500자 (의료/법률 고위험 도메인은 200자)
* **청크 중복**: 50자 (10%)
* **임베딩 모델**: `BAAI/bge-m3` 또는 `text-embedding-3-small`

---

## 완료 후 요약 형식
```json
{
  "task_completed": "비즈니스 코드 구현 및 LLM 입출력 가드 파이프라인 통합",
  "credentials_scan": "CLEAN",
  "pydantic_validation_applied": true,
  "input_guard": {"char_limit": 4000, "injection_filter_applied": true},
  "output_guard": {"json_validation_applied": true, "max_retries": 1, "pii_masking_count": 3},
  "requires_approval": false
}
```

---

## 금지 사항
* 🚫 외부 API 키나 데이터베이스 패스워드를 코드에 하드코딩하여 커밋하는 행위 금지.
* 🚫 오류 발생 시 원시 예외 메시지나 DB 에러 스택을 가공 없이 클라이언트 화면에 출력하는 행위 금지.
* 🚫 출력 가드의 최대 재시도 횟수를 선언하지 않아 LLM API를 무제한으로 중복 호출하는 루프 생성 금지.
