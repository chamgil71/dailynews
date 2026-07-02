# FastAPI 모범 개발 패턴 가이드 (backend_fastapi_patterns.md)

이 가이드는 백엔드 API 설계 시 FastAPI 프레임워크의 성능을 극대화하고 결합도를 낮추기 위한 패턴들을 정의합니다.

---

## 1. Pydantic 스키마 활용 패턴
*   **API 입출력 분리**: 요청 스키마(`RequestModel`)와 응답 스키마(`ResponseModel`)는 무조건 다르게 구성하여 내부 데이터가 외부에 무분별하게 노출되는 것을 막습니다.
*   **Pydantic v2 준수**: `@field_validator` 및 `@model_validator`를 활용하여 데이터가 도달하는 Router 레벨에서 사전 비즈니스 유효성 검증(Validation)을 통과시켜야 합니다.

## 2. 의존성 주입 (Dependency Injection - Depends)
*   **느슨한 결합**: 서비스 및 레포지토리 객체 생성 시 생성자 주입 및 FastAPI의 `Depends`를 활용하여 결합도를 낮추고 테스트 시 Mocking을 용이하게 합니다.
*   **DB 세션 관리**: DB 세션은 `Depends(get_db)` 형식으로 생명주기를 통제하고, yield문을 활용하여 세션이 정상 처리 후 반드시 닫히도록(Close) 구현합니다.

## 3. 비동기 엔드포인트 (`async def` vs `def`)
*   **I/O 바운드 작업**: 데이터베이스 조회, 외부 API 호출, 파일 쓰기 등 대기 시간이 발생하는 비동기 I/O 함수는 반드시 `async def`로 정의하고 내부 연산에는 `await` 키워드를 붙여 이벤트 루프의 블로킹을 예방합니다.
*   **CPU 바운드 작업**: 복잡한 이미지 처리, 대량 데이터 계산 등의 작업은 `async def` 내부에서 동기식으로 호출하지 말고, `run_in_executor`를 활용해 별도 스레드/프로세스에서 돌려야 합니다.
