import math
import re
from typing import List, Dict

class LocalEmbeddingEngine:
    """Generates normalized Term Frequency (TF) embedding vectors for text processing."""

    def _tokenize(self, text: str) -> List[str]:
        """Standardizes and tokenizes text input."""
        return re.findall(r'[a-zA-Z0-9]+', text.lower())

    def get_vocabulary(self, texts: List[str]) -> List[str]:
        """Builds a unique sorted vocabulary list from a collection of texts."""
        vocab = set()
        for text in texts:
            vocab.update(self._tokenize(text))
        return sorted(list(vocab))

    def get_embedding(self, text: str, vocabulary: List[str]) -> List[float]:
        """Generates a normalized Term Frequency (TF) vector for a text string."""
        tokens = self._tokenize(text)
        counts = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1

        vector = []
        for word in vocabulary:
            vector.append(float(counts.get(word, 0)))

        # Apply standard L2 vector normalization
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            return [v / magnitude for v in vector]
        return [0.0] * len(vocabulary)
