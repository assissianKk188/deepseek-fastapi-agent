from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be blank")
        return value


@dataclass(frozen=True)
class ChatResult:
    conversation_id: str
    answer: str
    request_id: str


class ConversationRepository(Protocol):
    def append(self, conversation_id: str, role: str, content: str) -> None: ...

    def history(self, conversation_id: str) -> list[tuple[str, str]]: ...


class AgentRunner(Protocol):
    def run(self, history: list[tuple[str, str]]) -> str: ...

