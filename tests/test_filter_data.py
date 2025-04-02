import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_filter_data_valid_input():
    """Test /filter-data with valid input."""
    test_input = {"json_data": {"events": [{"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1"}]}}
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_filter_data_missing_json_data():
    """Test /filter-data with missing json_data."""
    response = client.post("/filter-data", json={"json_data": {}})
    assert response.status_code == 400
    assert response.json()["detail"] == "No JSON data provided"

def test_filter_data_missing_events_key():
    """Test /filter-data with missing events key."""
    response = client.post("/filter-data", json={"json_data": {"time_object": {"timestamp": "2024-01-01T00:00:00"}}})
    assert response.status_code == 400

def test_filter_data_invalid_timestamp_format():
    """Test /filter-data with invalid timestamp format."""
    test_input = {
        "json_data": {"events": [{"time_object": {"timestamp": "invalid"}}]},
        "start_timestamp": "invalid-timestamp"
    }
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 500
    assert "Invalid start_timestamp format" in response.json()["detail"]

def test_filter_data_no_matching_filters():
    """Test /filter-data with filters that do not match any events."""
    test_input = {
        "json_data": {"events": [{"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1", "attribute": {"key": "value"}}]},
        "filters": [{"attribute": "key", "values": ["no-match"]}]
    }
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 200
    assert response.json()["filtered_data"] == []
