import logging
from typing import List, Dict, Any

logger = logging.getLogger("app.agents.investigators.knowledge.utils.token_counter")

class TokenCounter:
    """Calculates tokens count for documents and chunks with fallbacks to word-length estimation."""

    def __init__(self, model_name: str = "cl100k_base") -> None:
        self.model_name = model_name
        self.encoder = None
        try:
            import tiktoken
            # Try to get encoding for model
            try:
                self.encoder = tiktoken.encoding_for_model(model_name)
            except Exception:
                self.encoder = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            logger.info("tiktoken library not installed. Falling back to word estimation metric.")

    def count_tokens(self, text: str) -> int:
        """Returns the number of tokens in a string."""
        if not text:
            return 0
        if self.encoder:
            return len(self.encoder.encode(text))
        
        # Fallback word-length estimation (typical English text has ~1.3 tokens per word)
        words = len(text.split())
        return int(words * 1.3) + 1

    def calculate_statistics(self, chunks: List[Dict[str, Any]], document_text: str) -> Dict[str, Any]:
        """Calculates token counts, averages, and bounds for execution telemetry."""
        doc_tokens = self.count_tokens(document_text)
        
        chunk_token_counts = []
        for c in chunks:
            # Count tokens and inject into chunk dictionary
            cnt = self.count_tokens(c["content"])
            c["token_count"] = cnt
            chunk_token_counts.append(cnt)

        num_chunks = len(chunks)
        avg_chunk = sum(chunk_token_counts) / num_chunks if num_chunks > 0 else 0.0
        max_chunk = max(chunk_token_counts) if num_chunks > 0 else 0

        return {
            "document_tokens": doc_tokens,
            "chunks_count": num_chunks,
            "average_chunk_size_tokens": avg_chunk,
            "maximum_chunk_size_tokens": max_chunk,
            "chunk_token_counts": chunk_token_counts
        }
export_token_counter = TokenCounter
