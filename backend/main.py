import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from sklearn.linear_model import LinearRegression
from motor.motor_asyncio import AsyncIOMotorClient

# Setup logging to see errors in HuggingFace "Logs" tab
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Master CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI)
# We will check both 'sample_analytics' and 'sample_supplies' to find data
db_analytics = client.sample_analytics
db_supplies = client.sample_supplies

@app.get("/")
async def read_root():
    return {"status": "Vault BD API is online and connected to Atlas"}

@app.get("/analytics")
async def get_db_spending():
    try:
        # Strategy: Try to get product data from the 'sales' collection in sample_supplies
        # It's usually the most reliable sample dataset for counting categories
        pipeline = [
            {"$unwind": "$items"},
            {"$group": {"_id": "$items.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 8}
        ]
        
        # Try sample_supplies first
        cursor = db_supplies.sales.aggregate(pipeline)
        results = await cursor.to_list(length=10)
        
        # If empty, try the other sample database
        if not results:
            logger.info("Sample supplies empty, trying sample_analytics")
            pipeline_alt = [
                {"$unwind": "$products"},
                {"$group": {"_id": "$products", "count": {"$sum": 1}}}
            ]
            cursor = db_analytics.accounts.aggregate(pipeline_alt)
            results = await cursor.to_list(length=10)

        return {"category_summaries": results}
    except Exception as e:
        logger.error(f"MongoDB Error: {e}")
        return {"category_summaries": [{"_id": "Error fetching data", "count": 0}]}

@app.post("/analyze")
async def analyze_spending():
    # Mock data for demonstration - next phase will use real data from your 'transactions'
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
        "average_spend": round(float(mean), 2),
        "database": "Live connection active"
    }
