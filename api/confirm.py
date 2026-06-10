"""
GET /api/confirm?token=xxx  또는  ?email=xxx (토큰 없는 단순 확인)
→ 토큰 검증 → subscribers status=active → 토큰 삭제 → 완료 페이지
"""
import sys
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from api._supabase import sb_get, sb_patch, sb_delete
from api._smtp import _page, SITE_BASE_URL


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        token  = params.get("token", [""])[0].strip()
        email  = params.get("email", [""])[0].strip().lower()

        if not token and not email:
            self._respond(400, _page("오류", "잘못된 요청입니다.", "#ef4444"))
            return

        try:
            if token:
                rows = sb_get("subscription_tokens",
                              {"token": f"eq.{token}", "action": "eq.confirm"})
                if not rows:
                    self._respond(400, _page("오류", "유효하지 않거나 만료된 링크입니다.", "#ef4444"))
                    return

                row = rows[0]
                if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
                    sb_delete("subscription_tokens", "token", token)
                    self._respond(400, _page("오류", "링크가 만료되었습니다. 다시 구독 신청해 주세요.", "#ef4444",
                                             f"{SITE_BASE_URL}/subscribe", "구독 신청"))
                    return
                email = row["email"]
                sb_delete("subscription_tokens", "token", token)

            result = sb_patch("subscribers", "email", email, {
                "status":       "active",
                "confirmed_at": datetime.now(timezone.utc).isoformat(),
            })
            if not result:
                self._respond(404, _page("오류", "구독 정보를 찾을 수 없습니다.", "#ef4444"))
                return

            manage_url = f"{SITE_BASE_URL}/api/manage?email={urllib.parse.quote(email)}"
            self._respond(200, _page(
                "구독이 완료되었습니다!",
                f"<strong>{email}</strong>의 구독이 활성화되었습니다.<br>매일 최신 AI 뉴스를 받아보세요.",
                "#22c55e",
                manage_url, "채널 설정 변경",
            ))
        except Exception as e:
            self._respond(500, _page("오류", f"처리 중 오류가 발생했습니다: {e}", "#ef4444"))

    def _respond(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args): pass
