from deepseek_fastapi_agent.repository import InMemoryConversationRepository


def test_repository_appends_and_returns_history() -> None:
    repository = InMemoryConversationRepository()

    repository.append("c-1", "user", "你好")

    assert repository.history("c-1") == [("user", "你好")]

