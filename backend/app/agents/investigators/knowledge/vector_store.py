import logging
from typing import List, Dict, Any, Tuple, Optional
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.document_loader import Document
from app.agents.investigators.knowledge.embeddings import LocalEmbeddingEngine

logger = logging.getLogger("app.agents.KnowledgeAgent.VectorStore")

class LocalVectorStore:
    """In-memory vector store performing vector similarity searches on loaded documents."""

    def __init__(self, config: KnowledgeAgentConfig) -> None:
        self.config = config
        self.engine = LocalEmbeddingEngine()
        self.documents: List[Document] = []
        self.vocabulary: List[str] = []
        self.embeddings: List[List[float]] = []

    def index_documents(self, documents: List[Document]) -> None:
        """Indexes loaded documents, compiling the vocabulary and generating vectors."""
        self.documents = documents
        all_texts = [doc.page_content for doc in documents]
        self.vocabulary = self.engine.get_vocabulary(all_texts)
        
        self.embeddings = []
        for doc in documents:
            vector = self.engine.get_embedding(doc.page_content, self.vocabulary)
            self.embeddings.append(vector)
            
        logger.info("Indexed %d document chunks. Vocabulary size: %d", len(self.documents), len(self.vocabulary))

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates standard cosine similarity between two normalized vectors."""
        if len(vec_a) != len(vec_b):
            return 0.0
        return sum(a * b for a, b in zip(vec_a, vec_b))

    def similarity_search(
        self, 
        query: str, 
        top_k: int = 3, 
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """Finds top-K documents closest to the query string."""
        if not self.documents:
            return []
            
        query_vector = self.engine.get_embedding(query, self.vocabulary)
        
        results = []
        for doc, vector in zip(self.documents, self.embeddings):
            # Apply metadata filters if specified
            if filter_metadata:
                match = True
                for key, val in filter_metadata.items():
                    if doc.metadata.get(key) != val:
                        match = False
                        break
                if not match:
                    continue
                    
            similarity = self._cosine_similarity(query_vector, vector)
            results.append((doc, similarity))
            
        # Sort by similarity score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
