import os
from datetime import datetime
from typing import Dict, Any, Tuple

class DocumentLoader:
    """Reads raw file bytes and extracts filesystem modification parameters."""

    def load_filepath(self, filepath: str) -> Tuple[bytes, Dict[str, Any]]:
        """Reads file contents from disk and returns raw bytes along with filesystem metadata."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found at path: {filepath}")

        # Get file size & modification statistics
        stat = os.stat(filepath)
        size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        created_time = datetime.fromtimestamp(stat.st_ctime)

        # Read binary content
        with open(filepath, "rb") as f:
            content_bytes = f.read()

        file_metadata = {
            "source": filepath,
            "filename": os.path.basename(filepath),
            "file_size_bytes": size,
            "created_at": created_time,
            "last_modified": modified_time,
            "file_extension": os.path.splitext(filepath)[1].lower().replace(".", "")
        }

        return content_bytes, file_metadata
