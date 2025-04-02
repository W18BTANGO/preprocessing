from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

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
    assert response.json()["filtered_data"] == [{"time_object": {"timestamp": "2024-01-01T00:00:00"}, "event_type": "type1", "attribute": {}}]
