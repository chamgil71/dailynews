# 대규모 엔터프라이즈 확장성 및 프로덕션 고도화 지침서 (enterprise_expansion_guide.md)

본 문서는 1인/개인 개발 스케일로 구축된 본 프로젝트가 향후 **대규모 상용 프로덕션 환경 및 분산 아키텍처로 확장(Scale-up)될 때 참고해야 할 기술적 튜닝, 인프라 설계, AI 거버넌스 보완 및 마이그레이션 로드맵**을 상세히 기술합니다.

현재 로컬 개발 단계에서는 비용 및 리소스 효율성을 극대화하기 위해 인프라를 경량화(로컬 인메모리, 환경변수 파일 제어, 단일 스레드 등)하여 운영하지만, 대형 엔터프라이즈화 진입 시 본 지침서의 표준 아키텍처와 구현 모범 사례를 준수하여 점진적으로 전환합니다.

---

## 1. 1인 개발 vs 엔터프라이즈 아키텍처 비교

### 1.1 아키텍처 토폴로지 비교

```mermaid
graph TD
    subgraph "[로컬 1인 개발 아키텍처 (현 구조)]"
        UI_Local[Streamlit UI] -->|Direct/Local Call| SVC_Local[Local Services]
        SVC_Local -->|Local Env| Env_Local[.env File / Memory]
        SVC_Local -->|Direct Query| DB_Local[SQLite / ChromaDB Memory]
        SVC_Local -->|Blocking Async| LLM_Local((LLM API / Single Call))
    end

    subgraph "[엔터프라이즈 분산 프로덕션 아키텍처 (확장 구조)]"
        UI_Ent[Streamlit / React App] -->|HTTPS / API Gateway| GW[API Gateway / Load Balancer]
        GW -->|Round Robin| Workers[FastAPI Workers * N]
        
        Workers -->|Reserve/Adjust| Redis((Redis Cluster))
        Redis -->|Rate Limit / Cost Cache| Workers
        
        Workers -->|Async Queue| Rabbit[RabbitMQ / Celery Workers]
        Workers -->|Read/Write| DB_Ent[(PostgreSQL HA / Master-Slave)]
        Workers -->|Semantic Search| Vector_Ent[(pgvector / HNSW Index)]
        
        Workers -->|KMS Dynamic Decrypt| KMS[HashiCorp Vault / AWS Secrets Manager]
        Workers -->|Filtered API Call| LLM_Gateway[LLM Proxy Gateway / Presidio NER]
        LLM_Gateway -->|Semantic Eval Gate| Ragas[Ragas Eval Pipeline]
    end
```

### 1.2 아키텍처 세부 비교표

| 영역 | 로컬 1인 개발 모드 (현재) | 엔터프라이즈 프로덕션 모드 (확장) | 마이그레이션 복잡도 / 주의 사항 |
| :--- | :--- | :--- | :--- |
| **UI 및 웹 서버** | 단일 인스턴스 Streamlit 내부 실행 | Nginx / API Gateway + 컨테이너 분산 FastAPI + React UI 분리 | **상**. CORS 설정 및 세션/상태 동기화 필요. |
| **데이터베이스** | SQLite / 로컬 파일 / 단일 Vector DB 메모리 모드 | PostgreSQL HA (Master-Slave 복제) + pgvector (HNSW) | **중**. Alembic 마이그레이션 관리 및 인덱스 튜닝. |
| **비밀 정보 관리** | `.env` 로컬 환경 파일 및 하드코딩 검출 차단 | AWS Secrets Manager / HashiCorp Vault 동적 로드 | **중**. IAM 권한 및 SDK 의존성 추가 필요. |
| **비용 및 트래픽 통제** | 로컬 인메모리 변수 기반 임계값 차단 | Redis Cluster 기반 분산 ZSET Rate Limiter & 예산 차단기 | **중**. Redis 연결 타임아웃 처리 및 Fail-Closed 원칙 준수. |
| **비동기 태스크** | FastAPI 내장 `BackgroundTasks` / 단일 루프 | Celery + RabbitMQ/Redis 분산 태스크 큐 워커 | **상**. 데이터 직렬화 및 태스크 중복 실행 제어. |
| **보안 및 필터링** | 단순 정규식 기반 로컬 PII 마스킹 | Microsoft Presidio NER 모델 API 게이트웨이 파이프라인 | **중**. 지연 시간(Latency) 증가에 따른 비동기 스트리밍 설계. |
| **테스트 & 평가** | 단순 모킹(Mock) 및 1회성 API 호출 확인 | VCR.py 네트워크 격리 + Ragas 기반 CI/CD 자동 평가 분리 | **중**. 테스트 속도 유지 및 AI 평가용 데이터셋 관리. |

