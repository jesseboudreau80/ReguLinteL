# Pet Facility Regulatory Intelligence Scanner

Full-stack application for silent regulatory due diligence during pet facility M&A.

## Tech Stack
- **Backend:** FastAPI + SQLAlchemy
- **Frontend:** React (Vite)
- **Database:** PostgreSQL
- **External APIs:** OpenCage Geocoding, ArcGIS GIS lookup

## Project Structure
- `backend/` - API, scan engine integration, DB models/schema
- `frontend/` - Dashboard + deal intake/detail user interface
- `knowledge_base/` - Regulatory service/state/inspection/zoning/RACI data
- `services/` - External service adapter workspace
- `silent_scan_engine/` - Engine notes and integration scope
- `dashboard/` - Dashboard-specific docs
- `reports/` - Reporting/export assets

## Core Features Implemented
- New Regulatory Scan intake form with services checkboxes
- Silent scan pipeline (geocode, jurisdiction, GIS attempt with graceful fallback)
- Regulatory discovery engine (licenses, agencies, checklist)
- RACI matrix mapping for due diligence ownership
- LP Deal Risk Radar score (0–18) with risk classification
- Dashboard table with color risk dots and regulatory statuses
- Deal detail page with snapshot, checklist, agencies, licenses, risk radar
- Report export endpoints: PDF/TXT/JSON
- PostgreSQL schema for Deals, Services, ParcelData, RiskRadar, RequiredLicenses, InspectionAgencies, DueDiligenceTasks, Documents

## Run Locally

### 1) Database
Create PostgreSQL DB:

```bash
createdb petreg
```

Optional schema bootstrap:

```bash
psql -d petreg -f backend/schema.sql
```

### 2) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/petreg"
# optional external API keys
export OPENCAGE_API_KEY="your_key"
export ARCGIS_ENDPOINT="https://.../query"
uvicorn app.main:app --reload --port 8000
```

### 3) Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API Quick Reference
- `POST /api/scans` - run silent scan and create deal
- `GET /api/deals` - dashboard deals
- `GET /api/deals/{id}` - full deal detail
- `GET /api/deals/{id}/export/pdf|txt|json` - report exports
