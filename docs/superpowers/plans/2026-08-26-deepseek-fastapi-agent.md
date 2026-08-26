# DeepSeek FastAPI Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a small FastAPI service that serves a stateful DeepSeek-backed LangGraph agent through a public-facing chat API.

**Architecture:** FastAPI routes delegate to `ChatService`, which loads state from a repository and calls an `AgentRunner` port. The LangGraph/DeepSeek implementation and the in-memory repository sit behind these ports, preserving an upgrade path to additional tools, Redis, PostgreSQL, and other providers.

**Tech Stack:** Python 3.12, FastAPI, Pydantic Settings, LangGraph, LangChain OpenAI adapter, DeepSeek OpenAI-compatible API, pytest, httpx, uvicorn, Docker.

**Spec:** `docs/superpowers/specs/2026-08-26-deepseek-fastapi-agent-design.md`

## Global Constraints

- Require Python `>=3.12`.
- Default model is exactly `deepseek-v4-flash`; default base URL is exactly `https://api.deepseek.com`.
- Read every secret from environment or `.env`; never commit `.env` or API keys.
- Keep routes independent of LangGraph and provider SDK types.
- Do not contact DeepSeek in automated tests.

---

## File Structure

- `src/deepseek_fastapi_agent/config.py`: typed environment configuration.
- `src/deepseek_fastapi_agent/domain.py`: chat DTOs and protocol interfaces.
- `src/deepseek_fastapi_agent/repository.py`: in-memory conversation implementation.
- `src/deepseek_fastapi_agent/agent.py`: LangGraph DeepSeek runner and UTC tool.
- `src/deepseek_fastapi_agent/service.py`: orchestration and error mapping.
- `src/deepseek_fastapi_agent/api.py`: FastAPI factory, middleware, and routes.
- `tests/`: unit and API tests using injected fakes.
- `README.md`, `.env.example`, `Dockerfile`, `pyproject.toml`, `.github/workflows/test.yml`: operating and delivery assets.

### Task 1: Project foundation and configuration

**Files:**
- Create: `pyproject.toml`
- Create: `src/deepseek_fastapi_agent/__init__.py`
- Create: `src/deepseek_fastapi_agent/config.py`
- Create: `.env.example`
- Create: `.gitignore`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `Settings` with `deepseek_api_key: str | None`, `deepseek_model: str`, and `deepseek_base_url: str`.

- [ ] **Step 1: Write the failing configuration test**

```python
from deepseek_fastapi_agent.config import Settings

def test_settings_has_deepseek_defaults() -> None:
    settings = Settings(deepseek_api_key="test-key")
    assert settings.deepseek_model == "deepseek-v4-flash"
    assert settings.deepseek_base_url == "https://api.deepseek.com"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL because `deepseek_fastapi_agent.config` does not exist.

- [ ] **Step 3: Implement settings and project metadata**

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"
```

- [ ] **Step 4: Run the configuration test**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src tests .env.example .gitignore
git commit -m "chore: initialize agent project"
```

### Task 2: Domain ports and conversation repository

**Files:**
- Create: `src/deepseek_fastapi_agent/domain.py`
- Create: `src/deepseek_fastapi_agent/repository.py`
- Test: `tests/test_repository.py`

**Interfaces:**
- Produces: `ChatRequest`, `ChatResult`, `ConversationRepository`, `AgentRunner`, and `InMemoryConversationRepository`.

- [ ] **Step 1: Write the failing repository test**

```python
def test_repository_appends_and_returns_history() -> None:
    repository = InMemoryConversationRepository()
    repository.append("c-1", "user", "你好")
    assert repository.history("c-1") == [("user", "你好")]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_repository.py -v`
Expected: FAIL because the repository module does not exist.

- [ ] **Step 3: Implement the in-memory repository**

```python
class InMemoryConversationRepository:
    def __init__(self) -> None:
        self._conversations: dict[str, list[tuple[str, str]]] = {}

    def append(self, conversation_id: str, role: str, content: str) -> None:
        self._conversations.setdefault(conversation_id, []).append((role, content))
