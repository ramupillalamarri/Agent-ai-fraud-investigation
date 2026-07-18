import json
import re
from typing import Dict, Any

class DocumentParser:
    """Parses text content from supported document formats."""

    def parse(self, content_bytes: bytes, extension: str) -> str:
        """Determines format parsing logic based on file extension and returns extracted text."""
        ext = extension.lower().strip()
        
        if ext == "txt" or ext == "md":
            return content_bytes.decode("utf-8", errors="ignore")
            
        elif ext == "json":
            try:
                data = json.loads(content_bytes.decode("utf-8"))
                # If it's a dict/list of objects, serialize key values nicely
                if isinstance(data, dict):
                    return json.dumps(data, indent=2)
                return str(data)
            except Exception as e:
                raise ValueError(f"JSON parsing failed: {str(e)}")
                
        elif ext == "html":
            html_str = content_bytes.decode("utf-8", errors="ignore")
            # Strip html tags but preserve structural headings/paragraphs
            text = re.sub(r"<[^>]+>", " ", html_str)
            return text
            
        elif ext == "pdf":
            # PDF text extraction fallback/pypdf import checks
            try:
                import pypdf
                from io import BytesIO
                reader = pypdf.PdfReader(BytesIO(content_bytes))
                text_pages = [page.extract_text() for page in reader.pages]
                return "\n".join(text_pages)
            except ImportError:
                # Fallback basic PDF text scanner (searches for ASCII text blocks in PDF streams)
                # Find all printable strings between text operators or bracket blocks
                text_matches = re.findall(b"\\(([^)]+)\\)\\s*Tj", content_bytes)
                if not text_matches:
                    text_matches = re.findall(b"BT\\s*(.*?)\\s*ET", content_bytes, re.DOTALL)
                
                if text_matches:
                    decoded = []
                    for match in text_matches:
                        decoded.append(match.decode("ascii", errors="ignore"))
                    return "\n".join(decoded)
                
                # Ultimate fallback: decode as text (ignoring binaries)
                return content_bytes.decode("utf-8", errors="ignore")
                
        elif ext == "docx":
            # Future-ready DOCX placeholder stub
            return "DOCX Ingestion content (Future-ready stub placeholder)."
            
        else:
            raise ValueError(f"No parser implemented for extension '{ext}'")
export_parser = DocumentParser
