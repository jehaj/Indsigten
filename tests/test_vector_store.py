import unittest
from unittest.mock import MagicMock, patch
import numpy as np

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        # We will mock the database connection and the HNSW index
        self.mock_db_conn = MagicMock()
        self.mock_index = MagicMock()
        
    @patch('indsigten.db.vector_store.hnswlib.Index')
    @patch('indsigten.db.vector_store.sqlite3.connect')
    def test_add_embedding(self, mock_connect, mock_hnsw_index):
        from indsigten.db.vector_store import VectorStore
        
        # Setup mocks
        mock_connect.return_value = self.mock_db_conn
        mock_hnsw_index.return_value = self.mock_index
        
        store = VectorStore(db_path=":memory:", dim=384)

        # Test adding an embedding
        doc_id = "test_doc.pdf"
        page = 1
        text = "Some text content"
        embedding = np.random.rand(384).astype('float32')

        
        store.add_item(doc_id, page, text, embedding)
        
        # Verify DB insert
        self.mock_db_conn.execute.assert_called()
        # Verify HNSW index update
        self.mock_index.add_items.assert_called_once()
        
    @patch('indsigten.db.vector_store.hnswlib.Index')
    @patch('indsigten.db.vector_store.sqlite3.connect')
    def test_search(self, mock_connect, mock_hnsw_index):
        from indsigten.db.vector_store import VectorStore
        
        # Setup mocks
        mock_connect.return_value = self.mock_db_conn
        mock_hnsw_index.return_value = self.mock_index
        
        # Mock index search result (labels, distances)
        self.mock_index.knn_query.return_value = (np.array([[1]]), np.array([[0.1]]))
        # Mock DB lookup for the label
        self.mock_db_conn.execute.return_value.fetchone.return_value = ("test_doc.pdf", 1, "Some text content")
        
        store = VectorStore(db_path=":memory:", dim=384)
        query_vector = np.random.rand(384).astype('float32')

        
        results = store.search(query_vector, k=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['doc_id'], "test_doc.pdf")
        self.assertEqual(results[0]['page'], 1)
        self.mock_index.knn_query.assert_called_once()

if __name__ == '__main__':
    unittest.main()
