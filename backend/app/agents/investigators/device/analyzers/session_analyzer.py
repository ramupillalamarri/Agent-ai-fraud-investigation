from typing import Dict, Any, List
from app.agents.investigators.device.config import DeviceAgentConfig

class SessionAnalyzer:
    """Monitors session duration limits, concurrent logins, and hijacking indicators."""

    def __init__(self, config: DeviceAgentConfig) -> None:
        self.config = config

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Audits active session credentials state.
        
        Args:
            tx_data: Current transaction parameters.
            history: List of past transactions.
            
        Returns:
            List[Dict[str, Any]]: Structured session evidence logs.
        """
        evidence = []
        session_age = tx_data.get("session_age_seconds") or tx_data.get("session_age")
        simultaneous_sessions = tx_data.get("simultaneous_sessions")
        session_anomaly = tx_data.get("session_anomaly")

        # Session age validation
        if session_age is not None:
            try:
                age = float(session_age)
                if age < self.config.min_session_age_seconds:
                    evidence.append({
                        "type": "NewSession",
                        "severity": "LOW",
                        "confidence": 0.80,
                        "description": f"Session lifetime is too short ({age:.1f}s), indicating a possible script generation.",
                        "source": "SessionAnalyzer"
                    })
            except (ValueError, TypeError):
                pass

        # Concurrent session check
        if simultaneous_sessions is not None:
            try:
                sessions = int(simultaneous_sessions)
                if sessions > self.config.max_simultaneous_sessions:
                    evidence.append({
                        "type": "SimultaneousSessions",
                        "severity": "HIGH",
                        "confidence": 0.90,
                        "description": f"Simultaneous active sessions ({sessions}) exceed the security threshold limit.",
                        "source": "SessionAnalyzer"
                    })
            except (ValueError, TypeError):
                pass

        # Session hijacking validation
        is_hijack_risk = str(session_anomaly).lower() in ("true", "1", "yes") or session_anomaly is True
        if is_hijack_risk:
            evidence.append({
                "type": "SessionHijackRisk",
                "severity": "HIGH",
                "confidence": 0.95,
                "description": "Session credentials display hijacking indicators or validation token mismatches.",
                "source": "SessionAnalyzer"
            })
            
        return evidence
