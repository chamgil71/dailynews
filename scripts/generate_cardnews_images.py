"""
카드뉴스 → 1080×1080 PNG 이미지 직접 생성 (Pillow)
브라우저 없이 Python만으로 인스타용 이미지 생성

사용법:
  python scripts/generate_cardnews_images.py                    # 최신 날짜
  python scripts/generate_cardnews_images.py --date 2026-06-04  # 특정 날짜

출력: publish/cardnews/YYYY-MM-DD-{n}.png  (n: 0=커버, 1~3=이슈, 4=트렌드)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

CARDNEWS_DIR = Path(_ROOT, "publish", "cardnews")
CARD_SIZE    = 1080

# ── 폰트 우선순위 (CJK 지원 폰트) ─────────────────────────────────────────────
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",  # 일본/한국 Gothic
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",         # CJK 범용
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",    # IPA Gothic
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",           # macOS
    "C:/Windows/Fonts/malgun.ttf",                          # Windows
]

# ── 색상 팔레트 ───────────────────────────────────────────────────────────────
BG_TOP     = (15,  23, 42)      # #0f172a
BG_BOTTOM  = (17,  24, 59)      # #111838
CARD_BG    = (255, 255, 255, 13) # rgba 0.05
ACCENT     = (56, 189, 248)     # #38bdf8
TEXT_WHITE = (248, 250, 252)    # #f8fafc
TEXT_GRAY  = (148, 163, 184)    # #94a3b8
TEXT_MUTED = (71,  85, 105)     # #475569

ISSUE_COLORS = [
    (245, 158, 11),  # amber  #f59e0b
    (129, 140, 248), # indigo #818cf8
    (52,  211, 153), # emerald #34d399
]
TREND_COLOR = (56, 189, 248)     # sky #38bdf8

ISSUE_ICONS   = ["🔥", "📢", "💡"]
TREND_ICONS   = ["📊", "🎯", "⚡"]
CATEGORY_LABELS = {
    "ai_ml":          "AI·ML",
    "technology":     "기술",
    "economy":        "경제",
    "global_news":    "글로벌",
    "korean_news":    "국내",
    "korean_economy": "한국경제",
    "korean_tech":    "한국기술",
    "security":       "보안",
    "startup":        "스타트업",
}


# ── 폰트 로더 ─────────────────────────────────────────────────────────────────
def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_CANDIDATES
    if bold:
        bold_candidates = [p.replace("-Regular", "-Bold").replace(".ttf", "-Bold.ttf")
                           for p in candidates] + candidates
        candidates = bold_candidates

    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default(size=size)


# ── 그래디언트 배경 ────────────────────────────────────────────────────────────
def _make_background() -> Image.Image:
    img  = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
    draw = ImageDraw.Draw(img)

    # 상단 → 하단 세로 그래디언트
    for y in range(CARD_SIZE):
        t  = y / CARD_SIZE
        r  = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g  = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b  = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (CARD_SIZE, y)], fill=(r, g, b))

    # 오른쪽 상단 청색 글로우
    glow = Image.new("RGBA", (CARD_SIZE, CARD_SIZE), (0, 0, 0, 0))
    gd   = ImageDraw.Draw(glow)
    for radius in range(320, 0, -4):
        alpha = int(18 * (1 - radius / 320))
        gd.ellipse([CARD_SIZE - radius, -radius // 2,
                    CARD_SIZE + radius, radius * 3 // 2],
                   fill=(56, 189, 248, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    return img


# ── 유틸: 텍스트 줄바꿈 ────────────────────────────────────────────────────────
def _wrap_text(text: str, font: ImageFont.FreeTypeFont,
               max_width: int) -> list[str]:
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        words = list(paragraph)  # 글자 단위 (한글)
        # 그러나 영어 단어는 띄어쓰기 기준으로 분리
        # 혼합 처리: 공백 기준 토큰으로 먼저 처리
        tokens = paragraph.split(" ")
        current = ""
        for tok in tokens:
            test = (current + " " + tok).strip()
            bbox = font.getbbox(test)
            if bbox[2] - bbox[0] > max_width:
                if current:
                    lines.append(current)
                    current = tok
                else:
                    # 단어 하나가 너무 길면 글자 단위 분리
                    for ch in tok:
                        test2 = current + ch
                        bbox2 = font.getbbox(test2)
                        if bbox2[2] - bbox2[0] > max_width:
                            lines.append(current)
                            current = ch
                        else:
                            current = test2
            else:
                current = test
        if current:
            lines.append(current)
    return lines


def _text_h(font: ImageFont.FreeTypeFont, lines: list[str],
            line_gap: int = 8) -> int:
    if not lines:
        return 0
    h = sum(font.getbbox(l)[3] - font.getbbox(l)[1] for l in lines)
    return h + line_gap * (len(lines) - 1)


def _draw_text_wrapped(draw: ImageDraw.Draw, text: str, x: int, y: int,
                       font: ImageFont.FreeTypeFont, fill, max_width: int,
                       line_gap: int = 8) -> int:
    """줄바꿈 처리 후 텍스트 그리기. 마지막 줄 아래 y 반환."""
    lines = _wrap_text(text, font, max_width)
    cy = y
    for line in lines:
        draw.text((x, cy), line, font=font, fill=fill)
        lh = font.getbbox(line)[3] - font.getbbox(line)[1]
        cy += lh + line_gap
    return cy


def _rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int,
                  fill=None, outline=None, width: int = 1) -> None:
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                            fill=fill, outline=outline, width=width)


# ── 공통 하단 Footer ──────────────────────────────────────────────────────────
def _draw_footer(draw: ImageDraw.Draw, date_str: str,
                 card_idx: int, total_cards: int) -> None:
    # 구분선
    draw.line([(64, CARD_SIZE - 88), (CARD_SIZE - 64, CARD_SIZE - 88)],
              fill=(255, 255, 255, 20), width=1)

    font_sm = _load_font(22)

    # 왼쪽: 사이트
    draw.text((72, CARD_SIZE - 62), "ms-dailynews.vercel.app",
              font=font_sm, fill=ACCENT)

    # 가운데: 점 인디케이터
    dot_count = total_cards
    dot_w     = dot_count * 14 + max(0, dot_count - 1) * 8
    cx        = (CARD_SIZE - dot_w) // 2
    for i in range(dot_count):
        is_active = i == card_idx
        if is_active:
            draw.rounded_rectangle([cx, CARD_SIZE - 56, cx + 28, CARD_SIZE - 46],
                                   radius=5, fill=ACCENT)
            cx += 36
        else:
            draw.ellipse([cx, CARD_SIZE - 56, cx + 10, CARD_SIZE - 46],
                         fill=(255, 255, 255, 60))
            cx += 18

    # 오른쪽: 날짜
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        label = f"{dt.month}/{dt.day}"
    except ValueError:
        label = date_str
    bbox = font_sm.getbbox(label)
    tw   = bbox[2] - bbox[0]
    draw.text((CARD_SIZE - 72 - tw, CARD_SIZE - 62), label,
              font=font_sm, fill=TEXT_MUTED)


# ── 카드 0: 커버 ──────────────────────────────────────────────────────────────
def make_cover(date_str: str, issues: list[dict],
               card_idx: int, total_cards: int) -> Image.Image:
    img  = _make_background()
    draw = ImageDraw.Draw(img, "RGBA")

    # 로고 배지 (그래디언트 직사각형)
    lx, ly = 72, 72
    _rounded_rect(draw, (lx, ly, lx + 72, ly + 72), radius=16,
                  fill=(38, 99, 235))  # blue-600
    font_logo = _load_font(30, bold=True)
    draw.text((lx + 14, ly + 18), "AI", font=font_logo, fill=TEXT_WHITE)

    font_site  = _load_font(34, bold=True)
    font_sub   = _load_font(22)
    draw.text((lx + 84, ly + 10), "AI News Brief",
              font=font_site, fill=TEXT_WHITE)
    draw.text((lx + 84, ly + 48), "매일 아침 AI가 정리하는 핵심 뉴스",
              font=font_sub, fill=TEXT_GRAY)

    # 날짜
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        display = f"{dt.year}년 {dt.month}월 {dt.day}일 ({weekdays[dt.weekday()]})"
    except ValueError:
        display = date_str

    font_date = _load_font(30)
    draw.text((72, 184), display, font=font_date, fill=ACCENT)

    # 구분선
    draw.line([(72, 230), (CARD_SIZE - 72, 230)], fill=(*ACCENT, 100), width=2)

    # 헤드라인 레이블
    font_label = _load_font(24)
    draw.text((72, 254), "오늘의 핵심 이슈", font=font_label, fill=TEXT_MUTED)

    # 이슈 카드
    y = 300
    font_issue = _load_font(28, bold=True)
    for i, issue in enumerate(issues[:3]):
        color = ISSUE_COLORS[i]
        icon  = ISSUE_ICONS[i]
        title = issue.get("title", "")

        # 카드 배경
        card_h = 110
        _rounded_rect(draw, (72, y, CARD_SIZE - 72, y + card_h), radius=14,
                      fill=(255, 255, 255, 13),
                      outline=(255, 255, 255, 25), width=1)

        # 아이콘 (텍스트)
        draw.text((96, y + 34), icon, font=font_issue, fill=color)

        # 제목 (말줄임)
        max_w   = CARD_SIZE - 72 - 96 - 48 - 24
        lines   = _wrap_text(title, font_issue, max_w)
        display_title = lines[0][:28] + "..." if len(lines) > 1 or len(lines[0]) > 28 else lines[0]
        draw.text((144, y + 30), display_title, font=font_issue, fill=TEXT_WHITE)

        y += card_h + 16

    # 해시태그
    font_tag  = _load_font(22)
    draw.text((72, y + 8), "#AI뉴스  #테크  #데일리브리핑  #인공지능",
              font=font_tag, fill=TEXT_MUTED)

    _draw_footer(draw, date_str, card_idx, total_cards)
    return img


# ── 카드 1~3: 이슈 상세 ──────────────────────────────────────────────────────
def make_issue_card(date_str: str, issue: dict, rank: int,
                    card_idx: int, total_cards: int) -> Image.Image:
    img  = _make_background()
    draw = ImageDraw.Draw(img, "RGBA")

    color = ISSUE_COLORS[rank - 1]
    icon  = ISSUE_ICONS[rank - 1]
    cat   = CATEGORY_LABELS.get(issue.get("category", ""), issue.get("category", ""))
    title   = issue.get("title", "")
    summary = issue.get("summary", "")
    src_cnt = len(issue.get("sources", []))

    # 랭크 뱃지
    font_rank  = _load_font(26, bold=True)
    font_icon  = _load_font(40)
    font_cat   = _load_font(22)
    font_title = _load_font(38, bold=True)
    font_sum   = _load_font(27)
    font_src   = _load_font(22)

    # 아이콘
    draw.text((72, 72), icon, font=font_icon, fill=color)

    # 핵심 이슈 N
    draw.text((128, 82), f"핵심 이슈 {rank}", font=font_rank, fill=color)

    # 카테고리 뱃지
    cat_bbox = font_cat.getbbox(cat)
    cat_w    = cat_bbox[2] - cat_bbox[0] + 32
    _rounded_rect(draw, (CARD_SIZE - 72 - cat_w, 82, CARD_SIZE - 72, 82 + 34),
                  radius=17, fill=(255, 255, 255, 25))
    draw.text((CARD_SIZE - 72 - cat_w + 16, 84), cat,
              font=font_cat, fill=(203, 213, 225))

    # 구분선
    draw.rectangle([72, 140, 72 + 80, 145], fill=color)

    # 제목
    y = 168
    y = _draw_text_wrapped(draw, title, 72, y, font_title, TEXT_WHITE,
                           CARD_SIZE - 144, line_gap=10)
    y += 28

    # 본문 구분선 얇게
    draw.line([(72, y), (CARD_SIZE - 72, y)],
              fill=(255, 255, 255, 20), width=1)
    y += 24

    # 요약
    y = _draw_text_wrapped(draw, summary, 72, y, font_sum, TEXT_GRAY,
                           CARD_SIZE - 144, line_gap=10)
    y += 28

    # 출처
    draw.text((72, y), f"📎 출처 {src_cnt}개",
              font=font_src, fill=TEXT_MUTED)

    _draw_footer(draw, date_str, card_idx, total_cards)
    return img


# ── 카드 4: 트렌드 ────────────────────────────────────────────────────────────
def make_trends_card(date_str: str, trends: list[dict],
                     card_idx: int, total_cards: int) -> Image.Image:
    img  = _make_background()
    draw = ImageDraw.Draw(img, "RGBA")

    font_h   = _load_font(36, bold=True)
    font_kw  = _load_font(30, bold=True)
    font_desc = _load_font(25)
    font_icon = _load_font(34)

    # 헤더
    draw.text((72, 72), "📈", font=font_icon, fill=ACCENT)
    draw.text((124, 80), "주목할 트렌드 키워드", font=font_h, fill=TEXT_WHITE)

    # 구분선
    draw.line([(72, 138), (CARD_SIZE - 72, 138)], fill=(*ACCENT, 80), width=2)

    y = 172
    for i, trend in enumerate(trends[:3]):
        kw   = trend.get("keyword", "")
        desc = trend.get("description", "")
        icon = TREND_ICONS[i]

        # 트렌드 카드 배경
        # 높이 계산: 키워드 1줄 + 설명 ~2줄
        desc_lines = _wrap_text(desc, font_desc, CARD_SIZE - 200)
        desc_h = _text_h(font_desc, desc_lines, line_gap=8)
        card_h = 62 + desc_h + 30
        card_h = max(card_h, 120)

        _rounded_rect(draw,
                      (72, y, CARD_SIZE - 72, y + card_h),
                      radius=12,
                      fill=(255, 255, 255, 13),
                      outline=(255, 255, 255, 20), width=1)
        # 좌측 액센트 바
        draw.rectangle([72, y, 76, y + card_h], fill=TREND_COLOR)

        # 아이콘 + 키워드
        draw.text((100, y + 18), icon, font=font_desc, fill=ACCENT)
        draw.text((140, y + 14), f"#{kw}", font=font_kw, fill=ACCENT)

        # 설명
        cy = y + 58
        for line in desc_lines:
            draw.text((100, cy), line, font=font_desc, fill=TEXT_GRAY)
            lh = font_desc.getbbox(line)[3] - font_desc.getbbox(line)[1]
            cy += lh + 8

        y += card_h + 20

    _draw_footer(draw, date_str, card_idx, total_cards)
    return img


# ── 메인 생성 함수 ────────────────────────────────────────────────────────────
def generate_images(date_str: str) -> list[Path]:
    index_path = CARDNEWS_DIR / "cardnews-data.json"
    if not index_path.exists():
        raise FileNotFoundError("cardnews-data.json 없음. build_cardnews.py 먼저 실행.")

    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = next((e for e in index if e["date"] == date_str), None)
    if entry is None:
        raise ValueError(f"{date_str} 카드뉴스 인덱스 없음")

    # reports-data.json에서 structured 데이터 로드
    reports_path = Path(_ROOT, "publish", "reports-data.json")
    reports = json.loads(reports_path.read_text(encoding="utf-8"))
    report  = next((r for r in reports if r["date"] == date_str), None)
    if report is None:
        raise ValueError(f"{date_str} reports-data.json 항목 없음")

    ko      = report.get("structured", {}).get("ko", {})
    issues  = ko.get("issues", [])[:3]
    trends  = ko.get("trends", [])[:3]

    total_cards = 1 + len(issues) + (1 if trends else 0)
    output_paths: list[Path] = []

    # 커버
    img = make_cover(date_str, issues, 0, total_cards)
    out = CARDNEWS_DIR / f"{date_str}-0.png"
    img.save(str(out), "PNG", optimize=True)
    output_paths.append(out)
    print(f"  + {out.name}")

    # 이슈 카드
    for i, issue in enumerate(issues):
        img = make_issue_card(date_str, issue, i + 1, i + 1, total_cards)
        out = CARDNEWS_DIR / f"{date_str}-{i+1}.png"
        img.save(str(out), "PNG", optimize=True)
        output_paths.append(out)
        print(f"  + {out.name}")

    # 트렌드 카드
    if trends:
        img = make_trends_card(date_str, trends, 1 + len(issues), total_cards)
        out = CARDNEWS_DIR / f"{date_str}-{1+len(issues)}.png"
        img.save(str(out), "PNG", optimize=True)
        output_paths.append(out)
        print(f"  + {out.name}")

    return output_paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD (미입력 시 최신)")
    args = parser.parse_args()

    if args.date:
        date_str = args.date
    else:
        index_path = CARDNEWS_DIR / "cardnews-data.json"
        if not index_path.exists():
            print("cardnews-data.json 없음. build_cardnews.py 먼저 실행하세요.")
            sys.exit(1)
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if not index:
            print("카드뉴스 인덱스가 비어 있습니다.")
            sys.exit(1)
        date_str = index[0]["date"]

    print(f"[generate-images] {date_str}")
    paths = generate_images(date_str)
    print(f"  총 {len(paths)}개 이미지 생성 완료")


if __name__ == "__main__":
    main()
