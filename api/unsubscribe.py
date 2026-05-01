"""
Vercel Python serverless — /api/unsubscribe
GET ?email=xxx&token=yyy
- HMAC 토큰 검증
- storage/unsubscribed.txt에 이메일 추가 (GitHub Contents API)
"""

import base64
import hashlib
import hmac
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler

import requests as http_requests

UNSUBSCRIBE_SECRET  = os.environ.get("UNSUBSCRIBE_SECRET", "")
GH_CONTENTS_TOKEN   = os.environ.get("GH_CONTENTS_TOKEN", "")
GITHUB_REPOSITORY   = os.environ.get("GITHUB_REPOSITORY", "")   # "owner/repo"
UNSUB_FILE_PATH     = "storage/unsubscribed.txt"
GH_API_BASE         = "https://api.github.com"


def _make_token(email: str) -> str:
    key = (UNSUBSCRIBE_SECRET or "fallback-secret").encode()
    return hmac.new(key, email.lower().encode(), hashlib.sha256).hexdigest()[:16]


def _gh_headers() -> dict:
    return {
        "Authorization": f"Bearer {GH_CONTENTS_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_file() -> tuple[str, str]:
    """Returns (current_content, sha)"""
    url = f"{GH_API_BASE}/repos/{GITHUB_REPOSITORY}/contents/{UNSUB_FILE_PATH}"
    resp = http_requests.get(url, headers=_gh_headers(), timeout=10)
    if resp.status_code == 404:
        return "", ""
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return content, data["sha"]


def _put_file(content: str, sha: str, message: str) -> None:
    url = f"{GH_API_BASE}/repos/{GITHUB_REPOSITORY}/contents/{UNSUB_FILE_PATH}"
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    body: dict = {
        "message": message,
        "content": encoded,
        "committer": {"name": "AI News Bot", "email": "bot@noreply.github.com"},
    }
    if sha:
        body["sha"] = sha
    resp = http_requests.put(url, headers=_gh_headers(), json=body, timeout=10)
    resp.raise_for_status()


def _html_page(title: str, message: str, success: bool) -> str:
    color = "#22c55e" if success else "#ef4444"
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  body{{font-family:Arial,sans-serif;display:flex;align-items:center;justify-content:center;
       min-height:100vh;margin:0;background:#f9fafb}}
  .card{{background:#fff;border-radius:12px;padding:40px;max-width:400px;
         text-align:center;box-shadow:0 2px 16px rgba(0,0,0,.08)}}
  h2{{color:{color};margin:.5em 0}}
  p{{color:#666;line-height:1.6}}
</style></head>
<body>
<div class="card">
  <h2>{title}</h2>
  <p>{message}</p>
</div>
</body></html>"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        email  = params.get("email", [""])[0].strip().lower()
        token  = params.get("token", [""])[0].strip()

        # 기본 검증
        if not email or not token:
            self._respond(400, _html_page("오류", "잘못된 요청입니다.", False))
            return

        # HMAC 검증
        if not hmac.compare_digest(_make_token(email), token):
            self._respond(400, _html_page("오류", "유효하지 않은 링크입니다.", False))
            return

        # GitHub Contents API 없으면 에러
        if not GH_CONTENTS_TOKEN or not GITHUB_REPOSITORY:
            self._respond(500, _html_page("오류", "서버 설정 오류입니다.", False))
            return

        try:
            current, sha = _get_file()
            existing = {line.strip().lower() for line in current.splitlines() if line.strip()}

            if email in existing:
                self._respond(200, _html_page("이미 처리됨", f"{email} 은(는) 이미 구독 취소되어 있습니다.", True))
                return

            new_content = current.rstrip("\n") + ("\n" if current else "") + email + "\n"
            _put_file(new_content, sha, f"구독 취소: {email}")
            self._respond(200, _html_page("구독 취소 완료", f"{email} 의 구독이 취소되었습니다.<br>더 이상 뉴스레터를 받지 않습니다.", True))

        except Exception as exc:
            self._respond(500, _html_page("오류", f"처리 중 오류가 발생했습니다: {exc}", False))

    def _respond(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # noqa: ANN002
        pass  # Vercel handles logging
