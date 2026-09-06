"""Durable storage for raw traces, observations, and derived causal graphs."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized[:80] or "untitled-task"


class CausalStore:
    def __init__(self, root: Path | None = None) -> None:
        if root is None:
            override = os.environ.get("HERMES_CAUSAL_MEMORY_DIR") or os.environ.get("HERMES_TEMPORAL_MEMORY_DIR")
            if override:
                root = Path(override)
            else:
                try:
                    from plugins.plugin_storage import plugin_data_dir
                    root = plugin_data_dir("causal-memory")
                except ImportError:
                    root = Path.home() / ".hermes" / "plugin-data" / "causal-memory"
        self.root = root
        self.traces, self.observations, self.graphs = root / "traces", root / "observations", root / "causal"
        for directory in (self.traces, self.observations, self.graphs):
            directory.mkdir(parents=True, exist_ok=True)

    def append_trace(self, trace_id: str, event: dict[str, Any], max_events: int) -> None:
        path = self.traces / f"{slug(trace_id)}.json"
        trace = self.read_json(path, {"trace_id": trace_id, "events": []})
        trace["events"].append(event)
        trace["events"] = trace["events"][-max(1, max_events):]
        trace["updated_at"] = now()
        self.write_json(path, trace)

    def trace(self, trace_id: str) -> dict[str, Any]:
        return self.read_json(self.traces / f"{slug(trace_id)}.json", {"trace_id": trace_id, "events": []})

    def add_observations(self, task: str, observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        path = self.observations / f"{slug(task)}.json"
        document = self.read_json(path, {"task": task, "observations": []})
        document["observations"].extend(observations)
        document["updated_at"] = now()
        self.write_json(path, document)
        return document["observations"]

    def observations_for(self, task: str) -> list[dict[str, Any]]:
        document = self.read_json(self.observations / f"{slug(task)}.json", {"observations": []})
        return document["observations"]

    def save_graph(self, graph: dict[str, Any]) -> Path:
        document = {**graph, "updated_at": now(), "format": "hermes-causal-memory/v1"}
        path = self.graphs / f"{slug(graph['task'])}.yaml"
        self.write_json(path, document)
        return path

    def find_graphs(self, query: str) -> list[dict[str, Any]]:
        terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        matches: list[dict[str, Any]] = []
        for path in self.graphs.glob("*.yaml"):
            graph = self.read_json(path, None)
            if not graph:
                continue
            haystack = json.dumps(graph, ensure_ascii=False).lower()
            score = sum(term in haystack for term in terms)
            if score:
                matches.append({"score": score, "path": str(path), "graph": graph})
        return sorted(matches, key=lambda item: item["score"], reverse=True)

    @staticmethod
    def read_json(path: Path, default: Any) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default

    @staticmethod
    def write_json(path: Path, value: Any) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)
