from typing import List, Dict, Any, Optional
from datetime import datetime

def process_data(
    data: Dict[str, Any],
    event_type: str,
    filters: List[Dict[str, Any]],
    include_attributes: List[str],
    start_timestamp: Optional[str] = None,
    end_timestamp: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filters a dataset based on event type, attribute filters, and a time range.

    Parameters:
    - `data` (dict): The dataset to be filtered.
    - `event_type` (str): The type of event to filter by.
    - `filters` (List[Dict[str, Any]]): A list of attribute-value filters to apply.
    - `include_attributes` (List[str]): A list of attributes to include in the response.
    - `start_timestamp` (str, optional): The start timestamp for filtering events.
    - `end_timestamp` (str, optional): The end timestamp for filtering events.

    Returns:
    - `List[Dict[str, Any]]`: A list of filtered events with specified attributes.
    """
    events = data.get("events", [])
    
    # Convert timestamps to datetime objects for comparison
    start_dt = datetime.fromisoformat(start_timestamp) if start_timestamp else None
    end_dt = datetime.fromisoformat(end_timestamp) if end_timestamp else None

    def event_matches(event: Dict[str, Any]) -> bool:
        """Checks if an event meets the filter criteria."""
        if event.get("event_type") != event_type:
            return False
        
        event_time_str = event.get("time_object", {}).get("timestamp")
        if event_time_str:
            event_time = datetime.fromisoformat(event_time_str)
            if start_dt and event_time < start_dt:
                return False
            if end_dt and event_time > end_dt:
                return False
        
        # Check attribute filters
        attributes = event.get("attribute", {})
        for filter_ in filters:
            attr_name = filter_["attribute"]
            allowed_values = set(filter_["values"])
            if attr_name in attributes and attributes[attr_name] not in allowed_values:
                return False
        
        return True

    # Apply filtering
    filtered_events = [
        {
            "time_object": event["time_object"],
            "event_type": event["event_type"],
            "attribute": {key: value for key, value in event.get("attribute", {}).items() if key in include_attributes}
        }
        for event in events if event_matches(event)
    ]
    
    return filtered_events
