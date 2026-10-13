"""Optional AI provider connection, configured only on the backend."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any


def generate_answer(
    question: str,
    discipline: str,
    goal: str,
    records: list[dict[str, Any]],
    sources: list[dict[str, str]],
) -> tuple[str | None, str | None]:
    """Ask an OpenAI-compatible chat-completions endpoint when configured.

    Returns (answer, error). If settings are blank, returns (None, None),
    allowing the API route to report that AI setup is still pending.
    """
    endpoint = os.getenv("AI_CHAT_COMPLETIONS_URL", "").strip()
    api_key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "").strip()
    if not endpoint or not api_key or not model:
        return None, None

    if not records:
        return None, "知识库中还没有可供回答的问题相关资料。"

    context = json.dumps({"knowledge_records": records, "sources": sources}, ensure_ascii=False)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是公共卫生与计算机科学交叉研究的科研辅助助手。"
                    "只依据用户提供的知识库资料回答；资料不足时明确说明不足。"
                    "区分资料中的事实与推断，不编造定义、论文、作者或来源。"
                    "给出方法时说明适用条件和局限，并引用提供的来源编号。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"用户学科：{discipline}\n用户目标：{goal}\n研究问题：{question}\n\n"
                    f"检索到的项目知识库资料（JSON）：\n{context}"
                ),
            },
        ],
        "temperature": 0.2,
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        answer = result["choices"][0]["message"]["content"]
        return str(answer), None
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
        # Do not return request headers or the API key in an error message.
        return None, f"AI 服务调用失败（{type(exc).__name__}）。请检查服务地址、模型名称和网络连接。"
