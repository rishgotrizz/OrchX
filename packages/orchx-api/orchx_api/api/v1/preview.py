from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()

class ArtifactPreviewRequest(BaseModel):
    artifact_id: str
    artifact_type: str

class ArtifactPreviewResponse(BaseModel):
    artifact_id: str
    artifact_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]

@router.post("/render", response_model=ArtifactPreviewResponse, summary="Render Artifact for Preview Studio")
async def render_artifact(request: ArtifactPreviewRequest):
    """
    Universal Visualization Layer Endpoint.
    Takes an artifact ID and type, returning the rendered standard JSON format
    for the Preview Studio frontend.
    """
    # This is a stub implementation that would ideally fetch from StorageManager
    # and format the response based on the artifact_type (markdown, React, pdf, etc.)
    
    supported_types = [
        "react", "website", "dashboard", "document", "markdown", 
        "pdf", "image", "ui_component", "workflow", "architecture",
        "api_doc", "json", "yaml", "diff", "log", "build_artifact"
    ]
    
    if request.artifact_type not in supported_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported artifact type. Supported types: {supported_types}"
        )
        
    # Mocked response for now
    return ArtifactPreviewResponse(
        artifact_id=request.artifact_id,
        artifact_type=request.artifact_type,
        content={
            "raw": f"Preview content for {request.artifact_id}",
            "rendered": True
        },
        metadata={
            "version": "1.0",
            "source": "PreviewStudio"
        }
    )

@router.get("/history/{artifact_id}", response_model=List[ArtifactPreviewResponse], summary="Get Artifact History")
async def get_artifact_history(artifact_id: str):
    """Retrieve history of an artifact for diff/version previews."""
    return []
