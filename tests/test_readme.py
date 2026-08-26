from pathlib import Path


def test_readme_mentions_required_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "uv run pytest" in readme
    assert "uv run uvicorn deepseek_fastapi_agent.main:app" in readme

