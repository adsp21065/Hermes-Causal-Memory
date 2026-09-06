"""Extract observations; causal claims are computed, never generated, by the LLM."""

from __future__ import annotations

import json
from typing import Any

from .schema import OBSERVATION_SCHEMA

INSTRUCTIONS = """Extract grounded execution observations from this Hermes trace. Do not infer or claim causality.
For each attempt list only supported context conditions, facts before the attempt (causes), actions, observed effects,
outcome, and concise evidence. Use lower-case dotted identifiers when possible. Record negative effects such as
trigger.missed when observed. If ambiguous, use outcome unknown and empty lists instead of guessing.
The host calculates probabilities and causal candidates."""


def extract_observations(ctx: Any, trace: dict[str, Any], task_hint: str | None = None) -> dict[str, Any]:
    events = trace.get("events", [])
    if not events:
        raise ValueError("No events recorded for this task.")
    payload = {"task_hint": task_hint or trace.get("trace_id"), "events": events}
    result = ctx.llm.complete_structured(
        instructions=INSTRUCTIONS, input=[{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        json_schema=OBSERVATION_SCHEMA, purpose="causal-memory.extract-observations", temperature=0.0, max_tokens=1400,
    )
    if not result.parsed:
        raise ValueError("Extractor returned no valid structured observations.")
    return result.parsed
