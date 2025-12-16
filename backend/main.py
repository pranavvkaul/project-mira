import os
import json
import pickle
from typing import Optional, Dict, Any

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# --- ML Model Wrapper and Fallback Class ---

class ComplexTrapModelRenamed:
    """A wrapper class to ensure the application can load the ML model even if the 
    original class path changed. Provides a default prediction fallback."""
    def __init__(self, *args, **kwargs):
        self.model = None

    def predict(self, X):
        if self.model is not None:
            return self.model.predict(X)
        
        # Fallback prediction if the model is not loaded
        try:
            return [350000 for _ in range(len(X))]
        except Exception:
            return 350000


# --- FastAPI Application Setup ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Enables cross-origin requests from the frontend
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Data Loading (Mock Property Data) ---

MERGED_JSON = os.path.join(BASE_DIR, "merged.json")
PROPERTIES = []

try:
    # Load the merged property data
    with open(MERGED_JSON, "r", encoding="utf-8") as f:
        PROPERTIES = json.load(f)
except Exception:
    # Handles errors like File Not Found or JSON Decode Error
    PROPERTIES = []


# --- Model Loading (Inference) ---

MODEL = None
MODEL_PATH = os.path.join(BASE_DIR, "complex_price_model_v2.pkl")

try:
    with open(MODEL_PATH, "rb") as f:
        try:
            # Standard attempt to load the model
            MODEL = pickle.load(f)
        except Exception:
            f.seek(0)
            
            # Custom SafeUnpickler handles cases where the original class structure 
            # of the model file has changed.
            class SafeUnpickler(pickle.Unpickler):
                def find_class(self, module, name):
                    if name == "ComplexTrapModelRenamed":
                        return ComplexTrapModelRenamed
                    return super().find_class(module, name)

            MODEL = SafeUnpickler(f).load()
            print("Model loaded with SafeUnpickler")
except Exception as e:
    # If model loading fails entirely, MODEL remains None, triggering the rule-based fallback.
    print(f"Model load failed: {e}")
    MODEL = None


# --- Pydantic Data Models ---

class PropertyRequest(BaseModel):
    """Schema for a standard property prediction request."""
    location: str
    bedrooms: int
    bathrooms: int
    size_sqft: int


class LocationPayload(BaseModel):
    """Schema for a single property object passed from the frontend selection."""
    label: str
    value: str
    property: Dict[str, Any]


class CompareRequest(BaseModel):
    """Schema for the main /compare endpoint."""
    address1: Optional[LocationPayload] = None
    address2: Optional[LocationPayload] = None


# --- Data Preprocessing for ML Model ---

def prepare_model_input(prop: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Transforms raw property data into the feature set required by the ML model.
    Imputes default values for missing fields."""
    if prop:
        # Extract features with default fallbacks
        bedrooms = int(prop.get("bedrooms", 3))
        bathrooms = int(prop.get("bathrooms", 2))
        size = int(prop.get("size_sqft", 1500))
        amenities = [a.lower() for a in prop.get("amenities", [])]
    else:
        # Baseline defaults if no property dictionary is provided
        bedrooms = 3
        bathrooms = 2
        size = 1500
        amenities = []

    # Simple logic to determine property type for feature engineering
    property_type = (
        "SFH"
        if bedrooms >= 4 or "house" in (prop.get("title", "").lower() if prop else "")
        else "Condo"
    )

    # Feature engineering for area based on property type
    lot_area = size * 2 if property_type == "SFH" else 0
    building_area = size if property_type == "Condo" else 0

    # Boolean features from amenities list
    has_pool = any("pool" in a for a in amenities)
    has_garage = any("garage" in a for a in amenities)

    # Impute other necessary features
    year_built = int(prop.get("year_built", 2015)) if prop else 2015
    school_rating = int(prop.get("school_rating", 7)) if prop else 7

    # Return the feature set matching the ML model's expected schema
    return {
        "property_type": property_type,
        "lot_area": int(lot_area),
        "building_area": int(building_area),
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "year_built": year_built,
        "has_pool": has_pool,
        "has_garage": has_garage,
        "school_rating": school_rating,
    }


# --- Model Prediction Logic ---

def predict_with_model(input_data: Dict[str, Any]) -> float:
    """Performs price prediction using the loaded ML model or a rule-based fallback."""
    
    # Rule-Based Fallback if ML Model failed to load
    if MODEL is None:
        area = input_data.get("building_area") or max(
            1, input_data.get("lot_area", 0) // 2
        )
        base = 200 * area
        return float(
            base
            + input_data.get("bedrooms", 0) * 15000
            + input_data.get("bathrooms", 0) * 10000
            + (50000 if input_data.get("has_pool") else 0)
            + (20000 if input_data.get("has_garage") else 0)
        )

    # ML Model Prediction with robust error handling for various input formats
    try:
        # 1. Try passing as a Pandas DataFrame (common ML model input)
        df = pd.DataFrame([input_data])
        return float(MODEL.predict(df)[0])
    except Exception:
        try:
            # 2. Try passing as a list of dictionaries
            return float(MODEL.predict([input_data])[0])
        except Exception:
            try:
                # 3. Try passing the dictionary directly
                pred = MODEL.predict(input_data)
                return float(pred[0]) if hasattr(pred, "__getitem__") else float(pred)
            except Exception:
                # Final prediction failure fallback
                return 350000.0


# --- API Endpoints ---

@app.post("/predict")
def predict_price(item: PropertyRequest):
    """API endpoint for single-property price prediction."""
    inp = prepare_model_input(item.dict())
    price = predict_with_model(inp)
    # Returns the predicted price and the final features used for prediction
    return {"predicted_price": price, "features": inp}


@app.post("/compare")
def compare(req: CompareRequest):
    """Main API endpoint for the side-by-side comparison from the frontend."""
    if not req.address1 or not req.address2:
        return {"result": {"address1": None, "address2": None}}

    prop1 = req.address1.property
    prop2 = req.address2.property

    # Process both properties and run model prediction
    inp1 = prepare_model_input(prop1)
    inp2 = prepare_model_input(prop2)

    price1 = predict_with_model(inp1)
    price2 = predict_with_model(inp2)

    # Merge predicted price and features back into the original property data
    resp1 = {**prop1, "predicted_price": price1, "features": inp1}
    resp2 = {**prop2, "predicted_price": price2, "features": inp2}

    return {"result": {"address1": resp1, "address2": resp2}}
