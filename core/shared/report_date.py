# core/shared/report_date.py
"""
KST(Asia/Seoul) 기준 날짜 계산 — 3채널(news/stock/ai-issue) 공통 사용.

기존에는 각 스크립트가 datetime.now()를 그대로 쓰거나
datetime.now(timezone(timedelta(hours=9)))를 직접 풀어써서 제각각 구현했다.
전자는 OS/프로세스의 TZ 환경변수(GitHub Actions 워크플로우의 `env: TZ: Asia/Seoul`)에
암묵적으로 의존하므로, 로컬 개발 환경이나 TZ 미설정 환경에서 실행하면
조용히 다른 날짜가 나올 수 있다. 타임존을 코드에 명시해 이 의존성을 제거한다.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def kst_now() -> datetime:
    """현재 KST 기준 datetime (tz-aware)."""
    return datetime.now(KST)


def kst_today() -> str:
    """현재 KST 기준 오늘 날짜 (YYYY-MM-DD)."""
    return kst_now().strftime("%Y-%m-%d")


WEEKLY_SUFFIX = "(주간)"


def weekly_label(date_str: str) -> str:
    """주간 리포트 표시 라벨 — 'YYYY-MM-DD (주간)'. 사이트·이메일·SNS 공통.

    SPA(publish/app.html·index.html)의 JS 는 Python 과 공유할 수 없어 같은 형식을 별도 구현한다.
    """
    return f"{date_str} {WEEKLY_SUFFIX}"


# 리포트 MD 머리말의 생성 시각 — 뉴스·AI이슈 '생성일시: …', 주식 일일·주간 '생성: …'
_GENERATED_RE = re.compile(r"생성(?:일시)?\s*:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")
_HEADER_LINES = 15


def report_generated_at(md_text: str, fallback: str) -> str:
    """리포트가 실제로 생성된 시각(YYYY-MM-DD HH:MM). 머리말에 없으면 fallback.

    정적 페이지 하단 '생성 … KST' 표기에 빌드 시각(datetime.now) 대신 사용한다.
    빌드 시각을 쓰면 전체 재생성하는 주식·AI이슈 페이지가 내용이 같아도 매 빌드마다
    바뀌어 수십~백여 개 파일이 불필요하게 커밋되고, 표기도 실제 생성 시각이 아니게 된다.
    """
    head = "\n".join(md_text.splitlines()[:_HEADER_LINES])
    m = _GENERATED_RE.search(head)
    return m.group(1) if m else fallback
