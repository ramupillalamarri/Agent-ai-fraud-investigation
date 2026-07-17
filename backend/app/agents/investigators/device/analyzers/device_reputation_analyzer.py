from typing import Dict, Any, List
from app.agents.investigators.device.config import DeviceAgentConfig

class DeviceReputationAnalyzer:
    """Evaluates device security indexes, risk telemetry, and blacklist presence."""

    def __init__(self, config: DeviceAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scans device ID lists against reputation indicators.
        
        Args:
            tx_data: Current transaction parameters.
            history: List of past transactions.
            
        Returns:
            List[Dict[str, Any]]: Structured reputation evidence logs.
        """
        evidence = []
        device_id = tx_data.get("device_id")
        device_risk = float(tx_data.get("device_risk_score") or tx_data.get("device_risk") or 0.0)
        
        if not device_id:
            return evidence

        # Blacklist evaluation
        if device_id in self.config.blacklisted_devices:
            evidence.append({
                "type": "BlacklistedDevice",
                "severity": "HIGH",
                "confidence": 0.99,
                "description": f"Device ID '{device_id}' matches a blacklisted or historically fraudulent terminal ID.",
                "source": "DeviceReputationAnalyzer"
            })

        # Telemetry risk indices
        if device_risk > self.config.device_risk_threshold:
            evidence.append({
                "type": "CompromisedDeviceReputation",
                "severity": "HIGH",
                "confidence": 0.90,
                "description": f"Device risk evaluation score ({device_risk:.2f}) exceeds system safety threshold ({self.config.device_risk_threshold:.2f}).",
                "source": "DeviceReputationAnalyzer"
            })
            
        return evidence
