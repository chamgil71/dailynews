# 🤖 AI Issue Weekly — {{ period }}

생성일시: {{ generated_at }} | 기준: 주간 AI 동향 분석 리포트

인공지능 생태계의 주요 블로그, 공식 미디어, cs.AI arXiv 논문 및 주요 빅테크 종목의 변동을 종합 분석한 주간 기술/산업 보고서입니다.

---

## ■ 이번 주 AI 이슈 TOP 10

이번 주 전 세계 AI 산업에서 가장 중요하게 대두된 10대 핵심 사건 및 동향 분석 목록입니다.

{% for item in top10 -%}
### {{ item.rank }}위. [{{ item.category.upper() }}] {{ item.title }}
* **중요도**: {% for i in range(item.importance) %}★{% endfor %}{% for i in range(5 - item.importance) %}☆{% endfor %}
* **요약**: {{ item.summary }}
{% if item.sources -%}
* **주요 출처**: {% for src in item.sources %}[{{ src.name }}]({{ src.url }}){% if not loop.last %}, {% endif %}{% endfor %}
{%- endif %}

{% endfor %}
---

## ■ 주요 이슈 심층 분석 (TOP 3)

이번 주 가장 높은 임팩트를 지닌 3대 핵심 이슈의 배경, 핵심 내용, 산업적 파급 효과 분석 리포트입니다.

{% for issue in top10[:3] -%}
{% set detail = {} %}
{% for d in top3_detail %}
  {% if d.rank == issue.rank %}
    {% set _ = detail.update(d) %}
  {% endif %}
{% endfor %}
### 🌟 [이슈 {{ issue.rank }}위] {{ issue.title }}

#### 1) 이슈 배경
{{ detail.background or "관련 배경 정보 분석 중..." }}

#### 2) 핵심 발표 및 세부 내용
{{ detail.core_content or "세부 상세 내역 취합 중..." }}

#### 3) 인공지능 생태계 및 산업적 의의
{{ detail.industrial_impact or "산업적 파급 분석 중..." }}

#### 4) 향후 1~2년 내 미래 파급 효과 및 예측
{{ detail.future_effect or "미래 파급 예측 분석 중..." }}

---
{% endfor %}

{{ company_trends }}

---

## 💡 이번 주 AI 실용 팁 (Weekly Tip)

독자가 현업 또는 비즈니스에 즉각 도입해 볼 수 있는 구체적인 AI 도구 및 프롬프트 가이드입니다.

{% for tip in weekly_tips -%}
### 🛠️ [{{ tip.difficulty }}] {{ tip.title }}
* **대상 도구**: `{{ tip.tool_name }}`
* **실행 가이드**:
{{ tip.guide }}
* **실용 프롬프트 / 설정 템플릿**:
```text
{{ tip.prompt_example }}
```

{% endfor %}
---

## 📈 AI 투자 및 빅테크 펀딩 동향

주요 AI 빅테크 테마주의 주간(7일간) 누적 주가 등락 스냅샷입니다.

| 티커 | 종목명 | 주간 등락률 | 상세 가격 정보 및 특이사항 |
|:---:|:---|:---:|:---|
{% for stock in stock_snapshots -%}
| **{{ stock.ticker }}** | {{ stock.name }} | **{{ stock.weekly_change_pct | weekly_change_pct }}%** | {{ stock.note }} |
{% endfor %}

---

## 🔬 주목 논문 Pick (Research Radar)

이번 주 cs.AI cs.LG cs.CL 분야에 게재된 수백 편의 아카이브 논문 중 실무 임팩트와 아키텍처적 유용성을 고려하여 엄선한 주목 논문입니다.

{% for paper in paper_picks -%}
### 📄 {{ paper.title }}
* **저자진**: {{ paper.authors }}
* **한줄 요약**: *{{ paper.one_liner }}*
* **CTO 실무 적용 가이드**: 
  {{ paper.practical_note }}
* **원문 링크**: [arXiv: {{ paper.title[:30] }}...]({{ paper.url }})

{% endfor %}
---

{{ next_week_outlook }}

---
※ 본 보고서는 인공지능에 의해 정기 자동 취합 및 분석된 보고서입니다.
