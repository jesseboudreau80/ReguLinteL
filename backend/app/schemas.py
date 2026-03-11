from pydantic import BaseModel
from typing import List, Optional


class DealCreate(BaseModel):
    business_name: str
    street_address: str
    city: str
    state: str
    services: List[str]


class DealListItem(BaseModel):
    id: int
    business_name: str
    city: str
    state: str
    services: List[str]
    zoning_status: str
    licensing_status: str
    inspection_status: str
    infrastructure_status: str
    entity_status: str
    risk_score: int
    risk_level: str

    class Config:
        from_attributes = True


class RiskRadarOut(BaseModel):
    zoning_risk: int
    licensing_risk: int
    inspection_risk: int
    infrastructure_risk: int
    veterinary_risk: int
    entity_risk: int
    total_score: int
    level: str

    class Config:
        from_attributes = True


class DealDetail(BaseModel):
    id: int
    business_name: str
    street_address: str
    city: str
    state: str
    county: Optional[str]
    services: List[str]
    required_licenses: List[str]
    inspection_agencies: List[str]
    due_diligence_checklist: List[str]
    uploaded_documents: List[str]
    risk_radar: RiskRadarOut

