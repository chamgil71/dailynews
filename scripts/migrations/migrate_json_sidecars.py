# scripts/migrate_json_sidecars.py
"""
예전 news_*.md 파일들을 역으로 파싱하여
누락된 structured JSON 사이드카(news_*.json) 파일을 자동 생성하는 스크립트.
다양한 마크다운 리포트 양식(H3 헤더식, 1. **제목** 리스트식)을 모두 지원하도록 고도화.
"""
import glob
import json
import os
import re
from pathlib import Path

REPORTS_DIR = "reports"

def parse_issues(block: str) -> list[dict]:
    issues = []
    
    # ── 양식 A: ### 1. 제목 형태 파싱 ─────────────────────────────────────
    if "### 1." in block or "### 1 " in block:
        issue_blocks = re.split(r'###\s+(\d+)\.\s*', block)
        if len(issue_blocks) >= 2:
            for i in range(1, len(issue_blocks), 2):
                rank = int(issue_blocks[i])
                content_block = issue_blocks[i+1]
                
                lines = content_block.strip().splitlines()
                if not lines:
                    continue
                title = lines[0].strip()
                
                summary_lines = []
                sources = []
                for line in lines[1:]:
                    line_str = line.strip()
                    if not line_str:
                        continue
                    m_src = re.search(r'🔗\s*(?:주요\s*)?출처:\s*\[(.+?)\]\((.+?)\)', line_str)
                    if m_src:
                        sources.append({
                            "title": m_src.group(1).strip(),
                            "url": m_src.group(2).strip()
                        })
                    else:
                        summary_lines.append(line_str)
                        
                issues.append({
                    "rank": rank,
                    "title": title,
                    "summary": " ".join(summary_lines).strip(),
                    "category": "General",
                    "importance": "high" if rank <= 2 else "medium",
                    "sources": sources
                })
            return issues

    # ── 양식 B: 1. **제목** — 본문 형태 또는 들여쓰기 형태 파싱 ────────────
    # 1. **제목** — 요약 또는 1. **제목** [\n]    - 요약
    matches = re.finditer(r'(?:^|[\r\n])(\d+)\.\s*\*\*(.+?)\*\*([\s\S]*?)(?=[\r\n]\d+\.\s*\*\*|[\r\n]##|---|\Z)', block)
    for m in matches:
        rank = int(m.group(1))
        title_raw = m.group(2).strip()
        body_raw = m.group(3).strip()
        
        # 타이틀에서 양끝 공백 정리
        title = title_raw
        
        # 본문 요약 파싱
        # 대쉬(—)로 분리되어 있는 경우 예: 1. **제목** — 요약
        summary = ""
        sources = []
        
        if body_raw.startswith("—") or body_raw.startswith("-"):
            summary = body_raw.lstrip("—").lstrip("-").strip()
        else:
            # 줄별로 스캔하며 들여쓰기("- ") 제거 및 출처 추출
            summary_lines = []
            for line in body_raw.splitlines():
                line_str = line.strip()
                if not line_str:
                    continue
                # 출처 링크 추출 예: [주요 출처](url)
                m_src = re.search(r'\[(.+?)\]\((http.+?)\)', line_str)
                if m_src and ("출처" in line_str or "링크" in line_str or "http" in line_str):
                    sources.append({
                        "title": m_src.group(1).strip(),
                        "url": m_src.group(2).strip()
                    })
                else:
                    # 일반 들여쓰기 항목 리스트 가공
                    cleaned_line = re.sub(r'^[-\*\s\t]+', '', line_str)
                    summary_lines.append(cleaned_line)
            summary = " ".join(summary_lines).strip()
            
        # 만약 본문 요약이 처음에 대쉬로 쪼개져 있는 경우 추가 정제
        if "—" in title and not summary:
            t_parts = title.split("—", 1)
            title = t_parts[0].strip()
            summary = t_parts[1].strip()
            
        issues.append({
            "rank": rank,
            "title": title,
            "summary": summary,
            "category": "General",
            "importance": "high" if rank <= 2 else "medium",
            "sources": sources
        })
        
    return issues

def parse_trends(block: str) -> list[dict]:
    trends = []
    # 1. **[keyword]** 형태 파싱
    trend_blocks = re.findall(r'(?:^|[\r\n])(?:[-\*\d\.\s]+)?\*\*(.+?)\*\*[\s:]*([\s\S]*?)(?=(?:[\r\n](?:[-\*\d\.\s]+)?\*\*|---|\Z))', block)
    for i, (keyword, content) in enumerate(trend_blocks, 1):
        desc = content.replace("   ", "").strip()
        # 대쉬나 불필요한 들여쓰기 제거
        desc = re.sub(r'^[-\*\s\t\:]+', '', desc)
        trends.append({
            "keyword": keyword.strip(),
            "description": desc,
            "category": "technology"
        })
    return trends

def parse_section(section_text: str) -> dict:
    # 핵심 이슈 TOP 3 블록
    m_issues = re.search(r'##\s*핵심\s*이슈\s*(?:TOP\s*\d+)?([\s\S]*?)(?=##\s*주목할\s*트렌드|---|\Z)', section_text)
    issues = parse_issues(m_issues.group(1)) if m_issues else []
    
    # 주목할 트렌드 블록
    m_trends = re.search(r'##\s*주목할\s*트렌드([\s\S]*?)(?=---|\Z)', section_text)
    trends = parse_trends(m_trends.group(1)) if m_trends else []
    
    if not issues and not trends:
        return {}
        
    return {
        "lang": "ko",
        "issues": issues,
        "trends": trends,
        "category_stats": {}
    }

def migrate_file(md_path: Path):
    json_path = md_path.with_suffix(".json")
    
    raw = md_path.read_text(encoding="utf-8")
    
    # 글로벌 및 국내 분석 영역 쪼개기
    # 🌐 Global News Analysis
    en_match = re.search(r'##\s*🌐\s*Global\s*News\s*Analysis\s*([\s\S]*?)(?=---\s*[\r\n]+##\s*🇰🇷|##\s*📋|\Z)', raw)
    # 🇰🇷 국내 뉴스 분석
    ko_match = re.search(r'##\s*🇰🇷\s*국내\s*뉴스\s*분석\s*([\s\S]*?)(?=##\s*📋|\Z)', raw)
    
    en_data = parse_section(en_match.group(1)) if en_match else {}
    ko_data = parse_section(ko_match.group(1)) if ko_match else {}
    
    payload = {
        "en": en_data,
        "ko": ko_data
    }
    
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  + Re-created/Updated: {json_path.name}")
    return True

def main():
    print("[Migration] Scanning reports/ news_*.md files to rebuild structured JSON...")
    md_files = sorted(glob.glob(f"{REPORTS_DIR}/news_*.md"))
    created_count = 0
    
    for f in md_files:
        md_path = Path(f)
        if migrate_file(md_path):
            created_count += 1
            
    print(f"[Done] Rebuilt {created_count} structured JSON sidecar files with robust parser.")

if __name__ == "__main__":
    main()
