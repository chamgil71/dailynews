"""API 전용 경량 이메일 발송 — mailer.py 의존성 없이 SMTP 직접 사용."""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER     = os.environ.get("GMAIL_USER", "")
GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
SITE_BASE_URL  = os.environ.get("SITE_BASE_URL", "https://ms-dailynews.vercel.app").rstrip("/")


def send(to: str, subject: str, html: str) -> bool:
    if not GMAIL_USER or not GMAIL_PASSWORD:
        return False
    try:
        try:
            smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
            smtp.ehlo(); smtp.starttls()
        except Exception:
            smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)

        with smtp:
            smtp.login(GMAIL_USER, GMAIL_PASSWORD)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = GMAIL_USER
            msg["To"]      = to
            msg.attach(MIMEText(html, "html", "utf-8"))
            smtp.sendmail(GMAIL_USER, to, msg.as_string())
        return True
    except Exception:
        return False


def _page(title: str, msg: str, color: str = "#6366f1", btn_url: str = "", btn_text: str = "") -> str:
    btn = f'<a href="{btn_url}" style="display:inline-block;margin-top:20px;padding:12px 28px;background:{color};color:#fff;border-radius:8px;text-decoration:none;font-weight:600">{btn_text}</a>' if btn_url else ""
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  body{{font-family:'Noto Sans KR',Arial,sans-serif;display:flex;align-items:center;
       justify-content:center;min-height:100vh;margin:0;background:#f8fafc}}
  .card{{background:#fff;border-radius:16px;padding:48px 40px;max-width:420px;width:90%;
         text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.08)}}
  .icon{{font-size:48px;margin-bottom:16px}}
  h2{{color:#0f172a;margin:.5em 0;font-size:1.5rem}}
  p{{color:#64748b;line-height:1.7;margin:.5em 0}}
  .brand{{margin-top:32px;font-size:.85rem;color:#94a3b8}}
</style></head>
<body><div class="card">
<div class="icon">{"✅" if color=="#22c55e" else "❌" if color=="#ef4444" else "📬"}</div>
<h2>{title}</h2><p>{msg}</p>
{btn}
<div class="brand">AI News Daily · ms-dailynews.vercel.app</div>
</div></body></html>"""
