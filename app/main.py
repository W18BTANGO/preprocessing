from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.preprocessing import process_data
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Preprocessing API", description="API for extracting specific values from datasets", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class FilterCriteria(BaseModel):
    attribute: str
    values: List[Any]


class PreprocessRequest(BaseModel):
    json_data: Dict[str, Any]
    event_type: Optional[List[str]] = []  # Default: No filtering by event type
    filters: Optional[List[FilterCriteria]] = []  # Default: No filtering
    include_attributes: Optional[List[str]] = None  # Default: Include all attributes
    start_timestamp: Optional[str] = None  # Default: No time range filtering
    end_timestamp: Optional[str] = None  # Default: No time range filtering


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "microservice": "preprocessing"}


@app.post("/filter-data")
async def filter_data(request: PreprocessRequest):
    """
    Filters a dataset based on event type, attributes, and a time range.
    """
    if not request.json_data:
        raise HTTPException(status_code=400, detail="No JSON data provided")

    if "events" not in request.json_data:
        raise HTTPException(status_code=400, detail="Invalid JSON format: Missing 'events' key")

    try:
        filtered_data = process_data(
            data=request.json_data,
            event_types=request.event_type or [],
            filters=request.filters or [],
            include_attributes=request.include_attributes or [],
            start_timestamp=request.start_timestamp,
            end_timestamp=request.end_timestamp,
        )
        return {"status": "success", "filtered_data": filtered_data}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
