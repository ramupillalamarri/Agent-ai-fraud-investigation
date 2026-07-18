import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.models.investigation_context import InvestigationContext

logger = logging.getLogger("app.agents.investigators.merchant.analyzers.merchant_reputation_analyzer")

class ReputationProvider(ABC):
    """Abstract interface representing external or internal reputation threat intelligence providers."""
    
    @abstractmethod
    def check_reputation(self, merchant_id: str, fields: Dict[str, Any], config: MerchantAgentConfig) -> List[Dict[str, Any]]:
        """Audits merchant identifiers against provider database definitions."""
        pass


class InternalRiskEngineProvider(ReputationProvider):
    """Evaluates internal system reputation, whitelists, blacklists, watchlists, trust scores, and dispute metrics."""
    
    def check_reputation(self, merchant_id: str, fields: Dict[str, Any], config: MerchantAgentConfig) -> List[Dict[str, Any]]:
        evidence = []
        
        # 1. Blacklist check
        if merchant_id in config.blacklisted_merchants or fields.get("merchant_blacklisted") is True:
            evidence.append({
                "type": "BlacklistedMerchant",
                "severity": "CRITICAL",
                "title": "Blacklisted Merchant Profile",
                "description": f"Merchant ID '{merchant_id}' matches system blacklist records for past fraud/compliance events.",
                "confidence": 0.99,
                "source": "InternalRiskEngineProvider",
                "metadata": {"merchant_id": merchant_id, "list": "blacklist"}
            })
            
        # 2. Whitelist check
        if merchant_id in config.whitelisted_merchants or fields.get("merchant_whitelisted") is True:
            evidence.append({
                "type": "WhitelistedMerchantExemption",
                "severity": "LOW",
                "title": "Whitelisted Merchant Exemption",
                "description": f"Merchant ID '{merchant_id}' matches a trusted whitelist profile, lowering overall risk classification.",
                "confidence": 0.95,
                "source": "InternalRiskEngineProvider",
                "metadata": {"merchant_id": merchant_id, "list": "whitelist"}
            })

        # 3. Watchlist check
        if merchant_id in config.watchlist_merchants or fields.get("merchant_watchlisted") is True:
            evidence.append({
                "type": "WatchlistedMerchant",
                "severity": "HIGH",
                "title": "Watchlisted Merchant Profile",
                "description": f"Merchant ID '{merchant_id}' matches internal monitor/watchlist guidelines.",
                "confidence": 0.85,
                "source": "InternalRiskEngineProvider",
                "metadata": {"merchant_id": merchant_id, "list": "watchlist"}
            })

        # 4. Trust and Risk scores check
        trust_score = fields.get("merchant_trust_score")
        if trust_score is not None:
            try:
                f_trust = float(trust_score)
                if f_trust < config.min_allowed_trust_score:
                    evidence.append({
                        "type": "LowMerchantTrustScore",
                        "severity": "HIGH",
                        "title": "Low Merchant Trust Score",
                        "description": f"Merchant trust index ({f_trust:.2f}) is below the acceptable safety threshold of {config.min_allowed_trust_score:.2f}.",
                        "confidence": 0.88,
                        "source": "InternalRiskEngineProvider",
                        "metadata": {"trust_score": f_trust, "threshold": config.min_allowed_trust_score}
                    })
            except ValueError:
                pass

        risk_score = fields.get("merchant_risk_score") or fields.get("merchant_risk")
        if risk_score is not None:
            try:
                f_risk = float(risk_score)
                if f_risk > config.max_allowed_risk_score:
                    evidence.append({
                        "type": "CompromisedMerchantReputation",
                        "severity": "HIGH",
                        "title": "Compromised Merchant Reputation Score",
                        "description": f"Merchant risk reputation score ({f_risk:.2f}) exceeds system safety threshold ({config.max_allowed_risk_score:.2f}).",
                        "confidence": 0.90,
                        "source": "InternalRiskEngineProvider",
                        "metadata": {"risk_score": f_risk, "threshold": config.max_allowed_risk_score}
                    })
            except ValueError:
                pass

        # 5. Dispute scores check
        dispute_score = fields.get("merchant_dispute_score")
        if dispute_score is not None:
            try:
                f_dispute = float(dispute_score)
                if f_dispute > config.max_dispute_score:
                    evidence.append({
                        "type": "ElevatedMerchantDisputes",
                        "severity": "MEDIUM",
                        "title": "Elevated Customer Dispute Score",
                        "description": f"Merchant customer dispute score of {f_dispute:.2f} is higher than the max limit of {config.max_dispute_score:.2f}.",
                        "confidence": 0.80,
                        "source": "InternalRiskEngineProvider",
                        "metadata": {"dispute_score": f_dispute, "threshold": config.max_dispute_score}
                    })
            except ValueError:
                pass

        # 6. Previous investigations check
        prev_cases = fields.get("merchant_previous_investigations") or fields.get("merchant_previous_fraud_cases")
        if prev_cases is not None:
            try:
                i_cases = int(prev_cases)
                if i_cases > 0:
                    evidence.append({
                        "type": "PreviousFraudInvolvement",
                        "severity": "MEDIUM",
                        "title": "Prior Investigation Involvement",
                        "description": f"Merchant registry shows involvement in {i_cases} previous investigations.",
                        "confidence": 0.85,
                        "source": "InternalRiskEngineProvider",
                        "metadata": {"previous_cases": i_cases}
                    })
            except ValueError:
                pass

        return evidence


