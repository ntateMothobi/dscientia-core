from fastapi.testclient import TestClient

def test_get_dashboard_analytics_empty_db(client: TestClient):
    """
    Test that the dashboard analytics endpoint returns a valid structure
    even when the database is empty.
    """
    # Act
    response = client.get("/api/v1/analytics/dashboard")

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Check top-level keys
    assert "leads" in data
    assert "followups" in data

    # Check Leads structure
    leads = data["leads"]
    assert "total_leads" in leads
    assert isinstance(leads["total_leads"], int)
    assert "by_status" in leads
    assert isinstance(leads["by_status"], dict)

    # Check Followups structure
    followups = data["followups"]
    assert "total_followups" in followups
    assert isinstance(followups["total_followups"], int)
    assert "by_status" in followups
    assert isinstance(followups["by_status"], dict)

def test_get_dashboard_analytics_with_data(client: TestClient):
    """
    Test that the dashboard analytics endpoint correctly aggregates data.
    """
    # Arrange: Create a lead and a follow-up
    lead_payload = {"name": "Test Lead", "phone": "123", "status": "new"}
    lead_res = client.post("/api/v1/leads/", json=lead_payload)
    lead_id = lead_res.json()["id"]

    followup_payload = {"lead_id": lead_id, "note": "Test Note", "status": "pending"}
    client.post("/api/v1/followups/", json=followup_payload)

    # Act
    response = client.get("/api/v1/analytics/dashboard")

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Verify counts reflect the created data
    assert data["leads"]["total_leads"] >= 1
    assert data["leads"]["by_status"].get("new", 0) >= 1
    
    assert data["followups"]["total_followups"] >= 1
    assert data["followups"]["by_status"].get("pending", 0) >= 1
