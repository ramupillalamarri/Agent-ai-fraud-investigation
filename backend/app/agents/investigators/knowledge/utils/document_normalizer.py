import unicodedata
import re

class DocumentNormalizer:
    """Cleans extracted text, standardizing Unicode formats and white spaces while preserving layout indicators."""

    def normalize(self, text: str) -> str:
        """Runs Unicode normalization (NFKC), standardizes spacing, and clears redundant blank lines."""
        if not text:
            return ""

        # 1. Unicode normalization (NFKC)
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Convert carriage returns
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # 3. Standardize horizontal whitespace (tabs, consecutive spaces) on each line
        lines = normalized.split("\n")
        cleaned_lines = []
        for line in lines:
            # If the line is a header (starts with #) or a list (starts with -, *, numbers), preserve leading spaces/symbols
            is_layout = re.match(r"^\s*(?:#+|-|\*|\d+\.)", line)
            if is_layout:
                # Preserve leading markup, only compress duplicate spaces inside the line
                prefix = is_layout.group(0)
                body = line[len(prefix):]
                compressed_body = re.sub(r"[ \t]+", " ", body).strip()
                cleaned_lines.append(f"{prefix.rstrip()} {compressed_body}".strip())
            else:
                # Standard line, collapse whitespace
                collapsed = re.sub(r"[ \t]+", " ", line).strip()
                cleaned_lines.append(collapsed)

        # Rejoin lines
        rejoined = "\n".join(cleaned_lines)

        # 4. Collapse three or more consecutive blank lines down to two blank lines (double newline)
        collapsed_newlines = re.sub(r"\n{3,}", "\n\n", rejoined)

        return collapsed_newlines.strip()
export_normalizer = DocumentNormalizer
