# 애플리케이션 성능 최적화 및 프로파일링 표준 (performance_optimization.md)

이 문서는 AI-PMO 성능 및 진화 거버넌스(`08_evolution.md`)를 준수하는 SQL 튜닝, 메모리 프로파일링, 적응형 멀티프로세싱 및 Streamlit OOM/누수 제어, asyncio 비동기 튜닝 모범 코드 구현 가이드이다.

---

## 1. SQL EXPLAIN 튜닝 및 인덱스 최적화 패턴

조회 쿼리 수행 시 테이블 전체 스캔(Full Scan)을 탐지하고 실행 계획을 튜닝하여 인덱스 스캔으로 전환한다.

*   **AS-IS (인덱스 부재로 인한 테이블 전체 스캔)**:
    ```sql
    EXPLAIN QUERY PLAN SELECT * FROM stock_prices WHERE ticker = 'AAPL';
    -- 결과: SCAN TABLE stock_prices (100만 건 전수 탐색으로 O(N) 성능 하락)
    ```
*   **인덱스 생성 튜닝**:
    ```sql
    CREATE INDEX idx_stock_prices_ticker ON stock_prices (ticker);
    ```
*   **TO-BE (인덱스 검색 적용 완료)**:
    ```sql
    EXPLAIN QUERY PLAN SELECT * FROM stock_prices WHERE ticker = 'AAPL';
    -- 결과: SEARCH TABLE stock_prices USING INDEX idx_stock_prices_ticker (ticker=?) (O(log N) 최적화 완료)
    ```

---

## 2. Python 메모리 누수 (Memory Leak) 프로파일링

주기적으로 메모리가 계속 증가하여 OOM을 일으키는 스트리밍/배치 작업에 대해 `tracemalloc` 스냅샷을 사용해 누수 라인을 프로파일링한다.

```python
# src/core/profiler.py
import tracemalloc

def profile_memory_leak():
    tracemalloc.start()
    # 1. 초기 스냅샷 획득
    snapshot1 = tracemalloc.take_snapshot()
    
    # 2. 프로파일링 대상 업무 처리 로직 구동
    run_heavy_batch_job()
    
    # 3. 구동 완료 후 스냅샷 비교
    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    # 메모리 사용 증가 폭 기준 상위 3개 라인 진단 출력
    print("[Top 3 Memory Allocations]")
    for stat in top_stats[:3]:
        print(stat)
```

---

## 3. CPU 연산량 기반 적응형 멀티프로세싱 & Windows OS 안전 가드

단순한 데이터 개수 기준이 아닌 1건당 예상 총 연산 시간이 **1.0초**를 초과할 때만 멀티프로세싱을 구동하되, **Windows OS 환경에서의 안전한 프로세스 생성(Spawn)을 위해 반드시 진입점 보호 가드(`if __name__ == '__main__':`)를 적용**해야 프로세스 무한 복제 크래시를 방지할 수 있습니다.

```python
# src/core/concurrency.py
from concurrent.futures import ProcessPoolExecutor
import time

def heavy_job(x):
    # 실제 CPU 연산 로직 (예: 복잡한 주식 데이터 연산)
    return x * x

def process_data_adaptive(dataset: list, max_workers: int = 4):
    if not dataset:
        return []
        
    # 1. 10건의 소량 샘플을 임의 측정하여 평균 연산 시간(avg_t) 추정
    start_time = time.perf_counter()
    for sample in dataset[:10]:
        heavy_job(sample)
    end_time = time.perf_counter()
    
    avg_t = (end_time - start_time) / min(10, len(dataset))
    total_expected_time = avg_t * len(dataset)
    
    # 2. 임계치(1.0초) 미만인 경우 싱글 스레드 직렬 루프 실행 (Spawn 비용 절감)
    if total_expected_time < 1.0:
        return [heavy_job(x) for x in dataset]
        
    # 3. 임계치 이상일 때만 ProcessPoolExecutor 병렬 풀 구동
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(heavy_job, dataset))

# 4. [중요] Windows OS 환경에서 멀티프로세스를 실행하는 진입점 모듈 표준
if __name__ == "__main__":
    # Windows 환경에서 ProcessPoolExecutor가 새 인터프리터를 기동할 때 
    # 무한 프로세스 생성 루프에 빠져 시스템이 다운되는 것을 원천 방지
    test_data = list(range(1000))
    result = process_data_adaptive(test_data)
    print("Processing completed successfully.")
```

---

## 4. Streamlit OOM 및 SQLAlchemy 커넥션 누수 방지

*   **OOM 방지**: 대형 데이터프레임을 `@st.cache_data`로 통째로 캐싱하면 메모리 복제 오버헤드로 인해 컨테이너가 급격히 종료된다. 데이터는 데이터베이스단에서 커서 기반 페이징으로 필요한 만큼만 로드한다.
*   **커넥션 누수 방지**: 핫 리로드 시 SQLAlchemy 커넥션 풀 유실을 막기 위해 `atexit.register`를 사용해 풀을 강제 회수한다.
*   **페이징 누락 방지**: OFFSET 페이징의 Page Drift 현상을 막기 위해 Cursor-based Paging을 수행한다.

```python
# src/web/streamlit_app.py
import streamlit as st
from sqlalchemy import create_engine
import atexit

@st.cache_resource
def get_database_engine():
    # pool_pre_ping으로 커넥션 생존성 확인 검사
    engine = create_engine("postgresql://...", pool_pre_ping=True)
    # Streamlit 리로드 시 커넥션 누출을 원천 방지하기 위한 강제 폐기 핸들러 등록
    atexit.register(engine.dispose)
    return engine

@st.cache_data(ttl=300)
def fetch_data_cursor(ticker: str, limit: int = 100, last_timestamp: str = None):
    # OFFSET 대신 마지막 정렬값인 last_timestamp를 조건문으로 바인딩하여 스캔 범위 단축
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

다수의 독립적 HTTP/DB 비동기 쿼리를 루프 내에서 순차적으로 `await`하여 레이턴시가 누적(AS-IS)되는 현상을 차단하고, 이벤트 루프에 동시 예약하여 응답 속도를 개선(TO-BE)한다.

```python
# src/core/async_fetcher.py
import asyncio
import httpx

async def fetch_single_url(client: httpx.AsyncClient, url: str) -> dict:
    # 명시적 타임아웃 3초 부여
    response = await client.get(url, timeout=3.0)
    return response.json()

# ❌ 비효율적 순차 await 대기 (BAD - 동기 루프와 소요 시간이 동일)
async def fetch_all_data_sequential(urls: list):
    results = []
    async with httpx.AsyncClient() as client:
        for url in urls:
            response = await client.get(url)  # 순차 대기
            results.append(response.json())
    return results

#  비동기 병렬 최적화 호출 (GOOD - 가장 느린 요청 1개의 레이턴시에 수렴)
async def fetch_all_data_concurrently(urls: list):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_single_url(client, url) for url in urls]
        # return_exceptions=True를 통해 단일 에러가 다른 정상 태스크를 차단하지 못하게 방어
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```
