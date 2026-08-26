# DeepSeek FastAPI Agent

一个面向公众产品的、可扩展的 DeepSeek Agent 后端起点。它使用 FastAPI 提供 HTTP 接口，用 LangGraph 编排 Agent，并通过 DeepSeek 的 OpenAI 兼容 API 调用模型。

## 已包含

- `GET /health` 健康检查
- `POST /api/v1/chat` 有状态对话接口
- DeepSeek + LangGraph ReAct Agent 与一个安全的 UTC 时间工具
- 请求 ID、输入校验、结构化日志与可选 CORS 白名单
- 可替换的会话仓储接口（当前为进程内存实现）

## 本地运行

需要 Python 3.12 或更高版本及 [uv](https://docs.astral.sh/uv/)。

```powershell
uv sync --all-groups
Copy-Item .env.example .env
```

编辑 `.env`，填入你的 `DEEPSEEK_API_KEY`。随后启动服务：

```powershell
uv run uvicorn deepseek_fastapi_agent.main:app --reload
```

访问 `http://127.0.0.1:8000/docs` 查看并调试 API。

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/v1/chat -ContentType 'application/json' -Body '{"message":"现在几点？"}'
```

## 测试

```powershell
uv run pytest -v
```

所有测试注入本地 Fake Agent，不会产生 DeepSeek API 调用或费用。

## Docker

```powershell
docker build -t deepseek-fastapi-agent .
docker run --rm -p 8000:8000 --env-file .env deepseek-fastapi-agent
```

## 生产部署前必须补充

- 在网关或应用层加入用户认证与按用户/ IP 的限流。
- 用 Redis 或 PostgreSQL 实现 `ConversationRepository`，替代当前进程内存状态。
- 仅通过 `CORS_ORIGINS` 配置明确允许的前端域名。
- 用部署平台的密钥管理服务保存 `DEEPSEEK_API_KEY`，不要将 `.env` 上传或提交。
- 在接入订单、支付、写数据等工具前，为高风险操作增加权限校验与人工确认。

