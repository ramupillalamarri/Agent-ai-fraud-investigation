import logging
from typing import Dict, Any, List, Optional
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.models.investigation_context import InvestigationContext

logger = logging.getLogger("app.agents.investigators.merchant.analyzers.merchant_category_analyzer")

class MerchantCategoryAnalyzer:
    """Evaluates merchant category classifications, high-risk industries, transaction norms, and customer purchase consistency."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        """Initializes the MerchantCategoryAnalyzer with configuration thresholds."""
        self.config = config

    def analyze(self, context_or_tx_data: Any, history: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Performs category risk analysis on merchant classification.
        
        Supports receiving either:
          - InvestigationContext (full enterprise mode)
          - Dict[str, Any] (legacy tx_data mode for backward compatibility)
        """
        logger.info("Analyzer started")
        
        is_context_mode = isinstance(context_or_tx_data, InvestigationContext)
        
        # Safely extract merchant and transaction data depending on the input type
        if is_context_mode:
            tx_data = context_or_tx_data.transaction_data or {}
            metadata = context_or_tx_data.metadata or {}
            # Allow extracting profile either from transaction_data or metadata
            merchant_category_info = tx_data.get("merchant_profile") or tx_data or {}
            cust_history = context_or_tx_data.shared_memory.get("customer_history") or metadata.get("customer_history") or []
        else:
            tx_data = context_or_tx_data or {}
            merchant_category_info = tx_data
            cust_history = history or []

        # Safely extract merchant category
        category = (
            merchant_category_info.get("merchant_category") 
            or merchant_category_info.get("category") 
            or tx_data.get("merchant_category") 
            or tx_data.get("category")
        )
        
        logger.info("Category identified: %s", category)

        evidence: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        if not category:
            logger.warning("No merchant category found in payload")
            if is_context_mode:
                return {
                    "evidence": [],
                    "confidence_score": 1.0,
                    "metadata": {"error": "Missing merchant_category"},
                    "recommendations": ["Increase monitoring"]
                }
            return []

        normalized_cat = category.lower().strip()
        weight = self.config.category_weights.get(normalized_cat, 0.70)
        
        # 1. Category Risk Level Audits
        is_high_risk = normalized_cat in self.config.high_risk_categories
        is_medium_risk = normalized_cat in self.config.medium_risk_categories
        is_restricted = normalized_cat in self.config.restricted_categories

        if is_restricted:
            evidence.append({
                "type": "RestrictedMerchantCategory",
                "severity": "CRITICAL",
                "title": "Restricted Merchant Category",
                "description": f"Merchant category '{category}' is restricted by system guidelines.",
                "confidence": 0.99,
                "source": "MerchantCategoryAnalyzer",
                "metadata": {"category": category, "risk_type": "restricted"}
            })
        elif is_high_risk:
            evidence.append({
                "type": "HighRiskMerchantCategory",
                "severity": "HIGH" if weight >= 0.85 else "MEDIUM",
                "title": "High-Risk Merchant Category",
                "description": f"Merchant category '{category}' is classified as a high-risk industry (weight: {weight:.2f}).",
                "confidence": weight,
                "source": "MerchantCategoryAnalyzer",
                "metadata": {"category": category, "risk_type": "high_risk", "weight": weight}
            })
        elif is_medium_risk:
            evidence.append({
                "type": "MediumRiskMerchantCategory",
                "severity": "MEDIUM",
                "title": "Medium-Risk Merchant Category",
                "description": f"Merchant category '{category}' is classified as a medium-risk industry.",
                "confidence": 0.65,
                "source": "MerchantCategoryAnalyzer",
                "metadata": {"category": category, "risk_type": "medium_risk"}
            })

        # 2. Transaction Amount Category Norm Checks
        amount = tx_data.get("transaction_amount") or tx_data.get("amount")
        norm_limit = self.config.category_amount_norms.get(normalized_cat)
        has_abnormal_amount = False
        
        if amount is not None and norm_limit is not None:
            try:
                float_amount = float(amount)
                if float_amount > norm_limit:
                    has_abnormal_amount = True
                    evidence.append({
                        "type": "AbnormalCategoryAmount",
                        "severity": "MEDIUM",
                        "title": "Transaction Amount Exceeds Category Norm",
                        "description": f"Transaction amount ${float_amount:,.2f} exceeds typical category limit of ${norm_limit:,.2f} for '{category}'.",
                        "confidence": 0.80,
                        "source": "MerchantCategoryAnalyzer",
                        "metadata": {"amount": float_amount, "norm_limit": norm_limit, "category": category}
                    })
            except Exception as e:
                logger.error("Failed to parse transaction amount %s: %s", amount, str(e))

        # 3. Cross-Border Category Rules Check
        merchant_country = tx_data.get("merchant_country") or tx_data.get("country")
        location_country = tx_data.get("location_country") or tx_data.get("country")
        has_cross_border_risk = False
        
        if merchant_country and location_country and str(merchant_country).upper() != str(location_country).upper():
            if normalized_cat in self.config.cross_border_high_risk_categories:
                has_cross_border_risk = True
                evidence.append({
                    "type": "CrossBorderCategoryRisk",
                    "severity": "HIGH",
                    "title": "High-Risk Cross-Border Merchant Category",
                    "description": f"Cross-border transaction detected in high-risk merchant category '{category}' (Merchant Registry: {merchant_country}, Transaction Origin: {location_country}).",
                    "confidence": 0.85,
                    "source": "MerchantCategoryAnalyzer",
                    "metadata": {"merchant_country": merchant_country, "location_country": location_country, "category": category}
                })

        # 4. Customer History Interaction Check
        has_unexpected_category = False
        if cust_history:
            # Check if customer has previously successfully transacted in this category
            matched = False
            for hist_tx in cust_history:
                hist_cat = hist_tx.get("category") or hist_tx.get("merchant_category")
                hist_status = hist_tx.get("status", "SUCCESS")
                
                if hist_cat and hist_cat.lower().strip() == normalized_cat and hist_status.upper() in {"SUCCESS", "COMPLETED", "APPROVED"}:
                    matched = True
                    break
                    
            if not matched:
                has_unexpected_category = True
                evidence.append({
                    "type": "UnexpectedMerchantCategory",
                    "severity": "MEDIUM",
                    "title": "Unexpected Merchant Category for Customer Profile",
                    "description": f"Customer has no historical transactions matching category '{category}'.",
                    "confidence": 0.75,
                    "source": "MerchantCategoryAnalyzer",
                    "metadata": {"category": category}
                })

        logger.info("Risk evaluated")

        # Compute confidence score
        trust_score = 1.0
        if is_restricted:
            trust_score *= 0.1
        elif is_high_risk:
            trust_score *= 0.5
        elif is_medium_risk:
            trust_score *= 0.75
            
        if has_abnormal_amount:
            trust_score *= 0.8
        if has_cross_border_risk:
            trust_score *= 0.85
        if has_unexpected_category:
            trust_score *= 0.90
            
        trust_score = max(0.1, min(1.0, trust_score))

        # Recommendations mapping
        if is_restricted:
            recommendations.append("Review merchant manually")
            recommendations.append("Require additional verification")
        if is_high_risk or has_cross_border_risk:
            recommendations.append("Request customer confirmation")
            recommendations.append("Require additional verification")
        if has_abnormal_amount or has_unexpected_category:
            recommendations.append("Increase monitoring")
            recommendations.append("Require additional verification")
            
        if not recommendations:
            recommendations.append("Increase monitoring")

        logger.info("Evidence generated: %d items", len(evidence))
        logger.info("Analyzer completed")

        if is_context_mode:
            return {
                "evidence": evidence,
                "confidence_score": trust_score,
                "metadata": {
                    "category": category,
                    "weight": weight,
                    "is_high_risk": is_high_risk,
                    "is_medium_risk": is_medium_risk,
                    "is_restricted": is_restricted,
                    "checks_completed": ["category_risk", "amount_norms", "cross_border_rules", "customer_history_match"]
                },
                "recommendations": list(set(recommendations))
            }

        # Legacy mode returns raw evidence dict list
        return evidence
