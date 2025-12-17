from typing import List, Dict, Any

def generate_all_persona_insights(analytics_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Generates a dictionary of formatted insight strings for all personas.
    """
    if not analytics_data:
        return {
            "Founder": "No lead data available to generate insights.",
            "Sales Manager": "No lead data available to generate insights.",
            "Operations Manager": "No lead data available to generate insights."
        }

    return {
        "Founder": _generate_founder_insights(analytics_data),
        "Sales Manager": _generate_sales_manager_insights(analytics_data),
        "Operations Manager": _generate_operations_manager_insights(analytics_data),
    }

def _generate_founder_insights(data: List[Dict[str, Any]]) -> str:
    """Generates insights for the Founder/Executive persona."""
    total_leads = len(data)
    high_risk_leads = sum(1 for d in data if d['risk_level'] == 'High')
    sla_breaches = sum(1 for d in data if d['sla_breached'])
    
    breach_rate = (sla_breaches / total_leads * 100) if total_leads > 0 else 0
    high_risk_rate = (high_risk_leads / total_leads * 100) if total_leads > 0 else 0

    # Key Insight
    insight = f"We have {total_leads} active leads, but {high_risk_rate:.0f}% are high-risk."

    # Risk / Opportunity
    if breach_rate > 20:
        risk = f"High SLA breach rate ({breach_rate:.0f}%) suggests potential brand damage and lost revenue."
    else:
        risk = "Opportunity to double-down on high-performing channels, but data is limited."

    # Recommended Action
    if high_risk_rate > 30:
        recommendation = "Review lead management strategy to address high-risk leads and protect the pipeline."
    else:
        recommendation = "Invest in analytics to better understand conversion drivers and scale what works."

    return (
        "Founder / Executive\n"
        f"• Key Insight: {insight}\n"
        f"• Risk / Opportunity: {risk}\n"
        f"• Recommended Action: {recommendation}"
    )

def _generate_sales_manager_insights(data: List[Dict[str, Any]]) -> str:
    """Generates insights for the Sales Manager persona."""
    high_risk_leads = sorted([d for d in data if d['risk_level'] == 'High'], key=lambda x: x['risk_score'], reverse=True)
    stale_leads = sorted([d for d in data if d['age_days'] > 7 and d['followup_count'] <= 1], key=lambda x: x['age_days'], reverse=True)

    # Key Insight
    if high_risk_leads:
        insight = f"Focus on these {len(high_risk_leads)} high-risk leads immediately: {', '.join([l['name'] for l in high_risk_leads[:3]])}."
    elif stale_leads:
        insight = f"Several leads are going cold. Re-engage {len(stale_leads)} leads like {stale_leads[0]['name']} who haven't been followed up with recently."
    else:
        insight = "Pipeline is healthy with no immediate high-risk leads. Great work!"

    # What to do TODAY
    if stale_leads:
        action = f"Initiate a follow-up sequence for {len(stale_leads)} aging leads, starting with the oldest."
    else:
        action = "Review the current lead distribution and ensure the team is prepared for new inbound leads."

    # This WEEK
    if high_risk_leads:
        recommendation = f"Conduct a pipeline review this week to address all {len(high_risk_leads)} high-risk leads and assign clear next steps."
    else:
        recommendation = "Identify top-performing sales tactics on current leads and share them with the team."

    return (
        "Sales Manager\n"
        f"• Key Insight: {insight}\n"
        f"• What to do TODAY: {action}\n"
        f"• This WEEK: {recommendation}"
    )

def _generate_operations_manager_insights(data: List[Dict[str, Any]]) -> str:
    """Generates insights for the Operations/CRM Manager persona."""
    sla_breaches = [d for d in data if d['sla_breached']]
    total_leads = len(data)
    breach_rate = (len(sla_breaches) / total_leads * 100) if total_leads > 0 else 0

    # Key Insight
    if sla_breaches:
        breached_statuses = {d['status'] for d in sla_breaches}
        insight = f"{len(sla_breaches)} leads ({breach_rate:.0f}%) have breached SLA, primarily in the '{', '.join(breached_statuses)}' stage."
    else:
        insight = "Excellent SLA compliance across all lead stages. The current process is working effectively."

    # Process Gap
    if breach_rate > 15:
        gap = "There's a significant delay in moving leads through the pipeline, indicating a bottleneck or inefficient workflow."
    else:
        gap = "No major process gaps detected. Data suggests smooth transitions between lead stages."

    # Improvement Suggestion
    if breach_rate > 15:
        suggestion = "Investigate the bottleneck in the breached stages. Consider automating follow-up reminders or re-evaluating the SLA thresholds for those stages."
    else:
        suggestion = "Consider documenting the current successful workflow as a standard operating procedure to maintain high performance."

    return (
        "Operations / CRM Manager\n"
        f"• Key Insight: {insight}\n"
        f"• Process Gap: {gap}\n"
        f"• Improvement Suggestion: {suggestion}"
    )
