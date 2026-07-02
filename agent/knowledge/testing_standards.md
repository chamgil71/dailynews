# TDD 품질 검증 및 정량적 평가 표준 가이드 (testing_standards.md)

이 문서는 AI-PMO 품질 통제 거버넌스(`05_quality.md`)를 준수하는 비즈니스 TDD(pytest AAA) 및 비결정론적 AI 성능 검증(Semantic Assertion), 그리고 CI/CD 게이트 자동화 스크립트 구현 모범 가이드이다.

---

## 1. pytest AAA (Arrange-Act-Assert) 및 Mocking 표준

모든 비즈니스 로직 단위 테스트는 AAA 구조를 적용하고, 외부 데이터베이스나 API 등의 I/O 계층은 Mocking을 통해 완벽히 격리한다.

```python
# tests/services/test_user_service.py
import pytest
from unittest.mock import MagicMock
from src.services.user_service import UserService
from src.core.exceptions import UserNotFoundError

def test_get_user_profile_success():
    # 1. Arrange: 테스트 데이터 및 Mock Repository 설정
    mock_repo = MagicMock()
    mock_repo.fetch_by_id.return_value = {"id": 42, "name": "John Doe", "role": "member"}
    service = UserService(repo=mock_repo)
    
    # 2. Act: 비즈니스 API 실행
    result = service.get_user_by_id(42)
    
    # 3. Assert: 결과 검증 및 Mock 호출 확인
    assert result["name"] == "John Doe"
    assert result["role"] == "member"
    mock_repo.fetch_by_id.assert_called_once_with(42)
```

---

## 2. AI 비결정적 출력을 검증하는 경량 단언 (Lightweight Prompt Assertion)

로컬 개발 및 TDD 피드백 고속화를 위해, 로컬에서 무거운 AI 모델을 매번 로딩하는 대신 **핵심 키워드 포함 검사** 및 **필수 토큰 매칭 기법**을 적용하여 0.01초 이내에 의미론적 합격 여부를 판정합니다.

```python
# tests/evals/test_llm_lightweight.py
import pytest

# 1. 의미론적 핵심 키워드 매칭 헬퍼 함수
def assert_semantic_keywords(output_text: str, required_keywords: list[str]) -> None:
    """
    LLM의 출력이 비결정적이더라도, 비즈니스 목적을 달성하기 위한 
    필수 단어들이 포함되어 있는지 대소문자 구분 없이 검증합니다.
    """
    normalized_text = output_text.lower().replace(" ", "")
    for keyword in required_keywords:
        normalized_keyword = keyword.lower().replace(" ", "")
        assert normalized_keyword in normalized_text, f"Missing required factual keyword: '{keyword}'"

# 2. TDD 테스트 케이스 내에서의 고속 단언 실행
def test_llm_answer_factual_equivalence():
    # RAG 검색을 통해 반드시 전달되어야 할 팩트 단어셋 정의
    required_facts = ["공급", "수요", "가격", "변동"]
    
    # 실제 시스템을 거쳐 생성된 비결정적 LLM 출력 예시
    actual_llm_output = "주가는 주식 시장의 수요와 공급량에 따라 결정되어 움직입니다. (변동성 존재)"
    
    # 무거운 모델 로딩 없이 0.001초 이내에 팩트 정합성 검증 완료
    assert_semantic_keywords(actual_llm_output, required_facts)
```

---

## 3. CI/CD 자동화 품질 게이트 쉘 스크립트 (Quality Gate Script)

빌드 및 배포 파이프라인에서 정적 분석, 순환 참조 검사, 크레덴셜 유출 스캔을 자동 수행하고 위반 시 빌드를 거부(exit 1)한다.

```bash
#!/bin/bash
# scripts/run_audit_gate.sh
set -e

echo "=== Running Static Analysis and Security Scan ==="

# 1. detect-secrets 스캔 (entropy 기반 패스워드 탐지)
detect-secrets scan > .secrets.baseline

# baseline 내에 노출된 비밀 정보 개수가 0보다 큰지 확인
if grep -q "\"hashed_key\"" .secrets.baseline; then
    echo "🔴 Error: Hardcoded secrets detected by detect-secrets!"
    exit 1
fi

# 2. npx madge를 활용한 Node.js 순환 참조 검사 (해당 환경 시 활성)
if [ -d "node_modules" ]; then
    if npx madge --circular src | grep -q "circular"; then
        echo "🔴 Error: Circular dependencies detected in JS/TS codebase!"
        exit 1
    fi
fi

# 3. import-linter를 활용한 Python 계층 침범 정적 검사
if command -v lint-imports &> /dev/null; then
    if ! lint-imports; then
        echo "🔴 Error: Layer contract violation detected by import-linter!"
        exit 1
    fi
fi

echo "🟢 Success: All quality gates passed!"
exit 0
```
