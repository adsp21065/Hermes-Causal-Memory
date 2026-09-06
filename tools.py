"""Hermes tool handlers for the causal-memory plugin."""

from __future__ import annotations

import json
from typing import Any

from .causal import build_graph
from .store import CausalStore, now


def record_observation(args: dict[str, Any], store: CausalStore, **kwargs: Any) -> str:
    task = args.get("task", "").strip()
    actions, effects = args.get("actions") or [], args.get("effects") or []
    if not task or not actions or not effects:
        return json.dumps({"error": "task, actions, and effects are required"})
    observation = {"timestamp": now(), "context": args.get("context") or [], "causes": args.get("causes") or [],
                   "actions": actions, "effects": effects, "outcome": args.get("outcome", "unknown"),
                   "evidence": args.get("evidence", "recorded directly")}
    observations = store.add_observations(task, [observation])
    store.save_graph(build_graph(task, observations))
    return json.dumps({"recorded": True, "task": task, "observation": observation}, ensure_ascii=False)


def query(args: dict[str, Any], store: CausalStore, **kwargs: Any) -> str:
    matches = store.find_graphs(args.get("query", ""))[:5]
    return json.dumps({"matches": matches}, ensure_ascii=False)


def check(args: dict[str, Any], store: CausalStore, **kwargs: Any) -> str:
    task, action = args.get("task", ""), args.get("planned_action", "")
    facts = set(args.get("current_facts") or [])
    exact = next((match["graph"] for match in store.find_graphs(task)
                  if match["graph"].get("task", "").lower() == task.lower()), None)
    if not exact:
        return json.dumps({"warning": False, "reason": "No learned causal graph for this task."})
    warnings = [relation for relation in exact.get("relations", [])
                if relation.get("condition", {}).get("action") == action and relation["cause"] not in facts
                and relation["statistics"]["risk_difference"] >= 0.25]
    return json.dumps({"warning": bool(warnings), "planned_action": action, "missing_facts": [x["cause"] for x in warnings],
                       "relationships": warnings, "reason": "Historical evidence indicates a missing condition." if warnings else "No strong missing-condition signal."}, ensure_ascii=False)
