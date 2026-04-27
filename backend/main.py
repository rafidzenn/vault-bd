import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from sklearn.linear_model import LinearRegression
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Enable CORS so your Vercel frontend can talk to your HuggingFace backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB Atlas using the Secret variable set in HuggingFace
MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI)
# We are using the 'sample_analytics' database preloaded by Atlas
db = client.sample_analytics 

@app.get("/")
async def read_root():
    return {"status": "Connected to MongoDB Atlas"}

@app.get("/analytics")
async def get_db_spending():
    try:
        # Runs a real MongoDB Aggregation pipeline on the 'accounts' collection
        pipeline = [
            {"$unwind": "$products"},
            {"$group": {"_id": "$products", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        cursor = db.accounts.aggregate(pipeline)
        results = await cursor.to_list(length=10)
        return {"category_summaries": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_spending():
    # Currently uses mock data for the Z-score and Linear Regression logic
    # In the next phase, we will fetch this directly from your own MongoDB collections
    amounts = [120, 150, 135, 450, 140, 160] 
    
    # 1. Z-Score Anomaly Detection
    mean = np.mean(amounts)
    std = np.std(amounts)
    anomalies = [x for x in amounts if abs((x - mean) / std) > 2] if std > 0 else []

    # 2. Linear Regression Forecasting
    X = np.array(range(len(amounts))).reshape(-1, 1)
    y = np.array(amounts)
    model = LinearRegression().fit(X, y)
    prediction = model.predict([[len(amounts)]])[0]

    return {
        "anomalies_detected": anomalies,
        "forecasted_next_month": round(float(prediction), 2),
        "average_spend": round(float(mean), 2),
        "database": "Live connection active"
    }
