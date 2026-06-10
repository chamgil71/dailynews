# mailer_resend.py — Resend Batch API 기반 이메일 발송 (비활성 보존본)
#
# 현재 프로젝트는 Gmail SMTP(mailer.py)를 사용합니다.
# Resend로 전환이 필요할 경우 이 파일을 참고하세요.
# GitHub Secret: RESEND_API_KEY, EMAIL_FROM 필요
#
# 전환 방법:
#   1. GitHub Secrets에 RESEND_API_KEY, EMAIL_FROM 추가
#   2. config/settings.py에 RESEND_API_KEY = os.getenv("RESEND_API_KEY","") 추가
#   3. mailer.py의 send_email()을 아래 구현으로 교체

# import logging
# import os
# import requests
# from datetime import datetime
#
# from config.settings import EMAIL_FROM, EMAIL_SUBJECT, RESEND_API_KEY
#
# logger = logging.getLogger(__name__)
#
#
# def _get_recipients() -> list[str]:
#     raw = os.environ.get("RECIPIENT_EMAILS", "")
#     return [e.strip() for e in raw.split(",") if e.strip()]
#
#
# def _md_to_html(md: str, recipient_email: str) -> str:
#     import markdown2
#     body = markdown2.markdown(md, extras=["tables", "fenced-code-blocks"])
#     unsubscribe_url = f"mailto:unsubscribe@yourdomain.com?subject=unsubscribe&body={recipient_email}"
#     return f"""<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px">
# {body}
# <br><hr>
# <small style="color:#888">
#   AI News Daily — {datetime.now().strftime('%Y-%m-%d')} &nbsp;|&nbsp;
#   <a href="{unsubscribe_url}" style="color:#aaa">구독 취소</a>
# </small>
# </body></html>"""
#
#
# def send_email(md_content: str) -> bool:
#     """Resend Batch API로 구독자 전원에게 개별 발송."""
#     if not RESEND_API_KEY:
#         logger.warning("[이메일] RESEND_API_KEY 미설정 — 발송 건너뜀")
#         return False
#
#     recipients = _get_recipients()
#     if not recipients:
#         logger.warning("[이메일] RECIPIENT_EMAILS 미설정 — 발송 건너뜀")
#         return False
#
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     subject  = EMAIL_SUBJECT.format(date=date_str)
#
#     # 수신자별 개별 메일 객체 (Batch) — 수신자끼리 이메일 주소 미노출
#     batch_payload = [
#         {
#             "from":    EMAIL_FROM,
#             "to":      [email],
#             "subject": subject,
#             "html":    _md_to_html(md_content, email),
#         }
#         for email in recipients
#     ]
#
#     try:
#         resp = requests.post(
#             "https://api.resend.com/emails/batch",
#             headers={
#                 "Authorization": f"Bearer {RESEND_API_KEY}",
#                 "Content-Type":  "application/json",
#             },
#             json=batch_payload,
#             timeout=30,
#         )
#         if resp.status_code in (200, 201):
#             logger.info(f"[이메일 발송] 성공 → {len(recipients)}명")
#             return True
#         else:
#             logger.error(f"[이메일 발송 실패] {resp.status_code}: {resp.text}")
#             return False
#     except Exception as e:
#         logger.error(f"[이메일 발송 오류] {e}")
#         return False
