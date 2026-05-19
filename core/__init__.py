# core/__init__.py
"""
핵심 비즈니스 로직 패키지.

서브패키지 구조:
  core/news/   — 뉴스 수집(collector) · 분석(analyzer) · 리포트(report)
  core/stock/  — 주식 수집(collector) · 분석(analyzer) · 리포트(report)
  core/shared/ — 공통 유틸 (mailer, db)

루트 직접 임포트 (하위 호환):
  from core.collector import collect_news   # → core.news.collector
  from core.mailer import send_email        # → core.shared.mailer
"""
