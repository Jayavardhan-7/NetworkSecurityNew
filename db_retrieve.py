import os
import sys
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get MongoDB URI from environment
MONGO_DB_URL = os.getenv("MONGO_DB_URI")
print(f"Using MONGO_DB_URL: {MONGO_DB_URL}")

# Check if URI is loaded correctly
if not MONGO_DB_URL:
    print("❌ MONGO_DB_URL not found in .env file")
    sys.exit(1)

# MongoDB database and collection names
DATABASE_NAME = "jayai"
COLLECTION_NAME = "NetworkData"

try:
    # Connect to MongoDB
    mongo_client = pymongo.MongoClient(MONGO_DB_URL)
    db = mongo_client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Fetch sample documents to debug
    sample_docs = list(collection.find().limit(5))
    print(f"✅ Retrieved {len(sample_docs)} sample documents from MongoDB")

    # Convert to DataFrame
    df = pd.DataFrame(sample_docs)

    if df.empty:
        print("⚠️ No data retrieved. Collection may be empty or not reachable.")
    else:
        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)
        df.replace({"na": np.nan}, inplace=True)

        print("✅ DataFrame created from MongoDB collection:\n")
        print(df.head())

except Exception as e:
    print("❌ Error occurred while connecting to MongoDB or retrieving data:")
    print(str(e))
