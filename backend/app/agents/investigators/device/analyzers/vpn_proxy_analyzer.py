from typing import Dict, Any, List
from app.agents.investigators.device.config import DeviceAgentConfig

class VPNProxyAnalyzer:
    """Detects active VPN nodes, anonymous proxy connections, and TOR onion routing usage."""

    def __init__(self, config: DeviceAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audits connection headers for anonymous network features.
        
        Args:
            tx_data: Current transaction parameters.
            history: List of past transactions.
            
        Returns:
            List[Dict[str, Any]]: Structured network security evidence logs.
        """
        evidence = []
        vpn = tx_data.get("vpn_detected")
        proxy = tx_data.get("proxy_detected")
        tor = tx_data.get("tor_detected")

        # Explicit bool validation or string truth checks
        is_vpn = str(vpn).lower() in ("true", "1", "yes") or vpn is True
        is_proxy = str(proxy).lower() in ("true", "1", "yes") or proxy is True
        is_tor = str(tor).lower() in ("true", "1", "yes") or tor is True

        if is_vpn:
            evidence.append({
                "type": "VPNDetected",
                "severity": self.config.vpn_threat_severity,
                "confidence": 0.95,
                "description": "Active VPN network usage detected masking client geo-location.",
                "source": "VPNProxyAnalyzer"
            })

        if is_proxy:
            evidence.append({
                "type": "ProxyDetected",
                "severity": self.config.proxy_threat_severity,
                "confidence": 0.90,
                "description": "Active proxy connection node identified in request routing.",
                "source": "VPNProxyAnalyzer"
            })

        if is_tor:
            evidence.append({
                "type": "TorDetected",
                "severity": self.config.tor_threat_severity,
                "confidence": 0.99,
                "description": "Connection routing detected via anonymous TOR onion network node.",
                "source": "VPNProxyAnalyzer"
            })
            
        return evidence
