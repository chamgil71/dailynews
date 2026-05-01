코드 확인했습니다. 현재 구조의 문제점과 최소 수정안을 정확히 짚어드립니다.

---

## 현재 코드의 문제점

```python
"to": EMAIL_TO,  # ← 쉼표로 구분된 문자열 또는 리스트
```

`to` 필드에 여러 명을 넣으면 **수신자 전원이 서로의 이메일을 볼 수 있습니다.** 개인정보 문제입니다.

또한 `verify=False`는 SSL 인증서 검증을 끄는 것으로, 프로덕션에서 제거해야 합니다.

---

## 50명 이내, 무료 → 최적 수정안

외부 DB 없이 **환경변수 구독자 목록 + Resend Batch API**만으로 해결합니다.

```python
# core/mailer.py
"""
이메일 발송 모듈 (Resend Batch API)
- 수신자: RECIPIENT_EMAILS 환경변수 (쉼표 구분)
- 개별 발송: 수신자끼리 서로 이메일 주소 안 보임
- 구독 취소: 메일 하단 링크 클릭 → mailto 방식 (수동 관리)
"""

import logging
import os
import requests
from datetime import datetime
import markdown

from config.settings import EMAIL_FROM, EMAIL_SUBJECT, RESEND_API_KEY

logger = logging.getLogger(__name__)


def _get_recipients() -> list[str]:
    """환경변수에서 구독자 목록 파싱"""
    raw = os.environ.get("RECIPIENT_EMAILS", "")
    return [e.strip() for e in raw.split(",") if e.strip()]


def _md_to_html(md: str, recipient_email: str) -> str:
    body = markdown.markdown(md, extensions=["tables", "fenced_code"])
    # 구독 취소: mailto 방식 (별도 서버 불필요)
    unsubscribe_url = f"mailto:unsubscribe@yourdomain.com?subject=unsubscribe&body={recipient_email}"
    return f"""
<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px">
{body}
<br><hr>
<small style="color:#888">
  AI News Daily — {datetime.now().strftime('%Y-%m-%d')} &nbsp;|&nbsp;
  <a href="{unsubscribe_url}" style="color:#aaa">구독 취소</a>
</small>
</body></html>
"""


def send_email(md_content: str) -> bool:
    if not RESEND_API_KEY:
        logger.warning("[이메일] RESEND_API_KEY 미설정 — 발송 건너뜀")
        return False

    recipients = _get_recipients()
    if not recipients:
        logger.warning("[이메일] RECIPIENT_EMAILS 미설정 — 발송 건너뜀")
        return False

    date_str = datetime.now().strftime("%Y-%m-%d")
    subject  = EMAIL_SUBJECT.format(date=date_str)

    # 수신자별 개별 메일 객체 생성 (Batch)
    batch_payload = [
        {
            "from":    EMAIL_FROM,
            "to":      [email],          # 반드시 리스트, 1명씩
            "subject": subject,
            "html":    _md_to_html(md_content, email),
        }
        for email in recipients
    ]

    try:
        resp = requests.post(
            "https://api.resend.com/emails/batch",  # ← /batch 엔드포인트
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json=batch_payload,
            timeout=30,
            # verify=False 제거 — SSL 검증 활성화
        )
        if resp.status_code in (200, 201):
            logger.info(f"[이메일 발송] 성공 → {len(recipients)}명")
            return True
        else:
            logger.error(f"[이메일 발송 실패] {resp.status_code}: {resp.text}")
            return False

    except Exception as e:
        logger.error(f"[이메일 발송 오류] {e}")
        return False
```

---

## 변경 사항 요약

| 항목 | 기존 | 변경 후 |
|------|------|---------|
| 발송 방식 | `/emails` (단일, 전체 노출) | `/emails/batch` (개별, 비공개) |
| 구독자 관리 | `EMAIL_TO` 단일 변수 | `RECIPIENT_EMAILS` 쉼표 구분 |
| 구독 취소 | 없음 | mailto 링크 (수동 관리) |
| SSL 검증 | `verify=False` | 기본값(True) |
| HTML 생성 | 공통 1개 | 수신자별 개별 생성 |

---

## GitHub Secrets 설정

```
RECIPIENT_EMAILS = user1@gmail.com,user2@naver.com,user3@kakao.com
```

구독자 추가/삭제는 이 값만 수정하면 됩니다. 50명 이내, 무료 범위에서 이게 가장 단순하고 안전한 구성입니다.