from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ProviderMetadata(BaseModel):
    provider_id: str
    display_name: str
    required_credentials: List[str]
    optional_credentials: List[str] = Field(default_factory=list)
    supported_capabilities: List[str] = Field(default_factory=list)
    authentication_method: str = "Bearer"
    base_url: str = ""
    chat_endpoint: str = ""
    model_discovery_endpoint: Optional[str] = None
    embeddings_endpoint: Optional[str] = None
    vision_endpoint: Optional[str] = None
    discovery_strategy: str = "static-fallback"
    default_models: List[str] = Field(default_factory=list)
    health_check_strategy: str = "models_list"
    
    # Scope and Deployment Flags
    enabled: bool = True
    production_enabled: bool = True
    verification_enabled: bool = True
    authentication_required: bool = True
    local_provider: bool = False
    requires_network: bool = True

    def validate_credentials(self, credentials: Dict[str, str]) -> List[str]:
        errors = []
        for req in self.required_credentials:
            if req not in credentials or not credentials[req].strip():
                errors.append(f"Missing required credential: {req}")
        return errors

class ProviderMetadataRegistry:
    def __init__(self):
        self._providers: Dict[str, ProviderMetadata] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(ProviderMetadata(
            provider_id="openai",
            display_name="OpenAI",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "vision", "tool_calling", "embeddings", "reasoning"],
            base_url="https://api.openai.com",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["gpt-4o", "gpt-3.5-turbo"]
        ))
        self.register(ProviderMetadata(
            provider_id="anthropic",
            display_name="Anthropic (Claude)",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "vision", "tool_calling", "reasoning"],
            base_url="https://api.anthropic.com",
            chat_endpoint="/v1/messages",
            authentication_method="x-api-key",
            discovery_strategy="static-fallback",
            default_models=["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"]
        ))
        self.register(ProviderMetadata(
            provider_id="gemini",
            display_name="Google Gemini",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "vision", "tool_calling", "reasoning"],
            base_url="https://generativelanguage.googleapis.com",
            chat_endpoint="/v1beta/models",
            discovery_strategy="static-fallback",
            default_models=["gemini-1.5-pro", "gemini-1.5-flash"]
        ))
        self.register(ProviderMetadata(
            provider_id="groq",
            display_name="Groq",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "tool_calling"],
            base_url="https://api.groq.com/openai",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
        ))
        self.register(ProviderMetadata(
            provider_id="openrouter",
            display_name="OpenRouter",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "vision", "tool_calling"],
            base_url="https://openrouter.ai/api",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["anthropic/claude-3-opus", "meta-llama/llama-3-70b-instruct"]
        ))
        self.register(ProviderMetadata(
            provider_id="ollama",
            display_name="Ollama",
            required_credentials=[],
            optional_credentials=["api_key"],
            base_url="http://localhost:11434",
            chat_endpoint="/api/chat",
            model_discovery_endpoint="/api/tags",
            discovery_strategy="ollama-tags",
            supported_capabilities=["chat", "tool_calling"],
            default_models=["llama3", "mistral"],
            production_enabled=False,
            local_provider=True,
            authentication_required=False
        ))
        self.register(ProviderMetadata(
            provider_id="nvidia",
            display_name="NVIDIA NIM",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "vision"],
            base_url="https://integrate.api.nvidia.com",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["meta/llama3-70b"]
        ))
        self.register(ProviderMetadata(
            provider_id="kimi",
            display_name="Kimi",
            required_credentials=["api_key"],
            supported_capabilities=["chat"],
            base_url="https://api.moonshot.cn",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["moonshot-v1-32k"]
        ))
        self.register(ProviderMetadata(
            provider_id="huggingface",
            display_name="Hugging Face",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "embeddings"],
            base_url="https://api-inference.huggingface.co",
            chat_endpoint="/v1/chat/completions",
            discovery_strategy="static-fallback",
            default_models=["meta-llama/Meta-Llama-3-70B-Instruct"]
        ))
        self.register(ProviderMetadata(
            provider_id="mistral",
            display_name="Mistral AI",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "tool_calling", "embeddings"],
            base_url="https://api.mistral.ai",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["mistral-large-latest", "mistral-small-latest"]
        ))
        self.register(ProviderMetadata(
            provider_id="cohere",
            display_name="Cohere",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "embeddings", "tool_calling"],
            base_url="https://api.cohere.ai",
            chat_endpoint="/v1/chat",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["command-r-plus", "command-r"]
        ))
        self.register(ProviderMetadata(
            provider_id="opencode",
            display_name="OpenCode",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "tool_calling"],
            base_url="https://api.opencode.ai",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["opencode-v1"]
        ))
        self.register(ProviderMetadata(
            provider_id="github",
            display_name="GitHub Models",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "embeddings", "reasoning"],
            base_url="https://models.inference.ai.azure.com",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["gpt-5", "gpt-5-nano", "phi-4-mini-instruct", "text-embedding-3-large"]
        ))
        self.register(ProviderMetadata(
            provider_id="deepseek",
            display_name="DeepSeek",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "reasoning"],
            base_url="https://api.deepseek.com",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["deepseek-coder", "deepseek-chat"]
        ))
        self.register(ProviderMetadata(
            provider_id="siliconflow",
            display_name="SiliconFlow",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "reasoning"],
            base_url="https://api.siliconflow.cn",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["siliconflow-base"]
        ))
        self.register(ProviderMetadata(
            provider_id="cerebras",
            display_name="Cerebras",
            required_credentials=["api_key"],
            supported_capabilities=["chat"],
            base_url="https://api.cerebras.ai",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["llama3-70b-cerebras"]
        ))
        self.register(ProviderMetadata(
            provider_id="sambanova",
            display_name="SambaNova",
            required_credentials=["api_key"],
            supported_capabilities=["chat"],
            base_url="https://api.sambanova.ai",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["sambanova-llama3"]
        ))
        self.register(ProviderMetadata(
            provider_id="cloudflare",
            display_name="Cloudflare AI",
            required_credentials=["api_key"],
            supported_capabilities=["chat"],
            base_url="https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/ai/run",
            chat_endpoint="/@cf/meta/llama-3-8b-instruct",
            discovery_strategy="static-fallback",
            default_models=["@cf/meta/llama-3-8b-instruct"]
        ))
        self.register(ProviderMetadata(
            provider_id="lightning",
            display_name="Lightning AI",
            required_credentials=["api_key"],
            supported_capabilities=["chat"],
            base_url="https://api.lightning.ai",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["lightning-base"]
        ))
        self.register(ProviderMetadata(
            provider_id="stitch",
            display_name="Stitch",
            required_credentials=["api_key"],
            supported_capabilities=["chat", "embeddings"],
            base_url="https://api.stitch.ai",
            chat_endpoint="/v1/chat/completions",
            model_discovery_endpoint="/v1/models",
            discovery_strategy="openai-v1",
            default_models=["stitch-v1"]
        ))

    def register(self, metadata: ProviderMetadata):
        self._providers[metadata.provider_id] = metadata

    def get(self, provider_id: str) -> Optional[ProviderMetadata]:
        return self._providers.get(provider_id)

    def list_all(self) -> List[ProviderMetadata]:
        return list(self._providers.values())
