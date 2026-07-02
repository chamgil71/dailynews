# 수직 4대 레이어 격리 모범 및 안티패턴 코드 표준 (architecture_standards.md)

이 문서는 AI-PMO 아키텍처 거버넌스(`03_architecture.md`)를 준수하는 백엔드 애플리케이션의 수직 데이터 흐름 레이어 격리 구현 표준과 안티패턴을 제시한다.

---

## 1. 아키텍처 개요

모든 데이터 흐름은 단방향으로 흐르며 상위 계층이 하위 계층을 직접 호출한다. 역방향 호출 및 계층 건너뛰기는 금지된다.

```text
[요청] Router (API) ──► Service (Business) ──► Repository (Data Access) ──► Database [응답]
```

---

## 2. 계층별 모범 구현 패턴 (Best Practice)

### 2.1 Router Layer (API 진입점)
Router는 클라이언트의 HTTP 요청을 수신하고, 입력 매개변수를 샌티타이징하며, Service Layer에 비즈니스 처리를 위임한다. DB나 ORM 객체에 직접 의존하지 않는다.

```python
# src/web/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.services.user_service import UserService
from src.models.schemas import UserResponse, UserCreateRequest

router = APIRouter(prefix="/users", tags=["Users"])

# 의존성 주입 헬퍼 함수
def get_user_service(db=Depends(get_db_session)) -> UserService:
    from src.database.user_repository import UserRepository
    repo = UserRepository(db)
    return UserService(repo)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        # Router는 Service 계층의 비즈니스 API만 호출함
        return service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

### 2.2 Service Layer (순수 비즈니스 로직)
Service Layer는 비즈니스 규칙과 제약을 평가한다. DB 연결, 네트워크 I/O 등을 직접 수용하지 않으며 Repository 인터페이스를 통해서만 데이터를 영속화한다. RAG 연동 시 프롬프트 템플릿의 가공 및 결합도 이곳에서 수행한다.

```python
# src/services/user_service.py
from src.core.exceptions import UserNotFoundError
from src.database.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_by_id(self, user_id: int):
        # 1. 비즈니스 정합성 체크
        if user_id <= 0:
            raise ValueError("Invalid User ID")
        
        # 2. Repository 호출로 데이터 획득
        user = self.repo.fetch_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} does not exist.")
            
        return user
```

### 2.3 Repository Layer (데이터 액세스 추상화)
Repository는 데이터베이스 쿼리, 벡터 인덱스 검색 등 물리 인프라로의 데이터 접근을 전담한다. Service Layer가 인프라 상세를 알 필요가 없도록 도메인 모델이나 정형 데이터 구조로 변환하여 리턴한다.

```python
# src/database/user_repository.py
from sqlalchemy.orm import Session
from src.models.db_models import UserModel

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def fetch_by_id(self, user_id: int):
        # ORM을 이용한 실제 데이터베이스 조회 전담
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
```

---

## 3. 계층 침범 안티패턴 (Anti-Patterns)

### 3.1 ❌ Router에서 데이터베이스 ORM 직접 호출
API 진입점에서 데이터베이스 세션을 결합해 직접 SQL이나 ORM 쿼리를 구동하는 행위는 계층 격리 실패에 해당한다.
```python
# router.py (BAD)
@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    # 비평: Router가 데이터 액세스 모델 및 스키마에 직접 강결합됨
    user = db.query(UserModel).filter(UserModel.id == user_id).first() 
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    return user
```

### 3.2 ❌ Repository에서 비즈니스 로직 및 프롬프트 조립 수행
RAG 시스템 개발 시, Repository 계층이 벡터 DB의 검색 결과에 시스템 프롬프트 조지(Context String)를 감싸 조립해 반환하는 행위는 프롬프트 엔지니어링이 인프라 데이터 계층에 강결합되게 하므로 금지한다.
```python
# vector_repository.py (BAD)
class VectorRepository:
    def search_context_prompt(self, query: str):
        raw_docs = self.vector_db.similarity_search(query)
        # 비평: 데이터 저장소 계층이 프롬프트 서식 조립이라는 비즈니스/프롬프트 영역을 대행함
        context = "\n".join([doc.page_content for doc in raw_docs])
        return f"이 컨텍스트를 기반으로 답하십시오:\n{context}"
```
*올바른 수정 방향: `VectorRepository`는 가공되지 않은 순수한 데이터 엔티티(`List[DocumentEntity]`)만 반환하며, 프롬프트 포맷 가공은 오직 `Service Layer` 내부의 `Prompt Engine`이 전담한다.*
