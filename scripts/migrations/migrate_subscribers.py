"""
기존 RECIPIENT_EMAILS 환경변수 구독자 → Supabase subscribers 테이블 마이그레이션.

사용법:
  python scripts/migrate_subscribers.py

SUPABASE_URL, SUPABASE_SERVICE_KEY, RECIPIENT_EMAILS 환경변수 필요.
기존 이메일은 3채널 모두 활성(news=true, stock=true, ai_issue=true), status=active 로 삽입.
이미 존재하는 이메일은 건너뜀.
"""
import os
import sys
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

import requests

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://syxpwvmniwzohmxmvlyl.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
RECIPIENT_EMAILS = [e.strip() for e in os.getenv("RECIPIENT_EMAILS", "").split(",") if e.strip()]

if not SUPABASE_KEY:
    print("❌ SUPABASE_SERVICE_KEY 미설정")
    sys.exit(1)

if not RECIPIENT_EMAILS:
    print("❌ RECIPIENT_EMAILS 미설정")
    sys.exit(1)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=ignore-duplicates,return=representation",
}

print(f"[마이그레이션] {len(RECIPIENT_EMAILS)}명 처리 시작...")

ok = 0
skip = 0
for email in RECIPIENT_EMAILS:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/subscribers",
        headers=headers,
        json={
            "email":        email,
            "channels":     {"news": True, "stock": True, "ai_issue": True},
            "status":       "active",
            "confirmed_at": "now()",
        },
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        if result:
            print(f"  ✅ 삽입: {email}")
            ok += 1
        else:
            print(f"  ⏭  이미 존재: {email}")
            skip += 1
    else:
        print(f"  ❌ 오류 ({resp.status_code}): {email} — {resp.text}")

print(f"\n완료: 삽입 {ok}명 / 기존 {skip}명 / 총 {len(RECIPIENT_EMAILS)}명")
