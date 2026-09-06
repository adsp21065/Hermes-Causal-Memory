"""Durable, dependency-free storage. JSON is valid YAML 1.2, so documents use .yaml."""

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


class TemporalStore:
    def __init__(self, root: Path | None = None) -> None:
        if root is None:
            override = os.environ.get("HERMES_TEMPORAL_MEMORY_DIR")
            if override:
                root = Path(override)
            else:
                try:
                    from plugins.plugin_storage import plugin_data_dir
                    root = plugin_data_dir("temporal-memory")
                except ImportError:
                    root = Path.home() / ".hermes" / "plugin-data" / "temporal-memory"
        self.root = root
        self.traces = root / "traces"
        self.rules = root / "temporal"
        self.traces.mkdir(parents=True, exist_ok=True)
        self.rules.mkdir(parents=True, exist_ok=True)

    def _trace_path(self, trace_id: str) -> Path:
        return self.traces / f"{slug(trace_id)}.json"

    def append_trace(self, trace_id: str, event: dict[str, Any], max_events: int) -> None:
        path = self._trace_path(trace_id)
        trace = self.read_json(path, {"trace_id": trace_id, "events": []})
        trace["events"].append(event)
        trace["events"] = trace["events"][-max(1, max_events):]
        trace["updated_at"] = now()
        self.write_json(path, trace)

    def trace(self, trace_id: str) -> dict[str, Any]:
        return self.read_json(self._trace_path(trace_id), {"trace_id": trace_id, "events": []})

    def save_rule(self, document: dict[str, Any]) -> Path:
        document = {**document, "updated_at": now(), "format": "hermes-temporal-memory/v1"}
        path = self.rules / f"{slug(document['task'])}.yaml"
        self.write_json(path, document)
        return path

    def find_rules(self, query: str) -> list[dict[str, Any]]:
        terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        matches: list[dict[str, Any]] = []
        for path in self.rules.glob("*.yaml"):
            document = self.read_json(path, None)
            if not document:
                continue
            haystack = json.dumps(document, ensure_ascii=False).lower()
            score = sum(term in haystack for term in terms)
            if score:
                matches.append({"score": score, "path": str(path), "document": document})
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