class OFACSanctionProvider(ReputationProvider):
    """Adapter checking compliance registries, Office of Foreign Assets Control (OFAC) sanctions, and Anti-Money Laundering (AML)."""
    
    def check_reputation(self, merchant_id: str, fields: Dict[str, Any], config: MerchantAgentConfig) -> List[Dict[str, Any]]:
        evidence = []
        
        # 1. Sanctions match check
        if fields.get("merchant_sanctions_match") is True:
            evidence.append({
                "type": "SanctionsRegistryMatch",
                "severity": "CRITICAL",
                "title": "Sanctioned Entity Match",
                "description": f"Merchant '{merchant_id}' triggered a match on active sanctions / OFAC watchlists.",
                "confidence": 0.99,
                "source": "OFACSanctionProvider",
                "metadata": {"merchant_id": merchant_id, "source": "OFAC"}
            })

        # 2. AML Status check
        aml_status = fields.get("merchant_aml_status")
        if aml_status and str(aml_status).upper() not in {"ACTIVE", "PASSED", "CLEAN", "SUCCESS"}:
            evidence.append({
                "type": "AMLComplianceFailure",
                "severity": "HIGH",
                "title": "AML Compliance Failure",
                "description": f"Merchant AML compliance check is invalid or suspended (status: '{aml_status}').",
                "confidence": 0.95,
                "source": "OFACSanctionProvider",
                "metadata": {"aml_status": aml_status}
            })

        return evidence


class ExternalIntelligenceProvider(ReputationProvider):
    """Adapter verifying external threat scoring databases, KYC completion, and regulatory action feeds."""
    
    def check_reputation(self, merchant_id: str, fields: Dict[str, Any], config: MerchantAgentConfig) -> List[Dict[str, Any]]:
        evidence = []
        
        # 1. Compliance status check
        comp_status = fields.get("merchant_compliance_status")
        if comp_status and str(comp_status).upper() not in {"COMPLIANT", "PASSED", "ACTIVE"}:
            evidence.append({
                "type": "RegulatoryComplianceViolation",
                "severity": "HIGH",
                "title": "Regulatory Compliance Suspicion",
                "description": f"Merchant '{merchant_id}' is flagged as non-compliant or suspended (status: '{comp_status}').",
                "confidence": 0.90,
                "source": "ExternalIntelligenceProvider",
                "metadata": {"compliance_status": comp_status}
            })

        # 2. External intelligence score
        ext_score = fields.get("merchant_external_reputation_score")
        if ext_score is not None:
            try:
                f_ext = float(ext_score)
                # Let's flag if external reputation score falls below 0.60
                if f_ext < 0.60:
                    evidence.append({
                        "type": "ExternalReputationWarning",
                        "severity": "MEDIUM",
                        "title": "External Threat Score Warning",
                        "description": f"External intelligence services evaluated a low reputation score of {f_ext:.2f} for this merchant terminal.",
                        "confidence": 0.85,
                        "source": "ExternalIntelligenceProvider",
                        "metadata": {"external_reputation_score": f_ext}
                    })
            except ValueError:
                pass

        # 3. Regulatory flags check
        reg_flags = fields.get("merchant_regulatory_flags")
        if reg_flags:
            evidence.append({
                "type": "RegulatoryActionWarning",
                "severity": "MEDIUM",
                "title": "Regulatory Compliance Watchlist Flag",
                "description": f"Merchant has active warnings or actions logged by regulators: {reg_flags}.",
                "confidence": 0.80,
                "source": "ExternalIntelligenceProvider",
                "metadata": {"regulatory_flags": reg_flags}
            })

        return evidence


