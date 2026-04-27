from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from sklearn.linear_model import LinearRegression

app = FastAPI()

class SpendData(BaseModel):
    amounts: list[float]

@app.get("/")
def read_root():
    return {"status": "Vault BD API is online"}

@app.post("/analyze")
async def analyze_spending(data: SpendData):
    amounts = data.amounts
    if len(amounts) < 2:
        return {"error": "Not enough data to analyze"}

    # Z-Score Anomaly Detection
    mean = np.mean(amounts)
    std = np.std(amounts)
    # Flag anything 2 standard deviations away from mean
    anomalies = [x for x in amounts if abs((x - mean) / std) > 2] if std > 0 else []

    # Linear Regression Forecast for next month
    X = np.array(range(len(amounts))).reshape(-1, 1)
    y = np.array(amounts)
    model = LinearRegression().fit(X, y)
    prediction = model.predict([[len(amounts)]])[0]

    return {
        "anomalies_detected": anomalies,
        "forecasted_next_month": round(float(prediction), 2),
        "average_spend": round(float(mean), 2)
    }
