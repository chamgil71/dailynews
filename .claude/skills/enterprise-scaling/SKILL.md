---
description: 1인/개인 개발 규모 프로젝트를 대규모 상용 프로덕션·분산 아키텍처로 확장할 때 참고하는 마이그레이션 로드맵과 구현 패턴. enterprise 프로필(.claude/reference/profiles/enterprise.md)로 전환하거나 "확장", "스케일업", "분산 처리" 요청이 있을 때만 로드한다 — 로컬 1인 개발 단계에서는 불필요하다.
---

# 대규모 엔터프라이즈 확장성 및 프로덕션 고도화 지침서

본 문서는 1인/개인 개발 스케일로 구축된 프로젝트가 향후 **대규모 상용 프로덕션 환경 및 분산 아키텍처로 확장(Scale-up)될 때** 참고할 기술적 튜닝, 인프라 설계, 거버넌스 보완 및 마이그레이션 로드맵을 기술한다.

로컬 개발 단계에서는 비용·리소스 효율을 위해 인프라를 경량화(로컬 인메모리, 환경변수 파일, 단일 스레드)하지만, 엔터프라이즈화 진입 시 아래 표준 아키텍처와 구현 모범 사례를 준수해 점진적으로 전환한다.

---

## 1. 1인 개발 vs 엔터프라이즈 아키텍처 비교

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

| 영역 | 로컬 1인 개발 모드 (현재) | 엔터프라이즈 프로덕션 모드 (확장) | 마이그레이션 복잡도 |
| :--- | :--- | :--- | :--- |
| UI 및 웹 서버 | 단일 Streamlit 인스턴스 | Nginx/API Gateway + 컨테이너 분산 FastAPI + React 분리 | **상** — CORS·세션 동기화 필요 |
| 데이터베이스 | SQLite / 로컬 파일 / 단일 Vector DB 메모리 | PostgreSQL HA + pgvector(HNSW) | **중** — Alembic 마이그레이션·인덱스 튜닝 |
| 비밀 정보 관리 | `.env` 로컬 환경 파일 | AWS Secrets Manager / HashiCorp Vault 동적 로드 | **중** — IAM 권한·SDK 의존성 |
| 비용/트래픽 통제 | 로컬 인메모리 임계값 차단 | Redis Cluster 기반 분산 ZSET Rate Limiter | **중** — 타임아웃·Fail-Closed |
| 비동기 태스크 | FastAPI `BackgroundTasks` / 단일 루프 | Celery + RabbitMQ/Redis 분산 큐 | **상** — 직렬화·중복 실행 제어 |
| 보안/필터링 | 로컬 정규식 PII 마스킹 | Microsoft Presidio NER 게이트웨이 | **중** — 레이턴시 증가 대응 |
| 테스트/평가 | 단순 모킹, 1회성 확인 | VCR.py 격리 + Ragas CI/CD 자동 평가 | **중** — 속도 유지, 평가 데이터셋 관리 |

---

## 2. 단계적 스케일업 로드맵

```
[Phase 1: 로컬 최적화 (현 단계)]
  - SQLite/ChromaDB 메모리 모드, .env 로컬 구성
        │
        ▼
[Phase 2: 인프라 준중형화 (하이브리드)]
  - PostgreSQL 독립 서버 (Alembic), Redis 단일 인스턴스, KMS 연동
        │
        ▼
[Phase 3: 완전 분산 프로덕션 (엔터프라이즈)]
  - pgvector HNSW(10만 건 이상), Celery+RabbitMQ 분산 워커, CI/CD Ragas+Presidio
```

---

## 3. 분산 환경 비용·보안 통제

### 3.1 Redis Lua 스크립트 기반 원자적 Rate Limiter
로컬 메모리 `defaultdict`는 다중 워커 환경에서 트래픽을 합산 관리할 수 없다. 단순 Redis 명령 시퀀스(`zremrangebyscore`→`zcard`→`zadd`)는 동시 요청에서 레이스 컨디션이 발생하므로 **Lua 스크립트로 싱글 스레드 원자성**을 보장한다.

```python
# src/core/security/rate_limiter.py
RATE_LIMIT_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local current_requests = redis.call('ZCARD', key)
if current_requests < limit then
    redis.call('ZADD', key, now, member)
    redis.call('EXPIRE', key, window)
    return 1
else
    return 0
end
"""

class DistributedRateLimiter:
    def __init__(self, cache_repo):
        self.cache_repo = cache_repo

    async def is_allowed(self, client_ip: str, limit: int = 100, window: int = 60) -> bool:
        redis_client = self.cache_repo.get_client()
        key = f"rate_limit:{client_ip}"
        now = time.time()
        member = f"{now}-{uuid.uuid4()}"
        try:
            result = redis_client.eval(RATE_LIMIT_LUA, 1, key, now, window, limit, member)
            return bool(result)
        except Exception as e:
            logger.error(f"Rate Limiter Redis Error: {e}")
            return True  # 인프라 오류 시 가용성을 위해 Fail-Open
```

### 3.2 Redis 기반 분산 비용 차단기
다중 분산 컨테이너 스케일링 상태에서 예산 초과(Double-Spending)를 막기 위해 **선점형 예산 차감 + 사후 정산** 모델을 적용한다. 단일 프로세스용 기본 패턴은 [`security-cost-patterns.md`](../ai-governance/security-cost-patterns.md) 참고 — 여기서는 분산 환경 확장판이다.

