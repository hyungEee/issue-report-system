from __future__ import annotations

from dataclasses import dataclass

from anthropic import Anthropic

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class IssueDigest:
    title_ko: str
    summary: str
    insight: str


class LLMService:
    _SYSTEM_PROMPT = (
        "You are a news summarizer. "
        "Summarize strictly based on the article provided. "
        "Do not add any facts, names, or claims not explicitly stated in the article. "
        "Respond only in Korean, using polite formal language (존댓말). "
        "title_ko: translate the title to Korean if it is not already in Korean, otherwise keep it as is.\n"
        "summary: 2–3 sentences summarizing the article.\n"
        'insight: one sentence starting with "인사이트:" that provides a meaningful takeaway.'
    )

    _TOOL = {
        "name": "create_digest",
        "description": "뉴스 기사 요약 결과를 반환합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title_ko": {"type": "string"},
                "summary": {"type": "string"},
                "insight": {"type": "string"},
            },
            "required": ["title_ko", "summary", "insight"],
            "additionalProperties": False,
        },
    }

    def __init__(self) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)

    def summarize_issue(self, title: str, content: str | None) -> IssueDigest:
        user_content = f"제목: {title}\n\n본문:\n{content or '(본문 없음)'}"

        message = self._client.messages.create(
            model=settings.llm_model,
            max_tokens=800,
            system=self._SYSTEM_PROMPT,
            tools=[self._TOOL],
            tool_choice={"type": "tool", "name": "create_digest"},
            messages=[{"role": "user", "content": user_content}],
        )

        tool_input = message.content[0].input
        return IssueDigest(
            title_ko=tool_input.get("title_ko", title).strip(),
            summary=tool_input.get("summary", "").strip(),
            insight=tool_input.get("insight", "").strip(),
        )
