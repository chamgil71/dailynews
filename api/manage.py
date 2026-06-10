"""
GET  /api/manage?token=xxx  또는  ?email=xxx → 채널 관리 HTML 폼 표시
POST /api/manage?token=xxx  → 채널 설정 업데이트
"""
import secrets
import sys
import urllib.parse
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from api._supabase import sb_get, sb_patch, sb_insert, sb_delete
from api._smtp import _page, SITE_BASE_URL


def _manage_html(email: str, channels: dict, token: str) -> str:
    def ck(name: str) -> str:
        return "checked" if channels.get(name) else ""
    action = f"/api/manage?token={urllib.parse.quote(token)}"
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>구독 채널 관리</title>
<style>
  *{{box-sizing:border-box}}
  body{{font-family:'Noto Sans KR',Arial,sans-serif;background:#f8fafc;margin:0;padding:40px 20px}}
  .wrap{{max-width:480px;margin:auto;background:#fff;border-radius:16px;
         padding:48px 40px;box-shadow:0 4px 24px rgba(0,0,0,.08)}}
  h1{{font-size:1.5rem;color:#0f172a;margin-top:0}}
  .email{{background:#f1f5f9;border-radius:8px;padding:10px 16px;
          color:#334155;font-weight:600;margin-bottom:28px;font-size:.95rem}}
  .ch-list{{display:flex;flex-direction:column;gap:14px;margin-bottom:32px}}
  .ch-item{{display:flex;align-items:center;gap:14px;border:2px solid #e2e8f0;
            border-radius:12px;padding:16px 20px;cursor:pointer;transition:.15s}}
  .ch-item:has(input:checked){{border-color:#6366f1;background:#f5f3ff}}
  .ch-item input{{width:20px;height:20px;accent-color:#6366f1;cursor:pointer}}
  .ch-label{{flex:1}}
  .ch-title{{font-weight:700;color:#0f172a;font-size:1rem}}
  .ch-desc{{font-size:.85rem;color:#64748b;margin-top:2px}}
  .btn{{width:100%;padding:14px;background:#6366f1;color:#fff;border:none;
        border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer}}
  .btn:hover{{background:#4f46e5}}
  .unsub{{text-align:center;margin-top:20px;font-size:.85rem;color:#94a3b8}}
  .unsub a{{color:#ef4444;text-decoration:none}}
</style></head>
<body><div class="wrap">
<h1>📋 구독 채널 관리</h1>
<div class="email">✉️ {email}</div>
<form method="POST" action="{action}">
  <div class="ch-list">
    <label class="ch-item">
      <input type="checkbox" name="news" value="on" {ck("news")}>
      <div class="ch-label">
        <div class="ch-title">📰 AI 뉴스 브리핑</div>
        <div class="ch-desc">매일 아침 AI·테크 핵심 뉴스 요약</div>
      </div>
    </label>
    <label class="ch-item">
      <input type="checkbox" name="stock" value="on" {ck("stock")}>
      <div class="ch-label">
        <div class="ch-title">📈 주식 시황 브리핑</div>
        <div class="ch-desc">평일 AI 분석 주식·코스피 시황</div>
      </div>
    </label>
    <label class="ch-item">
      <input type="checkbox" name="ai_issue" value="on" {ck("ai_issue")}>
      <div class="ch-label">
        <div class="ch-title">🤖 AI 주간 이슈</div>
        <div class="ch-desc">매주 AI·빅테크 주요 이슈 분석</div>
      </div>
    </label>
  </div>
  <button class="btn" type="submit">설정 저장</button>
</form>
<div class="unsub">
  더 이상 받지 않으려면 <a href="/api/unsubscribe?token={token}">전체 구독 취소</a>
</div>
</div></body></html>"""


def _get_or_create_manage_token(email: str) -> str:
    """이메일로 manage 토큰 조회 or 신규 발급."""
    existing = sb_get("subscription_tokens",
                      {"email": f"eq.{email}", "action": "eq.manage"})
    if existing:
        row = existing[0]
        if datetime.fromisoformat(row["expires_at"]) > datetime.now(timezone.utc):
            return row["token"]
        sb_delete("subscription_tokens", "token", row["token"])

    token = secrets.token_urlsafe(32)
    sb_insert("subscription_tokens", {
        "token":      token,
        "email":      email,
        "action":     "manage",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    })
    return token


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        token  = params.get("token", [""])[0].strip()
        email  = params.get("email", [""])[0].strip().lower()

        try:
            if token:
                rows = sb_get("subscription_tokens",
                              {"token": f"eq.{token}", "action": "eq.manage"})
                if not rows or datetime.fromisoformat(rows[0]["expires_at"]) < datetime.now(timezone.utc):
                    self._respond(400, _page("오류", "링크가 만료되었습니다.", "#ef4444",
                                             f"{SITE_BASE_URL}/subscribe", "재구독"))
                    return
                email = rows[0]["email"]
            elif email:
                token = _get_or_create_manage_token(email)
            else:
                self._respond(400, _page("오류", "잘못된 요청입니다.", "#ef4444"))
                return

            subs = sb_get("subscribers", {"email": f"eq.{email}"})
            if not subs:
                self._respond(404, _page("오류", "구독 정보를 찾을 수 없습니다.", "#ef4444",
                                         f"{SITE_BASE_URL}/subscribe", "구독 신청"))
                return

            channels = subs[0].get("channels", {"news": True, "stock": False, "ai_issue": False})
            self._respond(200, _manage_html(email, channels, token))
        except Exception as e:
            self._respond(500, _page("오류", f"처리 중 오류: {e}", "#ef4444"))

    def do_POST(self):  # noqa: N802
        params  = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        token   = params.get("token", [""])[0].strip()
        length  = int(self.headers.get("Content-Length", 0))
        body    = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"))

        if not token:
            self._respond(400, _page("오류", "잘못된 요청입니다.", "#ef4444"))
            return

        try:
            rows = sb_get("subscription_tokens",
                          {"token": f"eq.{token}", "action": "eq.manage"})
            if not rows or datetime.fromisoformat(rows[0]["expires_at"]) < datetime.now(timezone.utc):
                self._respond(400, _page("오류", "링크가 만료되었습니다.", "#ef4444"))
                return

            email = rows[0]["email"]
            channels = {
                "news":     body.get("news",     [""])[0] == "on",
                "stock":    body.get("stock",    [""])[0] == "on",
                "ai_issue": body.get("ai_issue", [""])[0] == "on",
            }
            if not any(channels.values()):
                channels["news"] = True

            sb_patch("subscribers", "email", email, {"channels": channels, "status": "active"})

            self._respond(200, _page(
                "채널 설정이 저장되었습니다",
                "구독 채널 설정이 업데이트되었습니다.",
                "#22c55e",
                f"/api/manage?token={token}", "채널 설정 보기",
            ))
        except Exception as e:
            self._respond(500, _page("오류", f"처리 중 오류: {e}", "#ef4444"))

    def _respond(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args): pass
