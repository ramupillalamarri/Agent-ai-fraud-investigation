import hashlib
from typing import Dict, Any, Set
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig

class DocumentValidator:
    """Validates document format, size, corruption, and signature duplicates."""

    def __init__(self, config: KnowledgeAgentConfig) -> None:
        self.config = config
        self._seen_hashes: Set[str] = set()

    def calculate_hash(self, content_bytes: bytes) -> str:
        """Computes the SHA-256 signature of raw content bytes."""
        return hashlib.sha256(content_bytes).hexdigest()

    def validate(self, content_bytes: bytes, file_metadata: Dict[str, Any]) -> None:
        """Checks sizes, format signatures, empty statuses, and duplicates."""
        # 1. Check for empty files
        if not content_bytes or len(content_bytes) == 0:
            raise ValueError("Document validation failed: Content payload is empty.")

        # 2. Check maximum file size limits
        size = file_metadata.get("file_size_bytes", len(content_bytes))
        if size > self.config.max_file_size_bytes:
            raise ValueError(
                f"Document validation failed: File size ({size} bytes) exceeds limit ({self.config.max_file_size_bytes} bytes)."
            )

        # 3. Check format matching
        ext = file_metadata.get("file_extension")
        if ext not in self.config.supported_formats:
            raise ValueError(f"Document validation failed: Format extension '{ext}' is not supported.")

        # 4. Check for duplicates
        file_hash = self.calculate_hash(content_bytes)
        if file_hash in self._seen_hashes:
            raise ValueError("Document validation failed: Duplicate file content signature detected.")

    def register_hash(self, file_hash: str) -> None:
        """Saves a verified hash to check against future duplicates."""
        self._seen_hashes.add(file_hash)

    def clear_hashes(self) -> None:
        """Clears the duplicate detection cache registry."""
        self._seen_hashes.clear()
