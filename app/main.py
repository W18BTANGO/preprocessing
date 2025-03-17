from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.preprocessing import process_data

app = FastAPI(title="Preprocessing API", description="API for extracting specific values from datasets", version="1.0.0")

class FilterCriteria(BaseModel):
    attribute: str
    values: List[Any]

class PreprocessRequest(BaseModel):
    json_data: Dict[str, Any]
    # TO DO: CHANGE TO LIST OF EVENT TYPES
    # TO DO: MAKE DEFAULT NO FILTERING
    event_type: str
    # TO DO: MAKE DEFAULT NO FILTERING
    filters: List[FilterCriteria]
    # TO DO: MAKE DEFAULT ALL ATTRIBUTES
    include_attributes: List[str]
    # TO DO: MAKE DEFAULT ALL TIME RANGES
    start_timestamp: Optional[str] = None  # ISO 8601 format
    end_timestamp: Optional[str] = None  # ISO 8601 format


@app.post("/filter-data")
async def filter_data(request: PreprocessRequest):
    """
    Filters a dataset based on event type, attributes, and a time range.

    Parameters:
    - `data` (dict): A JSON object which is the dataset to be filtered.
    - `event_type` (str): The type of event to filter by.
    - `filters` (List[FilterCriteria]): A list of attribute-value filters to apply.
    - `include_attributes` (List[str]): A list of attributes to include in the response.
    - `start_timestamp` (str, optional): The start timestamp for filtering events.
    - `end_timestamp` (str, optional): The end timestamp for filtering events.

    Returns:
    - `dict`: A JSON object containing the filtered dataset.
    """
    if not request.json_data:
        raise HTTPException(status_code=400, detail="No JSON data provided")
    
    if "events" not in request.json_data:
        raise HTTPException(status_code=400, detail="Invalid JSON format: Missing 'events' key")
    
    try:
        filtered_data = process_data(
            request.json_data,
            request.event_type,
            request.filters,
            request.include_attributes,
            request.start_timestamp,
            request.end_timestamp
        )
        return {"status": "success", "filtered_data": filtered_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
