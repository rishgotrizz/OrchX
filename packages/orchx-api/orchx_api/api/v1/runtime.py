import logging
import time
import uuid
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from orchx_core.interfaces.provider_contracts import ProviderRequest, ProviderResponse
from orchx_runtime.selection_strategies import ExplicitSelectionStrategy
from orchx_api.api.v1.vault_routes import get_cred_manager
from orchx_runtime.infrastructure_layer import ProviderCredentialManager

logger = logging.getLogger("orchx.api.runtime")

SAFE_ERROR_MESSAGES = {
    "NO_PROVIDER_CONFIGURED": "No AI providers are configured yet. Add a provider in Settings Studio before executing prompts.",
    "PROVIDER_NOT_CONFIGURED": "The selected provider is not configured. Please add its API key in Settings Studio.",
    "PROVIDER_AUTH_FAILED": "Provider authentication failed. Check the configured API key.",
    "PROVIDER_UNAVAILABLE": "This provider is currently unavailable. Try again or use another configured provider.",
    "PROVIDER_TIMEOUT": "The provider took too long to respond. Please try again.",
    "PROVIDER_REQUEST_FAILED": "The provider request failed. Please try again.",
    "INVALID_PROVIDER_CONFIGURATION": "The provider configuration is invalid. Review the provider settings."
}

def sanitize_error(text: str) -> str:
    import re
    # Remove any potential sk- or gsk_ keys
    text = re.sub(r'\b(sk-|gsk_)[A-Za-z0-9_-]{10,}\b', '••••••••', text)
    # Remove any authorization headers pattern
    text = re.sub(r'(?i)authorization\s*:\s*\S+', 'Authorization: ••••••••', text)
    text = re.sub(r'(?i)bearer\s+\S+', 'Bearer ••••••••', text)
    if any(kw in text.lower() for kw in ("token", "api_key", "secret", "private")):
        return "Authentication failed or invalid API key configuration."
    return text

router = APIRouter(prefix="", tags=["runtime"])


class ExecutionRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to execute")
    conversation_id: Optional[str] = Field(None, description="Optional conversation tracking ID")
    model: Optional[str] = Field(None, description="Optional target model override")
    provider: Optional[str] = Field(None, description="Optional target provider override")
    stream: bool = Field(False, description="Whether to stream the response chunks")


class ExecutionResponse(BaseModel):
    success: bool
    response: str
    provider: str
    model: str
    latency_ms: float
    request_id: str


class CredentialBridgeRequest(BaseModel):
    provider: str = Field(..., description="The provider ID, e.g. 'groq'")
    api_key: str = Field(..., description="The plaintext API key to store")


@router.post("/runtime/execute", response_model=ExecutionResponse)
async def execute_prompt(request: ExecutionRequest, fastapi_req: Request):
    """
    Execute a prompt via the OrchX kernel and ProviderManager.
    """
    # 1. Fetch Kernel from app state
    kernel = getattr(fastapi_req.app.state, "kernel", None)
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel is not initialized")
        
    provider_manager = kernel.context.get_service("provider_manager")
    if not provider_manager:
        raise HTTPException(status_code=500, detail="ProviderManager service is not registered in kernel context")

    # Generate request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Sync provider adapters with provider_registry
    provider_manager._providers = []
    for provider in kernel.context.provider_registry.list_all():
        provider_manager.register_provider(provider)

    # 2. Build Selection Strategy (Explicit Selection Strategy)
    strategy = ExplicitSelectionStrategy(provider_id=request.provider, model_id=request.model)

    # 3. Construct Provider Request messages
    messages = [{"role": "user", "content": request.prompt}]
    
    # Required capability is "chat"
    required_capabilities = ["chat"]

    try:
        if request.stream:
            # We construct a streaming response using provider.stream if implemented
            selection = strategy.select_model(required_capabilities, provider_manager._providers)
            if not selection:
                raise ValueError("No online provider models satisfy explicit strategy selection.")
            provider, model = selection
            
            req = ProviderRequest(
                model_id=model.id,
                messages=messages
            )
            
            async def stream_generator():
                try:
                    async for chunk in provider.stream(req):
                        yield f"data: {chunk.model_dump_json()}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return StreamingResponse(stream_generator(), media_type="text/event-stream")
        
        # Non-streaming path
        response: ProviderResponse = await provider_manager.execute_request(
            required_capabilities=required_capabilities,
            messages=messages,
            strategy=strategy
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Log safe transaction metadata (never request body containing credentials)
        logger.info(
            f"Execution transaction complete - request_id={request_id} provider={request.provider or 'auto'} model={response.model_used} latency_ms={latency_ms:.2f} success=True"
        )
        
        # Determine actual provider and model from response
        actual_model = response.model_used
        actual_provider = request.provider or (response.model_used.split("/")[0] if "/" in response.model_used else "unknown")

        return ExecutionResponse(
            success=True,
            response=response.content or "",
            provider=actual_provider,
            model=actual_model,
            latency_ms=round(latency_ms, 2),
            request_id=request_id
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Execution transaction failed - request_id={request_id} latency_ms={latency_ms:.2f} success=False error={sanitize_error(str(e))}"
        )
        
        from orchx_core.exceptions import ProviderError
        
        error_code = "PROVIDER_REQUEST_FAILED"
        status_code = 500
        
        if isinstance(e, ProviderError):
            error_code = e.error_code
            status_code = 400 if error_code in ("NO_PROVIDER_CONFIGURED", "PROVIDER_NOT_CONFIGURED", "PROVIDER_AUTH_FAILED", "INVALID_PROVIDER_CONFIGURATION") else 500
        elif isinstance(e, ValueError):
            status_code = 400
            if "No AI providers are configured yet" in str(e):
                error_code = "NO_PROVIDER_CONFIGURED"
            elif "auth" in str(e).lower() or "permission" in str(e).lower():
                error_code = "PROVIDER_AUTH_FAILED"
        elif isinstance(e, TimeoutError):
            status_code = 504
            error_code = "PROVIDER_TIMEOUT"
        elif isinstance(e, ConnectionError):
            status_code = 502
            error_code = "PROVIDER_UNAVAILABLE"
            
        err_msg = SAFE_ERROR_MESSAGES.get(error_code, SAFE_ERROR_MESSAGES["PROVIDER_REQUEST_FAILED"])
            
        raise HTTPException(
            status_code=status_code,
            detail=f"[{error_code}] {err_msg}"
        )


@router.post("/providers/credentials")
async def store_credentials(
    request: CredentialBridgeRequest,
    manager: ProviderCredentialManager = Depends(get_cred_manager)
):
    """
    Store credential inside SecretVault via ProviderCredentialManager.
    """
    credentials = {"api_key": request.api_key}
    
    try:
        errors = manager.validate_and_store(request.provider, credentials)
        if errors:
            safe_errors = [sanitize_error(err) for err in errors]
            raise HTTPException(status_code=400, detail={"errors": safe_errors})
            
        return {
            "success": True,
            "provider": request.provider,
            "status": "stored"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to securely store provider credentials. Ensure master encryption key is configured."
        )
