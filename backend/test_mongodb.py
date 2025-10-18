"""
MongoDB Connection Test Script
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi  # provides CA bundle for TLS verification

# Load environment variables
load_dotenv()

def test_connection():
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb+srv://mothicaptures:mothi@cluster0.858fyte.mongodb.net/')
    db_name = os.getenv('DB_NAME', 'tangytown')

    if not mongodb_uri:
        print("❌ ERROR: MONGODB_URI not found in .env")
        return False

    # Mask password in output
    try:
        masked_uri = mongodb_uri.split('@')[0].split('://')[0] + "://***:***@" + mongodb_uri.split('@')[1]
    except:
        masked_uri = "***"

    print("\nConfiguration:")
    print(f"   Database Name: {db_name}")
    print(f"   Connection: {masked_uri}\n")
    print("Testing connection...")

    try:
        # Connect to MongoDB
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000
        )

        db = client[db_name]

        # Test connection
        print(f"Connected to database: {db.name}")
        print("Databases:", client.list_database_names())

        # Optional: test write & read
        test_collection = db.test_connection
        result = test_collection.insert_one({"test": "connection", "status": "success"})
        doc = test_collection.find_one({"_id": result.inserted_id})
        print(f"Write & read successful: {doc.get('test')}")
        test_collection.delete_one({"_id": result.inserted_id})

        client.close()
        return True

    except Exception as e:
        print("\nCONNECTION FAILED")
        print("Error:", e)
        return False

if __name__ == "__main__":
    test_connection()
