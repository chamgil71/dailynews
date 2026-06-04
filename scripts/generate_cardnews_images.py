"""
카드뉴스 HTML → 1080×1080 PNG 이미지 생성

기본: Playwright (헤드리스 Chromium, Google Fonts 로드 → 완벽한 Noto Sans KR)
폴백: Pillow (브라우저 없는 환경용, 폰트 품질 낮을 수 있음)

GitHub Actions 요구사항 (cardnews.yml에서 처리):
  sudo apt-get install -y fonts-noto-cjk
  pip install playwright
  playwright install chromium --with-deps

사용법:
  python scripts/generate_cardnews_images.py                    # 최신 날짜
  python scripts/generate_cardnews_images.py --date 2026-06-04  # 특정 날짜
  python scripts/generate_cardnews_images.py --backend pillow   # 폴백 강제
"""
from __future__ import annotations

import argparse
import http.server
import json
import re
import socketserver
import sys
import threading
import time
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

CARDNEWS_DIR = Path(_ROOT, "publish", "cardnews")
PUBLISH_DIR  = Path(_ROOT, "publish")
CARD_SIZE    = 1080


# ── 로컬 HTTP 서버 (Google Fonts CDN 로드를 위해 http:// 필요) ──────────────────
def _find_free_port() -> int:
    import socket
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _start_local_server(directory: Path, port: int) -> None:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)
        def log_message(self, fmt, *args):
            pass

    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        httpd.serve_forever()


# ── Playwright 백엔드 ──────────────────────────────────────────────────────────
def generate_playwright(date_str: str, html_path: Path) -> list[Path]:
    html_content = html_path.read_text(encoding="utf-8")
    total_cards  = len(re.findall(r'<div class="card"', html_content))
    if total_cards == 0:
        raise ValueError(f"카드를 찾을 수 없음: {html_path}")

    port   = _find_free_port()
    thread = threading.Thread(
        target=_start_local_server, args=(PUBLISH_DIR, port), daemon=True
    )
    thread.start()
    time.sleep(0.4)

    from playwright.sync_api import sync_playwright

    output_paths: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--disable-dev-shm-usage", "--font-render-hinting=none"]
        )
        ctx = browser.new_context(
            viewport={"width": CARD_SIZE, "height": CARD_SIZE},
            device_scale_factor=1,
        )
        page = ctx.new_page()

        for i in range(total_cards):
            url = f"http://127.0.0.1:{port}/cardnews/{date_str}.html?card={i}"
            page.goto(url, wait_until="networkidle", timeout=30_000)
            page.evaluate("() => document.fonts.ready")
            # 폰트 렌더링 안정화 대기
            page.wait_for_timeout(300)

            out = CARDNEWS_DIR / f"{date_str}-{i}.png"
            page.screenshot(
                path=str(out),
                clip={"x": 0, "y": 0, "width": CARD_SIZE, "height": CARD_SIZE}
            )
            output_paths.append(out)
            print(f"  + {out.name}")

        browser.close()

    return output_paths


