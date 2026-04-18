from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    def send_report(self, html_content: str, to_email: str, subject: str) -> bool:
        msg = MIMEText(html_content, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to_email

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.sendmail(settings.smtp_from, to_email, msg.as_string())
            return True
        except Exception as e:
            logger.error("이메일 발송 실패 - to=%s error=%s", to_email, e)
            return False
