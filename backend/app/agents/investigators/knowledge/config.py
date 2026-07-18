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

    # Ingestion pipeline settings
    supported_formats: list[str] = ("pdf", "md", "txt", "html", "json", "docx")
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_categories: list[str] = (
        "fraud_playbooks", "compliance", "pci_dss", "aml", 
        "merchant_policies", "historical_cases", "internal_guidelines"
    )
    max_tokens: int = 8192
    cache_enabled: bool = True

    # Vector Database settings
    collection_name: str = "retail_fraud_knowledge"
    embedding_dimension: int = 1536
    batch_size: int = 100
    distance_metric: str = "cosine"
    persist_directory: str = "chromadb_data"

    # Retrieval Engine settings
    similarity_threshold: float = 0.50
    metadata_boost: float = 0.15
    recency_weight: float = 0.10
    hybrid_search: bool = True


