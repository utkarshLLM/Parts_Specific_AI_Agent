"""
Vector Store Module
Handles embedding storage and similarity search for products
Uses FAISS for local vector database (no external dependencies)
"""

import json
import os
import numpy as np
from typing import List, Dict, Tuple


class VectorStore:
    """Local vector store using FAISS for similarity search"""
    
    def __init__(self, embedding_dim: int = 384):
        """Initialize vector store with embedding dimension"""
        self.embedding_dim = embedding_dim
        self.vectors = None
        self.metadata = []
        self.initialized = False
        
        # Try to import FAISS, fallback to numpy if unavailable
        try:
            import faiss
            self.faiss = faiss
            self.use_faiss = True
        except ImportError:
            self.use_faiss = False
            print("FAISS not available, using numpy for search (slower)")
    
    def initialize_from_products(self, products: List[Dict]) -> None:
        """
        Initialize vector store from product list.
        Each product should have: id, name, description, category, model_compat
        """
        if not products:
            raise ValueError("Products list cannot be empty")
        
        self.metadata = products
        embeddings = self._generate_embeddings(products)
        self._build_index(embeddings)
        self.initialized = True
        print(f"Vector store initialized with {len(products)} products")
    
    def _generate_embeddings(self, products: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for products using simple TF-IDF style approach.
        For production, replace with actual embedding model (e.g., sentence-transformers).
        """
        embeddings = []
        
        for product in products:
            # Combine text fields for embedding
            text = f"{product.get('name', '')} {product.get('description', '')} {product.get('category', '')}"
            text = text.lower()
            
            # Simple embedding: one-hot encode keywords (for demo)
            # In production, use: from sentence_transformers import SentenceTransformer
            embedding = self._create_simple_embedding(text)
            embeddings.append(embedding)
        
        return np.array(embeddings, dtype=np.float32)
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """Create a simple embedding vector from text"""
        # For production, replace with real embeddings:
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # return model.encode(text)
        
        # Demo embedding: hash-based simple approach
        keywords = {
            'refrigerator': 0, 'fridge': 0, 'ice maker': 1, 'freezer': 2,
            'dishwasher': 3, 'spray': 4, 'pump': 5, 'filter': 6,
            'installation': 7, 'install': 7, 'compatible': 8, 'model': 9,
            'part': 10, 'number': 11, 'whirlpool': 12, 'lg': 13, 'samsung': 14,
            'problem': 15, 'issue': 15, 'fix': 16, 'repair': 16
        }
        
        embedding = np.zeros(self.embedding_dim, dtype=np.float32)
        words = text.split()
        
        for word in words:
            if word in keywords:
                idx = keywords[word]
                if idx < self.embedding_dim:
                    embedding[idx] += 1.0
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _build_index(self, embeddings: np.ndarray) -> None:
        """Build search index from embeddings"""
        if self.use_faiss:
            self.vectors = self.faiss.IndexFlatL2(self.embedding_dim)
            self.vectors.add(embeddings)
        else:
            self.vectors = embeddings
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar products given a query string.
        Returns top_k most similar products with scores.
        """
        if not self.initialized:
            return []
        
        # Generate query embedding
        query_embedding = self._create_simple_embedding(query).reshape(1, -1)
        
        # Search
        if self.use_faiss:
            distances, indices = self.vectors.search(query_embedding, min(top_k, len(self.metadata)))
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                product = self.metadata[int(idx)].copy()
                product['score'] = float(1 / (1 + distance))  # Convert distance to similarity
                results.append(product)
        else:
            # Numpy-based search
            similarities = np.dot(self.vectors, query_embedding.T).flatten()
            top_indices = np.argsort(-similarities)[:top_k]
            results = []
            for idx in top_indices:
                product = self.metadata[int(idx)].copy()
                product['score'] = float(similarities[idx])
                results.append(product)
        
        return results
    
    def get_by_id(self, product_id: str) -> Dict:
        """Get product by ID"""
        for product in self.metadata:
            if product.get('id') == product_id:
                return product
        return None
    
    def search_by_model(self, model_number: str) -> List[Dict]:
        """Search for products compatible with a specific model"""
        model_number = model_number.lower()
        results = []
        
        for product in self.metadata:
            compat_models = product.get('compatible_models', [])
            if isinstance(compat_models, str):
                compat_models = [compat_models]
            
            if any(model_number in str(m).lower() for m in compat_models):
                results.append(product)
        
        return results
    
    def save_to_file(self, filepath: str) -> None:
        """Save vector store to file for persistence"""
        if not self.initialized:
            raise ValueError("Vector store not initialized")
        
        data = {
            'metadata': self.metadata,
            'embedding_dim': self.embedding_dim
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        print(f"Vector store saved to {filepath}")
    
    def load_from_file(self, filepath: str) -> None:
        """Load vector store from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.metadata = data['metadata']
        self.embedding_dim = data['embedding_dim']
        
        embeddings = self._generate_embeddings(self.metadata)
        self._build_index(embeddings)
        self.initialized = True
        
        print(f"Vector store loaded from {filepath}")


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def initialize_vector_store(products: List[Dict]) -> VectorStore:
    """Initialize the global vector store"""
    global _vector_store
    _vector_store = VectorStore()
    _vector_store.initialize_from_products(products)
    return _vector_store