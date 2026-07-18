import logging
import math
from typing import List, Dict, Any, Optional
from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.providers.vector_store_provider import VectorStoreProvider
from app.agents.investigators.knowledge.models.retrieval_result import RetrievalResult

logger = logging.getLogger("app.agents.investigators.knowledge.providers.chromadb_provider")

# Try-import ChromaDB library, fallback to clean in-memory cosine similarity engine
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.info("ChromaDB library not found. Instantiating in-memory fallback emulation client.")


class InMemoryCollectionMock:
    """Emulates a ChromaDB collection in-memory using math-based Cosine Distance metric."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.data: Dict[str, Dict[str, Any]] = {}

    def add(self, ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        for idx, cid in enumerate(ids):
            self.data[cid] = {
                "vector": embeddings[idx],
                "document": documents[idx],
                "metadata": metadatas[idx]
            }

    def update(self, ids: List[str], embeddings: Optional[List[List[float]]] = None, documents: Optional[List[str]] = None, metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        for idx, cid in enumerate(ids):
            if cid in self.data:
                if embeddings:
                    self.data[cid]["vector"] = embeddings[idx]
                if documents:
                    self.data[cid]["document"] = documents[idx]
                if metadatas:
                    self.data[cid]["metadata"] = metadatas[idx]

    def delete(self, ids: List[str]) -> None:
        for cid in ids:
            self.data.pop(cid, None)

    def count(self) -> int:
        return len(self.data)

    def query(self, query_embeddings: List[List[float]], n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        results = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        if not self.data or not query_embeddings:
            return results

        q_vec = query_embeddings[0]

        def cosine_distance(v1: List[float], v2: List[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(a * a for a in v2))
            if norm1 == 0 or norm2 == 0:
                return 1.0
            return 1.0 - (dot / (norm1 * norm2))

        candidates = []
        for cid, item in self.data.items():
            # Check metadata metadata filter
            if where:
                match = True
                for k, v in where.items():
                    if item["metadata"].get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            dist = cosine_distance(q_vec, item["vector"])
            candidates.append((dist, cid, item))

        # Sort by distance ascending
        candidates.sort(key=lambda x: x[0])
        top = candidates[:n_results]

        for dist, cid, item in top:
            results["ids"][0].append(cid)
            results["distances"][0].append(dist)
            results["documents"][0].append(item["document"])
            results["metadatas"][0].append(item["metadata"])

        return results


class InMemoryChromaMockClient:
    """Emulates a Persistent ChromaDB client in-memory."""

    def __init__(self, persist_directory: str) -> None:
        self.persist_directory = persist_directory
        self._collections: Dict[str, InMemoryCollectionMock] = {}

    def get_or_create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> InMemoryCollectionMock:
        if name not in self._collections:
            self._collections[name] = InMemoryCollectionMock(name)
        return self._collections[name]

    def delete_collection(self, name: str) -> None:
        self._collections.pop(name, None)


class ChromaDBProvider(VectorStoreProvider):
    """Concrete implementation of VectorStoreProvider using ChromaDB database."""

    def __init__(self, config: KnowledgeAgentConfig) -> None:
        self.config = config
        self.client = None
        self.collection = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Instantiates either persistent local ChromaDB or mock emulation client."""
        try:
            if CHROMADB_AVAILABLE:
                # Reuse connection client instance
                self.client = chromadb.PersistentClient(path=self.config.persist_directory)
                logger.info("ChromaDB persistent client initialized successfully at: %s", self.config.persist_directory)
            else:
                self.client = InMemoryChromaMockClient(self.config.persist_directory)
                logger.info("In-memory fallback Chroma emulation client initialized.")

            # Create default collection
            self.create_collection(self.config.collection_name)
        except Exception as e:
            logger.error("Failed to initialize ChromaDB connection: %s", str(e), exc_info=True)
            raise

    def create_collection(self, name: str) -> None:
        """Retrieves or creates a named vector collection schema."""
        try:
            # Map metrics to Chroma representation
            metadata = {}
            if self.config.distance_metric == "cosine":
                metadata["hnsw:space"] = "cosine"
            elif self.config.distance_metric == "l2":
                metadata["hnsw:space"] = "l2"
            else:
                metadata["hnsw:space"] = "ip"

            self.collection = self.client.get_or_create_collection(name, metadata=metadata)
            logger.info("Collection created or loaded: %s", name)
        except Exception as e:
            logger.error("Failed to create collection: %s", str(e))
            raise

    def delete_collection(self, name: str) -> None:
        """Deletes collection schema and all indexed vector items."""
        try:
            self.client.delete_collection(name)
            self.collection = None
            logger.info("Collection deleted: %s", name)
        except Exception as e:
            logger.error("Failed to delete collection %s: %s", name, str(e))
            raise

    def add_vectors(self, ids: List[str], vectors: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Indexes/upserts document vector embeddings in batches."""
        if not self.collection:
            raise RuntimeError("Database error: Collection is not initialized.")
        try:
            # Process in config-defined batch sizes
            b_size = self.config.batch_size
            total = len(ids)
            for i in range(0, total, b_size):
                b_ids = ids[i:i+b_size]
                b_vectors = vectors[i:i+b_size]
                b_docs = documents[i:i+b_size]
                b_meta = metadatas[i:i+b_size]
                
                logger.info("Batch indexing vectors: slice %d to %d (total %d)", i, min(i+b_size, total), total)
                self.collection.add(
                    ids=b_ids,
                    embeddings=b_vectors,
                    documents=b_docs,
                    metadatas=b_meta
                )
            logger.info("Documents indexed successfully: added %d items", total)
        except Exception as e:
            logger.error("Failed to add vectors to database: %s", str(e))
            raise

    def update_vectors(self, ids: List[str], vectors: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Updates vector embeddings and matching metadata fields."""
        if not self.collection:
            raise RuntimeError("Database error: Collection is not initialized.")
        try:
            self.collection.update(
                ids=ids,
                embeddings=vectors,
                documents=documents,
                metadatas=metadatas
            )
            logger.info("Update completed: modified %d items", len(ids))
        except Exception as e:
            logger.error("Failed to update vectors: %s", str(e))
            raise

    def delete_vectors(self, ids: List[str]) -> None:
        """Removes specified vector records by document/chunk IDs."""
        if not self.collection:
            raise RuntimeError("Database error: Collection is not initialized.")
        try:
            self.collection.delete(ids=ids)
            logger.info("Delete completed: removed %d items", len(ids))
        except Exception as e:
            logger.error("Failed to delete vectors: %s", str(e))
            raise

    def similarity_search(self, query_vector: List[float], top_k: int) -> List[RetrievalResult]:
        """Queries the vector database using vector embedding similarity distance metrics."""
        return self.similarity_search_with_filter(query_vector, top_k, None)

    def similarity_search_with_filter(self, query_vector: List[float], top_k: int, metadata_filter: Optional[Dict[str, Any]]) -> List[RetrievalResult]:
        """Queries the vector database utilizing both vector similarity and metadata WHERE constraints."""
        if not self.collection:
            raise RuntimeError("Database error: Collection is not initialized.")
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=metadata_filter
            )

            # Map raw dictionary queries into RetrievalResult list contract
            mapped_results = []
            if results and results.get("ids"):
                ids_list = results["ids"][0]
                docs_list = results["documents"][0]
                meta_list = results["metadatas"][0]
                
                # Fallback distance calculations if they are empty
                distances = results.get("distances", [[]])[0]
                
                for idx, cid in enumerate(ids_list):
                    score = 1.0 - distances[idx] if idx < len(distances) else 1.0
                    meta = meta_list[idx]
                    mapped_results.append(
                        RetrievalResult(
                            document_id=meta.get("document_id", "unknown"),
                            chunk_id=cid,
                            score=score,
                            content=docs_list[idx],
                            metadata=meta
                        )
                    )
            return mapped_results
        except Exception as e:
            logger.error("Failed to perform similarity search: %s", str(e))
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Returns statistical counts representing collection record sizes."""
        if not self.collection:
            return {"count": 0}
        try:
            return {
                "collection_name": self.config.collection_name,
                "count": self.collection.count()
            }
        except Exception as e:
            logger.error("Failed to retrieve statistics: %s", str(e))
            return {"count": 0}

    def health_check(self) -> bool:
        """Verifies database operational states and client connections."""
        logger.info("Health check started")
        try:
            if self.client is None or self.collection is None:
                return False
            # Verify basic collection count query responds successfully
            self.collection.count()
            return True
        except Exception as e:
            logger.error("Health check failed with error: %s", str(e))
            return False
export_provider = ChromaDBProvider