---

## 2. 단계적 스케일업 및 마이그레이션 로드맵

거대 프로젝트로 확장 시 한 번에 인프라를 변경하면 거대한 리스크가 수반됩니다. 3단계에 걸쳐 점진적으로 전환할 것을 권장합니다.

```
[Phase 1: 로컬 최적화 (현 단계)]
  - SQLite/ChromaDB 메모리 모드 유지
  - .env 로컬 구성 및 로컬 동기식 가드레일 적용
        │
        ▼
[Phase 2: 인프라 준중형화 (하이브리드)]
  - PostgreSQL 독립 서버 도입 (Alembic 버전 분리)
  - Redis 단일 인스턴스를 통한 비용/속도 동기화
  - KMS 연동 (AWS Secrets Manager)으로 로컬 .env 의존성 제거
        │
        ▼
[Phase 3: 완전 분산 프로덕션 (엔터프라이즈)]
  - pgvector HNSW 인덱스 활성화 (10만 건 이상 대응)
  - Celery + RabbitMQ 분산 워커 분리 (비동기 스레드 OOM 원천 방어)
  - CI/CD 파이프라인 Ragas 평가 및 Presidio 실시간 비식별화 연동
```

---

## 3. 분산 환경의 비용 및 보안 통제 고도화

### 3.1 Redis Lua 스크립트 기반 원자적 Rate Limiter (ZSET 누수 차단)
로컬 메모리 기반 `defaultdict`는 다중 웹 워커(uvicorn) 환경에서 트래픽을 합산 관리할 수 없습니다. 단순 Redis API 명령 시퀀스(`zremrangebyscore` -> `zcard` -> `zadd`)는 극도의 동시 요청에서 경쟁 상태(Race Condition)가 발생해 요청 한계를 초과하는 보안 구멍을 낳습니다. 

반드시 아래와 같이 Lua 스크립트를 적용하여 **싱글 스레드 원자성**을 보장해야 합니다.

```python
# src/core/security/rate_limiter.py
import time
import uuid
from src.database.cache_repository import CacheRepository

RATE_LIMIT_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]

-- 1. 윈도우 밖의 오래된 요청 원자적 제거
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
-- 2. 현재 윈도우 내 요청 개수 조회
local current_requests = redis.call('ZCARD', key)

-- 3. 허용 임계값과 대조 후 조건부 삽입
if current_requests < limit then
    redis.call('ZADD', key, now, member)
    redis.call('EXPIRE', key, window)
    return 1 -- 통과
else
    return 0 -- 차단
end
"""

class DistributedRateLimiter:
    def __init__(self, cache_repo: CacheRepository):
        self.cache_repo = cache_repo

    async def is_allowed(self, client_ip: str, limit: int = 100, window: int = 60) -> bool:
        redis_client = self.cache_repo.get_client()
        key = f"rate_limit:{client_ip}"
        now = time.time()
        # 동시성 정밀 분리를 위해 UUID 결합 멤버 생성
        member = f"{now}-{uuid.uuid4()}"
        
        try:
            # Redis Cluster 환경에서도 작동할 수 있도록 EVALSHA 또는 EVAL 실행
            # Lua 스크립트는 원자적으로 단일 트랜잭션 수행됨
            result = redis_client.eval(RATE_LIMIT_LUA, 1, key, now, window, limit, member)
            return bool(result)
        except Exception as e:
            # 인프라 오류 시 시스템 가용성을 위해 허용 (Fail-Open)
            logger.error(f"Rate Limiter Redis Error: {e}")
            return True
```

