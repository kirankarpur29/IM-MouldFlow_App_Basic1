from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
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
    melt_temp_optimal = Column(Float)  # Recommended processing temp
    mold_temp_min = Column(Float)
    mold_temp_max = Column(Float)
    mold_temp_optimal = Column(Float)  # Recommended mold temp
    ejection_temp = Column(Float)  # Safe ejection temperature

    # Physical properties
    density = Column(Float)  # g/cm³
    shrinkage_min = Column(Float)  # % (or perpendicular for filled)
    shrinkage_max = Column(Float)  # % (or parallel for filled)
    shrinkage_parallel = Column(Float, nullable=True)  # For fiber-reinforced materials
    shrinkage_perpendicular = Column(Float, nullable=True)  # For fiber-reinforced materials

    # Thermal properties (for cooling analysis)
    thermal_conductivity = Column(Float)  # W/m·K
    specific_heat = Column(Float)  # kJ/kg·K
    thermal_diffusivity = Column(Float)  # m²/s (calculated or measured)

    # Flow properties
    mfi = Column(Float)  # Melt Flow Index g/10min
    viscosity_class = Column(String(20))  # low/medium/high
    max_flow_length_ratio = Column(Float)  # flow length to thickness
    viscosity_curve = Column(JSON, nullable=True)  # {shear_rate: viscosity} pairs

    # Processing
    recommended_pressure_min = Column(Float)  # MPa
    recommended_pressure_max = Column(Float)
    recommended_injection_speed = Column(Float, nullable=True)  # cm³/s
    packing_pressure_ratio = Column(Float, default=0.70)  # Ratio of packing to injection pressure

    # Mechanical properties
    tensile_strength_mpa = Column(Float, nullable=True)
    flexural_modulus_mpa = Column(Float, nullable=True)
    impact_strength = Column(Float, nullable=True)  # kJ/m²

    # Special characteristics
    has_fiber_reinforcement = Column(Boolean, default=False)
    fiber_content_percent = Column(Float, nullable=True)  # % glass/carbon fiber
    is_crystalline = Column(Boolean, default=False)  # Affects cooling time

    # Metadata
    is_custom = Column(Boolean, default=False)
    source = Column(String(200))  # data source citation
    created_at = Column(DateTime, server_default=func.now())
