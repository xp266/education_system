"""
向量文本检索核心模块
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MODEL_LOCAL_PATH = os.path.abspath(os.path.join(BASE_DIR, "models/bge-small-zh-v1.5"))


class Embedder:
    def __init__(self, model_name: str = None):
        self.model = None
        self.model_name = MODEL_LOCAL_PATH

    
    def load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(
                self.model_name,
                local_files_only=True,
            )
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        if self.model is None:
            self.load_model()
        
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(text, normalize_embeddings=True)
        return embeddings
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        return float(np.dot(embedding1, embedding2))
    
    def search_similar(self, query_text: str, chunks: List[dict], top_k: int = 5) -> List[dict]:
        if self.model is None:
            self.load_model()
        
        query_embedding = self.encode(query_text)[0]
        chunk_texts = [chunk["content"] for chunk in chunks]
        chunk_embeddings = self.encode(chunk_texts)
        
        similarities = []
        for i, chunk_embedding in enumerate(chunk_embeddings):
            sim = self.similarity(query_embedding, chunk_embedding)
            similarities.append({
                "chunk": chunks[i],
                "similarity": sim
            })
        
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
