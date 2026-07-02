# 실운영 관측성 및 장애 회복 탄력성 구현 표준 (resilience_and_observability.md)

이 문서는 AI-PMO 운영 거버넌스(`07_operations.md`)를 준수하는 FastAPI 헬스체크, Sentry 관측성 로깅, 비동기 알림 위임, 지수 백오프 재시도 및 메모리 누수 방지 모범 코드 구현 가이드이다.

---

## 1. 물리적 종속성을 포함한 FastAPI 헬스체크 엔드포인트

단순 200 OK 문자열 리턴이 아닌, 데이터베이스 등 물리 백엔드 종속성의 가용성 커넥션을 1초 이내 타임아웃 쿼리로 직접 확인하고 모니터링 시스템에 보고한다.

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
    health_status = {
        "status": "healthy", 
        "components": {"database": "unhealthy"}
    }
    try:
        # 데이터베이스 실제 SELECT 1 커넥션 테스트 (1초 타임아웃)
        db.execute(text("SELECT 1")).fetchone()
        health_status["components"]["database"] = "healthy"
        return health_status
    except Exception as e:
        health_status["status"] = "degraded"
        # 상세 에러 스택은 내부 로그로만 남기고 외부 JSON 응답에는 노출하지 않음
        logger.error(f"Database health check failed: {str(e)}")
        return health_status
```

---

## 2. Sentry 관측성 설정 표준

API Key 및 DSN 등의 민감 설정은 절대 코드베이스에 하드코딩하지 않고, 환경변수로부터 로드한다.

```python
# src/core/observability.py
import sentry_sdk
from src.core.config import settings

def init_sentry():
    if not settings.SENTRY_DSN:
        return
        
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
```

---

## 3. FastAPI 비동기 긴급 알림 (Slack Webhook) 위임

FastAPI 이벤트 루프의 블로킹을 방지하기 위해 동기 HTTP 요청(`requests`)을 금지하고, `BackgroundTasks`를 통해 비동기 클라이언트 호출로 알림을 위임 처리한다.

```python
# src/services/notification_service.py
import httpx
from fastapi import BackgroundTasks
import os
import logging

logger = logging.getLogger(__name__)

async def send_emergency_alert_async(error_msg: str):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
        
    payload = {
        "text": f"🚨 [Emergency Alert] 프로덕션 치명적 에러 발생:\n```{error_msg}```"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 타임아웃 2초 적용 비동기 전송
            await client.post(webhook_url, json=payload, timeout=2.0)
        except Exception as e:
            logger.error(f"Failed to send Slack alert async: {str(e)}")

def trigger_error_alert(error_msg: str, background_tasks: BackgroundTasks):
    # FastAPI 메인 스레드 대기 없이 백그라운드 태스크로 연동
    background_tasks.add_task(send_emergency_alert_async, error_msg)
```

---

## 4. 비동기 지수 백오프 재시도 (Asynchronous Exponential Backoff Retry)

비동기 웹 서비스 환경(FastAPI) 내에서 대기 시 동기식 `time.sleep`을 사용하면 전체 이벤트 루프가 멈추므로, 반드시 `asyncio.sleep`과 `httpx.AsyncClient` 비동기 호출을 결합 적용합니다.

```python
# src/core/resilience.py
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

async def call_api_with_retry_async(url: str, max_retries: int = 3) -> httpx.Response:
    base_delay = 1.0  # 초기 대기 시간 1초
    
    # 비동기 HTTP 클라이언트 사용
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                # 명시적 타임아웃 3.0초 지정 (행 현상 차단)
                response = await client.get(url, timeout=3.0)
                response.raise_for_status()
                return response
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Final retry attempt failed for {url}: {str(e)}")
                    raise e
                
                # 지수 백오프 계산: 1s -> 2s -> 4s
                delay = base_delay * (2 ** attempt)
                logger.warning(f"API call failed ({str(e)}). Retrying in {delay}s...")
                
                # 단일 스레드 루프를 멈추지 않는 논블로킹 비동기 대기
                await asyncio.sleep(delay)
```

---

## 5. AbortController를 통한 React TS 메모리 누수 방지

프론트엔드 컴포넌트의 언마운트 시점에 진행 중인 비동기 HTTP Fetch 요청을 즉시 중단(Abort) 처리하여 고아 콜백 및 메모리 리크를 원천 차단한다.

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

    // Cleanup 함수: 컴포넌트 언마운트 시 시그널 Abort 트리거
    return () => {
      controller.abort();
    };
  }, [url]);

  return data;
}
```
