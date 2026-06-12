# core/shared/notion.py
"""
노션(Notion) 데이터베이스 연동 및 동기화 모듈
- 동적 스키마 검색: 노션 DB의 속성명(한글/영어) 및 타입을 자동으로 감지하여 유연하게 매핑
- 병렬 업로드: ThreadPoolExecutor를 이용한 고속 병렬 페이지 생성 (속도 대폭 개선)
- 안정적인 재시도 로직: Notion API Rate Limit(429) 및 네트워크 에러 대비 3회 재시도 및 대기 적용
"""

import logging
import os
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

NOTION_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB_NEWS = os.getenv("NOTION_DATABASE_ID_NEWS")
NOTION_DB_STOCK = os.getenv("NOTION_DATABASE_ID_STOCK")

def _get_headers() -> dict:
    return {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

def get_database_schema(database_id: str) -> dict | None:
    """Notion DB 스키마 정보를 동적으로 조회하여 컬럼 이름과 타입을 파악합니다."""
    if not NOTION_KEY or not database_id:
        return None
    url = f"https://api.notion.com/v1/databases/{database_id}"
    try:
        res = requests.get(url, headers=_get_headers(), timeout=10)
        if res.status_code == 200:
            return res.json().get("properties", {})
        else:
            logger.error(f"[Notion] 데이터베이스 정보 조회 실패 ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        logger.error(f"[Notion] 데이터베이스 조회 오류: {e}")
        return None

def _create_page_with_retry(headers: dict, payload: dict, max_retries: int = 3) -> tuple[bool, str]:
    """페이지 생성 API 호출 (Rate Limit 429 대응 및 재시도 로직 내장)"""
    url = "https://api.notion.com/v1/pages"
    for attempt in range(max_retries):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=12)
            if res.status_code == 200:
                return True, "Success"
            elif res.status_code == 429:
                retry_after = int(res.headers.get("Retry-After", 2))
                logger.warning(f"[Notion] Rate Limit(429) 감지. {retry_after}초 대기 후 재시도 ({attempt + 1}/{max_retries})")
                time.sleep(retry_after)
            else:
                # 400 등 일반적인 클라이언트/서버 오류의 경우도 일단 대기 후 재시도
                time.sleep(1)
        except Exception as e:
            if attempt == max_retries - 1:
                return False, str(e)
            time.sleep(1.5)
    return False, f"Max retries ({max_retries}) reached"

def sync_news_to_notion(news_items: list, date_str: str = None) -> int:
    """
    수집 완료된 신규 뉴스 기사들을 Notion 뉴스 데이터베이스에 고속 병렬로 페이지를 만들어 삽입합니다.
    """
    if not NOTION_KEY or not NOTION_DB_NEWS:
        logger.warning("[Notion 뉴스] NOTION_API_KEY 또는 NOTION_DATABASE_ID_NEWS 환경변수가 누락되어 동기화를 건너뜁니다.")
        return 0

    if not news_items:
        logger.info("[Notion 뉴스] 동기화할 신규 뉴스 기사가 없습니다.")
        return 0

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"[Notion 뉴스] '{NOTION_DB_NEWS}' 데이터베이스 스키마 검색 중...")
    schema = get_database_schema(NOTION_DB_NEWS)
    
    # ── 컬럼 매핑 규칙 동적 분석 ──
    # 기본값 설정
    col_title = "제목"
    col_url = "링크"
    col_category = "카테고리"
    col_date = "날짜"
    col_lang = "언어"

    if schema:
        # 1. Title 타입 컬럼 자동 매핑 (노션 DB의 기본 키 컬럼)
        for name, prop in schema.items():
            if prop.get("type") == "title":
                col_title = name
                break

        # 2. URL 타입 컬럼 자동 매핑
        url_found = False
        for name, prop in schema.items():
            if prop.get("type") == "url":
                col_url = name
                url_found = True
                break
        if not url_found:
            # URL 타입 컬럼이 없을 경우 한글/영어 텍스트 매핑 시도
            for name in ["링크", "Link", "URL", "url"]:
                if name in schema:
                    col_url = name
                    break

        # 3. Category (카테고리/라벨) 컬럼 매핑
        for name in ["카테고리", "Category", "라벨", "Label", "label", "category"]:
            if name in schema:
                col_category = name
                break

        # 4. Date (날짜) 컬럼 매핑
        for name in ["날짜", "Date", "date", "수집일", "날짜선택"]:
            if name in schema:
                col_date = name
                break

        # 5. Language (언어) 컬럼 매핑
        for name in ["언어", "Language", "Lang", "lang", "language"]:
            if name in schema:
                col_lang = name
                break

    logger.info(f"[Notion 뉴스] 최종 컬럼 매핑 적용 완료: [제목: '{col_title}'], [링크: '{col_url}'], "
                f"[카테고리: '{col_category}'], [날짜: '{col_date}'], [언어: '{col_lang}']")

    headers = _get_headers()
    payloads = []

    # 각 기사별로 Notion 페이지 생성용 Payload 조립
    for item in news_items:
        properties = {}
        
        # 1) 제목 컬럼
        properties[col_title] = {
            "title": [{"text": {"content": item.get("title", "")[:100]}}]
        }
        
        # 2) 링크 컬럼 (스키마에 맞춰 url 혹은 rich_text로 분기)
        is_url_type = schema and schema.get(col_url, {}).get("type") == "url"
        if is_url_type or not schema:
            properties[col_url] = {"url": item.get("link", "")}
        else:
            properties[col_url] = {
                "rich_text": [{"text": {"content": item.get("link", "")}}]
            }
            
        # 3) 카테고리 컬럼
        is_select = schema and schema.get(col_category, {}).get("type") == "select"
        label_val = item.get("label", item.get("category", "기타"))
        if is_select or not schema:
            properties[col_category] = {"select": {"name": label_val}}
        else:
            properties[col_category] = {
                "rich_text": [{"text": {"content": label_val}}]
            }
            
        # 4) 날짜 컬럼
        is_date_type = schema and schema.get(col_date, {}).get("type") == "date"
        if is_date_type or not schema:
            properties[col_date] = {"date": {"start": date_str}}
        else:
            properties[col_date] = {
                "rich_text": [{"text": {"content": date_str}}]
            }
            
        # 5) 언어 컬럼
        is_select_lang = schema and schema.get(col_lang, {}).get("type") == "select"
        lang_val = item.get("lang", "ko").upper()
        if is_select_lang or not schema:
            properties[col_lang] = {"select": {"name": lang_val}}
        else:
            properties[col_lang] = {
                "rich_text": [{"text": {"content": lang_val}}]
            }

        payload = {
            "parent": {"database_id": NOTION_DB_NEWS},
            "properties": properties
        }
        payloads.append(payload)

    # 고속 병렬 삽입 실행 (최대 5개 스레드로 속도 극대화 및 안전성 유지)
    logger.info(f"[Notion 뉴스] 총 {len(payloads)}개 뉴스 기사를 Notion으로 전송 시작합니다...")
    success_count = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_payload = {executor.submit(_create_page_with_retry, headers, payload): payload for payload in payloads}
        for future in as_completed(future_to_payload):
            success, err_msg = future.result()
            if success:
                success_count += 1
            else:
                logger.error(f"[Notion 뉴스] 페이지 생성 실패: {err_msg}")

    logger.info(f"[Notion 뉴스] 동기화 완료: 총 {len(payloads)}건 중 {success_count}건 성공적으로 기록 완료.")
    return success_count


