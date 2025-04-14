import pytest
from fastapi.testclient import TestClient
from api.fraud_api import app
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = TestClient(app)

# Get API key from environment
API_KEY = os.getenv("API_KEY", "test-api-key")

# Headers for authenticated requests
headers = {"X-API-Key": API_KEY}

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["title"] == "Credit Card Fraud Detection API"

def test_predict_endpoint():
    # Test data
    test_transaction = {
        "Time": 0.0,
        "V1": -1.359807,
        "V2": -0.072781,
        "V3": 2.536347,
        "V4": 1.378155,
        "V5": -0.338321,
        "V6": 0.462388,
        "V7": 0.239599,
        "V8": 0.098698,
        "V9": 0.363787,
        "V10": 0.090794,
        "V11": -0.551600,
        "V12": -0.617800,
        "V13": -0.991390,
        "V14": -0.311170,
        "V15": 1.468177,
        "V16": -0.470400,
        "V17": 0.207971,
        "V18": 0.025791,
        "V19": 0.403993,
        "V20": 0.251412,
        "V21": -0.018307,
        "V22": 0.277838,
        "V23": -0.110474,
        "V24": 0.066928,
        "V25": 0.128539,
        "V26": -0.189115,
        "V27": 0.133558,
        "V28": -0.021053,
        "Amount": 149.62
    }
    
    # Test without API key
    response = client.post("/predict", json=test_transaction)
    assert response.status_code == 403
    
    # Test with API key
    response = client.post("/predict", json=test_transaction, headers=headers)
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert "probability" in response.json()
    assert "transaction_id" in response.json()

def test_feedback_endpoint():
    feedback_data = {
        "transaction_id": "202504050033489834",
        "actual_class": 0,
        "notes": "Test feedback"
    }
    
    # Test with API key
    response = client.post("/feedback", json=feedback_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_model_health_endpoint():
    # Test with API key
    response = client.get("/model-health", headers=headers)
    assert response.status_code == 200
    assert "total_predictions" in response.json()
    assert "total_feedback" in response.json()

def test_invalid_transaction():
    invalid_transaction = {
        "Time": "invalid",  # Should be float
        "Amount": 100
    }
    
    # Test with API key
    response = client.post("/predict", json=invalid_transaction, headers=headers)
    assert response.status_code == 422  # Validation error

def test_invalid_api_key():
    test_transaction = {
        "Time": 0.0,
        "Amount": 100.0
    }
    
    # Test with invalid API key
    response = client.post("/predict", json=test_transaction, headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 403 