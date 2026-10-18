"""
Database Connection Manager for Smart Hospital System.
Handles connection to MongoDB via PyMongo, with optional offline mock fallback
so that the project is 100% runnable anywhere (e.g. viva rooms, offline laptops).
"""

import os
from typing import Tuple, Any
from dotenv import load_dotenv
import pymongo
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

# Load environment variables
load_dotenv()

DEFAULT_MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DEFAULT_DB_NAME = os.getenv("DATABASE_NAME", "SmartHospitalDB")
ENABLE_OFFLINE_MOCK = os.getenv("ENABLE_OFFLINE_MOCK_FALLBACK", "True").lower() == "true"


def get_db_connection(
    uri: str = DEFAULT_MONGO_URI,
    db_name: str = DEFAULT_DB_NAME,
    timeout_ms: int = 2500
) -> Tuple[Any, Any, bool]:
    """
    Connect to MongoDB instance.
    Returns:
        (client, db, is_mock)
    """
    try:
        # Attempt connection to live MongoDB instance
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        # Verify connection with a quick ping command
        client.admin.command("ping")
        db = client[db_name]
        return client, db, False

    except pymongo.errors.PyMongoError as exc:
        if ENABLE_OFFLINE_MOCK:
            import mongomock
            print("\n[!] Notice: Could not connect to MongoDB server:")
            print(f"    Reason: {exc}")
            print("[*] Automatically activated In-Memory Mock Mode (mongomock).")
            print("    The application is fully functional for viva/demo.")
            print("    To connect to a live MongoDB server or Atlas, check your credentials or .env file.\n")
            client = mongomock.MongoClient()
            db = client[db_name]
            return client, db, True
        else:
            raise ConnectionError(
                f"Failed to connect to MongoDB server at {uri}. "
                "Ensure mongod service is running or check your network/credentials."
            ) from exc
