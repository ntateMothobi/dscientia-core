import pytest
from app.services.decision_engine import generate_recommendations
from app.core.security import UserRole
from app.schemas.decision import RecommendationPriority

def test_founder_has_higher_priority_and_score():
    # Setup identical analytics input
    analytics = {
        "duplicate_rate": 2,
        "data_completeness": 60 # Below 70 threshold -> triggers recommendation
    }
    confidence_score = 50.0

    # Generate for Founder
    founder_recs = generate_recommendations(analytics, confidence_score, UserRole.FOUNDER)
    founder_rec = next(r for r in founder_recs if r.title == "Address Data Completeness")

    # Generate for Ops
    ops_recs = generate_recommendations(analytics, confidence_score, UserRole.OPS_CRM)
    ops_rec = next(r for r in ops_recs if r.title == "Address Data Completeness")

    # Assertions
    # Founder score should be higher due to 1.3x multiplier
    assert founder_rec.confidence > ops_rec.confidence
    
    # Founder priority should be CRITICAL (logic in engine upgrades it)
    assert founder_rec.priority == RecommendationPriority.CRITICAL
    
    # Ops priority should be HIGH (default)
    assert ops_rec.priority == RecommendationPriority.HIGH

def test_sales_manager_weighting():
    analytics = {
        "duplicate_rate": 0,
        "data_completeness": 80
    }
    confidence_score = 70.0
    
    # Generate for Sales Manager
    sales_recs = generate_recommendations(analytics, confidence_score, UserRole.SALES_MANAGER)
    sales_rec = next(r for r in sales_recs if r.title == "Proceed with Automated Outreach")
    
    # Base confidence 70 * 1.1 = 77
    assert sales_rec.confidence == 77.0
