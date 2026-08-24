# ============================================================
# Step 1 - MODEL TRAINING
# ============================================================
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import logging
import hashlib
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import os

X, y = make_classification(
    n_samples=3000, n_features=10, n_informative=5, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=True, stratify=y, random_state=42)
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(n_estimators=100))
])

pipeline.fit(X_train, y_train)

# save everything not just the model
os.makedirs('models/v2', exist_ok=True)
joblib.dump(pipeline, 'models/v2/pipeline.pkl')
print(f'Pipeline saved: Accuracy: {pipeline.score(X_test, y_test):.3f}')

# ============================================================
# Step 2 - FAST API SERVER (WITH A/B TESTING)
# ============================================================

app = FastAPI(title="ML PREDICTION API", version='2.0')
logger = logging.getLogger("ab_test")

# Load BOTH models at startup for A/B testing
models = {
    "v1": joblib.load("models/v1/pipeline.pkl"),
    "v2": joblib.load("models/v2/pipeline.pkl")
}

# Traffic Split via environment variable (default 10%)
CANARY_PCT = int(os.getenv('CANARY_PCT', '10'))


def get_model_version(user_id: str) -> str:
    """Deterministic split -> same user will get same model everytime"""
    bucket = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
    return "v2" if bucket < CANARY_PCT else "v1"

# --- Pydantic Data Models ---


class PredictRequest(BaseModel):
    features: list[float]
    user_id: str = "anonymous"  # ADDED: Default to anonymous if not provided


class PredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    prediction: int
    probability: float
    model_version: str

# --- Endpoints ---


@app.get("/")
def root():
    return {
        "message": "Welcome to the ML Prediction API. Use /predict endpoint to get predictions.",
        "ab_test_status": f"{CANARY_PCT}% of traffic routing to v2"
    }


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        # 1. Determine version and grab correct model
        version = get_model_version(request.user_id)
        model = models[version]

        # 2. Make Prediction
        X = np.array(request.features).reshape(1, -1)
        pred = int(model.predict(X)[0])
        prob = float(model.predict_proba(X)[0, 1])

        # 3. Log for offline A/B analysis
        logger.info(
            f"version={version} user={request.user_id} pred={pred} prob={prob:.3f}")

        return PredictResponse(
            prediction=pred,
            probability=prob,
            model_version=version
        )
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.get("/ready")
def ready():
    try:
        # Check if BOTH models are alive and ready
        models["v1"].predict(np.zeros((1, models["v1"].n_features_in_)))
        models["v2"].predict(np.zeros((1, models["v2"].n_features_in_)))
        return {"status": "ready"}
    except Exception as ex:
        raise HTTPException(status_code=503, detail="Model Not Ready")
