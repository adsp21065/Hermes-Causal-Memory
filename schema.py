"""Schemas for the Hermes temporal-memory plugin."""

TEMPORAL_DOCUMENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["task", "summary", "preconditions", "states", "events", "temporal_constraints", "failure_patterns"],
    "properties": {
        "task": {"type": "string"},
        "summary": {"type": "string"},
        "preconditions": {"type": "array", "items": {"type": "string"}},
        "states": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}},
        "events": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": ["name", "source"], "properties": {"name": {"type": "string"}, "source": {"type": "string"}}}},
        "temporal_constraints": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": ["type", "before", "after", "reason"], "properties": {
                "type": {"type": "string", "enum": ["MUST_PRECEDE", "MUST_WAIT_FOR", "REQUIRES"]},
                "before": {"type": "string"}, "after": {"type": "string"}, "reason": {"type": "string"}}}},
        "failure_patterns": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": ["condition", "result", "recovery"], "properties": {
                "condition": {"type": "string"}, "result": {"type": "string"}, "recovery": {"type": "string"}}}},
    },
}

TEMPORAL_CHECK = {
    "name": "temporal_check",
    "description": "Check whether an action is allowed by learned temporal constraints. Use before an action whose ordering or prerequisite matters.",
    "parameters": {"type": "object", "properties": {
        "task": {"type": "string", "description": "Known task/workflow name."},
        "action": {"type": "string", "description": "The action to validate."},
        "current_states": {"type": "array", "items": {"type": "string"}, "description": "Facts currently true, e.g. scope.armed."},
    }, "required": ["task", "action"]},
}

TEMPORAL_QUERY = {
    "name": "temporal_query",
    "description": "Retrieve learned temporal rules, event ordering, and failures for a task or natural-language query.",
    "parameters": {"type": "object", "properties": {
        "query": {"type": "string", "description": "Task name or a concise workflow description."},
    }, "required": ["query"]},
}

TEMPORAL_RECORD_EVENT = {
    "name": "temporal_record_event",
    "description": "Record an observed event or state transition when a tool result alone does not expose it.",
    "parameters": {"type": "object", "properties": {
        "task": {"type": "string", "description": "Current task or workflow identifier."},
        "event": {"type": "string", "description": "Observed event or action name."},
        "source": {"type": "string", "description": "Agent, device, or subsystem that observed it."},
        "state": {"type": "string", "description": "Optional state reached, e.g. scope.armed."},
        "details": {"type": "string", "description": "Optional concise evidence."},
    }, "required": ["task", "event", "source"]},
}
