from typing import Dict, Any, List
from app.agents.investigators.device.config import DeviceAgentConfig

class IPAddressAnalyzer:
    """Evaluates client IP addresses for blocklist matches, datacenter classification, and profile shifts."""

    def __init__(self, config: DeviceAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyzes network location specifications.
        
        Args:
            tx_data: Current transaction parameters.
            history: List of past transactions.
            
        Returns:
            List[Dict[str, Any]]: Structured network evidence logs.
        """
        evidence = []
        ip = tx_data.get("ip_address")
        ip_type = str(tx_data.get("ip_type") or "").lower()
        
        if not ip:
            return evidence

        # Blocklist verification
        if ip in self.config.blacklisted_ips:
            evidence.append({
                "type": "BlacklistedIP",
                "severity": "HIGH",
                "confidence": 0.98,
                "description": f"IP Address '{ip}' matches a blacklisted compromised security network node.",
                "source": "IPAddressAnalyzer"
            })

        # Datacenter type matching (unusual for standard consumer shopping)
        is_datacenter = any(dc in ip_type for dc in self.config.datacenter_ip_subnets) or "datacenter" in ip_type
        if is_datacenter:
            evidence.append({
                "type": "DatacenterIP",
                "severity": "HIGH",
                "confidence": 0.92,
                "description": f"Connection originating from commercial hosting or datacenter IP segment: '{ip_type}'.",
                "source": "IPAddressAnalyzer"
            })

        # Profile shifts
        hist_ips = [tx.get("ip_address") for tx in history if tx.get("ip_address")]
        if hist_ips and ip not in hist_ips:
            evidence.append({
                "type": "NewIPAddress",
                "severity": "LOW",
                "confidence": 0.80,
                "description": f"First-time transaction origin from network IP: '{ip}'.",
                "source": "IPAddressAnalyzer"
            })
            
        return evidence
