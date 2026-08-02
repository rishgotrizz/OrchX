from typing import Dict, Any, List
from pydantic import BaseModel, Field

class PluginTemplate(BaseModel):
    template_id: str
    name: str
    scaffold_structure: Dict[str, str] = Field(default_factory=dict)
    default_manifest_config: Dict[str, Any] = Field(default_factory=dict)

class ManifestValidatorConfig(BaseModel):
    require_health_check: bool = True
    enforce_strict_versions: bool = True
    max_permissions_allowed: int = 10
