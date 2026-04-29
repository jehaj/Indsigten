import os
import sqlite3

import hnswlib


class VectorStore:
    def __init__(self, db_path, dim=384, max_elements=10000):
        self.db_path = db_path
        self.index_path = db_path + ".hnsw"
        self.dim = dim
        self.max_elements = max_elements

        # Initialize SQLite
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

        # Initialize HNSW index
        self.index = hnswlib.Index(space="cosine", dim=self.dim)
        if os.path.exists(self.index_path):
            self.index.load_index(self.index_path, max_elements=self.max_elements)
        else:
            self.index.init_index(
                max_elements=self.max_elements, ef_construction=200, M=16
            )

    def _save_index(self):
        self.index.save_index(self.index_path)

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT,
                page INTEGER,
                text TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT,
                last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def is_file_indexed(self, file_path, file_hash):
        cursor = self.conn.execute(
            "SELECT 1 FROM processed_files WHERE file_path = ? AND file_hash = ?",
            (file_path, file_hash),
        )
        return cursor.fetchone() is not None

    def mark_file_indexed(self, file_path, file_hash):
        self.conn.execute(
            "INSERT OR REPLACE INTO processed_files (file_path, file_hash) VALUES (?, ?)",
            (file_path, file_hash),
        )
        self.conn.commit()

    def add_item(self, doc_id, page, text, embedding):
        # 1. Store metadata in SQLite
        cursor = self.conn.execute(
            "INSERT INTO embeddings (doc_id, page, text) VALUES (?, ?, ?)",
            (doc_id, page, text),
        )
        label = cursor.lastrowid
        self.conn.commit()

        # 2. Add vector to HNSW
        self.index.add_items(embedding, label)
        self._save_index()

    def search(self, query_vector, k=5):
        labels, distances = self.index.knn_query(query_vector, k=k)

        results = []
        for label, distance in zip(labels[0], distances[0]):
            cursor = self.conn.execute(
                "SELECT doc_id, page, text FROM embeddings WHERE id = ?", (int(label),)
            )
            row = cursor.fetchone()
            if row:
                results.append(
                    {
                        "doc_id": row[0],
                        "page": row[1],
                        "text": row[2],
                        "score": 1.0
                        - float(distance),  # Convert cosine distance to similarity
                    }
                )
        return results
