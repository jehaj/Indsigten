from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name="google/gemma-7b"):
        # Note: EmbeddingGemma specifically might need a different identifier 
        # but for this implementation we use sentence-transformers interface
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text):
        embedding = self.model.encode(text)
        return embedding.astype('float32')
