from uuid import uuid4

from deepseek_fastapi_agent.domain import AgentRunner, ChatRequest, ChatResult, ConversationRepository


class ChatService:
    def __init__(self, repository: ConversationRepository, runner: AgentRunner) -> None:
        self._repository = repository
        self._runner = runner

    def reply(self, request: ChatRequest, request_id: str) -> ChatResult:
        conversation_id = request.conversation_id or str(uuid4())
        self._repository.append(conversation_id, "user", request.message)
        answer = self._runner.run(self._repository.history(conversation_id))
        self._repository.append(conversation_id, "assistant", answer)
        return ChatResult(conversation_id=conversation_id, answer=answer, request_id=request_id)

