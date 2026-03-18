"""MongoDB database access layer."""

from pymongo import MongoClient, errors
from pymongo.collection import Collection
from bson import ObjectId

from app.config import get_settings

settings = get_settings()
_mongo_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Get or create a single MongoDB client instance."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)
        _mongo_client.admin.command("ping")
    return _mongo_client


def get_database():
    """Get the configured MongoDB database."""
    return get_mongo_client()[settings.DATABASE_NAME]


def init_db():
    """Initialize MongoDB collections and indexes."""
    db = get_database()
    users = db.users
    emails = db.emails
    users.create_index("email", unique=True)
    emails.create_index([("user_email", 1), ("email", 1)], unique=True)

    return db

def get_user_emails(email: str):
    """Get associated email records for a user by user email."""
    db = init_db()
    result = db.emails.find({"user_email": email})
    return list(result)


def add_user_email(user_email: str, email: str, server: str, password: str):
    """Optional helper: add email account for user."""
    db = init_db()
    return db.emails.insert_one({"user_email": user_email, "email": email, "server": server, "password": password})
