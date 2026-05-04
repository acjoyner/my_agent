import os
from openai import OpenAI
from dotenv import load_dotenv
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

load_dotenv()

class UnifiedClient:
    """A wrapper to provide a consistent interface using local free models."""
    def __init__(self):
        # Default to local Ollama
        self.openai_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        self.mode = "ollama"

    @property
    def messages(self):
        return self 
        
    def create(self, model, messages, tools=None, max_tokens=1000, **kwargs):
        # Always use local gemma4 regardless of the requested model name
        openai_messages = []
        for m in messages:
            openai_messages.append({"role": m["role"], "content": m["content"]})
        
        response = self.openai_client.chat.completions.create(
            model="gemma4", 
            messages=openai_messages,
            max_tokens=max_tokens
        )
        
        class MockResponse:
            def __init__(self, content):
                self.content = [type('obj', (object,), {'text': content})]
        
        return MockResponse(response.choices[0].message.content)

client = UnifiedClient()