### 3.2 Redis 기반 분산 비용 차단기 (Cost Circuit Breaker)
다중 분산 서버리스/컨테이너 스케일링 상태에서 예산 초과(Double-Spending)를 방지하기 위해 **선점형 예산 차감(Pre-allocation) 및 사후 정산(Reconciliation)** 모델을 적용합니다.

```python
# src/core/governance/cost_breaker.py
from typing import Callable, Any
import asyncio
from src.database.cache_repository import CacheRepository

class CostCircuitBreaker:
    def __init__(self, cache_repo: CacheRepository, monthly_limit: float = 1500.0):
        self.cache_repo = cache_repo
        self.monthly_limit = monthly_limit

    def __call__(self, estimated_cost: float, fallback_func: Callable):
        def decorator(func: Callable):
            if asyncio.iscoroutinefunction(func):
                async def wrapper(*args, **kwargs):
                    # 1. 선점형 예산 차감 (Fail-Closed 원칙: Redis 장애 시 무조건 차단)
                    # reserve_budget은 Redis INCRBYFLOAT를 활용하여 누적액이 limit를 초과할지 체크 후 원자적으로 더함
                    allowed = await self.cache_repo.reserve_budget(estimated_cost, self.monthly_limit)
                    if not allowed:
                        logger.error("🚨 [Security Alert] 예산 임계치 초과 또는 캐시 장애로 비용 차단기 작동.")
                        return fallback_func(*args, **kwargs)
                    
                    try:
                        result = await func(*args, **kwargs)
                        # 2. 실제 사용된 비용 계산 및 사후 정산 (차액만큼 환불 또는 추가 차감)
                        actual_cost = result.get("usage_cost", estimated_cost)
                        diff = actual_cost - estimated_cost
                        await self.cache_repo.adjust_budget(diff)
                        return result
                    except Exception as e:
                        # 실행 오류 시 선점 비용 전액 환불
                        await self.cache_repo.adjust_budget(-estimated_cost)
                        raise e
                return wrapper
            else:
                def wrapper(*args, **kwargs):
                    allowed = self.cache_repo.reserve_budget(estimated_cost, self.monthly_limit)
                    if not allowed:
                        return fallback_func(*args, **kwargs)
                    try:
                        result = func(*args, **kwargs)
                        actual_cost = result.get("usage_cost", estimated_cost)
                        self.cache_repo.adjust_budget(actual_cost - estimated_cost)
                        return result
                    except Exception as e:
                        self.cache_repo.adjust_budget(-estimated_cost)
                        raise e
                return wrapper
        return decorator
```

---

## 4. RAG 및 UI 메모리 병목 극복 패턴 (OOM 방지)

### 4.1 Streamlit 대용량 데이터프레임 캐시 무력화 방지
*   **문제점**: Streamlit의 `@st.cache_data`는 캐시된 데이터를 무조건 메모리상에서 직렬화/역직렬화(Pickle 복사)하여 복제본을 리턴하므로, 100만 행이 넘는 대용량 주식/분석 데이터프레임을 호출하면 동시 사용자에 비례해 RAM 복사가 기하급수적으로 발생하여 즉시 **OOM(Out-Of-Memory) 크래시**가 유발됩니다.
*   **해결책**: 원본 데이터를 메모리에 들고 있지 말고, `@st.cache_resource`로 데이터베이스 커넥션만 캐싱한 후 UI 단에서 필요한 청크 데이터만 페이징으로 쿼리하여 가져옵니다.

