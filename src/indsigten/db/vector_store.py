import sqlite3
import hnswlib
import numpy as np
import os

class VectorStore:
    def __init__(self, db_path, dim=384, max_elements=10000):
        self.db_path = db_path
        self.dim = dim
        self.max_elements = max_elements
        
        # Initialize SQLite
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        
        # Initialize HNSW index
        self.index = hnswlib.Index(space='cosine', dim=self.dim)
        # In a real app, we would load the index from disk if it exists
        self.index.init_index(max_elements=self.max_elements, ef_construction=200, M=16)
        
    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT,
                page INTEGER,
                text TEXT
            )
        """)
        self.conn.commit()
        
    def add_item(self, doc_id, page, text, embedding):
        # 1. Store metadata in SQLite
        cursor = self.conn.execute(
            "INSERT INTO embeddings (doc_id, page, text) VALUES (?, ?, ?)",
            (doc_id, page, text)
        )
        label = cursor.lastrowid
        self.conn.commit()
        
        # 2. Add vector to HNSW
        self.index.add_items(embedding, label)
        
    def search(self, query_vector, k=5):
        labels, distances = self.index.knn_query(query_vector, k=k)
        
        results = []
        for label, distance in zip(labels[0], distances[0]):
            cursor = self.conn.execute(
                "SELECT doc_id, page, text FROM embeddings WHERE id = ?",
                (int(label),)
            )
            row = cursor.fetchone()
            if row:
                results.append({
                    'doc_id': row[0],
                    'page': row[1],
                    'text': row[2],
                    'score': 1.0 - float(distance) # Convert cosine distance to similarity
                })
        return results
