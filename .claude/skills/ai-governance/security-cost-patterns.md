# AI 보안 가드 및 예산/트래픽 비용 통제 표준

이 문서는 [`./SKILL.md`](./SKILL.md)가 정의하는 보안·비용 거버넌스를 준수하는 Redis 분산 비용 서킷 브레이커, Redis Sliding Window ZSET Rate Limiter, SQL 인젝션 방어(Parameterized SQL) 모범 코드 구현 가이드다. 로컬 1인 개발 규모를 넘어 분산 인프라로 확장할 때 필요한 패턴이므로, 단일 프로세스 소규모 프로젝트에서는 참고만 하고 그대로 도입하지 않아도 된다.

---

## 1. Redis 기반 분산 비용 차단기 (Cost Circuit Breaker)

uvicorn 다중 워커나 분산 컨테이너 환경에서 동시 다발적 요청으로 월간 예산 한계치를 순간 초과(Double-Spending)하는 것을 막기 위해 **선점형 가예산 차감(Pre-allocation) 및 사후 정산(Reconciliation)** 방식을 적용한다.

* **Fail-Closed 원칙**: Redis 통신 장애 시 차단기가 풀려버리는(Fail-Open) 문제를 막기 위해, 예외 발생 시 호출을 원천 차단(Fail-Closed)한다.
* **레이어 격리**: 비즈니스 서비스 레이어가 인프라(Redis)에 직접 의존하지 못하도록 `CacheRepository` 인터페이스를 주입해 경유한다. (레이어 원칙은 [layer-patterns.md](../architecture-design/layer-patterns.md) 참고)

```python
# src/database/cache_repository.py
class CacheRepository:
    """분산 캐시 및 비용 관리를 위한 추상 인터페이스"""
    def reserve_budget(self, amount: float, limit: float) -> bool:
        # Redis 트랜잭션/Pipeline으로 선차감 연산 수행. 예외/한도 초과 시 즉각 False (Fail-Closed)
        pass

    def adjust_budget(self, amount: float) -> None:
        # 실제 사용 비용과 선점 비용 간 차액 정산 또는 환불
        pass
```

```python
# src/core/cost_guard.py
import asyncio
from typing import Callable
from src.database.cache_repository import CacheRepository
import logging

logger = logging.getLogger(__name__)

def cost_circuit_breaker(estimated_cost: float, cache_repo: CacheRepository, fallback_func: Callable):
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                if not cache_repo.reserve_budget(estimated_cost, limit=1500.0):
                    logger.error("Cost budget threshold exceeded or cache error (Fail-Closed).")
                    return fallback_func(*args, **kwargs)
                try:
                    result = await func(*args, **kwargs)
                    actual_cost = result.get("usage_cost", estimated_cost)
                    cache_repo.adjust_budget(actual_cost - estimated_cost)
                    return result
                except Exception as e:
                    cache_repo.adjust_budget(-estimated_cost)
                    raise e
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                if not cache_repo.reserve_budget(estimated_cost, limit=1500.0):
                    logger.error("Cost budget threshold exceeded or cache error (Fail-Closed).")
                    return fallback_func(*args, **kwargs)
                try:
                    result = func(*args, **kwargs)
                    actual_cost = result.get("usage_cost", estimated_cost)
                    cache_repo.adjust_budget(actual_cost - estimated_cost)
                    return result
                except Exception as e:
                    cache_repo.adjust_budget(-estimated_cost)
                    raise e
            return sync_wrapper
    return decorator
```

---

## 2. Redis ZSET 슬라이딩 윈도우 Rate Limiter

로컬 메모리 `defaultdict` 대신 Redis Sorted Set(ZSET) 트랜잭션을 적용해 다중 컨테이너 분산 환경에서도 동일한 API 요청 제한 상태를 안전하게 격리 통제한다.

```python
# src/web/middlewares/rate_limiter.py
from fastapi import Request, HTTPException, status
import time
import uuid

async def rate_limiter_middleware(request: Request, call_next, redis_client):
    client_ip = request.client.host
    current_time = time.time()
    redis_key = f"rate_limit:{client_ip}"
    window_seconds = 60
    max_requests = 100

    try:
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(redis_key, 0, current_time - window_seconds)
        pipe.zcard(redis_key)
        # 레이스 컨디션 방지를 위해 UUID를 결합한 유니크 멤버 값 생성
        unique_member_id = f"{current_time}-{uuid.uuid4()}"
        pipe.zadd(redis_key, {unique_member_id: current_time})
        pipe.expire(redis_key, window_seconds)
        _, request_count, _, _ = pipe.execute()

        if request_count > max_requests:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded.")
    except HTTPException:
        raise
    except Exception as e:
        # Rate Limiter 인프라 장애 시 서비스 가용성을 위해 요청을 허용(Fail-Open)
        logger.error(f"Redis rate limiter exception: {str(e)}")

    return await call_next(request)
```

---

## 3. 데이터 보안 및 Parameterized SQLi 방어 표준

사용자 입력(특히 RAG 인덱스 검색 질의)이 쿼리 문자열에 `f-string`으로 직접 바인딩되어 발생하는 SQL 인젝션을 차단하기 위해 매개변수 바인딩을 강제한다.

```python
# src/database/helpers.py
from sqlalchemy import text

# ❌ 인젝션 공격 취약 코드 (BAD)
def unsafe_get_user(username: str, db):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(text(query)).fetchall()

# ✅ 안전한 파라미터 바인딩 코드 (GOOD)
def safe_get_user(username: str, db):
    query = "SELECT * FROM users WHERE username = :username"
    return db.execute(text(query), {"username": username}).fetchall()
```

---

## 4. 코드 하드코딩·비밀값 격리 (상시 적용)

* API Key, 비밀번호, 호스트 정보 등은 `.env`에 기록하고 `os.environ` 또는 Pydantic Settings로 로드한다.
* 커밋/제출 전 비밀 키 노출 여부를 스캔한다: `grep -rn "api_key\|password\|secret_key\|jwt_secret" --include="*.py" --include="*.ts" .`
* 라이선스·비용 산정 등 대규모 운영 단계 전용 절차는 [`./SKILL.md`](./SKILL.md) 참고.
