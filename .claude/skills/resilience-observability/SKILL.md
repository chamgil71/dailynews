---
description: FastAPI 헬스체크, Sentry 관측성 로깅, 비동기 알림, 지수 백오프 재시도, React 메모리 누수 방지의 실물 코드가 필요할 때 로드한다. `operations` 스킬에서 참조된다.
---

# 실운영 관측성 및 장애 회복 탄력성 구현 표준

`operations` 스킬이 다루는 헬스체크·재시도·알림 구현의 실물 코드 가이드다.

---

## 1. 물리적 종속성을 포함한 FastAPI 헬스체크 엔드포인트

단순 200 OK가 아닌, 데이터베이스 등 물리 백엔드 종속성의 가용성을 1초 이내 타임아웃 쿼리로 직접 확인하고 모니터링 시스템에 보고한다.

```python
# src/web/health.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    health_status = {"status": "healthy", "components": {"database": "unhealthy"}}
    try:
        db.execute(text("SELECT 1")).fetchone()
        health_status["components"]["database"] = "healthy"
        return health_status
    except Exception as e:
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {str(e)}")
        return health_status
```

---

## 2. Sentry 관측성 설정 표준

API Key·DSN 등 민감 설정은 절대 코드베이스에 하드코딩하지 않고 환경변수에서 로드한다.

```python
# src/core/observability.py
import sentry_sdk
from src.core.config import settings

def init_sentry():
    if not settings.SENTRY_DSN:
        return
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0, profiles_sample_rate=1.0)
```

---

## 3. FastAPI 비동기 긴급 알림 (Slack Webhook) 위임

이벤트 루프 블로킹을 방지하기 위해 동기 HTTP 요청(`requests`)을 금지하고, `BackgroundTasks`로 비동기 클라이언트 호출을 위임 처리한다.

```python
# src/services/notification_service.py
import httpx
from fastapi import BackgroundTasks
import os, logging

logger = logging.getLogger(__name__)

async def send_emergency_alert_async(error_msg: str):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    payload = {"text": f"🚨 [Emergency Alert] 프로덕션 치명적 에러 발생:\n```{error_msg}```"}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(webhook_url, json=payload, timeout=2.0)
        except Exception as e:
            logger.error(f"Failed to send Slack alert async: {str(e)}")

def trigger_error_alert(error_msg: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_emergency_alert_async, error_msg)
```

---

## 4. 비동기 지수 백오프 재시도

비동기 서비스(FastAPI)에서 동기식 `time.sleep`을 쓰면 이벤트 루프 전체가 멈춘다. 반드시 `asyncio.sleep`과 `httpx.AsyncClient`를 결합 적용한다.

```python
# src/core/resilience.py
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

async def call_api_with_retry_async(url: str, max_retries: int = 3) -> httpx.Response:
    base_delay = 1.0
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.get(url, timeout=3.0)
                response.raise_for_status()
                return response
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Final retry attempt failed for {url}: {str(e)}")
                    raise e
                delay = base_delay * (2 ** attempt)
                logger.warning(f"API call failed ({str(e)}). Retrying in {delay}s...")
                await asyncio.sleep(delay)
```

---

## 5. AbortController를 통한 React TS 메모리 누수 방지

컴포넌트 언마운트 시 진행 중인 비동기 Fetch 요청을 즉시 중단(Abort)하여 고아 콜백과 메모리 리크를 차단한다.

```typescript
// src/frontend/hooks/useFetchStocks.ts
import { useEffect, useState } from "react";

export function useFetchStocks(url: string) {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    async function fetchData() {
      try {
        const response = await fetch(url, { signal });
        const json = await response.json();
        setData(json);
      } catch (error: any) {
        if (error.name === "AbortError") {
          console.log("Fetch aborted successfully.");
        } else {
          console.error("Fetch error:", error);
        }
      }
    }
    fetchData();

    return () => {
      controller.abort();
    };
  }, [url]);

  return data;
}
```
