from fastapi.testclient import TestClient

def test_create_lead_success(client: TestClient):
    """
    Tests successful creation of a new lead.
    """
    # 1. Arrange: Define the lead data
    lead_data = {
        "name": "Budi Santoso",
        "phone": "+6281234567890",
        "email": "budi.santoso@example.com",
        "source": "website",
        "notes": "Looking for a 3BR apartment"
    }

    # 2. Act: Send a POST request to the endpoint
    response = client.post("/api/v1/leads/", json=lead_data)

    # 3. Assert: Check the response
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    data = response.json()
    
    # Assert that the response contains the created data
    assert "id" in data
    assert data["name"] == lead_data["name"]
    assert data["phone"] == lead_data["phone"]
    assert data["email"] == lead_data["email"]
    assert data["source"] == lead_data["source"]
    assert data["notes"] == lead_data["notes"]
    assert data["status"] == "new"  # Check default status
    assert "created_at" in data
