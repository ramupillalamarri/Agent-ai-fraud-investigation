from dataclasses import dataclass, field
from typing import List

@dataclass
class KnowledgeAgentConfig:
    """Configurable options for document loading, chunk size, vector search, and similarity thresholds."""
    
    # Chunking options
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Vector store / search options
    top_k: int = 3
    similarity_threshold: float = 0.30
    
    # Default directories / paths
    knowledge_dir: str = "backend/app/agents/investigators/knowledge/documents"
    
    # Default document playbooks for RAG indexing
    default_playbooks: List[dict] = field(default_factory=lambda: [
        {
            "id": "playbook-01",
            "title": "Account Takeover (ATO) Response Playbook",
            "content": "When account takeover (ATO) is suspected due to device fingerprint mismatch, geographic location jump, or billing updates, trigger MFA validation immediately. If risk score is above 80%, block the transaction and freeze the profile. If under 80%, place on 24-hour review hold.",
            "category": "playbook",
            "source": "Fraud Response Policy v1.2"
        },
        {
            "id": "guideline-02",
            "title": "Northeast US Retail Card Fraud Pattern Guide",
            "content": "Recent skimming fraud rings operate by executing card-not-present (CNP) purchases in rapid velocity (consecutive orders under 10 seconds) at electronics or gaming category merchants. Recommended actions: apply strict velocity limit rules and request device owner verification.",
            "category": "guideline",
            "source": "Retail Security Bulletins 2026"
        },
        {
            "id": "compliance-03",
            "title": "OFAC Sanctions & AML Compliance Policy",
            "content": "All transactions must be matched against OFAC sanctions watchlists. If an IP matches a high-risk jurisdiction, or names align with OFAC lists, escalate to legal counsel and suspend payment processing. False positives must be documented by senior analysts.",
            "category": "compliance",
            "source": "AML Regulatory Policy"
        }
    ])
