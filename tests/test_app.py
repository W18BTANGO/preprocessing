import json
import pytest
import os
import sys
import requests
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.preprocessing import process_data
from typing import List, Dict, Any

client = TestClient(app)

# Helper functions
def load_test_input(filepath):
    with open(filepath, "r") as file:
        return json.load(file)

# Endpoint Tests

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "microservice": "preprocessing", "updated": "02/04/2025"}

def test_filter_data():
    """Test filtering data with valid inputs."""
    test_input = {
        "json_data": {
            "events": [
                {
                    "time_object": {"timestamp": "2024-06-28T00:00:00"},
                    "event_type": "sales report",
                    "attribute": {"price": 945000, "suburb": "NELSON BAY"}
                }
            ]
        },
        "event_type": ["sales report"],
        "filters": [{"attribute": "suburb", "values": ["NELSON BAY"]}],
        "include_attributes": ["price", "suburb"]
    }
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["filtered_data"]) == 1

def test_filter_data_with_timestamp_range():
    """Test filtering data with timestamp range."""
    test_input = {
        "json_data": {
            "events": [
                {"time_object": {"timestamp": "2023-06-28T00:00:00"}, "event_type": "sales report", "attribute": {"price": 945000, "suburb": "NELSON BAY"}},
                {"time_object": {"timestamp": "2024-07-28T00:00:00"}, "event_type": "sales report", "attribute": {"price": 1200000, "suburb": "NELSON BAY"}}
            ]
        },
        "event_type": ["sales report"],
        "filters": [{"attribute": "suburb", "values": ["NELSON BAY"]}],
        "include_attributes": ["price", "suburb"],
        "start_timestamp": "2024-01-01T00:00:00",
        "end_timestamp": "2025-01-01T00:00:00"
    }
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 200
    assert len(response.json()["filtered_data"]) == 1
    assert response.json()["filtered_data"][0]["attribute"]["price"] == 1200000

def test_invalid_json():
    """Test handling of invalid JSON input."""
    response = client.post("/filter-data", json={"json_data": {}})
    assert response.status_code == 400
    assert response.json()["detail"] == "No JSON data provided"

def test_missing_events_key():
    """Test handling of missing events key."""
    response = client.post("/filter-data", json={"json_data": {"time_object": {"timestamp": "2024-01-01T00:00:00"}}})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON format: Missing 'events' key"

def test_invalid_timestamp():
    """Test handling of invalid timestamp format."""
    test_input = {
        "json_data": {"events": [{"time_object": {"timestamp": "invalid"}}]},
        "start_timestamp": "invalid-timestamp"
    }
    response = client.post("/filter-data", json=test_input)
    assert response.status_code == 500
    assert "Invalid start_timestamp format" in response.json()["detail"]


class TestProcessData:
    """Unit tests for the process_data function."""
    
    def setup_method(self):
        """Setup test data before each test."""
        self.test_data = {
            "events": [
                {
                    "time_object": {
                        "timestamp": "2023-06-28T00:00:00",
                        "duration": 0,
                        "duration_unit": "day",
                        "timezone": "AEDT"
                    },
                    "event_type": "sales report",
                    "attribute": {
                        "price": 945000,
                        "suburb": "NELSON BAY",
                        "property_type": "RESIDENCE",
                        "postcode": "2315"
                    }
                },
                {
                    "time_object": {
                        "timestamp": "2024-07-28T00:00:00",
                        "duration": 0,
                        "duration_unit": "day",
                        "timezone": "AEDT"
                    },
                    "event_type": "sales report",
                    "attribute": {
                        "price": 1200000,
                        "suburb": "NELSON BAY",
                        "property_type": "APARTMENT",
                        "postcode": "2315"
                    }
                },
                {
                    "time_object": {
                        "timestamp": "2024-08-15T00:00:00",
                        "duration": 0,
                        "duration_unit": "day",
                        "timezone": "AEDT"
                    },
                    "event_type": "market update",
                    "attribute": {
                        "price": 850000,
                        "suburb": "SALAMANDER BAY",
                        "property_type": "RESIDENCE",
                        "postcode": "2317"
                    }
                }
            ]
        }
        
    def test_filter_by_event_type(self):
        """Test filtering by event type."""
        result = process_data(
            self.test_data,
            event_types=["sales report"],
            include_attributes=["price", "suburb", "property_type"]
        )
        
        assert len(result) == 2
        for event in result:
            assert event["event_type"] == "sales report"
            assert "price" in event["attribute"]
            assert "suburb" in event["attribute"]
            assert "property_type" in event["attribute"]
    
    def test_filter_by_attributes(self):
        """Test filtering by attribute values."""
        # Filter class to mimic the FilterCriteria from FastAPI endpoint
        class FilterCriteria:
            def __init__(self, attribute, values):
                self.attribute = attribute
                self.values = values
        
        filters = [FilterCriteria("suburb", ["NELSON BAY"])]
        
        result = process_data(
            self.test_data,
            event_types=["sales report", "market update"],
            filters=filters,
            include_attributes=["price", "suburb"]
        )
        
        assert len(result) == 2
        for event in result:
            assert event["attribute"]["suburb"] == "NELSON BAY"
    
    def test_filter_by_timestamp_range(self):
        """Test filtering by timestamp range."""
        result = process_data(
            self.test_data,
            event_types=["sales report", "market update"],
            start_timestamp="2024-01-01T00:00:00",
            end_timestamp="2024-12-31T23:59:59",
            include_attributes=["price", "suburb"]
        )
        
        assert len(result) == 2
        # Check that events from 2023 are excluded
        for event in result:
            event_time = event["time_object"]["timestamp"]
            assert event_time.startswith("2024")
    
    def test_invalid_timestamp_format(self):
        """Test handling of invalid timestamp formats."""
        with pytest.raises(ValueError, match="Invalid start_timestamp format"):
            process_data(
                self.test_data,
                event_types=["sales report"],
                start_timestamp="invalid-timestamp"
            )
        
        with pytest.raises(ValueError, match="Invalid end_timestamp format"):
            process_data(
                self.test_data,
                event_types=["sales report"],
                end_timestamp="invalid-timestamp"
            )
    
    def test_empty_data(self):
        """Test processing empty data."""
        empty_data = {"events": []}
        result = process_data(
            empty_data,
            event_types=["sales report"],
            include_attributes=["price", "suburb"]
        )
        assert result == []
