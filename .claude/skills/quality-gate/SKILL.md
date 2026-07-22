---
description: TDD 품질 통제, /audit 9대 영역 코드 감사, LLM 성능 정량 평가(Eval)를 수행할 때 사용한다. "테스트 작성해줘", "품질 감사해줘", "/audit", 구현이 끝나고 커밋/릴리즈 전 검증이 필요한 시점에 반응한다.
---

# 품질 게이트 (Quality)

TDD 품질 통제, `/audit` 코드 감사, LLM 성능 정량 평가(Eval)를 책임진다. 비즈니스 로직의 TDD(Arrange-Act-Assert) 무결성을 증명하고, 코드베이스 전체에 대한 9대 영역 감사로 우선순위 개선 보고서를 발행하며, AI 응답의 정확도와 환각률을 수치로 판정한다.

---

## 담당 작업 범위

```text
✅ 자율 실행 가능
  - pytest를 활용한 유닛 및 통합 테스트 코드 구현 및 실행
  - /audit 정적 분석 실행 및 docs/audit-YYYY-MM-DD.md 보고서 생성
  - 50건 이상의 LLM 평가셋(Eval Set) 구동 및 카테고리별 채점

⚠️ 사용자 승인 필요
  - 테스트 커버리지 하한선(기본 80%) 또는 Eval 합격 임계치 기준의 임의 완화
  - 실패한 회귀 테스트 케이스의 Skip 처리
  - 배포 준비(deploy_ready) 최종 판정 승인
```

---

## 부트스트랩 및 TDD 설계
1. **검증계획 작성**: 아키텍처 설계가 승인되면 [`templates/SPEC_TEMPLATE.md`](../../reference/templates/SPEC_TEMPLATE.md)의 검증계획 파트를 기준으로 `docs/spec.md` 검증계획 섹션을 작성한다. (대형 프로젝트만 별도 `docs/tdd.md` 선택)
2. **테스트 명세서 작성**: 구현할 비즈니스 단위·엔드포인트별 테스트 시나리오를 작성해 `docs/spec.md`에 반영한다.

테스트 코드 작성 전 [`testing-patterns.md`](./testing-patterns.md)의 pytest AAA 패턴과 시맨틱 단언(Semantic Assertion) 기법을 먼저 참고한다.

---

## 정량적 AI 성능 평가 (Eval)

### 평가셋 구성 비율
최소 50건(권장 200건) 이상의 고정 질문 셋, 카테고리별 비율:
* 정상 기능 케이스: 50% (25건)
* 문서에 없는 질문(환각 유도): 20% (10건)
* 임계/경계 조건(Edge Case): 16% (8건)
* 적대적 질문(인젝션 테스트): 14% (7건)

### 환경별/모델 등급별 이원화 합격 기준선
개발 환경(Local-Dev)과 프로덕션 환경(Prod-Release)의 모델 사양(Premium: Sonnet/GPT-4o vs Light: Haiku/GPT-4o-mini)에 따른 성능 편차를 고려해 임계치를 이원화한다.

**[Local-Dev / Sandbox] Light 모델군**
| 지표 | Low Risk | Medium (기본) | High (의료/금융) |
| :--- | :---: | :---: | :---: |
| 정확도 | ≥65% | ≥75% | ≥85% |
| 환각률 | ≤20% | ≤10% | ≤3% |
| JSON 준수율 | ≥80% | ≥90% | ≥95% |
| P95 지연 | ≤5초 | ≤3초 | ≤2초 |
| 카테고리별 최소 정확도 | ≥55% | ≥65% | ≥75% |

**[Prod-Release / CI/CD] Premium 모델군**
| 지표 | Low Risk | Medium (기본) | High (의료/금융) |
| :--- | :---: | :---: | :---: |
| 정확도 | ≥75% | ≥85% | ≥95% |
| 환각률 | ≤10% | ≤5% | ≤1% |
| JSON 준수율 | ≥90% | ≥95% | ≥99% |
| P95 지연 | ≤10초 | ≤5초 | ≤3초 |
| 카테고리별 최소 정확도 | ≥65% | ≥70% | ≥85% |

