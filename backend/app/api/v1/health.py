"""Health API endpoints."""

from fastapi import APIRouter
from app.schemas.common import HealthCheckResponse
from app.database.connection import health_check

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=200,
    summary="Detailed health check",
    description="Check the health of all application services"
)
async def detailed_health_check():
    """Detailed health check endpoint."""
    try:
        # Check database
        db_healthy = health_check()
        
        services = {
            "database": "healthy" if db_healthy else "unhealthy",
            "email_service": "healthy",  # TODO: Implement actual check
            "file_storage": "healthy"   # TODO: Implement actual check
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in services.values()) else "unhealthy"
        
        return HealthCheckResponse(
            status=overall_status,
            version="1.0.0",
            services=services
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            version="1.0.0",
            services={
                "database": "unhealthy",
                "email_service": "unhealthy",
                "file_storage": "unhealthy"
            }
        )
