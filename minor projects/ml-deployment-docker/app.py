import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import os


X, y = make_classification(n_samples = 3000, n_features = 10, n_informative=5, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, stratify=y, random_state=42)
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(n_estimators=100))
])

pipeline.fit(X_train, y_train)

# save everything not just the model
os.makedirs('models/v2', exist_ok=True)
joblib.dump(pipeline, 'models/v2/pipeline.pkl')
print(f'Pipeline saved: Accuracy: {pipeline.score(X_test,y_test):.3f}')

# from sklearn.metrics import classification_report, confusion_matrix

# y_pred = pipeline.predict(X_test)

# print("\n" + "=" * 60)
# print("THE PROOF (Confusion Matrix)")
# print("=" * 60)
# print(confusion_matrix(y_test, y_pred))

# print("\nClassification Report:")
# print(classification_report(y_test, y_pred))


# Step 2 - FAST API SERVER

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ML PREDICTION API",version='2.0')

# Load at startup, not per request
MODEL_VERSION = os.getenv("MODEL_VERSION", "v2")
pipeline = joblib.load(f"models/{MODEL_VERSION}/pipeline.pkl")

class PredictRequest(BaseModel):
  features: list[float]

class PredictResponse(BaseModel):
  model_config = {"protected_namespaces":()}
  prediction: int
  probability : float
  model_version : str

@app.get("/")
def root():
  return {"message": f"Welcome to the ML Prediction API. Use /predict endpoint to get predictions. Version-{MODEL_VERSION}"}

@app.post("/predict", response_model = PredictResponse)
def predict(request: PredictRequest):
  try:
    X = np.array(request.features).reshape(1,-1)
    pred = int(pipeline.predict(X)[0])
    prob = float(pipeline.predict_proba(X)[0,1])
    return PredictResponse(
        prediction=pred, probability=prob,
        model_version=MODEL_VERSION
    )
  except Exception as ex:
    raise HTTPException(status_code=400, detail = str(ex))

@app.get("/ready")
def ready():
  try:
    pipeline.predict(np.zeros((1, pipeline.n_features_in_)))
    return {"status" : "ready"}
  except Exception as ex:
    raise HTTPException(status_code=503, detail= "Model Not Ready")


  # Run: uvicorn app:app --host 0.0.0.0 --port 8000