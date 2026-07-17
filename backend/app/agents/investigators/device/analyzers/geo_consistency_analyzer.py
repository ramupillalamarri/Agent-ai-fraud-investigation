import math
import logging
from datetime import datetime
from typing import Dict, Any, List
from app.agents.investigators.device.config import DeviceAgentConfig

logger = logging.getLogger("app.agents.DeviceGeoConsistency")

class GeoConsistencyAnalyzer:
    """Calculates geographical distances and timestamps to identify impossible physical travel speeds."""

    def __init__(self, config: DeviceAgentConfig) -> None:
        self.config = config

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes distance between two coordinates in kilometers."""
        R = 6371.0  # Earth radius
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(d_lat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def analyze(self, tx_data: Dict[str, Any], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verifies geo-consistency between current and previous transactions.
        
        Args:
            tx_data: Current transaction parameters.
            history: List of past transactions.
            
        Returns:
            List[Dict[str, Any]]: Structured travel evidence logs.
        """
        evidence = []
        
        current_lat = tx_data.get("latitude")
        current_lon = tx_data.get("longitude")
        current_country = tx_data.get("country")
        
        # Parse timestamp
        tx_ts_raw = tx_data.get("timestamp") or tx_data.get("transaction_timestamp")
        current_ts = None
        if isinstance(tx_ts_raw, datetime):
            current_ts = tx_ts_raw
        elif tx_ts_raw:
            try:
                current_ts = datetime.fromisoformat(str(tx_ts_raw))
            except Exception:
                pass

        if current_lat is None or current_lon is None or current_ts is None:
            # Fallback to country change check if coordinates are absent
            if current_country and history:
                last_tx = history[-1]
                last_country = last_tx.get("country")
                if last_country and last_country != current_country:
                    evidence.append({
                        "type": "LocationAnomaly",
                        "severity": "MEDIUM",
                        "confidence": 0.85,
                        "description": f"Transaction country changed suddenly from '{last_country}' to '{current_country}'.",
                        "source": "GeoConsistencyAnalyzer"
                    })
            return evidence
            
        try:
            current_lat = float(current_lat)
            current_lon = float(current_lon)
        except (ValueError, TypeError):
            return evidence

        prev_lat = None
        prev_lon = None
        prev_ts = None

        # Check previous_login_location first if available
        prev_loc = tx_data.get("previous_login_location")
        if isinstance(prev_loc, dict):
            prev_lat = prev_loc.get("latitude")
            prev_lon = prev_loc.get("longitude")
            prev_ts_raw = prev_loc.get("timestamp") or prev_loc.get("transaction_timestamp")
            if isinstance(prev_ts_raw, datetime):
                prev_ts = prev_ts_raw
            elif prev_ts_raw:
                try:
                    prev_ts = datetime.fromisoformat(str(prev_ts_raw))
                except Exception:
                    pass

        # Fallback to last history transaction coordinates if metadata not populated
        if (prev_lat is None or prev_lon is None) and history:
            for tx in reversed(history):
                if tx.get("latitude") is not None and tx.get("longitude") is not None:
                    try:
                        prev_lat = float(tx.get("latitude"))
                        prev_lon = float(tx.get("longitude"))
                        hist_ts_raw = tx.get("timestamp") or tx.get("transaction_timestamp")
                        if isinstance(hist_ts_raw, datetime):
                            prev_ts = hist_ts_raw
                        elif hist_ts_raw:
                            try:
                                prev_ts = datetime.fromisoformat(str(hist_ts_raw))
                            except Exception:
                                pass
                        break
                    except (ValueError, TypeError):
                        continue

        if prev_lat is not None and prev_lon is not None and prev_ts is not None:
            distance_km = self._haversine_distance(current_lat, current_lon, prev_lat, prev_lon)
            time_delta_hours = abs((current_ts - prev_ts).total_seconds()) / 3600.0
            
            if time_delta_hours > 0:
                speed_kmh = distance_km / time_delta_hours
                if speed_kmh > self.config.max_possible_travel_speed_kmh:
                    evidence.append({
                        "type": "ImpossibleTravel",
                        "severity": "HIGH",
                        "confidence": 0.95,
                        "description": f"Impossible travel speed detected: {speed_kmh:.2f} km/h (distance={distance_km:.1f} km, time={time_delta_hours:.2f} hours). Limit is {self.config.max_possible_travel_speed_kmh} km/h.",
                        "source": "GeoConsistencyAnalyzer"
                    })
                    
        return evidence
