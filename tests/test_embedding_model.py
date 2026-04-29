import unittest
from unittest.mock import MagicMock, patch
import numpy as np

class TestEmbeddingModel(unittest.TestCase):
    @patch('indsigten.embeddings.model.SentenceTransformer')
    def test_generate_embedding(self, mock_transformer):
        from indsigten.embeddings.model import EmbeddingModel
        
        # Setup mock
        mock_model_instance = MagicMock()
        mock_transformer.return_value = mock_model_instance
        
        # Mock the encode method to return a dummy embedding
        dummy_embedding = np.random.rand(384).astype('float32')

        mock_model_instance.encode.return_value = dummy_embedding
        
        model = EmbeddingModel(model_name="test-model")
        text = "This is a test sentence."
        
        embedding = model.get_embedding(text)
        
        # Verify
        mock_model_instance.encode.assert_called_once_with(text)
        np.testing.assert_array_equal(embedding, dummy_embedding)
        self.assertEqual(embedding.dtype, 'float32')

if __name__ == '__main__':
    unittest.main()
