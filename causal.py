"""Deterministic conditional-probability statistics for causal candidates."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any


def _p(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def build_graph(task: str, observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Build action-conditioned associations; they remain candidates, not causal proof."""
    by_action: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        for action in set(observation.get("actions", [])):
            by_action[action].append(observation)
    relations: list[dict[str, Any]] = []
    for action, samples in by_action.items():
        causes = sorted({fact for sample in samples for fact in sample.get("causes", [])})
        effects = sorted({fact for sample in samples for fact in sample.get("effects", [])})
        for cause in causes:
            for effect in effects:
                both = cause_only = effect_only = neither = 0
                for sample in samples:
                    has_cause = cause in sample.get("causes", [])
                    has_effect = effect in sample.get("effects", [])
                    if has_cause and has_effect: both += 1
                    elif has_cause: cause_only += 1
                    elif has_effect: effect_only += 1
                    else: neither += 1
                p_with, p_without = _p(both, both + cause_only), _p(effect_only, effect_only + neither)
                if p_with is None or p_without is None:
                    continue
                delta, n = p_with - p_without, len(samples)
                confidence = round(min(0.99, abs(delta) * math.sqrt(n / (n + 10))), 4)
                relations.append({"cause": cause, "effect": effect, "condition": {"action": action},
                    "statistics": {"observations": n, "cause_present_effect_present": both,
                        "cause_present_effect_absent": cause_only, "cause_absent_effect_present": effect_only,
                        "cause_absent_effect_absent": neither, "p_effect_given_cause": p_with,
                        "p_effect_given_no_cause": p_without, "risk_difference": round(delta, 4),
                        "lift": round(p_with / p_without, 4) if p_without else None},
                    "confidence": confidence,
                    "status": "candidate_cause" if n >= 8 and delta >= 0.25 else "observed_correlation"})
    return {"task": task, "observation_count": len(observations),
            "relations": sorted(relations, key=lambda item: (item["confidence"], item["statistics"]["observations"]), reverse=True)}
