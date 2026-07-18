from typing import List

def split_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Helper utility splitting raw text documents into overlapping chunk segments."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
        
    return chunks
