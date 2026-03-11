from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), nullable=False)
    street_address = Column(String(255), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(2), nullable=False)
    county = Column(String(120), nullable=True)
    zoning_status = Column(String(50), default="not_evaluated")
    licensing_status = Column(String(50), default="not_evaluated")
    inspection_status = Column(String(50), default="not_evaluated")
    infrastructure_status = Column(String(50), default="not_evaluated")
    entity_status = Column(String(50), default="not_evaluated")
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(50), default="Low")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    services = relationship("Service", back_populates="deal", cascade="all, delete-orphan")
    parcel_data = relationship("ParcelData", back_populates="deal", uselist=False, cascade="all, delete-orphan")
    risk_radar = relationship("RiskRadar", back_populates="deal", uselist=False, cascade="all, delete-orphan")
    required_licenses = relationship("RequiredLicense", back_populates="deal", cascade="all, delete-orphan")
    inspection_agencies = relationship("InspectionAgency", back_populates="deal", cascade="all, delete-orphan")
    due_diligence_tasks = relationship("DueDiligenceTask", back_populates="deal", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="deal", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    service_name = Column(String(100), nullable=False)

    deal = relationship("Deal", back_populates="services")


class ParcelData(Base):
    __tablename__ = "parcel_data"

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), unique=True, nullable=False)
    parcel_id = Column(String(120), nullable=True)
    zoning_district = Column(String(120), nullable=True)
    parcel_owner = Column(String(255), nullable=True)
    property_classification = Column(String(120), nullable=True)

    deal = relationship("Deal", back_populates="parcel_data")


class RiskRadar(Base):
    __tablename__ = "risk_radar"

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), unique=True, nullable=False)
    zoning_risk = Column(Integer, default=0)
    licensing_risk = Column(Integer, default=0)
    inspection_risk = Column(Integer, default=0)
    infrastructure_risk = Column(Integer, default=0)
    veterinary_risk = Column(Integer, default=0)
    entity_risk = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    level = Column(String(50), default="Low")

    deal = relationship("Deal", back_populates="risk_radar")


class RequiredLicense(Base):
    __tablename__ = "required_licenses"

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    name = Column(String(255), nullable=False)
    responsible_team = Column(String(80), nullable=True)

    deal = relationship("Deal", back_populates="required_licenses")


class InspectionAgency(Base):
    __tablename__ = "inspection_agencies"

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    name = Column(String(255), nullable=False)

    deal = relationship("Deal", back_populates="inspection_agencies")


class DueDiligenceTask(Base):
    __tablename__ = "due_diligence_tasks"

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    task = Column(Text, nullable=False)
    responsible_team = Column(String(80), nullable=True)
    completed = Column(Boolean, default=False)

    deal = relationship("Deal", back_populates="due_diligence_tasks")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)

    deal = relationship("Deal", back_populates="documents")
