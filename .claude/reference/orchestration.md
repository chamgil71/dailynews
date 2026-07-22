# 프로젝트 수명주기 및 단계별 절차 참고서 (.claude/reference/orchestration.md)

이 문서는 프로젝트 수명주기 전반에서 어떤 순서로 어떤 절차를 밟는지, 문서 명칭을 어떻게 통일하는지, 실패가 발생했을 때 어디로 되돌아가는지를 정의한다. Claude Code는 기본적으로 **단일 에이전트가 아래 단계들을 순차적으로** 밟아 나간다 — 각 단계의 세부 절차는 `AGENTS.md` §1에 나열된 스킬(`/strategy`, `/requirements`, ...)에 있다.

병렬·격리 작업이 필요할 때만(예: 구현과 별개로 보안 검토를 동시에 돌리고 싶을 때) `.claude/agents/{planner,coder,reviewer,refactor,security}.md`를 Agent 툴로 위임한다. 이 다섯은 Claude Code의 서브에이전트 기능으로 동작하는 실제 프로세스이며, 아래에서 설명하는 것은 그 서브에이전트를 어떻게 부르고 충돌을 어떻게 정리하는지에 대한 실무 규약이다.

---

## 0. 문서 명칭 규약 (Canonical Document Names) — SSOT

> [!IMPORTANT]
> 과거 지침의 `docs/prd.md`·`docs/tdd.md`와 프로필의 `docs/spec.md`가 혼용되던 문제를 해소하기 위해, **단일 정본(SSOT)을 `docs/spec.md`로 확정한다.**

| 정본(Canonical) | 역할 | 구(舊) 별칭 |
| :--- | :--- | :--- |
| **`docs/spec.md`** | 요구사항·설계·검증계획을 담는 단일 진실 공급원(SSOT) | `docs/prd.md`(요구사항) → spec §요구사항, `docs/tdd.md`(테스트전략) → spec §검증계획 |
| `docs/architecture.md` | 아키텍처 상세 (선택, 복잡할 때만 분리) | 변동 없음 |
| `docs/worklog.md` | 세션 이행 로그 | 루트 `worklog.md`, `work_logs.md` 등 → `docs/worklog.md`로 통일 |

별도의 `docs/prd.md`·`docs/tdd.md`를 물리 파일로 만드는 것은 대형 프로젝트에서만 선택적이며, 기본은 `docs/spec.md` 한 파일에 요구사항·검증계획 섹션을 둔다. `docs/prd.md`, `docs/tdd.md`의 서식 예시는 [`templates/prd.md`](./templates/prd.md), [`templates/tdd.md`](./templates/tdd.md)에 남아 있다 (대형 프로젝트에서 실제로 분리할 때만 사용).

---

## 1. 수명주기별 단계 순서

```text
[Phase 1. 설계/요구사항]
  /strategy (로드맵 작성) ──► /requirements (docs/spec.md 작성) ──► /architecture-design (docs/architecture.md 작성)
                                                                              │
[Phase 2. 구현 및 통합]                                                      ▼
  /development [RAG 파트] (docs/spec.md 기반 문서 인덱싱 구현) ◄─────────────┘
  /development [프롬프트 파트] (YAML 기반 프롬프트 템플릿 설계)
         │
         ▼
  /development [가드 파트] (입/출력 가드 및 PII 필터 설계) — RAG·프롬프트 완료 후에만 착수
         │
[Phase 3. 검증 및 평가]  ▼
  /quality-gate [Eval 파트] (50건 이상 평가셋 구동, 정확도/환각 측정) — 빌드가 정상 실행되는 상태에서만 착수
         │
         ▼
  /quality-gate [Regression/Audit 파트] (회귀 테스트 + /audit 9대 점검) — Eval 베이스라인 산출 이후에만 착수
         │
[Phase 4. 보안 및 배포]  ▼
  /ai-governance [보안 파트] (비밀값 스캔, SQLi 방어, 라이선스 체크)
         │
         ▼
  /release (릴리즈 게이트 최종 검사: 4대 게이트 100% 통과 시 배포 승인)
         │
[Phase 5. 실운영 통제]  ▼
  /operations (헬스체크 API 감시, Sentry 연동, Exception swallowed 차단)
  /ai-governance [비용 파트] (토큰 사용량 모니터링 및 실시간 예산 통제)
```

