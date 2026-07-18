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
