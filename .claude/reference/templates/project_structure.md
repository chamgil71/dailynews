Project Structure Guide
=======================

1\. Overview
------------

이 프로젝트는 **AI 협업 개발 환경을 고려하여 설계된 구조**이다.  
구조의 핵심 목적은 다음과 같다.

*   AI와 개발자가 **같은 규칙을 공유**하도록 한다
*   **도메인 구조와 인프라 구조를 분리**한다
*   **FastAPI 기반 백엔드 + Streamlit + React 프론트**를 동시에 지원한다
*   문서 / 규칙 / 코드 / 설정을 **명확하게 계층 분리**한다

전체 구조는 다음과 같다.

```
project_root/
├─ ai/
├─ config/
├─ docs/
├─ src/
├─ web/
├─ tests/
├─ scripts/
├─ .env
├─ .env.sample
└─ requirements.txt
```

* * *

2\. AI Layer (AI 협업 시스템)
========================

위치

```
ai/
```

이 폴더는 **AI 개발 규칙 및 컨텍스트 관리 시스템**이다.

LLM(Claude, GPT, Antigravity 등)이  
프로젝트를 이해하고 코드를 생성할 때 참고한다.

```
ai/
├─ base_guideline.md
├─ context/
├─ prompts/
├─ rules/
├─ skills/
└─ workflow/
```

2.1 base\_guideline.md
----------------------

AI 시스템의 **최상위 헌법 문서**이다.

포함 내용

*   AI 역할 정의
*   프로젝트 개발 철학
*   SRP / Clean Architecture 원칙
*   코드 생성 기본 규칙

AI는 항상 이 문서를 기준으로 행동해야 한다.

* * *

2.2 context/
------------

프로젝트 상태 및 히스토리 기록.

```
ai/context/
```

포함 예시

*   project\_summary.md
*   current\_state.md
*   개발 히스토리

AI가 **프로젝트 현재 상황을 이해**하기 위해 사용한다.

* * *

2.3 prompts/
------------

반복적으로 사용하는 **메타 프롬프트 저장소**

```
ai/prompts/
```

예

*   meta\_prompt.md
*   코드 생성 프롬프트
*   리뷰 프롬프트

* * *

2.4 rules/
----------

언어 및 프레임워크별 **Strict Rule 정의**

```
ai/rules/
```

예

*   python\_rules.md
*   backend\_fastapi\_rules.md
*   frontend\_react\_rules.md
*   streamlit\_rules.md

이 문서들은 **코드 스타일 및 구조 규칙**을 강제한다.

* * *

2.5 skills/
-----------

AI 전문 지식 모듈.

```
ai/skills/
```

예

*   planner.md
*   database.md
*   storage.md
*   services.md
*   web\_streamlit.md
*   code\_review.md

각 파일은 특정 역할의 **지식 패키지**다.

* * *

2.6 workflow/
-------------

AI 작업 흐름 정의

```
ai/workflow/
```

예

*   orchestrator.md

AI가 작업을 수행할 때

```
기획 → 구현 → 테스트 → 리뷰
```

순서를 정의한다.

* * *

3\. Configuration Layer
=======================

위치

```
config/
```

프로젝트 설정 관리.

```
config/
├─ config.yaml
└─ logging.yaml
```

설정 예

*   데이터베이스 설정
*   API 설정
*   환경별 설정
*   로깅 정책

* * *

4\. Documentation Layer
=======================

위치

```
docs/
```

프로젝트 공식 문서 저장소.

포함 문서

*   PRD
*   Architecture
*   API Spec
*   Project Structure

* * *

5\. Backend Layer (FastAPI)
===========================

위치

```
src/
```

백엔드 핵심 코드 영역이다.

```
src/
├─ api/
├─ core/
├─ repositories/
├─ services/
├─ models/
├─ utils/
└─ main.py
```

* * *

5.1 api/
--------

외부 인터페이스 계층

```
src/api/
```

포함

*   FastAPI router
*   request/response 처리
*   dependency injection

규칙

```
router → service 호출만 수행
business logic 금지
```

* * *

5.2 core/
---------

프레임워크 핵심 기능.

```
src/core/
```

예

*   config loader
*   security
*   exception handling
*   logging

* * *

5.3 repositories/
-----------------

데이터 접근 계층.

```
src/repositories/
```

예

*   database access
*   cache access
*   file storage

구조 예

```
repositories/
├─ db/
├─ cache/
└─ storage/
```

