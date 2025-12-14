from fastapi.testclient import TestClient

def test_followup_workflow(client: TestClient):
    """
    Tests the full lifecycle of a follow-up:
    1. Create a Lead (prerequisite)
    2. Create a Follow-up for that Lead
    3. Retrieve Follow-ups for that Lead
    """
    # --- Step 1: Create a Lead ---
    lead_payload = {
        "name": "Jane Doe",
        "phone": "+628111222333",
        "source": "instagram",
        "status": "new"
    }
    lead_response = client.post("/api/v1/leads/", json=lead_payload)
    assert lead_response.status_code == 201
    lead_id = lead_response.json()["id"]

    # --- Step 2: Create a Follow-up ---
    followup_payload = {
        "lead_id": lead_id,
        "note": "Sent property brochure via WA",
        "status": "contacted",
        "next_contact_date": "2024-12-31"
    }
    
    response = client.post("/api/v1/followups/", json=followup_payload)
    
    # Assert creation success
    assert response.status_code == 201
    data = response.json()
    assert data["lead_id"] == lead_id
    assert data["note"] == followup_payload["note"]
    assert data["status"] == "contacted"
    assert "id" in data

    # --- Step 3: Retrieve Follow-ups ---
    get_response = client.get(f"/api/v1/followups/lead/{lead_id}")
    
    # Assert retrieval success
    assert get_response.status_code == 200
    followups = get_response.json()
    
    # Assert list content
    assert isinstance(followups, list)
    assert len(followups) == 1
    assert followups[0]["id"] == data["id"]
    assert followups[0]["note"] == followup_payload["note"]


def test_create_followup_unknown_lead(client: TestClient):
    """
    Tests that creating a follow-up for a non-existent lead fails.
    """
    followup_payload = {
        "lead_id": 99999,  # ID that definitely doesn't exist
        "note": "This should fail",
        "status": "pending"
    }
    
    response = client.post("/api/v1/followups/", json=followup_payload)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
