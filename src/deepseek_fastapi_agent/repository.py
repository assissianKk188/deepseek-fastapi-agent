class InMemoryConversationRepository:
    """Development-only conversation state; replace this port for persistence."""

    def __init__(self) -> None:
        self._conversations: dict[str, list[tuple[str, str]]] = {}

    def append(self, conversation_id: str, role: str, content: str) -> None:
        self._conversations.setdefault(conversation_id, []).append((role, content))

    def history(self, conversation_id: str) -> list[tuple[str, str]]:
        return list(self._conversations.get(conversation_id, []))

