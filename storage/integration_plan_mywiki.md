# [계획서] DailyNews - MyWiki 통합 운영안

## 1. 개요
본 문서는 `dailynews` 프로젝트의 결과물을 `mywiki` (Quartz 기반) 프로젝트에 병합하여 단일 웹사이트로 운영하기 위한 기술적 가이드를 담고 있습니다. 현재는 계획 단계이며, 실행 시 본 가이드를 따릅니다.

## 2. 통합 아키텍처 모델
- **데이터 공급원**: `dailynews` (Python/Gemini)
- **데이터 소비처**: `mywiki` (Quartz/TypeScript)
- **연결 매커니즘**: `dailynews`가 생성한 Markdown 파일을 `mywiki/content/news/` 폴더로 직접 출력

## 3. 핵심 수정 사항

### 3.1 DailyNews 리포트 템플릿 고도화
`templates/daily_report.md`에 Quartz가 인식할 수 있는 전용 Frontmatter를 추가합니다.

```markdown
---
title: "뉴스 브리핑 - {{ date[:10] }}"
date: {{ date[:10] }}
tags:
  - news
  - daily
---
# Daily News Brief
...
```

### 3.2 리포트 저장 로직 확장
`core/report.py`의 `save_report` 함수가 환경 변수에 정의된 `MYWIKI_PATH`가 있을 경우 해당 경로로도 파일을 복사하도록 수정합니다.

```python
# 예시 로직
def save_report(md_content):
    # 1. 기존 reports/ 폴더 저장
    # 2. (추가) MYWIKI_PATH가 설정되어 있다면 content/news/ 폴더로도 저장
    wiki_path = os.getenv("MYWIKI_CONTENT_PATH")
    if wiki_path:
        target_path = os.path.join(wiki_path, "news", filename)
        # 파일 저장 수행
```

### 3.3 MyWiki 레이아웃 조정
`mywiki`의 사이드바나 최근 게시물 섹션에서 `news` 태그를 가진 노트들이 잘 보이도록 `quartz.layout.ts`를 조정합니다.

## 4. 기대 효과
- **검색 통합**: Quartz의 고성능 검색 기능을 통해 과거 뉴스 히스토리 조회가 용이해집니다.
- **UI 일원화**: 두 개의 도메인을 관리할 필요 없이 하나의 프리미엄 디자인(Quartz)으로 통합됩니다.
- **지식 연결**: 뉴스 리포트 내의 키워드와 기존 위키 노트 간의 링크(`[[키워드]]`)가 활성화됩니다.

---
**작성일**: 2026-04-05
**상태**: 보류(계획 수립 완료)
