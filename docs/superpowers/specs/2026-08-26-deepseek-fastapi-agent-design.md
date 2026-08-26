# DeepSeek FastAPI Agent Design

## Goal

Create a small, production-oriented backend foundation for a public-facing AI agent. It must expose a stable FastAPI chat API, use DeepSeek by default, and make future tools, persistent sessions, and additional model providers additive changes.

## Scope

The first version supplies one authenticated-at-the-application-boundary-ready chat endpoint, request validation, structured errors, request IDs, logging, an in-memory conversation store, and a single LangGraph ReAct agent. It includes one deterministic demonstration tool (current UTC time) so the tool boundary is testable without external services.

The first version does not implement user accounts, billing, rate limiting, a browser UI, RAG, production database migrations, or external tool credentials. Their intended integration points are defined without shipping unused infrastructure.

## Architecture

FastAPI is the HTTP adapter. It validates `ChatRequest`, generates or accepts a request ID, and delegates to `ChatService`. `ChatService` owns conversation loading/saving through a `ConversationRepository` protocol and executes the LangGraph agent. The agent builder lives behind `AgentRunner`, isolating LangGraph and the DeepSeek client from HTTP concerns.

`Settings` loads configuration exclusively from the process environment or `.env` in local development. The model defaults to `deepseek-v4-flash`; the DeepSeek base URL and API key are configurable. No secret, token, or `.env` file is committed.

## API

`GET /health` returns `{ "status": "ok" }`.

`POST /api/v1/chat` accepts:

```json
{
  "message": "你好",
  "conversation_id": "optional-client-id"
}
```

It returns a server-generated or supplied `conversation_id`, the final agent `answer`, and `request_id`. Invalid or blank messages receive FastAPI validation errors. Missing or invalid DeepSeek configuration is returned as a non-secret `503` application error.

## State and Extensibility

The in-memory repository stores message histories by conversation ID for local development. Its protocol makes replacement with Redis or PostgreSQL possible without changing routes or agent code. The only initial tool returns the current UTC time; future business tools are registered in the agent builder and validated with the same tool-call boundary.

## Reliability and Safety

All application logs are structured and include the request ID. Error responses never include API keys or upstream body details. The API includes CORS configuration only from an explicit environment allow-list. Public deployment must place authentication, rate limiting, and a persistent repository in front of or alongside this starter before serving real users.

## Verification

pytest tests will cover health, chat request validation, request-ID propagation, service state behavior, and mapping of unavailable model configuration to `503`. A `MockAgentRunner` is injected in API tests so tests never call DeepSeek. The README documents local setup, test execution, OpenAPI access, Docker use, configuration, and the production hardening steps outside this starter's scope.

