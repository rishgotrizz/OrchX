from abc import abstractmethod
from typing import Any, Optional
from orchx_core.interfaces.plugin import BasePlugin


class BaseProvider(BasePlugin):
    """
    Plugin contract for text generation and LLM providers.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """
        Query the underlying language model to generate text.
        """
        pass
