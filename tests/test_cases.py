import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.preprocessing import process_data

client = TestClient(app)

# Unit Tests for process_data
def test_process_data_valid_inputs():
    """Test process_data with valid inputs."""
    test_data = {
        "events": [
            {"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1", "attribute": {"key": "value"}}
        ]
    }
    result = process_data(test_data, event_types=["type1"], filters=[], include_attributes=[], start_timestamp=None, end_timestamp=None)
    assert len(result) == 1

def test_process_data_empty_data():
    """Test process_data with empty data."""
    result = process_data({"events": []}, event_types=["type1"])
    assert result == []

def test_process_data_invalid_timestamps():
    """Test process_data with invalid timestamps."""
    test_data = {
        "events": [
            {"time_object": {"timestamp": "invalid"}, "event_type": "type1", "attribute": {"key": "value"}}
        ]
    }
    with pytest.raises(ValueError, match="Invalid start_timestamp format"):
        process_data(
            data=test_data,
            event_types=["type1"],
            filters=[],
            include_attributes=[],
            start_timestamp="invalid",
            end_timestamp=None
        )

def test_process_data_no_matching_filters():
    """Test process_data with filters that do not match any events."""
    test_data = {
        "events": [
            {"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1", "attribute": {"key": "value"}}
        ]
    }
    result = process_data(
        data=test_data,
        event_types=["type1"],
        filters=[MagicMock(attribute="key", values=["no-match"])],
        include_attributes=[],
        start_timestamp=None,
        end_timestamp=None
    )
    assert result == []

def test_process_data_overlapping_timestamps():
    """Test process_data with overlapping timestamp ranges."""
    test_data = {
        "events": [
            {"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1", "attribute": {"key": "value"}}
        ]
    }
    result = process_data(test_data, event_types=["type1"], filters=[], include_attributes=[], start_timestamp="2023-12-31T23:59:59", end_timestamp="2024-01-01T23:59:59")
    assert len(result) == 1

def test_process_data_missing_attributes():
    """Test process_data with missing attributes in events."""
    test_data = {
        "events": [
            {"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1"}
        ]
    }
    result = process_data(
        data=test_data,
        event_types=["type1"],
        filters=[],
        include_attributes=["key"],
        start_timestamp=None,
        end_timestamp=None
    )
    assert len(result) == 1
    assert result[0]["attribute"] == {}

def test_process_data_large_dataset():
    """Test process_data with large datasets."""
    test_data = {"events": [{"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1"}] * 1000}
    result = process_data(test_data, event_types=["type1"])
    assert len(result) == 1000

# API Tests
def test_health_check_endpoint():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "microservice": "preprocessing"}

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

# Integration Tests
@patch("app.preprocessing.process_data")
def test_filter_data_integration(mock_process_data):
    """Test integration of process_data with /filter-data."""
    mock_process_data.return_value = [{"event_type": "type1", "time_object": {}, "attribute": {}}]
    test_input = {
        "json_data": {"events": [{"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1"}]},
        "event_type": ["type1"],
        "filters": [],
        "include_attributes": [],
        "start_timestamp": None,
        "end_timestamp": None
    }
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 200
    print(response.json())
    assert response.json()["filtered_data"] == [{'time_object': {'timestamp': '2024-01-01T00:00:00'}, 'event_type': 'type1', 'attribute': {}}]

