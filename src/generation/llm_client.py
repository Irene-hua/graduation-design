"""
LLM Client for generating responses using Ollama
LLM客户端，使用Ollama生成响应
"""

import requests
from typing import List, Dict, Optional
import json


class LLMClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "llama2:7b",
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9
    ):
        """
        Initialize the LLM client
        
        Args:
            base_url: Base URL of Ollama API
            model_name: Name of the model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
    
    def generate(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        stream: bool = False
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User prompt/question
            context: Optional context chunks to provide
            stream: Whether to stream the response
        
        Returns:
            str: Generated response
        """
        # Build the full prompt with context
        full_prompt = self._build_prompt_with_context(prompt, context)
        
        # Prepare request
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
                "top_p": self.top_p
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=120)
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        json_response = json.loads(line)
                        if 'response' in json_response:
                            full_response += json_response['response']
                        if json_response.get('done', False):
                            break
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                return result.get('response', '')
        
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
    
    def _build_prompt_with_context(
        self,
        question: str,
        context: Optional[List[str]] = None
    ) -> str:
        """
        Build prompt with context for RAG
        
        Args:
            question: User question
            context: List of context chunks
        
        Returns:
            str: Formatted prompt
        """
        if not context:
            return question
        
        # Format context
        context_text = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(context)])
        
        # Build RAG prompt
        prompt = f"""Based on the following context, please answer the question.

Context:
{context_text}

Question: {question}

Answer (based on the context provided):"""
        
        return prompt
    
    def check_connection(self) -> bool:
        """
        Check if Ollama server is accessible
        
        Returns:
            bool: True if server is accessible, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> List[str]:
        """
        List available models
        
        Returns:
            list: List of model names
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException:
            return []
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """
        Chat with LLM using message history
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response
        
        Returns:
            str: Generated response
        """
        url = f"{self.base_url}/api/chat"
        data = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
                "top_p": self.top_p
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=120)
            response.raise_for_status()
            
            if stream:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        json_response = json.loads(line)
                        if 'message' in json_response and 'content' in json_response['message']:
                            full_response += json_response['message']['content']
                        if json_response.get('done', False):
                            break
                return full_response
            else:
                result = response.json()
                return result.get('message', {}).get('content', '')
        
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
