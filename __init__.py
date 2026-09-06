"""Causal experience memory for Hermes Agent."""

from __future__ import annotations

import json
import logging
from typing import Any

from . import schema, tools
from .causal import build_graph
from .extractor import extract_observations
from .store import CausalStore, now

logger = logging.getLogger(__name__)


def register(ctx: Any) -> None:
    store = CausalStore()
    settings = ctx.get_config() or {}
    max_events = int(settings.get("max_trace_events", 80))
    last_session_id: str | None = None

    def trace_id(task_id: str | None, kwargs: dict[str, Any]) -> str:
        return str(kwargs.get("session_id") or task_id or "default")

    def on_post_tool_call(tool_name: str, args: dict[str, Any], result: str, task_id: str, duration_ms: int, **kwargs: Any) -> None:
        if tool_name.startswith(("causal_", "temporal_")):
            return
        store.append_trace(trace_id(task_id, kwargs), {"kind": "tool_call", "timestamp": now(), "tool": tool_name,
            "arguments": args, "result": result, "duration_ms": duration_ms}, max_events)

    def on_pre_llm_call(session_id: str, user_message: str, **kwargs: Any) -> None:
        # Preserve user intent in the same trace without injecting additional context.
        nonlocal last_session_id
        last_session_id = session_id
        store.append_trace(session_id, {"kind": "user_message", "timestamp": now(), "content": user_message}, max_events)
        return None

    def learn(trace_key: str, task_hint: str | None = None) -> str:
        extracted = extract_observations(ctx, store.trace(trace_key), task_hint)
        task = task_hint or extracted["task"]
        observations = store.add_observations(task, extracted["observations"])
        graph = build_graph(task, observations)
        path = store.save_graph(graph)
        return json.dumps({"status": "candidate", "task": task, "path": str(path), "observation_count": len(observations)}, ensure_ascii=False)

    def on_session_end(session_id: str, completed: bool, **kwargs: Any) -> None:
        if completed and settings.get("auto_extract", False):
            try:
                learn(session_id)
            except Exception as exc:
                logger.warning("Causal extraction skipped for %s: %s", session_id, exc)

    def causal_learn(raw_args: str) -> str:
        # Explicit command keeps extraction aligned with /learn-like human intent and avoids surprise spend.
        task_hint = raw_args.strip() or None
        # Slash-command handlers receive only raw text, not session metadata. The most recent
        # pre-LLM hook gives interactive CLI sessions their current trace; an explicit session
        # id remains available for headless or multi-session uses.
        trace_key = last_session_id or "default"
        if task_hint and task_hint.startswith("session:"):
            trace_key = task_hint.removeprefix("session:").strip()
            task_hint = None
        try:
            return learn(trace_key, task_hint)
        except Exception as exc:
            return json.dumps({"error": str(exc), "hint": "Pass the current session/task id, or enable auto_extract."})

    ctx.register_tool(name="causal_check", toolset="causal_memory", schema=schema.CAUSAL_CHECK,
                      handler=lambda args, **kw: tools.check(args, store, **kw))
    ctx.register_tool(name="causal_query", toolset="causal_memory", schema=schema.CAUSAL_QUERY,
                      handler=lambda args, **kw: tools.query(args, store, **kw))
    ctx.register_tool(name="causal_record_observation", toolset="causal_memory", schema=schema.CAUSAL_RECORD_OBSERVATION,
                      handler=lambda args, **kw: tools.record_observation(args, store, **kw))
    ctx.register_hook("post_tool_call", on_post_tool_call)
    ctx.register_hook("pre_llm_call", on_pre_llm_call)
    ctx.register_hook("on_session_end", on_session_end)
    ctx.register_command("causal-learn", causal_learn, "Extract observations and update causal candidates from the current task trace.", "[task-or-session-id]")
