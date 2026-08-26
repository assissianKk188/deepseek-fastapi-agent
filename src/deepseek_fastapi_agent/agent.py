from datetime import UTC, datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from deepseek_fastapi_agent.config import Settings


@tool
def current_utc_time() -> str:
    """Return the current time in UTC using ISO 8601 format."""
    return datetime.now(UTC).isoformat()


class DeepSeekLangGraphRunner:
    """LangGraph ReAct runner backed by DeepSeek's OpenAI-compatible API."""

    def __init__(self, settings: Settings) -> None:
        if not settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required")
        model = ChatOpenAI(
            model=settings.deepseek_model,
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self._agent = create_react_agent(model, tools=[current_utc_time])

    def run(self, history: list[tuple[str, str]]) -> str:
        messages = [HumanMessage(content=content) if role == "user" else AIMessage(content=content) for role, content in history]
        result = self._agent.invoke({"messages": messages})
        answer = result["messages"][-1].content
        return answer if isinstance(answer, str) else str(answer)

