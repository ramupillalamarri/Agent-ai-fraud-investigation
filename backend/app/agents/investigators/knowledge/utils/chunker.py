import re
from typing import List, Dict, Any
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig

class DocumentChunker:
    """Splits normalized text documents into semantic chunks with offsets and structural metadata."""

    def __init__(self, config: KnowledgeAgentConfig) -> None:
        self.config = config

    def split_document(self, text: str, document_id: str, strategy: str = "recursive") -> List[Dict[str, Any]]:
        """Splits document text based on the selected chunking strategy."""
        if not text:
            return []

        strategy = strategy.lower().strip()
        chunks_raw = []

        if strategy == "fixed":
            chunks_raw = self._split_fixed(text)
        elif strategy == "sentence":
            chunks_raw = self._split_sentence(text)
        elif strategy == "paragraph":
            chunks_raw = self._split_paragraph(text)
        else:  # default recursive
            chunks_raw = self._split_recursive(text)

        # Post-process raw text slices into structured chunk dicts with metadata
        processed_chunks = []
        for idx, (chunk_text, start_offset, end_offset) in enumerate(chunks_raw):
            section_title = self._find_nearest_section_title(text, start_offset)
            page_num = (start_offset // 2000) + 1  # basic estimate of 2000 characters per page
            
            processed_chunks.append({
                "chunk_id": f"chunk_{document_id}_{idx}",
                "document_id": document_id,
                "content": chunk_text,
                "start_offset": start_offset,
                "end_offset": end_offset,
                "section_title": section_title,
                "page_number": page_num,
                "token_count": 0  # To be filled by token counter
            })

        return processed_chunks

    def _split_fixed(self, text: str) -> List[tuple[str, int, int]]:
        """Splits text by fixed character sizes and sliding window overlaps."""
        results = []
        size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        text_len = len(text)
        start = 0

        while start < text_len:
            end = min(start + size, text_len)
            chunk = text[start:end]
            results.append((chunk, start, end))
            if end == text_len:
                break
            start += size - overlap
            
        return results

    def _split_paragraph(self, text: str) -> List[tuple[str, int, int]]:
        """Splits text into chunks respecting paragraph boundaries."""
        results = []
        paragraphs = re.split(r"\n\n", text)
        current_offset = 0
        
        for para in paragraphs:
            if not para.strip():
                # Account for character offset of paragraph breaks
                current_offset += len(para) + 2
                continue
                
            start = text.find(para, current_offset)
            end = start + len(para)
            results.append((para, start, end))
            current_offset = end
            
        return results

    def _split_sentence(self, text: str) -> List[tuple[str, int, int]]:
        """Splits text into chunks respecting sentence boundaries."""
        results = []
        # Split on sentence terminals followed by space
        sentences = re.split(r"(?<=[.!?])\s+", text)
        current_offset = 0
        
        for sent in sentences:
            if not sent.strip():
                current_offset += len(sent)
                continue
            start = text.find(sent, current_offset)
            end = start + len(sent)
            results.append((sent, start, end))
            current_offset = end
            
        return results

    def _split_recursive(self, text: str) -> List[tuple[str, int, int]]:
        """Recursively splits text on paragraph, sentence, and space boundaries to fit chunk limits."""
        results = []
        size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        
        def recurse(sub_text: str, offset: int):
            if len(sub_text) <= size:
                if sub_text.strip():
                    results.append((sub_text, offset, offset + len(sub_text)))
                return
                
            # Attempt to split by paragraph first
            split_points = [m.start() for m in re.finditer(r"\n\n", sub_text)]
            if not split_points:
                # Attempt to split by sentence
                split_points = [m.start() for m in re.finditer(r"(?<=[.!?])\s+", sub_text)]
            if not split_points:
                # Attempt to split by space
                split_points = [m.start() for m in re.finditer(r"\s+", sub_text)]
                
            if not split_points:
                # Fallback to fixed chunking
                chunk = sub_text[:size]
                results.append((chunk, offset, offset + len(chunk)))
                recurse(sub_text[size - overlap:], offset + size - overlap)
                return

            # Find optimal split index that fits under chunk_size
            optimal_split = -1
            for p in split_points:
                if p <= size:
                    optimal_split = p
                else:
                    break
                    
            if optimal_split == -1:
                # If no split point is under size, force split on first available point
                optimal_split = split_points[0]
                
            chunk = sub_text[:optimal_split]
            if chunk.strip():
                results.append((chunk, offset, offset + len(chunk)))
            # recurse remaining text with overlap
            remaining_start = max(0, optimal_split - overlap)
            recurse(sub_text[remaining_start:], offset + remaining_start)

        recurse(text, 0)
        return results

    def _find_nearest_section_title(self, text: str, offset: int) -> str:
        """Scans backward from the current offset to locate the nearest markdown heading title."""
        # Search for headings starting with '#' before the offset
        search_sub = text[:offset]
        headings = re.findall(r"(?:^|\n)(#+\s+.*)", search_sub)
        if headings:
            # Return last heading found, clean leading hash symbols
            last_heading = headings[-1]
            return re.sub(r"^#+\s+", "", last_heading).strip()
        return "Introduction"
export_chunker = DocumentChunker
