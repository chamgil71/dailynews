# AI 거버넌스 마스터 오케스트레이션 지침서 (agent/orchestration.md)

본 문서는 프로젝트 수명주기 전반에서 복수의 전문 에이전트들(01_strategy ~ 09_ai_governance)이 상호작용하는 **실행 순서, 병렬 협업 조합, 필수 의존성, 실패 시 롤백 프로세스 및 범용 통신 규격**을 정의한다. 오케스트레이터(마스터 에이전트)는 본 지침에 따라 하위 에이전트를 소환하고 위임한다.

---

## 0. 문서 명칭 규약 (Canonical Document Names) — SSOT

> [!IMPORTANT]
> 과거 지침의 `docs/prd.md`·`docs/tdd.md` 와 프로필의 `docs/spec.md` 가 혼용되던 문제를 해소하기 위해, **단일 정본(SSOT)을 `docs/spec.md` 로 확정한다.** 본 문서·프롬프트·프로필의 모든 참조는 아래 매핑을 따른다.

| 정본(Canonical) | 역할 | 구(舊) 별칭 |
| :--- | :--- | :--- |
| **`docs/spec.md`** | 요구사항·설계·검증계획을 담는 **단일 진실 공급원(SSOT)** | `docs/prd.md`(요구사항) → spec §요구사항, `docs/tdd.md`(테스트전략) → spec §검증계획 |
| `docs/architecture.md` | 아키텍처 상세(선택, 복잡 시 분리) | 변동 없음 |
| `docs/worklog.md` | 세션 이행 로그 | 루트 `worklog.md`·`work_logs.md` 등 → `docs/worklog.md` 로 통일 |

- 별도의 `docs/prd.md`·`docs/tdd.md` 를 물리 파일로 생성하는 것은 **대형 프로젝트에서만 선택적**이며, 기본은 `docs/spec.md` 한 파일에 요구사항·검증계획 섹션을 둔다.
- 본 문서 이하에서 "`docs/spec.md`" 로 표기된 모든 지점은 이 정본을 가리킨다.

---

## 1. 수명주기별 에이전트 오케스트레이션 시퀀스

에이전트는 기획부터 운영까지 다음 흐름에 맞춰 작업을 수행하고 문서를 동기화한다.

```text
[Phase 1. 설계/요구사항]
  오케스트레이터 ──► 01_strategy (로드맵 작성) ──► 02_requirements (docs/spec.md 작성) ──► 03_architecture (docs/architecture.md 작성)
                                                                                                      │
[Phase 2. 구현 및 통합]                                                                               ▼
  오케스트레이터 ──┬─ 04_development [RAG 파트] (docs/spec.md 기반 문서 인덱싱 구현) ◄──────────────────┘
                  └─ 04_development [프롬프트 파트] (YAML 기반 프롬프트 템플릿 설계)
                         │
                         ▼
                  04_development [가드 파트] (입/출력 가드 및 PII 필터 설계)
                         │
[Phase 3. 검증 및 평가]   ▼
  오케스트레이터 ──► 05_quality [Eval 파트] (50건 이상 평가셋 구동 및 정확도/환각 측정)
                         │
                         ▼
                  05_quality [Regression/Audit 파트] (전체 회귀 테스트 실행 & /audit 9대 점검 보고서)
                         │
[Phase 4. 보안 및 배포]   ▼
  오케스트레이터 ──► 09_ai_governance [보안 파트] (비밀값 스캔, SQLi 방어, 라이선스 체크)
                         │
                         ▼
                  06_release (릴리즈 게이트 최종 검사: 100% 통과 시 배포 승인)
                         │
[Phase 5. 실운영 통제]   ▼
  오케스트레이터 ──┬─ 07_operations (헬스체크 API 감시, Sentry 연동, Exception swallowed 차단)
                  └─ 09_ai_governance [비용 파트] (토큰 사용량 모니터링 및 실시간 예산 통제)
```

---

## 2. 병렬 실행 조합 및 의존성 규칙

오버헤드(지연 시간 및 토큰 비용)를 최소화하기 위해 독립적인 태스크는 병렬 실행하되, 데이터 정합성을 위해 의존성 선행 조건을 강제한다.

### 2.1 병렬 실행 가능 조합 (Concurrent Execution)
*   **조합 A (구현 단계)**: `04_development [RAG]`와 `04_development [프롬프트]`
    *   *이유*: RAG 임베딩/청킹 파이프라인 구축과 시스템 프롬프트 YAML 조립은 상호 간의 코드 의존성이 없으므로 동시 개발이 가능하다.
