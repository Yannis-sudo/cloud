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
    email_addresses = db.email_addresses  # Renamed from emails to email_addresses
    users.create_index("email", unique=True)
    email_addresses.create_index([("user_email", 1), ("email", 1)], unique=True)  # Updated index for email_addresses

    return db


def get_user_emails(email: str):
    """Get associated email records for a user by user email."""
    db = init_db()
    # Check if there are any email records for this user
    count = db.email_addresses.count_documents({"user_email": email.lower()})
    if count == 0:
        return "Email not found"
    
    # Return the list of email records
    return list(db.email_addresses.find({"user_email": email.lower()}))


def add_user_email(user_email: str, email: str, server: str, password: str):
    """Optional helper: add email account for user."""
    db = init_db()
    return db.email_addresses.insert_one({"user_email": user_email.lower(), "email": email, "server": server, "password": password})
