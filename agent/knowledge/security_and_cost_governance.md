# AI 보안 가드 및 예산/트래픽 비용 통제 표준 (security_and_cost_governance.md)

이 문서는 AI-PMO 보안 및 비용 거버넌스(`09_ai_governance.md`)를 준수하는 Redis 분산 비용 서킷 브레이커, Redis Sliding Window ZSET Rate Limiter 및 SQL 인젝션 방어 Parameterized SQL 모범 코드 구현 가이드이다.

---

## 1. Redis 기반 분산 비용 차단기 (Cost Circuit Breaker)

uvicorn 다중 워커나 분산 컨테이너 스케일링 환경에서 동시 다발적인 API 요청으로 월간 예산 한계치를 순간 초과(Double-Spending)하는 것을 차단하기 위해 **선점형 가예산 차감(Pre-allocation) 및 사후 정산(Reconciliation)** 방식을 적용한다. 

*   **Fail-Closed 원칙**: Redis 통신 장애 시 차단기가 풀려 버리는(Fail-Open) 보안 문제를 예방하기 위해, 예외 발생 시 호출을 원천 차단(Fail-Closed)한다.
*   **Shin 아키텍처 격리**: 비즈니스 서비스 레이어가 인프라(Redis)에 직접 의존하지 못하도록 `CacheRepository` 인터페이스를 주입해 경유한다.

```python
# src/database/cache_repository.py
class CacheRepository:
    """분산 캐시 및 비용 관리를 위한 추상 인터페이스"""
    def reserve_budget(self, amount: float, limit: float) -> bool:
        # Redis 트랜잭션/Pipeline을 구동해 선차감 연산 수행.
        # 예외 또는 한도 초과 시 즉각 False 반환 (Fail-Closed)
        pass

    def adjust_budget(self, amount: float) -> None:
        # 실제 사용된 토큰 비용과 선선점 비용 간의 차액 정산 또는 환불
        pass
```

```python
# src/core/cost_guard.py
import asyncio
from typing import Callable, Any
from src.database.cache_repository import CacheRepository
import logging

logger = logging.getLogger(__name__)

def cost_circuit_breaker(estimated_cost: float, cache_repo: CacheRepository, fallback_func: Callable):
    def decorator(func: Callable):
        # 대상 함수가 비동기(async)인지 동기인지 판별하여 래퍼 분기 생성
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                # 1. 선점 차감 시도
                if not cache_repo.reserve_budget(estimated_cost, limit=1500.0):
                    logger.error("Cost budget threshold exceeded or cache error (Fail-Closed).")
                    return fallback_func(*args, **kwargs)
                
                try:
                    # 2. 비동기 LLM 호출
                    result = await func(*args, **kwargs)
                    # 3. 실제 소모 비용 획득 및 차액 정산 (정산 로직 호출)
                    actual_cost = result.get("usage_cost", estimated_cost)
                    cache_repo.adjust_budget(actual_cost - estimated_cost)
                    return result
                except Exception as e:
                    # 에러 발생 시 예산을 선차감 금액만큼 환불 처리
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

메모리를 무제한 고갈시키는 로컬 메모리 `defaultdict` 대신 Redis Sorted Set(ZSET) 트랜잭션을 적용해 다중 컨테이너 분산 환경에서도 동일한 API 요청 제한 상태를 안전하게 격리 통제한다.

```python
# src/web/middlewares/rate_limiter.py
from fastapi import Request, HTTPException, status
import time
import uuid

async def rate_limiter_middleware(request: Request, call_next, redis_client):
    client_ip = request.client.host
    current_time = time.time()
    
    # IP별 ZSET 키 설계
    redis_key = f"rate_limit:{client_ip}"
    
    # 윈도우 크기: 60초, 최대 허용 요청 수: 100회
    window_seconds = 60
    max_requests = 100
    
    try:
        # Pipeline 트랜잭션으로 원자적 차단 실행
        pipe = redis_client.pipeline()
        
        # 1. 윈도우 이전의 오래된 요청 데이터 제거
        pipe.zremrangebyscore(redis_key, 0, current_time - window_seconds)
        # 2. 현재 윈도우 내의 요청 수 조회
        pipe.zcard(redis_key)
        # 3. [중요] 레이스 컨디션 방지를 위해 UUID를 결합한 유니크 멤버 값 생성
        # 단순 current_time만 넣으면 동일 밀리초에 요청이 겹칠 시 데이터가 덮어써져 누수 발생
        unique_member_id = f"{current_time}-{uuid.uuid4()}"
        pipe.zadd(redis_key, {unique_member_id: current_time})
        # 4. 키의 TTL 갱신 (지속적 침입이 멈추면 메모리 회수)
        pipe.expire(redis_key, window_seconds)
        
        # 실행 결과 추출
        _, request_count, _, _ = pipe.execute()
        
        if request_count > max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                detail="Rate limit exceeded. Please try again later."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        # Rate Limiter 인프라 장애 시 서비스 가용성을 위해 요청을 허용(Fail-Open)
        logger.error(f"Redis rate limiter exception: {str(e)}")
        
    return await call_next(request)
```

---

## 3. 데이터 보안 및 Parameterized SQLi 방어 표준

사용자 입력(특히 LLM RAG용 인덱스 검색 질의 등)이 쿼리 문자열에 포맷 문자열(`f-string`)로 직접 바인딩되어 발생하는 SQL 인젝션 공격을 차단하기 위해 매개변수 바인딩(Parameterized Query)을 강제한다.

```python
# src/database/helpers.py
from sqlalchemy import text

# ❌ 인젝션 공격 취약 코드 (BAD)
def unsafe_get_user(username: str, db):
    # 비평: 입력값이 SQL 문자열에 직접 주입되어 특수 문자로 쿼리를 조작 가능
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(text(query)).fetchall()

#  안전한 파라미터 바인딩 코드 (GOOD)
def safe_get_user(username: str, db):
    # 비평: 드라이버 레벨에서 값을 안전하게 샌티타이징하여 바인딩하므로 인젝션 방어
    query = "SELECT * FROM users WHERE username = :username"
    return db.execute(text(query), {"username": username}).fetchall()
```
