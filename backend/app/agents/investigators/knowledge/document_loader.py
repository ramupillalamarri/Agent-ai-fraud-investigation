import os
import json
import logging
from typing import List, Dict, Any
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig

logger = logging.getLogger("app.agents.KnowledgeAgent.DocumentLoader")

class Document:
    """Represents a text chunk and associated source metadata for RAG."""
    def __init__(self, page_content: str, metadata: Dict[str, Any]) -> None:
        self.page_content = page_content
        self.metadata = metadata

class DocumentLoader:
    """Loads internal playbooks, compliance guidelines, and policies into Document structures."""

    def __init__(self, config: KnowledgeAgentConfig) -> None:
        self.config = config

    def load_all(self) -> List[Document]:
        """Loads files from the target knowledge directory, falling back to static config files."""
        documents: List[Document] = []
        
        # Ensure target directory exists
        if os.path.exists(self.config.knowledge_dir):
            try:
                for file_name in os.listdir(self.config.knowledge_dir):
                    file_path = os.path.join(self.config.knowledge_dir, file_name)
                    if os.path.isfile(file_path):
                        if file_name.endswith((".txt", ".md")):
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            documents.append(Document(
                                page_content=content,
                                metadata={
                                    "title": file_name.rsplit(".", 1)[0],
                                    "source": file_name,
                                    "category": "local_documentation"
                                }
                            ))
                        elif file_name.endswith(".json"):
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    documents.append(Document(
                                        page_content=item.get("content", ""),
                                        metadata={
                                            "title": item.get("title", file_name),
                                            "source": item.get("source", file_name),
                                            "category": item.get("category", "json_records")
                                        }
                                    ))
            except Exception as e:
                logger.error("Error reading documents from directory %s: %s", self.config.knowledge_dir, str(e))

        # Fallback to defaults if no docs loaded
        if not documents:
            logger.info("No documents found in registry directory. Pre-populating default playbooks.")
            for doc in self.config.default_playbooks:
                documents.append(Document(
                    page_content=doc["content"],
                    metadata={
                        "title": doc["title"],
                        "source": doc["source"],
                        "category": doc["category"],
                        "id": doc["id"]
                    }
                ))
                
        return self.split_documents(documents)

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Splits loaded texts into smaller overlapping chunks for semantic retrieval."""
        split_docs = []
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        
        for doc in documents:
            text = doc.page_content
            if len(text) <= chunk_size:
                split_docs.append(doc)
                continue
                
            start = 0
            chunk_index = 0
            while start < len(text):
                end = start + chunk_size
                chunk_content = text[start:end]
                
                metadata = doc.metadata.copy()
                metadata["chunk_index"] = chunk_index
                
                split_docs.append(Document(page_content=chunk_content, metadata=metadata))
                
                start += chunk_size - overlap
                chunk_index += 1
                
        return split_docs