*   **조합 B (운영 단계)**: `07_operations [관측]`과 `09_ai_governance [비용]`
    *   *이유*: 헬스체크 및 에러 로깅 모니터링과 API 비용 추적은 독립된 관측 인프라에서 병렬 수집된다.

### 2.2 순차 실행 필수 의존성 (Strict Sequential Dependencies)
*   **의존성 Rule 1 (가드 설계 선행)**:
    *   `04_development [가드]`는 RAG 및 프롬프트 로직이 완료된 후에만 실행한다.
*   **의존성 Rule 2 (품질 검증 선행)**:
    *   `05_quality [Eval]`은 RAG, 프롬프트, 가드 컴포넌트가 모두 소스코드에 통합 완료되어 빌드가 정상 실행되는 상태여야만 구동한다.
*   **의존성 Rule 3 (회귀 분석 선행)**:
    *   `05_quality [Regression]`은 `05_quality [Eval]`의 성능 벤치마크 점수(정확도 등 Baseline)가 산출된 이후에만 회귀 비교가 가능하다.

### 2.3 에이전트 간 호출 권한 계층 및 통제 규칙 (Authority & Causality)
*   **원칙 (Peer-to-Peer 호출 전면 금지)**: 개별 에이전트가 오케스트레이터의 위임 없이 다른 하위 에이전트를 직접 소환하거나 실행 권한을 위임하는 행위(P2P Call)를 엄격히 차단한다. P2P 호출 허용 시, 임의적인 아키텍처/코드 변경으로 인해 호출 인과관계의 무한 루프(Deadlock) 및 버전 충돌이 발생한다.
*   **단방향 권한 계층 (Authority Hierarchy)**: 모든 에이전트는 오직 오케스트레이터(Orchestrator)의 위임 요청에 의해서만 실행 권한(Lock)을 획득한다.
    *   *오케스트레이터* $\rightarrow$ *개별 서브에이전트* (실행 명령 및 Context 전송)
    *   *서브에이전트* $\rightarrow$ *오케스트레이터* (성공/실패 데이터 응답 회신)
*   **예외 에스컬레이션 경로 (Escalation Path)**:
    *   구현 단계(`04_development`)에서 아키텍처 타당성이 충돌하거나, 운영 단계(`07_operations`)에서 치명적 예외가 발생할 경우, 서브에이전트는 독단으로 타 에이전트를 직접 호출하여 문제를 수정하려 하지 말고, 오케스트레이터에게 즉시 예외 상태를 회신하고 실행 권한을 반납(Escalation)한다.
    *   오케스트레이터는 수신된 에스컬레이션 로그를 기반으로 `4. 실패 처리 롤백 규정`에 따라 상위 단계로의 롤백 및 동기화 루프를 재가동한다.

---

## 3. 병렬 작업 시 Git 협업 및 충돌 방지 규칙
복수의 에이전트가 병렬 작업을 수행할 때 소스코드의 레이스 컨디션 및 충돌을 방지하기 위해 다음 Git 브랜칭 프로토콜을 필수로 강제한다.
1.  **브랜치 격리**: 병렬 가동되는 에이전트는 절대 `main` 또는 `develop` 브랜치에서 직접 작업하지 않는다. 반드시 `feature/pmo-agent-{역할명}` 형식의 독립 브랜치를 생성하여 작업한다.
2.  **커밋 규격**: `feat(rag):`, `feat(prompt):` 등 작업한 도메인 영역을 접두사로 명시하여 커밋한다.
3.  **자율적 Git 머지 충돌(Merge Conflict) 해결 프로토콜**:
    *   오케스트레이터가 feature 브랜치를 상위 브랜치(develop 등)에 머지하려 할 때, 충돌이 발생하면 다음 순서로 자율 해결한다.
    *   *1단계*: 충돌 마커(`<<<<<<< HEAD`, `=======`, `>>>>>>>`)가 표시된 파일들을 정적 리서치하여 충돌 코드블록의 문맥과 로직을 분리한다.
    *   *2단계*: RAG 모듈과 프롬프트 모듈 등 기능적 충돌인 경우, 두 모듈의 독립성을 유지하는 방향으로 팩토리 패턴이나 신규 헬퍼 함수를 신설하여 코드를 통합한다.
    *   *3단계*: 판단이 불분명하여 비즈니스 로직 붕괴가 의심될 경우, 임의로 머지하지 않고 충돌 상태의 보고서를 작성하여 사람에게 즉시 예외 알림을 보낸다.

