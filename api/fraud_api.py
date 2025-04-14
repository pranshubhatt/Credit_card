from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import APIKeyHeader
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel
import numpy as np
import joblib
import pandas as pd
import datetime
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from api.database import SessionLocal, Transaction as DBTransaction

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key_header

# At the top of fraud_api.py, update the path handling
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(os.path.dirname(current_dir), "models", "fraud_xgb_model.pkl")
scaler_path = os.path.join(os.path.dirname(current_dir), "models", "scaler.pkl")

# Add more detailed error messages
if not os.path.exists(model_path):
    print(f"ERROR: Model file not found at {model_path}")
    raise FileNotFoundError(f"Model file not found: {model_path}")
if not os.path.exists(scaler_path):
    print(f"ERROR: Scaler file not found at {scaler_path}")
    raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

# Add try-except for clearer error messages
try:
    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)
    print("Model loaded successfully")
    
    print(f"Loading scaler from {scaler_path}...")
    scaler = joblib.load(scaler_path)
    print("Scaler loaded successfully")
except Exception as e:
    print(f"ERROR loading model or scaler: {str(e)}")
    raise

# Initialize FastAPI with security middleware
app = FastAPI(title="Credit Card Fraud Detection API",
             description="API for detecting fraudulent credit card transactions",
             version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Rate limiting - 100 requests per minute
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # Simple rate limiting based on IP
    client_ip = request.client.host
    redis_key = f"rate_limit:{client_ip}"
    
    response = await call_next(request)
    return response

# Monitoring data file path (keep it simple)
MONITORING_DATA_FILE = os.path.join(current_dir, "monitoring_data.json")

# Initialize empty monitoring data if file doesn't exist
if not os.path.exists(MONITORING_DATA_FILE):
    with open(MONITORING_DATA_FILE, 'w') as f:
        json.dump({"predictions": [], "feedback": []}, f)

# Define the input data schema
class TransactionInput(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float

# Define the prediction response schema
class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    timestamp: str
    transaction_id: str
    important_features: Dict[str, float]

# Define feedback schema for concept drift monitoring
class FeedbackModel(BaseModel):
    transaction_id: str
    actual_class: int  # 0 for not fraud, 1 for fraud
    notes: Optional[str] = None

# Generate a unique transaction ID
def generate_transaction_id():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(np.random.randint(1000, 9999))

# Get top 5 important features for a prediction
def get_important_features(input_data, feature_names):
    # For tree-based models like XGBoost, we can use feature_importances_
    if hasattr(model, 'feature_importances_'):
        # Get the feature importance values
        importance = model.feature_importances_
        
        # Create a dictionary of feature name to importance
        feature_importance = dict(zip(feature_names, importance))
        
        # Sort and get top 5
        sorted_features = dict(sorted(feature_importance.items(), 
                                    key=lambda item: abs(item[1]), 
                                    reverse=True)[:5])
        return sorted_features
    else:
        # Fallback for models that don't have feature_importances_
        return {"Note": "Feature importance not available for this model type"}

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Update the predict endpoint to store in database
@app.post("/predict", response_model=PredictionResponse)
async def predict(data: TransactionInput, api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    try:
        # Convert input to array
        feature_names = list(data.__annotations__.keys())
        input_values = [getattr(data, field) for field in feature_names]
        input_data = np.array([input_values])
        
        # Scale the input
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction_class = model.predict(input_scaled)[0]
        prediction_proba = model.predict_proba(input_scaled)[0, 1]
        
        # Determine result
        result = "Fraud" if prediction_class == 1 else "Not Fraud"
        
        # Get important features
        important_features = get_important_features(input_data, feature_names)
        
        # Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # Create database record
        db_transaction = DBTransaction(
            transaction_id=transaction_id,
            timestamp=datetime.datetime.now(),
            prediction=result,
            probability=float(prediction_proba),
            amount=data.Amount,
            v1=data.V1,
            v2=data.V2,
            v3=data.V3,
            v4=data.V4,
            v5=data.V5,
            v6=data.V6,
            v7=data.V7,
            v8=data.V8,
            v9=data.V9,
            v10=data.V10,
            v11=data.V11,
            v12=data.V12,
            v13=data.V13,
            v14=data.V14,
            v15=data.V15,
            v16=data.V16,
            v17=data.V17,
            v18=data.V18,
            v19=data.V19,
            v20=data.V20,
            v21=data.V21,
            v22=data.V22,
            v23=data.V23,
            v24=data.V24,
            v25=data.V25,
            v26=data.V26,
            v27=data.V27,
            v28=data.V28
        )
        
        db.add(db_transaction)
        db.commit()
        
        # Create response
        response = {
            "prediction": result,
            "probability": float(prediction_proba),
            "timestamp": datetime.datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "important_features": important_features
        }
        
        return response
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Endpoint for receiving feedback (for monitoring concept drift)
@app.post("/feedback")
def record_feedback(feedback: FeedbackModel):
    try:
        with open(MONITORING_DATA_FILE, 'r') as f:
            monitoring_data = json.load(f)
        
        # Add feedback
        monitoring_data["feedback"].append({
            "transaction_id": feedback.transaction_id,
            "actual_class": feedback.actual_class,
            "notes": feedback.notes,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        with open(MONITORING_DATA_FILE, 'w') as f:
            json.dump(monitoring_data, f)
        
        return {"status": "success", "message": "Feedback recorded"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")

# Endpoint to get model health metrics
@app.get("/model-health")
def get_model_health():
    try:
        with open(MONITORING_DATA_FILE, 'r') as f:
            monitoring_data = json.load(f)
        
        predictions = monitoring_data["predictions"]
        feedback = monitoring_data["feedback"]
        
        # Match predictions with feedback
        matched_data = []
        for fb in feedback:
            for pred in predictions:
                if fb["transaction_id"] == pred["transaction_id"]:
                    matched_data.append({
                        "transaction_id": fb["transaction_id"],
                        "predicted": pred["prediction"],
                        "actual": fb["actual_class"],
                        "probability": pred["probability"],
                        "timestamp": pred["timestamp"]
                    })
        
        # Calculate metrics if we have matched data
        if matched_data:
            correct = sum(1 for item in matched_data if item["predicted"] == item["actual"])
            total = len(matched_data)
            accuracy = correct / total if total > 0 else 0
            
            # Get recent accuracy (last 50 transactions or less)
            recent_matched = matched_data[-50:] if len(matched_data) >= 50 else matched_data
            recent_correct = sum(1 for item in recent_matched if item["predicted"] == item["actual"])
            recent_total = len(recent_matched)
            recent_accuracy = recent_correct / recent_total if recent_total > 0 else 0
            
            # Check for concept drift based on accuracy drop
            drift_detected = recent_accuracy < accuracy * 0.9  # 10% drop as threshold
            
            return {
                "total_predictions": len(predictions),
                "total_feedback": len(feedback),
                "matched_predictions": len(matched_data),
                "overall_accuracy": accuracy,
                "recent_accuracy": recent_accuracy,
                "concept_drift_detected": drift_detected,
                "drift_details": "Recent accuracy has dropped significantly compared to overall accuracy." if drift_detected else "No significant drift detected."
            }
        else:
            return {
                "total_predictions": len(predictions),
                "total_feedback": len(feedback),
                "matched_predictions": 0,
                "status": "Not enough data to calculate model health metrics"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating model health: {str(e)}")

# Root endpoint for API info
@app.get("/")
def read_root():
    return {
        "title": "Credit Card Fraud Detection API",
        "version": "1.0.0",
        "description": "API for detecting fraudulent credit card transactions",
        "endpoints": [
            {"path": "/predict", "method": "POST", "description": "Predict if a transaction is fraudulent"},
            {"path": "/feedback", "method": "POST", "description": "Submit feedback on predictions for monitoring"},
            {"path": "/model-health", "method": "GET", "description": "Get model health metrics and drift detection"}
        ]
    }

# Add this at the end of fraud_api.py
if __name__ == "__main__":
    import uvicorn
    print("Starting server directly...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
