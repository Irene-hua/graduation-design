"""Ollama client for local LLM inference."""
from typing import Optional, Dict, Any
import ollama


class OllamaClient:
    """Client for Ollama local LLM."""
    
    def __init__(
        self,
        model_name: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Initialize Ollama client.
        
        Args:
            model_name: Name of the Ollama model
            base_url: Base URL for Ollama server
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Configure Ollama client
        ollama._client._base_url = base_url
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            temperature: Override temperature
            max_tokens: Override max tokens
            
        Returns:
            Generated text
        """
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                'temperature': temperature or self.temperature,
                'num_predict': max_tokens or self.max_tokens
            }
        )
        
        return response['response']
    
    def chat(
        self,
        messages: list,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chat with the model using message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override temperature
            max_tokens: Override max tokens
            
        Returns:
            Generated response
        """
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
            options={
                'temperature': temperature or self.temperature,
                'num_predict': max_tokens or self.max_tokens
            }
        )
        
        return response['message']['content']
    
    def list_models(self) -> list:
        """List available models."""
        try:
            models = ollama.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """
        Pull/download a model.
        
        Args:
            model_name: Name of model to pull. If None, uses self.model_name
            
        Returns:
            True if successful
        """
        model = model_name or self.model_name
        
        try:
            ollama.pull(model)
            return True
        except Exception as e:
            print(f"Error pulling model {model}: {e}")
            return False
    
    def check_model_available(self) -> bool:
        """Check if the configured model is available."""
        available_models = self.list_models()
        return self.model_name in available_models
