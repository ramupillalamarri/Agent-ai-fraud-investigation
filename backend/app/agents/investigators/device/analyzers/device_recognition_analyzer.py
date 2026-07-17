from typing import Dict, Any, List
from app.agents.investigators.device.config import DeviceAgentConfig

class DeviceRecognitionAnalyzer:
    """Analyzes device ownership transitions, familiarity metrics, and frequency patterns."""

    def __init__(self, config: DeviceAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Checks for new devices, frequent device shifts, and familiarity records.
        
        Args:
            tx_data: Current transaction parameters.
            history: List of past transactions.
            
        Returns:
            List[Dict[str, Any]]: Structured recognition evidence logs.
        """
        evidence = []
        device_id = tx_data.get("device_id")
        previous_device_id = tx_data.get("previous_device_id")
        
        if not device_id:
            return evidence

        # Historical device profiles
        hist_devices = [tx.get("device_id") for tx in history if tx.get("device_id")]
        
        # Check for first-time device usage
        if hist_devices and device_id not in hist_devices:
            evidence.append({
                "type": "NewDevice",
                "severity": "MEDIUM",
                "confidence": 0.85,
                "description": f"New device ID detected: '{device_id}'. No matching records found in customer device history.",
                "source": "DeviceRecognitionAnalyzer"
            })

        # Check for device replacement
        if previous_device_id and previous_device_id != device_id:
            evidence.append({
                "type": "DeviceShift",
                "severity": "LOW",
                "confidence": 0.90,
                "description": f"Customer device transitioned from previous device '{previous_device_id}' to '{device_id}'.",
                "source": "DeviceRecognitionAnalyzer"
            })
            
        return evidence