```python
# src/web/dashboard.py (Streamlit UI 전용 계층)
import streamlit as st
from src.services.stock_service import StockService

# 데이터프레임 자체를 캐싱하지 않고, Service/Repository 커넥션 리소스만 캐싱!
@st.cache_resource
def get_stock_service():
    return StockService()

def draw_large_stock_table():
    st.title("엔터프라이즈 주식 분석 데이터 조회 (서버 사이드 페이징)")
    
    # 1. UI에서 현재 볼 페이지 번호와 크기 설정
    page = st.number_input("Page", min_value=1, value=1)
    page_size = 50
    offset = (page - 1) * page_size
    
    service = get_stock_service()
    
    # 2. 전체를 메모리에 올리는 대신, limit/offset 쿼리로 필요한 50건만 메모리 로드
    data_page = service.get_stocks_paginated(limit=page_size, offset=offset)
    total_count = service.get_total_stocks_count()
    
    st.dataframe(data_page)
    st.write(f"Total Rows: {total_count} | Page {page} of {int(total_count / page_size) + 1}")
```

### 4.2 멀티프로세싱(Spawn) 최적 분기 임계점 및 Windows 크래시 가드
*   **오버헤드 경고**: CPU 바운드 전처리를 가속화하기 위해 무분별하게 `ProcessPoolExecutor`를 소환하면, 프로세스 포크/스폰 비용 및 IPC(Inter-Process Communication) 데이터 직렬화 역직렬화 지연이 원본 연산 속도보다 길어지는 성능 역전 현상이 일어납니다.
*   **분기 기준**: 단일 루프 기준 연산 시간이 최소 **1.0초 이상**이며, 대상 데이터 개수가 **10,000건 이상**인 경우에만 멀티프로세스로 분기합니다.
*   **Windows 무한 재귀 스폰 방지**: Windows는 Unix 계열과 달리 `fork`가 없고 `spawn` 방식을 취하므로, 아래와 같은 main 진입점 가드를 두지 않으면 백그라운드 프로세스가 메인 애플리케이션을 무한 재귀로 가져와 1초 만에 CPU와 RAM이 고갈되어 터지게 됩니다.

```python
# src/services/data_processing_service.py
from concurrent.futures import ProcessPoolExecutor
import os

def heavy_calculation_unit(row_data):
    # 실제 CPU 바운드 연산 로직 (예: 복잡한 주가 수학 모델 파싱)
    return row_data * 2 # 단순 예시

class EnterpriseDataService:
    def process_large_dataset(self, dataset: list):
        # 1. 분기 임계점 체크 (데이터가 10,000건 이하이거나 로컬 디버깅 시 동기식 처리)
        if len(dataset) < 10000:
            return [heavy_calculation_unit(x) for x in dataset]
            
        # 2. 분산 병렬 연산 처리
        # CPU 코어 수의 최대 80%만 점유하여 웹 워커 고사 방지
        max_workers = max(1, int(os.cpu_count() * 0.8))
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(heavy_calculation_unit, dataset))
        return results

# [필수 규칙] 이 코드를 호출하는 메인 실행 진입점(예: 스크립트 실행, 로컬 테스트)은 
# 반드시 아래의 main 가드를 명시해야 합니다. (특히 Windows OS)
if __name__ == "__main__":
    # main 가드 없이 ProcessPoolExecutor를 띄우면 
    # 서브 프로세스가 이 파일을 다시 임포트하면서 다시 프로세스 풀을 만드는 무한 루프 크래시가 납니다.
    service = EnterpriseDataService()
    test_data = list(range(50000))
    print(service.process_large_dataset(test_data))
```

---

## 5. 엔터프라이즈 CI/CD 및 가용성 극복

