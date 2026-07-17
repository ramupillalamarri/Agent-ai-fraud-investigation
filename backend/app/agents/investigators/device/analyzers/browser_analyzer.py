from typing import Dict, Any, List
from app.agents.investigators.device.config import DeviceAgentConfig

class BrowserAnalyzer:
    """Detects headless browser runs, user agent mismatches, and automated testing frameworks."""

    def __init__(self, config: DeviceAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audits the browser client signature metrics.
        
        Args:
            tx_data: Current transaction parameters.
            history: List of past transactions.
            
        Returns:
            List[Dict[str, Any]]: Structured browser evidence logs.
        """
        evidence = []
        browser = str(tx_data.get("browser") or "").lower()
        user_agent = str(tx_data.get("user_agent") or "").lower()
        
        # Detect headless browsers or automated automation tools (e.g. selenium, phantomjs)
        is_headless = any(ub in browser or ub in user_agent for ub in self.config.unusual_browsers)
        
        if is_headless or "headless" in browser or "headless" in user_agent:
            evidence.append({
                "type": "SuspiciousBrowser",
                "severity": "HIGH",
                "confidence": 0.95,
                "description": f"Automated or headless browser framework environment detected: '{browser or user_agent}'.",
                "source": "BrowserAnalyzer"
            })
            
        return evidence
