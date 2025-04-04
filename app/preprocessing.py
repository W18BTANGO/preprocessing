from typing import List, Dict, Any, Optional
from datetime import datetime


def process_data(
    data: Dict[str, Any],
    event_types: List[str],  # Updated to support multiple event types
    filters: Optional[List[Any]] = None,  # Optional filters
    include_attributes: Optional[List[str]] = None,  # Optional attributes
    start_timestamp: Optional[str] = None,
    end_timestamp: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filters a dataset based on event type, attribute filters, and a time range.

    Parameters:
    - `data` (dict): The dataset to be filtered.
    - `event_type` (str): The type of event to filter by.
    - `filters` (List[Any]): A list of filter objects with `attribute` and `values`.
    - `include_attributes` (List[str]): A list of attributes to include in the response.
    - `start_timestamp` (str, optional): The start timestamp for filtering events.
    - `end_timestamp` (str, optional): The end timestamp for filtering events.

    Returns:
    - `List[Dict[str, Any]]`: A list of filtered events with specified attributes.
    """
    events = data.get("events", [])

    # Convert timestamps to datetime objects for comparison
    try:
        start_dt = datetime.fromisoformat(start_timestamp) if start_timestamp else None
    except ValueError:
        raise ValueError(f"Invalid start_timestamp format: {start_timestamp}")

    try:
        end_dt = datetime.fromisoformat(end_timestamp) if end_timestamp else None
    except ValueError:
        raise ValueError(f"Invalid end_timestamp format: {end_timestamp}")

    def event_matches(event: Dict[str, Any]) -> bool:
        """Checks if an event meets the filter criteria."""
        if event.get("event_type") not in event_types:
            return False

        event_time_str = event.get("time_object", {}).get("timestamp")
        if event_time_str:
            try:
                event_time = datetime.fromisoformat(
                    event_time_str[:26]
                )  # Trim extra precision if needed
                if start_dt and event_time < start_dt:
                    return False
                if end_dt and event_time > end_dt:
                    return False
            except ValueError:
                return False  # Skip events with invalid timestamps

        # Check attribute filters
        if filters:
            attributes = event.get("attribute", {})
            for filter_ in filters:
                if hasattr(filter_, "attribute") and hasattr(filter_, "values"):
                    attr_name = filter_.attribute
                    allowed_values = set(filter_.values)
                    if attr_name not in attributes or attributes[attr_name] not in allowed_values:
                        return False

        return True

    # Apply filtering
    filtered_events = [
        {
            "time_object": event["time_object"],
            "event_type": event["event_type"],
            "attribute": {
                key: value
                for key, value in event.get("attribute", {}).items()
                if not include_attributes or key in include_attributes
            },
        }
        for event in events
        if event_matches(event)
    ]

    return filtered_events
