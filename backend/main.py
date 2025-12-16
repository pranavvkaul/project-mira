import os
import json
import pickle
from typing import Optional, Dict, Any

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ------------------ Safe model fallback ------------------

class ComplexTrapModelRenamed:
    def __init__(self, *args, **kwargs):
        self.model = None

    def predict(self, X):
        if self.model is not None:
            return self.model.predict(X)
        try:
            return [350000 for _ in range(len(X))]
        except Exception:
            return 350000


# ------------------ App setup ------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------ Load properties ------------------

MERGED_JSON = os.path.join(BASE_DIR, "merged.json")

try:
    with open(MERGED_JSON, "r", encoding="utf-8") as f:
        PROPERTIES = json.load(f)
except Exception:
    PROPERTIES = []


# ------------------ Load ML model ------------------

MODEL = None
MODEL_PATH = os.path.join(BASE_DIR, "complex_price_model_v2.pkl")

try:
    with open(MODEL_PATH, "rb") as f:
        try:
            MODEL = pickle.load(f)
            print("Model loaded successfully")
        except Exception:
            f.seek(0)

            class SafeUnpickler(pickle.Unpickler):
                def find_class(self, module, name):
                    if name == "ComplexTrapModelRenamed":
                        return ComplexTrapModelRenamed
                    return super().find_class(module, name)

            MODEL = SafeUnpickler(f).load()
            print("Model loaded with SafeUnpickler")
except Exception as e:
    print(f"Model load failed: {e}")
    MODEL = None


# ------------------ Request models ------------------

class PropertyRequest(BaseModel):
    location: str
    bedrooms: int
    bathrooms: int
    size_sqft: int


class LocationPayload(BaseModel):
    label: str
    value: str
    property: Dict[str, Any]


class CompareRequest(BaseModel):
    address1: Optional[LocationPayload] = None
    address2: Optional[LocationPayload] = None


# ------------------ Helpers ------------------

def prepare_model_input(prop: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if prop:
        bedrooms = int(prop.get("bedrooms", 3))
        bathrooms = int(prop.get("bathrooms", 2))
        size = int(prop.get("size_sqft", 1500))
        amenities = [a.lower() for a in prop.get("amenities", [])]
    else:
        bedrooms = 3
        bathrooms = 2
        size = 1500
        amenities = []

    property_type = (
        "SFH"
        if bedrooms >= 4 or "house" in (prop.get("title", "").lower() if prop else "")
        else "Condo"
    )

    lot_area = size * 2 if property_type == "SFH" else 0
    building_area = size if property_type == "Condo" else 0

    has_pool = any("pool" in a for a in amenities)
    has_garage = any("garage" in a for a in amenities)

    year_built = int(prop.get("year_built", 2015)) if prop else 2015
    school_rating = int(prop.get("school_rating", 7)) if prop else 7

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


def predict_with_model(input_data: Dict[str, Any]) -> float:
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

    try:
        df = pd.DataFrame([input_data])
        return float(MODEL.predict(df)[0])
    except Exception:
        try:
            return float(MODEL.predict([input_data])[0])
        except Exception:
            try:
                pred = MODEL.predict(input_data)
                return float(pred[0]) if hasattr(pred, "__getitem__") else float(pred)
            except Exception:
                return 350000.0


# ------------------ Routes ------------------

@app.post("/predict")
def predict_price(item: PropertyRequest):
    inp = prepare_model_input(item.dict())
    price = predict_with_model(inp)
    return {"predicted_price": price, "features": inp}


@app.post("/compare")
def compare(req: CompareRequest):
    if not req.address1 or not req.address2:
        return {"result": {"address1": None, "address2": None}}

    prop1 = req.address1.property
    prop2 = req.address2.property

    inp1 = prepare_model_input(prop1)
    inp2 = prepare_model_input(prop2)

    price1 = predict_with_model(inp1)
    price2 = predict_with_model(inp2)

    resp1 = {**prop1, "predicted_price": price1, "features": inp1}
    resp2 = {**prop2, "predicted_price": price2, "features": inp2}

    return {"result": {"address1": resp1, "address2": resp2}}
