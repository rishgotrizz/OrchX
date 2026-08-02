from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from orchx_api.core.auth import get_current_user
from orchx_api.core.database import get_db
from orchx_api.models import AuditLog, User
from orchx_api.schemas import DashboardStatsResponse

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_minimized_telemetry(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve minimized kernel metrics, health diagnostics, and logs."""
    kernel = request.app.state.kernel
    health = kernel.health()

    # Retrieve recent logs
    recent_logs_result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
    )
    recent_logs = recent_logs_result.scalars().all()

    return DashboardStatsResponse(
        status=health.status,
        version=health.version,
        uptime=health.uptime,
        loaded_components=health.loaded_components,
        capabilities=health.capabilities,
        providers_count=health.details.get("providers_count", 0),
        agents_count=health.details.get("agents_count", 0),
        tools_count=health.details.get("tools_count", 0),
        workflows_count=health.details.get("workflows_count", 0),
        recent_logs=recent_logs
    )
