from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(100))  # e.g., "SABIC", "LG Chem"
    grade = Column(String(100))  # e.g., "Cycolac MG47"
    category = Column(String(50))  # ABS, PP, PC, etc.

    # Temperature ranges (°C)
    melt_temp_min = Column(Float)
    melt_temp_max = Column(Float)
    mold_temp_min = Column(Float)
    mold_temp_max = Column(Float)

    # Physical properties
    density = Column(Float)  # g/cm³
    shrinkage_min = Column(Float)  # %
    shrinkage_max = Column(Float)

    # Flow properties
    mfi = Column(Float)  # Melt Flow Index g/10min
    viscosity_class = Column(String(20))  # low/medium/high
    max_flow_length_ratio = Column(Float)  # flow length to thickness

    # Processing
    recommended_pressure_min = Column(Float)  # MPa
    recommended_pressure_max = Column(Float)

    # Metadata
    is_custom = Column(Boolean, default=False)
    source = Column(String(200))  # data source citation
    created_at = Column(DateTime, server_default=func.now())
