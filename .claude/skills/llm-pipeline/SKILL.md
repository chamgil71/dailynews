---
description: LLM 연동 파이프라인(Pydantic 입력 검증, 프롬프트 엔진, 입력/출력 가드, PII 마스킹)을 직접 구현할 때 참고하는 실물 코드 가이드. RAG나 챗봇, 프롬프트 인젝션 방어, 개인정보 마스킹을 구현하는 프로젝트에서만 로드하면 된다.
---

# LLM 파이프라인 개발 표준 및 실물 구현 가이드

`development` 스킬이 정의하는 개발 거버넌스를 준수하는 LLM 연동 파이프라인(Pydantic, Prompt Engine, Input/Output Guards)의 모범 코드 구현 가이드다.

---

## 1. Pydantic v2 유효성 검사 표준

API 엔드포인트의 입력 라우터 레벨에서 데이터 정합성을 필수로 검증한다.

```python
from pydantic import BaseModel, Field, field_validator
import re

class StockQueryRequest(BaseModel):
    ticker: str = Field(..., min_length=3, max_length=6, description="주식 티커명 (예: AAPL)")
    limit: int = Field(10, ge=1, le=100, description="조회 건수")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[A-Z]+$", v):
            raise ValueError("Ticker must contain only uppercase alphabets")
        return v
```

---

## 2. 프롬프트 엔진 및 동적 템플릿 로딩

시스템 프롬프트는 소스 코드 내에 하드코딩하지 않고, 물리적 YAML/Markdown 파일로 완전히 격리하고 동적으로 로드해 관리한다.

```yaml
# configs/prompts/stock_analysis.yaml
system_prompt: |
  당신은 주식 시장 분석 전문가입니다. 주어진 컨텍스트를 바탕으로 객관적인 정보를 제공하십시오.
  답변은 반드시 다음 형식을 유지해야 합니다.
```

```python
# src/services/prompt_service.py
import yaml
import os

class PromptEngine:
    def __init__(self, prompt_dir: str):
        self.prompt_dir = prompt_dir

    def load_prompt_template(self, prompt_name: str) -> str:
        prompt_path = os.path.join(self.prompt_dir, f"{prompt_name}.yaml")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt template {prompt_path} not found.")
        with open(prompt_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config["system_prompt"]
```

---

## 3. 입력 가드 (Input Guard) 및 프롬프트 인젝션 방어

외부 요청에 대해 토큰 크기를 제한하고 시스템 프롬프트 우회나 Jailbreak 시도를 정규표현식으로 1차 필터링한다.

```python
import re

INJECTION_PATTERNS = [
    r"이전\s*(지시|명령|규칙).*무시",
    r"(ignore|forget|disregard).*(instruction|prompt|rule)",
    r"당신의\s*(역할|시스템\s*프롬프트).*알려",
    r"(reveal|show|repeat).*(system\s*prompt|instruction)",
    r"jailbreak"
]

def input_guard_check(user_input: str) -> str:
    if len(user_input) > 4000:
        raise ValueError("Input length exceeds 4,000 characters limit.")
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            raise PermissionError("Suspicious input pattern detected (Injection Blocked).")
    return user_input
```

---

## 4. 출력 가드 (Output Guard) 및 개인정보 마스킹

LLM의 비결정적 출력이 정형화된 JSON 형식을 준수하도록 보장하며, 주민등록번호·휴대전화·이메일 등 기밀 데이터(PII)를 전송 전에 필터링 마스킹한다.

```python
import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

PII_PATTERNS = {
    "rrn": r"\d{6}-[1-4]\d{6}",
    "phone": r"01[0-9]-\d{3,4}-\d{4}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
}

def mask_pii_data(text: str) -> str:
    for name, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f"[MASKED_{name.upper()}]", text)
    return text

def output_guard_pipeline(llm_client, prompt: str, max_retries: int = 1) -> Dict[str, Any]:
    retry_count = 0
    fallback_response = {
        "answer": "죄송합니다. 현재 답변을 생성하기 어렵습니다. 잠시 후 다시 시도해 주세요.",
        "sources": [], "confidence": "low", "fallback": True
    }
    while retry_count <= max_retries:
        try:
            raw_response = llm_client.call(prompt, timeout=3.0)
            masked_response = mask_pii_data(raw_response)
            json_text = re.sub(r"```json|```", "", masked_response).strip()
            data = json.loads(json_text)
            return data
        except (json.JSONDecodeError, Exception) as e:
            retry_count += 1
            if retry_count > max_retries:
                break
            prompt += f"\n\n[Warning] JSON 파싱 실패. 철저히 JSON만 출력하십시오: {str(e)}"
    logger.error("LLM parsing failed. Immediate fallback triggered to preserve system availability.")
    return fallback_response
```
