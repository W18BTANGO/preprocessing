import json
from fastapi.testclient import TestClient
from app.main import app  # Ensure this is the correct import for your FastAPI app

client = TestClient(app)

def load_test_input(filepath):
    with open(filepath, "r") as file:
        return json.load(file)

def test_filter_data():
    test_input = load_test_input("tests/sample-input/input1.json")
    response = client.post("/filter-data", json=test_input)
    print(response.json())
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "success"
    assert "filtered_data" in response_json
    assert isinstance(response_json["filtered_data"], list)
    
    # Check expected filtered events
    expected_filtered_events = [
        {
            "time_object": {
                "timestamp": "2019-07-21T13:04:40.340101",
                "duration": 1,
                "duration_unit": "second",
                "timezone": "GMT+11"
            },
            "event_type": "house sale",
            "attribute": {
                "price": 1600000,
                "suburb": "Balmain"
            }
        },
        {
            "time_object": {
                "timestamp": "2019-03-21T18:11:40.340101",
                "duration": 1,
                "duration_unit": "second",
                "timezone": "GMT+11"
            },
            "event_type": "house sale",
            "attribute": {
                "price": 2800000,
                "suburb": "Glebe"
            }
        }
    ]
    assert response_json["filtered_data"] == expected_filtered_events

def test_invalid_json():
    response = client.post("/filter-data", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON format: Missing 'json_data' key"

def test_missing_events_key():
    response = client.post("/filter-data", json={"json_data": {}})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON format: Missing 'events' key"

def test_invalid_timestamp():
    test_input = load_test_input("tests/sample-input/input1.json")
    test_input["start_timestamp"] = "invalid-timestamp"
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 500
    assert "Invalid start_timestamp format" in response.json()["detail"]