### 5.1 CI/CD 환경 내의 OpenAPI 스키마 정적 샌드박스 추출
*   **문제점**: CI/CD 파이프라인에서 프론트엔드 연동용 OpenAPI JSON 스키마를 빌드 시점에 자동 추출하려고 `from src.main import app`을 실행하면, DB 연결 시도 또는 AWS KMS Secrets Manager 연결 타임아웃 등으로 인해 빌드가 멈추거나 실패하게 됩니다.
*   **해결책**: DB 드라이버 및 인프라 모듈을 임포트 시점에 동적으로 우회(Mocking)하거나 가짜 환경 변수를 주입하는 샌드박스 빌드 스크립트를 작성하여 해결합니다.

```python
# scripts/extract_openapi_sandbox.py
import os
import sys
from unittest.mock import MagicMock

# 1. 데이터베이스 커넥션 및 외부 KMS 연결 시도를 모킹하여 우회
# 실제 DB 커넥션을 맺으려는 모듈들을 더미 MagicMock으로 대체합니다.
sys.modules['src.database.connection'] = MagicMock()
sys.modules['src.core.kms'] = MagicMock()

# 2. 로컬 빌드용 더미 환경 변수 주입 (Connection Error 회피)
os.environ["DATABASE_URL"] = "postgresql://dummy:dummy@localhost:5432/dummy"
os.environ["STAGE"] = "CI"
os.environ["OPENAI_API_KEY"] = "mock-key-for-sandbox-only"

try:
    from src.main import app
    import json
    
    # 3. FastAPI 인스턴스로부터 의존성 없는 OpenAPI JSON 정적 생성
    openapi_schema = app.openapi()
    
    # output 디렉토리로 스키마 내보내기
    output_path = "storage/output/openapi.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print("✅ OpenAPI Schema successfully extracted in sandbox mode.")
    
except Exception as e:
    print(f"❌ Failed to extract openapi schema in sandbox: {e}")
    sys.exit(1)
```

### 5.2 Ragas 기반 CI/CD Eval Gate (AI 정량 평가 분리)
*   **유닛 테스트**: `vcrpy`를 활용해 LLM 호출 입출력을 캐시하고 로컬 테스트는 1초 안에 끝나도록 분리합니다.
*   **평가 파이프라인**: 50건 이상의 정량 평가셋(벤치마크)에 대해 LLM 환각(Hallucination)률 및 사실 유사도를 검증하는 작업은 CI/CD 빌드 후속 단계로 배치화하여 비동기로 구동합니다.

```python
# tests/eval/eval_rag_pipeline.py
import pytest
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance
from datasets import Dataset

def test_rag_evaluation_gate():
    # 1. 벤치마크 평가셋 로드 (문서 검색 질의, 정답 셋)
    # CI/CD 배치에서 가동되며, 실제 LLM 및 임베딩 코스모스를 호출하여 평가
    test_questions = [
        "2026년 주식 시장의 주요 금리 변동 영향은?",
        # ... 50개 이상의 다양한 벤치마크 셋
    ]
    
    # 2. 파이프라인 예측 결과 수집
    # RAG 파이프라인에서 실제 컨텍스트와 생성된 답변을 수집
    results = run_rag_pipeline_batch(test_questions)
    
    dataset = Dataset.from_dict({
        "question": test_questions,
        "contexts": [r["contexts"] for r in results],
        "answer": [r["answer"] for r in results],
        "ground_truth": [r["ground_truth"] for r in results]
    })
    
    # 3. Ragas 평가 수행 (충실도 및 답변 유사도)
    score = evaluate(dataset, metrics=[faithfulness, answer_relevance])
    
    # 4. 엔터프라이즈 품질 게이트 기준 단언 (Assertion)
    # 충실도가 85% 미만이거나 답변 유사도가 80% 미만인 경우 빌드를 강제 중단(Fail)시킴
    assert score["faithfulness"] >= 0.85, f"RAG Faithfulness drop detected: {score['faithfulness']}"
    assert score["answer_relevance"] >= 0.80, f"RAG Answer Relevance drop: {score['answer_relevance']}"
    print("✅ RAG Evaluation Gate Passed successfully.")
```

