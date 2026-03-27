from app.database import init_db

def verify_user(email: str, password: str) -> bool:
    """Verify user credentials."""
    db = init_db()
    user = db.users.find_one({"email": email.lower(), "password": password})
    return user is not None

def get_user_by_email(email: str):
    """Return user object by email."""
    db = init_db()
    return db.users.find_one({"email": email.lower()})