### LLM-as-Judge 편향 제어
1. **심판 교차**: 피평가 모델이 Claude면 심판은 GPT-4o (반대도 동일, 자기 편향 방지)
2. **길이 패널티 방지**: "Do not reward verbosity. Rate based on conciseness and factual accuracy." 명시
3. **순서 편향 방지**: 복수 답변 비교 채점 시 A/B 주입 순서를 50% 확률로 swap

---

## `/audit` 전방위 코드베이스 점검 (9대 영역)

프로젝트 전체 소스코드를 대상으로 아래 9대 영역을 자동 점검(정적 분석 + 쉘 검색 병행)하여 `docs/audit-YYYY-MM-DD.md` 보고서를 발행한다.

### 1. 보안 (Security)
* 명령어 주입: `grep -rn "exec\|spawn" --include="*.py" --include="*.ts" .`
* 경로 탈출: 사용자 제공 경로가 루트 디렉토리 내부로 제한되는지 (`resolvedPath.startswith(rootDir)`)
* XSS: `innerHTML`, `dangerouslySetInnerHTML` 이스케이프 없는 렌더링 검사
* CSS 주입: HEX 컬러 검증 정규식(`^#?[0-9A-Fa-f]{3,8}$`) 적용 여부
* 로컬스토리지: `JSON.parse(localStorage.getItem())`의 try/catch 보호 여부
* 의존성 취약점: `npm audit --json` 또는 `pip-audit`
* CORS: `Access-Control-Allow-Origin`이 와일드카드로 무분별하게 열려있는지
* 파일명 주입: Content-Disposition 헤더 내 파일명의 `encodeURIComponent` 처리 여부

### 2. 버그 & 런타임 오류
TDZ 변수 호출 순서 / import 대상 파일의 물리적 존재 확인 / async 함수의 try/catch 누락 / React ErrorBoundary 배치 / useEffect 의존성 배열 누락

### 3. 하드코딩 & 정합성
기관명·사내 IP 등 고유값의 코드 내 고정 여부 / 여러 파일에 파편화된 중복 상수 / 드롭다운 옵션 수와 백엔드 설정 항목 수 일치 / `if username == "admin"` 식 하드코딩 차단 로직 (Config `locked: true` 플래그로 대체 권장)

### 4. 성능
500줄 이상 컴포넌트의 `useMemo`/`useCallback` 부재 / 정적 이미지 WebP/AVIF 압축·`loading="lazy"` / 단일 청크 500kB 초과 여부 및 코드 스플리팅 / 300줄 이상 대형 함수

### 5. 유지보수성
`tsconfig.json`의 `strict`/`strictNullChecks` / 동일 가공 로직(`parseDate` 등)의 중복 산재 / 데드코드(미사용 파일·호출 안 하는 변수) / `.eslintrc` 존재 및 `npm run lint` 정합성 / 테스트 커버리지 및 핵심 로직 커버 여부

### 6. 접근성 (A11y)
`<div onClick>` 대신 `<button>` 및 헤더 계층 준수 / 아이콘 버튼 `aria-label`, 모달 `role="dialog"` / 탭 포커스 이동성, `outline: none` 무분별 사용 여부 / WCAG AA 색상 대비(4.5:1 이상)

### 7. 운영성 (DevOps)
GitHub Workflows 빌드/테스트 자동화 / `.env`와 `.env.example` 매핑, `.gitignore` 등록 / `package-lock.json`/`pnpm-lock.yaml` 커밋 여부 / 프로덕션 코드 내 무분별한 `console.log` 제거

### 8. 데이터 무결성
ajv/zod 등 API 스키마 가드 존재 / 디스크 쓰기 중단 대비 write-then-rename 패턴 / `JSON.parse` 예외 처리 및 순환 참조 직렬화 오류 가능성

### 9. 법적 준수 & 문서화
`npx license-checker`로 GPL 등 카피레프트 라이선스 검출 / `localStorage` 내 암호화 안 된 기밀·개인정보 / README의 설치·실행·테스트·빌드 명령어 완비 여부

CI/CD 게이트 스크립트(`run_audit_gate.sh`)와 보고서 템플릿 구조는 [`testing-patterns.md`](./testing-patterns.md) 참고.

---

## 리뷰 결과 보고 형식
코드 리뷰 피드백은 [`templates/CODE_REVIEW_TEMPLATE.json`](../../reference/templates/CODE_REVIEW_TEMPLATE.json) 규격과 정확히 일치하도록 컴파일하여 `outputs/`에 저장하고 보고한다.