---

## 6. 다중 에이전트 협업 시 Git 병합 충돌 자동 해결 (Semantic Merge) 프로토콜

여러 서브 에이전트가 동시에 별도 브랜치에서 기능 개발을 전개하다 머지 충돌(Merge Conflict)이 발생했을 때, 에이전트가 독단으로 충돌 코드를 임의로 지우거나 프로세스를 정지시키지 않고 다음과 같은 **의미론적 충돌 병합(Semantic Merge)** 절차에 따라 안전하게 병합을 완수해야 합니다.

### 6.1 충돌 감지 및 파싱 단계
1. `git merge` 또는 `git rebase` 과정에서 충돌이 감지되면, 에이전트는 즉시 충돌 마커(`<<<<<<<`, `=======`, `>>>>>>>`)를 포함한 소스 코드를 읽어 들입니다.
2. 충돌 영역을 세 부분으로 정밀 분리합니다.
   * **HEAD (현재 브랜치)**: 내가 수정한 비즈니스 논리
   * **THEIRS (머지하려는 브랜치)**: 타 에이전트가 수정한 비즈니스 논리
   * **COMMON BASE (공통 조상)**: 원래 오리지널 소스 코드

### 6.2 의미론적 분석 및 병합 수행 규칙 (Semantic Merge Rules)

에이전트는 단순히 한쪽 코드를 덮어쓰지 않고, 아래의 의사결정 트리에 의해서만 충돌 코드를 재작성합니다.

```
                  충돌 영역 분석
                        │
         ┌──────────────┴──────────────┐
  [단순 순서 변경 및 추가]         [동일 핵심 로직의 변형]
         │                             │
         ▼                             ▼
두 변경 사항을 순차 병합          1) 두 로직의 동작 의도 교차 분석
(독립적인 두 함수 추가 등)       2) API 명세 및 DB 스키마 정합성 검사
                                 3) 두 의도를 공존시킨 통합 모듈 재구현
```

### 6.3 Semantic Merge AI 프롬프트 템플릿
에이전트가 스스로 코드를 통합하기 위해 가동하는 프롬프트 가이드라인입니다.

```markdown
당신은 Git Conflict 해결 전문 아키텍트입니다.
현재 파일에서 아래와 같은 충돌이 발생했습니다:

[충돌 소스코드 블록]
<<<<<<< HEAD
{나의 로직}
=======
{타인의 로직}
>>>>>>> branch-name

[수행 지침]
1. 두 로직이 해결하려는 비즈니스 기능적 목적을 각각 주석으로 정리하십시오.
2. 둘 중 한쪽을 날리면 기능적 결함이 유발되는가?
   - 그렇다면 두 기능이 나란히 수행되도록 논리적으로 병합한 단일 함수/클래스를 구현하십시오.
   - 변수명이 충돌하는 경우, 상위 인터페이스 설계 및 DTO를 유지하며 내부 변수명을 고유화하십시오.
3. 병합된 최종 완성본 코드를 제시하고, 충돌 마커를 완전히 제거하십시오.
```

### 6.4 사후 품질 보증 게이트 (Post-Merge Verification)
충돌 병합을 완료한 에이전트는 **즉시 아래 검증 게이트를 순차 실행**해야만 머지 승인을 요청할 수 있습니다.
1. `pylint` 또는 `eslint`와 같은 정적 분석기를 실행하여 문법 오류가 없는지 검출합니다.
2. `pytest tests/`를 구동하여, 병합 이후 기존 비즈니스 테스트 케이스가 하나도 깨지지 않았음을 입증하는 터미널 성공 로그를 확보합니다.
3. 병합 결과에 따른 변경의 영향도(Impact Scope)를 작성하여 최종 PR 본문에 첨부하고 인간 오케스트레이터의 승인을 득합니다.
