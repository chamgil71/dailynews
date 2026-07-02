# architecture.md

## 1. 문서 목적

이 문서는 프로젝트의 **전체 시스템 구조(System Architecture)** 를 정의한다.
AI 코딩 환경에서 다음 목적을 가진다.

* 시스템 전체 구성 요소 명확화
* 백엔드 / 프론트엔드 / 데이터 계층 구조 정의
* AI 코드 생성 시 **구조적 일관성 유지**
* 개발 및 리팩토링 기준 제공

이 문서는 다음 문서들과 함께 사용된다.

* `docs/prd.md` → 제품 요구사항
* `docs/tdd.md` → 테스트 전략
* `ai/base_guideline.md` → AI 코딩 원칙
* `ai/rules/*.md` → 기술별 구현 규칙
* `ai/skills/*.md` → AI 작업 단위 스킬

---

# 2. 시스템 전체 구조

본 프로젝트는 **Layered Architecture + Service Architecture** 기반으로 설계된다.

```
User
  │
  ▼
Frontend Layer
  │
  ▼
API Layer (FastAPI)
  │
  ▼
Service Layer
  │
  ▼
Data Access Layer
  │
  ▼
Database / Storage
```

구성 계층

| Layer    | 역할          |
| -------- | ----------- |
| Frontend | 사용자 인터페이스   |
| API      | HTTP API 제공 |
| Service  | 비즈니스 로직     |
| Data     | 데이터 처리      |
| Storage  | DB / 파일 저장  |

각 계층은 **명확한 책임 분리(Separation of Concerns)** 를 유지해야 한다.

---

# 3. 프로젝트 디렉토리 구조

권장 프로젝트 구조

```
project-root
│
├ ai
│
├ docs
│
├ src
│  ├ app
│  │
│  ├ api
│  │
│  ├ services
│  │
│  ├ models
│  │
│  ├ data
│  │
│  ├ storage
│  │
│  ├ scripts
│  │
│  └ frontend
│
├ tests
│
├ requirements.txt
└ README.md
```

각 디렉토리 역할

| 폴더       | 설명                      |
| -------- | ----------------------- |
| app      | FastAPI application 초기화 |
| api      | API 라우터                 |
| services | 비즈니스 로직                 |
| models   | 데이터 모델                  |
| data     | 데이터 처리                  |
| storage  | DB 접근                   |
| scripts  | 배치 / 유틸                 |
| frontend | UI 코드                   |
| tests    | 테스트 코드                  |

---

# 4. Backend Architecture

백엔드는 **FastAPI 기반 REST API** 구조로 설계된다.

### 구성

```
FastAPI
 ├ Router
 ├ Service
 ├ Repository
 └ Database
```

### 흐름

```
Client
  │
  ▼
API Router
  │
  ▼
Service
  │
  ▼
Repository
  │
  ▼
Database
```

### 역할 정의

| 구성         | 역할              |
| ---------- | --------------- |
| Router     | API endpoint 정의 |
| Service    | 비즈니스 로직         |
| Repository | DB 접근           |
| Database   | 실제 데이터 저장       |

### 예시 흐름

```
GET /stocks

Router
 → Service.get_stocks()

Service
 → Repository.fetch_stocks()

Repository
 → SQL Query

Database
 → Result
```

---

# 5. Frontend Architecture

Frontend는 다음 두 가지 방식으로 사용될 수 있다.

### 1️⃣ Streamlit (내부 분석 UI)

용도

* 데이터 분석
* 투자 대시보드
* 내부 도구

구조

```
frontend/streamlit

├ app.py
├ pages
├ components
└ services
```

---

### 2️⃣ React (외부 웹 서비스)

용도

* 웹 서비스
* 사용자 UI
* SaaS

구조

```
frontend/react

├ src
│ ├ pages
│ ├ components
│ ├ hooks
│ ├ api
│ └ state
```

Frontend는 API를 통해 백엔드와 통신한다.

```
React / Streamlit
        │
        ▼
      REST API
```

---

# 6. Data Architecture

데이터 계층은 다음 구조를 따른다.

```
Service
  │
  ▼
Repository
  │
  ▼
Database
```

지원 데이터 저장소

| 저장소           | 용도     |
| ------------- | ------ |
| SQLite        | 로컬 개발  |
| PostgreSQL    | 운영 DB  |
| CSV / Parquet | 데이터 분석 |
| Redis         | 캐시     |

데이터 처리 방식

* ETL scripts
* Batch processing
* API ingestion

---

# 7. AI Integration Architecture

AI 관련 로직은 **ai 디렉토리에서 관리**된다.

```
ai
│
├ base_guideline.md
├ context
├ prompts
├ rules
├ skills
└ workflow
```

AI 시스템 역할

| 구성        | 역할       |
| --------- | -------- |
| guideline | 코딩 원칙    |
| rules     | 언어별 규칙   |
| prompts   | AI 작업 정의 |
| skills    | 작업 모듈    |
| workflow  | 자동화 흐름   |

AI는 다음 작업을 수행한다.

* 코드 생성
* 코드 리뷰
* 리팩토링
* 테스트 생성
* 문서 생성

---

# 8. Deployment Architecture

배포 구조 예시

```
User
 │
 ▼
Cloudflare
 │
 ▼
Frontend
 │
 ▼
Backend API
 │
 ▼
Database
```

배포 방식

| 구성       | 방식             |
| -------- | -------------- |
| Backend  | Docker         |
| Frontend | Static hosting |
| DB       | Managed DB     |
| DNS      | Cloudflare     |

개발 환경에서는 다음 구조를 사용할 수 있다.

```
Local PC
 ├ FastAPI
 ├ Streamlit
 └ SQLite
```

---

# 9. Logging and Monitoring

시스템 운영을 위해 다음 기능이 필요하다.

### Logging

* API request log
* error log
* application log

### Monitoring

* API response time
* error rate
* DB performance

도구 예시

* Prometheus
* Grafana
* ELK stack

---

# 10. Security

보안 기본 원칙

### 인증

* JWT Authentication

### 권한

* Role based access control

### API 보안

* Rate limit
* Input validation
* CORS 정책

---

# 11. Testing Architecture

테스트 전략

| 테스트              | 설명           |
| ---------------- | ------------ |
| Unit Test        | 함수 단위        |
| Integration Test | 서비스 연동       |
| API Test         | endpoint 테스트 |

권장 도구

* pytest
* httpx
* coverage

---

# 12. Development Workflow

개발 흐름

```
PRD 작성
   │
   ▼
Architecture 설계
   │
   ▼
AI Planner
   │
   ▼
Code Generation
   │
   ▼
Code Review
   │
   ▼
Testing
   │
   ▼
Deployment
```

AI는 다음 단계에서 사용된다.

* 설계
* 코드 생성
* 리뷰
* 테스트 생성

---

# 13. Architecture Principles

시스템 설계 원칙

1️⃣ **Separation of Concerns**

각 계층은 명확한 책임을 가져야 한다.

2️⃣ **Modularity**

모듈 단위 개발을 유지한다.

3️⃣ **Scalability**

서비스 확장이 가능해야 한다.

4️⃣ **Maintainability**

코드 유지보수가 쉬워야 한다.

5️⃣ **Testability**

모든 주요 로직은 테스트 가능해야 한다.

---

다음으로 만드는 것이 좋다.

```
skills/planner.md
```

이 파일이 **AI 코딩 시스템의 핵심**이다.

원하면 다음 단계에서
**planner.md를 "AI 코딩 자동 설계 엔진 수준"으로 만들어 줄게.**
