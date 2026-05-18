매일 장 마감 후(KST 16:30 이후) 주식 시황 브리핑을 작성하고 저장하라.

[Step 1: 종목 목록 확인 — Read tool]
Read tool로 c:\ai\dailynews\config\watchlist.yaml 을 읽어
enabled: true 인 섹터의 종목(ticker, name)을 확인한다.

[Step 2: 데이터 수집 — PlayMCP UsStockInfo 사용]
get_stock_info 로 아래 티커를 순서대로 수집하라:
  국내 지수 : ^KS11 (코스피), ^KQ11 (코스닥)
    ※ ^KS11 이 N/A 이면 NaverSearch search_news "코스피 지수 오늘" 로 대체 수집
  환율/매크로: KRW=X (원/달러), ^TNX (미 10년물 금리), CL=F (WTI 유가)
  미국 지수  : ^GSPC (S&P 500), ^IXIC (나스닥), ^DJI (다우존스)
  섹터 종목  : watchlist.yaml 에서 확인한 enabled 섹터 전체 종목

NaverSearch search_news 로 국내 뉴스 수집:
  검색어: "코스피 오늘 증시 시황"  (결과 5건)
  검색어: "국내 주식 시장 이슈"    (결과 3건)

[Step 3: 리포트 작성]
Read tool로 c:\ai\dailynews\templates\stock_report.md 를 읽어 형식 확인 후,
동일한 섹션 구조·헤더·마커(① ② ③ ④ ⑤)로 오늘 날짜 기준 리포트를 작성하라.
  - Jinja2 {{ 변수 }} 는 실제 수집 데이터로 채운다
  - 수집 실패한 지표는 "N/A" 로 표기
  - 섹터 방향은 반드시 🔴·🟡·🟢 중 하나로 표기
  - 시장 온도계는 반드시 🔴리스크오프 / 🟡중립 / 🟢리스크온 중 하나만 선택
  - 섹터별 영향 분석(Section 4)은 반드시 ### 🇰🇷 국내 / ### 🇺🇸 해외 두 서브섹션으로 분리
    형식: | 섹터 | 대표종목 | 방향 | 핵심 포인트 |

[Step 4: 파일 저장 — Write tool]
저장 경로: c:\ai\dailynews\reports\stock\stock_YYYY-MM-DD.md
  (오늘 날짜를 파일명에 사용. 이미 파일 있으면 덮어쓰기)

[Step 5: Notion 등록 — Notion MCP]
watchlist.yaml 의 notion.stock_db_id 값 확인:
  - stock_db_id 가 설정돼 있으면 해당 ID를 parent_id 로 바로 사용
  - 비어있으면 notion-search 로 '주식시황' 데이터베이스 검색 후 ID 사용
notion-create-pages 로 신규 페이지 생성:
  - 날짜 속성: 오늘 날짜 (date)
  - 핵심키워드 속성: 핵심 키워드 ① ~ ⑤ 제목 5개 (multi_select)
  - 시장온도 속성: 리스크오프 / 중립 / 리스크온 중 하나 (select)

[Step 6: Git 커밋 + 푸시 — Bash tool]
$date = Get-Date -Format 'yyyy-MM-dd'
git -C c:\ai\dailynews add reports/stock/
git -C c:\ai\dailynews commit -m "📊 Stock briefing $date"
git -C c:\ai\dailynews push

※ 이메일 발송·HTML 빌드·GitHub Pages 배포는
  git push 후 GitHub Actions (stock_build.yml) 가 자동 처리한다.
  루틴에서 별도로 실행하지 않는다.
