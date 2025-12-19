from typing import List, Dict, Any
from app.schemas.decision import DecisionRecommendation, RecommendationPriority, SuggestedOwner
from app.schemas.rule_result import RuleResult
from app.core.security import UserRole

PERSONA_WEIGHTS = {
    UserRole.FOUNDER: 1.3,
    UserRole.SALES_MANAGER: 1.1,
    UserRole.OPS_CRM: 1.0,
    UserRole.VIEWER: 1.0
}

def check_confidence_threshold(confidence_score: float) -> RuleResult:
    passed = confidence_score >= 60
    return RuleResult(
        rule_id="CONFIDENCE_CHECK",
        passed=passed,
        weight=0.5,
        explanation=f"System confidence is {confidence_score}%, which is {'above' if passed else 'below'} the 60% threshold."
    )

def check_policy_violation(metrics: Dict[str, Any]) -> RuleResult:
    violation = metrics.get("duplicate_rate", 0) > 5
    return RuleResult(
        rule_id="POLICY_VIOLATION_CHECK",
        passed=not violation,
        weight=0.3,
        explanation=f"Data duplication rate is {metrics.get('duplicate_rate', 0)}%, which {'does not violate' if not violation else 'violates'} the policy."
    )

def check_data_completeness(metrics: Dict[str, Any]) -> RuleResult:
    passed = metrics.get("data_completeness", 0) >= 70
    return RuleResult(
        rule_id="COMPLETENESS_CHECK",
        passed=passed,
        weight=0.2,
        explanation=f"Data completeness is {metrics.get('data_completeness', 0)}%, which is {'above' if passed else 'below'} the 70% threshold."
    )

def explain_decision(decision: DecisionRecommendation, rule_results: List[RuleResult]) -> Dict[str, Any]:
    passed_rules = [r for r in rule_results if r.passed]
    failed_rules = [r for r in rule_results if not r.passed]
    summary = f"Recommendation '{decision.title}' is fully supported." if not failed_rules else f"Recommendation '{decision.title}' is generated despite {len(failed_rules)} warning(s)."
    return {
        "summary": summary,
        "contributing_factors": [r.explanation for r in passed_rules],
        "triggered_rule_ids": [r.rule_id for r in rule_results]
    }

def generate_recommendations(
    analytics_metrics: Dict[str, Any], 
    confidence_score: float,
    persona: UserRole
) -> List[DecisionRecommendation]:
    recommendations = []
    weight_multiplier = PERSONA_WEIGHTS.get(persona, 1.0)
    weighted_confidence = int(min(100, confidence_score * weight_multiplier))

    rule_results = [
        check_confidence_threshold(confidence_score),
        check_policy_violation(analytics_metrics),
        check_data_completeness(analytics_metrics)
    ]

    if all(r.passed for r in rule_results):
        rec = DecisionRecommendation(
            title="Proceed with Automated Outreach",
            recommendation="All system checks passed. It is safe to proceed with automated marketing campaigns.",
            priority=RecommendationPriority.HIGH if weighted_confidence >= 80 else RecommendationPriority.MEDIUM,
            confidence=weighted_confidence,
            rationale="High confidence and data quality allow for safe automation.",
            impacted_metrics=["Lead Engagement", "Conversion Rate"],
            governance_flags=[],
            suggested_owner=SuggestedOwner.MARKETING
        )
        rec.explanation = explain_decision(rec, rule_results)
        rec.explainability_summary = rec.explanation["summary"]
        recommendations.append(rec)

    if not check_data_completeness(analytics_metrics).passed:
        rec = DecisionRecommendation(
            title="Address Data Completeness",
            recommendation="Data completeness is below the 70% threshold. Prioritize data enrichment activities.",
            priority=RecommendationPriority.CRITICAL if persona == UserRole.FOUNDER else RecommendationPriority.HIGH,
            confidence=weighted_confidence,
            rationale="Low data completeness reduces the effectiveness of sales and marketing efforts.",
            impacted_metrics=["Data Quality", "Lead Conversion Rate"],
            governance_flags=["data_gap"],
            suggested_owner=SuggestedOwner.OPS
        )
        rec.explanation = explain_decision(rec, rule_results)
        rec.explainability_summary = rec.explanation["summary"]
        recommendations.append(rec)

    return recommendations

def filter_recommendations_by_persona(
    recommendations: List[DecisionRecommendation], 
    persona: UserRole
) -> List[DecisionRecommendation]:
    if persona == UserRole.FOUNDER:
        return [r for r in recommendations if r.priority in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]]
    elif persona == UserRole.SALES_MANAGER:
        return [r for r in recommendations if r.suggested_owner in [SuggestedOwner.SALES, SuggestedOwner.MARKETING]]
    elif persona == UserRole.OPS_CRM:
        return [r for r in recommendations if r.suggested_owner == SuggestedOwner.OPS]
    return recommendations
