import logging
import math
from typing import Dict, Any, List, Optional
from app.agents.investigators.merchant.config import MerchantAgentConfig
from app.agents.models.investigation_context import InvestigationContext

logger = logging.getLogger("app.agents.investigators.merchant.analyzers.merchant_location_analyzer")

class MerchantLocationAnalyzer:
    """Evaluates geographic, cross-border, timezone, and coordinates distance risk signals for merchant terminals."""

    def __init__(self, config: MerchantAgentConfig) -> None:
        """Initializes the MerchantLocationAnalyzer with configuration thresholds."""
        self.config = config

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two points in kilometers using Haversine formula."""
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def analyze(self, context_or_tx_data: Any, history: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Performs location risk analysis on merchant registry and execution geographics.
        
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
            merchant_loc_info = tx_data.get("merchant_profile") or tx_data or {}
        else:
            tx_data = context_or_tx_data or {}
            merchant_loc_info = tx_data
            metadata = {}

        # Safely extract merchant ID
        merchant_id = (
            merchant_loc_info.get("merchant_id") 
            or merchant_loc_info.get("merchant") 
            or tx_data.get("merchant_id") 
            or tx_data.get("merchant")
        )
        
        logger.info("Location loaded for merchant: %s", merchant_id)

        evidence: List[Dict[str, Any]] = []
        recommendations: List[str] = []

        if not merchant_id:
            logger.warning("No merchant_id found in location payload")
            if is_context_mode:
                return {
                    "evidence": [],
                    "confidence_score": 1.0,
                    "metadata": {"error": "Missing merchant_id"},
                    "recommendations": ["Enhanced monitoring"]
                }
            return []

        # Extract fields
        merchant_country = (
            merchant_loc_info.get("merchant_country") 
            or merchant_loc_info.get("merchant_location_country") 
            or tx_data.get("merchant_country")
        )
        merchant_region = merchant_loc_info.get("merchant_region")
        merchant_operating_regions = merchant_loc_info.get("merchant_operating_regions")
        
        location_country = (
            tx_data.get("location_country") 
            or tx_data.get("country") 
            or tx_data.get("transaction_country")
        )
        
        customer_country = tx_data.get("customer_country")
        
        # 1. Geographic country mismatch (cross-border)
        is_cross_border = False
        if location_country and merchant_country and str(location_country).upper() != str(merchant_country).upper():
            is_cross_border = True
            evidence.append({
                "type": "MerchantLocationMismatch",
                "severity": "MEDIUM",
                "title": "Merchant Location Mismatch",
                "description": f"Cross-border transaction mismatch: User is executing transaction in '{location_country}' while merchant terminal is registered in '{merchant_country}'.",
                "confidence": 0.80,
                "source": "MerchantLocationAnalyzer",
                "metadata": {"merchant_country": merchant_country, "transaction_country": location_country}
            })

        if customer_country and merchant_country and str(customer_country).upper() != str(merchant_country).upper():
            evidence.append({
                "type": "MerchantCustomerCountryMismatch",
                "severity": "MEDIUM",
                "title": "Customer Merchant Country Mismatch",
                "description": f"Customer billing country '{customer_country}' mismatches merchant registry country '{merchant_country}'.",
                "confidence": 0.75,
                "source": "MerchantLocationAnalyzer",
                "metadata": {"customer_country": customer_country, "merchant_country": merchant_country}
            })

        # 2. High-risk, Watchlist & Sanctioned countries check
        is_sanctioned = False
        is_watchlist = False
        is_restricted_region = False

        if merchant_country:
            norm_country = str(merchant_country).upper().strip()
            if norm_country in self.config.sanctioned_countries:
                is_sanctioned = True
                evidence.append({
                    "type": "SanctionedMerchantJurisdiction",
                    "severity": "CRITICAL",
                    "title": "Sanctioned Merchant Jurisdiction",
                    "description": f"Merchant '{merchant_id}' is operating from a sanctioned country: '{merchant_country}'.",
                    "confidence": 0.99,
                    "source": "MerchantLocationAnalyzer",
                    "metadata": {"merchant_country": merchant_country, "classification": "sanctioned"}
                })
            elif norm_country in self.config.watchlist_countries:
                is_watchlist = True
                evidence.append({
                    "type": "WatchlistMerchantJurisdiction",
                    "severity": "HIGH",
                    "title": "Watchlist Merchant Jurisdiction",
                    "description": f"Merchant '{merchant_id}' is operating from a watchlist country: '{merchant_country}'.",
                    "confidence": 0.85,
                    "source": "MerchantLocationAnalyzer",
                    "metadata": {"merchant_country": merchant_country, "classification": "watchlist"}
                })

        if merchant_region and str(merchant_region).lower().strip() in self.config.restricted_regions:
            is_restricted_region = True
            evidence.append({
                "type": "RestrictedMerchantRegion",
                "severity": "HIGH",
                "title": "Restricted Merchant Region",
                "description": f"Merchant '{merchant_id}' is registered in a restricted region: '{merchant_region}'.",
                "confidence": 0.80,
                "source": "MerchantLocationAnalyzer",
                "metadata": {"merchant_region": merchant_region, "classification": "restricted"}
            })

        # 3. Operating outside declared regions check
        is_outside_operating_region = False
        if merchant_operating_regions and location_country:
            # operating regions can be a list, set, or string list
            if isinstance(merchant_operating_regions, str):
                regions_list = [r.strip().upper() for r in merchant_operating_regions.split(",")]
            else:
                regions_list = [str(r).upper() for r in merchant_operating_regions]
                
            if str(location_country).upper() not in regions_list:
                is_outside_operating_region = True
                evidence.append({
                    "type": "MerchantOutsideOperatingRegion",
                    "severity": "HIGH",
                    "title": "Merchant Operating Outside Declared Regions",
                    "description": f"Merchant transaction execution location '{location_country}' is outside declared operating regions: {regions_list}.",
                    "confidence": 0.85,
                    "source": "MerchantLocationAnalyzer",
                    "metadata": {"location_country": location_country, "declared_regions": regions_list}
                })

        # 4. Geolocation distance checks
        has_extreme_distance = False
        cust_lat = tx_data.get("customer_latitude") or tx_data.get("latitude")
        cust_lon = tx_data.get("customer_longitude") or tx_data.get("longitude")
        merch_lat = merchant_loc_info.get("merchant_latitude") or tx_data.get("merchant_latitude")
        merch_lon = merchant_loc_info.get("merchant_longitude") or tx_data.get("merchant_longitude")
        
        distance_km = 0.0
        if all(x is not None for x in [cust_lat, cust_lon, merch_lat, merch_lon]):
            try:
                distance_km = self._haversine_distance(
                    float(cust_lat), float(cust_lon), float(merch_lat), float(merch_lon)
                )
                # If distance exceeds 5000 km, flag it
                if distance_km > 5000.0:
                    has_extreme_distance = True
                    evidence.append({
                        "type": "ExtremeGeoDistance",
                        "severity": "HIGH",
                        "title": "Extreme Customer-Merchant Geodistance",
                        "description": f"Calculated distance between customer location and merchant terminal is extreme: {distance_km:,.1f} km.",
                        "confidence": 0.85,
                        "source": "MerchantLocationAnalyzer",
                        "metadata": {"customer_coordinates": (cust_lat, cust_lon), "merchant_coordinates": (merch_lat, merch_lon), "distance_km": distance_km}
                    })
            except Exception as e:
                logger.error("Failed to parse coordinates: %s", str(e))

        # 5. Timezone inconsistency check
        has_tz_inconsistency = False
        cust_tz = tx_data.get("customer_timezone") or tx_data.get("timezone")
        merch_tz = merchant_loc_info.get("merchant_timezone") or tx_data.get("merchant_timezone")
        
        if cust_tz is not None and merch_tz is not None:
            try:
                # If they are numbers (e.g. UTC offset like +5 or -3), check difference
                c_offset = float(cust_tz)
                m_offset = float(merch_tz)
                offset_diff = abs(c_offset - m_offset)
                # If offset difference exceeds 6 hours, flag it
                if offset_diff > 6.0:
                    has_tz_inconsistency = True
                    evidence.append({
                        "type": "TimezoneMismatch",
                        "severity": "MEDIUM",
                        "title": "Merchant Customer Timezone Inconsistency",
                        "description": f"Anomalous timezone offset difference ({offset_diff} hours) detected between customer ({cust_tz}) and merchant ({merch_tz}).",
                        "confidence": 0.75,
                        "source": "MerchantLocationAnalyzer",
                        "metadata": {"customer_timezone": cust_tz, "merchant_timezone": merch_tz, "offset_difference": offset_diff}
                    })
            except Exception:
                # If strings, do a simple unequal check (fallback)
                if str(cust_tz).strip().upper() != str(merch_tz).strip().upper():
                    has_tz_inconsistency = True
                    evidence.append({
                        "type": "TimezoneMismatch",
                        "severity": "MEDIUM",
                        "title": "Merchant Customer Timezone Inconsistency",
                        "description": f"Customer timezone '{cust_tz}' does not align with merchant timezone '{merch_tz}'.",
                        "confidence": 0.75,
                        "source": "MerchantLocationAnalyzer",
                        "metadata": {"customer_timezone": cust_tz, "merchant_timezone": merch_tz}
                    })

        logger.info("Location checks completed")

        # Calculate trust/confidence score
        trust_score = 1.0
        if is_sanctioned:
            trust_score *= 0.1
        elif is_watchlist:
            trust_score *= 0.6
        if is_restricted_region:
            trust_score *= 0.7
        if is_outside_operating_region:
            trust_score *= 0.75
        if is_cross_border:
            trust_score *= 0.85
        if has_extreme_distance:
            trust_score *= 0.8
        if has_tz_inconsistency:
            trust_score *= 0.9
            
        trust_score = max(0.1, min(1.0, trust_score))

        # Recommendations mapping
        if is_sanctioned:
            recommendations.append("Block transaction")
            recommendations.append("Manual review")
        if is_watchlist or is_restricted_region or is_outside_operating_region:
            recommendations.append("Require additional verification")
            recommendations.append("Manual review")
        if is_cross_border or has_extreme_distance:
            recommendations.append("Request customer confirmation")
            recommendations.append("Enhanced monitoring")
        if has_tz_inconsistency:
            recommendations.append("Enhanced monitoring")
            
        if not recommendations:
            recommendations.append("Enhanced monitoring")

        logger.info("Evidence generated: %d items", len(evidence))
        logger.info("Analyzer completed")

        if is_context_mode:
            return {
                "evidence": evidence,
                "confidence_score": trust_score,
                "metadata": {
                    "merchant_country": merchant_country,
                    "merchant_region": merchant_region,
                    "distance_km": distance_km,
                    "checks_completed": ["jurisdiction_check", "cross_border_match", "operating_regions", "geodistance", "timezones"]
                },
                "recommendations": list(set(recommendations))
            }
        
        # Legacy/Agent mode returns raw list of evidence dicts
        return evidence
export_analyzer = MerchantLocationAnalyzer
