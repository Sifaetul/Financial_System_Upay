from abc import ABC, abstractmethod
from typing import List
import os

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            
    def get_embedding(self, text: str) -> List[float]:
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        response = self.client.embeddings.create(input=[text], model=self.model)
        # Assuming we keep 384 dims for local DB compatibility, we'd truncate/pad.
        # But actually if OpenAI is used, it returns 1536. 
        # For this setup, we enforce 384.
        emb = response.data[0].embedding
        return emb[:384]

class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text).tolist()
        return embedding[:384] # all-MiniLM-L6-v2 is exactly 384

def get_embedding_provider() -> EmbeddingProvider:
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIEmbeddingProvider()
    return LocalEmbeddingProvider()
