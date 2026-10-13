"""Load the project's CSV knowledge files and find simple keyword matches.

This is a starter retrieval method, not embedding/vector search. Keep source
attribution in the CSV rows so every result can be checked by a person.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

KNOWLEDGE_FILES = {
    "concept": "concepts.csv",
    "method": "methods.csv",
    "mapping": "mappings.csv",
}


def _read_csv(filename: str) -> list[dict[str, str]]:
    """Read one UTF-8 CSV file. An empty template simply returns no rows."""
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return [row for row in csv.DictReader(stream) if any(value.strip() for value in row.values() if value)]


def _tokens(text: str) -> list[str]:
    """A deliberately simple baseline tokenizer for Chinese and English text."""
    return [part.lower() for part in re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", text)]


def find_related(question: str, discipline: str, limit: int = 6) -> list[dict[str, Any]]:
    """Return the most relevant non-empty concept, method, and mapping rows."""
    query_tokens = set(_tokens(question))
    candidates: list[dict[str, Any]] = []

    for record_type, filename in KNOWLEDGE_FILES.items():
        for row in _read_csv(filename):
            searchable_text = " ".join(value for value in row.values() if value)
            record_tokens = set(_tokens(searchable_text))
            score = len(query_tokens & record_tokens)
            if discipline and discipline in searchable_text:
                score += 2
            if score:
                candidates.append({"type": record_type, "score": score, "data": row})

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:limit]


def find_sources(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Resolve source IDs referenced by retrieved knowledge rows."""
    wanted: set[str] = set()
    for record in records:
        raw_ids = record["data"].get("source_ids", "")
        wanted.update(part.strip() for part in raw_ids.split(";") if part.strip())

    if not wanted:
        return []
    return [row for row in _read_csv("sources.csv") if row.get("id", "").strip() in wanted]
