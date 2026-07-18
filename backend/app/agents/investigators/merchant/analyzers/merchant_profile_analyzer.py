import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.models.investigation_context import InvestigationContext

logger = logging.getLogger("app.agents.investigators.merchant.analyzers.merchant_profile_analyzer")

class MerchantProfileAnalyzer:
    """Evaluates merchant profile registration, verification status, and profile completeness metrics."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        """Initializes the MerchantProfileAnalyzer with configuration thresholds."""
        self.config = config

    def analyze(self, context_or_tx_data: Any, history: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Performs static analysis of merchant profile information.
        
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
            merchant_profile = tx_data.get("merchant_profile") or tx_data or {}
        else:
            tx_data = context_or_tx_data or {}
            merchant_profile = tx_data
            metadata = {}

        # Safely extract merchant ID
        merchant_id = (
            merchant_profile.get("merchant_id") 
            or merchant_profile.get("merchant") 
            or tx_data.get("merchant_id") 
            or tx_data.get("merchant")
        )
        
        logger.info("Profile loaded for merchant: %s", merchant_id)

        evidence: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        if not merchant_id:
            logger.warning("No merchant_id found in profile")
            if is_context_mode:
                return {
                    "evidence": [],
                    "confidence_score": 0.0,
                    "metadata": {"error": "Missing merchant_id"},
                    "recommendations": ["Verify merchant profile"]
                }
            return []

        # 1. Merchant Completeness Checks
        missing_required = []
        for field in self.config.required_profile_fields:
            if not merchant_profile.get(field):
                missing_required.append(field)
                
        if missing_required:
            evidence.append({
                "type": "MissingRequiredMerchantFields",
                "severity": "HIGH",
                "title": "Missing Required Merchant Profile Fields",
                "description": f"Merchant profile '{merchant_id}' is missing required fields: {', '.join(missing_required)}.",
                "confidence": 0.90,
                "source": "MerchantProfileAnalyzer",
                "metadata": {"missing_required_fields": missing_required}
            })

        missing_important = []
        for field in self.config.important_profile_fields:
            if not merchant_profile.get(field):
                missing_important.append(field)
                
        if missing_important:
            evidence.append({
                "type": "MissingImportantMerchantFields",
                "severity": "MEDIUM",
                "title": "Missing Important Merchant Profile Fields",
                "description": f"Merchant profile '{merchant_id}' is missing important fields: {', '.join(missing_important)}.",
                "confidence": 0.70,
                "source": "MerchantProfileAnalyzer",
                "metadata": {"missing_important_fields": missing_important}
            })

        # 2. Merchant Verification Status
        # If explicitly set to False, or 'unverified'
        is_verified = merchant_profile.get("merchant_verified")
        if is_verified is False or is_verified == "unverified" or not merchant_profile.get("merchant_verified", True):
            evidence.append({
                "type": "UnverifiedMerchantProfile",
                "severity": "HIGH",
                "title": "Unverified Merchant Profile",
                "description": f"Merchant '{merchant_id}' profile is unverified or lacks valid business registry credentials.",
                "confidence": 0.90,
                "source": "MerchantProfileAnalyzer",
                "metadata": {"verification_status": is_verified}
            })

        # 3. Merchant Age (Recently registered merchants)
        reg_date = merchant_profile.get("merchant_registration_date")
        merchant_age_days = merchant_profile.get("merchant_age") or merchant_profile.get("merchant_age_days")
        
        is_new = merchant_profile.get("merchant_is_new", False)
        
        # Calculate age if registration date is provided
        if reg_date:
            try:
                if isinstance(reg_date, (datetime, date)):
                    reg_dt = reg_date
                else:
                    reg_dt = datetime.fromisoformat(str(reg_date)).date()
                
                # Compute difference in days
                delta = date.today() - (reg_dt.date() if isinstance(reg_dt, datetime) else reg_dt)
                merchant_age_days = delta.days
            except Exception as e:
                logger.error("Failed to parse merchant_registration_date %s: %s", reg_date, str(e))

        if is_new or (merchant_age_days is not None and merchant_age_days < self.config.recently_registered_days):
            age_str = f"{merchant_age_days} days" if merchant_age_days is not None else "unknown days"
            evidence.append({
                "type": "NewMerchantProfile",
                "severity": "MEDIUM",
                "title": "Recently Registered Merchant",
                "description": f"Merchant '{merchant_id}' is a newly registered terminal (registered {age_str} ago).",
                "confidence": 0.85,
                "source": "MerchantProfileAnalyzer",
                "metadata": {"merchant_age_days": merchant_age_days}
            })

        # 4. Inactive Merchant Status
        status = merchant_profile.get("merchant_status")
        if status and status.upper() not in self.config.active_merchant_statuses:
            evidence.append({
                "type": "InactiveMerchantStatus",
                "severity": "HIGH",
                "title": "Inactive Merchant Status",
                "description": f"Merchant '{merchant_id}' is currently marked as inactive or suspended (status: '{status}').",
                "confidence": 0.95,
                "source": "MerchantProfileAnalyzer",
                "metadata": {"merchant_status": status}
            })

        # 5. Country Consistency
        country = merchant_profile.get("merchant_country")
        if country:
            # Code structure check (ISO 2-letter or 3-letter codes)
            if len(str(country)) < 2 or len(str(country)) > 3:
                evidence.append({
                    "type": "InvalidMerchantCountry",
                    "severity": "MEDIUM",
                    "title": "Invalid Merchant Country Code",
                    "description": f"Merchant '{merchant_id}' has an invalid country code structure: '{country}'.",
                    "confidence": 0.80,
                    "source": "MerchantProfileAnalyzer",
                    "metadata": {"country": country}
                })
            
            # Cross-reference with transaction country if present
            tx_country = tx_data.get("location_country") or tx_data.get("country")
            if tx_country and str(country).upper() != str(tx_country).upper():
                evidence.append({
                    "type": "CountryInconsistency",
                    "severity": "MEDIUM",
                    "title": "Merchant Country Inconsistency",
                    "description": f"Merchant country registry '{country}' does not match current transaction execution country '{tx_country}'.",
                    "confidence": 0.85,
                    "source": "MerchantProfileAnalyzer",
                    "metadata": {"merchant_country": country, "transaction_country": tx_country}
                })

        # 6. Category Consistency
        category = merchant_profile.get("merchant_category")
        if category:
            if str(category).lower() in self.config.invalid_merchant_categories:
                evidence.append({
                    "type": "InvalidMerchantCategory",
                    "severity": "MEDIUM",
                    "title": "Invalid Merchant Category",
                    "description": f"Merchant '{merchant_id}' category registration is invalid or generic: '{category}'.",
                    "confidence": 0.80,
                    "source": "MerchantProfileAnalyzer",
                    "metadata": {"category": category}
                })
            elif str(category).lower() in self.config.high_risk_categories:
                evidence.append({
                    "type": "HighRiskMerchantCategory",
                    "severity": "MEDIUM",
                    "title": "High-Risk Merchant Category",
                    "description": f"Merchant '{merchant_id}' belongs to high-risk business classification: '{category}'.",
                    "confidence": 0.75,
                    "source": "MerchantProfileAnalyzer",
                    "metadata": {"category": category}
                })

        # 7. Business Type Consistency
        m_type = merchant_profile.get("merchant_type")
        if category and m_type:
            # Flag if a sole proprietor / micro merchant is registered in extreme high-risk categories like crypto exchanges
            if str(category).lower() in {"crypto_exchange", "jewelry"} and str(m_type).upper() in {"INDIVIDUAL", "MICRO", "SOLE_PROPRIETORSHIP"}:
                evidence.append({
                    "type": "BusinessTypeInconsistency",
                    "severity": "MEDIUM",
                    "title": "Merchant Business Type Inconsistency",
                    "description": f"Merchant '{merchant_id}' is operating as '{m_type}' but registered in high-risk category '{category}'.",
                    "confidence": 0.80,
                    "source": "MerchantProfileAnalyzer",
                    "metadata": {"category": category, "merchant_type": m_type}
                })

        logger.info("Checks completed")

        # Compute legitimacy/completeness confidence score
        total_fields = len(self.config.required_profile_fields) + len(self.config.important_profile_fields)
        filled_fields = sum(1 for f in self.config.required_profile_fields if merchant_profile.get(f)) + \
                        sum(1 for f in self.config.important_profile_fields if merchant_profile.get(f))
        
        completeness_score = filled_fields / total_fields if total_fields > 0 else 1.0
        
        confidence_score = completeness_score
        # Deprecate confidence if major anomalies are found
        if is_verified is False or is_verified == "unverified" or not merchant_profile.get("merchant_verified", True):
            confidence_score *= 0.5
        if status and status.upper() not in self.config.active_merchant_statuses:
            confidence_score *= 0.3
            
        confidence_score = max(0.1, min(1.0, confidence_score))

        # Map recommendations based on checks
        if missing_required:
            recommendations.append("Review merchant onboarding")
            recommendations.append("Require additional KYC")
        if is_verified is False or is_verified == "unverified" or not merchant_profile.get("merchant_verified", True):
            recommendations.append("Require additional KYC")
            recommendations.append("Verify merchant profile")
        if status and status.upper() not in self.config.active_merchant_statuses:
            recommendations.append("Manual verification")
            recommendations.append("Review merchant onboarding")
        if reg_date and (merchant_age_days is not None and merchant_age_days < self.config.recently_registered_days):
            recommendations.append("Review merchant onboarding")
            
        if not recommendations:
            recommendations.append("Verify merchant profile")  # standard proactive fallback

        logger.info("Evidence generated: %d items", len(evidence))
        logger.info("Analyzer completed")

        if is_context_mode:
            return {
                "evidence": evidence,
                "confidence_score": confidence_score,
                "metadata": {
                    "completeness_score": completeness_score,
                    "missing_required": missing_required,
                    "missing_important": missing_important,
                    "merchant_id": merchant_id,
                    "checks_completed": ["completeness", "verification", "age", "status", "country", "category", "business_type"]
                },
                "recommendations": list(set(recommendations))
            }
        
        # Legacy/Agent mode returns raw list of evidence dicts
        return evidence
