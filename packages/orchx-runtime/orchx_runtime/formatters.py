import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from orchx_core.interfaces.provider_contracts import ProviderRequest, Model

class RequestFormatter(ABC):
    @abstractmethod
    def format(self, request: ProviderRequest, model: Model) -> Dict[str, Any]:
        pass

class OpenAIFormatter(RequestFormatter):
    def format(self, request: ProviderRequest, model: Model) -> Dict[str, Any]:
        payload = {
            "model": request.model_id,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True
        }
        return payload

class AnthropicFormatter(RequestFormatter):
    def format(self, request: ProviderRequest, model: Model) -> Dict[str, Any]:
        system_msg = next((m["content"] for m in request.messages if m["role"] == "system"), None)
        filtered_messages = [m for m in request.messages if m["role"] != "system"]
        
        payload = {
            "model": request.model_id,
            "messages": filtered_messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True
        }
        if system_msg:
            payload["system"] = system_msg
        return payload

class GeminiFormatter(RequestFormatter):
    def format(self, request: ProviderRequest, model: Model) -> Dict[str, Any]:
        contents = []
        for m in request.messages:
            role = "user" if m["role"] in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
            
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens
            }
        }
        return payload

class OllamaFormatter(RequestFormatter):
    def format(self, request: ProviderRequest, model: Model) -> Dict[str, Any]:
        payload = {
            "model": request.model_id,
            "messages": request.messages,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            },
            "stream": True
        }
        return payload

class RequestFormatterFactory:
    @staticmethod
    def get_formatter(strategy: str) -> RequestFormatter:
        if strategy == "openai-v1":
            return OpenAIFormatter()
        if strategy == "anthropic-messages":
            return AnthropicFormatter()
        if strategy == "gemini-contents":
            return GeminiFormatter()
        if strategy == "ollama-tags":
            return OllamaFormatter()
        return OpenAIFormatter() # default fallback
