"""LLM extraction prompt and trace conversion."""

from __future__ import annotations

import json
from typing import Any

from .schema import TEMPORAL_DOCUMENT_SCHEMA

INSTRUCTIONS = """Extract only supported temporal/causal facts from this Hermes execution trace.
Return a candidate rule, not canonical truth. Do not invent device states, events, or ordering.
Use MUST_PRECEDE when `before` must occur before `after`; MUST_WAIT_FOR when an action must await an event/state;
and REQUIRES when `after` cannot happen without `before`. Normalize identifiers as lower-case dotted names when possible.
If evidence is insufficient, return empty arrays. Include failed attempts and their recovery only when present in evidence."""


def extract(ctx: Any, trace: dict[str, Any], task_hint: str | None = None) -> dict[str, Any]:
    events = trace.get("events", [])
    if not events:
        raise ValueError("No events recorded for this task.")
    payload = {"task_hint": task_hint or trace.get("trace_id"), "events": events}
    result = ctx.llm.complete_structured(
        instructions=INSTRUCTIONS,
        input=[{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        json_schema=TEMPORAL_DOCUMENT_SCHEMA,
        purpose="temporal-memory.extract",
        temperature=0.0,
        max_tokens=1200,
    )
    if not result.parsed:
        raise ValueError("Extractor returned no valid structured document.")
    document = result.parsed
    document["status"] = "candidate"
    document["evidence"] = {"trace_id": trace.get("trace_id"), "event_count": len(events)}
    return document
