import sqlite3
import numpy as np
import faiss
import openai
from typing import List, Tuple

class EmbeddingProcessor:
    def __init__(self, db_name: str = 'local_browsing_history.db'):
        """
        Initialize the EmbeddingProcessor with database configuration.
        
        Args:
            db_name (str): Name of the SQLite database file
        """
        self.db_name = db_name
        self.model_name = "text-embedding-ada-002"

    def read_metadata_from_db(self) -> List[Tuple]:
        """
        Read metadata from SQLite database.
        
        Returns:
            List[Tuple]: List of (id, title, description) tuples
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description FROM browsing_history")
            return cursor.fetchall()

    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for given texts using OpenAI's API.
        
        Args:
            texts (List[str]): List of texts to encode
            
        Returns:
            List[List[float]]: List of embeddings
        """
        response = openai.embeddings.create(
            input=texts,
            model=self.model_name
        )
        return [item.embedding for item in response.data]

    def process_and_store_embeddings(self, batch_size: int = 10) -> None:
        """
        Process texts and store their embeddings in a FAISS index.
        
        Args:
            batch_size (int): Number of texts to process in each batch
        """
        # Read metadata and prepare texts
        metadata = self.read_metadata_from_db()
        texts = [f"{title} {description}" for _, title, description in metadata]

        # Initialize FAISS index with first batch
        first_batch_embedding = np.array(self.encode_texts(texts[:1]))
        embedding_dim = first_batch_embedding.shape[1]
        index = faiss.IndexFlatL2(embedding_dim)

        # Process remaining texts in batches
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            embeddings = self.encode_texts(batch_texts)
            index.add(np.array(embeddings).astype(np.float32))
            
            print(f"Processed batch {i // batch_size + 1} of {total_batches}")

        # Save index to disk
        faiss.write_index(index, 'faiss_index.bin')
        print("FAISS index saved successfully.")

def main():
    processor = EmbeddingProcessor()
    processor.process_and_store_embeddings()

if __name__ == "__main__":
    main()
