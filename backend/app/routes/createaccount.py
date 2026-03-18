"""Account creation endpoints."""

from fastapi import APIRouter, HTTPException, status
from pymongo import errors

from app.database import init_db
from app.schemas import CreateAccountRequest, SuccessResponse
from app.constants import ERROR_EMAIL_EXISTS, SUCCESS_ACCOUNT_CREATED

# MongoDb implementation with atomic ID generation and unique email constraint
def _get_next_id(db, collection_name: str) -> int:
    """Atomically increment and return the next integer ID for a collection."""
    counter = db.counters.find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]


def create_user(username: str, email: str, password: str):
    """Create a user in MongoDB. Raises DuplicateKeyError on conflicts."""
    db = init_db()
    user_id = _get_next_id(db, "users")
    return db.users.insert_one({
        "id": user_id,
        "username": username,
        "email": email,
        "password": password
    })

# FastAPI router setup
router = APIRouter(tags=["accounts"])

# Router endpoint
@router.post("/create-account", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_account(request: CreateAccountRequest) -> SuccessResponse:
    """Create a new user account using the shared database helper."""
    try:
        create_user(request.username, request.email, request.password)

        return SuccessResponse(message=SUCCESS_ACCOUNT_CREATED)
    except errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_EMAIL_EXISTS,
        )