```

- [ ] **Step 4: Run repository tests**

Run: `pytest tests/test_repository.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/deepseek_fastapi_agent/domain.py src/deepseek_fastapi_agent/repository.py tests/test_repository.py
git commit -m "feat: add conversation repository port"
```

### Task 3: Agent runner and chat service

**Files:**
- Create: `src/deepseek_fastapi_agent/agent.py`
- Create: `src/deepseek_fastapi_agent/service.py`
- Test: `tests/test_service.py`

**Interfaces:**
- Consumes: `Settings`, `ConversationRepository`, `AgentRunner`.
- Produces: `ChatService.reply(request: ChatRequest, request_id: str) -> ChatResult` and `DeepSeekLangGraphRunner`.

- [ ] **Step 1: Write the failing service test using a fake runner**

```python
def test_service_saves_user_and_assistant_messages() -> None:
    service = ChatService(repository=InMemoryConversationRepository(), runner=FakeRunner("欢迎"))
    result = service.reply(ChatRequest(message="你好"), request_id="r-1")
    assert result.answer == "欢迎"
    assert result.request_id == "r-1"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_service.py -v`
Expected: FAIL because `ChatService` does not exist.

- [ ] **Step 3: Implement service and runner**

```python
def reply(self, request: ChatRequest, request_id: str) -> ChatResult:
    conversation_id = request.conversation_id or str(uuid4())
    self._repository.append(conversation_id, "user", request.message)
    answer = self._runner.run(self._repository.history(conversation_id))
    self._repository.append(conversation_id, "assistant", answer)
    return ChatResult(conversation_id=conversation_id, answer=answer, request_id=request_id)
```

`DeepSeekLangGraphRunner` must build `ChatOpenAI` using `Settings.deepseek_base_url` and expose a UTC-time tool through a LangGraph prebuilt ReAct agent.

- [ ] **Step 4: Run service tests**

Run: `pytest tests/test_service.py -v`
Expected: PASS without network access.

- [ ] **Step 5: Commit**

```bash
git add src/deepseek_fastapi_agent/agent.py src/deepseek_fastapi_agent/service.py tests/test_service.py
git commit -m "feat: add deepseek agent service"
```

### Task 4: FastAPI adapter and operational behavior

**Files:**
- Create: `src/deepseek_fastapi_agent/api.py`
- Create: `src/deepseek_fastapi_agent/main.py`
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `ChatService.reply(request: ChatRequest, request_id: str) -> ChatResult`.
- Produces: `create_app(service: ChatService | None = None) -> FastAPI` and `app`.

- [ ] **Step 1: Write failing API tests**

```python
def test_health_returns_ok(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}

def test_chat_returns_request_id(client: TestClient) -> None:
    response = client.post("/api/v1/chat", json={"message": "你好"})
    assert response.status_code == 200
    assert response.json()["request_id"]
```

- [ ] **Step 2: Run API tests to verify they fail**

Run: `pytest tests/test_api.py -v`
Expected: FAIL because the application factory does not exist.

- [ ] **Step 3: Implement app factory and endpoints**

```python
@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request, service: ChatService = Depends(get_service)) -> ChatResponse:
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    return ChatResponse.model_validate(service.reply(payload, request_id))
```

Map a missing `DEEPSEEK_API_KEY` to `503` with `{"detail": "Agent service is not configured"}`.

- [ ] **Step 4: Run API tests**

Run: `pytest tests/test_api.py -v`
Expected: PASS with a fake runner injected into `create_app`.

- [ ] **Step 5: Commit**

```bash
git add src/deepseek_fastapi_agent/api.py src/deepseek_fastapi_agent/main.py tests/test_api.py
git commit -m "feat: expose chat api"
```

### Task 5: Delivery assets and full verification

**Files:**
- Create: `README.md`
- Create: `Dockerfile`
- Create: `.github/workflows/test.yml`
- Test: `tests/test_config.py`, `tests/test_repository.py`, `tests/test_service.py`, `tests/test_api.py`

**Interfaces:**
- Produces: documented local and container startup instructions.

- [ ] **Step 1: Write a README command verification test**

```python
def test_readme_mentions_required_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "uv run pytest" in readme
    assert "uvicorn deepseek_fastapi_agent.main:app" in readme
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_readme.py -v`
Expected: FAIL because `README.md` does not exist.

- [ ] **Step 3: Add Docker, CI, and README instructions**

The README must include setup with `uv sync`, `.env` creation from `.env.example`, `uv run pytest`, `uv run uvicorn deepseek_fastapi_agent.main:app --reload`, Docker build/run commands, `/docs`, and the explicit production checklist: authentication, rate limiting, Redis/PostgreSQL state, CORS allow-list, and secret management.

- [ ] **Step 4: Run all tests and build package**

Run: `uv run pytest -v && uv build`
Expected: all tests PASS and a wheel plus source distribution are created in `dist/`.

- [ ] **Step 5: Commit**

```bash
git add README.md Dockerfile .github tests
git commit -m "docs: add deployment guidance"
```

