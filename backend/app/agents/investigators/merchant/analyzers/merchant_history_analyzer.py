import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.models.investigation_context import InvestigationContext

logger = logging.getLogger("app.agents.investigators.merchant.analyzers.merchant_history_analyzer")

class MerchantHistoryAnalyzer:
    """Audits merchant historic fraud metrics, chargeback ratios, dispute frequencies, and consistency trends."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        """Initializes the MerchantHistoryAnalyzer with configuration thresholds."""
        self.config = config

    def analyze(self, context_or_tx_data: Any, history: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Performs behavioral analysis of merchant transaction history metrics.
        
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
            merchant_history = tx_data.get("merchant_history") or metadata.get("merchant_history") or tx_data or {}
        else:
            tx_data = context_or_tx_data or {}
            merchant_history = tx_data
            metadata = {}

        # Safely extract merchant ID
        merchant_id = (
            merchant_history.get("merchant_id") 
            or merchant_history.get("merchant") 
            or tx_data.get("merchant_id") 
            or tx_data.get("merchant")
        )
        
        logger.info("Historical data loaded for merchant: %s", merchant_id)

        evidence: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        if not merchant_id:
            logger.warning("No merchant_id found in history payload")
            if is_context_mode:
                return {
                    "evidence": [],
                    "confidence_score": 0.0,
                    "metadata": {"error": "Missing merchant_id"},
                    "recommendations": ["Increase monitoring"]
                }
            return []

        # Extract history metrics safely with default fallbacks
        total_tx = int(merchant_history.get("total_transactions") or 0)
        successful_tx = int(merchant_history.get("successful_transactions") or 0)
        failed_tx = int(merchant_history.get("failed_transactions") or 0)
        chargebacks = int(merchant_history.get("chargebacks") or 0)
        refunds = int(merchant_history.get("refunds") or 0)
        fraud_cases = int(merchant_history.get("fraud_cases") or 0)
        customer_disputes = int(merchant_history.get("customer_disputes") or 0)
        daily_vol = float(merchant_history.get("daily_transaction_volume") or 0.0)
        monthly_vol = float(merchant_history.get("monthly_transaction_volume") or 0.0)
        last_tx_date = merchant_history.get("last_transaction_date")

        # 1. Limited History Check
        if total_tx < self.config.min_established_transactions:
            evidence.append({
                "type": "LimitedMerchantHistory",
                "severity": "MEDIUM",
                "title": "Limited Merchant Transaction History",
                "description": f"Merchant '{merchant_id}' has limited historical transaction volume ({total_tx} transactions).",
                "confidence": 0.80,
                "source": "MerchantHistoryAnalyzer",
                "metadata": {"total_transactions": total_tx}
            })

        # Calculate ratios if transactions exist
        chargeback_rate = 0.0
        refund_rate = 0.0
        dispute_rate = 0.0
        
        if total_tx > 0:
            chargeback_rate = chargebacks / total_tx
            refund_rate = refunds / total_tx
            dispute_rate = customer_disputes / total_tx

        # 2. Chargeback Ratio Check
        # Support either legacy fields (merchant_chargeback_rate) or calculated
        legacy_cb_rate = float(merchant_history.get("merchant_chargeback_rate") or 0.0)
        actual_cb_rate = max(chargeback_rate, legacy_cb_rate)
        if actual_cb_rate > self.config.high_chargeback_rate_threshold:
            evidence.append({
                "type": "HighMerchantChargebackRate",
                "severity": "HIGH",
                "title": "High Merchant Chargeback Rate",
                "description": f"Merchant '{merchant_id}' chargeback rate of {actual_cb_rate:.2%} exceeds system threshold of {self.config.high_chargeback_rate_threshold:.2%}.",
                "confidence": 0.92,
                "source": "MerchantHistoryAnalyzer",
                "metadata": {"chargeback_rate": actual_cb_rate, "chargebacks": chargebacks, "total_transactions": total_tx}
            })

        # 3. Refund Ratio Check
        if refund_rate > self.config.high_refund_rate_threshold:
            evidence.append({
                "type": "HighMerchantRefundRate",
                "severity": "HIGH",
                "title": "High Merchant Refund Rate",
                "description": f"Merchant '{merchant_id}' has a disproportionately high refund rate of {refund_rate:.2%} (threshold: {self.config.high_refund_rate_threshold:.2%}).",
                "confidence": 0.85,
                "source": "MerchantHistoryAnalyzer",
                "metadata": {"refund_rate": refund_rate, "refunds": refunds, "total_transactions": total_tx}
            })

        # 4. Fraud History Check
        # Support either legacy (merchant_fraud_rate) or explicit fraud_cases
        legacy_fraud_rate = float(merchant_history.get("merchant_fraud_rate") or 0.0)
        has_fraud_history = fraud_cases > 0 or legacy_fraud_rate > self.config.high_fraud_rate_threshold
        if has_fraud_history:
            rate_desc = f"fraud rate: {legacy_fraud_rate:.2%}" if legacy_fraud_rate > 0 else f"{fraud_cases} previous cases"
            evidence.append({
                "type": "HighMerchantFraudRate",
                "severity": "HIGH",
                "title": "Historical Merchant Fraud Cases",
                "description": f"Merchant '{merchant_id}' has a history of elevated fraud activity ({rate_desc}).",
                "confidence": 0.95,
                "source": "MerchantHistoryAnalyzer",
                "metadata": {"fraud_cases": fraud_cases, "fraud_rate": legacy_fraud_rate}
            })

        # 5. Customer Dispute Frequency Check
        if dispute_rate > self.config.high_dispute_rate_threshold:
            evidence.append({
                "type": "HighMerchantDisputeRate",
                "severity": "HIGH",
                "title": "High Customer Dispute Rate",
                "description": f"Merchant '{merchant_id}' customer dispute rate is elevated: {dispute_rate:.2%} (threshold: {self.config.high_dispute_rate_threshold:.2%}).",
                "confidence": 0.90,
                "source": "MerchantHistoryAnalyzer",
                "metadata": {"dispute_rate": dispute_rate, "customer_disputes": customer_disputes, "total_transactions": total_tx}
            })

        # 6. Merchant Inactivity Check
        if last_tx_date:
            try:
                if isinstance(last_tx_date, (datetime, date)):
                    last_dt = last_tx_date
                else:
                    last_dt = datetime.fromisoformat(str(last_tx_date)).date()
                
                inactive_days = (date.today() - (last_dt.date() if isinstance(last_dt, datetime) else last_dt)).days
                if inactive_days > self.config.inactivity_days_threshold:
                    evidence.append({
                        "type": "InactiveMerchantHistory",
                        "severity": "MEDIUM",
                        "title": "Prolonged Merchant Inactivity",
                        "description": f"Merchant '{merchant_id}' was inactive for {inactive_days} days since last transaction (threshold: {self.config.inactivity_days_threshold} days).",
                        "confidence": 0.80,
                        "source": "MerchantHistoryAnalyzer",
                        "metadata": {"inactive_days": inactive_days, "last_transaction_date": str(last_tx_date)}
                    })
            except Exception as e:
                logger.error("Failed to parse last_transaction_date %s: %s", last_tx_date, str(e))

        # 7. Growth & Historical Transaction Consistency Checks
        if successful_tx + failed_tx > total_tx:
            evidence.append({
                "type": "TransactionConsistencyAnomaly",
                "severity": "MEDIUM",
                "title": "Historical Transaction Consistency Anomaly",
                "description": f"Merchant '{merchant_id}' has inconsistent transaction history records: sum of successful ({successful_tx}) and failed ({failed_tx}) transactions exceeds total count ({total_tx}).",
                "confidence": 0.85,
                "source": "MerchantHistoryAnalyzer",
                "metadata": {"successful": successful_tx, "failed": failed_tx, "total": total_tx}
            })
            
        if daily_vol > monthly_vol:
            evidence.append({
                "type": "TransactionConsistencyAnomaly",
                "severity": "MEDIUM",
                "title": "Historical Transaction Consistency Anomaly",
                "description": f"Merchant '{merchant_id}' shows anomalous growth trend: daily volume (${daily_vol:,.2f}) exceeds monthly volume (${monthly_vol:,.2f}).",
                "confidence": 0.85,
                "source": "MerchantHistoryAnalyzer",
                "metadata": {"daily_volume": daily_vol, "monthly_volume": monthly_vol}
            })

        logger.info("History analyzed")

        # Compute trust/confidence score
        trust_score = 1.0
        if actual_cb_rate > self.config.high_chargeback_rate_threshold:
            trust_score *= 0.5
        if refund_rate > self.config.high_refund_rate_threshold:
            trust_score *= 0.7
        if dispute_rate > self.config.high_dispute_rate_threshold:
            trust_score *= 0.8
        if has_fraud_history:
            trust_score *= 0.4
            
        trust_score = max(0.1, min(1.0, trust_score))

        # Map recommendations based on audits
        if actual_cb_rate > self.config.high_chargeback_rate_threshold:
            recommendations.append("Reduce transaction limits")
            recommendations.append("Require manual review")
        if has_fraud_history:
            recommendations.append("Require manual review")
            recommendations.append("Temporary merchant verification")
        if refund_rate > self.config.high_refund_rate_threshold:
            recommendations.append("Increase monitoring")
            recommendations.append("Require manual review")
        if total_tx < self.config.min_established_transactions:
            recommendations.append("Increase monitoring")
            
        if not recommendations:
            recommendations.append("Increase monitoring")  # standard proactive default

        logger.info("Evidence generated: %d items", len(evidence))
        logger.info("Analyzer completed")

        if is_context_mode:
            return {
                "evidence": evidence,
                "confidence_score": trust_score,
                "metadata": {
                    "chargeback_rate": actual_cb_rate,
                    "refund_rate": refund_rate,
                    "dispute_rate": dispute_rate,
                    "total_transactions": total_tx,
                    "checks_completed": ["transaction_volume", "chargeback_ratio", "refund_ratio", "fraud_history", "disputes", "inactivity", "consistency"]
                },
                "recommendations": list(set(recommendations))
            }
        
        # Legacy/Agent mode returns raw list of evidence dicts
        return evidence
export_analyzer = MerchantHistoryAnalyzer
