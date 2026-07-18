import logging
from typing import Dict, Any, List, Optional
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.models.investigation_context import InvestigationContext

logger = logging.getLogger("app.agents.investigators.merchant.analyzers.merchant_velocity_analyzer")

class MerchantVelocityAnalyzer:
    """Analyzes merchant real-time transaction velocities, spikes, failure rates, card testing, and growth trends."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        """Initializes the MerchantVelocityAnalyzer with configuration thresholds."""
        self.config = config

    def analyze(self, context_or_tx_data: Any, history: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Performs real-time velocity audit checks on current merchant metrics.
        
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
            merchant_metrics = tx_data.get("merchant_profile") or tx_data or {}
            history_list = context_or_tx_data.shared_memory.get("customer_history") or metadata.get("customer_history") or []
        else:
            tx_data = context_or_tx_data or {}
            merchant_metrics = tx_data
            history_list = history or []

        # Safely extract merchant ID
        merchant_id = (
            merchant_metrics.get("merchant_id") 
            or merchant_metrics.get("merchant") 
            or tx_data.get("merchant_id") 
            or tx_data.get("merchant")
        )
        
        logger.info("Velocity metrics loaded for merchant: %s", merchant_id)

        evidence: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        if not merchant_id:
            logger.warning("No merchant_id found in velocity metrics payload")
            if is_context_mode:
                return {
                    "evidence": [],
                    "confidence_score": 1.0,
                    "metadata": {"error": "Missing merchant_id"},
                    "recommendations": ["Increase monitoring"]
                }
            return []

        # Extract values
        tx_minute = int(merchant_metrics.get("transactions_last_minute") or 0)
        tx_5min = int(merchant_metrics.get("transactions_last_5_minutes") or 0)
        tx_hour = int(merchant_metrics.get("transactions_last_hour") or 0)
        tx_day = int(merchant_metrics.get("transactions_last_day") or 0)
        
        avg_hour = float(merchant_metrics.get("average_transactions_per_hour") or 0.0)
        avg_day = float(merchant_metrics.get("average_transactions_per_day") or 0.0)
        
        amount = float(merchant_metrics.get("current_transaction_amount") or tx_data.get("amount") or 0.0)
        avg_amount = float(merchant_metrics.get("average_transaction_amount") or 0.0)
        
        failed_hour = int(merchant_metrics.get("failed_transactions_last_hour") or 0)
        success_hour = int(merchant_metrics.get("successful_transactions_last_hour") or 0)
        
        refunds_day = int(merchant_metrics.get("refunds_last_day") or 0)
        chargebacks_week = int(merchant_metrics.get("chargebacks_last_week") or 0)
        
        new_cust_hour = int(merchant_metrics.get("new_customers_last_hour") or 0)
        repeat_cust_hour = int(merchant_metrics.get("repeat_customers_last_hour") or 0)

        # 1. Transaction Burst Detection (5 mins count burst)
        # Expected average in 5 mins is (average_per_hour / 12)
        expected_5min = (avg_hour / 12.0) if avg_hour > 0 else 1.0
        if tx_5min > self.config.velocity_burst_multiplier * expected_5min and tx_5min > 10:
            evidence.append({
                "type": "MerchantVelocitySpike",
                "severity": "HIGH",
                "title": "Sudden Transaction Count Burst",
                "description": f"Merchant transaction rate spike: processed {tx_5min} transactions in 5 minutes (expected average: {expected_5min:.1f}).",
                "confidence": 0.85,
                "source": "MerchantVelocityAnalyzer",
                "metadata": {"transactions_5min": tx_5min, "expected_5min": expected_5min}
            })

        # 2. Sudden Increase in Transaction Value
        has_amount_deviation = False
        if avg_amount > 0 and amount > self.config.amount_deviation_multiplier * avg_amount:
            has_amount_deviation = True
            evidence.append({
                "type": "ExcessiveMerchantAmount",
                "severity": "HIGH",
                "title": "Abnormal Transaction Amount Deviation",
                "description": f"Current transaction amount (${amount:,.2f}) deviates significantly from historical average of ${avg_amount:,.2f}.",
                "confidence": 0.88,
                "source": "MerchantVelocityAnalyzer",
                "metadata": {"current_amount": amount, "average_amount": avg_amount}
            })

        # 3. High Failure Rate Check
        has_high_failure = False
        total_hour = failed_hour + success_hour
        if total_hour > 5:
            failed_tx_rate = failed_hour / total_hour
            if failed_tx_rate > self.config.max_failed_tx_rate:
                has_high_failure = True
                evidence.append({
                    "type": "HighFailedTransactionRate",
                    "severity": "HIGH",
                    "title": "High Transaction Failure Rate",
                    "description": f"Merchant is experiencing a high transaction failure rate of {failed_tx_rate:.2%} in the last hour (failed: {failed_hour}, total: {total_hour}).",
                    "confidence": 0.90,
                    "source": "MerchantVelocityAnalyzer",
                    "metadata": {"failed_rate": failed_tx_rate, "failed": failed_hour, "total": total_hour}
                })

        # 4. Spike in Refunds
        has_refund_spike = False
        if refunds_day > self.config.max_refunds_last_day:
            has_refund_spike = True
            evidence.append({
                "type": "RefundSpikeDetected",
                "severity": "HIGH",
                "title": "Merchant Refund Spike",
                "description": f"Refund count of {refunds_day} in the last 24 hours exceeds threshold of {self.config.max_refunds_last_day}.",
                "confidence": 0.85,
                "source": "MerchantVelocityAnalyzer",
                "metadata": {"refunds_last_day": refunds_day, "limit": self.config.max_refunds_last_day}
            })

        # 5. Spike in Chargebacks
        has_cb_spike = False
        if chargebacks_week > self.config.max_chargebacks_last_week:
            has_cb_spike = True
            evidence.append({
                "type": "ChargebackSpikeDetected",
                "severity": "HIGH",
                "title": "Merchant Chargeback Spike",
                "description": f"Chargeback count of {chargebacks_week} in the last week exceeds threshold of {self.config.max_chargebacks_last_week}.",
                "confidence": 0.92,
                "source": "MerchantVelocityAnalyzer",
                "metadata": {"chargebacks_last_week": chargebacks_week, "limit": self.config.max_chargebacks_last_week}
            })

        # 6. Abnormal New Customer Ratio
        has_new_cust_spike = False
        total_cust_hour = new_cust_hour + repeat_cust_hour
        if total_cust_hour > 5:
            new_ratio = new_cust_hour / total_cust_hour
            if new_ratio > self.config.new_customer_ratio_threshold:
                has_new_cust_spike = True
                evidence.append({
                    "type": "NewCustomerRatioSpike",
                    "severity": "MEDIUM",
                    "title": "Abnormal New Customer Ratio",
                    "description": f"Unusually high ratio of new customers ({new_ratio:.2%}) transacting in the last hour (new: {new_cust_hour}, total: {total_cust_hour}).",
                    "confidence": 0.80,
                    "source": "MerchantVelocityAnalyzer",
                    "metadata": {"new_customer_ratio": new_ratio, "new_customers": new_cust_hour, "total": total_cust_hour}
                })

        # 7. High-Frequency Low-Value Card Testing Detection
        is_card_testing = False
        if tx_minute >= self.config.high_freq_low_value_count and amount <= self.config.high_freq_low_value_threshold:
            is_card_testing = True
            evidence.append({
                "type": "CardTestingVelocity",
                "severity": "CRITICAL",
                "title": "Potential Card Testing Velocity",
                "description": f"High frequency of low-value transactions detected: {tx_minute} transactions/min below ${self.config.high_freq_low_value_threshold:.2f}.",
                "confidence": 0.95,
                "source": "MerchantVelocityAnalyzer",
                "metadata": {"transactions_last_minute": tx_minute, "amount": amount}
            })

        # 8. Rapid Growth Anomaly Check
        has_growth_anomaly = False
        if avg_day > 0:
            growth_multiplier = tx_day / avg_day
            if growth_multiplier > self.config.growth_rate_multiplier:
                has_growth_anomaly = True
                evidence.append({
                    "type": "RapidMerchantGrowth",
                    "severity": "MEDIUM",
                    "title": "Rapid Merchant Growth Anomaly",
                    "description": f"Merchant volume processed in the last 24 hours is {growth_multiplier:.1f}x higher than historical average daily rate.",
                    "confidence": 0.75,
                    "source": "MerchantVelocityAnalyzer",
                    "metadata": {"day_volume": tx_day, "average_day": avg_day, "growth_multiplier": growth_multiplier}
                })

        # Check legacy triggers to stay backward compatible with history lists
        if history_list and not is_context_mode:
            # Legacy fallback: Count consecutive transactions at this merchant in history
            merchant_txns = [h for h in history_list if (h.get("merchant") == merchant_id or h.get("merchant_id") == merchant_id)]
            if len(merchant_txns) >= 5:
                # Deduplicate type to avoid repeats
                if not any(ev["type"] == "MerchantVelocitySpike" for ev in evidence):
                    evidence.append({
                        "type": "MerchantVelocitySpike",
                        "severity": "MEDIUM",
                        "title": "Consecutive Transaction Velocity Spikes",
                        "description": f"Customer has established high velocity ({len(merchant_txns)} consecutive transactions) at merchant '{merchant_id}' in recent history.",
                        "confidence": 0.75,
                        "source": "MerchantVelocityAnalyzer",
                        "metadata": {"history_count": len(merchant_txns)}
                    })

        logger.info("Velocity analysis completed")

        # Compute confidence score
        trust_score = 1.0
        if is_card_testing:
            trust_score *= 0.2
        if has_cb_spike:
            trust_score *= 0.5
        if has_refund_spike:
            trust_score *= 0.7
        if len(evidence) > 0:
            # Factor in general alerts multiplier
            multiplier = 0.9**len(evidence)
            trust_score *= multiplier
            
        trust_score = max(0.1, min(1.0, trust_score))

        # Recommendations mapping
        if is_card_testing:
            recommendations.append("Temporarily suspend settlement")
            recommendations.append("Require manual review")
        if has_cb_spike or has_refund_spike:
            recommendations.append("Temporarily limit transaction volume")
            recommendations.append("Require manual review")
        if has_high_failure or has_amount_deviation or has_growth_anomaly:
            recommendations.append("Increase monitoring")
            recommendations.append("Request additional merchant verification")
            
        if not recommendations:
            recommendations.append("Increase monitoring")

        logger.info("Evidence generated: %d items", len(evidence))
        logger.info("Analyzer completed")

        if is_context_mode:
            return {
                "evidence": evidence,
                "confidence_score": trust_score,
                "metadata": {
                    "checks_completed": ["burst_detection", "amount_deviation", "failed_rates", "refunds_day", "chargebacks_week", "growth_anomaly", "card_testing"],
                    "alerts_triggered_count": len(evidence)
                },
                "recommendations": list(set(recommendations))
            }
        
        # Legacy returns list of evidence
        return evidence
export_analyzer = MerchantVelocityAnalyzer
