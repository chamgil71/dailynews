Test Driven Development Spec
============================

* * *

1\. 테스트 전략
==========

테스트는 다음 구조로 작성한다.

```
tests
 ├ unit
 ├ api
 └ integration
```

* * *

2\. Unit Test
=============

service 로직 테스트

pytest 사용

예시

```
def test_calculate_return():
```

* * *

3\. API Test
============

FastAPI endpoint 테스트

```
from fastapi.testclient import TestClient
```

* * *

4\. Integration Test
====================

DB 포함 테스트

* * *

5\. 커버리지 목표
===========

최소

80%