# ── Pillow 폴백 백엔드 ────────────────────────────────────────────────────────
def generate_pillow(date_str: str) -> list[Path]:
    from PIL import Image, ImageDraw, ImageFont

    FONT_CANDIDATES = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansKR-Regular.otf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    ]

    def _font(size: int) -> ImageFont.FreeTypeFont:
        for p in FONT_CANDIDATES:
            if Path(p).exists():
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default(size=size)

    def _bg() -> Image.Image:
        img  = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
        draw = ImageDraw.Draw(img)
        for y in range(CARD_SIZE):
            t = y / CARD_SIZE
            r = int(10 + 7 * t); g = int(15 + 12 * t); b = int(30 + 28 * t)
            draw.line([(0, y), (CARD_SIZE, y)], fill=(r, g, b))
        # 상단 컬러 바
        draw.rectangle([0, 0, CARD_SIZE, 5], fill=(56, 189, 248))
        return img

    def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
        lines, cur = [], ""
        for tok in text.split(" "):
            test = (cur + " " + tok).strip()
            if font.getbbox(test)[2] > max_w and cur:
                lines.append(cur); cur = tok
            else:
                cur = test
        if cur: lines.append(cur)
        return lines or [text]

    def _draw_text(draw, text, x, y, font, fill, max_w, gap=12):
        cy = y
        for line in _wrap(text, font, max_w):
            draw.text((x, cy), line, font=font, fill=fill)
            cy += font.getbbox(line)[3] - font.getbbox(line)[1] + gap
        return cy

    reports   = json.loads(Path(_ROOT, "publish", "reports-data.json").read_text())
    report    = next((r for r in reports if r["date"] == date_str), None)
    if not report:
        raise ValueError(f"reports-data.json에 {date_str} 없음")

    ko     = report.get("structured", {}).get("ko", {})
    issues = ko.get("issues", [])[:3]
    trends = ko.get("trends", [])[:3]
    total  = 1 + len(issues) + (1 if trends else 0)

    ACCENT  = (56, 189, 248)
    WHITE   = (248, 250, 252)
    GRAY    = (148, 163, 184)
    MUTED   = (71, 85, 105)
    ICOLORS = [(245, 158, 11), (129, 140, 248), (52, 211, 153)]

    # 날짜 포맷
    try:
        from datetime import datetime as dt
        d = dt.strptime(date_str, "%Y-%m-%d")
        wds = ["월","화","수","목","금","토","일"]
        display_date = f"{d.year}년 {d.month}월 {d.day}일 ({wds[d.weekday()]})"
    except Exception:
        display_date = date_str

    def footer(img, card_idx):
        draw = ImageDraw.Draw(img, "RGBA")
        draw.line([(72, CARD_SIZE-90), (CARD_SIZE-72, CARD_SIZE-90)],
                  fill=(255,255,255,18), width=1)
        fs = _font(24)
        draw.text((80, CARD_SIZE-66), "ms-dailynews.vercel.app", font=fs, fill=ACCENT)
        tw = fs.getbbox(display_date[:5])[2]
        draw.text((CARD_SIZE-80-fs.getbbox(display_date[:5])[2], CARD_SIZE-66),
                  display_date[:5], font=fs, fill=MUTED)
        # dots
        cx = CARD_SIZE//2 - (total*18)//2
        for i in range(total):
            if i == card_idx:
                draw.rounded_rectangle([cx,CARD_SIZE-68,cx+30,CARD_SIZE-57], radius=5, fill=ACCENT)
                cx += 38
            else:
                draw.ellipse([cx,CARD_SIZE-68,cx+11,CARD_SIZE-57], fill=(255,255,255,50))
                cx += 19

    output_paths = []

    # Cover
    img  = _bg()
    draw = ImageDraw.Draw(img, "RGBA")
    fL   = _font(40); fM = _font(32); fS = _font(26)
    draw.text((80, 70), "AI", font=fL, fill=(255,255,255))
    draw.text((140, 76), "AI News Brief", font=_font(40), fill=WHITE)
    draw.text((140, 126), "매일 아침 AI가 정리하는 핵심 뉴스", font=_font(24), fill=GRAY)
    draw.text((80, 196), display_date, font=fM, fill=ACCENT)
    draw.rectangle([80, 246, 80+200, 249], fill=ACCENT)
    draw.text((80, 268), "오늘의 핵심 이슈", font=_font(26), fill=MUTED)
    y = 316
    for i, issue in enumerate(issues):
        ic = ICOLORS[i]; icons = ["🔥","📢","💡"]
        h = 104
        draw.rounded_rectangle([80,y,CARD_SIZE-80,y+h], radius=14, fill=(255,255,255,12),
                                outline=(255,255,255,22), width=1)
        draw.text((104, y+30), icons[i], font=_font(32), fill=ic)
        t = issue.get("title","")[:26]+"…" if len(issue.get("title",""))>26 else issue.get("title","")
        draw.text((155, y+26), t, font=_font(30), fill=WHITE)
        y += h + 18
    draw.text((80, y+8), "#AI뉴스  #테크  #데일리브리핑", font=_font(24), fill=MUTED)
    footer(img, 0)
    out = CARDNEWS_DIR / f"{date_str}-0.png"
    img.save(str(out), "PNG"); output_paths.append(out); print(f"  + {out.name}")

    # Issues
    for i, issue in enumerate(issues):
        img  = _bg()
        draw = ImageDraw.Draw(img, "RGBA")
        ic   = ICOLORS[i]; icons = ["🔥","📢","💡"]
        draw.text((80,72), icons[i], font=_font(44), fill=ic)
        draw.text((144,82), f"핵심 이슈 {i+1}", font=_font(30), fill=ic)
        cat = {"ai_ml":"AI·ML","technology":"기술","economy":"경제",
               "korean_economy":"한국경제","korean_tech":"한국기술"}.get(issue.get("category",""), issue.get("category",""))
        draw.text((CARD_SIZE-80-_font(22).getbbox(cat)[2]-20, 90), cat, font=_font(22), fill=GRAY)
        draw.rectangle([80,152,152,157], fill=ic)
        y = _draw_text(draw, issue.get("title",""), 80, 180, _font(46), WHITE, CARD_SIZE-160, gap=14)
        y += 22
        draw.line([(80,y),(CARD_SIZE-80,y)], fill=(255,255,255,18), width=1); y+=24
        y = _draw_text(draw, issue.get("summary",""), 80, y, _font(29), GRAY, CARD_SIZE-160, gap=12)
        draw.text((80,y+20), f"📎 출처 {len(issue.get('sources',[]))}개", font=_font(24), fill=MUTED)
        footer(img, i+1)
        out = CARDNEWS_DIR / f"{date_str}-{i+1}.png"
        img.save(str(out), "PNG"); output_paths.append(out); print(f"  + {out.name}")

    # Trends
    if trends:
        img  = _bg()
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text((80,72), "📈", font=_font(44), fill=ACCENT)
        draw.text((144,80), "주목할 트렌드 키워드", font=_font(38), fill=WHITE)
        draw.line([(80,148),(CARD_SIZE-80,148)], fill=(*ACCENT,80), width=2)
        y = 180
        for i, t in enumerate(trends):
            desc_lines = _wrap(t.get("description",""), _font(26), CARD_SIZE-200)
            lh = sum(_font(26).getbbox(l)[3]-_font(26).getbbox(l)[1]+10 for l in desc_lines)
            h  = max(60+lh+20, 120)
            draw.rounded_rectangle([80,y,CARD_SIZE-80,y+h], radius=14,
                                   fill=(255,255,255,12), outline=(255,255,255,20), width=1)
            draw.rectangle([80,y,85,y+h], fill=ACCENT)
            draw.text((106,y+16), f"#{t.get('keyword','')}", font=_font(30), fill=ACCENT)
            cy = y+58
            for l in desc_lines:
                draw.text((106,cy), l, font=_font(26), fill=GRAY)
                cy += _font(26).getbbox(l)[3]-_font(26).getbbox(l)[1]+10
            y += h+20
        footer(img, 1+len(issues))
        out = CARDNEWS_DIR / f"{date_str}-{1+len(issues)}.png"
        img.save(str(out),"PNG"); output_paths.append(out); print(f"  + {out.name}")

    return output_paths


# ── 메인 ──────────────────────────────────────────────────────────────────────
def generate_images(date_str: str, backend: str = "auto") -> list[Path]:
    html_path = CARDNEWS_DIR / f"{date_str}.html"
    if not html_path.exists():
        raise FileNotFoundError(f"HTML 없음: {html_path}. build_cardnews.py를 먼저 실행하세요.")

    if backend == "pillow":
        print("  [Pillow 백엔드]")
        return generate_pillow(date_str)

    # Playwright 시도
    try:
        import playwright  # noqa: F401
        print("  [Playwright 백엔드]")
        return generate_playwright(date_str, html_path)
    except ImportError:
        print("  Playwright 없음 → Pillow 폴백")
    except Exception as e:
        print(f"  Playwright 실패({e}) → Pillow 폴백")

    return generate_pillow(date_str)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date",    help="YYYY-MM-DD (미입력 시 최신)")
    parser.add_argument("--backend", choices=["auto", "playwright", "pillow"],
                        default="auto", help="렌더링 백엔드")
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
    paths = generate_images(date_str, args.backend)
    print(f"  총 {len(paths)}개 이미지 생성 완료")


if __name__ == "__main__":
    main()
