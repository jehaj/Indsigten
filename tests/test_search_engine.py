import unittest
from unittest.mock import MagicMock, patch
import numpy as np

class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_store = MagicMock()
        
    @patch('indsigten.embeddings.model.EmbeddingModel')
    @patch('indsigten.core.search_engine.VectorStore')
    def test_add_document(self, mock_vector_store, mock_embedding_model):
        from indsigten.core.search_engine import SearchEngine
        
        mock_embedding_model.return_value = self.mock_model
        mock_vector_store.return_value = self.mock_store
        
        engine = SearchEngine(db_path=":memory:")
        
        doc_id = "test.pdf"
        page = 1
        text = "Hello world"
        embedding = np.random.rand(384).astype('float32')
        self.mock_model.get_embedding.return_value = embedding

        
        engine.add_page(doc_id, page, text)
        
        self.mock_model.get_embedding.assert_called_once_with(text)
        self.mock_store.add_item.assert_called_once_with(doc_id, page, text, embedding)

    @patch('indsigten.embeddings.model.EmbeddingModel')
    @patch('indsigten.core.search_engine.VectorStore')
    def test_search(self, mock_vector_store, mock_embedding_model):
        from indsigten.core.search_engine import SearchEngine
        
        mock_embedding_model.return_value = self.mock_model
        mock_vector_store.return_value = self.mock_store
        
        engine = SearchEngine(db_path=":memory:")
        
        query = "find something"
        query_vector = np.random.rand(384).astype('float32')
        self.mock_model.get_embedding.return_value = query_vector

        self.mock_store.search.return_value = [{"doc_id": "test.pdf", "page": 1, "text": "result", "score": 0.9}]
        
        results = engine.search(query)
        
        self.assertEqual(len(results), 1)
        self.mock_model.get_embedding.assert_called_once_with(query)
        self.mock_store.search.assert_called_once_with(query_vector, k=5)

if __name__ == '__main__':
    unittest.main()
