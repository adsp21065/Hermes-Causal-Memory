"""Schemas exposed by the Hermes causal-memory plugin."""

OBSERVATION_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["task", "observations"],
    "properties": {"task": {"type": "string"}, "observations": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["context", "causes", "actions", "effects", "outcome", "evidence"],
        "properties": {"context": {"type": "array", "items": {"type": "string"}},
            "causes": {"type": "array", "items": {"type": "string"}}, "actions": {"type": "array", "items": {"type": "string"}},
            "effects": {"type": "array", "items": {"type": "string"}},
            "outcome": {"type": "string", "enum": ["success", "failure", "unknown"]}, "evidence": {"type": "string"}}}}}}

CAUSAL_CHECK = {
    "name": "causal_check",
    "description": "Check causal candidates before a planned action. Returns evidence-based warnings, never a hard block.",
    "parameters": {"type": "object", "properties": {
        "task": {"type": "string", "description": "Known task/workflow name."},
        "planned_action": {"type": "string", "description": "Action about to be performed."},
        "current_facts": {"type": "array", "items": {"type": "string"}, "description": "Facts currently true."},
    }, "required": ["task", "planned_action"]},
}

CAUSAL_QUERY = {
    "name": "causal_query",
    "description": "Retrieve statistically supported causal candidates, conditions, and conditional probabilities.",
    "parameters": {"type": "object", "properties": {
        "query": {"type": "string", "description": "Task name or a concise workflow description."},
    }, "required": ["query"]},
}

CAUSAL_RECORD_OBSERVATION = {
    "name": "causal_record_observation",
    "description": "Record a real-world state/action/result observation that tool output does not expose.",
    "parameters": {"type": "object", "properties": {
        "task": {"type": "string", "description": "Current task or workflow identifier."},
        "context": {"type": "array", "items": {"type": "string"}},
        "causes": {"type": "array", "items": {"type": "string"}},
        "actions": {"type": "array", "items": {"type": "string"}},
        "effects": {"type": "array", "items": {"type": "string"}},
        "outcome": {"type": "string", "enum": ["success", "failure", "unknown"]},
        "evidence": {"type": "string"},
    }, "required": ["task", "actions", "effects", "outcome"]},
}
