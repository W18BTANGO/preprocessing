from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.preprocessing import process_data

app = FastAPI(title="Preprocessing API", description="API for extracting specific values from datasets", version="1.0.0")

class FilterCriteria(BaseModel):
    attribute: str
    values: List[Any]

class PreprocessRequest(BaseModel):
    json_data: Dict[str, Any] = None
    event_type: Optional[List[str]] = []  # Default: No filtering by event type
    filters: Optional[List[FilterCriteria]] = []  # Default: No filtering
    include_attributes: Optional[List[str]] = None  # Default: Include all attributes
    start_timestamp: Optional[str] = None
    end_timestamp: Optional[str] = None


@app.post("/filter-data")
async def filter_data(request: PreprocessRequest):
    if request.json_data is None:
        raise HTTPException(status_code=400, detail="Invalid JSON format: Missing 'json_data' key")
    
    if "events" not in request.json_data:
        raise HTTPException(status_code=400, detail="Invalid JSON format: Missing 'events' key")

    print("Received json_data:", request.json_data)
    print("Event Types:", request.event_type)
    print("Filters:", request.filters)
    print("Include Attributes:", request.include_attributes)
    print("Start Timestamp:", request.start_timestamp)
    print("End Timestamp:", request.end_timestamp)

    try:
        filtered_data = process_data(
            request.json_data,
            request.event_type or [],  
            request.filters or None,  
            request.include_attributes or None,
            request.start_timestamp,
            request.end_timestamp
        )
        print("Filtered Data:", filtered_data)  # Debug output
        return {"status": "success", "filtered_data": filtered_data}
    except Exception as e:
        print("Error:", str(e))  # Print error details
        raise HTTPException(status_code=500, detail=str(e))