* * *

5.4 services/
-------------

비즈니스 로직 계층.

```
src/services/
```

서비스는 다음 책임을 가진다.

*   도메인 로직
*   데이터 처리
*   비즈니스 규칙

* * *

5.5 models/
-----------

도메인 모델 및 API 스키마.

```
src/models/
```

포함

*   Domain Models
*   Pydantic Schemas
*   Validation Models

* * *

5.6 utils/
----------

공통 유틸리티.

```
src/utils/
```

예

*   helper functions
*   common utilities
*   shared helpers

* * *

5.7 main.py
-----------

FastAPI 애플리케이션 진입점.

```
src/main.py
```

예

*   FastAPI app 생성
*   router 등록
*   middleware 설정

* * *

6\. Frontend Layer
==================

위치

```
web/
```

두 가지 프론트 전략을 지원한다.

```
web/
├─ streamlit/
└─ frontend/
```

* * *

6.1 streamlit/
--------------

빠른 내부 UI 및 프로토타입 용도.

예

*   데이터 분석
*   내부 대시보드
*   실험용 UI

* * *

6.2 frontend/
-------------

정식 웹 서비스 UI.

표준 기술 스택 체인

```
React
  ↓
TanStack Start
  ↓
Vite
  ↓
Tailwind CSS
  ↓
shadcn/ui
```

* * *

7\. Testing Layer
=================

위치

```
tests/
```

pytest 기반 테스트 코드.

예

```
tests/
├─ unit/
├─ integration/
└─ api/
```

* * *

8\. Scripts Layer
=================

위치

```
scripts/
```

운영 및 관리 스크립트.

예

*   데이터 마이그레이션
*   초기화 스크립트
*   배포 스크립트

* * *

9\. Environment Configuration
=============================

.env
----

비공개 환경 변수.

예

```
DATABASE_URL
API_KEYS
SECRET_KEY
```

* * *

.env.sample
-----------

환경 변수 템플릿.

팀원 또는 배포 환경에서 사용.

* * *

10\. Dependency Management
==========================

파일

```
requirements.txt
```

Python 패키지 의존성 관리.

예

*   fastapi
*   pydantic
*   sqlalchemy
*   pytest

* * *

11\. Architecture Summary
=========================

이 프로젝트는 다음 구조 원칙을 따른다.

*   Clean Architecture
*   Layered Architecture
*   AI-assisted Development

핵심 흐름

```
Client
 ↓
API Router
 ↓
Service
 ↓
Repository
 ↓
Database / Storage
```

```
project_root/
├─ ai/                       # AI 컨텍스트 및 가이드라인 (LLM 참조용)
│  ├─ base_guideline.md      # 프로젝트 페르소나 및 핵심 원칙
│  ├─ context/               # 히스토리 및 현재 진행 상황 기록
│  ├─ prompts/               # 반복 사용되는 메타 프롬프트 관리
│  ├─ rules/                 # 언어/프레임워크별 Strict Rules
│  ├─ skills/                # 역할별 전문 지식 (Planner, DB 등)
│  └─ workflow/              # 작업 단계별 오케스트레이션 로직
├─ config/                   # 설정 관리 (YAML, Logging)
│  ├─ config.yaml
│  └─ logging.yaml
├─ docs/                     # 문서화 (PRD, Architecture, API Spec)
├─ src/                      # 백엔드 및 시스템 코어 (FastAPI/Python)
│  ├─ api/                   # 외부 인터페이스 (router, dependencies, wrapper)
│  ├─ core/                  # framework core (config, logging, security, exceptions)
│  ├─ repositories/          # 데이터 접근 계층(db),cache, storage(출력산출물)를 하위폴더로
│  ├─ services/              # 비즈니스 로직
│  ├─ models/                # Domain models + API schema (Pydantic)
│  ├─ utils/                 # 공통 유틸리티
│  └─ main.py                # 진입점
├─ web/                      # 프론트엔드 영역
│  ├─ streamlit/             # 빠른 프로토타이핑/내부 도구용
│  └─ frontend/              # 본격적인 웹 서비스용 (React → TanStack Start → Vite → Tailwind CSS → shadcn/ui)
├─ tests/                    # pytest 기반 테스트 코드
├─ scripts/                  # 배포, 마이그레이션, 초기화 스크립트
├─ .env                      # 환경 변수 (비공개)
├─ .env.sample               # 환경 변수 템플릿
└─ requirements.txt          # 의존성 관리
```