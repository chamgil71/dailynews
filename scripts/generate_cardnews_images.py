"""
카드뉴스 HTML → 1080×1080 PNG 이미지 생성 (3채널 지원)

출력 경로:
  publish/cardnews/news/YYYY-MM-DD-{N}.png
  publish/cardnews/ai-issue/YYYY-MM-DD-{N}.png
  publish/cardnews/stock/YYYY-MM-DD-{N}.png

기본: Playwright (헤드리스 Chromium, Google Fonts 로드 → 완벽한 Noto Sans KR)
폴백: Pillow (브라우저 없는 환경용, 폰트 품질 낮을 수 있음)

GitHub Actions 요구사항 (cardnews.yml에서 처리):
  sudo apt-get install -y fonts-noto-cjk
  pip install playwright
  playwright install chromium --with-deps

사용법:
  python scripts/generate_cardnews_images.py                          # 뉴스 최신
  python scripts/generate_cardnews_images.py --type ai-issue          # AI이슈 최신
  python scripts/generate_cardnews_images.py --type stock             # 주식 최신
  python scripts/generate_cardnews_images.py --type news --date 2026-06-04
  python scripts/generate_cardnews_images.py --backend pillow         # 폴백 강제
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

PUBLISH_DIR  = Path(_ROOT, "publish")
CARDNEWS_DIR = PUBLISH_DIR / "cardnews"
CARD_SIZE    = 1080


def _type_dir(channel: str) -> Path:
    return CARDNEWS_DIR / channel


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
def generate_playwright(date_str: str, channel: str, html_path: Path) -> list[Path]:
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

    out_dir       = _type_dir(channel)
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
            url = f"http://127.0.0.1:{port}/cardnews/{channel}/{date_str}.html?card={i}"
            page.goto(url, wait_until="networkidle", timeout=30_000)
            page.evaluate("() => document.fonts.ready")
            page.wait_for_timeout(300)

            out = out_dir / f"{date_str}-{i}.png"
            page.screenshot(
                path=str(out),
                clip={"x": 0, "y": 0, "width": CARD_SIZE, "height": CARD_SIZE}
            )
            output_paths.append(out)
            print(f"  + {out.name}")

        browser.close()

    return output_paths


# ── Pillow 폴백 백엔드 ────────────────────────────────────────────────────────
def generate_pillow(date_str: str, channel: str) -> list[Path]:
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

    # 채널별 액센트 색상
    ACCENT_MAP = {
        "news":     (56, 189, 248),
        "ai-issue": (167, 139, 250),
        "stock":    (52, 211, 153),
    }
    ACCENT = ACCENT_MAP.get(channel, (56, 189, 248))

    def _bg() -> Image.Image:
        img  = Image.new("RGB", (CARD_SIZE, CARD_SIZE))
        draw = ImageDraw.Draw(img)
        for y in range(CARD_SIZE):
            t = y / CARD_SIZE
            r = int(10 + 7 * t); g = int(15 + 12 * t); b = int(30 + 28 * t)
            draw.line([(0, y), (CARD_SIZE, y)], fill=(r, g, b))
        draw.rectangle([0, 0, CARD_SIZE, 5], fill=ACCENT)
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

    WHITE   = (248, 250, 252)
    GRAY    = (148, 163, 184)
    MUTED   = (71, 85, 105)
    ICOLORS = [(245, 158, 11), (129, 140, 248), (52, 211, 153)]

    try:
        from datetime import datetime as dt
        d = dt.strptime(date_str, "%Y-%m-%d")
        wds = ["월","화","수","목","금","토","일"]
        display_date = f"{d.year}년 {d.month}월 {d.day}일 ({wds[d.weekday()]})"
    except Exception:
        display_date = date_str

    out_dir = _type_dir(channel)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 채널별 데이터 로드
    if channel == "news":
        reports = json.loads(Path(_ROOT, "publish", "reports-data.json").read_text())
        report  = next((r for r in reports if r["date"] == date_str), None)
        if not report:
            raise ValueError(f"reports-data.json에 {date_str} 없음")
        ko     = report.get("structured", {}).get("ko", {})
        issues = ko.get("issues", [])[:3]
        trends = ko.get("trends", [])[:3]

    elif channel == "ai-issue":
        ai_path = Path(_ROOT, "publish", "ai-issue", f"{date_str}.json")
        if not ai_path.exists():
            raise FileNotFoundError(f"AI이슈 데이터 없음: {ai_path}")
        data   = json.loads(ai_path.read_text(encoding="utf-8"))
        top10  = data.get("top10", [])
        issues = [{"title": t.get("title",""), "summary": t.get("summary",""),
                   "category": t.get("category",""), "sources": t.get("sources", [])}
                  for t in top10[:3]]
        trends = []

    elif channel == "stock":
        stock_path = Path(_ROOT, "publish", "stock", "stock-data.json")
        if not stock_path.exists():
            raise FileNotFoundError(f"주식 데이터 없음: {stock_path}")
        all_data = json.loads(stock_path.read_text(encoding="utf-8"))
        report   = next((r for r in (all_data if isinstance(all_data, list) else [all_data])
                         if r.get("date") == date_str), None)
        if not report:
            raise ValueError(f"stock-data.json에 {date_str} 없음")
        temp     = report.get("temperature", {})
        issues   = [{"title": temp.get("display", "시장 온도계"),
                     "summary": temp.get("reason", ""), "category": "stock", "sources": []}]
        trends   = []

    else:
        raise ValueError(f"알 수 없는 채널: {channel}")

    total = 1 + len(issues) + (1 if trends else 0)

    def footer(img, card_idx):
        draw = ImageDraw.Draw(img, "RGBA")
        draw.line([(72, CARD_SIZE-90), (CARD_SIZE-72, CARD_SIZE-90)],
                  fill=(255,255,255,18), width=1)
        fs = _font(24)
        draw.text((80, CARD_SIZE-66), "ms-dailynews.vercel.app", font=fs, fill=ACCENT)
        draw.text((CARD_SIZE-80-fs.getbbox(display_date[:5])[2], CARD_SIZE-66),
                  display_date[:5], font=fs, fill=MUTED)
        cx = CARD_SIZE//2 - (total*18)//2
        for i in range(total):
            if i == card_idx:
                draw.rounded_rectangle([cx,CARD_SIZE-68,cx+30,CARD_SIZE-57], radius=5, fill=ACCENT)
                cx += 38
            else:
                draw.ellipse([cx,CARD_SIZE-68,cx+11,CARD_SIZE-57], fill=(255,255,255,50))
                cx += 19

    output_paths = []

    # Cover card
    img  = _bg()
    draw = ImageDraw.Draw(img, "RGBA")
    ICONS_COVER = ["*", ">>", "!"]
    draw.text((80, 196), display_date, font=_font(32), fill=ACCENT)
    draw.rectangle([80, 246, 280, 249], fill=ACCENT)
    draw.text((80, 268), "오늘의 핵심 이슈", font=_font(26), fill=MUTED)
    y = 316
    for i, issue in enumerate(issues):
        ic = ICOLORS[i]
        h  = 104
        draw.rounded_rectangle([80,y,CARD_SIZE-80,y+h], radius=14, fill=(255,255,255,12),
                                outline=(255,255,255,22), width=1)
        t = issue.get("title","")[:26]+"..." if len(issue.get("title",""))>26 else issue.get("title","")
        draw.text((104, y+26), t, font=_font(30), fill=WHITE)
        y += h + 18
    draw.text((80, y+8), f"#{channel} #AI뉴스 #데일리브리핑", font=_font(24), fill=MUTED)
    footer(img, 0)
    out = out_dir / f"{date_str}-0.png"
    img.save(str(out), "PNG"); output_paths.append(out); print(f"  + {out.name}")

    # Issue cards
    for i, issue in enumerate(issues):
        img  = _bg()
        draw = ImageDraw.Draw(img, "RGBA")
        ic   = ICOLORS[i]
        draw.text((80,82), f"핵심 이슈 {i+1}", font=_font(30), fill=ic)
        draw.rectangle([80,152,152,157], fill=ic)
        y = _draw_text(draw, issue.get("title",""), 80, 180, _font(46), WHITE, CARD_SIZE-160, gap=14)
        y += 22
        draw.line([(80,y),(CARD_SIZE-80,y)], fill=(255,255,255,18), width=1); y+=24
        y = _draw_text(draw, issue.get("summary",""), 80, y, _font(29), GRAY, CARD_SIZE-160, gap=12)
        footer(img, i+1)
        out = out_dir / f"{date_str}-{i+1}.png"
        img.save(str(out), "PNG"); output_paths.append(out); print(f"  + {out.name}")

    # Trends card
    if trends:
        img  = _bg()
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text((80,80), "주목할 트렌드 키워드", font=_font(38), fill=WHITE)
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
        out = out_dir / f"{date_str}-{1+len(issues)}.png"
        img.save(str(out),"PNG"); output_paths.append(out); print(f"  + {out.name}")

    return output_paths


# ── 메인 ──────────────────────────────────────────────────────────────────────
def generate_images(date_str: str, channel: str = "news", backend: str = "auto") -> list[Path]:
    out_dir   = _type_dir(channel)
    html_path = out_dir / f"{date_str}.html"
    if not html_path.exists():
        raise FileNotFoundError(f"HTML 없음: {html_path}. build_cardnews.py를 먼저 실행하세요.")

    out_dir.mkdir(parents=True, exist_ok=True)

    if backend == "pillow":
        print("  [Pillow 백엔드]")
        return generate_pillow(date_str, channel)

    try:
        import playwright  # noqa: F401
        print("  [Playwright 백엔드]")
        return generate_playwright(date_str, channel, html_path)
    except ImportError:
        print("  Playwright 없음 → Pillow 폴백")
    except Exception as e:
        print(f"  Playwright 실패({e}) → Pillow 폴백")

    return generate_pillow(date_str, channel)


def _latest_date(channel: str) -> str:
    data_path = _type_dir(channel) / "data.json"
    if not data_path.exists():
        raise FileNotFoundError(f"data.json 없음: {data_path}. build_cardnews.py 먼저 실행하세요.")
    index = json.loads(data_path.read_text(encoding="utf-8"))
    if not index:
        raise ValueError(f"카드뉴스 인덱스가 비어 있습니다 ({channel})")
    return index[0]["date"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", dest="channel",
                        choices=["news", "ai-issue", "stock"],
                        default="news", help="카드뉴스 채널")
    parser.add_argument("--date",    help="YYYY-MM-DD (미입력 시 최신)")
    parser.add_argument("--backend", choices=["auto", "playwright", "pillow"],
                        default="auto", help="렌더링 백엔드")
    args = parser.parse_args()

    date_str = args.date if args.date else _latest_date(args.channel)

    print(f"[generate-images] {args.channel} / {date_str}")
    paths = generate_images(date_str, args.channel, args.backend)
    print(f"  총 {len(paths)}개 이미지 생성 완료")


if __name__ == "__main__":
    main()