---

## 4. 실패 처리 및 상향식 피드백(Back-propagation) 롤백 규정

후기 검증/출시 단계에서 심각한 아키텍처 결함이나 기획 상충이 발견되면, 다음 룰셋에 따라 상위 기획 문서로 피드백을 역전파하고 시스템을 일관되게 롤백한다.

1.  **결함 보고 및 역전파**:
    *   보안(`09_ai_governance`) 또는 성능 평가(`05_quality`)에서 아키텍처 수준의 중대 위반이 탐지되면, 오케스트레이터는 탐지 지점의 예외 로그와 함께 상위 `docs/spec.md` 및 `docs/architecture.md`로 피드백 문서를 전송한다.
2.  **문서 일관성 업데이트**:
    *   에이전트는 상위 문서의 성능 사양서(비기능 요건 완화 등) 또는 데이터 흐름 모델을 수정 및 업데이트하고, 해당 커밋 해시를 갱신한다.
3.  **순차 롤백 배포**:
    *   상위 문서 수정 승인 완료 후, 수정된 사양에 맞추어 하위 코드 구현(`04_development`) 및 가드 설계를 다시 이행하며, 기존 변경 로그(Changelog)에 롤백 사유와 버전을 소급 적용한다.

| 실패 탐지 지점 | 예상 원인 계층 | 롤백 대상 단계 및 문서 | 복구 액션 가이드라인 |
| :--- | :--- | :--- | :--- |
| **05_quality [Eval]**<br>정확도 미달 | **RAG 검색 실패** (청크가 검색 안 됨) | Phase 2로 롤백<br>`docs/spec.md`, RAG 코드 | 청킹 단위를 500자에서 200자로 쪼개거나 중복도를 조정하고, `docs/spec.md`의 명세를 갱신한 뒤 재색인한다. |
| **05_quality [Eval]**<br>환각 발생률 초과 | **프롬프트 지시 모호** (Few-shot 부족) | Phase 2로 롤백<br>Prompt YAML 파일 | 프롬프트 내에 도메인 특화 Few-shot 예시를 보강하고 부정 프롬프트(Negative Prompt) 지침을 강화한다. |
| **05_quality [Eval]**<br>형식 파싱 에러 | **출력 가드 미작동** | Phase 2로 롤백<br>Output Guard 코드 | JSON 구조 검증 함수에 자동 재시도(최대 3회) 및 폴백(Fallback) 반환 분기를 수정 구현한다. |
| **05_quality [Regression]**<br>회귀 테스트 실패 | **부작용(Side-effect)** | Phase 1/2로 롤백<br>`docs/architecture.md` | `pylint`로 순환 참조 여부를 검사하고, 결합도를 낮추기 위해 Service 레이어를 재설계한다. |

---

## 5. 범용 에이전트 간 통신 프로토콜 (Message Schema)

오케스트레이터가 서브에이전트에게 작업을 위임하고 회신받을 때, AI 간 컨텍스트 유실을 예방하기 위해 아래의 JSON 스키마 규격을 전송 및 응답 프로토콜로 사용한다.

### 5.1 에이전트 호출 메시지 (Request)
```json
{
  "sender": "orchestrator",
  "target_agent": "05_quality",
  "phase": "Phase 3. 검증",
  "action": "RUN_EVALUATION",
  "inputs": {
    "project_path": "./",
    "eval_set_path": "./tests/eval_set.json",
    "target_baseline": 0.85
  },
  "instructions": "RAG 파이프라인의 변경이 발생했으므로, 50건의 평가셋을 구동하여 정확도를 측정하고, docs/spec.md의 조건과 대조하십시오."
}
```

### 5.2 에이전트 응답 메시지 (Response)
```json
{
  "sender": "05_quality",
  "task_completed": "평가셋 구동 및 회귀 검증",
  "status": "SUCCESS | FAILED",
  "metrics": {
    "total_cases": 50,
    "accuracy": 0.88,
    "hallucination_rate": 0.02,
    "format_compliance": 1.0,
    "deploy_ready": true
  },
  "requires_approval": true,
  "approval_items": [
    "deploy_ready: true - 최종 릴리즈 게이트 진입을 위해 사용자 승인 필요"
  ],
  "failure_reason": {
    "layer": "RAG | PROMPT | GUARD | NONE",
    "description": "실패 사유 서술"
  }
}
```
