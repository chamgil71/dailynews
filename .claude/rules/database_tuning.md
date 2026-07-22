---
paths:
  - "**/migrations/**"
  - "**/models/**"
  - "**/*.sql"
  - "**/database/**/*.py"
---

# 데이터베이스 튜닝 및 인덱스 가이드

이 가이드는 애플리케이션 응답 성능의 병목이 되는 데이터베이스 계층의 쿼리 튜닝 및 인덱스 활용 규칙을 정의한다.

## 1. 인덱스(Index) 설계 원칙
* **WHERE 및 JOIN 대상 인덱싱**: 자주 조회되는 필터 조건(`WHERE column = ?`) 및 조인 대상 필드(`ON tableA.id = tableB.ref_id`)에는 반드시 인덱스를 생성하여 테이블 전체 스캔을 방어한다.
* **복합 인덱스 순서**: 다중 컬럼 인덱스는 카디널리티(중복도가 낮고 유일한 값의 비율)가 높은 컬럼을 선두 컬럼으로 배치한다.

## 2. 쿼리 최적화 패턴
* **N+1 쿼리 방지**: 관계 조회 시 루프를 돌며 하위 쿼리를 반복 호출하지 말고, ORM의 `joinedload`/`selectinload` 또는 명시적 SQL `JOIN`으로 1회에 조인해서 가져온다.
* **페이징 필수 적용**: 대용량 테이블 조회 시 조건 없이 전체 리스트를 조회하지 말고 반드시 `LIMIT`/`OFFSET` 또는 Cursor 기반 페이징을 선언한다.

## 3. 실행 계획(Explain) 분석
* 느린 쿼리가 감지되면 `EXPLAIN QUERY PLAN`(SQLite) 또는 `EXPLAIN ANALYZE`(PostgreSQL)로 인덱스 적용 여부와 스캔 횟수를 확인한다.

상세 튜닝 시나리오·프로파일링 기법은 [`.claude/skills/performance-optimization/SKILL.md`](../skills/performance-optimization/SKILL.md) 참고.
