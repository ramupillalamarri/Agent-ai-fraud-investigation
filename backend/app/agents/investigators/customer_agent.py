import logging
import math
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from app.agents.base.base_agent import BaseAgent
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult

logger = logging.getLogger("app.agents.CustomerInvestigationAgent")

@dataclass
class CustomerAgentConfig:
    """Configurable thresholds and windows for customer behavioral anomaly detection."""
    spending_deviation_threshold: float = 3.0  # std deviation units
    velocity_time_window_seconds: int = 3600  # 1 hour
    velocity_transaction_count_threshold: int = 3
    unusual_hour_start: int = 23  # 11 PM
    unusual_hour_end: int = 5     # 5 AM
    min_history_count_for_stats: int = 3
    rare_category_probability_threshold: float = 0.05
    rare_payment_method_probability_threshold: float = 0.05

class CustomerInvestigationAgent(BaseAgent):
    """AI Investigation Agent analyzing current retail transactions against historical customer profiles."""

    def __init__(
        self,
        agent_id: str = "customer-investigator-01",
        agent_name: str = "CustomerInvestigationAgent",
        description: str = "Analyzes transaction patterns against historical customer profiles.",
        version: str = "1.0.0",
        enabled: bool = True,
        execution_priority: int = 10,
        supported_features: Optional[List[str]] = None,
        config: Optional[CustomerAgentConfig] = None
    ) -> None:
        """Initializes the CustomerInvestigationAgent."""
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            version=version,
            enabled=enabled,
            execution_priority=execution_priority,
            supported_features=supported_features or ["customer", "behavior"]
        )
        self.config = config or CustomerAgentConfig()

    def validate(self, context: InvestigationContext) -> None:
        """Validates that transaction_data contains customer_id."""
        tx_data = context.transaction_data or {}
        if "customer_id" not in tx_data and "user_id" not in tx_data:
            raise ValueError("CustomerInvestigationAgent requires customer_id or user_id in transaction_data.")

    def health_check(self) -> bool:
        """Health check indicator."""
        return True

    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Executes rules/statistical checks on the current transaction against history."""
        tx_data = context.transaction_data
        
        # Resolve customer ID
        customer_id = tx_data.get("customer_id") or tx_data.get("user_id", "UNKNOWN")
        
        # Load transaction details
        current_amount = float(tx_data.get("amount") or tx_data.get("transaction_amount") or 0.0)
        
        # Resolve current timestamp
        tx_ts_raw = tx_data.get("timestamp") or tx_data.get("transaction_timestamp")
        if isinstance(tx_ts_raw, datetime):
            current_timestamp = tx_ts_raw
        elif tx_ts_raw:
            try:
                current_timestamp = datetime.fromisoformat(str(tx_ts_raw))
            except Exception:
                current_timestamp = datetime.now(timezone.utc)
        else:
            current_timestamp = datetime.now(timezone.utc)

        current_category = tx_data.get("category") or tx_data.get("merchant_category", "UNKNOWN")
        current_payment = tx_data.get("payment_method", "UNKNOWN")

        # Load customer transaction history (mock db/store injection fallback)
        history: List[Dict[str, Any]] = context.shared_memory.get("customer_history") or context.metadata.get("customer_history") or []
        
        evidence_list: List[Dict[str, Any]] = []
        findings: List[str] = []
        recommendations: List[str] = []
        rules_triggered: List[str] = []
        analyzed_features = ["amount", "timestamp", "category", "payment_method"]

        # Parse history statistics
        hist_amounts = []
        hist_timestamps = []
        hist_categories = []
        hist_payments = []

        for tx in history:
            # Amount parsing
            amt = tx.get("amount") or tx.get("transaction_amount")
            if amt is not None:
                hist_amounts.append(float(amt))
            
            # Timestamp parsing
            ts_raw = tx.get("timestamp") or tx.get("transaction_timestamp")
            if isinstance(ts_raw, datetime):
                hist_timestamps.append(ts_raw)
            elif ts_raw:
                try:
                    hist_timestamps.append(datetime.fromisoformat(str(ts_raw)))
                except Exception:
                    pass
            
            # Category and payment parsing
            cat = tx.get("category") or tx.get("merchant_category")
            if cat:
                hist_categories.append(cat)
            pay = tx.get("payment_method")
            if pay:
                hist_payments.append(pay)

        history_len = len(hist_amounts)
        self.log_info("Analyzing history of customer: %s | Records count: %d", customer_id, history_len)

        # ----------------------------------------------------
        # Rule 1: Spending Anomaly
        # ----------------------------------------------------
        if history_len > 0:
            mean_amt = sum(hist_amounts) / history_len
            variance = sum((x - mean_amt) ** 2 for x in hist_amounts) / history_len
            std_dev = math.sqrt(variance)

            deviation = current_amount - mean_amt
            if history_len >= self.config.min_history_count_for_stats and std_dev > 0:
                std_multiplier = deviation / std_dev
                if std_multiplier > self.config.spending_deviation_threshold:
                    rules_triggered.append("SpendingAnomaly")
                    findings.append(f"Spending deviation is unusually high: {std_multiplier:.2f} standard deviations above mean.")
                    evidence_list.append({
                        "type": "SpendingAnomaly",
                        "severity": "HIGH" if std_multiplier > 5.0 else "MEDIUM",
                        "description": f"Transaction amount of ${current_amount:.2f} is significantly higher than customer mean of ${mean_amt:.2f} (std={std_dev:.2f}).",
                        "confidence": min(0.99, 0.85 + (std_multiplier / 50.0))
                    })
            else:
                # Fallback ratio check for small histories
                if current_amount > 5.0 * mean_amt:
                    rules_triggered.append("SpendingAnomaly")
                    findings.append(f"Spending ratio is abnormally high: {current_amount / mean_amt:.1f}x the historical mean.")
                    evidence_list.append({
                        "type": "SpendingAnomaly",
                        "severity": "HIGH",
                        "description": f"Transaction amount of ${current_amount:.2f} is {current_amount / mean_amt:.1f}x the customer mean of ${mean_amt:.2f}.",
                        "confidence": 0.80
                    })

        # ----------------------------------------------------
        # Rule 2: Time of Day Anomaly
        # ----------------------------------------------------
        hour = current_timestamp.hour
        is_unusual_hour = False
        if self.config.unusual_hour_start > self.config.unusual_hour_end:
            is_unusual_hour = hour >= self.config.unusual_hour_start or hour < self.config.unusual_hour_end
        else:
            is_unusual_hour = self.config.unusual_hour_start <= hour < self.config.unusual_hour_end

        if is_unusual_hour:
            rules_triggered.append("TimeOfDayAnomaly")
            findings.append(f"Transaction occurred at an unusual hour: {hour:02d}:00.")
            evidence_list.append({
                "type": "TimeAnomaly",
                "severity": "MEDIUM",
                "description": f"Transaction initiated at {hour:02d}:00, which falls within the unusual hour range ({self.config.unusual_hour_start:02d}:00-{self.config.unusual_hour_end:02d}:00).",
                "confidence": 0.75
            })

        # ----------------------------------------------------
        # Rule 3: Day of Week Anomaly
        # ----------------------------------------------------
        if history_len >= self.config.min_history_count_for_stats:
            current_day = current_timestamp.weekday()
            hist_days = [ts.weekday() for ts in hist_timestamps]
            if current_day not in hist_days:
                rules_triggered.append("DayOfWeekAnomaly")
                findings.append(f"Transaction day of week ({current_timestamp.strftime('%A')}) has no historical match.")
                evidence_list.append({
                    "type": "DayOfWeekAnomaly",
                    "severity": "LOW",
                    "description": f"Customer historically has not made transactions on {current_timestamp.strftime('%A')}s.",
                    "confidence": 0.65
                })

        # ----------------------------------------------------
        # Rule 4: Category Anomaly
        # ----------------------------------------------------
        if history_len >= self.config.min_history_count_for_stats and current_category != "UNKNOWN":
            cat_count = hist_categories.count(current_category)
            cat_probability = cat_count / len(hist_categories) if hist_categories else 0.0
            if cat_probability < self.config.rare_category_probability_threshold:
                rules_triggered.append("CategoryAnomaly")
                findings.append(f"Rare purchase category detected: {current_category}.")
                evidence_list.append({
                    "type": "CategoryAnomaly",
                    "severity": "MEDIUM" if cat_count == 0 else "LOW",
                    "description": f"Transaction category '{current_category}' is rare for this customer (probability={cat_probability:.2f}).",
                    "confidence": 0.80
                })

        # ----------------------------------------------------
        # Rule 5: Payment Method Anomaly
        # ----------------------------------------------------
        if history_len >= self.config.min_history_count_for_stats and current_payment != "UNKNOWN":
            pay_count = hist_payments.count(current_payment)
            pay_probability = pay_count / len(hist_payments) if hist_payments else 0.0
            if pay_probability < self.config.rare_payment_method_probability_threshold:
                rules_triggered.append("PaymentMethodAnomaly")
                findings.append(f"Rare payment method instrument detected: {current_payment}.")
                evidence_list.append({
                    "type": "PaymentMethodAnomaly",
                    "severity": "MEDIUM" if pay_count == 0 else "LOW",
                    "description": f"Payment instrument '{current_payment}' is rarely used by this customer.",
                    "confidence": 0.80
                })

        # ----------------------------------------------------
        # Rule 6: Velocity Check
        # ----------------------------------------------------
        recent_txs = 0
        for ts in hist_timestamps:
            delta = abs((current_timestamp - ts).total_seconds())
            if delta <= self.config.velocity_time_window_seconds:
                recent_txs += 1
                
        if recent_txs >= self.config.velocity_transaction_count_threshold:
            rules_triggered.append("VelocityAnomaly")
            findings.append(f"High velocity transaction counts: {recent_txs} transactions within last hour.")
            evidence_list.append({
                "type": "VelocityAnomaly",
                "severity": "HIGH" if recent_txs > 5 else "MEDIUM",
                "description": f"Customer triggered velocity alerts: {recent_txs} purchases within the target {self.config.velocity_time_window_seconds}s time window.",
                "confidence": 0.90
            })

        # Calculate overall confidence score based on history richness
        if history_len >= 10:
            confidence = 0.95
        elif history_len >= 3:
            confidence = 0.85
        else:
            confidence = 0.50

        # Generate action recommendations based on triggered anomalies
        high_severity_alerts = any(ev.get("severity") == "HIGH" for ev in evidence_list)
        med_severity_alerts = any(ev.get("severity") == "MEDIUM" for ev in evidence_list)
        
        if high_severity_alerts:
            recommendations.append("Manual investigation")
            recommendations.append("Decline transaction and alert cardholder")
        elif med_severity_alerts:
            recommendations.append("Request OTP confirmation")
            recommendations.append("Verify customer identity")
        elif evidence_list:
            recommendations.append("Flag customer profile for verification")
        else:
            findings.append("No unusual behavioral patterns identified for this customer.")
            recommendations.append("Approve transaction")

        # Compile metadata execution details
        metadata = {
            "rules_triggered": rules_triggered,
            "analyzed_features": analyzed_features,
            "execution_statistics": {
                "historical_count": history_len,
                "anomalies_found": len(evidence_list),
                "timestamp_processed": datetime.utcnow().isoformat()
            }
        }

        # Build output result status
        status = "SUCCESS"
        if not evidence_list:
            confidence_score = 1.0  # certain it is normal
        else:
            confidence_score = confidence

        return AgentResult(
            agent_name=self.agent_name,
            status=status,
            confidence_score=confidence_score,
            findings=findings,
            recommendations=recommendations,
            evidence=evidence_list,
            execution_time_ms=0,  # calculated automatically by BaseAgent execute
            metadata=metadata
        )
