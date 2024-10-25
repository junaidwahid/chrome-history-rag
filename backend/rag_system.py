import faiss
import openai
import sqlite3
import numpy as np
from typing import List, Tuple, Optional, Union

import os
import json
from pathlib import Path
from typing import Dict

class ConfigLoader:
    """Handles loading and validation of configuration settings."""
    
    DEFAULT_CONFIG_PATH = "config.json"
    
    @staticmethod
    def load_config(config_path: Optional[str] = None) -> Dict:
        """
        Load configuration from JSON file.
        
        Args:
            config_path (Optional[str]): Path to config file
            
        Returns:
            Dict: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            KeyError: If required keys are missing
        """
        config_path = config_path or ConfigLoader.DEFAULT_CONFIG_PATH
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found at {config_file}. "
                "Please create one with your OpenAI API key."
            )
            
        with open(config_file) as f:
            config = json.load(f)
            
        if 'openai_api_key' not in config:
            raise KeyError(
                "OpenAI API key not found in config file. "
                "Please add 'openai_api_key' to your config."
            )
            
        return config


def initialize_openai():
    """Initialize OpenAI with API key from config."""
    try:
        config = ConfigLoader.load_config()
        openai.api_key = config['openai_api_key']
    except (FileNotFoundError, KeyError) as e:
        print(f"Error loading OpenAI configuration: {e}")
        raise




class RAGSystem:
    def __init__(self, db_path: str = 'local_browsing_history.db', 
                 index_path: str = 'faiss_index.bin'):
        """
        Initialize the RAG system with database and index paths.
        
        Args:
            db_path: Path to SQLite database containing Chrome history
            index_path: Path to FAISS index file
        """
        self.db_path = db_path
        self.index_path = index_path
        self.index = None
        self.load_faiss_index()

    def load_faiss_index(self) -> None:
        """Load the FAISS index from disk."""
        try:
            self.index = faiss.read_index(self.index_path)
        except Exception as e:
            raise Exception(f"Failed to load FAISS index: {str(e)}")

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode the query text using OpenAI's embedding model.
        
        Args:
            query: Input text to encode
            
        Returns:
            Numpy array containing the query embedding
        """
        response = openai.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        return np.array(embedding).reshape((1, -1))

    def search_index(self, query: str, k: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search the FAISS index for similar content.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        query_embedding = self.encode_query(query)
        return self.index.search(
            query_embedding.astype(np.float32),
            k
        )

    def retrieve_content_from_db(self, indices: List[int]) -> List[Tuple[str, str]]:
        """
        Retrieve content from SQLite database based on indices.
        
        Args:
            indices: List of database indices to retrieve
            
        Returns:
            List of (title, description) tuples
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            content = []
            print("passed index")
            print(indices[0])
            
            for idx in indices[0]:  # indices is a nested array
                print("SELECT title, description FROM browsing_history WHERE id = "+ str(idx))
                cursor.execute(
                    "SELECT title, description FROM browsing_history WHERE id = "+ str(idx)
                )
                result = cursor.fetchone()
                print(result)
                if result:
                    content.append(result)
                    
        return content

    def generate_openai_response(self, query: str) -> str:
        """
        Generate a direct response using OpenAI's API.
        
        Args:
            query: User query
            
        Returns:
            Generated response
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": query}],
            max_tokens=150
        )
        return response.choices[0].message.content

    def generate_response_from_content(self, 
                                    retrieved_content: List[Tuple[str, str]], 
                                    query: str) -> str:
        """
        Generate a response based on retrieved content.
        
        Args:
            retrieved_content: List of (title, description) tuples
            query: Original user query
            
        Returns:
            Generated response
        """
        context = "\n".join([
            f"Title: {title}\nDescription: {desc}" 
            for title, desc in retrieved_content
        ])
        
        prompt = (f"Based on the following information and the user's query: "
                 f"'{query}', the retrieved response is \n\n{context} . Please strcuture the answer")
        
        print()

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content

    def query(self, 
             user_query: str, 
             mode: str = "rag", 
             k: int = 1) -> Union[str, List[Tuple[str, str]]]:
        """
        Process a user query in either RAG or direct generation mode.
        
        Args:
            user_query: User's question
            mode: Either "rag" for Chrome history search or "generate" for direct OpenAI
            k: Number of results to retrieve (for RAG mode)
            
        Returns:
            Either a generated response string or list of relevant content
        """
        if mode.lower() == "rag":
            distances, indices = self.search_index(user_query, k)
            relevant_content = self.retrieve_content_from_db(indices)
            
            if not relevant_content:
                return "No relevant content found in Chrome history."
                

            temp_answer  =self.generate_response_from_content(relevant_content, user_query)

            return temp_answer
            
        elif mode.lower() == "generate":
            return self.generate_openai_response(user_query)
            
        else:
            raise ValueError("Mode must be either 'rag' or 'generate'")

# Example usage
if __name__ == "__main__":
    # Initialize the system
    rag_system = RAGSystem()
    
    # Example queries
    query = "Upstox Accounts None"
    
    # Use RAG mode (search Chrome history)
    rag_response = rag_system.query(query, mode="rag", k=3)
    print("RAG Response:", rag_response)
    
    # Use direct generation mode
    direct_response = rag_system.query(query, mode="generate")
    print("Direct Response:", direct_response)