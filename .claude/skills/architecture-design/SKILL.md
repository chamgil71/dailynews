---
description: 시스템 아키텍처를 설계하거나, 레이어 구조/순환 참조/God Object 여부를 점검할 때 사용한다. "아키텍처 설계해줘", "docs/architecture.md 작성", "레이어 구조 점검" 같은 요청, 또는 요구사항 확정 직후 구현 착수 전에 반응한다.
---

# 아키텍처 설계 (Architecture)

시스템 아키텍처 수립 및 계층 격리(Layer Isolation) 보호를 책임진다. 수직 레이어 격리 구조(Router→Service→Repository→DB)와 AI 서비스 특화 수평 파이프라인(Input Guard→Context→Prompt→Output Guard→Observability)을 융합 설계하고, 모듈 간 결합도 및 순환 참조를 엄격하게 차단한다.

---

## 담당 작업 범위

```text
✅ 자율 실행 가능
  - docs/architecture.md 작성 및 아키텍처 다이어그램 설계
  - npx madge 및 import-linter를 활용한 순환 의존성 및 계층 계약 검증
  - 단일 파일/클래스의 God Object 여부 정적 진단

⚠️ 사용자 승인 필요
  - 프로젝트 신규 최상위 디렉토리 생성 및 패키지 구조 변경
  - 아키텍처 4대 레이어 격리 규칙 변경 (예: Router에서 DB 직접 조회 허용 등)
  - 웹/API 프레임워크 변경 (Streamlit → FastAPI, FastAPI → Next.js 등)
```

---

## 부트스트랩 및 아키텍처 문서화
1. **템플릿 복사 (대형 프로젝트 선택)**: 기획 단계(`docs/spec.md`)가 승인되면 [`templates/architecture.md`](../../reference/templates/architecture.md)를 `docs/architecture.md`로 복사한다. (소규모는 `docs/spec.md` 아키텍처 섹션으로 갈음)
2. **아키텍처 명세서 작성**: 레이어 관계와 물리 구조를 기록한 뒤 `docs/spec.md` 아키텍처 파트에 동기화하고 사용자 승인을 득한다.

## Shin 수직 4대 레이어 격리 스펙
```text
[요청] Router (API) ──► Service (Business) ──► Repository (Data Access) ──► Database [응답]
```
* **RAG 데이터 접근 레이어**: LLM 서비스의 RAG(검색) 동작도 Service가 벡터 DB 인프라에 직접 연결하는 것을 금지하며, 반드시 `VectorRepository` 계층을 경유한다. `VectorRepository`는 가공되지 않은 순수 도메인 객체(`List[DocumentEntity]`)만 반환하고, 프롬프트 포맷 가공은 Service Layer의 Prompt Engine이 전담한다.
* 코드 예시·안티패턴은 [`layer-patterns.md`](./layer-patterns.md)를 먼저 읽고 적용한다.

## Harness AI 수평 5대 레이어 파이프라인 (Service 내부)
AI 연동 서비스 설계 시 `Service Layer` 내부에 다음 파이프라인을 구축해 LLM의 비결정적 출력을 안정화한다.
1. **입력 가드**: 주입 공격 차단 및 입력 크기 통제
2. **컨텍스트 엔진**: 의미 청크 검색(RAG) 및 이력 슬라이딩 윈도우
3. **프롬프트 엔진**: YAML/마크다운 템플릿과 컨텍스트의 물리적 조립
4. **출력 가드**: JSON 스키마 강제, PII 필터링, 실패 시 재시도/폴백
5. **관측 레이어**: 토큰 소모, 레이턴시, API 에러 추적 메트릭 수집

## 순환 참조 및 결합도 제어 기준 (정적 검사)
* **Node.js/JS**: `npx madge --circular src`
* **Python**: 기본 순환 참조만 검출하는 pylint 대신, 레이어 임포트 규칙을 계약으로 검증하는 `import-linter`를 사용해 `router`가 `repository`를 직접 임포트하는 것을 차단한다. `lint-imports`
* **God Object 통제 수치**:
  * 단일 소스코드 파일 1,000줄 초과 금지 (복잡한 수식 연산·대형 마이그레이션 스크립트는 최대 30% 완화 버퍼인 1,300줄까지 예외 인정)
  * 단일 React 컴포넌트 500줄 및 15개 state 초과 금지 (복잡한 SVG 렌더러·일체형 대시보드는 예외)
  * 함수 길이: 권장 ≤50줄, 51~100줄은 구조적 예외 허용, 100줄 초과는 즉각 분할 대상 (God Function)
  * 체크리스트: 단일 책임(SRP) 여부 / 중첩 제어문 3단계 이하 / 순환 복잡도 10 이하 / 중복 패턴 제거 / 독립 유닛 테스트 가능 여부
