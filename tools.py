"""Hermes tool handlers for the temporal-memory plugin."""

from __future__ import annotations

import json
from typing import Any

from .store import TemporalStore, now


def record_event(args: dict[str, Any], store: TemporalStore, **kwargs: Any) -> str:
    task = args.get("task", "").strip()
    event = args.get("event", "").strip()
    source = args.get("source", "").strip()
    if not all((task, event, source)):
        return json.dumps({"error": "task, event, and source are required"})
    store.append_trace(task, {"kind": "observed_event", "timestamp": now(), "event": event,
                              "source": source, "state": args.get("state", ""), "details": args.get("details", "")}, 80)
    return json.dumps({"recorded": True, "task": task, "event": event})


def query(args: dict[str, Any], store: TemporalStore, **kwargs: Any) -> str:
    matches = store.find_rules(args.get("query", ""))[:5]
    return json.dumps({"matches": matches}, ensure_ascii=False)


def check(args: dict[str, Any], store: TemporalStore, **kwargs: Any) -> str:
    task, action = args.get("task", ""), args.get("action", "")
    states = set(args.get("current_states") or [])
    exact = next((match["document"] for match in store.find_rules(task)
                  if match["document"].get("task", "").lower() == task.lower()), None)
    if not exact:
        return json.dumps({"allowed": True, "reason": "No learned temporal rule for this task."})
    missing = [rule for rule in exact.get("temporal_constraints", [])
               if rule.get("after") == action and rule.get("before") not in states]
    return json.dumps({"allowed": not missing, "action": action, "missing": missing,
                       "reason": "All known prerequisites are satisfied." if not missing else "A learned prerequisite is not satisfied."}, ensure_ascii=False)
