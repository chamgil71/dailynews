"""
POST /api/subscribe
폼 데이터: email, news(on/off), stock(on/off), ai_issue(on/off)
→ subscribers upsert → confirm 토큰 생성 → 확인 이메일 발송
"""
import json
import os
import secrets
import sys
import urllib.parse
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from api._supabase import sb_upsert, sb_insert, sb_delete, sb_get
from api._smtp import send, _page, SITE_BASE_URL


def _token_url(action: str, token: str) -> str:
    return f"{SITE_BASE_URL}/api/{action}?token={token}"


def _confirm_html(email: str, channels: dict) -> str:
    ch_names = []
    if channels.get("news"):     ch_names.append("뉴스")
    if channels.get("stock"):    ch_names.append("주식시황")
    if channels.get("ai_issue"): ch_names.append("AI이슈")
    ch_str = " · ".join(ch_names) or "선택 없음"
    confirm_url = f"{SITE_BASE_URL}/api/confirm?email={urllib.parse.quote(email)}"
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>구독 확인</title>
<style>
  body{{font-family:'Noto Sans KR',Arial,sans-serif;background:#f8fafc;margin:0;padding:40px 20px}}
  .wrap{{max-width:560px;margin:auto;background:#fff;border-radius:16px;
         padding:48px 40px;box-shadow:0 4px 24px rgba(0,0,0,.08)}}
  h1{{font-size:1.6rem;color:#0f172a;margin-top:0}}
  .ch{{background:#f1f5f9;border-radius:8px;padding:14px 20px;margin:20px 0;color:#334155;font-weight:600}}
  .btn{{display:inline-block;padding:14px 32px;background:#6366f1;color:#fff;
        border-radius:10px;text-decoration:none;font-weight:700;font-size:1rem;margin-top:8px}}
  p{{color:#64748b;line-height:1.7}}
  .footer{{margin-top:32px;font-size:.82rem;color:#94a3b8;border-top:1px solid #e2e8f0;padding-top:16px}}
</style></head>
<body><div class="wrap">
<h1>📬 구독 신청 확인</h1>
<p>아래 버튼을 클릭하면 <strong>{email}</strong>의 구독이 활성화됩니다.</p>
<div class="ch">📋 선택 채널: {ch_str}</div>
<a class="btn" href="{confirm_url}">✅ 구독 확인하기</a>
<p style="margin-top:24px;font-size:.9rem">
  이 링크는 24시간 후 만료됩니다.<br>
  본인이 신청하지 않았다면 이 이메일을 무시하세요.
</p>
<div class="footer">AI News Daily · <a href="{SITE_BASE_URL}" style="color:#6366f1">ms-dailynews.vercel.app</a></div>
</div></body></html>"""


class handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length  = int(self.headers.get("Content-Length", 0))
        raw     = self.rfile.read(length).decode("utf-8")
        params  = urllib.parse.parse_qs(raw)

        email = params.get("email", [""])[0].strip().lower()
        if not email or "@" not in email:
            self._respond(400, _page("오류", "유효한 이메일을 입력해 주세요.", "#ef4444"))
            return

        channels = {
            "news":     "news"     in params and params["news"][0]     == "on",
            "stock":    "stock"    in params and params["stock"][0]    == "on",
            "ai_issue": "ai_issue" in params and params["ai_issue"][0] == "on",
        }
        if not any(channels.values()):
            channels["news"] = True  # 기본값: 뉴스

        try:
            # 구독자 upsert (이미 있으면 채널·status 업데이트)
            sb_upsert("subscribers", {
                "email":    email,
                "channels": channels,
                "status":   "pending",
            }, on_conflict="email")

            # 기존 confirm 토큰 삭제 후 재발급
            existing = sb_get("subscription_tokens",
                               {"email": f"eq.{email}", "action": "eq.confirm"})
            for t in existing:
                sb_delete("subscription_tokens", "token", t["token"])

            token = secrets.token_urlsafe(32)
            sb_insert("subscription_tokens", {
                "token":      token,
                "email":      email,
                "action":     "confirm",
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
            })

            sent = send(email, "📬 AI News Daily 구독 확인", _confirm_html(email, channels))
            if not sent:
                self._respond(500, _page("오류", "이메일 발송에 실패했습니다. 잠시 후 다시 시도해 주세요.", "#ef4444"))
                return

            self._respond(200, _page(
                "확인 이메일을 발송했습니다",
                f"<strong>{email}</strong>로 확인 이메일을 보냈습니다.<br>메일함을 확인해 구독을 완료해 주세요.",
                "#6366f1",
            ))
        except Exception as e:
            self._respond(500, _page("오류", f"처리 중 오류가 발생했습니다: {e}", "#ef4444"))

    def do_GET(self):  # noqa: N802
        # GET 요청 → 구독 페이지로 리다이렉트
        self.send_response(302)
        self.send_header("Location", f"{SITE_BASE_URL}/subscribe")
        self.end_headers()

    def _respond(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args): pass
