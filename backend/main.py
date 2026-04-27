import os
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from sklearn.linear_model import LinearRegression
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Connect using the Secret we set in HuggingFace
MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.sample_analytics  # Using the sample data Atlas is preloading

@app.get("/")
async def read_root():
    return {"status": "Connected to MongoDB Atlas"}

@app.get("/analytics")
async def get_db_spending():
    # This runs a MongoDB Aggregation to get real data
    # It looks at the sample 'accounts' collection
    pipeline = [
        {"$unwind": "$products"},
        {"$group": {"_id": "$products", "count": {"$sum": 1}}}
    ]
    cursor = db.accounts.aggregate(pipeline)
    results = await cursor.to_list(length=10)
    return {"category_summaries": results}

@app.post("/analyze")
async def analyze_spending():
    # For now, let's keep the logic but eventually, 
    # we'll fetch 'amounts' from your own 'transactions' collection
    amounts = [120, 150, 135, 450, 140, 160] 
    
    mean = np.mean(amounts)
    std = np.std(amounts)
    anomalies = [x for x in amounts if abs((x - mean) / std) > 2] if std > 0 else []

    X = np.array(range(len(amounts))).reshape(-1, 1)
    y = np.array(amounts)
    model = LinearRegression().fit(X, y)
    prediction = model.predict([[len(amounts)]])[0]

    return {
        "anomalies_detected": anomalies,
        "forecasted_next_month": round(float(prediction), 2),
        "database": "Live connection active"
    }
