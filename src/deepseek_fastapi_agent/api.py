import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from deepseek_fastapi_agent.agent import DeepSeekLangGraphRunner
from deepseek_fastapi_agent.config import Settings
from deepseek_fastapi_agent.domain import ChatRequest
from deepseek_fastapi_agent.repository import InMemoryConversationRepository
from deepseek_fastapi_agent.service import ChatService

logger = logging.getLogger(__name__)


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    request_id: str


def build_default_service() -> ChatService:
    settings = Settings()
    try:
        runner = DeepSeekLangGraphRunner(settings)
    except ValueError as error:
        raise HTTPException(status_code=503, detail="Agent service is not configured") from error
    return ChatService(repository=InMemoryConversationRepository(), runner=runner)


def create_app(service: ChatService | None = None) -> FastAPI:
    app = FastAPI(title="DeepSeek FastAPI Agent", version="0.1.0")
    settings = Settings()
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=False,
            allow_methods=["POST", "GET"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info("request_complete", extra={"request_id": request_id, "status_code": response.status_code})
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/chat", response_model=ChatResponse)
    def chat(payload: ChatRequest, request: Request) -> ChatResponse:
        active_service = service or build_default_service()
        result = active_service.reply(payload, request.state.request_id)
        return ChatResponse(**result.__dict__)

    return app

