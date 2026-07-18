from dataclasses import dataclass

@dataclass
class KnowledgeAgentConfig:
    """Configurable options and parameters for the Knowledge Agent RAG pipeline."""
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "text-embedding-3-small"
    vector_store: str = "chroma"
    top_k: int = 5
    reranking: bool = True
    cache: bool = True