def sync_stock_to_notion(date_str: str, summary: str, market_data: dict = None, temperature: str = None) -> bool:
    """
    일일 주식 시황 브리핑을 Notion 주식 데이터베이스에 기록합니다.
    - date_str: "2026-05-26"
    - summary: 핵심 요약 텍스트 (3줄 요약)
    - market_data: {"kospi": ..., "kosdaq": ..., "sp500": ..., "exchange_rate": ...} 등
    - temperature: 시장 온도계 값 (예: "🟠 상승")
    """
    if not NOTION_KEY or not NOTION_DB_STOCK:
        logger.warning("[Notion 주식] NOTION_API_KEY 또는 NOTION_DATABASE_ID_STOCK 환경변수가 누락되어 동기화를 건너뜁니다.")
        return False

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"[Notion 주식] '{NOTION_DB_STOCK}' 데이터베이스 스키마 검색 중...")
    schema = get_database_schema(NOTION_DB_STOCK)

    # ── 컬럼 매핑 ──
    col_title       = "제목"
    col_date        = "날짜"
    col_summary     = "요약"
    col_kospi       = "코스피"
    col_sp500       = "S&P500"
    col_exchange    = "환율"
    col_temperature = "시장온도"

    if schema:
        for name, prop in schema.items():
            if prop.get("type") == "title":
                col_title = name
                break
        for name in ["날짜", "Date", "date"]:
            if name in schema:
                col_date = name
                break
        for name in ["요약", "Summary", "summary", "핵심요약"]:
            if name in schema:
                col_summary = name
                break
        for name in ["코스피", "KOSPI", "kospi"]:
            if name in schema:
                col_kospi = name
                break
        for name in ["S&P500", "SP500", "sp500", "S&P 500"]:
            if name in schema:
                col_sp500 = name
                break
        for name in ["환율", "원달러", "KRW/USD", "exchange"]:
            if name in schema:
                col_exchange = name
                break
        for name in ["시장온도", "온도계", "Temperature", "temperature"]:
            if name in schema:
                col_temperature = name
                break

    market_data = market_data or {}
    properties = {}

    # 제목: "📊 주식 시황 브리핑 — 2026-05-26"
    properties[col_title] = {
        "title": [{"text": {"content": f"📊 주식 시황 브리핑 — {date_str}"}}]
    }

    # 날짜
    is_date_type = schema and schema.get(col_date, {}).get("type") == "date"
    if is_date_type or not schema:
        properties[col_date] = {"date": {"start": date_str}}
    else:
        properties[col_date] = {"rich_text": [{"text": {"content": date_str}}]}

    # 요약
    if col_summary in (schema or {}):
        properties[col_summary] = {
            "rich_text": [{"text": {"content": (summary or "")[:2000]}}]
        }

    # 수치 필드 (number 타입이면 number, 아니면 rich_text)
    def _set_number_col(col_name, value):
        if not value or col_name not in (schema or {}):
            return
        is_num = schema and schema.get(col_name, {}).get("type") == "number"
        try:
            num_val = float(str(value).replace(",", "").replace("%", ""))
            if is_num:
                properties[col_name] = {"number": num_val}
            else:
                properties[col_name] = {"rich_text": [{"text": {"content": str(value)}}]}
        except ValueError:
            properties[col_name] = {"rich_text": [{"text": {"content": str(value)}}]}

    _set_number_col(col_kospi,    market_data.get("kospi"))
    _set_number_col(col_sp500,    market_data.get("sp500"))
    _set_number_col(col_exchange, market_data.get("exchange_rate"))

    # 시장 온도계 (select 또는 rich_text)
    if temperature and col_temperature in (schema or {}):
        is_select = schema and schema.get(col_temperature, {}).get("type") == "select"
        if is_select:
            properties[col_temperature] = {"select": {"name": temperature}}
        else:
            properties[col_temperature] = {"rich_text": [{"text": {"content": temperature}}]}

    payload = {
        "parent": {"database_id": NOTION_DB_STOCK},
        "properties": properties
    }

    headers = _get_headers()
    success, err_msg = _create_page_with_retry(headers, payload)
    if success:
        logger.info(f"[Notion 주식] {date_str} 시황 기록 완료.")
    else:
        logger.error(f"[Notion 주식] 기록 실패: {err_msg}")
    return success