---

## 4. RAG 및 UI 메모리 병목 극복 패턴 (OOM 방지)

### 4.1 Streamlit 대용량 데이터프레임 캐시 무력화 방지
`@st.cache_data`는 캐시 데이터를 무조건 메모리상에서 직렬화/역직렬화(Pickle 복사)해 복제본을 리턴하므로, 100만 행이 넘는 데이터프레임을 캐싱하면 동시 사용자 수에 비례해 RAM 복사가 기하급수적으로 늘어 OOM 크래시를 유발한다. `@st.cache_resource`로 DB 커넥션만 캐싱하고 필요한 청크만 페이징으로 조회한다 (상세 코드는 `performance-optimization` 스킬).

### 4.2 멀티프로세싱(Spawn) 최적 분기 임계점 및 Windows 크래시 가드
`ProcessPoolExecutor`를 무분별하게 소환하면 포크/스폰 비용과 IPC 직렬화 지연이 원본 연산보다 길어지는 성능 역전이 발생한다. 분기 기준(연산 시간 1.0초 이상, 데이터 10,000건 이상)과 Windows `if __name__ == "__main__":` 가드는 `performance-optimization` 스킬에 코드가 있다.

---

## 5. 엔터프라이즈 CI/CD 및 가용성

### 5.1 CI/CD 환경의 OpenAPI 스키마 정적 샌드박스 추출
CI 빌드 시점에 `from src.main import app`을 실행하면 DB/KMS 연결 시도로 빌드가 멈추거나 실패한다. DB 드라이버·인프라 모듈을 임포트 시점에 동적으로 모킹하거나 더미 환경변수를 주입하는 샌드박스 빌드 스크립트로 해결한다.

```python
# scripts/extract_openapi_sandbox.py
import os, sys, json
from unittest.mock import MagicMock

sys.modules['src.database.connection'] = MagicMock()
sys.modules['src.core.kms'] = MagicMock()
os.environ["DATABASE_URL"] = "postgresql://dummy:dummy@localhost:5432/dummy"
os.environ["STAGE"] = "CI"
os.environ["OPENAI_API_KEY"] = "mock-key-for-sandbox-only"

try:
    from src.main import app
    openapi_schema = app.openapi()
    output_path = "storage/output/openapi.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print("✅ OpenAPI Schema successfully extracted in sandbox mode.")
except Exception as e:
    print(f"❌ Failed to extract openapi schema in sandbox: {e}")
    sys.exit(1)
```

### 5.2 Ragas 기반 CI/CD Eval Gate
유닛 테스트는 `vcrpy`로 LLM 호출 입출력을 캐시해 1초 안에 끝나도록 분리한다. 평가 파이프라인은 50건 이상의 벤치마크셋으로 환각률·사실 유사도를 검증하는 CI/CD 후속 배치로 분리한다.

```python
# tests/eval/eval_rag_pipeline.py
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance
from datasets import Dataset

def test_rag_evaluation_gate():
    test_questions = ["..."]  # 50개 이상의 벤치마크 셋
    results = run_rag_pipeline_batch(test_questions)
    dataset = Dataset.from_dict({
        "question": test_questions,
        "contexts": [r["contexts"] for r in results],
        "answer": [r["answer"] for r in results],
        "ground_truth": [r["ground_truth"] for r in results]
    })
    score = evaluate(dataset, metrics=[faithfulness, answer_relevance])
    assert score["faithfulness"] >= 0.85
    assert score["answer_relevance"] >= 0.80
```

---

## 6. 다중 브랜치 병렬 작업 시 Git 병합 충돌 해결 (Semantic Merge)

이 프로젝트가 `.claude/agents/`의 여러 서브에이전트(예: coder + refactor)를 병렬로 돌려 여러 feature 브랜치에서 동시에 작업하는 경우, 머지 충돌을 임의로 지우거나 프로세스를 정지시키지 않고 다음 절차로 안전하게 병합한다.

1. **충돌 감지·파싱**: `<<<<<<<`/`=======`/`>>>>>>>` 마커를 읽어 HEAD(현재 브랜치)·THEIRS(머지 대상)·COMMON BASE(공통 조상) 세 부분으로 분리한다.
2. **의미론적 분석**: 단순 순서 변경/추가라면 두 변경을 순차 병합한다. 동일 핵심 로직의 변형이라면 (1) 두 로직의 의도를 교차 분석, (2) API/스키마 정합성 검사, (3) 두 의도를 공존시키는 통합 모듈로 재구현한다.
3. **판단이 불분명하면** 임의로 병합하지 않고 충돌 상태 보고서를 작성해 사람에게 즉시 알린다.
4. **사후 검증**: 병합 완료 후 정적 분석기(`pylint`/`eslint`) 실행 → `pytest tests/`로 기존 테스트가 하나도 깨지지 않았음을 확인 → 변경 영향도(Impact Scope)를 PR 본문에 첨부하고 사람의 승인을 받는다.

브랜치 격리(`feature/{역할명}`)와 커밋 접두사 컨벤션은 [`orchestration.md`](../../reference/orchestration.md) 참고.
