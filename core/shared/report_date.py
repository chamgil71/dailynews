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
