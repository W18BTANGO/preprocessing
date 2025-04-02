import pytest
from app.preprocessing import process_data
from unittest.mock import MagicMock

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
