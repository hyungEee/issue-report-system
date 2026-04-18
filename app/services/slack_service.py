from __future__ import annotations

import httpx

from app.core.logger import get_logger

logger = get_logger(__name__)

_TIMEOUT = 10


class SlackService:
    def send_report(self, content: str, webhook_url: str) -> bool:
        """일간 리포트 발송."""
        return self._post(webhook_url, content)

    def _post(self, webhook_url: str, text: str) -> bool:
        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                resp = client.post(webhook_url, json={"text": text})
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error("Slack 발송 실패 - error=%s", e)
            return False
