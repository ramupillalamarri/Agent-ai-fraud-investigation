import sys
import os
import pytest
from typing import Dict, Any

# Set pythonpath so we can import app modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.investigators.knowledge.config import KnowledgeAgentConfig
from app.agents.investigators.knowledge.services.document_service import DocumentService
from app.agents.investigators.knowledge.models.knowledge_document import KnowledgeDocument

@pytest.fixture
def doc_service():
    config = KnowledgeAgentConfig()
    return DocumentService(config)

def test_markdown_ingestion(tmp_path, doc_service):
    """Verify Markdown parsing, metadata extraction, and normalization layout checks."""
    md_content = """# AML Verification Guide

- Verify customer ID
- Match billing addresses
"""
    file_path = tmp_path / "aml_guide.md"
    file_path.write_text(md_content, encoding="utf-8")
    
    doc = doc_service.ingest_document(str(file_path), "aml")
    
    assert isinstance(doc, KnowledgeDocument)
    assert doc.title == "AML Verification Guide"
    assert doc.category == "aml"
    assert "Verify customer ID" in doc.content
    assert doc.metadata["author"] == "System Engine"

def test_html_ingestion(tmp_path, doc_service):
    """Verify HTML parsing strips tags while preserving structure."""
    html_content = """
    <html>
        <body>
            <h1>Merchant Refund Rules</h1>
            <p>Refunds should not exceed 10% of total weekly volume.</p>
        </body>
    </html>
    """
    file_path = tmp_path / "refund_rules.html"
    file_path.write_text(html_content, encoding="utf-8")
    
    doc = doc_service.ingest_document(str(file_path), "merchant_policies")
    
    assert "Merchant Refund Rules" in doc.content
    assert "Refunds should not exceed 10%" in doc.content
    assert "<p>" not in doc.content
    assert "<html>" not in doc.content

def test_json_ingestion(tmp_path, doc_service):
    """Verify JSON parsing decodes object fields successfully."""
    json_content = '{"case_id": "CASE-9922", "findings": ["Chargeback velocity alert matched on electronic purchase."]}'
    file_path = tmp_path / "case_record.json"
    file_path.write_text(json_content, encoding="utf-8")
    
    doc = doc_service.ingest_document(str(file_path), "historical_cases")
    
    assert "CASE-9922" in doc.content
    assert "Chargeback velocity" in doc.content

def test_pdf_ingestion_fallback(tmp_path, doc_service):
    """Verify PDF scanner matches text operators under the fallback regex mode."""
    # Write text streams formatted as basic PDF structure chunks
    pdf_bytes = b"BT (OFAC Compliance Checks are mandatory for all wires) Tj ET"
    file_path = tmp_path / "ofac_sop.pdf"
    file_path.write_bytes(pdf_bytes)
    
    doc = doc_service.ingest_document(str(file_path), "compliance")
    
    assert "OFAC Compliance Checks" in doc.content

def test_ingestion_validation_rules(tmp_path, doc_service):
    """Verify validation triggers on size limits, categories, and duplicates."""
    # 1. Invalid category check
    file_path = tmp_path / "normal.txt"
    file_path.write_text("Legitimate playbooks.", encoding="utf-8")
    
    with pytest.raises(ValueError, match="Category 'invalid_category' is not allowed"):
        doc_service.ingest_document(str(file_path), "invalid_category")
        
    # 2. Duplicate document check
    doc_service.ingest_document(str(file_path), "fraud_playbooks")
    with pytest.raises(ValueError, match="Duplicate file content signature detected"):
        doc_service.ingest_document(str(file_path), "fraud_playbooks")
