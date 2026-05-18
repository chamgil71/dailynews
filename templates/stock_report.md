# 📊 일일 주식 시황 브리핑 — {{ date }}

> 📅 생성일시: {{ generated_at }}
> 📊 데이터 기준: {{ market_close_time }}

---

## ■ 핵심 요약 (3줄)
{{ summary }}

---

## 1. 국내 시장

| 지수 | 종가 | 등락률 |
|------|-----:|-------:|
| 코스피 | {{ kospi_close }} | {{ kospi_chg }}% |
| 코스닥 | {{ kosdaq_close }} | {{ kosdaq_chg }}% |
| 원/달러 | {{ usd_krw_close }}원 | {{ usd_krw_chg }}% |

> **주요 이슈**
{{ domestic_issues }}

---

## 2. 글로벌 시장

| 지수/지표 | 수치 | 등락 |
|-----------|-----:|------:|
| S&P 500 | {{ sp500_close }} | {{ sp500_chg }}% |
| 나스닥 | {{ nasdaq_close }} | {{ nasdaq_chg }}% |
| 다우존스 | {{ dow_close }} | {{ dow_chg }}% |
| 미국 10년물 금리 | {{ us10y_val }}% | {{ us10y_bp }}bp |
| WTI 유가 | ${{ wti_close }} | {{ wti_chg }}% |

> **매크로**
{{ global_macro }}

---

## 3. 핵심 키워드 TOP 5
{{ keywords }}

---

## 4. 섹터별 영향 분석

### 🇰🇷 국내

{{ sectors_kr_table }}

### 🇺🇸 해외

{{ sectors_us_table }}

---

## 5. 내일 주목 이벤트

{{ events_table }}

---

## 6. 장기투자 관점 코멘트
{{ lt_comment }}

---

## 시장 온도계: {{ temperature_display }}

> {{ temperature_reason }}

---
※ 투자 권유 아님. 데이터 기준: {{ market_close_time }}
