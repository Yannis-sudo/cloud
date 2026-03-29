"""Add folder endpoint"""

import fastapi
from app.schemas import AddFolderRequest
from app.database import init_db
from app.auth import verify_user
from app.constants import ERROR_INVALID_CREDENTIALS
from fastapi import HTTPException, status
from modules.email.addnewfolder import add_new_folder

router = fastapi.APIRouter()

@router.post("/addfolder", response_model=fastapi.Response, status_code=fastapi.status.HTTP_201_CREATED)
def add_folder(request: AddFolderRequest) -> fastapi.Response:
    # Initialize the database
    init_db()
    # Authorize the user by verifying email and password
    valid_user = verify_user(request.email, request.password)
    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )
    
    # Add the new folder
    try:
        success = add_new_folder(request.email, request.folder_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add folder to email server",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding folder: {str(e)}",
        )
    
    return fastapi.Response(status_code=fastapi.status.HTTP_201_CREATED)

    
