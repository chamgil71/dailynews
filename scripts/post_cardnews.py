"""
카드뉴스 멀티 플랫폼 SNS 발송 (3채널 지원) — 진입점

사용법:
  python scripts/post_cardnews.py --platform instagram,telegram,twitter
  python scripts/post_cardnews.py --type ai-issue --platform telegram --date 2026-06-04
  python scripts/post_cardnews.py --type stock --platform telegram
  python scripts/post_cardnews.py --type news --mode text        # 카드 이미지 없이 텍스트만

발송 모드 (--mode, 기본값: 환경변수 CARDNEWS_MODE → 없으면 image):
  image  - 카드뉴스 PNG 포함 발송 (카드 빌드 선행 필요)
  text   - 텍스트만 발송. 캡션은 원본 발행 데이터(core/shared/sns_source.py)에서 생성.
           Instagram 은 텍스트 단독 게시 불가 → 건너뜀(실패 아님)
  --platform 미지정 시 config/cardnews_themes.json sns.default_platforms[mode] 사용

플랫폼 핸들러는 scripts/sns/ 에 플랫폼별로 분리:
  instagram (카루셀) / threads (텍스트·카루셀) / facebook (멀티 사진·텍스트+링크)
  telegram (미디어 그룹+버튼) / twitter (이미지 트윗)

필요한 GitHub Secrets:
  [Instagram] INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID
  [Threads]   THREADS_ACCESS_TOKEN, THREADS_USER_ID
  [Facebook]  META_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID
  [Telegram]  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_STOCK
  [Twitter/X] TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.shared import sns_source  # noqa: E402
from core.shared.sns_report import PlatformSkipped, SnsReport  # noqa: E402
from scripts.sns.caption import build_caption as _build_caption  # noqa: E402,F401
from scripts.sns.common import channel_dir, load_themes_config  # noqa: E402
from scripts.sns.facebook import post_facebook  # noqa: E402
from scripts.sns.instagram import post_instagram  # noqa: E402
from scripts.sns.telegram import post_telegram  # noqa: E402
from scripts.sns.threads import post_threads  # noqa: E402
from scripts.sns.twitter import post_twitter  # noqa: E402

MODES = ("image", "text")

PLATFORM_HANDLERS = {
    "instagram": post_instagram,
    "telegram":  post_telegram,
    "twitter":   post_twitter,
    "threads":   post_threads,
    "facebook":  post_facebook,
}


def _default_platforms(mode: str) -> list[str]:
    """config/cardnews_themes.json sns.default_platforms[mode]."""
    return list(load_themes_config()["sns"]["default_platforms"][mode])


def _resolve_date(channel: str, mode: str) -> str:
    """최신 날짜. text 모드는 원본 발행 데이터, image 모드는 카드 인덱스 기준."""
    if mode == "text":
        return sns_source.latest_date(channel)
    data_path = channel_dir(channel) / "data.json"
    index = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else []
    if not index:
        raise FileNotFoundError(f"카드 인덱스 없음 ({data_path}) — build_cardnews.py 먼저 실행")
    return index[0]["date"]


def run(channel: str, date_str: str, mode: str, platforms: list[str]) -> SnsReport:
    """플랫폼별 발송 후 결과 리포트 반환 (한 플랫폼 실패가 다른 플랫폼을 막지 않음)."""
    report = SnsReport(channel=channel, date_str=date_str, mode=mode)
    for platform in platforms:
        handler = PLATFORM_HANDLERS.get(platform)
        if not handler:
            print(f"  ⚠ 알 수 없는 플랫폼: {platform} (지원: {list(PLATFORM_HANDLERS)})")
            continue
        print(f"\n── {platform.upper()} ──────────────────")
        try:
            handler(channel, date_str, mode)
            report.record_success(platform)
        except PlatformSkipped as e:
            print(f"  ⏭ {platform} 건너뜀 — {e}")
            report.record_skip(platform, str(e))
        except Exception as e:  # 플랫폼 격리: 기록 후 다음 플랫폼 진행, 종료 코드로 전파
            print(f"  ✗ {platform} 발송 실패: {e}")
            report.record_failure(platform, e)
    return report


def main() -> None:
    """CLI 진입점 — 실패 플랫폼이 하나라도 있으면 exit 1."""
    parser = argparse.ArgumentParser(description="카드뉴스 SNS 발송")
    parser.add_argument("--type", dest="channel",
                        choices=["news", "ai-issue", "stock"],
                        default="news", help="카드뉴스 채널")
    parser.add_argument("--platform", default="",
                        help="발송 플랫폼 (쉼표 구분). 미지정 시 모드별 기본값(config)")
    parser.add_argument("--mode", choices=MODES,
                        default=os.environ.get("CARDNEWS_MODE", "").strip() or "image",
                        help="image(카드 PNG 포함) | text(텍스트만)")
    parser.add_argument("--date", help="YYYY-MM-DD (미입력 시 최신)")
    args = parser.parse_args()

    try:
        date_str = args.date or _resolve_date(args.channel, args.mode)
    except (FileNotFoundError, ValueError) as e:
        print(f"발송 날짜 결정 실패: {e}")
        sys.exit(1)

    platforms = ([p.strip() for p in args.platform.split(",") if p.strip()]
                 or _default_platforms(args.mode))
    print(f"[post-cardnews] {args.channel} / {date_str}  mode={args.mode}  "
          f"플랫폼: {', '.join(platforms)}")

    report = run(args.channel, date_str, args.mode, platforms)
    report.write_github_output()
    print("\n" + report.detail_text())
    if report.has_failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
