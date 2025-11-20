from sqlalchemy import Column, Integer, String, Float, ForeignKey, LargeBinary, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200))

    # File info
    file_name = Column(String(255))
    file_type = Column(String(10))  # STL, STEP, manual

    # Computed geometry
    volume = Column(Float)  # cm³
    projected_area = Column(Float)  # cm²
    surface_area = Column(Float)  # cm²
    max_thickness = Column(Float)  # mm
    min_thickness = Column(Float)
    avg_thickness = Column(Float)

    # Bounding box
    bbox_x = Column(Float)  # mm
    bbox_y = Column(Float)
    bbox_z = Column(Float)

    # Manual input fallback
    manual_length = Column(Float)
    manual_width = Column(Float)
    manual_height = Column(Float)
    manual_thickness = Column(Float)

    # Stored geometry
    geometry_data = Column(LargeBinary)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="parts")
    analyses = relationship("Analysis", back_populates="part", cascade="all, delete-orphan")
