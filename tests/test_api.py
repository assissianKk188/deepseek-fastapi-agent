from fastapi.testclient import TestClient

from deepseek_fastapi_agent.api import create_app
from deepseek_fastapi_agent.repository import InMemoryConversationRepository
from deepseek_fastapi_agent.service import ChatService


class FakeRunner:
    def run(self, history: list[tuple[str, str]]) -> str:
        return "你好，世界"


def build_client() -> TestClient:
    service = ChatService(repository=InMemoryConversationRepository(), runner=FakeRunner())
    return TestClient(create_app(service=service))


def test_health_returns_ok() -> None:
    response = build_client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_request_id() -> None:
    response = build_client().post("/api/v1/chat", json={"message": "你好"})

    assert response.status_code == 200
    assert response.json()["answer"] == "你好，世界"
    assert response.json()["request_id"]


def test_chat_rejects_blank_message() -> None:
    response = build_client().post("/api/v1/chat", json={"message": "  "})

    assert response.status_code == 422

