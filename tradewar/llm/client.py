"""LLM client abstraction for interfacing with language model providers."""

import logging
from typing import Dict, List, Optional, Union

from tradewar.config import config

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available. OpenAI LLM provider will not work.")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic package not available. Anthropic LLM provider will not work.")

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("LiteLLM package not available. LiteLLM provider will not work.")


class LLMClient:
    """
    Client for interacting with large language models.
    
    This class provides a unified interface for different LLM providers
    (like OpenAI, Anthropic, LiteLLM, etc.) to generate text completions for
    trade policy simulations.
    """
    
    def __init__(
        self, 
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize the LLM client.
        
        Args:
            provider: LLM provider (openai, anthropic, litellm)
            api_key: API key for the provider
            model: Model to use for generation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.provider = provider or config.llm.provider
        self.api_key = api_key or config.llm.api_key
        self.model = model or config.llm.model
        self.temperature = temperature or config.llm.temperature
        self.max_tokens = max_tokens or config.llm.max_tokens
        
        # Initialize the appropriate client
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Set up the client for the specified provider."""
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not installed. Run 'pip install openai'")
            
            openai.api_key = self.api_key
            self.client = openai
        
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic package not installed. Run 'pip install anthropic'")
            
            self.client = anthropic.Anthropic(api_key=self.api_key)
        
        elif self.provider == "litellm":
            if not LITELLM_AVAILABLE:
                raise ImportError("LiteLLM package not installed. Run 'pip install litellm'")
            
            litellm.api_key = self.api_key
            self.client = litellm
        
        elif self.provider == "test_provider":
            # Mock client for testing
            self.client = object()
            
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_response(
        self, 
        prompt: str,
        system_message: Optional[str] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the language model.
        
        Args:
            prompt: The prompt to send to the LLM
            system_message: Optional system message for models that support it
            stop_sequences: Optional sequences that stop generation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == "openai":
                return self._generate_openai(prompt, system_message, stop_sequences, **kwargs)
            elif self.provider == "anthropic":
                return self._generate_anthropic(prompt, system_message, stop_sequences, **kwargs)
            elif self.provider == "litellm":
                return self._generate_litellm(prompt, system_message, stop_sequences, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return "ERROR: Unable to generate response from LLM."
    
    def _generate_openai(
        self, 
        prompt: str,
        system_message: Optional[str],
        stop_sequences: Optional[List[str]],
        **kwargs
    ) -> str:
        """Generate a response using OpenAI's API."""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stop=stop_sequences,
        )
        
        return response.choices[0].message.content
    
    def _generate_anthropic(
        self, 
        prompt: str,
        system_message: Optional[str],
        stop_sequences: Optional[List[str]],
        **kwargs
    ) -> str:
        """Generate a response using Anthropic's API."""
        system = system_message or ""
        
        response = self.client.completions.create(
            model=self.model,
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
            system=system,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens_to_sample=kwargs.get("max_tokens", self.max_tokens),
            stop_sequences=stop_sequences or ["Human:"],
        )
        
        return response.completion
    
    def _generate_litellm(
        self, 
        prompt: str,
        system_message: Optional[str],
        stop_sequences: Optional[List[str]],
        **kwargs
    ) -> str:
        """Generate a response using LiteLLM's unified API."""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.completion(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stop=stop_sequences,
            api_key=self.api_key
        )
        
        return response.choices[0].message.content
