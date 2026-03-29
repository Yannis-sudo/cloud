"""Get folders endpoint"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import GetFoldersRequest, GetFoldersResponse
from app.database import init_db
from app.auth import verify_user
from app.constants import ERROR_INVALID_CREDENTIALS
from app.modules.email.getfolders import get_folders

router = APIRouter(tags=["accounts"])

@router.post("/getfolders", response_model=GetFoldersResponse)
def get_folders_endpoint(request: GetFoldersRequest) -> GetFoldersResponse:
    # Initialize the database
    init_db()
    # Authorize the user by verifying email and password
    valid_user = verify_user(request.email, request.password)
    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )
    
    # Get folders from email server
    try:
        folders = get_folders(request.email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving folders: {str(e)}",
        )
    
    return GetFoldersResponse(folders=folders)