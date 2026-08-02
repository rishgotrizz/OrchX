from typing import List
from fastapi import APIRouter, Depends, Request
from orchx_api.core.auth import get_current_user
from orchx_api.models import User
from orchx_api.schemas import DashboardPluginInfo

router = APIRouter()


@router.get("/", response_model=List[DashboardPluginInfo])
async def list_registered_plugins(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Retrieve metadata of all active plugins loaded in the kernel registries."""
    kernel = request.app.state.kernel
    context = request.app.state.kernel_context

    plugins_list = []

    # Providers
    for provider in context.provider_registry.list_all():
        manifest = provider.manifest
        plugins_list.append(
            DashboardPluginInfo(
                id=manifest.id,
                name=manifest.name,
                version=manifest.version,
                api_version=manifest.api_version,
                type="provider",
                capabilities=manifest.capabilities,
                permissions=manifest.permissions
            )
        )

    # Agents
    for agent in context.agent_registry.list_all():
        manifest = agent.manifest
        plugins_list.append(
            DashboardPluginInfo(
                id=manifest.id,
                name=manifest.name,
                version=manifest.version,
                api_version=manifest.api_version,
                type="agent",
                capabilities=manifest.capabilities,
                permissions=manifest.permissions
            )
        )

    # Tools
    for tool in context.tool_registry.list_all():
        manifest = tool.manifest
        plugins_list.append(
            DashboardPluginInfo(
                id=manifest.id,
                name=manifest.name,
                version=manifest.version,
                api_version=manifest.api_version,
                type="tool",
                capabilities=manifest.capabilities,
                permissions=manifest.permissions
            )
        )

    return plugins_list
