import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from sklearn.linear_model import LinearRegression
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to your REAL database
MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client.vault_db

@app.get("/")
async def read_root():
    return {"status": "Vault BD Finance API Online"}

@app.get("/analytics")
async def get_db_spending():
    try:
        # Aggregation: Grouping by your real finance categories
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}, "total": {"$sum": "$amount"}}},
            {"$sort": {"total": -1}}
        ]
        cursor = db.transactions.aggregate(pipeline)
        results = await cursor.to_list(length=10)
        return {"category_summaries": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_spending():
    try:
        # Fetch real amounts for AI processing
        cursor = db.transactions.find({}, {"amount": 1})
        docs = await cursor.to_list(length=100)
        amounts = [d["amount"] for d in docs] if docs else [0]

        # AI Logic: Z-Score for Anomalies
        mean = np.mean(amounts)
        std = np.std(amounts)
        anomalies = [x for x in amounts if abs((x - mean) / std) > 1.5] if std > 0 else []

        # AI Logic: Forecasting next month
        X = np.array(range(len(amounts))).reshape(-1, 1)
        y = np.array(amounts)
        model = LinearRegression().fit(X, y)
        prediction = model.predict([[len(amounts)]])[0]

        return {
            "anomalies_detected": anomalies,
            "forecasted_next_month": round(float(prediction), 2),
            "average_spend": round(float(mean), 2),
            "database": "Live Vault_DB Connected"
        }
    except Exception as e:
        return {"error": str(e)}
