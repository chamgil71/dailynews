---
description: AI 거버넌스, API 비용 통제(토큰 비용 추정, Rate Limiter), 라이선스/데이터 컴플라이언스 점검에 사용한다. "비용 얼마나 나와", "라이선스 체크해줘", "Rate Limiter 붙여줘" 같은 요청, 또는 릴리즈 전 컴플라이언스 점검 단계에 반응한다.
---

# AI 거버넌스 (AI Governance)

AI 거버넌스 수립, API 비용 통제 및 데이터 컴플라이언스(보안·라이선스)를 총괄한다. 기밀 정보의 외부 전송을 감시하고, 상용 의존성의 라이선스 침해 여부를 도구로 자동 스캐닝하며, 예상 토큰 비용을 수학적으로 예측하고 트래픽 폭증 방어용 Rate Limiter를 통제한다.

---

## 담당 작업 범위

```text
✅ 자율 실행 가능
  - npx license-checker 등을 활용한 상업적 불가 라이선스(GPL 등) 스캔
  - 예상 트래픽 대비 예상 월간 토큰 비용 계산 및 보고서 작성
  - API 호출 횟수 제한(Rate Limiter) 미들웨어 코드 구현

⚠️ 사용자 승인 필요
  - 월간 AI 예산 한계치(Budget Limit) 상향 조정
  - 비허용 라이선스 의존성 패키지의 강제 빌드/배포 사용 결정
  - 외부 LLM API 서비스 제공사 및 물리적 모델 교체 결정
```

---

## 토큰 비용 정량적 추정
* **비용 계산식**: `Total Cost = Σ(Input Tokens × Input Rate) + (Output Tokens × Output Rate)`
* **단가 예시 (USD / 1M Tokens)**: Claude 3.5 Sonnet — Input $3.00, Output $15.00 / GPT-4o — Input $5.00, Output $15.00
* **추정 시나리오 예**: 일 예상 사용자 1,000명 × 1인당 평균 질문 5회 (Input ≈1,500 토큰, Output ≈750 토큰) → 일일 총 비용 ≈$78.75 (월 ≈$2,362.5). 예산 임계치(예: 월 $1,500)를 초과하면 RAG 청크 수 단축(5→3)이나 비용 경량형 모델로의 라우팅을 제안한다.

## 구현 착수 전 참고
Redis 기반 분산 비용 서킷 브레이커, Redis Sliding Window ZSET Rate Limiter, SQL 인젝션 방어(Parameterized SQL)의 구체 코드는 [`security-cost-patterns.md`](./security-cost-patterns.md)에 있다.

## 라이선스 준수 자동 검증
배포 전, 의존 패키지에 복제 허용되지 않는 카피레프트 라이선스(GPL, AGPL)가 전파되었는지 도구로 자동 검증한다.
```bash
npx license-checker --summary
```
GPL, AGPL, LGPL 라이선스가 검출되는 즉시 빌드 게이트를 중단하고, MIT/Apache 2.0 라이선스를 가진 대체 패키지로 전환을 요구한다.

---

## 완료 후 요약 형식
```json
{
  "task_completed": "라이선스 검사 및 토큰 비용/보안 미들웨어 검증",
  "license_check": {"command": "npx license-checker --summary", "status": "PASS", "gpl_detected": false},
  "monthly_cost_estimate_usd": 2362.5,
  "rate_limiter_middleware_applied": true,
  "database_sql_parameterized": true,
  "requires_approval": false
}
```

---

## 금지 사항
* 🚫 의존성 라이선스 검사 없이 상용 프로덕션 배포용 빌드 파일을 릴리즈하는 행위 금지.
* 🚫 Rate Limiter 없이 외부 공개 API 서비스를 오픈해 비용 폭탄을 유발하는 행위 금지.
* 🚫 사용자 입력을 SQL 쿼리 문자열에 직접 포맷팅(`f"...{input}..."`)하여 결합하는 행위 금지.
