from deepseek_fastapi_agent.domain import ChatRequest
from deepseek_fastapi_agent.repository import InMemoryConversationRepository
from deepseek_fastapi_agent.service import ChatService


class FakeRunner:
    def run(self, history: list[tuple[str, str]]) -> str:
        return "欢迎"


def test_service_saves_user_and_assistant_messages() -> None:
    repository = InMemoryConversationRepository()
    service = ChatService(repository=repository, runner=FakeRunner())

    result = service.reply(ChatRequest(message="你好"), request_id="r-1")

    assert result.answer == "欢迎"
    assert result.request_id == "r-1"
    assert repository.history(result.conversation_id) == [("user", "你好"), ("assistant", "欢迎")]

