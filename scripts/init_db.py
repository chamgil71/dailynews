# scripts/init_db.py
"""
기존 reports/*.md 파일로 storage/news_db.xlsx 초기화
실행: python scripts/init_db.py
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import append_news

REPORTS_DIR = "reports"

LABEL_MAP = {
    "국내 종합":      ("korean_general",      "ko"),
    "국내 경제":      ("korean_economy",       "ko"),
    "국내 증권·투자": ("korean_stock",          "ko"),
    "국내 IT·기술":   ("korean_tech",           "ko"),
    "국내 부동산":    ("korean_realestate",     "ko"),
    "국내 정치":      ("korean_politics",       "ko"),
    "국제 (한국어)":  ("korean_international",  "ko"),
    "글로벌 종합":    ("global_news",           "en"),
    "글로벌 기술":    ("technology",            "en"),
    "AI·ML":          ("ai_ml",                 "en"),
    "글로벌 경제":    ("economy",               "en"),
    "스타트업·VC":    ("startup",               "en"),
}


def parse_md(md_path: str, date_str: str) -> list:
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()

    items = []
    for line in raw.splitlines():
        m = re.match(r'^- \*\*\[(.+?)\]\*\* \[(.+?)\]\((.+?)\)', line)
        if not m:
            continue
        label, title, link = m.group(1), m.group(2), m.group(3)
        category, lang = LABEL_MAP.get(label, ("", "ko"))
        items.append({
            "category": category,
            "label":    label,
            "lang":     lang,
            "title":    title,
            "link":     link,
            "published": "",
            "summary":   "",
        })
    return items


def main():
    md_files = sorted(glob.glob(f"{REPORTS_DIR}/news_*.md"))
    if not md_files:
        print("⚠ reports/ 에 MD 파일이 없습니다.")
        return

    total = 0
    for md_path in md_files:
        date_str = os.path.basename(md_path).replace("news_", "").replace(".md", "")
        items = parse_md(md_path, date_str)
        added = append_news(items, date_str)
        print(f"  {date_str}: {added}건 추가")
        total += added

    print(f"\n✅ 초기화 완료: 총 {total}건 → storage/news_db.xlsx")


if __name__ == "__main__":
    main()
