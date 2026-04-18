from __future__ import annotations

from dataclasses import dataclass

from anthropic import Anthropic

from app.core.config import settings
from app.core.logger import get_logger
from app.models.issue import Issue

logger = get_logger(__name__)


@dataclass
class IssueDigest:
    summary: str
    insight: str


class LLMService:
    _SYSTEM_PROMPT = (
        "You are a concise news analyst. "
        "Respond only in Korean. "
        "Return exactly two lines:\n"
        "Line 1 — a 2–3 sentence summary of the issue.\n"
        "Line 2 — a single-sentence insight starting with '인사이트:'."
    )

    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)

    def summarize_issue(self, issue: Issue) -> IssueDigest:
        user_content = (
            f"카테고리: {issue.category}\n"
            f"제목: {issue.representative_title}\n"
            f"요약: {issue.representative_summary or '없음'}\n"
            f"관련 기사 수: {issue.article_count}"
        )

        message = self._client.messages.create(
            model=settings.llm_model,
            max_tokens=300,
            system=self._SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        text = message.content[0].text.strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        summary = lines[0] if len(lines) > 0 else issue.representative_title
        insight = lines[1] if len(lines) > 1 else ""

        return IssueDigest(summary=summary, insight=insight)
