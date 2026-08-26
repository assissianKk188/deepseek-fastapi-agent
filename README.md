# DeepSeek FastAPI Agent

一个面向公众产品的、可扩展的 DeepSeek Agent 后端起点。它使用 FastAPI 提供 HTTP 接口，用 LangGraph 编排 Agent，并通过 DeepSeek 的 OpenAI 兼容 API 调用模型。

## 本地运行

```powershell
uv sync --all-groups
Copy-Item .env.example .env
uv run uvicorn deepseek_fastapi_agent.main:app --reload
```

详见仓库中的完整文档。