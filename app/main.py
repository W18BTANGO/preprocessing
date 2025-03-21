from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.preprocessing import process_data

app = FastAPI(
    title="Preprocessing API",
    description="API for extracting specific values from datasets",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

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
    json_data: Dict[str, Any] = None  # type: ignore
    event_type: Optional[List[str]] = []
    filters: Optional[List[FilterCriteria]] = []
    include_attributes: Optional[List[str]] = None
    start_timestamp: Optional[str] = None
    end_timestamp: Optional[str] = None


@app.post("/filter-data")
async def filter_data(request: PreprocessRequest):
    if request.json_data is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format: Missing 'json_data' key"
        )

    if "events" not in request.json_data:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format: Missing 'events' key"
        )

    try:
        filtered_data = process_data(
            request.json_data,
            request.event_type or [],
            request.filters or None,
            request.include_attributes or None,
            request.start_timestamp,
            request.end_timestamp,
        )
        print("Filtered Data:", filtered_data)  # Debug output
        return {"status": "success", "filtered_data": filtered_data}
    except Exception as e:
        print("Error:", str(e))  # Print error details
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    return {"status": "healthy", "microservice": "preprocessing"}
