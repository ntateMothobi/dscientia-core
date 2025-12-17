from typing import List, Dict, Any

def generate_alerts(analytics_data: List[Dict[str, Any]], persona: str) -> List[Dict[str, Any]]:
    """
    Generates a list of alerts based on analytics data and persona.
    """
    alerts = []
    
    # --- Alert Calculation ---
    sla_breached_leads = [d for d in analytics_data if d['sla_breached']]
    high_risk_leads = [d for d in analytics_data if d['risk_level'] == 'High' and not d['sla_breached']] # Avoid double-counting
    
    if not analytics_data:
        return alerts

    oldest_unattended = max(analytics_data, key=lambda x: x['age_days'])

    # --- Persona-Aware Messaging ---
    persona_map = {
        "founder": {
            "sla_title": "SLA Breaches Impacting Reputation",
            "sla_message": f"{len(sla_breached_leads)} leads have breached SLA, posing a risk to client trust and brand reputation.",
            "risk_title": "High-Risk Leads Signal Pipeline Weakness",
            "risk_message": f"{len(high_risk_leads)} leads are high-risk, indicating potential revenue loss if not addressed.",
            "summary_title": "Daily Strategic Summary",
            "summary_message": f"Attention: {len(high_risk_leads)} high-risk leads and {len(sla_breached_leads)} SLA breaches require strategic review. Oldest unattended lead is {oldest_unattended['age_days']} days old."
        },
        "sales": {
            "sla_title": "Urgent: Follow Up on Breached Leads",
            "sla_message": f"{len(sla_breached_leads)} leads need immediate follow-up today. Start with: {', '.join([l['name'] for l in sla_breached_leads[:2]])}.",
            "risk_title": "High-Risk Leads to Prioritize",
            "risk_message": f"Focus on these {len(high_risk_leads)} high-risk leads to keep the pipeline moving.",
            "summary_title": "Your Daily Action Summary",
            "summary_message": f"Today's focus: {len(high_risk_leads)} high-risk leads and {len(sla_breached_leads)} urgent SLA breaches. Your oldest unattended lead is {oldest_unattended['name']} ({oldest_unattended['age_days']} days)."
        },
        "ops": {
            "sla_title": "Process Alert: SLA Compliance Failure",
            "sla_message": f"Process failure: {len(sla_breached_leads)} leads have breached SLA, indicating a bottleneck in the '{', '.join(set([l['status'] for l in sla_breached_leads]))}' stage(s).",
            "risk_title": "High-Risk Leads Analysis",
            "risk_message": f"{len(high_risk_leads)} leads are high-risk. Investigate if this is due to process delays or data issues.",
            "summary_title": "Daily Operational Health Check",
            "summary_message": f"System status: {len(high_risk_leads)} high-risk leads, {len(sla_breached_leads)} SLA breaches. The oldest unattended lead is {oldest_unattended['age_days']} days old, indicating a process stall."
        }
    }

    messages = persona_map.get(persona, persona_map["sales"]) # Default to sales

    # --- Alert Generation ---
    if sla_breached_leads:
        alerts.append({
            "type": "sla_breach",
            "severity": "high",
            "icon": "⏰",
            "title": messages["sla_title"],
            "message": messages["sla_message"],
            "action_hint": "Filter for 'SLA Breached' in the Risk & SLA view."
        })

    if high_risk_leads:
        alerts.append({
            "type": "high_risk",
            "severity": "medium",
            "icon": "⚠️",
            "title": messages["risk_title"],
            "message": messages["risk_message"],
            "action_hint": "Filter for 'High' risk level."
        })
        
    if analytics_data:
        alerts.append({
            "type": "summary",
            "severity": "low",
            "icon": "🔥",
            "title": messages["summary_title"],
            "message": messages["summary_message"],
            "action_hint": "Use the dashboard filters to explore."
        })

    return alerts
