import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.models.knowledge_document import KnowledgeDocument
from app.agents.investigators.knowledge.utils.document_loader import DocumentLoader
from app.agents.investigators.knowledge.utils.document_validator import DocumentValidator
from app.agents.investigators.knowledge.utils.document_parser import DocumentParser
from app.agents.investigators.knowledge.utils.document_normalizer import DocumentNormalizer

logger = logging.getLogger("app.agents.investigators.knowledge.services.document_service")

class DocumentService:
    """ETL Service orchestrating raw document loading, validation, format parsing, and metadata tag extractions."""

    def __init__(
        self,
        config: KnowledgeAgentConfig,
        loader: Optional[DocumentLoader] = None,
        validator: Optional[DocumentValidator] = None,
        parser: Optional[DocumentParser] = None,
        normalizer: Optional[DocumentNormalizer] = None
    ) -> None:
        self.config = config
        self.loader = loader or DocumentLoader()
        self.validator = validator or DocumentValidator(config)
        self.parser = parser or DocumentParser()
        self.normalizer = normalizer or DocumentNormalizer()

    def ingest_document(self, filepath: str, category: str) -> KnowledgeDocument:
        """Runs the entire ingestion pipeline to load, parse, normalize, and extract document metadata."""
        # 0. Validate category
        if category not in self.config.allowed_categories:
            raise ValueError(f"Ingestion failed: Category '{category}' is not allowed.")

        # 1. Load document
        content_bytes, file_metadata = self.loader.load_filepath(filepath)
        logger.info("Document loaded: %s", filepath)

        # 2. Validate content
        self.validator.validate(content_bytes, file_metadata)
        # Register hash to prevent future duplicates in execution session
        file_hash = self.validator.calculate_hash(content_bytes)
        self.validator.register_hash(file_hash)
        logger.info("Document validated: %s", filepath)

        # 3. Parse content
        raw_text = self.parser.parse(content_bytes, file_metadata["file_extension"])
        logger.info("Document parsed: %s", filepath)

        # 4. Normalize content
        normalized_text = self.normalizer.normalize(raw_text)

        # 5. Extract metadata
        # Extract title from first markdown header if available, else use filename
        title = file_metadata["filename"]
        first_line = normalized_text.split("\n")[0] if normalized_text else ""
        if first_line.startswith("# "):
            title = first_line.replace("# ", "", 1).strip()
            
        doc_metadata = {
            "title": title,
            "category": category,
            "source": filepath,
            "author": file_metadata.get("author", "System Engine"),
            "created_date": str(file_metadata.get("created_at", datetime.utcnow())),
            "last_modified": str(file_metadata.get("last_modified", datetime.utcnow())),
            "document_version": file_metadata.get("document_version", "1.0.0"),
            "language": file_metadata.get("language", "en"),
            "sha256_hash": file_hash
        }
        logger.info("Metadata extracted: %s", filepath)

        # 6. Generate KnowledgeDocument
        doc = KnowledgeDocument(
            document_id=f"doc_{file_hash[:12]}",
            title=title,
            source=filepath,
            category=category,
            content=normalized_text,
            metadata=doc_metadata,
            created_at=file_metadata.get("created_at", datetime.utcnow())
        )
        logger.info("KnowledgeDocument created: %s", doc.document_id)

        return doc
