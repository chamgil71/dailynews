---
description: SQL 튜닝, 메모리 프로파일링, 적응형 멀티프로세싱, Streamlit OOM/누수 제어, asyncio 비동기 튜닝의 실물 코드가 필요할 때 로드한다. `evolution` 스킬에서 참조된다.
---

# 애플리케이션 성능 최적화 및 프로파일링 표준

`evolution` 스킬이 다루는 성능 개선 작업의 실물 코드 구현 가이드다.

---

## 1. SQL EXPLAIN 튜닝 및 인덱스 최적화 패턴

* **AS-IS (인덱스 부재 → 테이블 전체 스캔)**:
```sql
EXPLAIN QUERY PLAN SELECT * FROM stock_prices WHERE ticker = 'AAPL';
-- SCAN TABLE stock_prices (100만 건 전수 탐색, O(N))
```
* **인덱스 생성**: `CREATE INDEX idx_stock_prices_ticker ON stock_prices (ticker);`
* **TO-BE**:
```sql
EXPLAIN QUERY PLAN SELECT * FROM stock_prices WHERE ticker = 'AAPL';
-- SEARCH TABLE stock_prices USING INDEX idx_stock_prices_ticker (ticker=?) (O(log N))
```

---

## 2. Python 메모리 누수 프로파일링

```python
# src/core/profiler.py
import tracemalloc

def profile_memory_leak():
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()
    run_heavy_batch_job()
    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    print("[Top 3 Memory Allocations]")
    for stat in top_stats[:3]:
        print(stat)
```

---

## 3. CPU 연산량 기반 적응형 멀티프로세싱 & Windows 안전 가드

단일 루프 기준 예상 총 연산 시간이 **1.0초**를 초과하고 데이터가 **10,000건 이상**일 때만 멀티프로세싱으로 분기한다. Windows는 `fork`가 없고 `spawn` 방식이므로 `if __name__ == "__main__":` 진입점 가드가 없으면 프로세스가 무한 재귀 복제되어 크래시한다.

```python
# src/core/concurrency.py
from concurrent.futures import ProcessPoolExecutor
import time, os

def heavy_job(x):
    return x * x

def process_data_adaptive(dataset: list, max_workers: int = 4):
    if not dataset:
        return []
    start_time = time.perf_counter()
    for sample in dataset[:10]:
        heavy_job(sample)
    end_time = time.perf_counter()
    avg_t = (end_time - start_time) / min(10, len(dataset))
    total_expected_time = avg_t * len(dataset)

    if total_expected_time < 1.0:
        return [heavy_job(x) for x in dataset]

    max_workers = max(1, int(os.cpu_count() * 0.8))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(heavy_job, dataset))

if __name__ == "__main__":
    test_data = list(range(1000))
    result = process_data_adaptive(test_data)
    print("Processing completed successfully.")
```

---

## 4. Streamlit OOM 및 SQLAlchemy 커넥션 누수 방지

* **OOM 방지**: 대형 데이터프레임을 `@st.cache_data`로 통째로 캐싱하면 메모리 복제 오버헤드로 컨테이너가 급격히 종료된다. 데이터베이스단에서 커서 기반 페이징으로 필요한 만큼만 로드한다.
* **커넥션 누수 방지**: 핫 리로드 시 커넥션 풀 유실을 막기 위해 `atexit.register`로 풀을 강제 회수한다.
* **페이징 누락 방지**: OFFSET 페이징의 Page Drift를 막기 위해 Cursor-based Paging을 수행한다.

```python
# src/web/streamlit_app.py
import streamlit as st
from sqlalchemy import create_engine
import atexit

@st.cache_resource
def get_database_engine():
    engine = create_engine("postgresql://...", pool_pre_ping=True)
    atexit.register(engine.dispose)
    return engine

@st.cache_data(ttl=300)
def fetch_data_cursor(ticker: str, limit: int = 100, last_timestamp: str = None):
    query = """
        SELECT * FROM stock_prices
        WHERE ticker = :ticker AND timestamp < :last_timestamp
        ORDER BY timestamp DESC
        LIMIT :limit
    """
    ...
```

---

## 5. asyncio.gather 비동기 병렬 I/O 최적화

```python
# src/core/async_fetcher.py
import asyncio
import httpx

async def fetch_single_url(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url, timeout=3.0)
    return response.json()

# ❌ 비효율적 순차 await (BAD)
async def fetch_all_data_sequential(urls: list):
    results = []
    async with httpx.AsyncClient() as client:
        for url in urls:
            response = await client.get(url)
            results.append(response.json())
    return results

# ✅ 비동기 병렬 최적화 (GOOD)
async def fetch_all_data_concurrently(urls: list):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_single_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```