class MerchantReputationAnalyzer:
    """Verifies merchant status against reputation blacklists, whitelists, compliance, and threat intelligence providers."""

    def __init__(self, config: MerchantAgentConfig, providers: Optional[List[ReputationProvider]] = None) -> None:
        """Initializes the MerchantReputationAnalyzer with configuration and adapters."""
        self.config = config
        self.providers = providers if providers is not None else [
            InternalRiskEngineProvider(),
            OFACSanctionProvider(),
            ExternalIntelligenceProvider()
        ]

    def analyze(self, context_or_tx_data: Any, history: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Performs reputation risk checks across all loaded providers.
        
        Supports receiving either:
          - InvestigationContext (full enterprise mode)
          - Dict[str, Any] (legacy tx_data mode for backward compatibility)
        """
        logger.info("Analyzer started")
        
        is_context_mode = isinstance(context_or_tx_data, InvestigationContext)
        
        # Safely extract merchant and transaction data depending on the input type
        if is_context_mode:
            tx_data = context_or_tx_data.transaction_data or {}
            # Allow extracting profile either from transaction_data or metadata
            merchant_reputation = tx_data.get("merchant_profile") or tx_data or {}
        else:
            tx_data = context_or_tx_data or {}
            merchant_reputation = tx_data

        # Safely extract merchant ID
        merchant_id = (
            merchant_reputation.get("merchant_id") 
            or merchant_reputation.get("merchant") 
            or tx_data.get("merchant_id") 
            or tx_data.get("merchant")
        )
        
        logger.info("Reputation data loaded for merchant: %s", merchant_id)

        evidence: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        if not merchant_id:
            logger.warning("No merchant_id found in reputation metrics payload")
            if is_context_mode:
                return {
                    "evidence": [],
                    "confidence_score": 1.0,
                    "metadata": {"error": "Missing merchant_id"},
                    "recommendations": ["Increase monitoring"]
                }
            return []

        # Run reputation analysis across providers
        for provider in self.providers:
            prov_evidence = provider.check_reputation(merchant_id, merchant_reputation, self.config)
            evidence.extend(prov_evidence)
            
        logger.info("Provider checks completed")

        # Check triggers for custom logic and confidence score calculations
        is_whitelisted = any(ev["type"] == "WhitelistedMerchantExemption" for ev in evidence)
        is_blacklisted = any(ev["type"] == "BlacklistedMerchant" for ev in evidence)
        is_sanctions_match = any(ev["type"] == "SanctionsRegistryMatch" for ev in evidence)
        is_watchlisted = any(ev["type"] == "WatchlistedMerchant" for ev in evidence)
        is_low_trust = any(ev["type"] == "LowMerchantTrustScore" for ev in evidence)
        is_compliance_violation = any(ev["type"] == "RegulatoryComplianceViolation" for ev in evidence)

        # Compute trust/confidence score
        trust_score = 1.0
        if is_whitelisted:
            trust_score = 1.0
        else:
            if is_sanctions_match or is_blacklisted:
                trust_score *= 0.1
            if is_watchlisted:
                trust_score *= 0.6
            if is_low_trust:
                trust_score *= 0.7
            if is_compliance_violation:
                trust_score *= 0.75
                
            if len(evidence) > 0:
                multiplier = 0.9**len(evidence)
                trust_score *= multiplier

        trust_score = max(0.1, min(1.0, trust_score))

        # Recommendations mapping
        if is_whitelisted:
            recommendations.append("Approve merchant")
        if is_sanctions_match or is_blacklisted:
            recommendations.append("Suspend merchant")
            recommendations.append("Freeze settlement")
            recommendations.append("Escalate investigation")
        if is_watchlisted or is_compliance_violation:
            recommendations.append("Manual compliance review")
            recommendations.append("Increase monitoring")
            
        if not recommendations:
            recommendations.append("Increase monitoring")

        logger.info("Evidence generated: %d items", len(evidence))
        logger.info("Analyzer completed")

        if is_context_mode:
            return {
                "evidence": evidence,
                "confidence_score": trust_score,
                "metadata": {
                    "is_whitelisted": is_whitelisted,
                    "is_blacklisted": is_blacklisted,
                    "is_sanctions_match": is_sanctions_match,
                    "checks_completed": ["whitelist_blacklist", "watchlist", "scores_evaluation", "sanctions_check", "aml_audit", "compliance_audit"],
                    "alerts_triggered_count": len(evidence)
                },
                "recommendations": list(set(recommendations))
            }
        
        # Legacy/Agent mode returns raw list of evidence dicts
        return evidence
export_analyzer = MerchantReputationAnalyzer
