from io import BytesIO
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fpdf import FPDF

from .database import Base, engine, get_db
from .models import (
    Deal,
    Service,
    ParcelData,
    RiskRadar,
    RequiredLicense,
    InspectionAgency,
    DueDiligenceTask,
)
from .schemas import DealCreate, DealDetail, DealListItem
from .scan_engine import geocode_address, gis_lookup, discover_requirements, score_risk

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pet Facility Regulatory Intelligence Scanner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/scans", response_model=dict)
def run_silent_scan(payload: DealCreate, db: Session = Depends(get_db)):
    geo = geocode_address(payload.street_address, payload.city, payload.state)
    gis = gis_lookup(geo.get("lat"), geo.get("lng"))
    requirements = discover_requirements(payload.services, payload.state)
    risk = score_risk(payload.services, gis.get("zoning_district"), bool(gis.get("parcel_id")))

    deal = Deal(
        business_name=payload.business_name,
        street_address=payload.street_address,
        city=payload.city,
        state=payload.state.upper(),
        county=geo.get("county"),
        risk_score=risk["total_score"],
        risk_level=risk["level"],
        zoning_status="complete" if gis.get("zoning_district") else "warning",
        licensing_status="complete",
        inspection_status="complete",
        infrastructure_status="warning" if not gis else "complete",
        entity_status="complete",
    )
    db.add(deal)
    db.flush()

    for service in payload.services:
        db.add(Service(deal_id=deal.id, service_name=service.lower()))

    db.add(
        ParcelData(
            deal_id=deal.id,
            parcel_id=gis.get("parcel_id"),
            zoning_district=gis.get("zoning_district"),
            parcel_owner=gis.get("parcel_owner"),
            property_classification=gis.get("property_classification"),
        )
    )

    db.add(RiskRadar(deal_id=deal.id, **risk))

    for lic in requirements["licenses"]:
        db.add(
            RequiredLicense(
                deal_id=deal.id,
                name=lic,
                responsible_team=requirements["raci"].get(lic, {}).get("responsible_team", "LP"),
            )
        )

    for agency in requirements["agencies"]:
        db.add(InspectionAgency(deal_id=deal.id, name=agency))

    for task in requirements["checklist"]:
        db.add(
            DueDiligenceTask(
                deal_id=deal.id,
                task=task["task"],
                responsible_team=task["responsible_team"],
            )
        )

    db.commit()
    return {"deal_id": deal.id, "message": "Silent scan completed"}


@app.get("/api/deals", response_model=list[DealListItem])
def list_deals(db: Session = Depends(get_db)):
    deals = db.query(Deal).order_by(Deal.id.desc()).all()
    items = []
    for d in deals:
        items.append(
            DealListItem(
                id=d.id,
                business_name=d.business_name,
                city=d.city,
                state=d.state,
                services=[s.service_name for s in d.services],
                zoning_status=d.zoning_status,
                licensing_status=d.licensing_status,
                inspection_status=d.inspection_status,
                infrastructure_status=d.infrastructure_status,
                entity_status=d.entity_status,
                risk_score=d.risk_score,
                risk_level=d.risk_level,
            )
        )
    return items


@app.get("/api/deals/{deal_id}", response_model=DealDetail)
def deal_detail(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return DealDetail(
        id=deal.id,
        business_name=deal.business_name,
        street_address=deal.street_address,
        city=deal.city,
        state=deal.state,
        county=deal.county,
        services=[s.service_name for s in deal.services],
        required_licenses=[l.name for l in deal.required_licenses],
        inspection_agencies=[a.name for a in deal.inspection_agencies],
        due_diligence_checklist=[t.task for t in deal.due_diligence_tasks],
        uploaded_documents=[doc.filename for doc in deal.documents],
        risk_radar=deal.risk_radar,
    )


@app.get("/api/deals/{deal_id}/export/{fmt}")
def export_report(deal_id: int, fmt: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    payload = {
        "deal": deal.business_name,
        "location": f"{deal.city}, {deal.state}",
        "risk_score": deal.risk_score,
        "risk_level": deal.risk_level,
        "licenses": [l.name for l in deal.required_licenses],
        "agencies": [a.name for a in deal.inspection_agencies],
        "tasks": [t.task for t in deal.due_diligence_tasks],
    }

    if fmt == "json":
        import json

        return Response(content=json.dumps(payload, indent=2), media_type="application/json")

    if fmt == "txt":
        lines = [
            f"Regulatory Report: {payload['deal']}",
            f"Location: {payload['location']}",
            f"Risk: {payload['risk_score']} ({payload['risk_level']})",
            "Required Licenses:",
            *[f"- {l}" for l in payload["licenses"]],
            "Inspection Agencies:",
            *[f"- {a}" for a in payload["agencies"]],
        ]
        return Response(content="\n".join(lines), media_type="text/plain")

    if fmt == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in [
            f"Regulatory Report: {payload['deal']}",
            f"Location: {payload['location']}",
            f"Risk: {payload['risk_score']} ({payload['risk_level']})",
            "",
            "Required Licenses:",
            *[f"- {l}" for l in payload["licenses"]],
            "",
            "Inspection Agencies:",
            *[f"- {a}" for a in payload["agencies"]],
        ]:
            pdf.cell(0, 8, line, ln=True)

        blob = BytesIO(pdf.output(dest="S").encode("latin-1"))
        return Response(content=blob.getvalue(), media_type="application/pdf")

    raise HTTPException(status_code=400, detail="Supported formats: pdf, txt, json")
