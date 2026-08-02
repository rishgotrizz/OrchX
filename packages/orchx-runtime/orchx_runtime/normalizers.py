import json
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from orchx_core.interfaces.provider_contracts import ProviderResponse, Model, UsageMetrics

class ResponseNormalizer(ABC):
    @abstractmethod
    def normalize(self, raw: Dict[str, Any], model: Model) -> ProviderResponse:
        pass

    @abstractmethod
    def parse_stream_chunk(self, chunk: bytes, model: Model) -> Optional[ProviderResponse]:
        pass

class OpenAINormalizer(ResponseNormalizer):
    def normalize(self, raw: Dict[str, Any], model: Model) -> ProviderResponse:
        usage = raw.get("usage", {})
        return ProviderResponse(
            id=raw.get("id", str(uuid.uuid4())),
            content=raw.get("choices", [{}])[0].get("message", {}).get("content", ""),
            role="assistant",
            usage=UsageMetrics(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            model_used=model.id,
            finish_reason="stop"
        )
        
    def parse_stream_chunk(self, chunk: bytes, model: Model) -> Optional[ProviderResponse]:
        line = chunk.decode("utf-8").strip()
        if not line or line.startswith(":"):
            return None
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                return None
            try:
                raw = json.loads(data)
                delta = raw.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content", "")
                
                # Some implementations send usage in the last chunk
                usage = raw.get("usage", {})
                u_metrics = UsageMetrics()
                if usage:
                    u_metrics.prompt_tokens = usage.get("prompt_tokens", 0)
                    u_metrics.completion_tokens = usage.get("completion_tokens", 0)
                    u_metrics.total_tokens = usage.get("total_tokens", 0)

                return ProviderResponse(
                    id=raw.get("id", str(uuid.uuid4())),
                    content=content,
                    role="assistant",
                    usage=u_metrics,
                    model_used=model.id,
                    finish_reason=raw.get("choices", [{}])[0].get("finish_reason", "") or ""
                )
            except json.JSONDecodeError:
                return None
        return None

class AnthropicNormalizer(ResponseNormalizer):
    def normalize(self, raw: Dict[str, Any], model: Model) -> ProviderResponse:
        usage = raw.get("usage", {})
        content_blocks = raw.get("content", [])
        content = "".join([b.get("text", "") for b in content_blocks if b.get("type") == "text"])
        return ProviderResponse(
            id=raw.get("id", str(uuid.uuid4())),
            content=content,
            role="assistant",
            usage=UsageMetrics(
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            ),
            model_used=model.id,
            finish_reason=raw.get("stop_reason", "stop") or "stop"
        )

    def parse_stream_chunk(self, chunk: bytes, model: Model) -> Optional[ProviderResponse]:
        # Implementation for Anthropic SSE
        line = chunk.decode("utf-8").strip()
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                type_ = data.get("type")
                if type_ == "content_block_delta":
                    return ProviderResponse(
                        id=str(uuid.uuid4()),
                        content=data.get("delta", {}).get("text", ""),
                        role="assistant",
                        usage=UsageMetrics(),
                        model_used=model.id,
                        finish_reason=""
                    )
                elif type_ == "message_stop":
                    return ProviderResponse(
                        id=str(uuid.uuid4()),
                        content="",
                        role="assistant",
                        usage=UsageMetrics(), # Can accumulate from message_start/message_delta
                        model_used=model.id,
                        finish_reason="stop"
                    )
            except json.JSONDecodeError:
                pass
        return None

class GeminiNormalizer(ResponseNormalizer):
    def normalize(self, raw: Dict[str, Any], model: Model) -> ProviderResponse:
        candidates = raw.get("candidates", [])
        content = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            content = "".join([p.get("text", "") for p in parts])
            
        usage = raw.get("usageMetadata", {})
        return ProviderResponse(
            id=str(uuid.uuid4()),
            content=content,
            role="assistant",
            usage=UsageMetrics(
                prompt_tokens=usage.get("promptTokenCount", 0),
                completion_tokens=usage.get("candidatesTokenCount", 0),
                total_tokens=usage.get("totalTokenCount", 0),
            ),
            model_used=model.id,
            finish_reason="stop"
        )

    def parse_stream_chunk(self, chunk: bytes, model: Model) -> Optional[ProviderResponse]:
        try:
            # Gemini stream returns a JSON array or sequence of JSON objects
            data = json.loads(chunk.decode("utf-8").strip().lstrip(',').lstrip('[').rstrip(']'))
            return self.normalize(data, model)
        except:
            return None

class OllamaNormalizer(ResponseNormalizer):
    def normalize(self, raw: Dict[str, Any], model: Model) -> ProviderResponse:
        return ProviderResponse(
            id=str(uuid.uuid4()),
            content=raw.get("message", {}).get("content", ""),
            role="assistant",
            usage=UsageMetrics(
                prompt_tokens=raw.get("prompt_eval_count", 0),
                completion_tokens=raw.get("eval_count", 0),
                total_tokens=raw.get("prompt_eval_count", 0) + raw.get("eval_count", 0),
            ),
            model_used=model.id,
            finish_reason="stop" if raw.get("done") else ""
        )

    def parse_stream_chunk(self, chunk: bytes, model: Model) -> Optional[ProviderResponse]:
        try:
            data = json.loads(chunk.decode("utf-8").strip())
            return self.normalize(data, model)
        except:
            return None

class ResponseNormalizerFactory:
    @staticmethod
    def get_normalizer(strategy: str) -> ResponseNormalizer:
        if strategy == "openai-v1":
            return OpenAINormalizer()
        if strategy == "anthropic-messages":
            return AnthropicNormalizer()
        if strategy == "gemini-contents":
            return GeminiNormalizer()
        if strategy == "ollama-tags":
            return OllamaNormalizer()
        return OpenAINormalizer()
