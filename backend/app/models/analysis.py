from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    # Configuration
    cavity_count = Column(Integer, default=1)
    gate_type = Column(String(50))  # edge, pin, fan, submarine
    gate_location_x = Column(Float)
    gate_location_y = Column(Float)
    gate_location_z = Column(Float)
    gate_diameter = Column(Float)  # mm
    runner_diameter = Column(Float)  # mm
    safety_factor = Column(Float, default=1.15)

    # Results - Fill
    fill_time = Column(Float)  # seconds
    injection_pressure = Column(Float)  # MPa

    # Results - Tonnage
    clamp_tonnage_min = Column(Float)
    clamp_tonnage_recommended = Column(Float)
    clamp_tonnage_max = Column(Float)

    # Results - Cycle
    cooling_time = Column(Float)
    pack_time = Column(Float)
    cycle_time = Column(Float)  # seconds

    # Results - Other
    part_weight = Column(Float)  # grams
    shot_weight = Column(Float)  # including runners

    # Feasibility
    feasibility_status = Column(String(20))  # feasible, borderline, not_recommended
    feasibility_score = Column(Integer)  # 0-100

    # Warnings and risks (JSON arrays)
    warnings = Column(JSON)
    risk_zones = Column(JSON)

    # Machine recommendations (JSON)
    recommended_machines = Column(JSON)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    part = relationship("Part", back_populates="analyses")
    material = relationship("Material")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")
