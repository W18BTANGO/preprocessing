from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
import os


app = FastAPI(title="Preprocessing API", description="API for extracting specific values from datasets", version="1.0.0")

class PreprocessRequest(BaseModel):
    file_path: str  # Path to the JSON file to preprocess

def preprocess_data(file_path: str):
    # Load the JSON data
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Convert the JSON data into a DataFrame for easier processing
    df = pd.json_normalize(data)  # Flatten the JSON structure

    # Perform any preprocessing here, like handling missing values, normalizing data, etc.
    
    # Example: Handle missing values by filling NaN with a default value
    df.fillna(0, inplace=True)
    
    # Example: Standardize numeric columns (you can extend this to any column)
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].apply(lambda x: (x - x.mean()) / x.std())

    return df

@app.get("/standardize")
async def standardize_data(file_path: str):
    """Endpoint to standardize data and return the transformed result."""
    if not file_path:
        raise HTTPException(status_code=404, detail="No file provided")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        preprocessed_df = preprocess_data(file_path)
        standardized_data = preprocessed_df.to_dict(orient="records")
        return {"status": "success", "message": "Data standardized successfully", "data": standardized_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))