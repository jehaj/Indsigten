from indsigten.embeddings.model import EmbeddingModel
from indsigten.db.vector_store import VectorStore

class SearchEngine:
    def __init__(self, db_path, model_name="all-MiniLM-L6-v2", dim=384):
        self.model = EmbeddingModel(model_name=model_name)
        self.store = VectorStore(db_path=db_path, dim=dim)
        
    def add_page(self, doc_id, page, text):
        embedding = self.model.get_embedding(text)
        self.store.add_item(doc_id, page, text, embedding)
        
    def search(self, query, k=5):
        query_vector = self.model.get_embedding(query)
        return self.store.search(query_vector, k=k)
