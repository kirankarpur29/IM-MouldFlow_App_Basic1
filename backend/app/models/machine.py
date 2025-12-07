from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    manufacturer = Column(String(100))

    # Specifications
    tonnage = Column(Float, nullable=False, index=True)  # tons
    shot_volume_max = Column(Float)  # cm³
    screw_diameter = Column(Float)  # mm

    # Platen dimensions
    platen_width = Column(Float)  # mm
    platen_height = Column(Float)  # mm
    tie_bar_spacing_h = Column(Float)  # mm
    tie_bar_spacing_v = Column(Float)  # mm

    # Additional info
    typical_use = Column(String(200))
    is_custom = Column(Boolean, default=False)
    owner_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
