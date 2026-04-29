from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Note: EmbeddingGemma specifically might need a different identifier
        # but for this implementation we use sentence-transformers interface
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text):
        embedding = self.model.encode(text)
        return embedding.astype("float32")
