from typing import Dict, Any
from app.schemas.simulation import ScenarioResult, ImpactResult, SimulationResponse

def calculate_risk_score(metrics: dict) -> int:
    """
    Calculates a risk score based on a weighted average of normalized metrics.
    Output: 0–100 risk score
    """
    weights = {
        "lead_conversion_rate": 0.30,
        "whatsapp_response_rate": 0.25,
        "data_completeness": 0.20,
        "avg_response_time": 0.15,
        "duplicate_rate": 0.10
    }

    normalized = {
        "lead_conversion_rate": max(0, 100 - (metrics.get("lead_conversion_rate", 0) * 10)),
        "whatsapp_response_rate": max(0, 100 - metrics.get("whatsapp_response_rate", 0)),
        "data_completeness": max(0, 100 - metrics.get("data_completeness", 0)),
        "avg_response_time": min(100, metrics.get("avg_response_time", 0) / 2),
        "duplicate_rate": min(100, metrics.get("duplicate_rate", 0) * 10)
    }

    score = sum(normalized[k] * w for k, w in weights.items())
    return int(min(100, score))

def _map_risk_to_decision(risk_score: int) -> Dict[str, str]:
    """Maps a risk score to a decision level and priority."""
    if risk_score >= 75:
        return {"decision": "CRITICAL", "priority": "P0"}
    if risk_score >= 50:
        return {"decision": "HIGH", "priority": "P1"}
    if risk_score >= 30:
        return {"decision": "MEDIUM", "priority": "P2"}
    return {"decision": "LOW", "priority": "P3"}

def simulate_scenario(
    base_metrics: Dict[str, Any],
    overrides: Dict[str, float]
) -> SimulationResponse:
    """
    Merges base metrics with simulation overrides, recalculates risk, and compares outcomes.
    """
    baseline_score = calculate_risk_score(base_metrics)
    baseline_decision = _map_risk_to_decision(baseline_score)
    baseline_result = ScenarioResult(risk_score=baseline_score, **baseline_decision)

    simulated_metrics = base_metrics.copy()
    for key, improvement in overrides.items():
        if key in simulated_metrics:
            original_value = simulated_metrics[key]
            new_value = original_value * (1 + improvement)
            if "rate" in key or "completeness" in key:
                simulated_metrics[key] = max(0, min(100, new_value))
            else:
                simulated_metrics[key] = max(0, new_value)

    simulated_score = calculate_risk_score(simulated_metrics)
    simulated_decision = _map_risk_to_decision(simulated_score)
    simulated_result = ScenarioResult(risk_score=simulated_score, **simulated_decision)

    impact_result = ImpactResult(
        risk_delta=simulated_score - baseline_score,
        decision_changed=(baseline_result.decision != simulated_result.decision),
        priority_changed=(baseline_result.priority != simulated_result.priority)
    )

    return SimulationResponse(
        baseline=baseline_result,
        simulated=simulated_result,
        impact=impact_result
    )
