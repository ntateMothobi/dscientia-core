from typing import List, Dict, Any, Tuple
from app.schemas.decision import DecisionRecommendation, RecommendationPriority, SuggestedOwner
from app.schemas.rule_result import RuleResult
from app.core.security import UserRole

def check_confidence_threshold(confidence_score: float) -> RuleResult:
    passed = confidence_score >= 60
    return RuleResult(
        rule_id="CONFIDENCE_CHECK",
        passed=passed,
        weight=0.5,
        explanation=f"System confidence score is {confidence_score}%, which is {'above' if passed else 'below'} the 60% minimum threshold."
    )

def check_policy_violation(metrics: Dict[str, Any]) -> RuleResult:
    # Dummy logic for policy violation
    violation = metrics.get("duplicate_rate", 0) > 5
    return RuleResult(
        rule_id="POLICY_VIOLATION_CHECK",
        passed=not violation,
        weight=0.3,
        explanation=f"Data duplication rate is {metrics.get('duplicate_rate', 0)}%, which {'does not violate' if not violation else 'violates'} the 5% policy."
    )

def check_data_completeness(metrics: Dict[str, Any]) -> RuleResult:
    passed = metrics.get("data_completeness", 0) >= 70
    return RuleResult(
        rule_id="COMPLETENESS_CHECK",
        passed=passed,
        weight=0.2,
        explanation=f"Data completeness is {metrics.get('data_completeness', 0)}%, which is {'above' if passed else 'below'} the 70% minimum threshold."
    )

def explain_decision(decision: DecisionRecommendation, rule_results: List[RuleResult]) -> Dict[str, Any]:
    passed_rules = [r for r in rule_results if r.passed]
    failed_rules = [r for r in rule_results if not r.passed]

    if not failed_rules:
        summary = f"Recommendation '{decision.title}' is fully supported by all system checks."
    else:
        summary = f"Recommendation '{decision.title}' is generated despite {len(failed_rules)} warning(s)."

    contributing_factors = [r.explanation for r in passed_rules]
    triggered_rule_ids = [r.rule_id for r in rule_results]

    return {
        "summary": summary,
        "contributing_factors": contributing_factors,
        "triggered_rule_ids": triggered_rule_ids
    }

def generate_recommendations(analytics_metrics: Dict[str, Any], confidence_score: float) -> List[DecisionRecommendation]:
    recommendations = []
    
    # Run all rules
    rule_results = [
        check_confidence_threshold(confidence_score),
        check_policy_violation(analytics_metrics),
        check_data_completeness(analytics_metrics)
    ]

    # Example of a decision based on rule results
    if all(r.passed for r in rule_results):
        rec = DecisionRecommendation(
            title="Proceed with Automated Outreach",
            recommendation="All system checks passed. It is safe to proceed with automated marketing campaigns.",
            priority=RecommendationPriority.MEDIUM,
            confidence=int(confidence_score),
            rationale="High confidence and data quality allow for safe automation.",
            impacted_metrics=["Lead Engagement", "Conversion Rate"],
            suggested_owner=SuggestedOwner.MARKETING
        )
        explanation = explain_decision(rec, rule_results)
        rec.explainability_summary = explanation["summary"]
        # In a real system, you might attach more from the explanation object
        recommendations.append(rec)

    # Add a recommendation if a specific rule fails
    if not check_data_completeness(analytics_metrics).passed:
        rec = DecisionRecommendation(
            title="Address Data Completeness",
            recommendation="Data completeness is below the 70% threshold. Prioritize data enrichment activities.",
            priority=RecommendationPriority.HIGH,
            confidence=int(confidence_score),
            rationale="Low data completeness reduces the effectiveness of sales and marketing efforts.",
            impacted_metrics=["Data Quality", "Lead Conversion Rate"],
            suggested_owner=SuggestedOwner.OPS
        )
        explanation = explain_decision(rec, rule_results)
        rec.explainability_summary = explanation["summary"]
        recommendations.append(rec)

    return recommendations

def filter_recommendations_by_persona(recommendations: List[DecisionRecommendation], persona: UserRole) -> List[DecisionRecommendation]:
    # ... (existing filtering logic remains the same)
    if persona == UserRole.FOUNDER:
        return [rec for rec in recommendations if rec.priority in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]]
    elif persona == UserRole.SALES_MANAGER:
        return [rec for rec in recommendations if rec.suggested_owner in [SuggestedOwner.SALES, SuggestedOwner.MARKETING]]
    elif persona == UserRole.OPS_CRM:
        return [rec for rec in recommendations if rec.suggested_owner == SuggestedOwner.OPS]
    return recommendations
