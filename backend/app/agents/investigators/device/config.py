from dataclasses import dataclass, field
from typing import List, Set

@dataclass
class DeviceAgentConfig:
    """Configurable thresholds and rules for all independent device analyzers."""
    
    # Device Recognition Thresholds
    max_device_changes_per_day: int = 3
    
    # Device Reputation Thresholds
    blacklisted_devices: Set[str] = field(default_factory=lambda: {"DEV_COMPROMISED_01", "DEV_FRAUD_99", "DEV_BLOCKED_03"})
    device_risk_threshold: float = 0.70  # Scale 0 to 1
    
    # Browser Anomalies
    unusual_browsers: List[str] = field(default_factory=lambda: ["phantomjs", "headlesschrome", "selenium", "puppeteer", "headless", "bot"])
    
    # IP Address Anomalies
    datacenter_ip_subnets: List[str] = field(default_factory=lambda: ["datacenter", "hosting", "aws", "gcp", "digitalocean", "linode"])
    blacklisted_ips: Set[str] = field(default_factory=lambda: {"198.51.100.1", "203.0.113.5", "192.0.2.1"})
    
    # VPN/Proxy Threat Levels
    vpn_threat_severity: str = "HIGH"
    proxy_threat_severity: str = "HIGH"
    tor_threat_severity: str = "CRITICAL"
    
    # Geo Consistency Limit (km/h)
    max_possible_travel_speed_kmh: float = 900.0  # standard flight speeds
    
    # Session Checks
    min_session_age_seconds: int = 15
    max_simultaneous_sessions: int = 2
