import os
import certifi
import pymongo
import pandas as pd

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get the CA certificate for secure connection
ca = certifi.where()

class MongoDBClient:
    def __init__(self, database_name="ineuron", collection_name="customer_segmentation"):
        try:
            # Get MongoDB connection URL from environment variable
            mongo_db_url = os.getenv("MONGODB_URL_KEY")
            if mongo_db_url is None:
                raise Exception("Environment variable 'MONGODB_URL' is not set.")

            # Connect to MongoDB
            self.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.database = self.client[database_name]
            self.collection = self.database[collection_name]

            print("✅ Connected to MongoDB Atlas")

            """Deletes all existing documents from the collection to avoid duplication."""
            self.collection.delete_many({})
            print("🗑️ Deleted existing data from MongoDB")

            # ✅ Read CSV file properly with tab delimiter
            df = pd.read_csv(r"notebooks\marketing_campaign.csv", delimiter="\t")

            # ✅ Strip column names of any leading/trailing spaces
            df.columns = df.columns.str.strip()

            # ✅ Convert all values to string (MongoDB compatibility)
            df = df.astype(str)

            # ✅ Convert DataFrame to list of dictionaries
            data = df.to_dict(orient="records")

            # ✅ Insert the corrected data into MongoDB
            self.collection.insert_many(data)
            print(f"📂 Successfully uploaded {len(data)} records to MongoDB!")

            """Fetches and prints a few records from MongoDB for verification."""
            sample_data = list(self.collection.find({}, {"_id": 0}).limit(5))
            print("\n🔍 Sample Data from MongoDB:")
            for record in sample_data:
                print(record)

        except Exception as e:
            raise Exception(f"MongoDB connection failed: {e}")

