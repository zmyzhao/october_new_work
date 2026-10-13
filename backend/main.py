"""Local API server: serves the page and connects retrieval to the AI module."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.ai_service import generate_answer
from backend.retrieval import find_related, find_sources

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(title="知域：公共卫生 × 计算机科学", version="0.1.0")


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    discipline: str = Field(default="公共卫生", max_length=40)
    goal: str = Field(default="概念对应与方法建议", max_length=100)


@app.get("/")
def home() -> FileResponse:
    """Open the existing prototype page from the local server."""
    return FileResponse(PROJECT_ROOT / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "Python 后端已启动"}


@app.post("/api/query")
def query(request: QueryRequest) -> dict[str, object]:
    """Retrieve project records, then call the configured AI model if available."""
    records = find_related(request.question, request.discipline)
    sources = find_sources(records)

    if not records:
        return {
            "mode": "knowledge_base_empty",
            "answer": "知识库模板目前还没有资料。请先在 data 文件夹的 CSV 表格中填写并核验概念、方法或映射关系。",
            "records": [],
            "sources": [],
        }

    answer, error = generate_answer(
        question=request.question,
        discipline=request.discipline,
        goal=request.goal,
        records=records,
        sources=sources,
    )
    if answer:
        return {"mode": "ai", "answer": answer, "records": records, "sources": sources}
    if error:
        return {"mode": "ai_error", "answer": error, "records": records, "sources": sources}

    return {
        "mode": "retrieval_only",
        "answer": "已从本地知识表中找到相关条目。AI API 尚未配置，因此暂时只返回检索资料。",
        "records": records,
        "sources": sources,
    }
