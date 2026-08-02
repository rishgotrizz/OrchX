from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from orchx_runtime.infrastructure_layer import ProviderCredentialManager
from orchx_runtime.provider_metadata import ProviderMetadataRegistry

router = APIRouter(prefix="/vault", tags=["vault"])

class CredentialPayload(BaseModel):
    provider: str
    credentials: Dict[str, str]

class RotationPayload(BaseModel):
    provider: str
    new_credentials: Dict[str, str]

# In a real app we'd inject this via Depends, but for simplicity here we assume
# it can be accessed globally or instantiated. For this milestone, we instantiate
# a global credential manager. We will initialize it properly in main.py lifespan.
global_cred_manager: Optional[ProviderCredentialManager] = None

def get_cred_manager() -> ProviderCredentialManager:
    if global_cred_manager is None:
        raise HTTPException(status_code=500, detail="Vault not initialized")
    return global_cred_manager

@router.post("/providers")
async def add_provider_credentials(payload: CredentialPayload, manager: ProviderCredentialManager = Depends(get_cred_manager)):
    errors = manager.validate_and_store(payload.provider, payload.credentials)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    return {"status": "success", "message": f"Credentials securely stored for {payload.provider}"}

@router.get("/providers")
async def list_providers(manager: ProviderCredentialManager = Depends(get_cred_manager)):
    registry = manager.metadata_registry
    providers = []
    for meta in registry.list_all():
        providers.append({
            "provider_id": meta.provider_id,
            "display_name": meta.display_name,
            "required": meta.required_credentials,
            "optional": meta.optional_credentials,
        })
    return {"providers": providers}

@router.put("/providers/{provider}")
async def update_credentials(provider: str, credentials: Dict[str, str], manager: ProviderCredentialManager = Depends(get_cred_manager)):
    errors = manager.validate_and_store(provider, credentials)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    return {"status": "success", "message": "Credentials updated."}

@router.delete("/providers/{provider}")
async def remove_provider(provider: str, manager: ProviderCredentialManager = Depends(get_cred_manager)):
    from orchx_runtime.vault import SecretAccessPolicy
    import uuid
    policy = SecretAccessPolicy(
        service="WebFrontend",
        provider=provider,
        reason="User requested removal",
        request_id=str(uuid.uuid4())
    )
    # We delete all known keys for this provider
    meta = manager.metadata_registry.get(provider)
    if not meta:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    try:
        keys_to_remove = meta.required_credentials + meta.optional_credentials
        for k in keys_to_remove:
            secret_key = f"{provider}_{k}"
            manager.vault_adapter.remove_secret_sync(secret_key, policy)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"status": "success", "message": f"Credentials removed for {provider}"}

@router.post("/validate")
async def validate_credentials(payload: CredentialPayload, manager: ProviderCredentialManager = Depends(get_cred_manager)):
    meta = manager.metadata_registry.get(payload.provider)
    if not meta:
        raise HTTPException(status_code=400, detail="Unknown provider")
    errors = meta.validate_credentials(payload.credentials)
    if errors:
        return {"valid": False, "errors": errors}
    return {"valid": True, "message": "Credentials syntax is valid"}

@router.post("/rotate")
async def rotate_credentials(payload: RotationPayload, manager: ProviderCredentialManager = Depends(get_cred_manager)):
    # Since credentials are just key-value pairs, we rotate them by updating them
    # which inherently invokes the store_secret flow which invalidates old ones.
    errors = manager.validate_and_store(payload.provider, payload.new_credentials)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    return {"status": "success", "message": "Credentials rotated successfully."}

@router.get("/providers/{provider}/capabilities")
async def get_capabilities(provider: str, manager: ProviderCredentialManager = Depends(get_cred_manager)):
    try:
        caps = manager.get_capabilities(provider)
        return {"provider": provider, "capabilities": caps.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