병렬로 진행해도 안전한 조합: `/development`의 RAG 파트와 프롬프트 파트(서로 코드 의존성 없음), `/operations`의 관측 작업과 `/ai-governance`의 비용 작업(독립된 관측 인프라). 그 외는 위 순서대로 순차 진행한다.

---

## 2. 병렬 작업 시 Git 협업 규칙

`.claude/agents/`의 서브에이전트를 여러 개 동시에 돌려 병렬 작업을 수행할 때 소스코드 레이스 컨디션과 충돌을 방지하기 위한 브랜칭 프로토콜.

1. **브랜치 격리**: `main`/`develop`에서 직접 작업하지 않는다. 반드시 `feature/{역할명}` 형식의 독립 브랜치를 생성한다.
2. **커밋 규격**: `feat(rag):`, `feat(prompt):` 등 작업한 도메인 영역을 접두사로 명시한다.
3. **머지 충돌 해결**: 충돌이 발생하면 [`.claude/skills/enterprise-scaling/SKILL.md`](../skills/enterprise-scaling/SKILL.md) §6의 Semantic Merge 절차를 따른다. 판단이 불분명하면 임의로 병합하지 말고 사람에게 즉시 보고한다.

---

## 3. 실패 처리 및 롤백 규정

후기 검증/출시 단계에서 아키텍처 결함이나 기획 상충이 발견되면, 상위 기획 문서로 피드백을 되돌리고 시스템을 일관되게 롤백한다.

1. **결함 보고**: 보안(`/ai-governance`) 또는 성능 평가(`/quality-gate`)에서 아키텍처 수준의 중대 위반이 탐지되면, 탐지 지점의 로그와 함께 `docs/spec.md`·`docs/architecture.md`에 피드백을 반영한다.
2. **문서 일관성 업데이트**: 상위 문서의 비기능 요건이나 데이터 흐름 모델을 수정하고 관련 커밋 해시를 갱신한다.
3. **순차 롤백**: 문서 수정이 사용자 승인을 받으면, 수정된 사양에 맞춰 `/development` 구현과 가드 설계를 다시 이행하고 Changelog에 롤백 사유·버전을 소급 적용한다.

| 실패 탐지 지점 | 예상 원인 | 롤백 대상 | 복구 액션 |
| :--- | :--- | :--- | :--- |
| `/quality-gate` [Eval] 정확도 미달 | RAG 검색 실패 (청크가 검색 안 됨) | Phase 2 — `docs/spec.md`, RAG 코드 | 청킹 단위를 500자→200자로 쪼개거나 중복도 조정, spec 갱신 후 재색인 |
| `/quality-gate` [Eval] 환각 발생률 초과 | 프롬프트 지시 모호 (Few-shot 부족) | Phase 2 — Prompt YAML | 도메인 특화 Few-shot 보강, 부정 프롬프트 지침 강화 |
| `/quality-gate` [Eval] 형식 파싱 에러 | 출력 가드 미작동 | Phase 2 — Output Guard 코드 | JSON 검증 함수에 재시도(최대 3회) + 폴백 분기 추가 |
| `/quality-gate` [Regression] 실패 | 부작용(Side-effect) | Phase 1/2 — `docs/architecture.md` | 순환 참조 검사, 결합도를 낮추도록 Service 레이어 재설계 |

---

## 4. 완료 보고 형식

각 스킬의 SKILL.md에는 "완료 후 요약 형식"으로 JSON 예시가 들어 있다. 이는 실제 프로세스 간 통신 프로토콜이 아니라, 세션 종료 시 사용자에게 남기는 **구조화된 요약 포맷**이다 — 무엇을 했고, 무엇이 승인 대기 중인지 한눈에 보이게 하는 것이 목적이다.
