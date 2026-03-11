import json
import os
from pathlib import Path
from typing import Dict, List
import requests

KB_DIR = Path(__file__).resolve().parents[2] / "knowledge_base"


def load_json(name: str):
    with open(KB_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def geocode_address(street_address: str, city: str, state: str):
    key = os.getenv("OPENCAGE_API_KEY")
    query = f"{street_address}, {city}, {state}, USA"
    if not key:
        return {"lat": None, "lng": None, "county": None, "state": state}

    try:
        resp = requests.get(
            "https://api.opencagedata.com/geocode/v1/json",
            params={"q": query, "key": key, "countrycode": "us"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json().get("results", [])
        if not data:
            return {"lat": None, "lng": None, "county": None, "state": state}
        comp = data[0].get("components", {})
        geom = data[0].get("geometry", {})
        return {
            "lat": geom.get("lat"),
            "lng": geom.get("lng"),
            "county": comp.get("county"),
            "state": comp.get("state_code", state),
            "city": comp.get("city") or comp.get("town") or city,
        }
    except Exception:
        return {"lat": None, "lng": None, "county": None, "state": state}


def gis_lookup(lat, lng):
    if lat is None or lng is None:
        return {}

    base = os.getenv("ARCGIS_ENDPOINT")
    if not base:
        return {}

    try:
        resp = requests.get(
            base,
            params={"f": "json", "geometry": f"{lng},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326},
            timeout=10,
        )
        resp.raise_for_status()
        attrs = resp.json().get("features", [{}])[0].get("attributes", {})
        return {
            "parcel_id": attrs.get("PARCEL_ID") or attrs.get("APN"),
            "zoning_district": attrs.get("ZONING") or attrs.get("ZONE_DESC"),
            "parcel_owner": attrs.get("OWNER_NAME"),
            "property_classification": attrs.get("USE_CODE") or attrs.get("PROPERTY_CLASS"),
        }
    except Exception:
        return {}


def map_responsibility(asset: str, raci: Dict):
    direct = raci.get(asset)
    if direct:
        return direct.get("responsible_team")
    for key, value in raci.items():
        if key.lower() in asset.lower():
            return value.get("responsible_team")
    return "LP"


def discover_requirements(services: List[str], state: str):
    services_kb = load_json("services.json")
    states_kb = load_json("states.json")
    inspections_kb = load_json("inspections.json")
    zoning_kb = load_json("zoning_patterns.json")
    raci_kb = load_json("raci_matrix.json")

    licenses = set()
    agencies = set()

    for service in services:
        s = services_kb.get(service.lower(), {})
        for lic in s.get("licenses", []):
            licenses.add(lic)
        for agency in s.get("inspection_agencies", []):
            agencies.add(agency)

    for lic in states_kb.get(state.upper(), {}).get("statewide_licenses", []):
        licenses.add(lic)

    for agency in inspections_kb.get(state.upper(), {}).get("agencies", []):
        agencies.add(agency)

    checklist = []
    for lic in sorted(licenses):
        checklist.append(
            {
                "task": f"Verify active {lic}",
                "responsible_team": map_responsibility(lic, raci_kb),
            }
        )

    for agency in sorted(agencies):
        checklist.append(
            {
                "task": f"Request latest inspection report from {agency}",
                "responsible_team": map_responsibility(agency, raci_kb),
            }
        )

    zoning_flags = zoning_kb.get("patterns", [])
    return {
        "licenses": sorted(licenses),
        "agencies": sorted(agencies),
        "checklist": checklist,
        "zoning_flags": zoning_flags,
        "raci": raci_kb,
    }


def score_risk(services: List[str], zoning_district: str | None, has_parcel: bool):
    veterinary = 3 if "veterinary" in services else 1
    swimming = 2 if "swimming" in services else 0
    zoning = 2 if not zoning_district else 1
    licensing = min(3, len(services) // 2 + 1)
    inspections = min(3, len(services) // 3 + 1)
    infrastructure = min(3, swimming + (0 if has_parcel else 1))
    entity = 2 if len(services) >= 4 else 1

    total = zoning + licensing + inspections + infrastructure + veterinary + entity
    if total <= 4:
        level = "Low Risk"
    elif total <= 9:
        level = "Moderate Risk"
    elif total <= 14:
        level = "High Risk"
    else:
        level = "Critical Risk"

    return {
        "zoning_risk": zoning,
        "licensing_risk": licensing,
        "inspection_risk": inspections,
        "infrastructure_risk": infrastructure,
        "veterinary_risk": veterinary,
        "entity_risk": entity,
        "total_score": total,
        "level": level,
    }
