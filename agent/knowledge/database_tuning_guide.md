# 데이터베이스 튜닝 및 인덱스 가이드 (database_tuning_guide.md)

이 가이드는 애플리케이션의 응답 성능의 병목이 되는 데이터베이스 계층의 쿼리 튜닝 및 인덱스 활용 규칙을 정의합니다.

---

## 1. 인덱스(Index) 설계 원칙
*   **WHERE 및 JOIN 대상 인덱싱**: 자주 조회되는 필터 조건(`WHERE column = ?`) 및 조인 대상 필드(`ON tableA.id = tableB.ref_id`)에는 반드시 인덱스를 생성하여 테이블 전체 스캔(Table Full Scan)을 방어합니다.
*   **복합 인덱스(Composite Index) 순서**: 다중 컬럼 인덱스를 만들 때는 카디널리티(Cardinality - 중복도가 낮고 유일한 값의 비율)가 높은 컬럼을 복합 인덱스의 선두 컬럼으로 배치합니다.

## 2. 쿼리 최적화 패턴
*   **N+1 쿼리 방지**: 다대일, 일대다 관계 조회 시 루프를 돌면서 하위 쿼리를 반복 호출하지 말고, ORM의 `joinedload`나 `selectinload` 혹은 명시적인 SQL `JOIN` 문을 사용하여 1회에 조인해서 가져오도록 구현합니다.
*   **페이징 필수 적용 (LIMIT & OFFSET)**: 대용량 테이블 조회 시 조건 없이 전체 리스트를 조회하지 말고, 반드시 페이징 규칙(`LIMIT`, `OFFSET` 또는 Cursor 기반 페이징)을 선언하여 메모리 과부하를 예방합니다.

## 3. 실행 계획(Explain) 분석
*   느린 쿼리가 감지되면 반드시 `EXPLAIN QUERY PLAN` (SQLite) 또는 `EXPLAIN ANALYZE` (PostgreSQL) 명령어를 터미널에서 실행하여 인덱스가 올바르게 적용되어 있는지 검증하고, 스캔 횟수를 확인합니다.