def sync_ai_issue_to_notion(issue_date: str, period: str, top10: list,
                             outlook: str, database_id: str = None) -> int:
    """
    주간 AI 이슈 보고서를 Notion AI Issue 데이터베이스에 기록합니다.
    - issue_date: "2026-06-01" (일요일 날짜)
    - period: "2026-05-26 ~ 2026-06-01"
    - top10: List[dict] — rank, title, category, importance, summary
    - outlook: 차주 전망 텍스트
    - database_id: NOTION_DATABASE_ID_AI_ISSUE (없으면 환경변수에서 읽음)
    """
    db_id = database_id or os.getenv("NOTION_DATABASE_ID_AI_ISSUE")
    if not NOTION_KEY or not db_id:
        logger.warning("[Notion AI이슈] NOTION_API_KEY 또는 NOTION_DATABASE_ID_AI_ISSUE 환경변수가 누락되어 동기화를 건너뜁니다.")
        return 0

    if not top10:
        logger.info("[Notion AI이슈] 동기화할 이슈 데이터가 없습니다.")
        return 0

    logger.info(f"[Notion AI이슈] '{db_id}' 데이터베이스 스키마 검색 중...")
    schema = get_database_schema(db_id)

    col_title    = "제목"
    col_date     = "날짜"
    col_period   = "기간"
    col_category = "카테고리"
    col_rank     = "순위"
    col_summary  = "요약"
    col_outlook  = "차주전망"

    if schema:
        for name, prop in schema.items():
            if prop.get("type") == "title":
                col_title = name
                break
        for name in ["날짜", "Date", "date"]:
            if name in schema: col_date = name; break
        for name in ["기간", "Period", "period"]:
            if name in schema: col_period = name; break
        for name in ["카테고리", "Category", "category"]:
            if name in schema: col_category = name; break
        for name in ["순위", "Rank", "rank"]:
            if name in schema: col_rank = name; break
        for name in ["요약", "Summary", "summary"]:
            if name in schema: col_summary = name; break
        for name in ["차주전망", "Outlook", "outlook", "전망"]:
            if name in schema: col_outlook = name; break

    headers = _get_headers()
    payloads = []

    for issue in top10:
        properties = {}
        # 제목
        properties[col_title] = {
            "title": [{"text": {"content": f"[{issue.get('rank', '')}] {issue.get('title', '')}"[:100]}}]
        }
        # 날짜
        is_date_type = schema and schema.get(col_date, {}).get("type") == "date"
        if is_date_type or not schema:
            properties[col_date] = {"date": {"start": issue_date}}
        else:
            properties[col_date] = {"rich_text": [{"text": {"content": issue_date}}]}

        # 기간
        if col_period in (schema or {}):
            properties[col_period] = {"rich_text": [{"text": {"content": period}}]}

        # 카테고리
        if col_category in (schema or {}):
            is_select = schema and schema.get(col_category, {}).get("type") == "select"
            cat_val = issue.get("category", "기타")
            if is_select or not schema:
                properties[col_category] = {"select": {"name": cat_val}}
            else:
                properties[col_category] = {"rich_text": [{"text": {"content": cat_val}}]}

        # 순위
        if col_rank in (schema or {}):
            is_num = schema and schema.get(col_rank, {}).get("type") == "number"
            if is_num:
                properties[col_rank] = {"number": issue.get("rank", 0)}
            else:
                properties[col_rank] = {"rich_text": [{"text": {"content": str(issue.get("rank", ""))}}]}

        # 요약
        if col_summary in (schema or {}):
            properties[col_summary] = {
                "rich_text": [{"text": {"content": issue.get("summary", "")[:2000]}}]
            }

        # 차주전망 (1번 이슈에만 첨부)
        if issue.get("rank") == 1 and col_outlook in (schema or {}):
            properties[col_outlook] = {
                "rich_text": [{"text": {"content": (outlook or "")[:2000]}}]
            }

        # ── 5번 요구사항: 상세 본문(Page Body) children 블록 구성 ──
        body_blocks = []
        
        # 1. 머리글 추가
        body_blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": f"🤖 {issue.get('rank')}위 이슈 상세 리포트"}}]
            }
        })
        
        # 2. 요약글 추가
        if issue.get("summary"):
            body_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"📝 요약: {issue['summary']}"}}]
                }
            })
            
        # 3. 마크다운 상세(detail) 파싱 후 children 추가 (TOP 3 심층 분석)
        detail_md = issue.get("detail", "")
        if detail_md:
            body_blocks.extend(_markdown_to_notion_blocks(detail_md))
            
        # 4. 1위 이슈인 경우 차주 전망(outlook)도 본문 하단에 추가적 적재
        if issue.get("rank") == 1 and outlook:
            body_blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "🔮 차주 AI 모니터링 포인트 및 전망"}}]
                }
            })
            body_blocks.extend(_markdown_to_notion_blocks(outlook))

        payload = {
            "parent": {"database_id": db_id},
            "properties": properties
        }
        
        if body_blocks:
            payload["children"] = body_blocks[:100] # Notion 100개 제한

        payloads.append(payload)

    logger.info(f"[Notion AI이슈] 총 {len(payloads)}개 이슈를 Notion으로 전송 시작합니다...")
    success_count = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_create_page_with_retry, headers, p): p for p in payloads}
        for future in as_completed(futures):
            ok, err = future.result()
            if ok:
                success_count += 1
            else:
                logger.error(f"[Notion AI이슈] 페이지 생성 실패: {err}")

    logger.info(f"[Notion AI이슈] 동기화 완료: {len(payloads)}건 중 {success_count}건 성공.")
    return success_count


def _markdown_to_notion_blocks(md_text: str) -> list[dict]:
    """간단한 Markdown 텍스트를 Notion Block Object 리스트로 컴파일합니다."""
    if not md_text:
        return []
        
    blocks = []
    lines = md_text.splitlines()
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Heading 3 (### )
        if line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                }
            })
        # Heading 2 (## )
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                }
            })
        # Bulleted list (- or * )
        elif line.startswith("- ") or line.startswith("* "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                }
            })
        # Paragraph
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line[:2000]}}]
                }
            })
        i += 1
        
    return blocks
