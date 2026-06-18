"""
GET /api/unsubscribe?token=xxx
→ 토큰 검증 → subscribers status=unsubscribed → 토큰 삭제 → 완료 페이지

레거시 호환: ?email=xxx&token=xxx (HMAC 방식) 도 처리
"""
import hashlib
import hmac
import os
import sys
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from api._supabase import sb_get, sb_patch, sb_delete
from api._smtp import _page, SITE_BASE_URL

UNSUBSCRIBE_SECRET = os.environ.get("UNSUBSCRIBE_SECRET", "")


def _hmac_token(email: str) -> str:
    key = (UNSUBSCRIBE_SECRET or "fallback-secret").encode()
    return hmac.new(key, email.lower().encode(), hashlib.sha256).hexdigest()[:16]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        token  = params.get("token", [""])[0].strip()
        email  = params.get("email", [""])[0].strip().lower()

        if not token:
            self._respond(400, _page("오류", "잘못된 요청입니다.", "#ef4444"))
            return

        try:
            email_to_unsub = None

            # 1) 레거시 HMAC 방식 우선 확인 (이메일 파라미터 및 16자리 토큰이 있는 경우)
            # DB 조회를 회피하여 환경변수 누락 시에도 이메일 구독취소는 항상 동작하도록 보장합니다.
            if email and len(token) == 16:
                if hmac.compare_digest(_hmac_token(email), token):
                    email_to_unsub = email
                else:
                    self._respond(400, _page("오류", "유효하지 않은 링크입니다.", "#ef4444"))
                    return

            # 2) Supabase 토큰 방식
            else:
                rows = sb_get("subscription_tokens", {"token": f"eq.{token}"})
                if rows:
                    row = rows[0]
                    # 구독취소 및 관리(manage) 토큰 둘 다 허용
                    if row.get("action") in ("unsubscribe", "manage"):
                        expires_at_str = row["expires_at"].replace("Z", "+00:00")
                        if datetime.fromisoformat(expires_at_str) < datetime.now(timezone.utc):
                            sb_delete("subscription_tokens", "token", token)
                            self._respond(400, _page("오류", "링크가 만료되었습니다.", "#ef4444",
                                                     f"{SITE_BASE_URL}/subscribe", "재구독"))
                            return
                        email_to_unsub = row["email"]
                        sb_delete("subscription_tokens", "token", token)
                    else:
                        self._respond(400, _page("오류", "유효하지 않은 링크입니다.", "#ef4444"))
                        return
                else:
                    self._respond(400, _page("오류", "유효하지 않거나 만료된 링크입니다.", "#ef4444"))
                    return

            if not email_to_unsub:
                self._respond(400, _page("오류", "유효하지 않은 요청입니다.", "#ef4444"))
                return

            result = sb_patch("subscribers", "email", email_to_unsub, {
                "status":           "unsubscribed",
                "unsubscribed_at":  datetime.now(timezone.utc).isoformat(),
            })

            if not result:
                # Supabase에 없으면 정상 처리 (이미 취소됐거나 미등록)
                pass

            self._respond(200, _page(
                "구독이 취소되었습니다",
                f"<strong>{email_to_unsub}</strong>의 구독이 취소되었습니다.<br>언제든지 다시 구독하실 수 있습니다.",
                "#22c55e",
                f"{SITE_BASE_URL}/subscribe", "다시 구독하기",
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
