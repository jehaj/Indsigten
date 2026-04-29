from indsigten.db.vector_store import VectorStore


class SearchEngine:
    def __init__(self, db_path, model_name="all-MiniLM-L6-v2", dim=384):
        self.db_path = db_path
        self.model_name = model_name
        self.dim = dim
        self._model = None
        self.store = VectorStore(db_path=db_path, dim=dim)

    @property
    def model(self):
        if self._model is None:
            from indsigten.embeddings.model import EmbeddingModel
            self._model = EmbeddingModel(model_name=self.model_name)
        return self._model

    def add_page(self, doc_id, page, text):
        embedding = self.model.get_embedding(text)
        self.store.add_item(doc_id, page, text, embedding)

    def is_file_indexed(self, file_path, file_hash):
        return self.store.is_file_indexed(file_path, file_hash)

    def mark_file_indexed(self, file_path, file_hash):
        self.store.mark_file_indexed(file_path, file_hash)

    def search(self, query, k=5):
        query_vector = self.model.get_embedding(query)
        return self.store.search(query_vector, k=k)

