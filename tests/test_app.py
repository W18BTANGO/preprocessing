import pytest
from fastapi.testclient import TestClient
from app.main import app 
import json

# Fixture to set up the TestClient
@pytest.fixture
def client():
    return TestClient(app)

# Test case for the standardize endpoint with a valid file path
def test_standardize_valid_file(client):
    # Mock valid file path (the file should exist for this test to pass)
    valid_file_path = "./tests/mock_data.json"  # Make sure this file exists in your test directory
    
    # Send GET request to standardize endpoint
    response = client.get(f"/standardize?file_path={valid_file_path}")
    
    # Check the response status code
    assert response.status_code == 200
    
    # Check the response structure
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Data standardized successfully"
    
    # Check that the returned data is standardized (you can modify this as per your actual logic)
    assert isinstance(data["data"], list)  # Data should be in a list format
    assert "district_code" in data["data"][0]
    assert "price" in data["data"][0]
    assert "land_area" in data["data"][0]

# Test case for the standardize endpoint when the file does not exist
def test_standardize_file_not_found(client):
    invalid_file_path = "./tests/non_existent_file.json"
    
    response = client.get(f"/standardize?file_path={invalid_file_path}")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "File not found"

# Test case for missing file_path parameter
def test_standardize_missing_file_path(client):
    response = client.get("/standardize")
    
    assert response.status_code == 422  # Validation error because 'file_path' is missing
    data = response.json()
    assert "detail" in data
    assert "Field required" in str(data["detail"])

# Test case for standardizing empty or invalid data (you can simulate empty file content)
def test_standardize_empty_data(client):
    empty_file_path = "./tests/empty_mock_data.json"  # A file with an empty list or no valid data
    
    # Send GET request
    response = client.get(f"/standardize?file_path={empty_file_path}")
    
    # Ensure we handle empty or invalid data
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Data standardized successfully"
    assert data["data"] == []  # If no valid data, return an empty list or appropriate message
