# 데일리 카드뉴스 — 구현계획서

> 작성일: 2026-05-18  
> 상태: **미시행 (Phase 2)**  
> 목적: 뉴스 이슈/키워드를 시각적 카드뉴스로 자동 생성하는 기능 계획

---

## 1. 시스템 목표

기존 뉴스 브리핑의 핵심 이슈 3개 + 트렌드 키워드 3~5개를 슬라이드형 카드뉴스 HTML로 자동 생성하여 웹사이트에 추가한다.

---

## 2. 현재 준비 완료 상태

Phase 1에서 이미 구조화 데이터 추출이 구현되어 있다.

### 2-1. 파싱 완료

`scripts/build_site.py`에 구현 완료:

```python
_parse_issues(text)
  → "### 핵심 이슈 TOP 3" 섹션에서 title, body, url, url_text 추출
  → issues_en, issues_ko 반환

_parse_keywords(text)
  → "### 주목할 트렌드 키워드" 섹션에서 keyword, desc 추출
  → keywords_en, keywords_ko 반환
```

### 2-2. 데이터 저장

`publish/reports-data.json`에 날짜별로 적재 중:

```json
{
  "2026-05-18": {
    "issues_en":   [{"title": "...", "body": "...", "url": "...", "url_text": "..."}],
    "issues_ko":   [...],
    "keywords_en": [{"keyword": "...", "desc": "..."}],
    "keywords_ko": [...]
  }
}
```

---

## 3. 구현 계획

### 3-1. 카드뉴스 HTML 템플릿

**가로 스크롤 슬라이드 방식** (순수 CSS, 라이브러리 불필요):

```html
<div class="card-news-container">
  <!-- 이슈 카드 (최대 3장) -->
  <div class="news-card type-issue">
    <div class="card-header">
      <div class="icon">🔥</div>
      <h3>{이슈 제목}</h3>
    </div>
    <div class="card-body">{이슈 요약}</div>
    <div class="card-footer">
      <a href="{url}">🔗 원문 보기</a>
    </div>
  </div>

  <!-- 키워드 카드 (최대 3장) -->
  <div class="news-card type-keyword">
    <div class="card-header">
      <div class="icon">🏷️</div>
      <h3>#{키워드}</h3>
    </div>
    <div class="card-body">{키워드 설명}</div>
    <div class="card-footer">주목할 트렌드</div>
  </div>
</div>
```

**CSS 핵심:**
```css
.card-news-container {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  gap: 16px;
  -webkit-overflow-scrolling: touch;
}
.news-card {
  flex: 0 0 300px;
  scroll-snap-align: center;
  border-radius: 16px;
}
.type-issue .card-header  { background: var(--color-blue); }
.type-keyword .card-header { background: var(--color-navy); }
```

### 3-2. Python 연동 로직

`scripts/build_site.py`에 추가할 함수:

```python
def generate_card_section_html(
    issues: list[dict],
    keywords: list[dict],
    lang: str = "ko"
) -> str:
    """
    issues/keywords 파싱 결과 → 카드뉴스 HTML 섹션 생성
    
    이슈 아이콘 매핑: 0→🔥, 1→📢, 2→💡
    키워드 아이콘 매핑: 0→🏷️, 1→📊, 2→🎯
    """
```

### 3-3. 출력 경로

```
publish/cardnews/
  YYYY-MM-DD.html   ← 날짜별 카드뉴스 페이지
  index.html        ← 최신 카드뉴스 (리다이렉트 또는 포함)
```

메인 페이지(`publish/index.html`)에도 카드뉴스 섹션 삽입.

### 3-4. 이메일 대응

이메일에서는 가로 스크롤이 Gmail에서 동작하지 않는다.  
이메일 본문에는 카드를 세로 나열로 렌더링하고, "웹에서 카드뉴스 보기" CTA 추가.

---

## 4. 구현 순서

### Step 1: 카드뉴스 HTML 생성 함수 (build_site.py)

- [ ] `generate_card_section_html(issues, keywords)` 구현
- [ ] 이슈 카드 최대 3장 + 키워드 카드 최대 3장
- [ ] URL이 있는 경우에만 "🔗 원문 보기" 링크 표시

### Step 2: 날짜별 카드뉴스 페이지 생성

- [ ] `build_cardnews_page(date, issues_ko, keywords_ko, issues_en, keywords_en)`
- [ ] `publish/cardnews/YYYY-MM-DD.html` 저장

### Step 3: 테마 연동

- [ ] `themes/base.py`에 `render_cardnews(ctx, theme_name)` 추가
- [ ] CSS 토큰 (`--color-blue`, `--color-navy` 등) 카드뉴스에 적용

### Step 4: 메인 페이지 연동

- [ ] `publish/index.html`에 최신 카드뉴스 섹션 삽입
- [ ] "카드뉴스 전체 보기" 링크 추가

### Step 5: 아카이브

- [ ] `publish/cardnews/archive.html` — 카드뉴스 날짜 목록

---

## 5. 데이터 의존성

카드뉴스는 `reports-data.json`의 데이터를 사용한다.  
이 데이터는 AI 프롬프트 구조(`### 핵심 이슈 TOP 3`, `### 주목할 트렌드 키워드`)에 의존한다.

**주의:** 프롬프트 헤더 구조 변경 시 파서(`_parse_issues`, `_parse_keywords`)와 카드뉴스 생성 함수를 함께 수정해야 한다.

---

## 6. 아이콘 매핑 계획

```python
ISSUE_ICONS = ["🔥", "📢", "💡"]
KEYWORD_ICONS = ["🏷️", "📊", "🎯"]

# 카테고리 기반 자동 매핑 (선택적 개선)
CATEGORY_ICONS = {
    "ai_ml":     "🤖",
    "technology": "💻",
    "korean_economy": "📈",
    "korean_tech": "🇰🇷",
}
```

---

## 7. 이메일 본문 대응

```python
# themes/base.py::render_email() 확장
def _card_email_section(issues, keywords):
    """이메일용 세로 나열 카드 섹션"""
    cards_html = ""
    for i, issue in enumerate(issues[:3]):
        cards_html += f"""
        <div style="background:#f0f4ff;border-radius:8px;padding:16px;margin-bottom:12px">
          <div style="font-weight:700;color:#1e3a5f">{ISSUE_ICONS[i]} {issue['title']}</div>
          <div style="font-size:.9rem;color:#334155;margin-top:8px">{issue['body'][:120]}...</div>
          {f'<a href="{issue["url"]}" style="color:#2563eb;font-size:.8rem">🔗 원문</a>' if issue.get('url') else ''}
        </div>"""
    return cards_html
```

---

## 8. 참고 사항

- 카드뉴스 기능은 새로운 MD 파일이 새 프롬프트 형식(`### h3`, URL 포함)으로 생성된 이후부터 유효하다.
- 기존 MD 파일(2026-05-18 이전)은 구조화 데이터가 없어 카드뉴스 생성 불가.
- 첫 유효 데이터 확인 후 구현 시작 권장.
- 상세 CSS 컴포넌트 설계: `config/theme_config.py`의 디자인 토큰 기준으로 작성.
