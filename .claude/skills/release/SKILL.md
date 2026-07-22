---
description: 최종 출시 품질 게이트 통제 및 배포 승인 절차. 4대 릴리즈 게이트(테스트/아키텍처/보안/문서)를 점검하고 SemVer·Changelog를 확정한다. 배포는 되돌리기 어려운 행위이므로 사용자가 명시적으로 /release를 호출할 때만 실행한다.
disable-model-invocation: true
---

# 릴리즈 게이트 (Release)

프로젝트의 최종 출시 품질 게이트(Release Quality Gate) 통제 및 배포 승인을 전담한다. 배포 전 코드와 문서의 정합성을 최종 판정하며, 유의적 버전 넘버링(SemVer)을 엄격히 통제하고 변경 이력(Changelog)을 생성한다.

---

## 담당 작업 범위

```text
✅ 자율 실행 가능
  - 빌드 결과물 로그 분석 및 경고(Warning) 사항 목록화
  - SemVer 기반 다음 출시 버전 후보군 계산
  - Changelog 변경 이력 초안 컴파일

⚠️ 사용자 승인 필요
  - 스테이징 및 프로덕션 환경의 최종 배포 개시 승인
  - 주요 마이그레이션(Major Version Up) 수행 결정
  - 실패한 릴리즈 게이트 조건의 강제 통과(Bypass) 요청
```

---

## 배포 승인을 위한 4대 품질 게이트

아래 4대 게이트를 전수 점검하고, 모든 항목이 **PASS**인 경우에만 사용자에게 배포 승인을 요청한다.

| 단계 | 점검 항목 | 통과 조건 | 검사 방법 |
| :--- | :--- | :--- | :--- |
| Gate 1 | 테스트 무결성 | 전체 회귀 테스트 통과율 100% | `pytest` 또는 `npm run test` 결과 요약 |
| Gate 2 | 아키텍처 위반 | 계층 침범 0건, 순환 의존 0건 | `import-linter` 또는 `madge` 실행 |
| Gate 3 | 보안 및 라이선스 | 비밀값 검출 0건, 비허용 라이선스 0건 | `npx license-checker`, `detect-secrets` |
| Gate 4 | 문서 동기화 | `spec.md`, `worklog.md` 최종 업데이트 | 최종 커밋 해시와 스펙 문서 대조 |

## 빌드 로그 분석
```bash
npm run build 2>&1 | grep -E "dist|kB|MB|warn|error"
```
빌드 크기가 500kB를 초과하는 청크가 감지되거나 Warning이 다수 발생하면 `development` 스킬의 작업으로 되돌려 번들 스플리팅을 검토한다.

## Conventional Commits 및 파괴적 변경 이중 교차 검증(Double-Lock)
Git 커밋 메시지 접두사와 변경 파일 목록을 교차 분석해 Breaking Change가 미인지 상태로 배포되는 사고를 방어한다.
* **X.0.0 (Major)**: 커밋에 `BREAKING CHANGE:` 또는 `!` 포함. **이중 락**: 접두사가 Minor/Patch여도 변경 파일에 DB 마이그레이션(`alembic/versions/`)이나 스키마 모델(`src/models/`)이 있으면 자동으로 Major 후보로 분류하고 릴리즈를 일시 차단, 사람의 최종 승인을 거친다.
* **1.Y.0 (Minor)**: `feat` 접두사 커밋이 있고 DB 파괴적 변경이 없을 때.
* **1.0.Z (Patch)**: `fix`/`refactor`/`perf` 접두사 커밋만 있고 DB·도메인 인터페이스 변경이 없을 때.

## Changelog / 릴리즈 노트
`outputs/release-note-vX.Y.Z.md`에 승인 후 기록하며, 표준 Markdown 형식(주요 추가 기능, 버그 수정, 마이그레이션 안내)을 따른다.

---

## 완료 후 요약 형식
```json
{
  "task_completed": "릴리즈 품질 게이트 검증 및 Changelog 작성",
  "release_version": "v1.2.0",
  "gate_results": {"gate1_tests": "PASS", "gate2_architecture": "PASS", "gate3_security": "PASS", "gate4_docs": "PASS"},
  "bundle_size_check": {"max_chunk_size_kb": 320, "status": "PASS"},
  "changelog_created": true,
  "deploy_ready": true,
  "requires_approval": true
}
```

---

## 금지 사항
* 🚫 4대 품질 게이트 중 하나라도 FAILED인데 사람 승인 없이 릴리즈를 종결하는 행위 금지.
* 🚫 DB 스키마 파괴적 변경이 발생했는데 Major가 아닌 Patch 버전을 올리는 행위 금지.
* 🚫 치명적 컴파일 에러·경고 로그를 무시하고 배포 파일에 포함시키는 행위 금지.
