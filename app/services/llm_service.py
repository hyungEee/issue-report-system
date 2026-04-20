from __future__ import annotations

import json
from dataclasses import dataclass

from anthropic import Anthropic

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class IssueDigest:
    summary: str
    insight: str


class LLMService:
    _SYSTEM_PROMPT = (
        "You are a news summarizer. "
        "Summarize strictly based on the article provided. "
        "Do not add any facts, names, or claims not explicitly stated in the article. "
        "Respond only in Korean. "
        "Return a JSON object with exactly two keys:\n"
        '  "summary": 2–3 sentences summarizing the article.\n'
        '  "insight": one sentence starting with "인사이트:" that provides a meaningful takeaway.\n'
        "Return only the JSON object with no markdown, no code block, no extra text."
    )

    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)

    def summarize_issue(self, title: str, content: str | None) -> IssueDigest:
        user_content = f"제목: {title}\n\n본문:\n{content or '(본문 없음)'}"

        message = self._client.messages.create(
            model=settings.llm_model,
            max_tokens=400,
            system=self._SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )

        text = message.content[0].text.strip()

        try:
            parsed = json.loads(text)
            summary = str(parsed.get("summary", "")).strip()
            insight = str(parsed.get("insight", "")).strip()
            if not summary:
                raise ValueError("summary 필드 없음")
        except Exception:
            logger.warning("LLM 응답 JSON 파싱 실패 - raw=%s", text[:200])
            summary = title
            insight = ""

        return IssueDigest(summary=summary, insight=insight)
