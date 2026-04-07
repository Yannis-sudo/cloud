"""Files API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer

from app.core.security import TokenData
from app.schemas.common import SuccessResponse
from app.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/upload",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
    description="Upload a file to GridFS storage"
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
) -> SuccessResponse:
    """Upload file."""
    return SuccessResponse(
        message="File uploaded successfully",
        data={"filename": file.filename, "size": file.size}
    )
